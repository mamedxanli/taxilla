from taxilla.celery import app
from config.local_secrets import GOOGLE_MAPS_SERVER_API_KEY
from django.utils import timezone
from googlemaps import Client
from accounts.models import TaxillaUser
from vehicles.models import Vehicle
from travels.models import Travel


@app.task
def vehicle_location_update(vehicle_id, travel_id, lat, lng, user_id):
    """
    Updates vehicle's location in the database, calculates the distance
    in the travel and updates travel duration times
    """
    user = TaxillaUser.objects.get(pk=user_id)
    travel = Travel.objects.get(pk=travel_id)
    vehicle = Vehicle.objects.get(pk=vehicle_id)
    print('new task with args: VID{}, TID{}, LT{}, LN{}, UID{}'.format(
        vehicle_id, travel_id, lat, lng, user_id))
    if user != travel.assigned_driver:
        return
    # Need to check if the travel is the soonest one applied to the vehicle
    # and it is not in the past
    now = timezone.now()
    try:
        earliest_travel = Travel.objects.filter(assigned_vehicle=vehicle,
            date_time__gt=now).order_by('date_time')[0]
    except IndexError:
        # In case there are no matching travels
        return
    if travel != earliest_travel:
        return
    # Pick a driver who just updated the location
    if user in vehicle.drivers.all():
        vehicle.active_driver = user
    else:
        return
    vehicle.latitude = float(lat)
    vehicle.longitude = float(lng)
    vehicle.location_update_datetime = now
    # Also update the travel duration_vehicle field
    gmaps = Client(key=GOOGLE_MAPS_SERVER_API_KEY)
    result = gmaps.distance_matrix(
        '{},{}'.format(lat, lng),
        'place_id:{}'.format(travel.pickup_data['place_id'])
    )
    # Get duration
    try:
        duration = result['rows'][0]['elements'][0]['duration']['value']
    except:
        # In case if google does not know the answer, provide the default
        # booking duration of 0 seconds
        duration = 0
    # Update the travel object
    travel.duration_vehicle = duration
    # Save the objects
    vehicle.save()
    travel.save()
