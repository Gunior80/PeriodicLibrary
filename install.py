#!/usr/bin/env python

import platform
import os
import subprocess
import sys
from pathlib import Path


service_name = 'PeriodicLibrary'
current_directory = Path(__file__).resolve().parent
venv_directory = current_directory.joinpath('venv')
operating_system = platform.system()


def run(app, args):
    if operating_system == 'Windows':
        subdir = 'Scripts'
    elif operating_system == 'Linux':
        subdir = 'bin'
    else:
        raise 'OS not supported from installer'
    subprocess.run([str(venv_directory.joinpath(subdir, app)), *args], shell=True)


def venv_create():
    if not os.path.exists(venv_directory):
        subprocess.call([sys.executable, '-m', 'venv', venv_directory])
    run('pip.exe', ('install', '-r', current_directory.joinpath('requirements.txt')))


venv_create()


def django_prepare():
    with open(current_directory.joinpath('.env'), "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            os.environ[key] = value
    run('python.exe', (current_directory.joinpath('manage.py'), 'collectstatic'))
    run('python.exe', (current_directory.joinpath('manage.py'), 'makemigrations'))
    run('python.exe', (current_directory.joinpath('manage.py'), 'migrate'))
    run('python.exe', (current_directory.joinpath('manage.py'), 'createsuperuser'))


django_prepare()
