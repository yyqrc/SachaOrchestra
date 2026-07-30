[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Root,
    [Parameter(Mandatory)][string]$PromptPath,
    [Parameter(Mandatory)][string]$ExpectedHead,
    [Parameter(Mandatory)][string[]]$WritePath,
    [string[]]$ReadPath = @(),
    [string]$PiPath = 'pi',
    [AllowNull()][ValidatePattern('^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$')][string]$Model,
    [ValidateSet('low', 'medium', 'high', 'xhigh', 'max')][string]$Effort = 'high',
    [ValidateRange(30, 86400)][int]$TimeoutSeconds = 1800,
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$')][string]$RunId = ([Guid]::NewGuid().ToString('N'))
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function Test-ContainedPath {
    param(
        [Parameter(Mandatory)][string]$RootPath,
        [Parameter(Mandatory)][string]$CandidatePath
    )

    $rootFull = [System.IO.Path]::GetFullPath($RootPath).TrimEnd('\', '/')
    $candidateFull = [System.IO.Path]::GetFullPath($CandidatePath).TrimEnd('\', '/')
    if ($candidateFull.Equals($rootFull, [StringComparison]::OrdinalIgnoreCase)) {
        return $true
    }
    return $candidateFull.StartsWith(
        $rootFull + [System.IO.Path]::DirectorySeparatorChar,
        [StringComparison]::OrdinalIgnoreCase
    )
}

function Get-RelativePath {
    param(
        [Parameter(Mandatory)][string]$BasePath,
        [Parameter(Mandatory)][string]$TargetPath
    )

    return [System.IO.Path]::GetRelativePath($BasePath, $TargetPath).Replace('\', '/')
}

function Assert-NoReparseAncestor {
    param(
        [Parameter(Mandatory)][string]$RootPath,
        [Parameter(Mandatory)][string]$CandidatePath
    )

    $rootFull = [System.IO.Path]::GetFullPath($RootPath).TrimEnd('\', '/')
    $current = [System.IO.Path]::GetFullPath($CandidatePath)
    while (-not (Test-Path -LiteralPath $current)) {
        $parent = [System.IO.Path]::GetDirectoryName($current)
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent.Equals($current, [StringComparison]::OrdinalIgnoreCase)) {
            break
        }
        $current = $parent
    }
    while (Test-ContainedPath -RootPath $rootFull -CandidatePath $current) {
        $item = Get-Item -LiteralPath $current -Force
        $itemFull = [System.IO.Path]::GetFullPath($item.FullName).TrimEnd('\', '/')
        $currentFull = [System.IO.Path]::GetFullPath($current).TrimEnd('\', '/')
        if (-not $itemFull.Equals($currentFull, [StringComparison]::OrdinalIgnoreCase)) {
            throw "拒绝非规范路径别名：$current"
        }
        if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "拒绝通过 reparse point 访问：$current"
        }
        if ($current.TrimEnd('\', '/').Equals($rootFull, [StringComparison]::OrdinalIgnoreCase)) {
            break
        }
        $current = [System.IO.Path]::GetDirectoryName($current)
    }
}

function Resolve-Command {
    param([Parameter(Mandatory)][string]$Command)

    $resolved = Get-Command $Command -ErrorAction Stop
    $source = $resolved.Source
    $extension = [System.IO.Path]::GetExtension($source)
    if ($extension.Equals('.ps1', [StringComparison]::OrdinalIgnoreCase)) {
        $pwsh = (Get-Command pwsh -ErrorAction Stop).Source
        return [pscustomobject]@{
            executable = $pwsh
            prefix     = @('-NoProfile', '-File', $source)
            source     = $source
        }
    }
    if ($extension.Equals('.exe', [StringComparison]::OrdinalIgnoreCase)) {
        return [pscustomobject]@{
            executable = $source
            prefix     = @()
            source     = $source
        }
    }
    throw "PiPath 必须解析为 .ps1 或 .exe：$source"
}

function Invoke-Process {
    param(
        [Parameter(Mandatory)]$CommandInfo,
        [Parameter(Mandatory)][string[]]$Arguments,
        [Parameter(Mandatory)][string]$WorkingDirectory,
        [AllowEmptyString()][string]$StandardInput = '',
        [hashtable]$Environment = @{},
        [Parameter(Mandatory)][int]$TimeoutMilliseconds
    )

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $CommandInfo.executable
    $startInfo.WorkingDirectory = $WorkingDirectory
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardInput = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.StandardInputEncoding = [System.Text.UTF8Encoding]::new($false)
    $startInfo.StandardOutputEncoding = [System.Text.Encoding]::UTF8
    $startInfo.StandardErrorEncoding = [System.Text.Encoding]::UTF8
    foreach ($argument in @($CommandInfo.prefix) + $Arguments) {
        $null = $startInfo.ArgumentList.Add($argument)
    }
    foreach ($name in $Environment.Keys) {
        $startInfo.Environment[$name] = [string]$Environment[$name]
    }

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    $started = [DateTime]::UtcNow
    if (-not $process.Start()) {
        throw "无法启动命令：$($CommandInfo.source)"
    }
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    if ($StandardInput.Length -gt 0) {
        $process.StandardInput.Write($StandardInput)
    }
    $process.StandardInput.Close()

    $timedOut = -not $process.WaitForExit($TimeoutMilliseconds)
    if ($timedOut) {
        try {
            $process.Kill($true)
            $process.WaitForExit()
        }
        catch {
            # The summary still reports timeout even if the process already exited.
        }
    }
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()
    $exitCode = if ($timedOut) { -1 } else { $process.ExitCode }
    $process.Dispose()

    return [pscustomobject]@{
        exit_code   = $exitCode
        timed_out   = $timedOut
        duration_ms = [int]([DateTime]::UtcNow - $started).TotalMilliseconds
        stdout      = $stdout
        stderr      = $stderr
    }
}

function Invoke-Git {
    param(
        [Parameter(Mandatory)][string]$RootPath,
        [Parameter(Mandatory)][string[]]$Arguments
    )

    $output = @(& git -C $RootPath @Arguments 2>&1)
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "git $($Arguments -join ' ') 失败：$($output -join [Environment]::NewLine)"
    }
    return @($output | ForEach-Object { $_.ToString() })
}

function Get-ChangedPaths {
    param([Parameter(Mandatory)][string]$RootPath)

    $tracked = @(Invoke-Git -RootPath $RootPath -Arguments @('diff', '--name-only', '--no-renames', '--'))
    $staged = @(Invoke-Git -RootPath $RootPath -Arguments @('diff', '--cached', '--name-only', '--no-renames', '--'))
    $untracked = @(Invoke-Git -RootPath $RootPath -Arguments @('ls-files', '--others', '--exclude-standard'))
    return @($tracked + $staged + $untracked |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        ForEach-Object { $_.Replace('\', '/') } |
        Sort-Object -Unique)
}

function Test-AllowedWrite {
    param(
        [Parameter(Mandatory)][string]$RelativePath,
        [Parameter(Mandatory)][string[]]$AllowedPaths
    )

    $candidate = $RelativePath.TrimEnd('/')
    foreach ($allowed in $AllowedPaths) {
        if (
            $candidate.Equals($allowed, [StringComparison]::OrdinalIgnoreCase) -or
            $candidate.StartsWith($allowed.TrimEnd('/') + '/', [StringComparison]::OrdinalIgnoreCase)
        ) {
            return $true
        }
    }
    return $false
}

function Resolve-ScopedPaths {
    param(
        [Parameter(Mandatory)][string]$RootPath,
        [Parameter(Mandatory)][string[]]$Paths,
        [Parameter(Mandatory)][string]$Label
    )

    $resolved = @()
    foreach ($path in $Paths) {
        $segments = @($path -split '[\\/]')
        $invalidSegment = @($segments | Where-Object {
            [string]::IsNullOrEmpty($_) -or
            $_ -in @('.', '..') -or
            $_.EndsWith(' ') -or
            $_.EndsWith('.') -or
            $_.IndexOfAny([System.IO.Path]::GetInvalidFileNameChars()) -ge 0 -or
            $_ -match '^(?i:con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(?:\..*)?$'
        }).Count -gt 0
        if (
            [string]::IsNullOrWhiteSpace($path) -or
            [System.IO.Path]::IsPathRooted($path) -or
            $invalidSegment -or
            $path.IndexOfAny([char[]]'*?[]!()') -ge 0
        ) {
            throw "不安全的 ${Label}：$path"
        }
        $candidate = [System.IO.Path]::GetFullPath((Join-Path $RootPath $path))
        if (-not (Test-ContainedPath -RootPath $RootPath -CandidatePath $candidate)) {
            throw "${Label} 不在 Root 内：$path"
        }
        Assert-NoReparseAncestor -RootPath $RootPath -CandidatePath $candidate
        $relative = (Get-RelativePath -BasePath $RootPath -TargetPath $candidate).TrimEnd('/')
        if (
            $relative.Equals('.', [StringComparison]::OrdinalIgnoreCase) -or
            $relative.Equals('.git', [StringComparison]::OrdinalIgnoreCase) -or
            $relative.Equals('.temp', [StringComparison]::OrdinalIgnoreCase) -or
            $relative.StartsWith('.git/', [StringComparison]::OrdinalIgnoreCase) -or
            $relative.StartsWith('.temp/', [StringComparison]::OrdinalIgnoreCase)
        ) {
            throw "${Label} 不得指向控制目录：$path"
        }
        $resolved += $relative
    }
    return @($resolved | Sort-Object -Unique)
}

function Get-FileState {
    param(
        [Parameter(Mandatory)][string]$BasePath,
        [Parameter(Mandatory)][AllowEmptyCollection()][string[]]$RelativePaths
    )

    $state = @{}
    foreach ($relative in $RelativePaths) {
        $fullPath = Join-Path $BasePath $relative
        if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
            $state[$relative.Replace('\', '/')] = (Get-FileHash -LiteralPath $fullPath -Algorithm SHA256).Hash
        }
    }
    return $state
}

function Get-DirectoryFileState {
    param([Parameter(Mandatory)][string]$DirectoryPath)

    $relativePaths = @(
        Get-ChildItem -LiteralPath $DirectoryPath -File -Recurse -Force |
            ForEach-Object { Get-RelativePath -BasePath $DirectoryPath -TargetPath $_.FullName }
    )
    return Get-FileState -BasePath $DirectoryPath -RelativePaths @($relativePaths)
}

function Get-IgnoredFileState {
    param(
        [Parameter(Mandatory)][string]$RootPath,
        [Parameter(Mandatory)][string[]]$AllowedPaths
    )

    $ignored = @(
        Invoke-Git -RootPath $RootPath -Arguments @(
            '-c', 'core.quotepath=false',
            'ls-files', '--others', '--ignored', '--exclude-standard', '--'
        )
    ) | Where-Object {
        $relative = $_.Replace('\', '/')
        -not $relative.StartsWith('.temp/') -and
        -not (Test-AllowedWrite -RelativePath $relative -AllowedPaths $AllowedPaths)
    }
    return Get-FileState -BasePath $RootPath -RelativePaths @($ignored)
}

function Compare-FileState {
    param(
        [Parameter(Mandatory)][hashtable]$Before,
        [Parameter(Mandatory)][hashtable]$After
    )

    return @(
        @($Before.Keys) + @($After.Keys) |
            Sort-Object -Unique |
            Where-Object {
                -not $Before.ContainsKey($_) -or
                -not $After.ContainsKey($_) -or
                $Before[$_] -ne $After[$_]
            }
    )
}

$summary = [ordered]@{
    status                   = 'error'
    run_id                   = $RunId
    requested_model          = $Model
    effective_model          = $null
    effort                   = $Effort
    pi_version               = $null
    capabilities_verified    = $false
    pi_exit_code             = $null
    timed_out                = $false
    duration_ms              = 0
    head_before              = $null
    head_after               = $null
    changed_files            = @()
    scope_violations         = @()
    ignored_scope_violations = @()
    git_metadata_changed     = $false
    stdout_json_valid        = $false
    agent_settled            = $false
    structured_result_received = $false
    outcome                  = $null
    result_summary           = $null
    blockers                 = @()
    raw_dir                  = $null
    error                    = $null
}
$scriptExitCode = 2

try {
    $rootPath = (Resolve-Path -LiteralPath $Root).Path
    if (-not (Test-Path -LiteralPath (Join-Path $rootPath '.git') -PathType Leaf)) {
        throw 'Root 必须是由 git worktree 建立的 linked worktree，不能是主工作树'
    }
    $gitDirectory = [System.IO.Path]::GetFullPath(
        @(Invoke-Git -RootPath $rootPath -Arguments @('rev-parse', '--absolute-git-dir'))[0].Trim()
    )
    $commonDirectory = [System.IO.Path]::GetFullPath(
        @(Invoke-Git -RootPath $rootPath -Arguments @('rev-parse', '--path-format=absolute', '--git-common-dir'))[0].Trim()
    )
    if ($gitDirectory.Equals($commonDirectory, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Root 的 Git directory 与 common directory 相同，不是独立 linked worktree'
    }

    $promptResolved = (Resolve-Path -LiteralPath $PromptPath).Path
    if (-not (Test-ContainedPath -RootPath $rootPath -CandidatePath $promptResolved)) {
        throw 'PromptPath 必须位于 Root 内'
    }
    Assert-NoReparseAncestor -RootPath $rootPath -CandidatePath $promptResolved

    $allowedPaths = @(Resolve-ScopedPaths -RootPath $rootPath -Paths $WritePath -Label 'WritePath')
    if ($allowedPaths.Count -eq 0) {
        throw 'WritePath 不得为空'
    }
    $readPaths = @(
        Resolve-ScopedPaths -RootPath $rootPath -Paths @($ReadPath + $WritePath) -Label 'ReadPath'
    )

    $headBefore = @(Invoke-Git -RootPath $rootPath -Arguments @('rev-parse', 'HEAD'))[0].Trim()
    $summary.head_before = $headBefore
    if (-not $headBefore.Equals($ExpectedHead.Trim(), [StringComparison]::OrdinalIgnoreCase)) {
        throw "HEAD 与 ExpectedHead 不匹配：expected=$ExpectedHead actual=$headBefore"
    }

    $preexisting = @(Invoke-Git -RootPath $rootPath -Arguments @('status', '--porcelain', '--untracked-files=all'))
    if ($preexisting.Count -gt 0) {
        throw "linked worktree 不是干净基线：$($preexisting -join '; ')"
    }

    $rawPath = Join-Path $rootPath ('.temp\sacha-pi\' + $RunId)
    $rawParent = Split-Path -Parent $rawPath
    Assert-NoReparseAncestor -RootPath $rootPath -CandidatePath $rawParent
    $null = New-Item -ItemType Directory -Path $rawParent -Force
    if (Test-Path -LiteralPath $rawPath) {
        throw "RunId 已存在：$RunId"
    }
    $null = New-Item -ItemType Directory -Path $rawPath
    $summary.raw_dir = (Get-RelativePath -BasePath $rootPath -TargetPath $rawPath)

    $commandInfo = Resolve-Command -Command $PiPath
    $versionResult = Invoke-Process `
        -CommandInfo $commandInfo `
        -Arguments @('--version') `
        -WorkingDirectory $rootPath `
        -TimeoutMilliseconds 20000
    if ($versionResult.exit_code -ne 0) {
        throw "pi --version 失败：$($versionResult.stderr.Trim())"
    }
    $summary.pi_version = $versionResult.stdout.Trim()
    $helpResult = Invoke-Process `
        -CommandInfo $commandInfo `
        -Arguments @('--help') `
        -WorkingDirectory $rootPath `
        -TimeoutMilliseconds 20000
    if ($helpResult.exit_code -ne 0) {
        throw "pi --help 失败：$($helpResult.stderr.Trim())"
    }
    foreach ($marker in @(
        '--print',
        '--no-session',
        '--mode',
        '--model',
        '--thinking',
        '--tools',
        '--extension',
        '--no-extensions',
        '--no-skills',
        '--no-prompt-templates',
        '--no-context-files',
        '--no-approve',
        '--append-system-prompt'
    )) {
        if (-not $helpResult.stdout.Contains($marker)) {
            throw "当前 Pi CLI 不支持所需能力：$marker"
        }
    }
    $summary.capabilities_verified = $true

    $guardPath = Join-Path $PSScriptRoot 'pi_guard.mjs'
    if (-not (Test-Path -LiteralPath $guardPath -PathType Leaf)) {
        throw "Pi guard extension 不存在：$guardPath"
    }
    Assert-NoReparseAncestor -RootPath (Split-Path -Parent $PSScriptRoot) -CandidatePath $guardPath

    $arguments = @(
        '-p',
        '--no-session',
        '--mode', 'json',
        '--thinking', $Effort,
        '--no-extensions',
        '--extension', $guardPath,
        '--no-skills',
        '--no-prompt-templates',
        '--no-context-files',
        '--no-approve',
        '--tools', 'read,edit,write,sacha_result',
        '--append-system-prompt',
        'You are a one-shot implementation worker. Use only the active tools and allowed paths. Do not create commits or alter Git metadata. Do not ask for interaction. Finish by calling sacha_result exactly once; use completed only after implementation and available verification, otherwise report blocked or failed.',
        ('@' + $promptResolved)
    )
    if (-not [string]::IsNullOrWhiteSpace($Model)) {
        $arguments = @($arguments[0..3]) + @('--model', $Model) + @($arguments[4..($arguments.Count - 1)])
    }

    $prompt = [System.IO.File]::ReadAllText($promptResolved, [System.Text.Encoding]::UTF8)
    [System.IO.File]::WriteAllText(
        (Join-Path $rawPath 'prompt.md'),
        $prompt,
        [System.Text.UTF8Encoding]::new($false)
    )
    $ignoredStateBefore = Get-IgnoredFileState -RootPath $rootPath -AllowedPaths $allowedPaths
    $gitStateBefore = Get-DirectoryFileState -DirectoryPath $gitDirectory
    $result = Invoke-Process `
        -CommandInfo $commandInfo `
        -Arguments $arguments `
        -WorkingDirectory $rootPath `
        -Environment @{
            SACHA_PI_ROOT = $rootPath
            SACHA_PI_READ_PATHS_JSON = (ConvertTo-Json -InputObject @($readPaths) -Compress)
            SACHA_PI_WRITE_PATHS_JSON = (ConvertTo-Json -InputObject @($allowedPaths) -Compress)
        } `
        -TimeoutMilliseconds ($TimeoutSeconds * 1000)

    $summary.pi_exit_code = $result.exit_code
    $summary.timed_out = $result.timed_out
    $summary.duration_ms = $result.duration_ms
    [System.IO.File]::WriteAllText(
        (Join-Path $rawPath 'stdout.jsonl'),
        $result.stdout,
        [System.Text.UTF8Encoding]::new($false)
    )
    [System.IO.File]::WriteAllText(
        (Join-Path $rawPath 'stderr.txt'),
        $result.stderr,
        [System.Text.UTF8Encoding]::new($false)
    )
    $events = @()
    $jsonLines = @(
        $result.stdout -split '\r?\n' |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    )
    $summary.stdout_json_valid = $jsonLines.Count -gt 0
    foreach ($line in $jsonLines) {
        try {
            $events += $line | ConvertFrom-Json
        }
        catch {
            $summary.stdout_json_valid = $false
            break
        }
    }
    if ($summary.stdout_json_valid) {
        $modelEvents = @($events | Where-Object {
            $null -ne $_.message -and
            $_.message.role -eq 'assistant' -and
            -not [string]::IsNullOrWhiteSpace([string]$_.message.model)
        })
        if ($modelEvents.Count -gt 0) {
            $effectiveMessage = $modelEvents[-1].message
            $summary.effective_model = if (
                -not [string]::IsNullOrWhiteSpace([string]$effectiveMessage.provider)
            ) {
                "$($effectiveMessage.provider)/$($effectiveMessage.model)"
            }
            else {
                [string]$effectiveMessage.model
            }
        }
        $summary.agent_settled = @($events | Where-Object {
            $_.type -eq 'agent_settled'
        }).Count -gt 0
        $resultEvents = @($events | Where-Object {
            $_.type -eq 'tool_execution_end' -and
            $_.toolName -eq 'sacha_result' -and
            -not [bool]$_.isError
        })
        if ($resultEvents.Count -gt 0) {
            $details = $resultEvents[-1].result.details
            if (
                $null -ne $details -and
                $details.outcome -in @('completed', 'blocked', 'failed') -and
                $details.summary -is [string] -and
                $details.PSObject.Properties.Name -contains 'blockers'
            ) {
                $summary.structured_result_received = $true
                $summary.outcome = $details.outcome
                $summary.result_summary = $details.summary
                $summary.blockers = if ($null -eq $details.blockers) {
                    @()
                }
                else {
                    @($details.blockers)
                }
            }
        }
    }

    $gitStateAfter = Get-DirectoryFileState -DirectoryPath $gitDirectory
    $gitMetadataChanges = @(Compare-FileState -Before $gitStateBefore -After $gitStateAfter)
    $summary.git_metadata_changed = $gitMetadataChanges.Count -gt 0
    $ignoredStateAfter = Get-IgnoredFileState -RootPath $rootPath -AllowedPaths $allowedPaths
    $ignoredScopeViolations = @(Compare-FileState -Before $ignoredStateBefore -After $ignoredStateAfter)
    $summary.ignored_scope_violations = $ignoredScopeViolations

    $postGitError = $null
    try {
        $headAfter = @(Invoke-Git -RootPath $rootPath -Arguments @('rev-parse', 'HEAD'))[0].Trim()
        $summary.head_after = $headAfter
        $changedFiles = @(Get-ChangedPaths -RootPath $rootPath)
        $summary.changed_files = $changedFiles
    }
    catch {
        $postGitError = $_.Exception.Message
        $headAfter = $null
        $changedFiles = @()
    }
    $scopeViolations = @(
        @($changedFiles | Where-Object {
            -not (Test-AllowedWrite -RelativePath $_ -AllowedPaths $allowedPaths)
        }) + $ignoredScopeViolations |
            Sort-Object -Unique
    )
    $summary.scope_violations = $scopeViolations

    if (
        $summary.git_metadata_changed -or
        $postGitError -or
        -not $headAfter.Equals($headBefore, [StringComparison]::OrdinalIgnoreCase) -or
        $scopeViolations.Count -gt 0
    ) {
        $summary.status = 'containment_failed'
        $summary.error = if ($scopeViolations.Count -gt 0) {
            "Pi 写出允许范围：$($scopeViolations -join ', ')"
        }
        elseif ($summary.git_metadata_changed) {
            'Pi 改变了 linked worktree Git metadata'
        }
        elseif ($postGitError) {
            "Pi 破坏了 linked worktree Git 状态：$postGitError"
        }
        else {
            'Pi 改变了 worktree HEAD'
        }
        $scriptExitCode = 4
    }
    elseif (
        $result.timed_out -or
        $result.exit_code -ne 0 -or
        -not $summary.stdout_json_valid -or
        -not $summary.agent_settled -or
        -not $summary.structured_result_received -or
        (
            -not [string]::IsNullOrWhiteSpace($Model) -and
            -not $Model.Equals([string]$summary.effective_model, [StringComparison]::OrdinalIgnoreCase)
        ) -or
        $summary.outcome -ne 'completed' -or
        $summary.blockers.Count -gt 0
    ) {
        $summary.status = 'pi_failed'
        $summary.error = if ($result.timed_out) {
            "Pi 超过 TimeoutSeconds=$TimeoutSeconds"
        }
        elseif ($result.exit_code -ne 0) {
            "Pi 退出码：$($result.exit_code)"
        }
        elseif (-not $summary.stdout_json_valid) {
            'Pi stdout 不是合法 JSONL'
        }
        elseif (-not $summary.agent_settled) {
            'Pi 未到达 agent_settled'
        }
        elseif (-not $summary.structured_result_received) {
            'Pi 未通过 sacha_result 返回结构化结果'
        }
        elseif (
            -not [string]::IsNullOrWhiteSpace($Model) -and
            -not $Model.Equals([string]$summary.effective_model, [StringComparison]::OrdinalIgnoreCase)
        ) {
            "Pi effective model 与请求不一致：requested=$Model effective=$($summary.effective_model)"
        }
        else {
            "Pi 结果不是 completed：outcome=$($summary.outcome) blockers=$($summary.blockers -join '; ')"
        }
        $scriptExitCode = 3
    }
    else {
        $summary.status = 'candidate'
        $scriptExitCode = 0
    }
}
catch {
    $summary.status = 'precondition_failed'
    $summary.error = $_.Exception.Message
    $scriptExitCode = 2
}

$summaryJson = $summary | ConvertTo-Json -Depth 8 -Compress
Write-Output $summaryJson
exit $scriptExitCode
