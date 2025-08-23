$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$Version = Get-Content VERSION
$AppName = "netdigger"
$BinName = "$AppName-$Version.exe"

python -m pip install --upgrade pip pyinstaller
Remove-Item -Recurse -Force build, dist -ErrorAction Ignore

pyinstaller `
  --name $BinName `
  --onefile `
  --noconsole `
  --add-data "gfx;gfx" `
  "src/netdigger.py"

Write-Host "Build OK -> dist\$BinName"
