from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from companies.models import Company
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class DriverManager(models.Manager):
    def get_queryset(self):
        return super(DriverManager, self).get_queryset().filter(is_driver=True)


class OperatorManager(models.Manager):
    def get_queryset(self):
        return super(OperatorManager, self).get_queryset().filter(is_staff=True,
            is_superuser=False)


class RegularUserManager(models.Manager):
    def get_queryset(self):
        return super(RegularUserManager, self).get_queryset().filter(
            is_driver=False, is_staff=False)


class AdminManager(models.Manager):
    def get_queryset(self):
        return super(AdminManager, self).get_queryset().filter(is_staff=True,
            is_superuser=True)


class TaxillaUser(AbstractUser):
    """
    This model to contain all users: regular, drivers, operators
    """
    employee_id = models.CharField(max_length=20, default="Unregistered")
    company = models.ForeignKey(Company, verbose_name="Employer name",
        blank=True, null=True)
    phone = models.CharField(max_length=50)
    title = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    is_driver = models.BooleanField(default=False)
    objects = UserManager()
    drivers = DriverManager()
    operators = OperatorManager()
    users = RegularUserManager()
    admins = AdminManager()


    LEVELS = (
        (None, 'Please pick the level'),
        ('lv1', 'Reek'),
        ('lv2', 'TBA'),
        ('lv3', 'Level 3 - Junior engineer'),
        ('lv4', 'Level 4 - Engineer'),
        ('lv5', 'level 5 - Senior engineer'),
        ('lv6', 'Level 6 - Principal engineer'),
        ('lv7', 'Level 7 - Lead engineer'),
        ('lv8', 'Level 8 - Legendary engineer'),
    )

    VIP = ((0, "Standard"),(1, "VIP"),)

    corporate_level = models.CharField(max_length=50, choices=LEVELS,
        default=None, blank=True, null=True)

    vip = models.BooleanField(default=False)


    def get_absolute_url(self):
        """
        Gets the full url of the user to personal page
        Allows user to submit data on profile page and
        return to the same page
        """
        return reverse('account-edit', args=[str(self.id)])


    def __str__(self):
        """
        Return user friendly string representation of the object
        """
        name = "{} {}".format(self.first_name, self.last_name)
        return name
