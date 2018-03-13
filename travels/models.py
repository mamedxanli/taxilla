from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _
from home.models import BaseModel
from vehicles.models import Vehicle
from django.contrib.postgres.fields import DateTimeRangeField


class Travel(BaseModel):
    """
    Travel model describing a single travel.
    """
    # Base model fields
    traveller = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE,
        help_text=_("Requester which intends to travel"))
    pickup = models.CharField(max_length=200,
        help_text=_("Pickup address or location name"))
    dropoff = models.CharField(max_length=200,
        help_text=_("Destination or drop-off address or location name"))
    pickup_data = JSONField(default=dict(),
        help_text=_("JSON encoded pickup location data"))
    dropoff_data = JSONField(default=dict(),
        help_text=_("JSON encoded dropoff location data"))
    date_time = models.DateTimeField(_('Date and time of the intended trip'))
    duration_range = DateTimeRangeField(_('Approximate duration of the trip'),
        blank=True, null=True, help_text=_("This field holds two datetime "
        "objects: starttime of travel and its end time. Duration is calculate"
        "d by the difference between end and start times."))
    notes = models.TextField(max_length=500, blank=True,
        help_text=_("Any additional notes left by the traveller/requester"))
    assigned_operator = models.ForeignKey(settings.AUTH_USER_MODEL,
        models.CASCADE, blank=True, null=True, related_name='assigned_travels',
        limit_choices_to={'is_staff': True, 'is_superuser': False},
        help_text=_("Operator user assigned to process the request"))
    # note that since Django 1.9 'on_delete' can now be used as the second
    # positional argument (it used to be just a keyword argument)
    assigned_vehicle = models.ForeignKey(Vehicle, models.SET_NULL, blank=True,
        null=True, limit_choices_to={'drivers__isnull': False},
        help_text=_("Vehicle assigned to fulfill the request"))
    assigned_driver = models.ForeignKey(settings.AUTH_USER_MODEL,
        models.CASCADE, help_text=_('Driver assigned to the request'),
        related_name='assigned_driver', blank=True, null=True,
        limit_choices_to={'is_driver': True})
    distance = models.CharField('Approximate travel distance', blank=True,
        null=True, help_text=_('This is the distance between pickup and'
        ' dropoff locations'), max_length=25)
    distance_raw = models.IntegerField(null=True, blank=True, default=0,
        help_text=_('Approximate travel distance in meters'))
    advanced_vehicle = models.BooleanField('Advanced vehicle selection',
        help_text=_("Option enables operators to freely choose and assign a "
        "vehicle to the request. An operator needs to tick the option and then "
        "click 'Save and continue editing' to avail of this feature. Once they "
        "do that, they will need to click the 'scope' button in order to open "
        "the advanced vehicle selection popup."), default=False)
    duration_vehicle = models.IntegerField(_('Duration to the vehicle'),
        blank=True, default=0, help_text=_('Duration in seconds for the vehicle'
        ' to reach the passenger. This value is calculated by the backend and '
        'automatically updated once the location of the vehicle changes.'),
        null=True)

    # Define choices here
    STATUSES = (
        (0, _('New')),
        (1, _('Approved')),
        (2, _('Declined')),
    )

    # Additional model fields
    no_of_passengers = models.IntegerField(
        choices=Vehicle.NUMBER_OF_SEATS_CHOICES, default=3)
    status = models.IntegerField(choices=STATUSES, default=0)

    def __str__(self):
        """
        Return user friendly string representation of the object
        """
        if self.traveller.first_name and self.traveller.last_name:
            name = "{} {}".format(self.traveller.first_name,
                self.traveller.last_name)
        elif self.traveller.first_name:
            name = self.traveller.first_name
        else:
            name = self.traveller.username

        return _('{} requested a car from {} to {}').format(name,
            self.pickup, self.dropoff)

    def is_resolved(self):
        """
        Determines whether the request is resolved or not.
        If either assigned_operator or assigned_vehicle fields are blank
        or status is 'New' this function will return False
        """
        return bool(self.assigned_operator and self.assigned_vehicle
            and self.status > 0)

    # This is required in order for admin consider this as a BooleanField
    is_resolved.boolean = True
    is_resolved.short_description = "Resolved?"

    def get_absolute_url(self):
        """
        Handy way of getting the url of the object to its detail view page
        """
        return reverse('travel-detail', args=(self.id, ))

    def get_duration(self):
        """
        Return a human friendly representation of the intended trip duration.
        This is calculated by using values in duration_range field.
        """
        duration = self.duration_range.upper - self.duration_range.lower
        return self._get_timedelta_str(duration.seconds)

    def get_vehicle_waiting_time(self):
        """
        Returns time for a vehicle to arrive to pickup point.
        """
        return self._get_timedelta_str(self.duration_vehicle)

    def get_driver_info(self):
        """
        Return detailed information about the driver(s) assigned to a vehicle
        """
        text = ''
        if self.assigned_vehicle and self.assigned_driver:
            text += str(self.assigned_vehicle.get_driver_str(
                self.assigned_driver)) + '\n'
        return text

    get_driver_info.short_description = _('Assigned driver')

    def _get_timedelta_str(self, seconds):
        """
        Returns str() hours and minutes constructed from seconds
        """
        minutes = seconds // 60
        hours = 0
        while minutes > 60:
            hours += 1
            minutes -= 60
        if hours > 0:
            result = _("{} hours {} minutes").format(hours, minutes)
        else:
            result = _("{} minutes").format(minutes)
        return result

    class Meta:
        verbose_name = _('request')
        ordering = ['-date_time']
