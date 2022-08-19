import os
import pathlib
from django.core.wsgi import get_wsgi_application
from django.core.files import File
from django.utils.translation import gettext_lazy as _
from datetime import datetime as dt

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PeriodicLibrary.settings")

application = get_wsgi_application()

from library.models import Periodical, Instance

if __name__ == "__main__":
    root = pathlib.Path('E:\\Няръяна Вындер')
    files = root.rglob('*.pdf')

    periodic, created = Periodical.objects.get_or_create(name=root.name)
    if created:
        periodic.save()
    for file in files:
        instance, created = Instance.objects.get_or_create(periodical=periodic,
                                                           date=dt.strptime(file.stem[3:-2] + file.parent.name,
                                                                            "%d.%m.%Y"))
        if created:
            with open(file, 'rb') as f:
                instance.file = File(f)
                instance.save()
                instance.tags.add(instance.date.strftime('%Y'),
                                  str(_(instance.date.strftime('%B'))),
                                  instance.date.strftime("%d"))
