[CmdletBinding()]
param(
    [string]$Root = (Get-Location).Path,
    [string]$Profile = 'docs',
    [string[]]$ChangedPath = @(),
    [string]$DiffDigestPath,
    [string]$PluginRoot = 'plugins/sacha-orchestra',
    [string]$PluginValidatorPath,
    [string]$Version,
    [string]$Phase = 'candidate',
    [string]$BuildWrapper,
    [switch]$RunBuild,
    [int]$TimeoutSeconds = 600,
    [int]$MaxChars = 6000,
    [switch]$Summary,
    [switch]$Details
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function Get-RelativePath {
    param(
        [Parameter(Mandatory)][string]$BasePath,
        [Parameter(Mandatory)][string]$TargetPath
    )

    if ([System.IO.Path].GetMethod('GetRelativePath', [type[]]@([string], [string]))) {
        return [System.IO.Path]::GetRelativePath($BasePath, $TargetPath)
    }
    $baseUri = [Uri]((Resolve-Path -LiteralPath $BasePath).Path.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar)
    $targetUri = [Uri]$TargetPath
    return [Uri]::UnescapeDataString($baseUri.MakeRelativeUri($targetUri).ToString()).Replace(
        '/',
        [System.IO.Path]::DirectorySeparatorChar
    )
}

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

function Resolve-SafeRelativePath {
    param(
        [Parameter(Mandatory)][string]$RootPath,
        [Parameter(Mandatory)][string]$InputPath,
        [switch]$MustExist
    )

    if (
        [string]::IsNullOrWhiteSpace($InputPath) -or
        $InputPath.StartsWith(':(') -or
        (($InputPath -split '[\\/]+') -contains '..')
    ) {
        throw "不安全或空路径：$InputPath"
    }
    $candidate = if ([System.IO.Path]::IsPathRooted($InputPath)) {
        [System.IO.Path]::GetFullPath($InputPath)
    }
    else {
        [System.IO.Path]::GetFullPath((Join-Path $RootPath $InputPath))
    }
    if (-not (Test-ContainedPath -RootPath $RootPath -CandidatePath $candidate)) {
        throw "路径不在 Root 内：$InputPath"
    }
    if ($MustExist -and -not (Test-Path -LiteralPath $candidate)) {
        throw "路径不存在：$InputPath"
    }
    return (Get-RelativePath -BasePath $RootPath -TargetPath $candidate).Replace('\', '/')
}

function Assert-NoReparsePoint {
    param([Parameter(Mandatory)][string]$InputPath)
    if (-not (Test-Path -LiteralPath $InputPath)) {
        return
    }
    $item = Get-Item -LiteralPath $InputPath -Force
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "拒绝在 reparse point 下写入：$InputPath"
    }
}

function Get-ExecutablePath {
    param([Parameter(Mandatory)][string]$Name)
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $command) {
        return $null
    }
    return $command.Source
}

function Invoke-LoggedProcess {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$Executable,
        [Parameter(Mandatory)][string[]]$Arguments,
        [Parameter(Mandatory)][string]$WorkingDirectory,
        [Parameter(Mandatory)][string]$RunDirectory,
        [Parameter(Mandatory)][int]$Timeout
    )

    $safeName = $Name -replace '[^A-Za-z0-9_.-]', '_'
    $stdoutPath = Join-Path $RunDirectory "$safeName.stdout.log"
    $stderrPath = Join-Path $RunDirectory "$safeName.stderr.log"
    $start = [DateTime]::UtcNow

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $Executable
    $startInfo.WorkingDirectory = $WorkingDirectory
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.CreateNoWindow = $true
    foreach ($argument in $Arguments) {
        $null = $startInfo.ArgumentList.Add($argument)
    }

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    $null = $process.Start()
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $completed = $process.WaitForExit($Timeout * 1000)
    $timedOut = -not $completed
    if ($timedOut) {
        try {
            $process.Kill($true)
        }
        catch {
            $process.Kill()
        }
        $process.WaitForExit()
    }
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()
    [System.IO.File]::WriteAllText($stdoutPath, $stdout, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText($stderrPath, $stderr, [System.Text.UTF8Encoding]::new($false))

    [pscustomobject]@{
        name        = $Name
        exit_code   = if ($timedOut) { $null } else { $process.ExitCode }
        timed_out   = $timedOut
        duration_ms = [int]([DateTime]::UtcNow - $start).TotalMilliseconds
        stdout      = $stdout
        stderr      = $stderr
        stdout_path = $stdoutPath
        stderr_path = $stderrPath
    }
}

