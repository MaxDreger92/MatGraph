import uuid
from typing import Union

from django import forms
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.views.generic import TemplateView
from django.db import models
from neomodel import db

from schema_ingestion.neo4j_handlers import Neo4jFabricationWorkflowHandler, Neo4jDataHandler, \
    Neo4jOrganizationalDataHandler, Neo4jMeasurementHandler


class UUIDModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)



    class Meta:
        abstract = True  # Ensure this is set to make it an abstract base class


        
# Models
class Step(UUIDModel):
    order = models.PositiveIntegerField(default=0, help_text="Defines the order of the step within the analysis.")

    class Meta:
        ordering = ['order']
        abstract = True  # Makes this model abstract

    def __str__(self):
        return f"Step {self.order}: {self.get_technique()}"

    def get_technique(self):
        # This method should be overridden by child models
        return "Technique Not Defined"

class OrganizationalData(UUIDModel, Neo4jOrganizationalDataHandler):
    experiment = models.ForeignKey(
        'schema_ingestion.Experiment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='organizational_data_experiment'
    )
    experiment_title = models.CharField(max_length=255)
    external_experiment_id = models.CharField(max_length=50, blank=True, null=True)  # Renamed to avoid clash
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

    def save(self, *args, **kwargs):
        print("Saving instance to Neo4j")
        # Save the instance to the Django database first
        super().save(*args, **kwargs)

        # After saving, prepare data for Neo4j
        self._save_to_neo4j()

class Quantity(UUIDModel):
    value = models.FloatField()
    error = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=10)
    name = models.CharField(max_length=100, default = None)


class Material(UUIDModel):
    name = models.CharField(max_length=100)
    amount = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=50, null=True, blank=True)
    lot_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

class Metadata(UUIDModel):
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

class Technique(UUIDModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class SynthesisStep(Step):
    precursor_materials = models.ManyToManyField(Material, related_name="s_precursors", blank=True)
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE)
    parameter = models.ManyToManyField(Quantity, related_name="s_parameters")
    target_materials = models.ManyToManyField(Material, related_name="s_targets")
    metadata = models.ManyToManyField(Metadata, related_name="s_metadata")

    def get_technique(self):
        return self.technique.name


class Synthesis(UUIDModel, Neo4jFabricationWorkflowHandler):
    steps = models.ManyToManyField(SynthesisStep, related_name="steps")
    experiment = models.ForeignKey(
        'schema_ingestion.Experiment',
        on_delete=models.CASCADE,
        blank=True,
        default=None,
        related_name='syntheses_experiment'  # Changed from default to 'syntheses'
    )


    def save(self, *args, **kwargs):
        # Save the instance to the Django database first
        super().save(*args, **kwargs)

        # After saving, prepare data for Neo4j
        self._save_to_neo4j()







class SamplePreparationStep(Step, Neo4jFabricationWorkflowHandler):
    precursor_materials = models.ManyToManyField(Material, related_name="sp_precursors", blank=True)
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE)
    parameter = models.ManyToManyField(Metadata, related_name="sp_parameters")
    target_materials = models.ManyToManyField(Material, related_name="sp_targets")
    metadata = models.ManyToManyField(Metadata, related_name="sp_metadata")

class SamplePreparation(UUIDModel, Neo4jFabricationWorkflowHandler):
    steps = models.ManyToManyField(SamplePreparationStep)
    experiment = models.ForeignKey(
        'schema_ingestion.Experiment',
        on_delete=models.CASCADE,
        blank=True,
        default=None,
        related_name='sample_preparation_experiment'  # Changed from default to 'syntheses'
    )


    def save(self, *args, **kwargs):
            # Save the instance to the Django database first
            super().save(*args, **kwargs)

            # After saving, prepare data for Neo4j
            self._save_to_neo4j()


class Data(UUIDModel):
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

class Preprocessing(UUIDModel, Neo4jDataHandler):
    steps = models.ManyToManyField(PreprocessingStep)
    experiment = models.ForeignKey(
        'schema_ingestion.Experiment',
        on_delete=models.CASCADE,
        blank=True,
        null=True,  # Add null=True to allow NULL values in the database
        default=None,
        related_name='preprocessing_experiment'
    )

    def save(self, *args, **kwargs):
        print("Saving instance to Neo4j")
        # Save the instance to the Django database first
        super().save(*args, **kwargs)

        # After saving, prepare data for Neo4j
        self._save_to_neo4j()


class Analysis(UUIDModel, Neo4jDataHandler):
    steps = models.ManyToManyField(AnalysisStep, related_name="a_steps")
    experiment = models.ForeignKey(
        'schema_ingestion.Experiment',
        on_delete=models.CASCADE,
        blank=True,
        default=None,
        null=True,
        related_name='analysis_experiment')

    def save(self, *args, **kwargs):
        # Save the instance to the Django database first
        super().save(*args, **kwargs)

        # After saving, prepare data for Neo4j
        self._save_to_neo4j()



class Measurement(UUIDModel, Neo4jMeasurementHandler):
    experiment = models.ForeignKey(
        'schema_ingestion.Experiment',  # Update the app label if different
        on_delete=models.CASCADE,
        related_name='measurements',
        null=True,
        blank=True,
    )

    measurement_method = models.CharField(
        max_length=255,
        help_text="Method used for the measurement (e.g., X-Ray Diffraction, Spectroscopy)."
    )
    measurement_type = models.CharField(
        max_length=255,
        help_text="Type of measurement conducted (e.g., Structural, Thermal)."
    )
    specimen = models.CharField(
        max_length=255,
        help_text="Description or identifier of the specimen being measured."
    )
    temperature = models.FloatField(
        null=True,
        blank=True,
        help_text="Temperature at which the measurement was conducted."
    )
    temperature_unit = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=[
            ('C', 'Celsius'),
            ('F', 'Fahrenheit'),
            ('K', 'Kelvin'),
            # Add more units as needed
        ],
        help_text="Unit of temperature."
    )
    pressure = models.FloatField(
        null=True,
        blank=True,
        help_text="Pressure at which the measurement was conducted."
    )
    pressure_unit = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=[
            ('atm', 'Atmospheres'),
            ('bar', 'Bar'),
            ('psi', 'Pounds per Square Inch'),
            # Add more units as needed
        ],
        help_text="Unit of pressure."
    )
    atmosphere = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Atmospheric conditions during the measurement (e.g., Vacuum, Air)."
    )

    # Timestamp Fields
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the measurement was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the measurement was last updated.")

    def __str__(self):
        return f"Measurement {self.uid} - {self.measurement_method} ({self.measurement_type})"

    class Meta:
        verbose_name = "Measurement"
        verbose_name_plural = "Measurements"
        ordering = ['-created_at']  # Orders measurements by most recent first

    def save(self, *args, **kwargs):
        print("Saving instance to Neo4j")
        # Save the instance to the Django database first
        super().save(*args, **kwargs)

        # After saving, prepare data for Neo4j
        self._save_to_neo4j()


class Experiment(UUIDModel):
    experiment_id = models.CharField(max_length=50, unique=True, blank=True, null=True, default=uuid.uuid4, editable=False)
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE, null=True, blank=True, related_name='experiments_measurement')
    organizational_data = models.ForeignKey(OrganizationalData, on_delete=models.CASCADE, null=True, blank=True, related_name='experiments_organizational_data')
    synthesis = models.ForeignKey(Synthesis, on_delete=models.CASCADE, null=True, blank=True, related_name='experiments_synthesis')
    sample_preparation = models.ForeignKey(SamplePreparation, on_delete=models.CASCADE, null=True, blank=True, related_name='experiments_sample_preparation')
    preprocessing = models.ForeignKey(Preprocessing, on_delete=models.CASCADE, null=True, blank=True, related_name='experiments_preprocessing')
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, null=True, blank=True, related_name='experiments_analysis')
    characterization = models.ForeignKey(Measurement, on_delete=models.CASCADE, null=True, blank=True, related_name='experiments_characterization')

    def __str__(self):
        return f"Experiment {self.experiment_id}"

    def _save_to_neo4j(self):
        return True
