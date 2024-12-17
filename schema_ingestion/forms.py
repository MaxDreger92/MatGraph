from django import forms
from django.forms import modelformset_factory, formset_factory

from .models import OrganizationalData, SynthesisStep, SamplePreparationStep, AnalysisStep, Synthesis, \
    SamplePreparation, Quantity, Metadata, Technique, Material


class ExcelUploadForm(forms.Form):
    file = forms.FileField()

class OrganizationalForm(forms.ModelForm):
    class Meta:
        model = OrganizationalData
        fields = [
            'experiment_title', 'experiment_id', 'measurement_id', 'upload_date', 'measurement_date', 'institution',
            'founding_body', 'country', 'author', 'orcid', 'email', 'published', 'publication', 'doi', 'journal',
            'volume', 'issue', 'pages', 'publication_date', 'topic', 'device', 'component', 'subcomponent',
            'granularity_level', 'format', 'file_size', 'file_size_unit', 'file_name', 'dimension_x', 'dimension_y',
            'dimension_z', 'pixel_per_metric', 'link', 'mask_exist', 'mask_link'
        ]
        widgets = {
            'experiment_title': forms.TextInput(attrs={'class': 'form-control'}),
            'experiment_id': forms.TextInput(attrs={'class': 'form-control'}),
            'measurement_id': forms.TextInput(attrs={'class': 'form-control'}),
            'upload_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'measurement_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'founding_body': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'orcid': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'publication': forms.TextInput(attrs={'class': 'form-control'}),
            'doi': forms.TextInput(attrs={'class': 'form-control'}),
            'journal': forms.TextInput(attrs={'class': 'form-control'}),
            'volume': forms.NumberInput(attrs={'class': 'form-control'}),
            'issue': forms.NumberInput(attrs={'class': 'form-control'}),
            'pages': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'device': forms.TextInput(attrs={'class': 'form-control'}),
            'component': forms.TextInput(attrs={'class': 'form-control'}),
            'subcomponent': forms.TextInput(attrs={'class': 'form-control'}),
            'granularity_level': forms.TextInput(attrs={'class': 'form-control'}),
            'format': forms.TextInput(attrs={'class': 'form-control'}),
            'file_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'file_size_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'file_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dimension_x': forms.NumberInput(attrs={'class': 'form-control'}),
            'dimension_y': forms.NumberInput(attrs={'class': 'form-control'}),
            'dimension_z': forms.NumberInput(attrs={'class': 'form-control'}),
            'pixel_per_metric': forms.NumberInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
            'mask_exist': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mask_link': forms.URLInput(attrs={'class': 'form-control'}),
        }
# Form for Quantity
from django import forms
from .models import SynthesisStep, Material, Metadata


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'amount', 'unit']  # Replace with your actual model fields
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Material Name', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'placeholder': 'Value', 'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'placeholder': 'Unit', 'class': 'form-control'}),
        }

class MetadataForm(forms.ModelForm):
    class Meta:
        model = Metadata
        fields = ['key', 'value']
        widgets = {
            'key': forms.TextInput(attrs={'placeholder': 'Key'}),
            'value': forms.TextInput(attrs={'placeholder': 'Value'}),
        }

class QuantityForm(forms.ModelForm):
    class Meta:
        model = Quantity
        fields = ['value', 'error', 'unit']
        widgets = {
            'value': forms.NumberInput(attrs={'placeholder': 'Value'}),
            'error': forms.NumberInput(attrs={'placeholder': 'Error'}),
            'unit': forms.TextInput(attrs={'placeholder': 'Unit'}),
        }

class TechniqueForm(forms.ModelForm):
    class Meta:
        model = Technique
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Technique Name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description'}),
        }



class SynthesisStepForm(forms.ModelForm):
    class Meta:
        model = SynthesisStep
        fields = ['precursor_materials', 'parameter', 'technique', 'target_materials', 'metadata']
        widgets = {
            'precursor_materials': forms.TextInput(attrs={'class': 'form-control'}),
            'parameter': forms.Textarea(attrs={'class': 'form-control'}),
            'target_materials': forms.Textarea(attrs={'class': 'form-control'}),
            'technique': forms.Select(attrs={'class': 'form-control'}),
            'metadata': forms.Textarea(attrs={'class': 'form-control'}),

        }

# Create formsets for materials and metadata
MaterialFormset = formset_factory(MaterialForm, extra=1, can_delete=True)
MetadataFormset = formset_factory(MetadataForm, extra=1, can_delete=True)
ParameterFormset = formset_factory(QuantityForm, extra=1, can_delete=True)
TechniqueFormset = formset_factory(TechniqueForm, extra=1, can_delete=True)

class SamplePreparationForm(forms.ModelForm):
    class Meta:
        model = SamplePreparation
        fields = []


class AnalysisForm(forms.ModelForm):
    class Meta:
        model = AnalysisStep
        fields = ['data_inputs', 'quantity_inputs', 'metadata', 'data_results', 'quantity_results']
