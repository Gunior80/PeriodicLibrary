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
    root = pathlib.Path('d:\\Няръяна Вындер')
    files = root.rglob('*.pdf')
    print('Периодическое издание:\t{0}'.format(root.name))
    periodic = Periodical(name=root.name)
    periodic.save()
    print('Периодическое издание:\tДобавлено')
    for file in files:
        with open(file, 'rb') as f:
            instance = Instance(periodical=periodic, file=File(f),
                                date=dt.strptime(file.stem[3:-2]+file.parent.name, "%d.%m.%Y"))
            instance.save()
            instance.tags.add(instance.date.strftime('%Y'),
                              str(_(instance.date.strftime('%B'))),
                              instance.date.strftime("%d"))
            print('Экземпляр:\t{0}\tдобавлен'.format(file.stem[3:]))
