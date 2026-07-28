[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$toolPath = Join-Path $repositoryRoot 'plugins\sacha-orchestra\scripts\change_closeout.ps1'
$pwsh = (Get-Command pwsh -ErrorAction Stop).Source
$testParent = Join-Path $repositoryRoot '.temp\tests'
$testRoot = Join-Path $testParent ('change-closeout-' + [Guid]::NewGuid().ToString('N'))

function Assert-True {
    param(
        [Parameter(Mandatory)][bool]$Condition,
        [Parameter(Mandatory)][string]$Message
    )
    if (-not $Condition) {
        throw $Message
    }
}

function Invoke-Tool {
    param([Parameter(Mandatory)][string[]]$Arguments)
    $raw = @(& $pwsh -NoProfile -File $toolPath @Arguments)
    $code = $LASTEXITCODE
    $text = $raw -join [Environment]::NewLine
    try {
        $data = $text | ConvertFrom-Json
    }
    catch {
        throw "输出不是合法 JSON：$text"
    }
    [pscustomobject]@{
        code = $code
        text = $text
        data = $data
    }
}

$null = New-Item -ItemType Directory -Path $testRoot
try {
    [System.IO.File]::WriteAllText(
        (Join-Path $testRoot '.gitignore'),
        ".temp/`nbuild-ran.txt`n",
        [System.Text.UTF8Encoding]::new($false)
    )
    [System.IO.File]::WriteAllText(
        (Join-Path $testRoot 'target.md'),
        "# Target`n",
        [System.Text.UTF8Encoding]::new($false)
    )
    [System.IO.File]::WriteAllText(
        (Join-Path $testRoot 'README.md'),
        "# Test`n`n[Target](target.md)`n",
        [System.Text.UTF8Encoding]::new($false)
    )
    [System.IO.File]::WriteAllText(
        (Join-Path $testRoot 'build.ps1'),
        "[System.IO.File]::WriteAllText((Join-Path `$PSScriptRoot 'build-ran.txt'),'ran')`n",
        [System.Text.UTF8Encoding]::new($false)
    )
    & git -C $testRoot init --quiet
    & git -C $testRoot config user.email 'test@example.invalid'
    & git -C $testRoot config user.name 'Change Closeout Test'
    & git -C $testRoot add .
    & git -C $testRoot commit --quiet -m init

    $default = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Profile', 'docs',
        '-ChangedPath', 'README.md'
    )
    Assert-True ($default.code -eq 0) '干净 docs closeout 应成功'
    Assert-True ($default.data.mode -eq 'summary') '默认必须是 summary'
    Assert-True ($default.data.failed -eq 0) '干净 closeout 不应失败'
    Assert-True (Test-Path -LiteralPath (Join-Path $testRoot $default.data.raw_dir)) 'raw_dir 必须存在'
    Assert-True (($default.data.checks.name) -contains 'git_diff_check') '必须检查 unstaged whitespace'
    Assert-True (($default.data.checks.name) -contains 'git_cached_diff_check') '必须检查 staged whitespace'

    $explicitSummary = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Profile', 'docs',
        '-ChangedPath', 'README.md',
        '-Summary'
    )
    Assert-True ($explicitSummary.code -eq 0) '显式 Summary 应成功'
    Assert-True ($explicitSummary.data.mode -eq 'summary') '显式 Summary mode 错误'
    Assert-True ($explicitSummary.data.checks.Count -eq $default.data.checks.Count) '默认与显式 Summary 的检查数应相同'

    $lowBudget = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Profile', 'docs',
        '-ChangedPath', 'README.md',
        '-MaxChars', '1000'
    )
    Assert-True ($lowBudget.code -eq 0) '合法的最小 MaxChars 应返回有界摘要'
    Assert-True ($lowBudget.text.Length -le 1000) '最小预算摘要不得超过 MaxChars'
    Assert-True ($lowBudget.data.status -eq 'passed') '最小预算摘要必须保留总体状态'
    Assert-True ($lowBudget.data.failed -eq 0) '最小预算摘要必须保留失败计数'
    Assert-True ($lowBudget.data.checks.Count -eq $default.data.checks.Count) '最小预算摘要必须保留全部检查状态'

    $details = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Profile', 'docs',
        '-ChangedPath', 'README.md',
        '-Details'
    )
    Assert-True ($details.code -eq 0) 'Details 应成功'
    Assert-True ($details.data.mode -eq 'details') 'Details mode 错误'
    Assert-True ($details.data.changed_paths[0] -eq 'README.md') 'Details 应包含 changed_paths'

    [System.IO.File]::AppendAllText(
        (Join-Path $testRoot 'README.md'),
        "trailing whitespace   `n",
        [System.Text.UTF8Encoding]::new($false)
    )
    $unstagedFailure = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Profile', 'docs',
        '-ChangedPath', 'README.md'
    )
    Assert-True ($unstagedFailure.code -eq 1) 'unstaged whitespace 应返回检查失败 1'
    $unstagedCheck = @($unstagedFailure.data.checks | Where-Object name -eq 'git_diff_check')[0]
    Assert-True ($unstagedCheck.status -eq 'failed') 'unstaged whitespace 检查必须失败'

    & git -C $testRoot add README.md
    $stagedFailure = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Profile', 'docs',
        '-ChangedPath', 'README.md'
    )
    Assert-True ($stagedFailure.code -eq 1) 'staged whitespace 应返回检查失败 1'
    $stagedCheck = @($stagedFailure.data.checks | Where-Object name -eq 'git_cached_diff_check')[0]
    Assert-True ($stagedCheck.status -eq 'failed') 'staged whitespace 检查必须失败'
    & git -C $testRoot reset --quiet HEAD README.md
    & git -C $testRoot checkout --quiet -- README.md

    [System.IO.File]::AppendAllText(
        (Join-Path $testRoot 'README.md'),
        "`n[Missing](missing.md)`n",
        [System.Text.UTF8Encoding]::new($false)
    )
    $linkFailure = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Profile', 'docs',
        '-ChangedPath', 'README.md'
    )
    Assert-True ($linkFailure.code -eq 1) '断链应返回检查失败 1'
    $linkCheck = @($linkFailure.data.checks | Where-Object name -eq 'markdown_links')[0]
    Assert-True ($linkCheck.status -eq 'failed') 'markdown_links 必须失败'
    & git -C $testRoot checkout --quiet -- README.md

    Move-Item -LiteralPath (Join-Path $testRoot 'target.md') -Destination (Join-Path $testRoot 'renamed.md')
    $incomingLinkFailure = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Profile', 'docs',
        '-ChangedPath', 'target.md'
    )
    Assert-True ($incomingLinkFailure.code -eq 1) '删除或重命名链接目标应返回检查失败 1'
    $incomingLinkCheck = @($incomingLinkFailure.data.checks | Where-Object name -eq 'markdown_links')[0]
    Assert-True ($incomingLinkCheck.status -eq 'failed') '全仓入链检查必须发现未改消费者断链'
    Move-Item -LiteralPath (Join-Path $testRoot 'renamed.md') -Destination (Join-Path $testRoot 'target.md')

    $unityPartial = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Profile', 'unity',
        '-ChangedPath', 'README.md'
    )
    Assert-True ($unityPartial.code -eq 0) '未授权构建不应把 Unity closeout 变成命令失败'
    Assert-True ($unityPartial.data.status -eq 'partial') '未执行领域构建时顶层必须是 partial'
    $unityBuildCheck = @($unityPartial.data.checks | Where-Object name -eq 'build_wrapper')[0]
    Assert-True ($unityBuildCheck.status -eq 'skipped') 'Unity profile 缺少 wrapper 时必须显式 skipped'

    $wrapperSkipped = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Profile', 'docs',
        '-ChangedPath', 'README.md',
        '-BuildWrapper', 'build.ps1'
    )
    Assert-True ($wrapperSkipped.code -eq 0) '只提供 wrapper 不应失败'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $testRoot 'build-ran.txt'))) '没有 RunBuild 时不得执行 wrapper'
    $buildCheck = @($wrapperSkipped.data.checks | Where-Object name -eq 'build_wrapper')[0]
    Assert-True ($buildCheck.status -eq 'skipped') '没有 RunBuild 时必须标记 skipped'
    Assert-True ($wrapperSkipped.data.status -eq 'partial') '存在 skipped check 时顶层必须是 partial'

    $wrapperRun = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Profile', 'docs',
        '-ChangedPath', 'README.md',
        '-BuildWrapper', 'build.ps1',
        '-RunBuild'
    )
    Assert-True ($wrapperRun.code -eq 0) '显式 RunBuild 应执行成功'
    Assert-True (Test-Path -LiteralPath (Join-Path $testRoot 'build-ran.txt')) '显式 RunBuild 应产生 marker'

    $conflict = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Summary',
        '-Details'
    )
    Assert-True ($conflict.code -eq 2) 'Summary+Details 必须返回参数错误 2'
    Assert-True ($conflict.data.status -eq 'error') '参数错误仍必须返回 JSON'

    $savedUserProfile = $env:USERPROFILE
    try {
        $fakeProfile = Join-Path $testRoot 'no-diff-digest-home'
        $null = New-Item -ItemType Directory -Path $fakeProfile
        $env:USERPROFILE = $fakeProfile
        $fallback = Invoke-Tool -Arguments @(
            '-Root', $testRoot,
            '-Profile', 'docs',
            '-ChangedPath', 'README.md'
        )
    }
    finally {
        $env:USERPROFILE = $savedUserProfile
    }
    Assert-True ($fallback.code -eq 0) '缺少 diff_digest 时应降级到 Git'
    Assert-True (($fallback.data.checks.name) -contains 'vcs_summary') '降级摘要应包含 vcs_summary'

    Write-Output 'change_closeout_tests=passed'
}
finally {
    $resolvedParent = [System.IO.Path]::GetFullPath($testParent).TrimEnd('\', '/')
    $resolvedTest = [System.IO.Path]::GetFullPath($testRoot)
    if ($resolvedTest.StartsWith($resolvedParent + [System.IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        Remove-Item -LiteralPath $resolvedTest -Recurse -Force -ErrorAction SilentlyContinue
    }
}
