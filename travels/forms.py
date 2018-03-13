import sys
import logging

from django.contrib import admin
from django.forms import (ModelForm, ValidationError, CharField, BooleanField,
    widgets)
from django.utils.translation import ugettext_lazy as _
from travels.models import Travel
from travels.widgets import MapWidget


log = logging.getLogger(__name__)


class TravelForm(ModelForm):

    # Field to enable geolocation for user forms
    geolocation = BooleanField(required=False, widget=widgets.HiddenInput(),
        initial=True)

    def clean_pickup_data(self):
        """
        Clean the pickup_data field and check if JSON is valid
        """
        data = self.cleaned_data['pickup_data']
        if sys.getsizeof(data) > 1000000:
            raise ValidationError("JSON size is too large!")
        return data

    def clean_dropoff_data(self):
        """
        Clean the dropoff_data field and check if JSON is valid
        """
        data = self.cleaned_data['dropoff_data']
        if sys.getsizeof(data) > 1000000:
            raise ValidationError("JSON size is too large!")
        return data

    class Meta:
        model = Travel
        fields = (
            'pickup',
            'dropoff',
            'pickup_data',
            'dropoff_data',
            'date_time',
            'no_of_passengers',
            'notes',
        )
        labels = {
            'pickup': _('From'),
            'dropoff': _('To'),
            'date_time': _('Date and time'),
            'no_of_passengers': _('Number of passengers'),
            'notes': _('Additional notes'),
        }
        help_texts = {
            'pickup': _('Address where you expect a pickup'),
            'dropoff': _('Destination address where you expect to go'),
            'date_time': _('Date and time when you expect a pickup'),
            'notes': _('Optional notes you wish to include with the request'),
            'no_of_passengers': _('Please indicate the number of passengers'),
        }
        error_messages = {
            'pickup_data': {
                'required': _('Please enter a valid address'),
            },
            'dropoff_data': {
                'required': _('Please enter a valid address'),
            },
            'date_time': {
                'required': _('Please enter a valid date and time'),
            },
        }
        widgets = {
            'pickup_data': widgets.HiddenInput(),
            'dropoff_data': widgets.HiddenInput(),
            'notes': widgets.Textarea(attrs={
                'rows': 6,
                'placeholder': _('You can include additional notes with your '
                    'request here')
            }),
        }


class TravelAdminForm(TravelForm):
    _map = CharField(
        label=_('Map'),
        help_text=_('Map displays pickup and dropoff points'),
        widget=MapWidget,
        required=False,
    )
    # Field to disable geolocation for admin forms
    geolocation = BooleanField(required=False, widget=widgets.HiddenInput(),
        initial=False)

    def __init__(self, *args, **kwargs):
        super(TravelAdminForm, self).__init__(*args, **kwargs)
        q = self.fields['assigned_vehicle'].queryset.distinct()
        self.fields['assigned_vehicle'].queryset = q

    def clean(self):
        cleaned_data = super(TravelAdminForm, self).clean()
        try:
            vehicle = cleaned_data['assigned_vehicle']
            status = cleaned_data['status']
        except KeyError as err:
            log.error('Houston weve got a problem')
            log.error(err)
        else:
            if status == 1 and not vehicle:
                msg = _('You need to assign a vehicle before approving a request')
                self.add_error('status', msg)
        return cleaned_data

    class Media:
        css = {
            'all': ('assets/css/custom.css',)
        }

    class Meta:
        model = Travel
        fields = (
            'pickup',
            'dropoff',
            'pickup_data',
            'dropoff_data',
            'date_time',
            'no_of_passengers',
            'notes',
            'status',
            'assigned_vehicle'
        )
        labels = {
            'get_duration': _('Duration'),
            'get_vehicle_waiting_time': _('Vehicle waiting time'),
            'pickup': _('From'),
            'dropoff': _('To'),
            'date_time': _('Date and time'),
            'no_of_passengers': _('Number of passengers'),
            'notes': _('Additional notes'),
        }
        help_texts = {
            'pickup': _('Address where traveller expects a pickup'),
            'dropoff': _('Destination address where traveller expects to go'),
            'date_time': _('Date and time of the expected pickup'),
            'notes': _('Optional notes left by the traveller'),
            'no_of_passengers': _('Number of travelling passengers'),
            'assigned_vehicle': _('Pick a vehicle to associate with this '
                                  'request'),
            'status': _('Change the status of the request to let the requester'
                        ' know'),
            'assigned_operator': _('Assign or reassign this request to another'
                                   ' operator'),
            'advanced_vehicle': _('Tick here, then "Save and continue editing"'
                ' in order to manually pick a vehicle'),
            'get_vehicle_waiting_time': _('Approximate time it will take for '
                'the vehicle to reach the passengers')
        }
