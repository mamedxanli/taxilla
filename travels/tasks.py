from taxilla.celery import app
from config.local_secrets import GOOGLE_MAPS_SERVER_API_KEY
from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.template import loader
from django.utils import timezone
from googlemaps import Client
from travels.models import Travel


@app.task
def travel_submit_task(travel_id):
    """
    We are going to trigger tasks on every travel create/update which populate
    missing fields like duration_range and generate an email to the operators so
    they could work on the request

    :param travel_id: Travel object id passed from the view
    """
    travel = Travel.objects.get(pk=travel_id)
    gmaps = Client(key=GOOGLE_MAPS_SERVER_API_KEY)
    result = gmaps.distance_matrix(
        'place_id:{}'.format(travel.pickup_data['place_id']),
        'place_id:{}'.format(travel.dropoff_data['place_id'])
    )
    # Get duration
    try:
        duration = result['rows'][0]['elements'][0]['duration']['value']
    except:
        # In case if google does not know the answer, provide the default
        # booking duration of 1 hour
        duration = 3600
    # Update the travel object
    travel.duration_range = (
        travel.date_time,
        travel.date_time + timezone.timedelta(seconds=duration)
    )

    # Get text distance
    try:
        travel.distance = result['rows'][0]['elements'][0]['distance']['text']
    except:
        travel.distance = None

    # Get raw distance in meters
    try:
        travel.distance_raw = \
            result['rows'][0]['elements'][0]['distance']['value']
    except:
        travel.distance_raw = 0
    travel.save()

    # Send an email to operators
    travel = Travel.objects.get(pk=travel_id)
    subject = "New request from {}".format(travel.traveller)
    domain = Site.objects.get_current()
    html_file = "notifications/new_request.html"
    text_file = "notifications/new_request.txt"
    # This may be converted to the list of emails or randomly chosen operator
    recipient = "operator@taxilla.inetreco.com"

    data = {
        "pickup" : travel.pickup,
        "dropoff" : travel.dropoff,
        "date_time" : travel.date_time,
        "user" : travel.traveller,
        "id" : travel.id,
        "duration": travel.get_duration,
        "distance": travel.distance,
        "notes": travel.notes,
        "site" : domain,
    }

    html_content = loader.get_template(html_file).render(data)
    text_content = loader.get_template(text_file).render(data)

    message = mail.EmailMultiAlternatives(subject, text_content,
        settings.DEFAULT_FROM_EMAIL, [recipient])
    message.attach_alternative(html_content, "text/html")
    message.send()