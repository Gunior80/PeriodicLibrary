import datetime as dt
import zipfile
import io
import os
from django.contrib import admin, messages
from django.db.models import Sum
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from PeriodicLibrary.settings import MEDIA_ROOT
from library.forms import TagGroupForm, TagInstanceForm
from library.models import Periodical, Instance, Client, Address, Statistic, TagGroup


@admin.register(TagGroup)
class TagGroupAdmin(admin.ModelAdmin):
    form = TagGroupForm
    actions = ('download_list', )

    def download_list(self, request, queryset):
        # queryset - это набор выбранных объектов
        memory_zip = io.BytesIO()

        with zipfile.ZipFile(memory_zip, 'w') as zipf:
            for obj in queryset:
                zipf.writestr("{0}.txt".format(obj.name), "\n".join(obj.tags_list()))

        # Передача zip-архива как байтов
        memory_zip.seek(0)
        zip_bytes = memory_zip.read()

        # Создание HTTP-ответа
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="group-tags.zip"'

        # Запись байтов zip-архива в HTTP-ответ
        response.write(zip_bytes)
        return response

    download_list.short_description = _("Download tag lists")


@admin.register(Periodical)
class PeriodicalAdmin(admin.ModelAdmin):
    fields = ['name', 'cover', 'all_statistic', 'clients_statistic', 'tag_groups']
    readonly_fields = ['all_statistic', 'clients_statistic']
    list_display = ['name', 'instances_count',
                    'views_for_today', 'visits_for_today',
                    'views_for_this_month', 'visits_for_this_month']

    def all_statistic(self, obj):
        stats = obj.get_statistic()
        div = '<div id="stats"></div>'
        data = ""
        if stats:
            data = '<script type="module">' \
                   'import {{allstats}} from "/static/library/js/stats.js";allstats({0});' \
                   '</script>'.format(str(stats))
        return mark_safe(div + data)

    all_statistic.short_description = _("Statistic")

    def clients_statistic(self, obj):
        clients = obj.clients.all().distinct()
        stats = []
        data = ''
        for client in clients:
            client_stats = obj.get_statistic(client)
            if client_stats:
                stats.append(client_stats)
        if stats:
            data = '<script type="module">' \
                   'import {{clientstats}} from "/static/library/js/stats.js";clientstats({0});' \
                   '</script>'.format(str(stats))
        div = '<div id="clients_stats"></div>'
        return mark_safe(div + data)

    clients_statistic.short_description = _("Clients")

    def instances_count(self, obj):
        return obj.instances.count()

    instances_count.short_description = _("Number of instances")

    def views_for_today(self, obj):
        return obj.statistics.filter(date=dt.date.today()).aggregate(total=Sum('views'))['total']

    views_for_today.short_description = " ".join([str(_("Views for")), str(_("today"))])

    def visits_for_today(self, obj):
        return obj.statistics.filter(date=dt.date.today()).aggregate(total=Sum('visits'))['total']

    visits_for_today.short_description = " ".join([str(_("Visits for")), str(_("today"))])

    def views_for_this_month(self, obj):
        return obj.statistics.filter(date__year=dt.date.today().year,
                                     date__month=dt.date.today().month).aggregate(total=Sum('views'))['total']

    views_for_this_month.short_description = " ".join([str(_("Views for")), str(_("this month"))])

    def visits_for_this_month(self, obj):
        return obj.statistics.filter(date__year=dt.date.today().year,
                                     date__month=dt.date.today().month).aggregate(total=Sum('visits'))['total']

    visits_for_this_month.short_description = " ".join([str(_("Visits for")), str(_("this month"))])

    class Media:
        js = ('/static/library/js/chart.min.js',
              '/static/library/js/jquery-3.6.0.min.js',
              '/static/library/jquery-ui/jquery-ui.min.js')
        css = {
            'all': ('/static/library/jquery-ui/jquery-ui.css',)
        }


@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    search_fields = ['periodical__name', 'tags__name', ]
    ordering = ('-date',)
    list_display = ['__str__', 'periodical', 'tags_list', ]
    list_filter = ['periodical__name', 'tags', ]

    actions = ('make_tags', )
    form = TagInstanceForm

    def make_tags(self, request, queryset):
        import time
        try:
            start_time = time.time()
            from library.utils.pdf2text import get_text
            from library.utils.morph import get_words
            for instance in queryset:
                if not instance.fulltext:
                    document = get_text(os.path.join(MEDIA_ROOT, instance.file.name))
                    text = ''
                    for value in document.values():
                        text += ''.join(value[4]).replace('-\n', '')
                    instance.fulltext = text
                    instance.save()
                words = get_words(instance.periodical, instance.fulltext)
                instance.tags.add(*words)
            messages.info(request, "{0} {1} {2}".format(_("The task is completed in"),
                                                        time.time() - start_time, _("seconds")))
        except Exception as e:
            messages.error(request, e)

    make_tags.short_description = _("Add keywords")

    def periodical(self, obj):
        return obj.periodical.name

    periodical.short_description = _("Number of instances")

    def tags_list(self, obj):
        tags = list(obj.tags.filter().values_list('name', flat=True))
        tags.sort()
        string = ', '.join(tags)
        if not string:
            string = "-"
        return string

    tags_list.short_description = _("List of tags")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


class AddressAdmin(admin.TabularInline):
    model = Address
    extra = 0


class PeriodicStatsAdmin(admin.TabularInline):
    model = Client
    extra = 0


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'addresses', ]
    inlines = [AddressAdmin, ]

    def addresses(self, obj):
        addrs = [[x['ipaddress'], x['comment']] for x in obj.addresses.all().values('ipaddress', 'comment').distinct()]
        template = '<p>{0} {1}</p>'
        string = ''
        for addr in addrs:
            string += template.format(addr[0], addr[1])
        return mark_safe(string)

    addresses.short_description = _("Addresses")


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    ordering = ('-date', )
    list_display = ['client', 'periodical', 'date', 'visits', 'views']
    list_filter = ['periodical__name', 'client__name', 'date']
