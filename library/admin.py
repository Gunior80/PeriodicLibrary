import datetime as dt
import calendar
from django.contrib import admin
from django.db.models import Sum
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from library.models import Periodical, Instance, Client, Address, Statistic


@admin.register(Periodical)
class PeriodicalAdmin(admin.ModelAdmin):
    fields = ['name', 'cover', 'statistic']
    readonly_fields = ['statistic']
    list_display = ['name', 'instances_count',
                    'views_for_today', 'visits_for_today',
                    'views_for_this_month', 'visits_for_this_month',
                    'views_for_this_year', 'visits_for_this_year']


    def statistic(self,obj):
        stats = obj.statistics.all()
        all_time = '{0}: {1}\t{2}: {3}'.format(_("visits"),
                                               stats.aggregate(total=Sum('visits'))['total'],
                                               _("views"),
                                               stats.aggregate(total=Sum('views'))['total']
                                               )
        data = dict([(x['date__year'], {}) for x in stats.values('date__year').distinct()])

        for year in data.keys():
            data[year]['visits'] = stats.filter(date__year=year).aggregate(total=Sum('visits'))['total']
            data[year]['views'] = stats.filter(date__year=year).aggregate(total=Sum('views'))['total']
            data[year]['months'] = {}
            months = dict([(_(calendar.month_name[x['date__month']]), {'num': int(x['date__month'])}) for x in stats.filter(date__year=year).values('date__month').distinct()])
            for month in months:
                data[year]['months'][month]['visits'] = stats.filter(date__year=year, date__month=month['num']).aggregate(total=Sum('visits'))['total']
                data[year]['months'][month]['views'] = stats.filter(date__year=year, date__month=month['num']).aggregate(total=Sum('views'))['total']

        print(data)
        mark_safe('<canvas id="myChart" width="400" height="400"></canvas>')
        return mark_safe(all_time)

    def instances_count(self, obj):
        return obj.instances.count()

    instances_count.short_description = _("number of instances")

    def views_for_today(self, obj):
        return obj.statistics.filter(date=dt.date.today()).aggregate(total=Sum('views'))['total']

    views_for_today.short_description = _("views for today")

    def visits_for_today(self, obj):
        return obj.statistics.filter(date__year=dt.date.today().year,
                                     date__day=dt.date.today().day).aggregate(total=Sum('visits'))['total']

    visits_for_today.short_description = _("visits for today")

    def views_for_this_month(self, obj):
        return obj.statistics.filter(date__year=dt.date.today().year,
                                     date__month=dt.date.today().month).aggregate(total=Sum('views'))['total']

    views_for_this_month.short_description = _("views for this month")

    def visits_for_this_month(self, obj):
        return obj.statistics.filter(date__year=dt.date.today().year,
                                     date__month=dt.date.today().month).aggregate(total=Sum('visits'))['total']

    visits_for_this_month.short_description = _("visits for this month")

    def views_for_this_year(self, obj):
        return obj.statistics.filter(date__year=dt.date.today().year).aggregate(total=Sum('views'))['total']

    views_for_this_year.short_description = _("views for this year")

    def visits_for_this_year(self, obj):
        return obj.statistics.filter(date__year=dt.date.today().year).aggregate(total=Sum('visits'))['total']

    visits_for_this_year.short_description = _("visits for this year")

    class Media:
        js = ('/static/library/js/chart.min.js',)


@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    search_fields = ['periodical__name', 'tags__name', ]
    ordering = ('-date',)
    list_display = ['__str__', 'periodical', 'tags_list']

    def periodical(self, obj):
        return obj.periodical.name

    periodical.short_description = _("number of instances")

    def tags_list(self, obj):
        tags = ', '.join(list(obj.tags.filter().values_list('name', flat=True)))
        if not tags:
            tags = "-"
        return tags

    periodical.short_description = _("list of tags")

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
    inlines = [AddressAdmin, ]


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    fields = ('periodical', 'client', ('year', 'month'), ('visits', 'views'))
    readonly_fields = ['periodical', 'client', 'year', 'month', 'visits', 'views']
    search_fields = ['periodical__name', 'client__name', 'date', ]
    ordering = ('-date', )
    list_display = ['periodical', 'client', 'year', 'month', 'visits', 'views']

    def year(self, obj):
        return obj.date.strftime('%Y')

    year.short_description = _("year")

    def month(self, obj):
        return _(obj.date.strftime('%B'))

    month.short_description = _("month")
