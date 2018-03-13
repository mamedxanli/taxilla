from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from vehicles import views

urlpatterns = [
    url(r'^vehicle_location_update/(?P<vehicle_id>\d+)/(?P<travel_id>\d+)',
        login_required(views.VehicleLocationUpdate.as_view()),
        name='vehicle-location-update'),
]
