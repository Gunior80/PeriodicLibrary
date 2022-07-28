from django.core.files import File
import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application

from datetime import datetime as dt


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PeriodicLibrary.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

application = get_wsgi_application()

from library.models import Periodical, Instance

def find_files(catalog, ext):
    find_files = []
    for root, dirs, files in os.walk(catalog):
        find_files += [os.path.join(root, name) for name in files if Path(name).suffix == ext]
    return find_files

def parse(file):
    path = file.split('\\')
    return '.'.join(path[-1].split('.')[1:-2]) + '.' + path[-2]

path = "d:\\Няръяна Вындер"
files = find_files(path, '.pdf')

periodic = Periodical(name=os.path.basename(path))
periodic.save()

for file in files:
    with open(file, 'rb') as f:
        m = Instance(periodical=periodic, file=File(f), date=dt.strptime(parse(file), "%d.%m.%Y"))
        m.save()

