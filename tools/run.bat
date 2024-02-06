@echo off

set rootdir=%~dp0
cd /d %rootdir%
set_env.bat & waitress-serve --host 127.0.0.1 --port=8001 PeriodicLibrary.wsgi:application
deactivate