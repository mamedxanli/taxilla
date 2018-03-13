from django.db import models
from home.models import BaseModel


class Company(BaseModel):
    """
    Class describing company a passenger works for. E.g.: BP.
    """
    name = models.CharField("Company name", max_length=50,
        help_text='Name of the company')
    description = models.CharField("Company description", max_length=200,
        blank=True, help_text='Description of the company')
    enabled = models.BooleanField(default=False,
        help_text='Option enables operators to make company available '
        'in order to assign it to particular user')

    def __str__(self):
        """
        Returns name of the  company
        """
        return "{} company".format(self.name)

    class Meta:
        verbose_name_plural = 'companies'
