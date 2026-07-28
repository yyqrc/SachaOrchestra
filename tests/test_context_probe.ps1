[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$toolPath = Join-Path $repositoryRoot 'plugins\sacha-orchestra\scripts\context_probe.ps1'
$pwsh = (Get-Command pwsh -ErrorAction Stop).Source
$testParent = Join-Path $repositoryRoot '.temp\tests'
$testRoot = Join-Path $testParent ('context-probe-' + [Guid]::NewGuid().ToString('N'))

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
    $null = New-Item -ItemType Directory -Path (Join-Path $testRoot 'src')
    [System.IO.File]::WriteAllText(
        (Join-Path $testRoot '.gitignore'),
        ".temp/`n",
        [System.Text.UTF8Encoding]::new($false)
    )
    [System.IO.File]::WriteAllText(
        (Join-Path $testRoot 'src\one.txt'),
        "first`nunique-needle`n中文唯一锚点`nlast`n",
        [System.Text.UTF8Encoding]::new($false)
    )
    [System.IO.File]::WriteAllText(
        (Join-Path $testRoot 'src\many.txt'),
        ((1..120 | ForEach-Object { "many-needle $_" }) -join "`n") + "`n",
        [System.Text.UTF8Encoding]::new($false)
    )
    [System.IO.File]::WriteAllText(
        (Join-Path $testRoot 'AGENTS.md'),
        "RULE_SECRET_TOKEN`n",
        [System.Text.UTF8Encoding]::new($false)
    )
    & git -C $testRoot init --quiet
    & git -C $testRoot config user.email 'test@example.invalid'
    & git -C $testRoot config user.name 'Context Probe Test'
    & git -C $testRoot add .
    & git -C $testRoot commit --quiet -m init

    $default = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Path', 'src',
        '-Query', 'unique-needle',
        '-MaxChars', '2000'
    )
    Assert-True ($default.code -eq 0) 'default summary 应成功'
    Assert-True ($default.data.mode -eq 'summary') 'default 必须是 summary'
    Assert-True ($default.data.matches -eq 1) '唯一查询应返回 1 个 match'
    Assert-True ($default.data.snippets.Count -eq 1) '唯一 locator 应展开一个 snippet'
    Assert-True ($default.text.Length -le 2000) 'summary 必须受 MaxChars 限制'
    Assert-True (Test-Path -LiteralPath (Join-Path $testRoot $default.data.raw_dir)) 'raw_dir 必须存在'

    $singleFile = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Path', 'src\one.txt',
        '-Query', '中文唯一锚点',
        '-MaxChars', '2000'
    )
    Assert-True ($singleFile.code -eq 0) '单文件中文查询应成功'
    Assert-True ($singleFile.data.matches -eq 1) '单文件中文查询应返回 1 个 match'
    Assert-True ($singleFile.data.locators[0] -eq 'src/one.txt:3') '单文件 locator 错误'

    $explicitSummary = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Path', 'src',
        '-Query', 'unique-needle',
        '-Summary',
        '-MaxChars', '2000'
    )
    Assert-True ($explicitSummary.code -eq 0) '显式 Summary 应成功'
    Assert-True ($explicitSummary.data.mode -eq 'summary') '显式 Summary mode 错误'
    Assert-True ($explicitSummary.data.matches -eq $default.data.matches) '默认与显式 Summary 的统计应相同'

    $details = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Path', 'src',
        '-Query', 'unique-needle',
        '-Details'
    )
    Assert-True ($details.code -eq 0) 'Details 应成功'
    Assert-True ($details.data.mode -eq 'details') 'Details mode 错误'
    Assert-True ($details.data.files.Count -ge 2) 'Details 应包含逐文件清单'
    Assert-True ($details.data.matches.Count -eq 1) 'Details 应包含逐 match 数组'

    $rule = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Path', '.',
        '-Query', 'RULE_SECRET_TOKEN'
    )
    Assert-True ($rule.code -eq 0) '规则 locator 查询应成功'
    Assert-True ($rule.data.snippets.Count -eq 1) '规则查询应返回 locator'
    Assert-True ([bool]$rule.data.snippets[0].locator_only) '规则文件必须 locator-only'
    Assert-True ($rule.data.snippets[0].lines.Count -eq 0) '规则正文不得进入 summary'
    Assert-True (-not $rule.text.Contains('RULE_SECRET_TOKEN')) 'summary 不得泄漏规则正文'

    $bounded = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Path', 'src',
        '-Query', 'many-needle',
        '-MaxChars', '700'
    )
    Assert-True ($bounded.code -eq 0) '大结果 summary 应成功'
    Assert-True ($bounded.text.Length -le 700) '大结果必须受预算限制'
    Assert-True ([bool]$bounded.data.truncated) '大结果必须标记 truncated'
    Assert-True ($bounded.data.omitted_matches -gt 0) '大结果必须报告 omitted_matches'

    $conflict = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Summary',
        '-Details'
    )
    Assert-True ($conflict.code -eq 2) 'Summary+Details 必须返回参数错误 2'
    Assert-True ($conflict.data.status -eq 'error') '参数错误仍必须返回 JSON'

    $outside = Invoke-Tool -Arguments @(
        '-Root', $testRoot,
        '-Path', $repositoryRoot
    )
    Assert-True ($outside.code -eq 2) 'Root 外路径必须拒绝'

    $savedPath = $env:PATH
    try {
        $env:PATH = "$PSHOME;$env:SystemRoot\System32"
        $fallback = Invoke-Tool -Arguments @(
            '-Root', $testRoot,
            '-Path', 'src',
            '-Query', 'unique-needle'
        )
    }
    finally {
        $env:PATH = $savedPath
    }
    Assert-True ($fallback.code -eq 0) '缺少 rg/git 时应降级成功'
    Assert-True ($fallback.data.status -eq 'warning') '降级必须明确 warning'
    Assert-True (($fallback.data.warnings -join ' ').Contains('rg')) '降级摘要应标记 rg 不可用'

    $status = @(& git -C $testRoot status --short)
    Assert-True ($status.Count -eq 0) '工具默认只允许 .temp 日志，不应修改受控文件'

    Write-Output 'context_probe_tests=passed'
}
finally {
    $resolvedParent = [System.IO.Path]::GetFullPath($testParent).TrimEnd('\', '/')
    $resolvedTest = [System.IO.Path]::GetFullPath($testRoot)
    if ($resolvedTest.StartsWith($resolvedParent + [System.IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        Remove-Item -LiteralPath $resolvedTest -Recurse -Force -ErrorAction SilentlyContinue
    }
}
