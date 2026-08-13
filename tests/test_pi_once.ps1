[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$toolPath = Join-Path $repositoryRoot 'plugins\sacha-orchestra\scripts\pi_once.ps1'
$pwsh = (Get-Command pwsh -ErrorAction Stop).Source
$testParent = Join-Path $repositoryRoot '.temp\tests'
$testRoot = Join-Path $testParent ('pi-once-' + [Guid]::NewGuid().ToString('N'))
$mainRoot = Join-Path $testRoot 'repo'
$fakePi = Join-Path $testRoot 'fake-pi.ps1'
$worktrees = [System.Collections.Generic.List[string]]::new()

function Assert-True {
    param(
        [Parameter(Mandatory)][bool]$Condition,
        [Parameter(Mandatory)][string]$Message
    )
    if (-not $Condition) {
        throw $Message
    }
}

function Assert-Contained {
    param(
        [Parameter(Mandatory)][string]$Parent,
        [Parameter(Mandatory)][string]$Child
    )
    $parentFull = [System.IO.Path]::GetFullPath($Parent).TrimEnd('\', '/')
    $childFull = [System.IO.Path]::GetFullPath($Child)
    if (-not $childFull.StartsWith(
        $parentFull + [System.IO.Path]::DirectorySeparatorChar,
        [StringComparison]::OrdinalIgnoreCase
    )) {
        throw "测试清理路径越界：$childFull"
    }
}

function New-LinkedWorktree {
    param([Parameter(Mandatory)][string]$Name)

    $path = Join-Path $testRoot $Name
    & git -C $mainRoot worktree add --quiet --detach $path HEAD
    if ($LASTEXITCODE -ne 0) {
        throw "无法创建测试 worktree：$Name"
    }
    $worktrees.Add($path)
    $promptDir = Join-Path $path '.temp'
    $null = New-Item -ItemType Directory -Path $promptDir -Force
    [System.IO.File]::WriteAllText(
        (Join-Path $promptDir 'packet.md'),
        "目标：写入 src/out.txt。`n范围：只修改 src/out.txt。`n完成：返回结构化结果。`n",
        [System.Text.UTF8Encoding]::new($false)
    )
    return $path
}

function Invoke-Helper {
    param(
        [Parameter(Mandatory)][string]$Worktree,
        [string]$ExpectedHead,
        [string[]]$ReadPath = @('src/base.txt'),
        [string[]]$WritePath = @('src/out.txt'),
        [string]$PromptPath,
        [AllowEmptyString()][string]$Model = 'test-provider/standard-model',
        [string]$Mode = 'success'
    )

    if ([string]::IsNullOrWhiteSpace($ExpectedHead)) {
        $ExpectedHead = (& git -C $Worktree rev-parse HEAD).Trim()
    }
    if ([string]::IsNullOrWhiteSpace($PromptPath)) {
        $PromptPath = Join-Path $Worktree '.temp\packet.md'
    }
    $savedMode = $env:SACHA_FAKE_PI_MODE
    try {
        $env:SACHA_FAKE_PI_MODE = $Mode
        $arguments = @(
            '-NoProfile',
            '-File', $toolPath,
            '-Root', $Worktree,
            '-PromptPath', $PromptPath,
            '-ExpectedHead', $ExpectedHead,
            '-ReadPath'
        ) + $ReadPath + @(
            '-WritePath'
        ) + $WritePath + @(
            '-PiPath', $fakePi,
            '-RunId', ('test-' + [Guid]::NewGuid().ToString('N')),
            '-TimeoutSeconds', '30'
        )
        if (-not [string]::IsNullOrWhiteSpace($Model)) {
            $arguments += @('-Model', $Model)
        }
        $raw = @(& $pwsh @arguments)
        $code = $LASTEXITCODE
    }
    finally {
        $env:SACHA_FAKE_PI_MODE = $savedMode
    }
    $text = $raw -join [Environment]::NewLine
    try {
        $data = $text | ConvertFrom-Json
    }
    catch {
        throw "helper 输出不是合法 JSON：$text"
    }
    return [pscustomobject]@{
        code = $code
        text = $text
        data = $data
    }
}

$null = New-Item -ItemType Directory -Path $mainRoot -Force
try {
    [System.IO.File]::WriteAllText(
        $fakePi,
        @'
if ($args -contains '--version') {
    Write-Output 'fake-pi 1.0'
    exit 0
}
if ($args -contains '--help') {
    Write-Output '--print --no-session --mode --model --thinking --tools --extension --no-extensions --no-skills --no-prompt-templates --no-context-files --no-approve --append-system-prompt'
    exit 0
}

$captureDir = Join-Path (Get-Location).Path '.temp'
$null = New-Item -ItemType Directory -Path $captureDir -Force
[System.IO.File]::WriteAllText(
    (Join-Path $captureDir 'fake-args.json'),
    ($args | ConvertTo-Json -Compress),
    [System.Text.UTF8Encoding]::new($false)
)
$promptReference = @($args | Where-Object { $_ -is [string] -and $_.StartsWith('@') })[-1]
$prompt = if ($promptReference) {
    [System.IO.File]::ReadAllText($promptReference.Substring(1), [System.Text.Encoding]::UTF8)
}
else {
    ''
}
[System.IO.File]::WriteAllText(
    (Join-Path $captureDir 'fake-prompt.md'),
    $prompt,
    [System.Text.UTF8Encoding]::new($false)
)
[System.IO.File]::WriteAllText(
    (Join-Path $captureDir 'fake-scope.json'),
    (@{
        root = $env:SACHA_PI_ROOT
        read = $env:SACHA_PI_READ_PATHS_JSON
        write = $env:SACHA_PI_WRITE_PATHS_JSON
    } | ConvertTo-Json -Compress),
    [System.Text.UTF8Encoding]::new($false)
)

switch ($env:SACHA_FAKE_PI_MODE) {
    'scope' {
        [System.IO.File]::WriteAllText(
            (Join-Path (Get-Location).Path 'outside.txt'),
            "outside`n",
            [System.Text.UTF8Encoding]::new($false)
        )
    }
    'staged-scope' {
        [System.IO.File]::WriteAllText(
            (Join-Path (Get-Location).Path 'outside.txt'),
            "staged outside`n",
            [System.Text.UTF8Encoding]::new($false)
        )
        & git add outside.txt
    }
    'ignored-scope' {
        $target = Join-Path (Get-Location).Path 'ignored\outside.txt'
        $null = New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force
        [System.IO.File]::WriteAllText(
            $target,
            "ignored outside`n",
            [System.Text.UTF8Encoding]::new($false)
        )
    }
    'head-change' {
        & git -c user.email=test@example.invalid -c user.name=Fake commit --allow-empty -m fake
    }
    'git-metadata' {
        $gitDirectory = (& git rev-parse --absolute-git-dir).Trim()
        [System.IO.File]::WriteAllText(
            (Join-Path $gitDirectory 'sacha-test-marker'),
            "changed`n",
            [System.Text.UTF8Encoding]::new($false)
        )
    }
    'fail' {
        [Console]::Error.WriteLine('fake failure')
        exit 7
    }
    'invalid-json' {
        Write-Output 'not-json'
        exit 0
    }
    default {
        $target = Join-Path (Get-Location).Path 'src\out.txt'
        $null = New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force
        [System.IO.File]::WriteAllText(
            $target,
            "generated`n",
            [System.Text.UTF8Encoding]::new($false)
        )
    }
}

@{ type = 'agent_start' } | ConvertTo-Json -Compress
$modelIndex = [Array]::IndexOf($args, '--model')
$effectiveModel = if ($env:SACHA_FAKE_PI_MODE -eq 'model-mismatch') {
    'other-provider/other-model'
}
elseif ($modelIndex -ge 0) {
    $args[$modelIndex + 1]
}
else {
    'runtime-provider/runtime-default'
}
$modelParts = $effectiveModel -split '/', 2
@{
    type = 'message_start'
    message = @{
        role = 'assistant'
        provider = $modelParts[0]
        model = $modelParts[1]
    }
} | ConvertTo-Json -Compress -Depth 4
if ($env:SACHA_FAKE_PI_MODE -ne 'no-result') {
    $outcome = if ($env:SACHA_FAKE_PI_MODE -eq 'blocked') { 'blocked' } else { 'completed' }
    $blockers = if ($outcome -eq 'blocked') { @('fake blocker') } else { @() }
    @{
        type = 'tool_execution_end'
        toolCallId = 'result-1'
        toolName = 'sacha_result'
        result = @{
            content = @(@{ type = 'text'; text = 'fake result' })
            details = @{
                outcome = $outcome
                summary = 'fake result'
                blockers = $blockers
            }
        }
        isError = $false
    } | ConvertTo-Json -Compress -Depth 8
}
@{ type = 'agent_end'; messages = @(); willRetry = $false } | ConvertTo-Json -Compress -Depth 8
@{ type = 'agent_settled' } | ConvertTo-Json -Compress
exit 0
'@,
        [System.Text.UTF8Encoding]::new($false)
    )
    [System.IO.File]::WriteAllText(
        (Join-Path $mainRoot '.gitignore'),
        ".temp/`nignored/`n",
        [System.Text.UTF8Encoding]::new($false)
    )
    $null = New-Item -ItemType Directory -Path (Join-Path $mainRoot 'src')
    [System.IO.File]::WriteAllText(
        (Join-Path $mainRoot 'src\base.txt'),
        "base`n",
        [System.Text.UTF8Encoding]::new($false)
    )
    & git -C $mainRoot init --quiet
    & git -C $mainRoot config core.autocrlf false
    & git -C $mainRoot config user.email 'test@example.invalid'
    & git -C $mainRoot config user.name 'Pi Once Test'
    & git -C $mainRoot add .
    & git -C $mainRoot commit --quiet -m init

    $primaryPromptDir = Join-Path $mainRoot '.temp'
    $null = New-Item -ItemType Directory -Path $primaryPromptDir
    [System.IO.File]::WriteAllText(
        (Join-Path $primaryPromptDir 'packet.md'),
        "primary must fail`n",
        [System.Text.UTF8Encoding]::new($false)
    )
    $primary = Invoke-Helper -Worktree $mainRoot
    Assert-True ($primary.code -eq 2) '主 worktree 必须拒绝'
    Assert-True ($primary.data.status -eq 'precondition_failed') '主 worktree 应是前置条件失败'

    $successRoot = New-LinkedWorktree -Name 'worktree-success'
    $success = Invoke-Helper -Worktree $successRoot
    Assert-True ($success.code -eq 0) "成功的待合入结果应返回 0：$($success.text)"
    Assert-True ($success.data.status -eq 'candidate') '成功结果必须使用机器状态 `candidate`'
    Assert-True ($success.data.changed_files.Count -eq 1) '成功结果应只有一个变更文件'
    Assert-True ($success.data.changed_files[0] -eq 'src/out.txt') '成功结果文件错误'
    Assert-True ($success.data.scope_violations.Count -eq 0) '成功结果不应越界'
    Assert-True ([bool]$success.data.stdout_json_valid) '成功 stdout 必须是 JSONL'
    Assert-True ([bool]$success.data.agent_settled) '成功结果必须到达 agent_settled'
    Assert-True ([bool]$success.data.structured_result_received) '成功结果必须包含 sacha_result'
    Assert-True ($success.data.outcome -eq 'completed') '成功结果 outcome 错误'
    Assert-True ([bool]$success.data.capabilities_verified) '成功前必须核对 CLI 能力'
    Assert-True ($success.data.requested_model -eq 'test-provider/standard-model') '请求型号未进入摘要'
    Assert-True ($success.data.effective_model -eq 'test-provider/standard-model') '实际型号未进入摘要'
    Assert-True (Test-Path -LiteralPath (Join-Path $successRoot $success.data.raw_dir 'stdout.jsonl')) '必须保留 stdout path'
    $capturedArgs = [System.IO.File]::ReadAllText((Join-Path $successRoot '.temp\fake-args.json'))
    foreach ($required in @(
        '-p',
        '--no-session',
        '--mode',
        'json',
        '--no-extensions',
        '--extension',
        'pi_guard.mjs',
        '--no-skills',
        '--no-prompt-templates',
        '--no-context-files',
        '--no-approve',
        '--thinking',
        'read,edit,write,sacha_result'
    )) {
        Assert-True ($capturedArgs.Contains($required)) "Pi 参数缺少：$required"
    }
    $capturedArgList = @($capturedArgs | ConvertFrom-Json)
    $toolsIndex = [Array]::IndexOf($capturedArgList, '--tools')
    Assert-True ($toolsIndex -ge 0) 'Pi 参数缺少 --tools'
    Assert-True ($capturedArgList[$toolsIndex + 1] -eq 'read,edit,write,sacha_result') 'Pi 工具 allowlist 不精确'
    $capturedPrompt = [System.IO.File]::ReadAllText((Join-Path $successRoot '.temp\fake-prompt.md'))
    Assert-True ($capturedPrompt.Contains('只修改 src/out.txt')) "Prompt 未通过 @file 完整传递：$capturedPrompt"
    $capturedScope = [System.IO.File]::ReadAllText((Join-Path $successRoot '.temp\fake-scope.json')) | ConvertFrom-Json
    Assert-True ($capturedScope.root -eq $successRoot) 'Pi guard Root 未通过子进程环境传递'
    Assert-True ($capturedScope.read.Contains('src/base.txt')) 'Pi guard ReadPath 未传递'
    Assert-True ($capturedScope.write.Contains('src/out.txt')) 'Pi guard WritePath 未传递'

    foreach ($model in @(
        'test-provider/pro-model',
        'test-provider/lite-deepseek-model',
        'test-provider/lite-gpt-model'
    )) {
        $modelName = ($model -split '/')[-1]
        $modelRoot = New-LinkedWorktree -Name ('worktree-model-' + $modelName)
        $modelResult = Invoke-Helper -Worktree $modelRoot -Model $model
        Assert-True ($modelResult.code -eq 0) "$model 候选应返回 0：$($modelResult.text)"
        Assert-True ($modelResult.data.requested_model -eq $model) "$model 未进入请求摘要"
        Assert-True ($modelResult.data.effective_model -eq $model) "$model 未进入实际摘要"
        $modelArgs = [System.IO.File]::ReadAllText((Join-Path $modelRoot '.temp\fake-args.json'))
        Assert-True ($modelArgs.Contains($model)) "$model 未传给 Pi CLI"
    }

    $defaultModelRoot = New-LinkedWorktree -Name 'worktree-runtime-default'
    $defaultModel = Invoke-Helper -Worktree $defaultModelRoot -Model $null
    Assert-True ($defaultModel.code -eq 0) "Runtime default 候选应返回 0：$($defaultModel.text)"
    Assert-True ([string]::IsNullOrWhiteSpace([string]$defaultModel.data.requested_model)) '省略型号时 requested_model 应为空'
    Assert-True ($defaultModel.data.effective_model -eq 'runtime-provider/runtime-default') 'Runtime default 实际型号未记录'
    $defaultArgs = [System.IO.File]::ReadAllText((Join-Path $defaultModelRoot '.temp\fake-args.json')) | ConvertFrom-Json
    Assert-True (-not (@($defaultArgs) -contains '--model')) '未配置型号时不得传 --model'

    $mismatchRoot = New-LinkedWorktree -Name 'worktree-model-mismatch'
    $mismatch = Invoke-Helper -Worktree $mismatchRoot -Mode 'model-mismatch'
    Assert-True ($mismatch.code -eq 3) '实际型号不一致必须返回 3'
    Assert-True ($mismatch.data.status -eq 'pi_failed') '型号不一致必须标记 pi_failed'
    Assert-True ($mismatch.data.error.Contains('effective model 与请求不一致')) '型号不一致诊断不明确'

    $scopeRoot = New-LinkedWorktree -Name 'worktree-scope'
    $scope = Invoke-Helper -Worktree $scopeRoot -Mode 'scope'
    Assert-True ($scope.code -eq 4) '越界写入必须返回 4'
    Assert-True ($scope.data.status -eq 'containment_failed') '越界写入必须标记 containment_failed'
    Assert-True ($scope.data.scope_violations[0] -eq 'outside.txt') '越界文件识别错误'

    $stagedScopeRoot = New-LinkedWorktree -Name 'worktree-staged-scope'
    $stagedScope = Invoke-Helper -Worktree $stagedScopeRoot -Mode 'staged-scope'
    Assert-True ($stagedScope.code -eq 4) '暂存的越界写入必须返回 4'
    Assert-True ($stagedScope.data.scope_violations[0] -eq 'outside.txt') '暂存越界文件未识别'

    $ignoredScopeRoot = New-LinkedWorktree -Name 'worktree-ignored-scope'
    $ignoredScope = Invoke-Helper -Worktree $ignoredScopeRoot -Mode 'ignored-scope'
    Assert-True ($ignoredScope.code -eq 4) 'ignored 越界写入必须返回 4'
    Assert-True ($ignoredScope.data.scope_violations[0] -eq 'ignored/outside.txt') 'ignored 越界文件未识别'

    $headChangeRoot = New-LinkedWorktree -Name 'worktree-head-change'
    $headChange = Invoke-Helper -Worktree $headChangeRoot -Mode 'head-change'
    Assert-True ($headChange.code -eq 4) '运行中改变 HEAD 必须返回 4'
    Assert-True ([bool]$headChange.data.git_metadata_changed) 'HEAD 改变必须标记 Git metadata 变化'

    $metadataRoot = New-LinkedWorktree -Name 'worktree-git-metadata'
    $metadata = Invoke-Helper -Worktree $metadataRoot -Mode 'git-metadata'
    Assert-True ($metadata.code -eq 4) 'Git metadata 写入必须返回 4'
    Assert-True ([bool]$metadata.data.git_metadata_changed) 'Git metadata 写入未识别'

    $dirtyRoot = New-LinkedWorktree -Name 'worktree-dirty'
    [System.IO.File]::WriteAllText(
        (Join-Path $dirtyRoot 'src\dirty.txt'),
        "dirty`n",
        [System.Text.UTF8Encoding]::new($false)
    )
    $dirty = Invoke-Helper -Worktree $dirtyRoot
    Assert-True ($dirty.code -eq 2) '脏基线必须拒绝'
    Assert-True ($dirty.data.error.Contains('不是干净基线')) '脏基线错误不明确'

    $headRoot = New-LinkedWorktree -Name 'worktree-head'
    $wrongHead = Invoke-Helper -Worktree $headRoot -ExpectedHead ('0' * 40)
    Assert-True ($wrongHead.code -eq 2) '错误 HEAD 必须拒绝'
    Assert-True ($wrongHead.data.error.Contains('ExpectedHead 不匹配')) '错误 HEAD 诊断不明确'

    $externalInput = Join-Path $testRoot 'external-input.txt'
    [System.IO.File]::WriteAllText($externalInput, "external`n", [System.Text.UTF8Encoding]::new($false))
    $outsideInputRoot = New-LinkedWorktree -Name 'worktree-outside-input'
    $outsideInput = Invoke-Helper -Worktree $outsideInputRoot -ReadPath @($externalInput)
    Assert-True ($outsideInput.code -eq 2) 'Root 外 ReadPath 必须拒绝'
    Assert-True ($outsideInput.data.error.Contains('不安全的 ReadPath')) 'Root 外 ReadPath 诊断不明确'

    foreach ($unsafePath in @(
        '*',
        'src/[base].txt',
        '.TEMP/child',
        '.TEMP /child',
        'src/file:stream',
        'src/file.',
        'NUL',
        'COM¹',
        'LPT².txt'
    )) {
        $unsafeName = 'worktree-unsafe-' + [Guid]::NewGuid().ToString('N')
        $unsafeRoot = New-LinkedWorktree -Name $unsafeName
        $unsafe = Invoke-Helper -Worktree $unsafeRoot -ReadPath @($unsafePath)
        Assert-True ($unsafe.code -eq 2) "危险 ReadPath 必须拒绝：$unsafePath"
        Assert-True ($unsafe.data.error.Contains('ReadPath')) "危险 ReadPath 诊断不明确：$unsafePath"
        Assert-True (-not (Test-Path -LiteralPath (Join-Path $unsafeRoot '.temp\fake-args.json'))) "危险 ReadPath 不得启动 Pi：$unsafePath"
    }

    $outsidePromptRoot = New-LinkedWorktree -Name 'worktree-outside-prompt'
    $outsidePrompt = Invoke-Helper -Worktree $outsidePromptRoot -PromptPath $externalInput
    Assert-True ($outsidePrompt.code -eq 2) 'Root 外 PromptPath 必须拒绝'
    Assert-True ($outsidePrompt.data.error.Contains('PromptPath 必须位于 Root 内')) 'Root 外 PromptPath 诊断不明确'

    $failureRoot = New-LinkedWorktree -Name 'worktree-failure'
    $failure = Invoke-Helper -Worktree $failureRoot -Mode 'fail'
    Assert-True ($failure.code -eq 3) 'Pi 失败必须返回 3'
    Assert-True ($failure.data.status -eq 'pi_failed') 'Pi 失败状态错误'
    Assert-True ($failure.data.pi_exit_code -eq 7) 'Pi 原始退出码丢失'

    $invalidRoot = New-LinkedWorktree -Name 'worktree-invalid-json'
    $invalid = Invoke-Helper -Worktree $invalidRoot -Mode 'invalid-json'
    Assert-True ($invalid.code -eq 3) '非法 JSON 必须返回 3'
    Assert-True (-not [bool]$invalid.data.stdout_json_valid) '非法 JSON 不得标记有效'

    $missingResultRoot = New-LinkedWorktree -Name 'worktree-no-result'
    $missingResult = Invoke-Helper -Worktree $missingResultRoot -Mode 'no-result'
    Assert-True ($missingResult.code -eq 3) '缺少 sacha_result 必须返回 3'
    Assert-True (-not [bool]$missingResult.data.structured_result_received) '缺少结果不得标记已收到'

    $blockedRoot = New-LinkedWorktree -Name 'worktree-blocked'
    $blocked = Invoke-Helper -Worktree $blockedRoot -Mode 'blocked'
    Assert-True ($blocked.code -eq 3) 'blocked outcome 必须返回 3'
    Assert-True ($blocked.data.outcome -eq 'blocked') 'blocked outcome 丢失'
    Assert-True (@($blocked.data.blockers) -contains 'fake blocker') 'blocked 原因丢失'

    Write-Output 'pi_once_tests=passed'
}
finally {
    foreach ($worktree in $worktrees) {
        Assert-Contained -Parent $testRoot -Child $worktree
        if (Test-Path -LiteralPath $worktree) {
            & git -C $mainRoot worktree remove --force $worktree 2>$null
        }
    }
    Assert-Contained -Parent $testParent -Child $testRoot
    if (Test-Path -LiteralPath $testRoot) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}
