[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Root,
    [Parameter(Mandatory)][string]$PromptPath,
    [Parameter(Mandatory)][string]$ExpectedHead,
    [Parameter(Mandatory)][string[]]$WritePath,
    [string[]]$ReadPath = @(),
    [string]$ClaudePath = 'claude',
    [ValidateSet('sonnet', 'opus', 'fable')][string]$Model = 'sonnet',
    [ValidateSet('low', 'medium', 'high', 'xhigh', 'max')][string]$Effort = 'high',
    [ValidateRange(30, 86400)][int]$TimeoutSeconds = 1800,
    [ValidateRange(0, 1000000)][decimal]$MaxBudgetUsd = 0,
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
    throw "ClaudePath 必须解析为 .ps1 或 .exe：$source"
}

function Invoke-Process {
    param(
        [Parameter(Mandatory)]$CommandInfo,
        [Parameter(Mandatory)][string[]]$Arguments,
        [Parameter(Mandatory)][string]$WorkingDirectory,
        [AllowEmptyString()][string]$StandardInput = '',
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
    status              = 'error'
    run_id              = $RunId
    model               = $Model
    effort              = $Effort
    claude_version      = $null
    capabilities_verified = $false
    claude_exit_code    = $null
    timed_out           = $false
    duration_ms         = 0
    head_before         = $null
    head_after          = $null
    changed_files       = @()
    scope_violations    = @()
    ignored_scope_violations = @()
    git_metadata_changed = $false
    stdout_json_valid   = $false
    raw_dir             = $null
    error               = $null
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

    $rawPath = Join-Path $rootPath ('.temp\sacha-claude\' + $RunId)
    $rawParent = Split-Path -Parent $rawPath
    Assert-NoReparseAncestor -RootPath $rootPath -CandidatePath $rawParent
    $null = New-Item -ItemType Directory -Path $rawParent -Force
    if (Test-Path -LiteralPath $rawPath) {
        throw "RunId 已存在：$RunId"
    }
    $null = New-Item -ItemType Directory -Path $rawPath
    $summary.raw_dir = (Get-RelativePath -BasePath $rootPath -TargetPath $rawPath)

    $commandInfo = Resolve-Command -Command $ClaudePath
    $versionResult = Invoke-Process `
        -CommandInfo $commandInfo `
        -Arguments @('--version') `
        -WorkingDirectory $rootPath `
        -TimeoutMilliseconds 20000
    if ($versionResult.exit_code -ne 0) {
        throw "claude --version 失败：$($versionResult.stderr.Trim())"
    }
    $summary.claude_version = $versionResult.stdout.Trim()
    $helpResult = Invoke-Process `
        -CommandInfo $commandInfo `
        -Arguments @('--help') `
        -WorkingDirectory $rootPath `
        -TimeoutMilliseconds 20000
    if ($helpResult.exit_code -ne 0) {
        throw "claude --help 失败：$($helpResult.stderr.Trim())"
    }
    foreach ($marker in @(
        '--print',
        '--safe-mode',
        '--no-session-persistence',
        '--json-schema',
        '--permission-mode',
        '--allowedTools',
        '--tools',
        '--prompt-suggestions',
        '--effort',
        '--model'
    )) {
        if (-not $helpResult.stdout.Contains($marker)) {
            throw "当前 Claude CLI 不支持所需能力：$marker"
        }
    }
    $summary.capabilities_verified = $true

    $schema = [ordered]@{
        type                 = 'object'
        additionalProperties = $false
        properties           = [ordered]@{
            outcome  = @{ type = 'string'; enum = @('completed', 'blocked', 'failed') }
            summary  = @{ type = 'string' }
            blockers = @{ type = 'array'; items = @{ type = 'string' } }
        }
        required             = @('outcome', 'summary')
    } | ConvertTo-Json -Depth 8 -Compress

    $allowedTools = @()
    foreach ($path in $readPaths) {
        $permissionPath = '/' + $path.TrimStart('/')
        $allowedTools += @("Read($permissionPath)", "Read($permissionPath/**)")
    }
    foreach ($path in $allowedPaths) {
        $permissionPath = '/' + $path.TrimStart('/')
        $allowedTools += @("Edit($permissionPath)", "Edit($permissionPath/**)")
    }
    $arguments = @(
        '-p',
        '--safe-mode',
        '--no-session-persistence',
        '--disable-slash-commands',
        '--no-chrome',
        '--prompt-suggestions', 'false',
        '--permission-mode', 'dontAsk',
        '--model', $Model,
        '--effort', $Effort,
        '--output-format', 'json',
        '--json-schema', $schema,
        '--tools', 'Read,Edit,Write',
        '--allowedTools'
    ) + $allowedTools + @(
        '--append-system-prompt',
        'You are a one-shot implementation worker. Use only the allowed paths, do not create commits or alter Git metadata, stop instead of requesting interaction, and return only the required structured result.'
    )
    if ($MaxBudgetUsd -gt 0) {
        $arguments += @('--max-budget-usd', $MaxBudgetUsd.ToString([Globalization.CultureInfo]::InvariantCulture))
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
        -StandardInput $prompt `
        -TimeoutMilliseconds ($TimeoutSeconds * 1000)

    $summary.claude_exit_code = $result.exit_code
    $summary.timed_out = $result.timed_out
    $summary.duration_ms = $result.duration_ms
    [System.IO.File]::WriteAllText(
        (Join-Path $rawPath 'stdout.json'),
        $result.stdout,
        [System.Text.UTF8Encoding]::new($false)
    )
    [System.IO.File]::WriteAllText(
        (Join-Path $rawPath 'stderr.txt'),
        $result.stderr,
        [System.Text.UTF8Encoding]::new($false)
    )
    try {
        $null = $result.stdout | ConvertFrom-Json
        $summary.stdout_json_valid = $true
    }
    catch {
        $summary.stdout_json_valid = $false
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
            "Claude 写出允许范围：$($scopeViolations -join ', ')"
        }
        elseif ($summary.git_metadata_changed) {
            'Claude 改变了 linked worktree Git metadata'
        }
        elseif ($postGitError) {
            "Claude 破坏了 linked worktree Git 状态：$postGitError"
        }
        else {
            'Claude 改变了 worktree HEAD'
        }
        $scriptExitCode = 4
    }
    elseif ($result.timed_out -or $result.exit_code -ne 0 -or -not $summary.stdout_json_valid) {
        $summary.status = 'claude_failed'
        $summary.error = if ($result.timed_out) {
            "Claude 超过 TimeoutSeconds=$TimeoutSeconds"
        }
        elseif ($result.exit_code -ne 0) {
            "Claude 退出码：$($result.exit_code)"
        }
        else {
            'Claude stdout 不是合法 JSON'
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
