import uuid
from typing import Union

from django import forms
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.views.generic import TemplateView
from django.db import models
from neomodel import db

from schema_ingestion.neo4j_handlers import Neo4jFabricationWorkflowHandler


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
    synthesis_steps = models.ManyToManyField(SynthesisStep, related_name="steps")
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
    sample_preparation_steps = models.ManyToManyField(SamplePreparationStep)

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

class Preprocessing(UUIDModel):
    preprocessing_steps = models.ManyToManyField(PreprocessingStep)

    def save(self, *args, **kwargs):
        # Save the instance to the Django database first
        super().save(*args, **kwargs)

        # After saving, prepare data for Neo4j
        self._save_to_neo4j()

    def _save_to_neo4j(self):
        cypher_query = """
        MERGE (pp:Preprocessing {uid: $pp_uid})
        
        // Create or merge related PreprocessingSteps
        UNWIND $steps AS step
            MERGE (pps:PreprocessingStep {uid: step.uid})
            SET pps.order = step.order
            SET pps.technique = step.technique
            
            // Associate Data Inputs
            UNWIND step.data_inputs AS data_in
                MERGE (d_in:Data {uid: data_in.uid})
                SET d_in.data_type = data_in.data_type
                SET d_in.data_format = data_in.data_format
                SET d_in.link = data_in.link
                MERGE (pps)-[:USES_DATA_INPUT]->(d_in)
            
            // Associate Quantity Inputs
            UNWIND step.quantity_inputs AS qty_in
                MERGE (q_in:Quantity {uid: qty_in.uid})
                SET q_in.name = qty_in.name
                SET q_in.value = qty_in.value
                SET q_in.unit = qty_in.unit
                SET q_in.error = qty_in.error
                MERGE (pps)-[:USES_QUANTITY_INPUT]->(q_in)
            
            // Associate Parameters
            UNWIND step.parameters AS param
                MERGE (meta:Quantity {uid: param.uid})  // Assuming parameters are Quantity
                SET meta.name = param.name
                SET meta.value = param.value
                SET meta.unit = param.unit
                SET meta.error = param.error
                MERGE (pps)-[:HAS_PARAMETER]->(meta)
            
            // Associate Data Results
            UNWIND step.data_results AS data_res
                MERGE (d_res:Data {uid: data_res.uid})
                SET d_res.data_type = data_res.data_type
                SET d_res.data_format = data_res.data_format
                SET d_res.link = data_res.link
                MERGE (pps)-[:GENERATES_DATA]->(d_res)
            
            // Associate Quantity Results
            UNWIND step.quantity_results AS qty_res
                MERGE (q_res:Quantity {uid: qty_res.uid})
                SET q_res.name = qty_res.name
                SET q_res.value = qty_res.value
                SET q_res.unit = qty_res.unit
                SET q_res.error = qty_res.error
                MERGE (pps)-[:GENERATES_QUANTITY]->(q_res)
            
            // Associate Metadata
            UNWIND step.metadatas AS meta
                MERGE (md:Metadata {uid: meta.uid})
                SET md.key = meta.key
                SET md.value = meta.value
                MERGE (pps)-[:HAS_METADATA]->(md)
        
            // Link Preprocessing to PreprocessingStep
            MERGE (pp)-[:HAS_STEP]->(pps)
        
        // Create ordered relationships between steps
        WITH pp, $steps AS steps
        UNWIND range(0, size(steps)-2) AS idx
            MATCH (current:PreprocessingStep {uid: steps[idx].uid})
            MATCH (next:PreprocessingStep {uid: steps[idx + 1].uid})
            MERGE (current)-[:FOLLOWED_BY]->(next)
        """
        # Prepare parameters
        steps_queryset = self.preprocessing_steps.all().order_by('order')
        steps_data = []
        for step in steps_queryset:
            step_data = {
                "uid": str(step.uid),
                "order": step.order,
                "technique": step.technique,
                "data_inputs": [
                    {
                        "uid": str(data.uid),
                        "data_type": data.data_type,
                        "data_format": data.data_format,
                        "link": data.link
                    }
                    for data in step.data_inputs.all()
                ],
                "quantity_inputs": [
                    {
                        "uid": str(qty.uid),
                        "name": qty.name,
                        "value": qty.value,
                        "unit": qty.unit,
                        "error": qty.error
                    }
                    for qty in step.quantity_inputs.all()
                ],
                "parameters": [
                    {
                        "uid": str(param.uid),
                        "name": param.name,
                        "value": param.value,
                        "unit": param.unit,
                        "error": param.error
                    }
                    for param in step.parameter.all()
                ],
                "data_results": [
                    {
                        "uid": str(data.uid),
                        "data_type": data.data_type,
                        "data_format": data.data_format,
                        "link": data.link
                    }
                    for data in step.data_results.all()
                ],
                "quantity_results": [
                    {
                        "uid": str(qty.uid),
                        "name": qty.name,
                        "value": qty.value,
                        "unit": qty.unit,
                        "error": qty.error
                    }
                    for qty in step.quantity_results.all()
                ],
                "metadatas": [
                    {
                        "uid": str(meta.uid),
                        "key": meta.key,
                        "value": meta.value
                    }
                    for meta in step.metadata.all()
                ],
            }
            steps_data.append(step_data)
        parameters = {
            "pp_uid": str(self.uid),
            "steps": steps_data,
        }
        db.cypher_query(cypher_query, params=parameters)

