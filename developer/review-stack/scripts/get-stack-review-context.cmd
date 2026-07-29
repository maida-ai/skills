@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%get_stack_review_context.py" (
  where python >nul 2>nul && python "%SCRIPT_DIR%get_stack_review_context.py" %* && exit /b !ERRORLEVEL!
  where py >nul 2>nul && py -3 "%SCRIPT_DIR%get_stack_review_context.py" %* && exit /b !ERRORLEVEL!
)
echo error: Python 3 is required >&2
exit /b 1
