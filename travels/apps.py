from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TravelsConfig(AppConfig):
    name = 'travels'
    verbose_name = _('Pickup Requests')
