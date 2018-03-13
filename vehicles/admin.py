from django.contrib import admin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from vehicles.forms import VehicleAdminForm
from vehicles.models import Vehicle


class ManufactureYearListFilter(admin.SimpleListFilter):
    title = _('decade manufactured')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'decade'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('latest', _('in the last two years')),
            ('2010s', _('between 2010 and the last two years')),
            ('2000s', _('before 2000 and 2010')),
            ('old', _('before 2000')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'old':
            return queryset.filter(year__lte=2000)
        if self.value() == '2000s':
            return queryset.filter(year__gte=2000, year__lte=2010)
        if self.value() == '2010s':
            return queryset.filter(year__gte=2010,
                                   year__lte=timezone.now().year-1)
        if self.value() == 'latest':
            return queryset.filter(year__gte=timezone.now().year-1)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    form = VehicleAdminForm
    filter_horizontal = ('drivers', )
    list_display = ('car_id', 'car_instance', 'registration_number', 'year',
        'number_of_passenger_seats')
    list_display_links = ('car_id', 'registration_number')
    list_filter = (ManufactureYearListFilter, 'number_of_passenger_seats')
    exclude = ('active_driver', )
    readonly_fields = ('get_active_driver', 'location_update_datetime')
    search_fields = ('car_id', 'registration_number', 'year', 'description',
        'drivers__first_name', 'drivers__last_name', 'drivers__username'
        )
    view_on_site = False
