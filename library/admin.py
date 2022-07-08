from django.contrib import admin

# Register your models here.
from library.models import Periodical, Instance, Client, Address


@admin.register(Periodical)
class PeriodicalAdmin(admin.ModelAdmin):
    pass


@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    pass


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass