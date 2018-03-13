from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.forms import ValidationError



class TaxillaUserForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    phone = forms.CharField(max_length=50,
        validators=[RegexValidator("[0]+(\d{2})+(\d?)-(\d{6})+((\d{0,2})?)",
        message="Please use the format like the example: 050-12345678 ")])

    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "phone",
            "email",
            "company",
            "employee_id",
            "title",
            "department",
            "location",
            "corporate_level",
        )
