@echo off
rem Adds Smart Mouse Jiggler to Windows startup for the current user.
rem Prefers the built exe (dist\SmartMouseJiggler.exe) if it exists,
rem otherwise launches the GUI script with pyw/pythonw (no console window).
setlocal
set "APP_DIR=%~dp0"
if "%APP_DIR:~-1%"=="\" set "APP_DIR=%APP_DIR:~0,-1%"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$appDir = $env:APP_DIR;" ^
 "$exe = Join-Path $appDir 'dist\SmartMouseJiggler.exe';" ^
 "if (Test-Path $exe) {" ^
 "  $target = $exe; $arguments = '';" ^
 "} else {" ^
 "  $pyw = (Get-Command pyw.exe -ErrorAction SilentlyContinue).Source;" ^
 "  if (-not $pyw) { $pyw = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source }" ^
 "  if (-not $pyw) { Write-Host 'ERROR: No built exe found and pyw.exe/pythonw.exe is not on PATH.'; exit 1 }" ^
 "  $target = $pyw;" ^
 "  $arguments = [char]34 + (Join-Path $appDir 'smart_mouse_jiggler_gui.py') + [char]34;" ^
 "}" ^
 "$startup = [Environment]::GetFolderPath('Startup');" ^
 "$lnk = Join-Path $startup 'Smart Mouse Jiggler.lnk';" ^
 "$shell = New-Object -ComObject WScript.Shell;" ^
 "$shortcut = $shell.CreateShortcut($lnk);" ^
 "$shortcut.TargetPath = $target;" ^
 "$shortcut.Arguments = $arguments;" ^
 "$shortcut.WorkingDirectory = $appDir;" ^
 "$shortcut.Description = 'Smart Mouse Jiggler';" ^
 "$shortcut.Save();" ^
 "Write-Host ('Added to startup: ' + $lnk);" ^
 "Write-Host ('Launches: ' + $target + ' ' + $arguments)"

echo.
pause
