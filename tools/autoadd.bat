@echo off

if "%1"=="" (
    echo Please provide the path to the auto-replenishment directory.
    exit /b 1
)

set rootdir=%~dp0
cd /d %rootdir%
set_env.bat & %rootdir%autoadd.py "%1"
deactivate