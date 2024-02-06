@echo off

cd ..
call venv\Scripts\activate
set "PYTHONPATH=%PYTHONPATH%;%cd%"
if exist .env (
    for /f "tokens=* delims=" %%a in ('type .env') do set %%a
)