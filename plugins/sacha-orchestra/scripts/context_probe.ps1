[CmdletBinding()]
param(
    [string]$Root = (Get-Location).Path,
    [string[]]$Query = @(),
    [string[]]$Path = @('.'),
    [string[]]$Anchor = @(),
    [string[]]$Include = @(),
    [string[]]$Exclude = @(),
    [int]$Context = 2,
    [int]$MaxLines = 80,
    [int]$MaxChars = 6000,
    [switch]$Regex,
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
    $targetUri = [Uri](Resolve-Path -LiteralPath $TargetPath).Path
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

    $prefix = $rootFull + [System.IO.Path]::DirectorySeparatorChar
    return $candidateFull.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)
}

function Resolve-ContainedExistingPath {
    param(
        [Parameter(Mandatory)][string]$RootPath,
        [Parameter(Mandatory)][string]$InputPath
    )

    if ([string]::IsNullOrWhiteSpace($InputPath) -or $InputPath.StartsWith(':(')) {
        throw "不安全或空路径：$InputPath"
    }

    $candidate = if ([System.IO.Path]::IsPathRooted($InputPath)) {
        $InputPath
    }
    else {
        Join-Path $RootPath $InputPath
    }
    $resolved = (Resolve-Path -LiteralPath $candidate).Path
    if (-not (Test-ContainedPath -RootPath $RootPath -CandidatePath $resolved)) {
        throw "路径不在 Root 内：$InputPath"
    }
    return $resolved
}

