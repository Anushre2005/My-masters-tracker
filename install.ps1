# Installs the built app (dist\MastersTracker) for the current user:
#   %LOCALAPPDATA%\Programs\MastersTracker  +  Start Menu folder  +  Desktop shortcut.
# Re-run after rebuilding to update. Your data lives in %LOCALAPPDATA%\MastersTracker\data and is not touched.
$ErrorActionPreference = 'Stop'
$src = Join-Path $PSScriptRoot 'dist\MastersTracker'
$dest = Join-Path $env:LOCALAPPDATA 'Programs\MastersTracker'
$exe = Join-Path $dest 'MastersTracker.exe'

Get-Process MastersTracker -ErrorAction SilentlyContinue | Stop-Process -Force
# wait until the app has fully exited and released its DLLs (a quick delete can fail with "access denied")
for ($i = 0; $i -lt 20 -and (Get-Process MastersTracker -ErrorAction SilentlyContinue); $i++) { Start-Sleep -Milliseconds 500 }
for ($i = 0; (Test-Path $dest) -and $i -lt 10; $i++) {
    try { Remove-Item $dest -Recurse -Force -ErrorAction Stop } catch { Start-Sleep -Seconds 1 }
}
if (Test-Path $dest) { throw "Could not remove $dest - close Masters Tracker (tray icon > Quit) and run the installer again." }
Copy-Item $src $dest -Recurse

$startup = [Environment]::GetFolderPath('Startup')
Set-Content (Join-Path $dest 'autostart_on.ps1') @"
`$s = (New-Object -ComObject WScript.Shell).CreateShortcut('$startup\Masters Tracker.lnk')
`$s.TargetPath = '$exe'; `$s.Arguments = '--hidden'; `$s.WorkingDirectory = '$dest'; `$s.IconLocation = '$exe'; `$s.Save()
Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Masters Tracker will now start in the tray when you log in.') | Out-Null
"@
Set-Content (Join-Path $dest 'autostart_off.ps1') @"
Remove-Item '$startup\Masters Tracker.lnk' -ErrorAction SilentlyContinue
Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Masters Tracker will no longer start at login.') | Out-Null
"@

$sh = New-Object -ComObject WScript.Shell
function New-Link($path, $target, $arguments, $icon) {
    $l = $sh.CreateShortcut($path); $l.TargetPath = $target; $l.Arguments = $arguments
    $l.WorkingDirectory = $dest; $l.IconLocation = $icon; $l.Save()
}
$menu = Join-Path ([Environment]::GetFolderPath('Programs')) 'Masters Tracker'
New-Item -ItemType Directory -Force $menu | Out-Null
New-Link "$menu\Masters Tracker.lnk" $exe '' $exe
$ps = "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe"
New-Link "$menu\Start at login - ON.lnk" $ps "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$dest\autostart_on.ps1`"" $exe
New-Link "$menu\Start at login - OFF.lnk" $ps "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$dest\autostart_off.ps1`"" $exe
New-Link (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Masters Tracker.lnk') $exe '' $exe
Write-Output "Installed to $dest"
