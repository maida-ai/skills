@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%install_skills.py" (
  where python >nul 2>nul && python "%SCRIPT_DIR%install_skills.py" %* && exit /b !ERRORLEVEL!
  where py >nul 2>nul && py -3 "%SCRIPT_DIR%install_skills.py" %* && exit /b !ERRORLEVEL!
)
echo error: Python 3 is required >&2
exit /b 1
