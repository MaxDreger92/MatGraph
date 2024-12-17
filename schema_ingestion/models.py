import uuid
from typing import Union

from django import forms
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.views.generic import TemplateView
from django.db import models

# Models
class Step(models.Model):
    order = models.PositiveIntegerField(default=0, help_text="Defines the order of the step within the analysis.")

    class Meta:
        ordering = ['order']
        abstract = True  # Makes this model abstract

    def __str__(self):
        return f"Step {self.order}: {self.get_technique()}"

    def get_technique(self):
        # This method should be overridden by child models
        return "Technique Not Defined"

class OrganizationalData(models.Model):
    experiment_title = models.CharField(max_length=255)
    experiment_id = models.CharField(max_length=50)
    measurement_id = models.CharField(max_length=50)
    upload_date = models.DateField()
    measurement_date = models.DateField(null=True, blank=True)
    institution = models.CharField(max_length=255)
    founding_body = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    author = models.TextField(null=True, blank=True)  # Store as a newline-separated string
    orcid = models.TextField(null=True, blank=True)  # Store as a newline-separated string
    email = models.TextField(null=True, blank=True)  # Store as a newline-separated string
    published = models.CharField(max_length=50, null=True, blank=True)
    publication = models.CharField(max_length=255, null=True, blank=True)
    doi = models.URLField(null=True, blank=True)
    journal = models.CharField(max_length=255, null=True, blank=True)
    volume = models.CharField(max_length=50, null=True, blank=True)
    issue = models.CharField(max_length=50, null=True, blank=True)
    pages = models.CharField(max_length=50, null=True, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    topic = models.CharField(max_length=255, null=True, blank=True)
    device = models.CharField(max_length=255, null=True, blank=True)
    component = models.CharField(max_length=255, null=True, blank=True)
    subcomponent = models.CharField(max_length=255, null=True, blank=True)
    granularity_level = models.CharField(max_length=255, null=True, blank=True)
    format = models.CharField(max_length=50, null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    file_size_unit = models.CharField(max_length=10, null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    dimension_x = models.PositiveIntegerField(null=True, blank=True)
    dimension_y = models.PositiveIntegerField(null=True, blank=True)
    dimension_z = models.PositiveIntegerField(null=True, blank=True)
    pixel_per_metric = models.FloatField(null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    mask_exist = models.BooleanField(default=False)
    mask_link = models.URLField(null=True, blank=True)

class Quantity(models.Model):
    value = models.FloatField()
    error = models.FloatField()
    unit = models.CharField(max_length=10)


class Material(models.Model):
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    unit = models.CharField(max_length=50)
    lot_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

class Metadata(models.Model):
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

class Technique(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

class SynthesisStep(Step):
    precursor_materials = models.ManyToManyField(Material, related_name="s_precursors", blank=True)
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE)
    parameter = models.ManyToManyField(Metadata, related_name="s_parameters")
    target_materials = models.ManyToManyField(Material, related_name="s_targets")
    metadata = models.ManyToManyField(Metadata, related_name="s_metadata")


class Synthesis(models.Model):
    synthesis_steps = models.ManyToManyField(SynthesisStep, related_name="steps")



class SamplePreparationStep(Step):
    precursor_materials = models.ManyToManyField(Material, related_name="sp_precursors", blank=True)
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE)
    parameter = models.ManyToManyField(Metadata, related_name="sp_parameters")
    target_materials = models.ManyToManyField(Material, related_name="sp_targets")
    metadata = models.ManyToManyField(Metadata, related_name="sp_metadata")

class SamplePreparation(models.Model):
    sample_preparation_steps = models.ManyToManyField(SamplePreparationStep)

class Data(models.Model):
    data_type = models.CharField(max_length=100)
    data_format = models.CharField(max_length=100)
    data = models.FileField(upload_to='data/')
    link = models.URLField(null=True, blank=True)

class AnalysisStep(Step):
    data_inputs = models.ManyToManyField(Data, related_name="analysis_steps_as_data", blank=True)
    quantity_inputs = models.ManyToManyField(Quantity, related_name="analysis_steps_as_quantity", blank=True)
    metadata = models.ManyToManyField(Metadata, related_name="analysis_metadata")
    technique = models.TextField(blank=True)
    parameter = models.ManyToManyField(Quantity, related_name="analysis_parameters")
    data_results = models.ManyToManyField(Data, related_name="analysis_results_as_data", blank=True)
    quantity_results = models.ManyToManyField(Quantity, related_name="analysis_results_as_quantity", blank=True)

class PreprocessingStep(Step):
    data_inputs = models.ManyToManyField(Data, related_name="pp_steps_as_data", blank=True)
    quantity_inputs = models.ManyToManyField(Quantity, related_name="pp_steps_as_quantity", blank=True)
    metadata = models.ManyToManyField(Metadata, related_name="pp_metadata")
    technique = models.TextField(blank=True)
    parameter = models.ManyToManyField(Quantity, related_name="pp_parameters")
    data_results = models.ManyToManyField(Data, related_name="pp_results_as_data", blank=True)
    quantity_results = models.ManyToManyField(Quantity, related_name="pp_results_as_quantity", blank=True)

class Preprocessing(models.Model):
    preprocessing_steps = models.ManyToManyField(PreprocessingStep)

class Analysis(models.Model):
    analysis_steps = models.ManyToManyField(AnalysisStep)

class Characterization(models.Model):
    measurement_method = models.CharField(max_length=100)
    measurement_type = models.CharField(max_length=100)
    specimen = models.CharField(max_length=100)
    temperature = models.FloatField()
    temperature_unit = models.CharField(max_length=10)
    pressure = models.FloatField()
    pressure_unit = models.CharField(max_length=10)
    atmosphere = models.CharField(max_length=100)


class Experiment(models.Model):
    experiment_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4, editable=False)
    organizational_data = models.ForeignKey(OrganizationalData, on_delete=models.CASCADE, null=True, blank=True)
    synthesis = models.ForeignKey(Synthesis, on_delete=models.CASCADE, null=True, blank=True)
    sample_preparation = models.ForeignKey(SamplePreparation, on_delete=models.CASCADE, null=True, blank=True)
    preprocessing = models.ForeignKey(Preprocessing, on_delete=models.CASCADE, null=True, blank=True)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, null=True, blank=True)
    characterization = models.ForeignKey(Characterization, on_delete=models.CASCADE, null=True, blank=True)

