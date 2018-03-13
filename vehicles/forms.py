from django.forms import ModelForm, CharField, widgets
from django.utils.translation import ugettext_lazy as _
from vehicles.widgets import MapWidget


class VehicleAdminForm(ModelForm):
    _map = CharField(
        label=_('Map'),
        help_text=_('Map displays last known vehicle location if available'),
        widget=MapWidget,
        required=False,
    )

    class Media:
        css = {
            'all': ('assets/css/custom.css',)
        }

    class Meta:
        widgets = {
            'latitude': widgets.HiddenInput(),
            'longitude': widgets.HiddenInput(),
        }
