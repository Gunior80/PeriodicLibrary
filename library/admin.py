from django.contrib import admin
from library.models import Periodical, Instance, Client, Address, Statistic


@admin.register(Periodical)
class PeriodicalAdmin(admin.ModelAdmin):

    pass


@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    pass


class AddressAdmin(admin.TabularInline):
    model = Address
    extra = 0

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    inlines = [AddressAdmin, ]


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    pass