function Assert-SafeGlob {
    param([Parameter(Mandatory)][string]$Pattern)

    if (
        [string]::IsNullOrWhiteSpace($Pattern) -or
        [System.IO.Path]::IsPathRooted($Pattern) -or
        $Pattern.StartsWith(':(') -or
        (($Pattern -split '[\\/]+') -contains '..')
    ) {
        throw "不安全的 include/exclude：$Pattern"
    }
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

function Invoke-CapturedCommand {
    param(
        [Parameter(Mandatory)][string]$Executable,
        [Parameter(Mandatory)][string[]]$Arguments,
        [Parameter(Mandatory)][string]$WorkingDirectory
    )

    $started = [DateTime]::UtcNow
    Push-Location -LiteralPath $WorkingDirectory
    try {
        $lines = @(& $Executable @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
    $text = ($lines | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine
    [pscustomobject]@{
        exit_code   = $exitCode
        duration_ms = [int]([DateTime]::UtcNow - $started).TotalMilliseconds
        text        = $text
    }
}

function Test-IncludedFile {
    param(
        [Parameter(Mandatory)][string]$RelativePath,
        [AllowEmptyCollection()][string[]]$IncludePattern,
        [AllowEmptyCollection()][string[]]$ExcludePattern
    )

    $normalized = $RelativePath.Replace('\', '/')
    if ($IncludePattern.Count -gt 0) {
        $included = $false
        foreach ($pattern in $IncludePattern) {
            if ($normalized -like $pattern.Replace('\', '/')) {
                $included = $true
                break
            }
        }
        if (-not $included) {
            return $false
        }
    }
    foreach ($pattern in $ExcludePattern) {
        if ($normalized -like $pattern.Replace('\', '/')) {
            return $false
        }
    }
    return $true
}

function Test-RuleFile {
    param([Parameter(Mandatory)][string]$InputPath)
    $name = [System.IO.Path]::GetFileName($InputPath)
    return $name.Equals('AGENTS.md', [StringComparison]::OrdinalIgnoreCase) -or
        $name.Equals('SKILL.md', [StringComparison]::OrdinalIgnoreCase)
}

function Get-Snippet {
    param(
        [Parameter(Mandatory)][string]$RootPath,
        [Parameter(Mandatory)][string]$FilePath,
        [Parameter(Mandatory)][int]$Line,
        [Parameter(Mandatory)][int]$Radius,
        [Parameter(Mandatory)][int]$RemainingLines
    )

    $relative = (Get-RelativePath -BasePath $RootPath -TargetPath $FilePath).Replace('\', '/')
    if (Test-RuleFile -InputPath $FilePath) {
        return [pscustomobject]@{
            locator     = "${relative}:$Line"
            locator_only = $true
            start       = $Line
            end         = $Line
            lines       = @()
        }
    }

    $allLines = @([System.IO.File]::ReadLines($FilePath))
    if ($Line -lt 1 -or $Line -gt [Math]::Max($allLines.Count, 1)) {
        throw "Anchor 行号越界：${relative}:$Line"
    }
    $start = [Math]::Max(1, $Line - $Radius)
    $end = [Math]::Min($allLines.Count, $Line + $Radius)
    if ($RemainingLines -le 0) {
        $end = $start - 1
    }
    elseif (($end - $start + 1) -gt $RemainingLines) {
        $end = $start + $RemainingLines - 1
    }
    $content = @()
    if ($end -ge $start) {
        for ($index = $start; $index -le $end; $index++) {
            $content += ('{0}: {1}' -f $index, $allLines[$index - 1])
        }
    }
    [pscustomobject]@{
        locator      = "${relative}:$Line"
        locator_only = $false
        start        = $start
        end          = $end
        lines        = $content
    }
}

function Convert-ToBoundedJson {
    param(
        [Parameter(Mandatory)]$Summary,
        [Parameter(Mandatory)][int]$CharacterBudget
    )

    $json = $Summary | ConvertTo-Json -Depth 10 -Compress
    while ($json.Length -gt $CharacterBudget -and $Summary.snippets.Count -gt 0) {
        $Summary.snippets = @($Summary.snippets | Select-Object -First ($Summary.snippets.Count - 1))
        $Summary.truncated = $true
        $json = $Summary | ConvertTo-Json -Depth 10 -Compress
    }
    while ($json.Length -gt $CharacterBudget -and $Summary.locators.Count -gt 0) {
        $Summary.locators = @($Summary.locators | Select-Object -First ($Summary.locators.Count - 1))
        $Summary.truncated = $true
        $json = $Summary | ConvertTo-Json -Depth 10 -Compress
    }
    if ($json.Length -gt $CharacterBudget) {
        $Summary.warnings = @($Summary.warnings | Select-Object -First 3 | ForEach-Object {
            if ($_.Length -gt 160) { $_.Substring(0, 160) + '…' } else { $_ }
        })
        $Summary.truncated = $true
        $json = $Summary | ConvertTo-Json -Depth 10 -Compress
    }
    if ($json.Length -gt $CharacterBudget) {
        $minimal = [ordered]@{
            status          = $Summary.status
            mode            = $Summary.mode
            vcs             = $Summary.vcs
            files           = $Summary.files
            matches         = $Summary.matches
            changed         = $Summary.changed
            snippets        = @()
            locators        = @()
            warnings        = @('摘要超过预算；读取 raw_dir')
            truncated       = $true
            omitted_matches = $Summary.matches
            raw_dir         = $Summary.raw_dir
        }
        $json = $minimal | ConvertTo-Json -Depth 5 -Compress
    }
    if ($json.Length -gt $CharacterBudget) {
        throw "MaxChars=$CharacterBudget 太小，无法容纳最小 JSON"
    }
    return $json
}

$exitCode = 0
$resultSummary = $null
$detailsResult = $null
$rootPath = $null
$rawRelative = $null

try {
    if ($Summary -and $Details) {
        throw '-Summary 与 -Details 不能同时使用'
    }
    if ($Context -lt 0 -or $Context -gt 20) {
        throw 'Context 必须在 0..20'
    }
    if ($MaxLines -lt 1 -or $MaxLines -gt 1000) {
        throw 'MaxLines 必须在 1..1000'
    }
    if ($MaxChars -lt 512 -or $MaxChars -gt 1000000) {
        throw 'MaxChars 必须在 512..1000000'
    }

    $rootPath = (Resolve-Path -LiteralPath $Root).Path
    foreach ($pattern in @($Include) + @($Exclude)) {
        Assert-SafeGlob -Pattern $pattern
    }
    $resolvedTargets = @($Path | ForEach-Object {
        Resolve-ContainedExistingPath -RootPath $rootPath -InputPath $_
    })

    $tempRoot = Join-Path $rootPath '.temp'
    Assert-NoReparsePoint -InputPath $tempRoot
    if (-not (Test-Path -LiteralPath $tempRoot)) {
        $null = New-Item -ItemType Directory -Path $tempRoot
    }
    $toolTempRoot = Join-Path $tempRoot 'context-probe'
    Assert-NoReparsePoint -InputPath $toolTempRoot
    if (-not (Test-Path -LiteralPath $toolTempRoot)) {
        $null = New-Item -ItemType Directory -Path $toolTempRoot
    }
    $runId = '{0}-{1}' -f (Get-Date -Format 'yyyyMMdd-HHmmss'), ([Guid]::NewGuid().ToString('N').Substring(0, 8))
    $runDirectory = Join-Path $toolTempRoot $runId
    $null = New-Item -ItemType Directory -Path $runDirectory
    $rawRelative = (Get-RelativePath -BasePath $rootPath -TargetPath $runDirectory).Replace('\', '/')

    $warnings = [System.Collections.Generic.List[string]]::new()
    $vcs = 'none'
    $statusText = ''
    $inventory = @()
    $targetRelative = @($resolvedTargets | ForEach-Object {
        $relative = Get-RelativePath -BasePath $rootPath -TargetPath $_
        if ($relative -eq '') { '.' } else { $relative }
    })

    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) {
        $probe = Invoke-CapturedCommand -Executable $git.Source -Arguments @('-C', $rootPath, 'rev-parse', '--is-inside-work-tree') -WorkingDirectory $rootPath
        if ($probe.exit_code -eq 0) {
            $vcs = 'git'
            $status = Invoke-CapturedCommand -Executable $git.Source -Arguments @('-C', $rootPath, 'status', '--short', '--untracked-files=normal') -WorkingDirectory $rootPath
            $statusText = $status.text
            $listArguments = @('-C', $rootPath, 'ls-files', '-co', '--exclude-standard', '--') + $targetRelative
            $listed = Invoke-CapturedCommand -Executable $git.Source -Arguments $listArguments -WorkingDirectory $rootPath
            if ($listed.exit_code -ne 0) {
                throw "git ls-files 失败：$($listed.text)"
            }
            $inventory = @($listed.text -split "`r?`n" | Where-Object { $_ })
        }
    }

    if ($vcs -eq 'none') {
        $svn = Get-Command svn -ErrorAction SilentlyContinue
        if ($svn) {
            $probe = Invoke-CapturedCommand -Executable $svn.Source -Arguments @('info', $rootPath) -WorkingDirectory $rootPath
            if ($probe.exit_code -eq 0) {
                $vcs = 'svn'
                $status = Invoke-CapturedCommand -Executable $svn.Source -Arguments @('status', $rootPath) -WorkingDirectory $rootPath
                $statusText = $status.text
            }
        }
    }

    if ($inventory.Count -eq 0) {
        if ($vcs -eq 'none') {
            $warnings.Add('未检测到 Git/SVN；文件清单使用只读 filesystem fallback')
        }
        $files = [System.Collections.Generic.List[string]]::new()
        foreach ($target in $resolvedTargets) {
            $item = Get-Item -LiteralPath $target -Force
            if (-not $item.PSIsContainer) {
                $files.Add((Get-RelativePath -BasePath $rootPath -TargetPath $item.FullName))
                continue
            }
            foreach ($file in Get-ChildItem -LiteralPath $item.FullName -File -Recurse -Force -ErrorAction SilentlyContinue) {
                if (($file.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                    continue
                }
                $relative = Get-RelativePath -BasePath $rootPath -TargetPath $file.FullName
                $segments = $relative -split '[\\/]+'
                if ($segments -contains '.git' -or $segments -contains '.svn' -or $segments -contains '.temp') {
                    continue
                }
                $files.Add($relative)
            }
        }
        $inventory = @($files | Sort-Object -Unique)
    }

    $inventory = @($inventory | Where-Object {
        Test-IncludedFile -RelativePath $_ -IncludePattern $Include -ExcludePattern $Exclude
    } | Sort-Object -Unique)
    [System.IO.File]::WriteAllLines((Join-Path $runDirectory 'inventory.txt'), $inventory, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText((Join-Path $runDirectory 'vcs-status.txt'), $statusText, [System.Text.UTF8Encoding]::new($false))

    $matches = [System.Collections.Generic.List[object]]::new()
    $rg = Get-Command rg -ErrorAction SilentlyContinue
    for ($queryIndex = 0; $queryIndex -lt $Query.Count; $queryIndex++) {
        $queryText = $Query[$queryIndex]
        if ([string]::IsNullOrWhiteSpace($queryText)) {
            throw 'Query 不能为空'
        }
        $queryMatches = @()
        if ($rg) {
            $arguments = @('-n', '--column', '--with-filename', '--no-heading', '--color', 'never')
            if (-not $Regex) {
                $arguments += '-F'
            }
            foreach ($pattern in $Include) {
                $arguments += @('-g', $pattern)
            }
            foreach ($pattern in $Exclude) {
                $arguments += @('-g', "!$pattern")
            }
            $arguments += @('--', $queryText)
            $arguments += $targetRelative
            $search = Invoke-CapturedCommand -Executable $rg.Source -Arguments $arguments -WorkingDirectory $rootPath
            [System.IO.File]::WriteAllText(
                (Join-Path $runDirectory ('search-{0:D3}.txt' -f ($queryIndex + 1))),
                $search.text,
                [System.Text.UTF8Encoding]::new($false)
            )
            if ($search.exit_code -notin @(0, 1)) {
                $warnings.Add("rg 查询失败：$queryText")
            }
            foreach ($line in $search.text -split "`r?`n") {
                $match = [regex]::Match($line, '^(.*?):(\d+):(\d+):(.*)$')
                if (-not $match.Success) {
                    continue
                }
                $relative = $match.Groups[1].Value.Replace('\', '/')
                $queryMatches += [pscustomobject]@{
                    query   = $queryText
                    path    = $relative
                    line    = [int]$match.Groups[2].Value
                    column  = [int]$match.Groups[3].Value
                    locator = '{0}:{1}' -f $relative, $match.Groups[2].Value
                }
            }
        }
        else {
            $warnings.Add('rg 不可用；使用 Select-String fallback')
            foreach ($relative in $inventory) {
                $full = Join-Path $rootPath $relative
                if (-not (Test-Path -LiteralPath $full -PathType Leaf)) {
                    continue
                }
                try {
                    $found = if ($Regex) {
                        Select-String -LiteralPath $full -Pattern $queryText -AllMatches -ErrorAction Stop
                    }
                    else {
                        Select-String -LiteralPath $full -SimpleMatch -Pattern $queryText -AllMatches -ErrorAction Stop
                    }
                    foreach ($entry in $found) {
                        $queryMatches += [pscustomobject]@{
                            query   = $queryText
                            path    = $relative.Replace('\', '/')
                            line    = $entry.LineNumber
                            column  = 1
                            locator = '{0}:{1}' -f $relative.Replace('\', '/'), $entry.LineNumber
                        }
                    }
                }
                catch {
                    continue
                }
            }
        }
        foreach ($entry in $queryMatches) {
            $matches.Add($entry)
        }
    }

    $snippets = [System.Collections.Generic.List[object]]::new()
    $usedLines = 0
    foreach ($queryText in $Query) {
        $queryMatches = @($matches | Where-Object { $_.query -eq $queryText })
        if ($queryMatches.Count -ne 1) {
            continue
        }
        $match = $queryMatches[0]
        $full = Resolve-ContainedExistingPath -RootPath $rootPath -InputPath $match.path
        $snippet = Get-Snippet -RootPath $rootPath -FilePath $full -Line $match.line -Radius $Context -RemainingLines ($MaxLines - $usedLines)
        $snippets.Add($snippet)
        $usedLines += $snippet.lines.Count
    }

    foreach ($anchorText in $Anchor) {
        $anchorMatch = [regex]::Match($anchorText, '^(.*?)(?::(\d+)|#L(\d+))$')
        if (-not $anchorMatch.Success) {
            throw "Anchor 必须是 path:line 或 path#Lline：$anchorText"
        }
        $lineNumber = if ($anchorMatch.Groups[2].Success) {
            [int]$anchorMatch.Groups[2].Value
        }
        else {
            [int]$anchorMatch.Groups[3].Value
        }
        $full = Resolve-ContainedExistingPath -RootPath $rootPath -InputPath $anchorMatch.Groups[1].Value
        $snippet = Get-Snippet -RootPath $rootPath -FilePath $full -Line $lineNumber -Radius $Context -RemainingLines ($MaxLines - $usedLines)
        $snippets.Add($snippet)
        $usedLines += $snippet.lines.Count
    }

    $fullMatches = @($matches)
    $detailsResult = [ordered]@{
        status       = if ($warnings.Count -gt 0) { 'warning' } else { 'ok' }
        mode         = 'details'
        root         = $rootPath
        vcs          = $vcs
        file_count   = $inventory.Count
        files        = $inventory
        changed      = @($statusText -split "`r?`n" | Where-Object { $_ })
        match_count  = $fullMatches.Count
        matches      = $fullMatches
        snippets     = @($snippets)
        warnings     = @($warnings)
        raw_dir      = $rawRelative
    }
    [System.IO.File]::WriteAllText(
        (Join-Path $runDirectory 'result.full.json'),
        ($detailsResult | ConvertTo-Json -Depth 10),
        [System.Text.UTF8Encoding]::new($false)
    )

    $locatorLimit = [Math]::Min(50, $fullMatches.Count)
    $locators = @()
    if ($locatorLimit -gt 0) {
        $locators = @($fullMatches | Select-Object -First $locatorLimit | ForEach-Object { $_.locator })
    }
    $changedLines = @($statusText -split "`r?`n" | Where-Object { $_ })
    $resultSummary = [ordered]@{
        status          = if ($warnings.Count -gt 0) { 'warning' } else { 'ok' }
        mode            = 'summary'
        vcs             = $vcs
        files           = $inventory.Count
        matches         = $fullMatches.Count
        changed         = $changedLines.Count
        snippets        = @($snippets)
        locators        = $locators
        warnings        = @($warnings)
        truncated       = ($fullMatches.Count -gt $locatorLimit) -or ($usedLines -ge $MaxLines)
        omitted_matches = [Math]::Max(0, $fullMatches.Count - $locatorLimit)
        raw_dir         = $rawRelative
    }
}
catch {
    $exitCode = 2
    $resultSummary = [ordered]@{
        status          = 'error'
        mode            = if ($Details) { 'details' } else { 'summary' }
        vcs             = 'unknown'
        files           = 0
        matches         = 0
        changed         = 0
        snippets        = @()
        locators        = @()
        warnings        = @($_.Exception.Message)
        truncated       = $false
        omitted_matches = 0
        raw_dir         = $rawRelative
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
        warnings  = @($_.Exception.Message)
        raw_dir   = $rawRelative
        truncated = $true
    } | ConvertTo-Json -Depth 3 -Compress)
}

[Console]::Out.WriteLine($json)
exit $exitCode
