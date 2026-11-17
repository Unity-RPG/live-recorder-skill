@echo off
chcp 936 >nul
cd /d "%~dp0"
if exist "..\main.py" cd /d ".."

set "FFMPEG=%cd%\ffmpeg\bin"
set "PY=%cd%\.venv\Scripts\python.exe"
set "PYW=%cd%\.venv\Scripts\pythonw.exe"

if not exist "%PY%" (
    set "PY=python.exe"
    set "PYW=pythonw.exe"
)
if not exist "%PYW%" set "PYW=%PY%"

if exist "%FFMPEG%" (
    set "PATH=%FFMPEG%;%PATH%"
)

echo =======================================================
echo   LiveStream Recorder 全自动直播监控与录制系统
echo   - 状态监控灯将自动浮动显示在桌面右上角
echo   - 退出请按 Ctrl+C，或运行 scripts\stop_record.bat
echo =======================================================

if exist "scripts\traffic_light.py" (
    start "" "%PYW%" "%cd%\scripts\traffic_light.py"
) else if exist "traffic_light.py" (
    start "" "%PYW%" "%cd%\traffic_light.py"
)

"%PY%" main.py
pause