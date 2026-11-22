# Instalador oficial de VANTS Clipper para Windows (1 línea en PowerShell):
#   irm https://raw.githubusercontent.com/VANTSGAMES/VANTS-Clipper/main/install.ps1 | iex
$ErrorActionPreference = "Stop"

Write-Host "=== Instalando VANTS Clipper (VANTS GAMES) ===" -ForegroundColor Cyan
$release = Invoke-RestMethod -Uri "https://api.github.com/repos/VANTSGAMES/VANTS-Clipper/releases/latest" -Headers @{ "User-Agent" = "VANTS-Clipper-Installer" }
$asset = $release.assets | Where-Object { $_.name -like "VANTS-Clipper-Setup-*.exe" } | Select-Object -First 1

if (-not $asset) {
  throw "Aún no hay un VANTS-Clipper-Setup-*.exe publicado en GitHub Releases. Crea un tag v1.0.0 o ejecuta el workflow Release Windows."
}

$tmp = Join-Path $env:TEMP $asset.name
Write-Host "Descargando $($asset.name)..."
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $tmp
Write-Host "Ejecutando instalador silencioso..."
Start-Process -FilePath $tmp -ArgumentList "/VERYSILENT" -Wait
Write-Host "Listo. VANTS Clipper instalado en %LOCALAPPDATA%\VANTSGAMES\VANTS-Clipper." -ForegroundColor Green
