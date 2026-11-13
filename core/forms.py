from django import forms
from django.forms import inlineformset_factory
from django.forms import BaseInlineFormSet, inlineformset_factory
from .models import (
    PatientComment, Patient, Address, Disease, Medication, Family
)


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css = 'form-check-input'
            elif isinstance(widget, forms.Select):
                css = 'form-select'
            else:
                css = 'form-control'
            widget.attrs.setdefault('class', css)


class PatientCommentForm(forms.ModelForm):
    class Meta:
        model = PatientComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Escribe un comentario...',
                'class': 'form-control',
            })
        }


class PatientForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'phone', 'email',
                  'birth_date', 'picture', 'preferred_companion']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preferred_companion'].empty_label = "Sin preferencia"


class AddressForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'ext_number', 'int_number',
                  'neighborhood', 'city', 'state', 'zip_code']


class DiseaseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Disease
        fields = ['name', 'comment']
        widgets = {'comment': forms.Textarea(attrs={'rows': 2})}


class MedicationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['name', 'dosage', 'frequency', 'active', 'comment']
        widgets = {'comment': forms.Textarea(attrs={'rows': 2})}


class FamilyForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Family
        fields = ['first_name', 'last_name', 'phone', 'email', 'relationship']

class FamilyBaseFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('error_messages', {
            'too_few_forms': 'Debes registrar al menos un familiar para poder enviarle los reportes.',
        })
        super().__init__(*args, **kwargs)


FamilyFormSet = inlineformset_factory(
    Patient, Family, form=FamilyForm, formset=FamilyBaseFormSet,
    extra=1, can_delete=True, min_num=1, validate_min=True
)


DiseaseFormSet = inlineformset_factory(
    Patient, Disease, form=DiseaseForm, extra=1, can_delete=True
)
MedicationFormSet = inlineformset_factory(
    Patient, Medication, form=MedicationForm, extra=1, can_delete=True
)
FamilyFormSet = inlineformset_factory(
    Patient, Family, form=FamilyForm, extra=1, can_delete=True,
    min_num=1, validate_min=True
)