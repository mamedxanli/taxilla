from datetime import datetime as dt, timedelta
import json
import logging
from psycopg2.extras import DateTimeTZRange

from accounts.models import TaxillaUser
from django.contrib import admin
from django.http import JsonResponse
from django.db.models import F
from django.db.models.expressions import Func
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from travels.forms import TravelAdminForm
from travels.models import Travel
from travels.tasks import travel_submit_task
from vehicles.models import Vehicle


log = logging.getLogger(__name__)


class VehicleListFilter(admin.SimpleListFilter):
    """returns short list of properties for
    vehicle in order to use them in filter on admin page"""
    title = _('by assigned vehicle')
    parameter_name = 'assigned_vehicle'

    def lookups(self, request, model_admin):
        assigned_vehicles = set([travel.assigned_vehicle
            for travel in Travel.objects.all() if travel.assigned_vehicle])
        return [(vehicle.id, '{} - {}'.format(vehicle.car_id,
            vehicle.registration_number)) for vehicle in assigned_vehicles]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(assigned_vehicle__id__exact = self.value())
        else:
            return queryset


@admin.register(Travel)
class TravelAdmin(admin.ModelAdmin):

    form = TravelAdminForm
    date_hierarchy = 'date_time'
    fieldsets = (
        (None, {
            'fields': (
                'traveller',
                'pickup',
                'dropoff',
                ('date_time', 'no_of_passengers'),
                '_map',
                ('get_duration', 'distance', 'get_vehicle_waiting_time'),
                'notes',
            )
        }),
        ('Operator', {
            'fields': (('assigned_vehicle', 'advanced_vehicle'),
                'get_driver_info', 'status'),
        }),
        ('Advanced options', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('assigned_operator', ),
        }),
        ('Data', {
            'classes': ('hidden',),
            'fields': ('geolocation', 'pickup_data', 'dropoff_data')
        }),
    )
    readonly_fields = ('is_resolved', 'notes', 'distance', 'get_duration',
        'get_driver_info', 'get_vehicle_waiting_time')
    list_display = ('traveller', 'pickup', 'dropoff', 'date_time',
        'assigned_vehicle', 'is_resolved')
    list_display_links = ('traveller', 'pickup', 'dropoff')
    list_filter = (VehicleListFilter, 'assigned_operator', 'date_time',
        'status')
    ordering = ('-date_time',)
    search_fields = ('traveller__username', 'traveller__first_name',
        'traveller__last_name', 'notes')
    view_on_site = False

    def add_view(self, request, form_url='', extra_context=None):
        log.info('STARTED')
        if request.is_ajax():
            data = self._parse_request(request.POST)

            json_result = self._get_json_response(data)

            import time
            time.sleep(3)
            return JsonResponse(json_result, safe=False)

        elif request.POST:
            form = TravelAdminForm(request.POST)
            return super(TravelAdmin, self).add_view(request,
                form_url='', extra_context=None)

        else:
            return super(TravelAdmin, self).add_view(request,
                form_url='', extra_context=None)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        log.info('STARTED')
        if request.is_ajax():
            data = self._parse_request(request.POST, edit=True)
            json_result = self._get_json_response(data, object_id)

            import time
            time.sleep(3)
            return JsonResponse(json_result, safe=False)

        elif request.POST:
            form = TravelAdminForm(request.POST)
            return super(TravelAdmin, self).change_view(request,
                object_id, form_url='', extra_context=None)

        else:
            return super(TravelAdmin, self).change_view(request,
                object_id, form_url='', extra_context=None)

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """        
        if '_continue' not in request.POST:
            obj.advanced_vehicle = False
        obj.save()
        travel_submit_task.apply_async(args=[obj.id], countdown=10)


    # TODO consider replacing this function with an ajax call
    def get_form(self, request, obj=None, **kwargs):
        self.raw_id_fields = []
        if obj and obj.advanced_vehicle:
            self.raw_id_fields.append('assigned_vehicle')
        return super(TravelAdmin, self).get_form(request, obj, **kwargs)


    def _get_date_time_finish(self, duration_text, dt_start):
        """
        Parses trip duration value and start date_and_time and
        calculates  corresponding trip finish date_and_time

        :param duration_text: string
        :param dt_start: datetime object
        :returns: datetime object
        """
        if 'hour' in duration_text:
            hrs = int(duration_text.split()[0])
            mins = int(duration_text.split()[2])
        else:
            mins = int(duration_text.split()[0])
            hrs = None

        if hrs:
            duration = 3600*hrs + 60*mins
        else:
            duration = 60*mins

        dt_fin = dt_start + timedelta(seconds=duration)
        return dt_fin

    def _parse_request(self, request, edit=False):
        """
        Parses request submitted via ajax or post and returns
        a dict replacing strings with corresponding objects

        :param request: QueryDict object (request.POST)
        :param edit: Boolean, shows if add or edit controller being called
        :returns: Dict object
        """
        params = dict()
        if edit == True:
            try:
                params['dt_start'] = dt.strptime("{dt} {tm}".format(
                    dt=request['date_time_0'],
                    tm=request['date_time_1']), 
                    "%Y-%m-%d %H:%M:%S")
            except ValueError as err:
                log.error(err)
                params['dt_start'] = dt.strptime("{dt} {tm}".format(
                    dt=request['date_time_0'],
                    tm=request['date_time_1']), 
                    "%Y-%m-%d %H:%M")
        else:
            params['dt_start'] = dt.strptime("{dt} {tm}".format(
                dt=request['date_time_0'],
                tm=request['date_time_1']), 
                "%Y-%m-%d %H:%M")
        params['dt_fin'] = self._get_date_time_finish(request['duration'],
            params['dt_start'])
        params['no_of_passengers'] = request['no_of_passengers']
        params['duration_range'] = DateTimeTZRange(params['dt_start'],
            params['dt_fin'], '(]')
        params['pickup_data'] = json.loads(request['pickup_data'])
        params['date_time'] = params['dt_start']
        return params

    def _get_json_response(self, data, object_id=None):
        """
        Parses 'data' dictionary (prepared by _parse_request from
        request.POST) and returns a dictionary which includes
        available vehicles

        :param data: Dict object
        :param object_id: 
        :returns: Dict object
        """
        qs = Vehicle.travels.by_count(data['dt_start']).filter(
                number_of_passenger_seats=data['no_of_passengers'],
                drivers__isnull=False)

        qs = qs.exclude(travel=Travel.objects.filter(
            duration_range__overlap=data['duration_range']).order_by('?'))
        # We are getting the first 50 items and ensure there are no dups
        # We need to fetch here as annotate and distinct don't work together
        values = set([x[0] for x in qs.values_list('id')[:50]])
        t_lat = data['pickup_data']['geometry']['location']['lat']
        t_lng = data['pickup_data']['geometry']['location']['lng']

        # check that the difference is 2hrs or less
        now = timezone.now()
        pickup_time = data['dt_start']
        pickup_time_aw = timezone.make_aware(pickup_time, 
            timezone.get_current_timezone())
        dif = now - pickup_time_aw
        minutes = int(dif.total_seconds() / 60)

        if minutes <= 120:
            # We are calculating Euclidean distance between travel pickup
            # location and vehicles by using Pythagorean theorem formula
            # (distance_to is a square value of actual distance)
            qs = Vehicle.objects.filter(pk__in=values).annotate(
                distance_to=Func((F('latitude') - t_lat), 2,
                function='power') + Func((F('longitude') - t_lng), 2,
                function='power')
            ).order_by('distance_to')
        else:
            qs = qs[:50]

        json_result = dict()
        for vehicle in qs:
            json_result[vehicle.id] = str(vehicle)

        # check that the vehicle assigned only on current travel, if 
        # true then add that vehicle to the drop available vehicles list
        if object_id:
            current_veh = Travel.objects.select_related().get(pk=object_id)
            current_veh_id = current_veh.assigned_vehicle.id
            veh_trv_lst = Travel.objects.filter(
                duration_range__overlap=data['duration_range'],
                no_of_passengers=int(data['no_of_passengers']))
            if len(veh_trv_lst) == 1 and veh_trv_lst[0].id == int(object_id):
                value = str(Vehicle.objects.get(pk=current_veh_id))
                json_result[current_veh_id] = value

        return json_result