class Analysis(UUIDModel):
    analysis_steps = models.ManyToManyField(AnalysisStep, related_name="a_steps")

    def save(self, *args, **kwargs):
        # Save the instance to the Django database first
        super().save(*args, **kwargs)

        # After saving, prepare data for Neo4j
        self._save_to_neo4j()

    def _save_to_neo4j(self):
        cypher_query = """
        MERGE (a:Analysis {uid: $analysis_uid})
        
        // Create or merge related AnalysisSteps
        UNWIND $steps AS step
            MERGE (as:AnalysisStep {uid: step.uid})
            SET as.order = step.order
            SET as.technique = step.technique
            
            // Associate Data Inputs
            UNWIND step.data_inputs AS data_in
                MERGE (d_in:Data {uid: data_in.uid})
                SET d_in.data_type = data_in.data_type
                SET d_in.data_format = data_in.data_format
                SET d_in.link = data_in.link
                MERGE (as)-[:USES_DATA_INPUT]->(d_in)
            
            // Associate Quantity Inputs
            UNWIND step.quantity_inputs AS qty_in
                MERGE (q_in:Quantity {uid: qty_in.uid})
                SET q_in.name = qty_in.name
                SET q_in.value = qty_in.value
                SET q_in.unit = qty_in.unit
                SET q_in.error = qty_in.error
                MERGE (as)-[:USES_QUANTITY_INPUT]->(q_in)
            
            // Associate Parameters
            UNWIND step.parameters AS param
                MERGE (q:Quantity {uid: param.uid})
                SET q.name = param.name
                SET q.value = param.value
                SET q.unit = param.unit
                SET q.error = param.error
                MERGE (as)-[:HAS_PARAMETER]->(q)
            
            // Associate Data Results
            UNWIND step.data_results AS data_res
                MERGE (d_res:Data {uid: data_res.uid})
                SET d_res.data_type = data_res.data_type
                SET d_res.data_format = data_res.data_format
                SET d_res.link = data_res.link
                MERGE (as)-[:GENERATES_DATA]->(d_res)
            
            // Associate Quantity Results
            UNWIND step.quantity_results AS qty_res
                MERGE (q_res:Quantity {uid: qty_res.uid})
                SET q_res.name = qty_res.name
                SET q_res.value = qty_res.value
                SET q_res.unit = qty_res.unit
                SET q_res.error = qty_res.error
                MERGE (as)-[:GENERATES_QUANTITY]->(q_res)
            
            // Associate Metadata
            UNWIND step.metadatas AS meta
                MERGE (md:Metadata {uid: meta.uid})
                SET md.key = meta.key
                SET md.value = meta.value
                MERGE (as)-[:HAS_METADATA]->(md)
        
            // Link Analysis to AnalysisStep
            MERGE (a)-[:HAS_STEP]->(as)
        
        // Create ordered relationships between steps
        WITH a, $steps AS steps
        UNWIND range(0, size(steps)-2) AS idx
            MATCH (current:AnalysisStep {uid: steps[idx].uid})
            MATCH (next:AnalysisStep {uid: steps[idx + 1].uid})
            MERGE (current)-[:FOLLOWED_BY]->(next)
        """
        # Prepare parameters
        steps_queryset = self.analysis_steps.all().order_by('order')
        steps_data = []
        for step in steps_queryset:
            step_data = {
                "uid": str(step.uid),
                "order": step.order,
                "technique": step.technique,
                "data_inputs": [
                    {
                        "uid": str(data.uid),
                        "data_type": data.data_type,
                        "data_format": data.data_format,
                        "link": data.link
                    }
                    for data in step.data_inputs.all()
                ],
                "quantity_inputs": [
                    {
                        "uid": str(qty.uid),
                        "name": qty.name,
                        "value": qty.value,
                        "unit": qty.unit,
                        "error": qty.error
                    }
                    for qty in step.quantity_inputs.all()
                ],
                "parameters": [
                    {
                        "uid": str(param.uid),
                        "name": param.name,
                        "value": param.value,
                        "unit": param.unit,
                        "error": param.error
                    }
                    for param in step.parameter.all()
                ],
                "data_results": [
                    {
                        "uid": str(data.uid),
                        "data_type": data.data_type,
                        "data_format": data.data_format,
                        "link": data.link
                    }
                    for data in step.data_results.all()
                ],
                "quantity_results": [
                    {
                        "uid": str(qty.uid),
                        "name": qty.name,
                        "value": qty.value,
                        "unit": qty.unit,
                        "error": qty.error
                    }
                    for qty in step.quantity_results.all()
                ],
                "metadatas": [
                    {
                        "uid": str(meta.uid),
                        "key": meta.key,
                        "value": meta.value
                    }
                    for meta in step.metadata.all()
                ],
            }
            steps_data.append(step_data)
        parameters = {
            "analysis_uid": str(self.uid),
            "steps": steps_data,
        }
        db.cypher_query(cypher_query, params=parameters)

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
    synthesis = models.ForeignKey(Synthesis, on_delete=models.CASCADE, null=True, blank=True, related_name='experiments_synthesis')
    sample_preparation = models.ForeignKey(SamplePreparation, on_delete=models.CASCADE, null=True, blank=True)
    preprocessing = models.ForeignKey(Preprocessing, on_delete=models.CASCADE, null=True, blank=True)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, null=True, blank=True)
    characterization = models.ForeignKey(Characterization, on_delete=models.CASCADE, null=True, blank=True)

