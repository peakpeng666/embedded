$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..')).TrimEnd('\')
$workspace = (Resolve-Path -LiteralPath $workspace).ProviderPath.TrimEnd('\')
$prefix = $workspace + '\'
$plan = Get-Content -LiteralPath (Join-Path $PSScriptRoot '移动计划.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$done = @{}
$logPath = Join-Path $PSScriptRoot '已完成移动.jsonl'
if (Test-Path -LiteralPath $logPath) {
    Get-Content -LiteralPath $logPath -Encoding UTF8 | ForEach-Object {
        $row = $_ | ConvertFrom-Json
        $done[$row.source] = $true
    }
}

function Assert-InWorkspace([string]$relative) {
    if ([IO.Path]::IsPathRooted($relative)) { $absolute = [IO.Path]::GetFullPath($relative) }
    else { $absolute = [IO.Path]::GetFullPath((Join-Path $workspace $relative)) }
    if (-not $absolute.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path outside workspace: $absolute"
    }
    if (Test-Path -LiteralPath $absolute) {
        $resolved = (Resolve-Path -LiteralPath $absolute).ProviderPath
        if (-not $resolved.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Resolved path outside workspace: $resolved"
        }
    }
    return $absolute
}

foreach ($entry in $plan) {
    if ($done.ContainsKey($entry.source)) { continue }
    $source = Assert-InWorkspace $entry.source
    $destination = Assert-InWorkspace $entry.target
    if (-not (Test-Path -LiteralPath $source)) { throw "Missing source: $source" }
    if ((Test-Path -LiteralPath $destination) -and -not ((Get-Item -LiteralPath $source).PSIsContainer -and (Get-Item -LiteralPath $destination).PSIsContainer)) {
        throw "Destination file already exists: $destination"
    }
}

function Move-Remaining([string]$source, [string]$destination) {
    $source = Assert-InWorkspace $source
    $destination = Assert-InWorkspace $destination
    if (-not (Test-Path -LiteralPath $destination)) {
        Move-Item -LiteralPath $source -Destination $destination -Force
        return
    }
    if (-not ((Get-Item -LiteralPath $source).PSIsContainer -and (Get-Item -LiteralPath $destination).PSIsContainer)) {
        throw "File collision: $destination"
    }
    foreach ($child in @(Get-ChildItem -LiteralPath $source -Force)) {
        Move-Remaining $child.FullName (Join-Path $destination $child.Name)
    }
    if (@(Get-ChildItem -LiteralPath $source -Force).Count -ne 0) { throw "Source still has files: $source" }
    Remove-Item -LiteralPath $source
}

$completed = 0
foreach ($entry in $plan) {
    if ($done.ContainsKey($entry.source)) { continue }
    $source = Assert-InWorkspace $entry.source
    $destination = Assert-InWorkspace $entry.target
    $parent = Split-Path -Parent $destination
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    Move-Remaining $source $destination
    [PSCustomObject]@{source=$entry.source; target=$entry.target; movedAt=(Get-Date -Format o)} |
        ConvertTo-Json -Compress | Add-Content -LiteralPath (Join-Path $PSScriptRoot '已完成移动.jsonl') -Encoding UTF8
    $completed++
}

foreach ($name in @('08_平台资源下载', '09_课堂展示_时钟之迹')) {
    $emptyDirectory = Assert-InWorkspace $name
    if ((Test-Path -LiteralPath $emptyDirectory) -and @(Get-ChildItem -LiteralPath $emptyDirectory -Force).Count -eq 0) {
        Remove-Item -LiteralPath $emptyDirectory
    }
}
Write-Output "Completed $completed moves."
