$ErrorActionPreference = 'Stop'

$raizProjeto = Split-Path -Parent $PSScriptRoot
$origem = Join-Path $raizProjeto 'frontend'
$destino = Join-Path $raizProjeto 'deploy\hostinger'
$arquivos = @('index.html', 'style.css', 'config.js', 'script.js')

New-Item -ItemType Directory -Path $destino -Force | Out-Null
Get-ChildItem -LiteralPath $destino -File | Remove-Item -Force

foreach ($arquivo in $arquivos) {
    Copy-Item -LiteralPath (Join-Path $origem $arquivo) -Destination (Join-Path $destino $arquivo)
}

Write-Host "Deploy Hostinger gerado em: $destino"
Write-Host 'URL Vercel copiada da configuração central frontend\config.js.'
