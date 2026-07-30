[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$inspector = Join-Path $root 'plugins\sacha-orchestra\skills\setup-project\scripts\inspect_pi_models.ps1'
$tempParent = Join-Path $root '.temp\tests'
$tempRoot = Join-Path $tempParent ('pi-inspect-' + [Guid]::NewGuid().ToString('N'))
$fakePi = Join-Path $tempRoot 'fake-pi.ps1'

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) {
        throw $Message
    }
}

$null = New-Item -ItemType Directory -Path $tempRoot -Force
try {
    [System.IO.File]::WriteAllText(
        $fakePi,
        @'
if ($args -contains '--help') {
    '--list-models'
    exit 0
}
if ($args -contains '--list-models') {
    'provider          model                    context  max-out'
    'local-provider    glm-5.2-custom           100K     10K'
    'local-provider    kimi-k3-plus             100K     10K'
    'local-provider    deepseek-v3              100K     10K'
    'local-provider    deepseek-v4-pro-custom   100K     10K'
    'local-provider    gpt-5.6-family-luna-lite  100K     10K'
    'project-provider  configured-model         100K     10K'
    exit 0
}
exit 9
'@,
        [System.Text.UTF8Encoding]::new($false)
    )

    $raw = & $inspector -PiPath $fakePi -ConfiguredModel 'standard::project-provider/configured-model'
    Assert-True ($LASTEXITCODE -eq 0) '巡检器应成功'
    $result = $raw | ConvertFrom-Json
    Assert-True ($result.inventory_count -eq 6) '模型清单解析数量错误'

    $standard = @($result.routes | Where-Object route -eq 'standard')[0]
    Assert-True ($standard.source -eq 'project_config') '项目配置必须优先'
    Assert-True ($standard.selected_model -eq 'project-provider/configured-model') '项目配置被替换'
    Assert-True ([bool]$standard.available) '存在的项目配置应标记可用'

    $pro = @($result.routes | Where-Object route -eq 'pro')[0]
    Assert-True ($pro.selected_model -eq 'local-provider/kimi-k3-plus') 'Kimi 家族模糊匹配失败'
    $lite = @($result.routes | Where-Object route -eq 'lite')[0]
    Assert-True ($lite.selected_model -eq 'local-provider/deepseek-v4-pro-custom') 'Lite 应优先 DeepSeek v4/pro'
    Assert-True (@($lite.candidates).Count -eq 3) 'Lite 候选未合并 DeepSeek 与 GPT Luna'
    Assert-True (@($lite.candidates) -contains 'local-provider/gpt-5.6-family-luna-lite') 'Lite 缺少 GPT Luna 备选'

    $unconfiguredRaw = & $inspector -PiPath $fakePi
    $unconfigured = $unconfiguredRaw | ConvertFrom-Json
    $unconfiguredStandard = @($unconfigured.routes | Where-Object route -eq 'standard')[0]
    Assert-True ($unconfiguredStandard.source -eq 'discovered') '无配置时应使用家族巡检'
    Assert-True ($unconfiguredStandard.selected_model -eq 'local-provider/glm-5.2-custom') 'GLM 家族模糊匹配失败'

    $missingRaw = & $inspector -PiPath $fakePi -ConfiguredModel 'pro::project-provider/missing-model'
    $missing = $missingRaw | ConvertFrom-Json
    $missingPro = @($missing.routes | Where-Object route -eq 'pro')[0]
    Assert-True ($missingPro.source -eq 'project_config') '缺失配置仍必须保持优先'
    Assert-True (-not [bool]$missingPro.available) '缺失配置应报告不可用'
    Assert-True ($missing.warnings.Count -gt 0) '缺失配置应产生 warning'

    Write-Output 'pi_model_inspector_tests=passed'
}
finally {
    $resolvedParent = [System.IO.Path]::GetFullPath($tempParent).TrimEnd('\', '/')
    $resolvedTarget = [System.IO.Path]::GetFullPath($tempRoot)
    if ($resolvedTarget.StartsWith(
        $resolvedParent + [System.IO.Path]::DirectorySeparatorChar,
        [StringComparison]::OrdinalIgnoreCase
    ) -and (Test-Path -LiteralPath $tempRoot)) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force
    }
}
