from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Periodical(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=64)

    class Meta:
        verbose_name = _("Periodical")
        verbose_name_plural = _("Periodicals")

    def __str__(self):
        return self.name


def periodical_save_path(instance, filename):
    return 'library/{0}/{1}/{2}.{3}'.format(instance.periodical.name, instance.date.year,
                                            instance.date.strftime("%m-%d-%Y"), filename.split('.')[-1])


class Instance(models.Model):
    periodical = models.ForeignKey(Periodical, verbose_name=_("periodical name"),
                                   related_name="periodical", on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("date"))
    file = models.FileField(verbose_name=_("instance"), upload_to=periodical_save_path)

    def save(self, *args, **kwargs):
        if self.pk:
            old_self = Instance.objects.get(pk=self.pk)
            if old_self.file and self.image != old_self.file:
                old_self.file.delete(False)
        return super(Instance, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Periodical instance")
        verbose_name_plural = _("Periodical instances")

    def __str__(self):
        return self.file.name


@receiver(pre_delete, sender=Instance)
def file_delete(sender, instance, **kwargs):
    if instance.file.name:
        instance.file.delete(False)


class Client(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=64)


class Address(models.Model):
    client = models.ForeignKey(Client, verbose_name=_("client"),
                               related_name="address", on_delete=models.CASCADE)
    ipaddress = models.CharField(verbose_name=_("name"), max_length=15, unique=True)

