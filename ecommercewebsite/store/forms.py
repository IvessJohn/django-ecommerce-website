from django import forms
from django_countries.widgets import CountrySelectWidget

from .models import *


class ShippingInformationForm(forms.ModelForm):
    class Meta:
        model = ShippingInformation
        fields = ('address', 'city', 'state', 'zipcode', 'country')
        widgets = {'country': CountrySelectWidget()}

        def __init__(self, *args, **kwargs):
            super(ShippingInformationForm, self).__init__(*args, **kwargs)
            for field in self.fields:
                field.widget.attrs.update({'class' : 'form-control'})