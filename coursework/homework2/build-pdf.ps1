param([string]$Compiler = 'xelatex')
$ErrorActionPreference = 'Stop'
$sourceName = '作业2_智装备241_彭俊杰_2024306100324.tex'
$buildDirectory = Join-Path $PSScriptRoot '_build/latex'
New-Item -ItemType Directory -Path $buildDirectory -Force | Out-Null
Push-Location -LiteralPath $PSScriptRoot
try {
    for ($pass = 1; $pass -le 2; $pass++) {
        & $Compiler -interaction=nonstopmode -halt-on-error -file-line-error -no-shell-escape -synctex=0 ('-output-directory=' + $buildDirectory) $sourceName
        if ($LASTEXITCODE -ne 0) {
            throw "XeLaTeX 编译失败：第 $pass 次"
        }
    }
    $pdfName = [System.IO.Path]::ChangeExtension($sourceName, '.pdf')
    Copy-Item -LiteralPath (Join-Path $buildDirectory $pdfName) -Destination (Join-Path $PSScriptRoot $pdfName) -Force
}
finally {
    Pop-Location
}
