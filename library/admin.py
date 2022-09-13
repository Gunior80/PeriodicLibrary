import datetime as dt
from django.contrib import admin
from django.db.models import Sum
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from library.models import Periodical, Instance, Client, Address, Statistic


@admin.register(Periodical)
class PeriodicalAdmin(admin.ModelAdmin):
    fields = ['name', 'cover', 'all_statistic', 'clients_statistic']
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
        print(data)
        return mark_safe(div + data)

    clients_statistic.short_description = _("Clients")

    def instances_count(self, obj):
        return obj.instances.count()

    instances_count.short_description = _("Number of instances")

    def views_for_today(self, obj):
        return obj.statistics.filter(date=dt.date.today()).aggregate(total=Sum('views'))['total']

    views_for_today.short_description = " ".join([str(_("Views for")), str(_("today"))])

    def visits_for_today(self, obj):
        return obj.statistics.filter(date__year=dt.date.today().year,
                                     date__day=dt.date.today().day).aggregate(total=Sum('visits'))['total']

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
    search_fields = ['periodical__name', 'client__name', 'date', ]
    ordering = ('-date', )
    list_display = ['periodical', 'client', 'year', 'month', 'visits', 'views']

    def year(self, obj):
        return obj.date.strftime('%Y')

    year.short_description = _("Year")

    def month(self, obj):
        return _(obj.date.strftime('%B'))

    month.short_description = _("Month")
