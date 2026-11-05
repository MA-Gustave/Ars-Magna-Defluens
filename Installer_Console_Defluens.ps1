# Install this *patch* into the existing Ars Magna Defluens repository.
# Run from the extracted patch folder or via powershell.exe -File ...
param(
  [string]$Destination = 'C:\mycode\Grammatical-Framework\ars-magna-defluens',
  [switch]$Launch
)
$ErrorActionPreference = 'Stop'
$Source = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Test-Path (Join-Path $Source 'console\server.py'))) {
  throw 'Console source files not found next to this installer.'
}
if (-not (Test-Path $Destination -PathType Container)) {
  throw "Ars Magna Defluens repository not found at $Destination. Supply -Destination with the correct repository root."
}
$srcResolved = (Resolve-Path -LiteralPath $Source).Path.TrimEnd('\')
$dstResolved = (Resolve-Path -LiteralPath $Destination).Path.TrimEnd('\')
if ($srcResolved -ine $dstResolved) {
  # Only merge: robocopy does not delete existing files without /MIR.
  robocopy $Source $Destination /E /R:1 /W:1 /NFL /NDL /NJH /NJS /NP /XD '__pycache__' /XF '*.pyc' | Out-Host
  if ($LASTEXITCODE -ge 8) { throw "File copy failed (robocopy exit code $LASTEXITCODE)." }
}
$Launcher = Join-Path $Destination 'Lancer_Ars_Magna_Defluens.bat'
if (-not (Test-Path -LiteralPath $Launcher)) { throw 'The root launcher was not installed.' }
Write-Host "Ars Magna Defluens console installed at: $Destination" -ForegroundColor Green
Write-Host "Root launcher: $Launcher"
if ($Launch) { Start-Process -FilePath $Launcher -WorkingDirectory $Destination }
