from django.http.response import HttpResponseForbidden, HttpResponse
from django.views import generic
from vehicles.models import Vehicle
from vehicles.tasks import vehicle_location_update


class VehicleLocationUpdate(generic.View):
    """
    Simple view to accept the coordinates from the driver which has the
    request detail page open. The page will constantly update and report
    location of the vehicle and this class is takes care of validating
    and updating necessary records in the database.
    Upon successfull call, this view will call a celery task to update the
    corresponding vehicle's location.
    """
    def get(self, request, *args, **kwargs):
        if request.user.is_driver != True:
            return HttpResponseForbidden()
        # Getting the driver of the given vehicle
        vehicle = Vehicle.objects.get(pk=int(kwargs['vehicle_id']))
        if not vehicle.drivers:
            return HttpResponseForbidden()
        if request.user not in vehicle.drivers.all():
            return HttpResponseForbidden()
        vehicle_location_update.delay(int(kwargs['vehicle_id']),
            int(kwargs['travel_id']), request.GET.get('lat'),
            request.GET.get('lng'), request.user.id)
        return HttpResponse('ОК')
