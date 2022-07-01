from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Periodical(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=64)


def periodical_save_path(instance, filename):
    return 'library/{0}/{1}/{2}.{3}'.format(instance.periodical.name, instance.date.year,
                                            instance.date.strftime("%m-%d-%Y"), filename.split[-1])


class Instance(models.Model):
    periodical = models.ForeignKey(Periodical, verbose_name=_("periodical name"),
                                   related_name="periodical", on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("date"))
    file = models.FileField(verbose_name=_("instance"), upload_to=None)
