import uuid
from typing import Union

from django import forms
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.views.generic import TemplateView
from django.db import models

# Models
class UUIDModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True  # Ensure this is set to make it an abstract base class
        
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

class OrganizationalData(UUIDModel):
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

class Quantity(UUIDModel):
    value = models.FloatField()
    error = models.FloatField()
    unit = models.CharField(max_length=10)


class Material(UUIDModel):
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    unit = models.CharField(max_length=50)
    lot_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

class Metadata(UUIDModel):
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

class Technique(UUIDModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

class SynthesisStep(Step):
    precursor_materials = models.ManyToManyField(Material, related_name="s_precursors", blank=True)
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE)
    parameter = models.ManyToManyField(Quantity, related_name="s_parameters")
    target_materials = models.ManyToManyField(Material, related_name="s_targets")
    metadata = models.ManyToManyField(Metadata, related_name="s_metadata")


class Synthesis(UUIDModel):
    synthesis_steps = models.ManyToManyField(SynthesisStep, related_name="steps")

    def save(self, *args, **kwargs):
        # Save the instance to the Django database first
        super().save(*args, **kwargs)

        # After saving, prepare data for Neo4j
        self._save_to_neo4j()

    def _save_to_neo4j(self):
        # Cypher query to merge Synthesis and its Steps, including ordered relationships
        cypher_query = """
            MERGE (s:Manufacturing:Process {uid: $synthesis_id})
    
            // Create or merge related SynthesisSteps
            UNWIND $steps AS step
                MERGE (ss:SynthesisStep {id: step.id})
                MERGE (s)-[:HAS_PART]->(ss)
                SET ss.name = step.step.technique.name

    
                // Associate Precursor Materials
                UNWIND step.precursor_material_ids AS precursor_id
                    MERGE (m:Material {uid: precursor_uid})
                    MERGE (ss)-[:HAS_PRECURSOR]->(m)
    
                // Associate Target Materials
                UNWIND step.target_material_ids AS target_id
                    MERGE (m:Material {id: target_id})
                    MERGE (ss)-[:TARGETS]->(m)
    
                // Associate Parameters
                UNWIND step.parameter_ids AS param_id
                    MERGE (md:Metadata {id: param_id})
                    MERGE (ss)-[:HAS_PARAMETER]->(md)
    
                // Associate Metadata
                UNWIND step.metadata_ids AS meta_id
                    MERGE (md:Metadata {id: meta_id})
                    MERGE (ss)-[:HAS_METADATA]->(md)
    
                // Link Synthesis to SynthesisStep
                MERGE (s)-[:INCLUDES_STEP]->(ss)
    
            // Create ordered relationships between steps
            WITH s, $steps AS steps
            UNWIND range(0, size(steps)-2) AS idx
                MATCH (current:SynthesisStep {id: steps[idx].id})
                MATCH (next:SynthesisStep {id: steps[idx + 1].id})
                MERGE (current)-[:NEXT_STEP]->(next)
            """

        # Prepare parameters
        steps_queryset = self.synthesis_steps.all().order_by('order')
        steps_data = []
        for step in steps_queryset:
            step_data = {
                "id": step.id,
                "order": step.order,
                "technique_id": step.technique.id if step.technique else None,
                "technique": step.technique.name if step.technique else None,
                "precursor_material_ids": list(step.precursor_materials.values_list('id', flat=True)),
                "target_material_ids": list(step.target_materials.values_list('id', flat=True)),
                "parameter_ids": list(step.parameter.values_list('id', flat=True)),
                "metadata_ids": list(step.metadata.values_list('id', flat=True)),
            }
            steps_data.append(step_data)

        parameters = {
            "synthesis_id": self.id,
            "steps": steps_data,
        }



class SamplePreparationStep(Step):
    precursor_materials = models.ManyToManyField(Material, related_name="sp_precursors", blank=True)
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE)
    parameter = models.ManyToManyField(Metadata, related_name="sp_parameters")
    target_materials = models.ManyToManyField(Material, related_name="sp_targets")
    metadata = models.ManyToManyField(Metadata, related_name="sp_metadata")

class SamplePreparation(UUIDModel):
    sample_preparation_steps = models.ManyToManyField(SamplePreparationStep)

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

class Preprocessing(UUIDModel):
    preprocessing_steps = models.ManyToManyField(PreprocessingStep)

class Analysis(UUIDModel):
    analysis_steps = models.ManyToManyField(AnalysisStep)

class Characterization(UUIDModel):
    measurement_method = models.CharField(max_length=100)
    measurement_type = models.CharField(max_length=100)
    specimen = models.CharField(max_length=100)
    temperature = models.FloatField()
    temperature_unit = models.CharField(max_length=10)
    pressure = models.FloatField()
    pressure_unit = models.CharField(max_length=10)
    atmosphere = models.CharField(max_length=100)


class Experiment(UUIDModel):
    experiment_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4, editable=False)
    organizational_data = models.ForeignKey(OrganizationalData, on_delete=models.CASCADE, null=True, blank=True)
    synthesis = models.ForeignKey(Synthesis, on_delete=models.CASCADE, null=True, blank=True)
    sample_preparation = models.ForeignKey(SamplePreparation, on_delete=models.CASCADE, null=True, blank=True)
    preprocessing = models.ForeignKey(Preprocessing, on_delete=models.CASCADE, null=True, blank=True)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, null=True, blank=True)
    characterization = models.ForeignKey(Characterization, on_delete=models.CASCADE, null=True, blank=True)

