from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory

from .models import Call, Lead, Profile, Vehicle


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        exclude = ['agent', 'status', 'next_call_date']

    def __init__(self, *args, **kwargs):
        super(LeadForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control input-sm'


class VehileForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        exclude = ['lead']


class UploadFileForm(forms.Form):
    file = forms.FileField()


VehicleFormset = inlineformset_factory(
    Lead,
    Vehicle,
    fields=(
        'make',
        'vehicle_model',
        'reg_number',
        'insurance_expiry',
    ),
    extra=1,
    can_delete=False
)


VehicleFormset1 = inlineformset_factory(
    Lead,
    Vehicle,
    fields=(
        'id',
        'make',
        'vehicle_model',
        'reg_number',
        'insurance_expiry',
        'status',
        'policy_type',
        'policy_number'
    ),
    extra=1,
    can_delete=False
)


class CallForm(forms.ModelForm):
    class Meta:
        model = Call
        fields = ['close_status', 'notes']


class AffiliateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['birth_date', 'city', 'account_number', 'ecocash_name',]


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
