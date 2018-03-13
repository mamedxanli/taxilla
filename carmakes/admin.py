from django.contrib import admin
from carmakes.models import Car
from carmakes.models import Manufacturer


class CarInline(admin.TabularInline):
    model = Car


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    inlines = (CarInline, )
    list_display = ('make', )