function Convert-ProcessToCheck {
    param(
        [Parameter(Mandatory)]$ProcessResult,
        [Parameter(Mandatory)][string]$RootPath
    )

    $combined = @($ProcessResult.stderr, $ProcessResult.stdout) -join [Environment]::NewLine
    $signal = @($combined -split "`r?`n" | Where-Object { $_ } | Select-Object -First 4) -join ' | '
    if ($signal.Length -gt 400) {
        $signal = $signal.Substring(0, 400) + '…'
    }
    [pscustomobject]@{
        name        = $ProcessResult.name
        status      = if ($ProcessResult.timed_out) {
            'failed'
        }
        elseif ($ProcessResult.exit_code -eq 0) {
            'passed'
        }
        else {
            'failed'
        }
        exit_code   = $ProcessResult.exit_code
        timed_out   = $ProcessResult.timed_out
        duration_ms = $ProcessResult.duration_ms
        summary     = if ($signal) { $signal } elseif ($ProcessResult.exit_code -eq 0) { 'passed' } else { 'failed' }
        stdout      = (Get-RelativePath -BasePath $RootPath -TargetPath $ProcessResult.stdout_path).Replace('\', '/')
        stderr      = (Get-RelativePath -BasePath $RootPath -TargetPath $ProcessResult.stderr_path).Replace('\', '/')
    }
}

function New-SkippedCheck {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$Reason
    )
    [pscustomobject]@{
        name        = $Name
        status      = 'skipped'
        exit_code   = $null
        timed_out   = $false
        duration_ms = 0
        summary     = $Reason
        stdout      = $null
        stderr      = $null
    }
}

function Invoke-MarkdownLinkCheck {
    param(
        [Parameter(Mandatory)][string]$RootPath,
        [Parameter(Mandatory)][string[]]$MarkdownFiles,
        [Parameter(Mandatory)][string]$RunDirectory
    )

    $start = [DateTime]::UtcNow
    $broken = [System.Collections.Generic.List[string]]::new()
    foreach ($relative in $MarkdownFiles) {
        $full = Join-Path $RootPath $relative
        if (-not (Test-Path -LiteralPath $full -PathType Leaf)) {
            continue
        }
        $base = Split-Path -Parent $full
        $text = [System.IO.File]::ReadAllText($full)
        foreach ($match in [regex]::Matches($text, '\[[^\]]+\]\(([^)]+)\)')) {
            $target = $match.Groups[1].Value.Trim()
            if (
                -not $target -or
                $target.StartsWith('#') -or
                $target -match '^(?i:https?|mailto):'
            ) {
                continue
            }
            $pathPart = ($target -split '#', 2)[0]
            if (-not $pathPart) {
                continue
            }
            try {
                $decoded = [Uri]::UnescapeDataString($pathPart.Trim('<', '>'))
                $candidate = [System.IO.Path]::GetFullPath((Join-Path $base $decoded))
                if (-not (Test-ContainedPath -RootPath $RootPath -CandidatePath $candidate)) {
                    $broken.Add("$relative -> $target (outside Root)")
                }
                elseif (-not (Test-Path -LiteralPath $candidate)) {
                    $broken.Add("$relative -> $target")
                }
            }
            catch {
                $broken.Add("$relative -> $target (invalid)")
            }
        }
    }

    $stdoutPath = Join-Path $RunDirectory 'markdown_links.stdout.log'
    $stderrPath = Join-Path $RunDirectory 'markdown_links.stderr.log'
    [System.IO.File]::WriteAllLines($stdoutPath, @($broken), [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText($stderrPath, '', [System.Text.UTF8Encoding]::new($false))
    [pscustomobject]@{
        name        = 'markdown_links'
        status      = if ($broken.Count -eq 0) { 'passed' } else { 'failed' }
        exit_code   = if ($broken.Count -eq 0) { 0 } else { 1 }
        timed_out   = $false
        duration_ms = [int]([DateTime]::UtcNow - $start).TotalMilliseconds
        summary     = if ($broken.Count -eq 0) { "$($MarkdownFiles.Count) file(s), 0 broken" } else { "$($broken.Count) broken link(s)" }
        stdout      = (Get-RelativePath -BasePath $RootPath -TargetPath $stdoutPath).Replace('\', '/')
        stderr      = (Get-RelativePath -BasePath $RootPath -TargetPath $stderrPath).Replace('\', '/')
    }
}

function Convert-ToBoundedJson {
    param(
        [Parameter(Mandatory)]$Summary,
        [Parameter(Mandatory)][int]$CharacterBudget
    )

    $json = $Summary | ConvertTo-Json -Depth 10 -Compress
    if ($json.Length -le $CharacterBudget) {
        return $json
    }
    foreach ($check in $Summary.checks) {
        if ($check.summary.Length -gt 120) {
            $check.summary = $check.summary.Substring(0, 120) + '…'
        }
    }
    $Summary.truncated = $true
    $json = $Summary | ConvertTo-Json -Depth 10 -Compress
    while ($json.Length -gt $CharacterBudget -and $Summary.checks.Count -gt 0) {
        $removable = @($Summary.checks | Where-Object { $_.status -eq 'skipped' } | Select-Object -Last 1)
        if ($removable.Count -eq 0) {
            break
        }
        $removeName = $removable[0].name
        $Summary.checks = @($Summary.checks | Where-Object { $_.name -ne $removeName })
        $json = $Summary | ConvertTo-Json -Depth 10 -Compress
    }
    if ($json.Length -gt $CharacterBudget) {
        $minimalChecks = @($Summary.checks | ForEach-Object {
            [ordered]@{
                name      = $_.name
                status    = $_.status
                exit_code = $_.exit_code
                summary   = $_.summary
                stdout    = $_.stdout
                stderr    = $_.stderr
            }
        })
        $minimal = [ordered]@{
            status    = $Summary.status
            mode      = $Summary.mode
            profile   = $Summary.profile
            checks    = $minimalChecks
            failed    = $Summary.failed
            skipped   = $Summary.skipped
            timed_out = $Summary.timed_out
            truncated = $true
            raw_dir   = $Summary.raw_dir
        }
        $json = $minimal | ConvertTo-Json -Depth 8 -Compress
    }
    if ($json.Length -gt $CharacterBudget) {
        $signals = @($Summary.checks | Where-Object { $_.status -ne 'passed' } | ForEach-Object {
            $signalSummary = [string]$_.summary
            if ($signalSummary.Length -gt 80) {
                $signalSummary = $signalSummary.Substring(0, 80) + '…'
            }
            [ordered]@{
                name      = $_.name
                status    = $_.status
                exit_code = $_.exit_code
                summary   = $signalSummary
            }
        })
        $essential = [ordered]@{
            status       = $Summary.status
            mode         = $Summary.mode
            profile      = $Summary.profile
            checks       = @($Summary.checks | ForEach-Object {
                '{0}:{1}:{2}' -f $_.name, $_.status, $_.exit_code
            })
            signals      = $signals
            failed       = $Summary.failed
            skipped      = $Summary.skipped
            timed_out    = $Summary.timed_out
            truncated    = $true
            summary_mode = 'essential'
            raw_dir      = $Summary.raw_dir
        }
        $json = $essential | ConvertTo-Json -Depth 6 -Compress
    }
    if ($json.Length -gt $CharacterBudget) {
        throw "MaxChars=$CharacterBudget 太小，无法容纳检查结果"
    }
    return $json
}

$exitCode = 0
$resultSummary = $null
$detailsResult = $null
$rawRelative = $null

try {
    if ($Summary -and $Details) {
        throw '-Summary 与 -Details 不能同时使用'
    }
    if ($Profile -notin @('docs', 'plugin', 'unity', 'engine')) {
        throw "Profile 必须是 docs|plugin|unity|engine：$Profile"
    }
    if ($Phase -notin @('candidate', 'release')) {
        throw "Phase 必须是 candidate|release：$Phase"
    }
    if ($TimeoutSeconds -lt 1 -or $TimeoutSeconds -gt 86400) {
        throw 'TimeoutSeconds 必须在 1..86400'
    }
    if ($MaxChars -lt 1000 -or $MaxChars -gt 1000000) {
        throw 'MaxChars 必须在 1000..1000000'
    }
    if ($RunBuild -and [string]::IsNullOrWhiteSpace($BuildWrapper)) {
        throw '-RunBuild 必须同时提供 -BuildWrapper'
    }

    $rootPath = (Resolve-Path -LiteralPath $Root).Path
    $changed = @($ChangedPath | ForEach-Object {
        Resolve-SafeRelativePath -RootPath $rootPath -InputPath $_
    } | Sort-Object -Unique)

    $tempRoot = Join-Path $rootPath '.temp'
    Assert-NoReparsePoint -InputPath $tempRoot
    if (-not (Test-Path -LiteralPath $tempRoot)) {
        $null = New-Item -ItemType Directory -Path $tempRoot
    }
    $toolTempRoot = Join-Path $tempRoot 'change-closeout'
    Assert-NoReparsePoint -InputPath $toolTempRoot
    if (-not (Test-Path -LiteralPath $toolTempRoot)) {
        $null = New-Item -ItemType Directory -Path $toolTempRoot
    }
    $runId = '{0}-{1}' -f (Get-Date -Format 'yyyyMMdd-HHmmss'), ([Guid]::NewGuid().ToString('N').Substring(0, 8))
    $runDirectory = Join-Path $toolTempRoot $runId
    $null = New-Item -ItemType Directory -Path $runDirectory
    $rawRelative = (Get-RelativePath -BasePath $rootPath -TargetPath $runDirectory).Replace('\', '/')

    $checks = [System.Collections.Generic.List[object]]::new()
    $git = Get-ExecutablePath -Name 'git'
    $isGit = $false
    if ($git) {
        $probe = Invoke-LoggedProcess -Name 'git_probe' -Executable $git -Arguments @('-C', $rootPath, 'rev-parse', '--is-inside-work-tree') -WorkingDirectory $rootPath -RunDirectory $runDirectory -Timeout $TimeoutSeconds
        $isGit = -not $probe.timed_out -and $probe.exit_code -eq 0
    }

    if ($DiffDigestPath) {
        $digestPath = (Resolve-Path -LiteralPath $DiffDigestPath).Path
    }
    else {
        $candidateDigest = Join-Path $env:USERPROFILE '.codex\scripts\diff_digest.ps1'
        $digestPath = if (Test-Path -LiteralPath $candidateDigest) { $candidateDigest } else { $null }
    }
    $pwsh = Get-ExecutablePath -Name 'pwsh'
    if ($digestPath -and $pwsh) {
        $arguments = @('-NoProfile', '-File', $digestPath, '-Root', $rootPath, '-Mode', 'Summary')
        if ($changed.Count -gt 0) {
            $arguments += '-Path'
            $arguments += $changed
        }
        $result = Invoke-LoggedProcess -Name 'diff_digest' -Executable $pwsh -Arguments $arguments -WorkingDirectory $rootPath -RunDirectory $runDirectory -Timeout $TimeoutSeconds
        $checks.Add((Convert-ProcessToCheck -ProcessResult $result -RootPath $rootPath))
    }
    elseif ($isGit) {
        $result = Invoke-LoggedProcess -Name 'vcs_summary' -Executable $git -Arguments @('-C', $rootPath, 'status', '--short') -WorkingDirectory $rootPath -RunDirectory $runDirectory -Timeout $TimeoutSeconds
        $checks.Add((Convert-ProcessToCheck -ProcessResult $result -RootPath $rootPath))
    }
    else {
        $checks.Add((New-SkippedCheck -Name 'vcs_summary' -Reason 'diff_digest 与 Git 均不可用'))
    }

    if ($isGit) {
        $pathArguments = if ($changed.Count -gt 0) { @('--') + $changed } else { @() }
        $unstaged = Invoke-LoggedProcess -Name 'git_diff_check' -Executable $git -Arguments (@('-C', $rootPath, 'diff', '--check') + $pathArguments) -WorkingDirectory $rootPath -RunDirectory $runDirectory -Timeout $TimeoutSeconds
        $checks.Add((Convert-ProcessToCheck -ProcessResult $unstaged -RootPath $rootPath))
        $staged = Invoke-LoggedProcess -Name 'git_cached_diff_check' -Executable $git -Arguments (@('-C', $rootPath, 'diff', '--cached', '--check') + $pathArguments) -WorkingDirectory $rootPath -RunDirectory $runDirectory -Timeout $TimeoutSeconds
        $checks.Add((Convert-ProcessToCheck -ProcessResult $staged -RootPath $rootPath))
    }
    else {
        $checks.Add((New-SkippedCheck -Name 'git_diff_check' -Reason '非 Git 工作副本'))
        $checks.Add((New-SkippedCheck -Name 'git_cached_diff_check' -Reason '非 Git 工作副本'))
    }

    $markdownFiles = @(
        Get-ChildItem -LiteralPath $rootPath -Filter '*.md' -File -Recurse -Force |
            Where-Object {
                $relative = (Get-RelativePath -BasePath $rootPath -TargetPath $_.FullName).Replace('\', '/')
                -not ($relative.StartsWith('.git/') -or $relative.StartsWith('.temp/'))
            } |
            ForEach-Object { (Get-RelativePath -BasePath $rootPath -TargetPath $_.FullName).Replace('\', '/') }
    )
    $checks.Add((Invoke-MarkdownLinkCheck -RootPath $rootPath -MarkdownFiles $markdownFiles -RunDirectory $runDirectory))

    if ($Profile -eq 'plugin') {
        $python = Get-ExecutablePath -Name 'python'
        $projectSetup = Join-Path $rootPath 'tests\validate_project_setup.py'
        if ($python -and (Test-Path -LiteralPath $projectSetup)) {
            $result = Invoke-LoggedProcess -Name 'project_setup' -Executable $python -Arguments @('-B', $projectSetup) -WorkingDirectory $rootPath -RunDirectory $runDirectory -Timeout $TimeoutSeconds
            $checks.Add((Convert-ProcessToCheck -ProcessResult $result -RootPath $rootPath))
        }
        else {
            $checks.Add((New-SkippedCheck -Name 'project_setup' -Reason '未找到 python 或 tests/validate_project_setup.py'))
        }

        if ($PluginValidatorPath) {
            if (-not $python) {
                $checks.Add((New-SkippedCheck -Name 'plugin_validator' -Reason 'python 不可用'))
            }
            else {
                $validator = (Resolve-Path -LiteralPath $PluginValidatorPath).Path
                $pluginRelative = Resolve-SafeRelativePath -RootPath $rootPath -InputPath $PluginRoot -MustExist
                $result = Invoke-LoggedProcess -Name 'plugin_validator' -Executable $python -Arguments @('-B', $validator, (Join-Path $rootPath $pluginRelative)) -WorkingDirectory $rootPath -RunDirectory $runDirectory -Timeout $TimeoutSeconds
                $checks.Add((Convert-ProcessToCheck -ProcessResult $result -RootPath $rootPath))
            }
        }
        else {
            $checks.Add((New-SkippedCheck -Name 'plugin_validator' -Reason '未显式提供 -PluginValidatorPath'))
        }

        if ($Version) {
            $coherence = Join-Path $rootPath 'tests\validate_release_coherence.py'
            if ($python -and (Test-Path -LiteralPath $coherence)) {
                $result = Invoke-LoggedProcess -Name 'release_coherence' -Executable $python -Arguments @('-B', $coherence, '--version', $Version, '--phase', $Phase) -WorkingDirectory $rootPath -RunDirectory $runDirectory -Timeout $TimeoutSeconds
                $checks.Add((Convert-ProcessToCheck -ProcessResult $result -RootPath $rootPath))
            }
            else {
                $checks.Add((New-SkippedCheck -Name 'release_coherence' -Reason '未找到 python 或 release coherence validator'))
            }
        }
        else {
            $checks.Add((New-SkippedCheck -Name 'release_coherence' -Reason '未显式提供 -Version'))
        }
    }

    if ($BuildWrapper) {
        $wrapperRelative = Resolve-SafeRelativePath -RootPath $rootPath -InputPath $BuildWrapper -MustExist
        $extension = [System.IO.Path]::GetExtension($wrapperRelative).ToLowerInvariant()
        if ($extension -notin @('.bat', '.cmd', '.ps1')) {
            throw "BuildWrapper 只允许 .bat/.cmd/.ps1：$BuildWrapper"
        }
        if ($RunBuild) {
            if ($extension -eq '.ps1') {
                if (-not $pwsh) {
                    throw 'pwsh 不可用，无法运行 BuildWrapper'
                }
                $buildExecutable = $pwsh
                $buildArguments = @('-NoProfile', '-File', (Join-Path $rootPath $wrapperRelative))
            }
            else {
                $cmd = Get-ExecutablePath -Name 'cmd.exe'
                if (-not $cmd) {
                    throw 'cmd.exe 不可用，无法运行 BuildWrapper'
                }
                $buildExecutable = $cmd
                $buildArguments = @('/d', '/s', '/c', ('"{0}"' -f (Join-Path $rootPath $wrapperRelative)))
            }
            $result = Invoke-LoggedProcess -Name 'build_wrapper' -Executable $buildExecutable -Arguments $buildArguments -WorkingDirectory $rootPath -RunDirectory $runDirectory -Timeout $TimeoutSeconds
            $checks.Add((Convert-ProcessToCheck -ProcessResult $result -RootPath $rootPath))
        }
        else {
            $checks.Add((New-SkippedCheck -Name 'build_wrapper' -Reason '已提供 wrapper，但未指定 -RunBuild'))
        }
    }
    elseif ($Profile -in @('unity', 'engine')) {
        $checks.Add((New-SkippedCheck -Name 'build_wrapper' -Reason "Profile=$Profile 未提供 BuildWrapper；未执行领域构建"))
    }

    $failed = @($checks | Where-Object { $_.status -eq 'failed' })
    $skipped = @($checks | Where-Object { $_.status -eq 'skipped' })
    $timedOut = @($checks | Where-Object { $_.timed_out })
    if ($timedOut.Count -gt 0) {
        $exitCode = 3
    }
    elseif ($failed.Count -gt 0) {
        $exitCode = 1
    }
    $resultSummary = [ordered]@{
        status    = if ($exitCode -eq 3) { 'timed_out' } elseif ($exitCode -eq 1) { 'failed' } elseif ($skipped.Count -gt 0) { 'partial' } else { 'passed' }
        mode      = 'summary'
        profile   = $Profile
        checks    = @($checks)
        failed    = $failed.Count
        skipped   = $skipped.Count
        timed_out = $timedOut.Count
        truncated = $false
        raw_dir   = $rawRelative
    }
    $detailsResult = [ordered]@{
        status        = $resultSummary.status
        mode          = 'details'
        profile       = $Profile
        root          = $rootPath
        changed_paths = $changed
        checks        = @($checks)
        failed        = $resultSummary.failed
        skipped       = $resultSummary.skipped
        timed_out     = $resultSummary.timed_out
        raw_dir       = $rawRelative
    }
    [System.IO.File]::WriteAllText(
        (Join-Path $runDirectory 'result.full.json'),
        ($detailsResult | ConvertTo-Json -Depth 10),
        [System.Text.UTF8Encoding]::new($false)
    )
}
catch {
    $exitCode = 2
    $resultSummary = [ordered]@{
        status    = 'error'
        mode      = if ($Details) { 'details' } else { 'summary' }
        profile   = $Profile
        checks    = @()
        failed    = 0
        skipped   = 0
        timed_out = 0
        truncated = $false
        raw_dir   = $rawRelative
        error     = $_.Exception.Message
    }
}

try {
    if ($Details -and $detailsResult) {
        $json = $detailsResult | ConvertTo-Json -Depth 10 -Compress
    }
    else {
        $json = Convert-ToBoundedJson -Summary $resultSummary -CharacterBudget $MaxChars
    }
}
catch {
    $exitCode = 2
    $json = ([ordered]@{
        status    = 'error'
        mode      = if ($Details) { 'details' } else { 'summary' }
        profile   = $Profile
        checks    = @()
        error     = $_.Exception.Message
        truncated = $true
        raw_dir   = $rawRelative
    } | ConvertTo-Json -Depth 4 -Compress)
}

[Console]::Out.WriteLine($json)
exit $exitCode
