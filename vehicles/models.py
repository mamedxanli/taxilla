from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.utils import timezone
from home.models import BaseModel
from carmakes.models import Car


class VehicleTravelManager(models.Manager):
    def by_count(self, date_time):
        """
        This will sort the vehicles by the least amount of travels in the
        given date_time. Used in Travel admin form.
        """
        qs = self.get_queryset().annotate(
            travels_by_day=models.Sum(
                models.Case(
                    models.When(travel__date_time__date=date_time.date(),
                                then=1),
                    default=0,
                    output_field=models.IntegerField())))
        qs = qs.order_by('travels_by_day')
        return qs


class Vehicle(BaseModel):
    """
    Vehicle model describing single car.
    """

    #List of choices for the fields
    FUEL_TYPE_CHOICES = (
        (0, _("Petrol")),
        (1, _("Diesel")),
        (2, _("Hybrid")),
        (3, _("Electric")),
        (4, _("Hydrogen")),
    )
    NUMBER_OF_SEATS_CHOICES = (
        (3, _("1-3")),
        (6, _("4-6")),
        (10, _("7-10")),
    )
    YEAR_CHOICES = []
    for r in range(1980, (timezone.now().year+1)):
        YEAR_CHOICES.append((r,r))

    #Vehicle entry fields:

    car_id = models.CharField(max_length=100, unique=True,
        help_text=_("Car unique id number. Example: 53"))
    car_instance = models.ForeignKey(Car, verbose_name='Car model',
        on_delete=models.CASCADE, null=True,
        help_text=_("Car model field. Example: Nissan Sunny"))
    year = models.IntegerField("Manufacture Year", _('year'),
        choices=YEAR_CHOICES, default=timezone.now().year,
        help_text=_("Car manufacture year"))
    engine = models.IntegerField("Engine Size (cc)", blank=True, null=True,
        help_text=_("Size of the car engine"))
    fuel_type = models.IntegerField(choices=FUEL_TYPE_CHOICES, default=0,
        help_text=_("Type of fuel"))
    number_of_passenger_seats = models.IntegerField(
        choices=NUMBER_OF_SEATS_CHOICES,default=3,
        help_text=_("Number of passenger seats"))
    description = models.CharField(max_length=1000, blank=True,
        help_text=_("Additional information and notes about the vehicle"))
    registration_number = models.CharField("Registration number", max_length=11,
        unique=True, help_text=_("Car registration number"))
    drivers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
        limit_choices_to={'is_driver': True},
        help_text=_("Drivers assigned to the vehicle"))
    latitude = models.FloatField(verbose_name='Latitude', blank=True, null=True,
        help_text=_('Current latitude of the vehicle'))
    longitude = models.FloatField(verbose_name='Longitude', blank=True, null=True,
        help_text=_('Current longitude of the vehicle'))
    active_driver = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE,
        help_text=_("Current driver who is riding the vehicle"), blank=True,
        null=True, related_name='active_driver')
    location_update_datetime = models.DateTimeField(_('Location update date '
        'and time'), help_text=_("Date and time when the vehicle's location "
        "was last updated"), null=True, blank=True)
    objects = models.Manager()
    travels = VehicleTravelManager()

    #Return user friendly string representation of the object
    def get_active_driver(self):
        """
        Method returns the driver who last updated the location of
        the vehicle, essentially, this determines which driver is actually
        driving the vehicle right now
        """
        # Doing boolean comparisons for performance
        return self.get_driver_str(self.active_driver)

    # This is the description for the admin page
    get_active_driver.short_description = _('Currently active driver')

    def __str__(self):
        """
        String method of the Vehicle.
        This method returns: Car model, id, registration number. Also, it
        it returns main and alternative drivers information.
        """
        return _('{} - {} - {}').format(
            self.car_id, self.car_instance, self.registration_number,
        )

    def get_driver_str(self, user_obj):
        """
        Helper method to construct a string containing driver name and
        a phone.
        """
        if not user_obj:
            return ''
        if user_obj.first_name and user_obj.last_name:
            name = "{} {}".format(user_obj.first_name,
                user_obj.last_name)
        elif user_obj.first_name:
            name = user_obj.first_name
        else:
            name = user_obj.username
        if user_obj.phone:
            name += ', {}'.format(user_obj.phone)
        return name

    def get_guest_str(self):
        """
        This function returns guest compatible view with only relevant
        amount of data.
        For use on travel request detail pages viewed by users.
        """
        return '{} {}'.format(self.car_instance, self.registration_number)
