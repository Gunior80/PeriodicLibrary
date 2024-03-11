import os
import pathlib
import time
from sys import argv
from django.core.wsgi import get_wsgi_application
from django.core.files import File
from django.utils.translation import gettext_lazy as _
from datetime import datetime as dt


def completion(path):
    from library.models import Periodical, Instance
    from PeriodicLibrary.settings import MEDIA_ROOT
    from library.utils.morph import get_words
    from library.utils.pdf2text import get_text
    start_time = time.time()
    files = path.rglob('*.pdf')

    periodic, created = Periodical.objects.get_or_create(name=path.name)
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

            if not instance.fulltext:
                document = get_text(pathlib.Path(MEDIA_ROOT).joinpath(instance.file.name))
                text = ''
                for value in document.values():
                    text += ''.join(value[4]).replace('-\n', '')
                instance.fulltext = text
                instance.save()
            words = get_words(periodic, instance.fulltext)
            instance.tags.add(*words)
    print("Задача завершена за {0} секунд".format(time.time() - start_time))


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PeriodicLibrary.settings")
    application = get_wsgi_application()
    try:
        path = pathlib.Path(argv[1])
        if path.is_dir():
            subdirectories = [subdir for subdir in path.iterdir() if subdir.is_dir()]
            for subdir in subdirectories:
                completion(subdir)
        else:
            raise "Folder is not exist."
    except Exception as e:
        print(e)
