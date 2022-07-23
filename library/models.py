import os
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
# Create your models here.
from library.utils import dateformat


class Periodical(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=64)

    class Meta:
        verbose_name = _("Periodical")
        verbose_name_plural = _("Periodicals")

    def __str__(self):
        return self.name

    def get_struct(self, queryset=None):
        if queryset:
            data = queryset
        else:
            data = self.instances.all()
        struct = {}
        for obj in data:
            year = obj.date.year
            month = _(obj.date.strftime('%B'))
            if year not in struct:
                struct[year] = {}
            if month not in struct[year]:
                struct[year][month] = []
            struct[year][month].append(obj)
        return struct


def periodical_save_path(instance, filename):
    return 'library/{0}/{1}/{2}.{3}'.format(instance.periodical.name, instance.date.year,
                                            instance.date.strftime("%d.%m.%Y"), filename.split('.')[-1])


class Instance(models.Model):
    periodical = models.ForeignKey(Periodical, verbose_name=_("Periodical name"),
                                   related_name="instances", on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("Date"))
    file = models.FileField(verbose_name=_("Instance"), upload_to=periodical_save_path)

    def shortname(self):
        return '.'.join(os.path.basename(self.file.name).split('.')[:-1])

    def save(self, *args, **kwargs):
        if self.pk:
            old_self = Instance.objects.get(pk=self.pk)
            if old_self.file and self.image != old_self.file:
                old_self.file.delete(False)
        return super(Instance, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Periodical instance")
        verbose_name_plural = _("Periodical instances")
        ordering = ["-date", ]

    def __str__(self):
        return self.file.name


@receiver(pre_delete, sender=Instance)
def file_delete(sender, instance, **kwargs):
    if instance.file.name:
        instance.file.delete(False)


class Client(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=64)

    def _getstat(self, periodic):
        return self.statistics.get_or_create(client=self, periodical=periodic, date=dateformat())[0]

    def inc_visit(self, periodic):
        stat = self._getstat(periodic)
        stat.visits += 1
        stat.save()

    def inc_view(self, periodic):
        stat = self._getstat(periodic)
        stat.views += 1
        stat.save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")


class Address(models.Model):
    client = models.ForeignKey(Client, verbose_name=_("Client"),
                               related_name="addresses", on_delete=models.CASCADE)
    ipaddress = models.GenericIPAddressField(verbose_name=_("Address"), unique=True)

    @staticmethod
    def is_client(addr):
        return Address.objects.filter(ipaddress=addr).first()

    @staticmethod
    def get_client(addr):
        return Address.objects.get(ipaddress=addr).client

    def __str__(self):
        return ' - '.join([self.client.name, self.ipaddress])

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")


class Statistic(models.Model):
    client = models.ForeignKey(Client, verbose_name=_("Client"),
                               related_name="statistics", on_delete=models.CASCADE)
    periodical = models.ForeignKey(Periodical, verbose_name=_("Periodical name"),
                                   related_name="statistics", on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("Date"), default=dateformat)
    visits = models.PositiveIntegerField(verbose_name=_('Visits'), default=0, blank=False, null=False)
    views = models.PositiveIntegerField(verbose_name=_('Views'), default=0, blank=False, null=False)

    def __str__(self):
        return ' - '.join([self.client.name, self.periodical.name])

    class Meta:
        verbose_name = _("Statistic")
        verbose_name_plural = _("Statistics")