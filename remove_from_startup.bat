@echo off
rem Removes Smart Mouse Jiggler from Windows startup for the current user.
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$lnk = Join-Path ([Environment]::GetFolderPath('Startup')) 'Smart Mouse Jiggler.lnk';" ^
 "if (Test-Path $lnk) {" ^
 "  Remove-Item $lnk;" ^
 "  Write-Host ('Removed from startup: ' + $lnk);" ^
 "} else {" ^
 "  Write-Host 'Smart Mouse Jiggler is not in the startup folder.';" ^
 "}"

echo.
pause
