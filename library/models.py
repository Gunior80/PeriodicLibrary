import pathlib
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from pytils.translit import slugify
from taggit.managers import TaggableManager
from django.core.cache import cache
import datetime as dt
import django.utils.timezone as tz
import calendar
from django.db.models import Sum


def cover_save_path(instance, filename):
    return 'library/{0}/cover{1}'.format(instance.name, pathlib.Path(filename).suffix)


class Periodical(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=64)
    slug = models.SlugField(default='', unique=True)
    cover = models.ImageField(verbose_name=_("cover"), upload_to=cover_save_path,
                              null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Periodical")
        verbose_name_plural = "    " + str(_("Periodicals"))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def _get_search_results(self, search_terms):
        if search_terms:
            search_terms = search_terms.split(", ")
            instances = self.instances.filter(tags__name__in=search_terms)
            for term in search_terms:
                if term == "":
                    continue
                instances &= self.instances.filter(tags__name=term)
            instances = instances.distinct()
        else:
            instances = self.instances.all()
        return instances

    def json_struct(self, search_terms):
        if not search_terms:
            cache_obj = cache.get('full_json_'+self.slug)
            if cache_obj:
                return cache_obj
        instances = self._get_search_results(search_terms)
        json_data = []
        for instance in instances:
            year = instance.date.year
            month = _(instance.date.strftime('%B'))
            if year not in [val.get('text') for val in json_data]:
                json_data.append({'text': year, 'nodes': [{'text': month,
                                                           'nodes': [
                                                               {'id': instance.id,
                                                                'class': 'menu-item',
                                                                'text': instance.shortname()}]}]})
            else:
                year_count = [count for count, val in enumerate(json_data) if val['text'] == year][0]
                if month not in [val.get('text') for val in json_data[year_count]['nodes']]:
                    json_data[year_count]['nodes'].append({'text': month,
                                                           'nodes': [
                                                               {'id': instance.id,
                                                                'class': 'menu-item',
                                                                'text': instance.shortname()}]})
                else:
                    month_count = [count for count, val in enumerate(json_data[year_count]['nodes'])
                                   if val['text'] == month][0]
                    json_data[year_count]['nodes'][month_count]['nodes'].append({'id': instance.id,
                                                                                 'class': 'menu-item',
                                                                                 'text': instance.shortname()})
        if not search_terms:
            cache.set('full_json_'+self.slug, json_data, 60*60*24)
        return json_data

    def get_statistic(self, client=None):
        if client:
            stats = self.statistics.filter(client=client)
        else:
            stats = self.statistics.all()
        data = dict([(x['date__year'], {}) for x in stats.values('date__year').distinct()])

        for year in data.keys():
            data[year][_('Visits')] = stats.filter(date__year=year).aggregate(total=Sum('visits'))['total']
            data[year][_('Views')] = stats.filter(date__year=year).aggregate(total=Sum('views'))['total']
            data[year]['months'] = {}
            months = dict([(_(calendar.month_name[x['date__month']]), {'num': x['date__month']})
                           for x in stats.filter(date__year=year).values('date__month').distinct()])
            for month in months.keys():
                data[year]['months'][month] = \
                    {_('Visits'): stats.filter(date__year=year,
                                               date__month=months[month]['num']).aggregate(total=Sum('visits'))['total']
                     }
                data[year]['months'][month][_('Views')] = \
                    stats.filter(date__year=year,
                                 date__month=months[month]['num']).aggregate(total=Sum('views'))['total']
        if client:
            data['name'] = client.name
        data['alltime'] = _("All time")

        return data


def instance_save_path(instance, filename):
    return 'library/{0}/{1}/{2}{3}'.format(instance.periodical.name, instance.date.year,
                                           instance.date.strftime("%d.%m.%Y"), pathlib.Path(filename).suffix)


class Instance(models.Model):
    periodical = models.ForeignKey(Periodical, verbose_name=_("Periodical"),
                                   related_name="instances", on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("Date"))
    file = models.FileField(verbose_name=_("Instance"), upload_to=instance_save_path)
    tags = TaggableManager(blank=True)

    def shortname(self):
        return pathlib.Path(self.file.name).stem

    def save(self, *args, **kwargs):
        if self.pk:
            old_self = Instance.objects.get(pk=self.pk)
            if old_self.file and self.file != old_self.file:
                old_self.file.delete(False)
        super().save(*args, **kwargs)
        cache.delete('full_json_' + self.periodical.slug)

    class Meta:
        verbose_name = _("Instance")
        verbose_name_plural = "   " + str(_("Instances"))
        ordering = ["-date", ]

    def __str__(self):
        return self.shortname()


@receiver(pre_delete, sender=Instance)
def file_delete(sender, instance, **kwargs):
    cache.delete('full_json_' + instance.periodical.slug)
    if instance.file.name:
        instance.file.delete(False)


class Client(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=64)
    periodical = models.ManyToManyField(Periodical, through='Statistic',
                                        related_name='clients')

    def _getstat(self, periodic):
        return self.statistics.get_or_create(client=self, periodical=periodic, date=dt.date.today())[0]

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
        verbose_name_plural = "  " + str(_("Clients"))


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
    periodical = models.ForeignKey(Periodical, verbose_name=_("Periodical"),
                                   related_name="statistics", on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("Date"), default=tz.now)
    visits = models.PositiveIntegerField(verbose_name=_('Visits'), default=0, blank=False, null=False)
    views = models.PositiveIntegerField(verbose_name=_('Views'), default=0, blank=False, null=False)

    def __str__(self):
        return ' - '.join([self.client.name, self.periodical.name])

    class Meta:
        verbose_name = _("Statistic")
        verbose_name_plural = " " + str(_("Statistics"))
