@echo off
chcp 936 >nul
cd /d "%~dp0"
if exist "..\main.py" cd /d ".."

echo =======================================================
echo   正在优雅停止直播录制程序，正在写入退出信号...
echo =======================================================
echo STOP > "%cd%\stop_signal.txt"
echo 已发送安全停止指令，正在等待录制切片落盘（最多60秒）...

powershell -NoProfile -Command "$i = 0; while($i -lt 60){ $r = Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|pythonw)\.exe$' -and $_.CommandLine -like '*main.py*' }; if(-not $r){ break }; Start-Sleep -Seconds 1; $i++ }"

powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { ($_.Name -match '^(python|pythonw)\.exe$') -and ($_.CommandLine -like '*main.py*' -or $_.CommandLine -like '*traffic_light.py*') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"

if exist "%cd%\stop_signal.txt" del "%cd%\stop_signal.txt"
echo.
echo [?] 录制程序及状态灯已完全停止。
timeout /t 3 >nul