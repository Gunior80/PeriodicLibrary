from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from library.models import Periodical, Instance, Client, Address, Statistic


@admin.register(Periodical)
class PeriodicalAdmin(admin.ModelAdmin):
    list_display = ['name', 'instances_count', ]

    def instances_count(self, obj):
        return obj.instances.count()

    instances_count.short_description = _("number of instances")


@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
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


class AddressAdmin(admin.TabularInline):
    model = Address
    extra = 0

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    inlines = [AddressAdmin, ]


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    pass