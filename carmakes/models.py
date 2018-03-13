from django.db import models
from home.models import BaseModel
from django.utils import timezone
from django.utils.translation import ugettext as _

class Manufacturer(BaseModel):
    """
    Class describing Car make. Example: 'Volvo'.
    """
    make = models.CharField("Car manufacturer", max_length=50,
        unique=True, help_text=_("Car manufacturer field. Example: 'Volvo'."))

    def __str__(self):
        """
        Returns manufacturer.
        """
        return self.make

    class Meta:
        verbose_name = _('Car manufacturer')


class Car(BaseModel):
    """
    Class describing make and model of a car. Example: "Land Rover Freelander".
    """
    manufacturer = models.ForeignKey(Manufacturer,
        help_text=_("Car manufacturer field. Example: 'Volvo'."))
    model = models.CharField("Model", max_length=100, unique=True,
        help_text=_("Car model field. Example: if model is 'Volvo'"
        "then this field can be S40."))

    def __str__(self):
        """
        Returns manufacturer and model.
        """
        return("{0} {1}".format(self.manufacturer, self.model))

    unique_together = ("manufacturer", "model")

    class Meta:
        verbose_name = _('Car model')
