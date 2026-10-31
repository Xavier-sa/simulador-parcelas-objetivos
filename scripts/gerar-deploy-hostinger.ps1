$ErrorActionPreference = 'Stop'

$raizProjeto = Split-Path -Parent $PSScriptRoot
$origem = Join-Path $raizProjeto 'frontend'
$destino = Join-Path $raizProjeto 'deploy\hostinger'
$zip = Join-Path $raizProjeto 'deploy\simulador-parcelas-hostinger.zip'
$arquivos = @('index.html', 'style.css', 'script.js')

New-Item -ItemType Directory -Path $destino -Force | Out-Null
Get-ChildItem -LiteralPath $destino -File | Remove-Item -Force

foreach ($arquivo in $arquivos) {
    Copy-Item -LiteralPath (Join-Path $origem $arquivo) -Destination (Join-Path $destino $arquivo)
}

if (Test-Path -LiteralPath $zip) {
    Remove-Item -LiteralPath $zip -Force
}
$fontesZip = $arquivos | ForEach-Object { Join-Path $destino $_ }
Compress-Archive -LiteralPath $fontesZip -DestinationPath $zip

Write-Host "Deploy Hostinger gerado em: $destino"
Write-Host "ZIP gerado em: $zip"
