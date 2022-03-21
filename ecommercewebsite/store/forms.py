from django import forms
from django_countries.widgets import CountrySelectWidget
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']