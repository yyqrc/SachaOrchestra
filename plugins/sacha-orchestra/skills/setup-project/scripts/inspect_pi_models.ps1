[CmdletBinding()]
param(
    [string]$PiPath = 'pi',
    [string[]]$ConfiguredModel = @()
)

$ErrorActionPreference = 'Stop'
$routeSpecs = [ordered]@{
    standard = @{
        family = 'glm-5.2'
        patterns = @('glm+52')
        bonuses = @('glm52')
    }
    pro = @{
        family = 'kimi k3'
        patterns = @('kimi+k3')
        bonuses = @('kimik3')
    }
    lite = @{
        family = 'deepseek or gpt-5.6 luna'
        patterns = @('deepseek', 'gpt+56+luna')
        bonuses = @('v4pro', 'v4', 'pro')
    }
}

function Normalize-ModelName {
    param([Parameter(Mandatory)][string]$Value)
    return ($Value.ToLowerInvariant() -replace '[^a-z0-9]', '')
}

function Parse-ConfiguredModels {
    param([AllowEmptyCollection()][string[]]$Values = @())

    $parsed = @{}
    foreach ($value in $Values) {
        $parts = @($value -split '::', 2)
        if ($parts.Count -ne 2) {
            throw 'ConfiguredModel 必须是 <route>::<provider/model>'
        }
        $route = $parts[0]
        $model = $parts[1]
        if (-not $routeSpecs.Contains($route) -or $route -cne $route.Trim().ToLowerInvariant()) {
            throw "未知 Pi route：$route"
        }
        if ($model -cne $model.Trim() -or $model -notmatch '^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$') {
            throw "不安全的 Pi model：$model"
        }
        if ($parsed.ContainsKey($route)) {
            throw "Pi route 重复配置：$route"
        }
        $parsed[$route] = $model
    }
    return $parsed
}

function Invoke-Pi {
    param(
        [Parameter(Mandatory)]$CommandInfo,
        [Parameter(Mandatory)][string[]]$Arguments
    )

    $output = @(& $CommandInfo.Source @Arguments 2>&1)
    if ($LASTEXITCODE -ne 0) {
        throw "Pi 命令失败：$($Arguments -join ' ')"
    }
    return @($output | ForEach-Object { $_.ToString() })
}

$configured = Parse-ConfiguredModels -Values $ConfiguredModel
$piCommand = Get-Command $PiPath -ErrorAction Stop
if ([string]::IsNullOrWhiteSpace($piCommand.Source)) {
    throw "PiPath 无法解析为可信本机命令：$PiPath"
}
$extension = [System.IO.Path]::GetExtension($piCommand.Source).ToLowerInvariant()
if ($extension -notin @('.ps1', '.exe', '.cmd', '.bat')) {
    throw "PiPath 必须解析为 .ps1、.exe、.cmd 或 .bat：$($piCommand.Source)"
}

$help = Invoke-Pi -CommandInfo $piCommand -Arguments @('--help')
if (-not (($help -join "`n").Contains('--list-models'))) {
    throw '当前 Pi CLI 不支持 --list-models'
}
$modelLines = Invoke-Pi -CommandInfo $piCommand -Arguments @('--list-models')
$inventory = @()
foreach ($line in $modelLines) {
    $columns = @($line.Trim() -split '\s{2,}')
    if ($columns.Count -lt 2 -or $columns[0] -eq 'provider' -or $columns[1] -eq 'model') {
        continue
    }
    if (
        $columns[0] -notmatch '^[A-Za-z0-9._-]+$' -or
        $columns[1] -notmatch '^[A-Za-z0-9._-]+$'
    ) {
        continue
    }
    $inventory += [pscustomobject]@{
        provider = $columns[0]
        model = $columns[1]
        exact = "$($columns[0])/$($columns[1])"
        normalized = Normalize-ModelName -Value $columns[1]
    }
}
$inventory = @($inventory | Sort-Object exact -Unique)

$warnings = @()
$routes = @()
foreach ($route in $routeSpecs.Keys) {
    $spec = $routeSpecs[$route]
    if ($configured.ContainsKey($route)) {
        $selected = $configured[$route]
        $available = @($inventory | Where-Object {
            $_.exact.Equals($selected, [StringComparison]::OrdinalIgnoreCase)
        }).Count -gt 0
        if (-not $available) {
            $warnings += "项目配置优先，但当前 Pi 清单未找到 route=$route 的精确型号"
        }
        $routes += [pscustomobject]@{
            route = $route
            family = $spec.family
            source = 'project_config'
            selected_model = $selected
            available = $available
            candidates = @()
        }
        continue
    }

    $matches = @(
        $inventory |
            Where-Object {
                $normalized = $_.normalized
                @($spec.patterns | Where-Object {
                    $tokens = @($_ -split '\+')
                    @($tokens | Where-Object { -not $normalized.Contains($_) }).Count -eq 0
                }).Count -gt 0
            } |
            ForEach-Object {
                $normalized = $_.normalized
                $score = 0
                for ($patternIndex = 0; $patternIndex -lt $spec.patterns.Count; $patternIndex++) {
                    $tokens = @($spec.patterns[$patternIndex] -split '\+')
                    if (@($tokens | Where-Object { -not $normalized.Contains($_) }).Count -eq 0) {
                        $score = 1000 - ($patternIndex * 100)
                        break
                    }
                }
                for ($index = 0; $index -lt $spec.bonuses.Count; $index++) {
                    if ($_.normalized.Contains($spec.bonuses[$index])) {
                        $score += 100 - $index
                        break
                    }
                }
                [pscustomobject]@{
                    model = $_.exact
                    score = $score
                }
            } |
            Sort-Object @{ Expression = 'score'; Descending = $true }, @{ Expression = 'model'; Descending = $false }
    )
    if ($matches.Count -eq 0) {
        $warnings += "未找到 route=$route 的 $($spec.family) 模型候选"
    }
    $routes += [pscustomobject]@{
        route = $route
        family = $spec.family
        source = if ($matches.Count -gt 0) { 'discovered' } else { 'unresolved' }
        selected_model = if ($matches.Count -gt 0) { $matches[0].model } else { $null }
        available = $matches.Count -gt 0
        candidates = @($matches | ForEach-Object { $_.model })
    }
}

[pscustomobject]@{
    status = if ($warnings.Count -gt 0) { 'ok_with_warnings' } else { 'ok' }
    inventory_count = $inventory.Count
    routes = $routes
    warnings = $warnings
} | ConvertTo-Json -Depth 6 -Compress
