from django.contrib import admin
from .models import (
    OrganizationalData,
    Quantity,
    Material,
    Metadata,
    Technique,
    SynthesisStep,
    Synthesis,
    SamplePreparationStep,
    SamplePreparation,
    Data,
    AnalysisStep,
    PreprocessingStep,
    Preprocessing,
    Analysis,
    Characterization,
    Experiment,
)


class OrganizationalDataAdmin(admin.ModelAdmin):
    list_display = (
        'experiment_title', 'experiment_id', 'measurement_id', 'upload_date', 'institution', 'published'
    )
    search_fields = ('experiment_title', 'experiment_id', 'institution', 'publication', 'doi', 'journal')
    list_filter = ('institution', 'published', 'country', 'format')


class QuantityAdmin(admin.ModelAdmin):
    list_display = ('value', 'error', 'unit')
    search_fields = ('unit',)


class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'unit', 'lot_number')
    search_fields = ('name', 'lot_number')


class MetadataAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ('key', 'value')


class TechniqueAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')


class SynthesisStepAdmin(admin.ModelAdmin):
    list_display = ('uid', 'technique')
    filter_horizontal = ('precursor_materials', 'parameter', 'target_materials', 'metadata')
    search_fields = ('technique__name',)


class SynthesisAdmin(admin.ModelAdmin):
    list_display = ('uid',)
    filter_horizontal = ('synthesis_steps',)
    # Add search_fields to enable autocomplete in ExperimentAdmin
    search_fields = ('uid',)


class SamplePreparationStepAdmin(admin.ModelAdmin):
    list_display = ('uid', 'technique')
    filter_horizontal = ('precursor_materials', 'parameter', 'target_materials', 'metadata')
    search_fields = ('technique__name',)


class SamplePreparationAdmin(admin.ModelAdmin):
    list_display = ('uid',)
    filter_horizontal = ('sample_preparation_steps',)
    # Add search_fields to enable autocomplete in ExperimentAdmin
    search_fields = ('uid',)


class DataAdmin(admin.ModelAdmin):
    list_display = ('data_type', 'data_format', 'data', 'link')
    search_fields = ('data_type', 'data_format')


class AnalysisStepAdmin(admin.ModelAdmin):
    list_display = ('uid', 'technique')
    filter_horizontal = ('data_inputs', 'quantity_inputs', 'metadata', 'parameter', 'data_results', 'quantity_results')
    search_fields = ('technique',)


class PreprocessingStepAdmin(admin.ModelAdmin):
    list_display = ('uid', 'technique')
    filter_horizontal = ('data_inputs', 'quantity_inputs', 'metadata', 'parameter', 'data_results', 'quantity_results')
    search_fields = ('technique',)


class PreprocessingAdmin(admin.ModelAdmin):
    list_display = ('uid',)
    filter_horizontal = ('preprocessing_steps',)
    # Add search_fields to enable autocomplete in ExperimentAdmin
    search_fields = ('uid',)


class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('uid',)
    filter_horizontal = ('analysis_steps',)
    # Even if not strictly required by ExperimentAdmin, having search_fields is good practice
    search_fields = ('uid',)


class CharacterizationAdmin(admin.ModelAdmin):
    list_display = ('measurement_method', 'measurement_type', 'specimen', 'temperature', 'pressure', 'atmosphere')
    search_fields = ('measurement_method', 'measurement_type', 'specimen', 'atmosphere')
    list_filter = ('measurement_method', 'measurement_type', 'atmosphere')


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('experiment_id', 'organizational_data', 'synthesis', 'sample_preparation', 'preprocessing', 'analysis', 'characterization')
    search_fields = ('experiment_id',)
    autocomplete_fields = [
        'organizational_data',
        'synthesis',
        'sample_preparation',
        'preprocessing',
        'analysis',
        'characterization'
    ]


admin.site.register(OrganizationalData, OrganizationalDataAdmin)
admin.site.register(Quantity, QuantityAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Metadata, MetadataAdmin)
admin.site.register(Technique, TechniqueAdmin)
admin.site.register(SynthesisStep, SynthesisStepAdmin)
admin.site.register(Synthesis, SynthesisAdmin)
admin.site.register(SamplePreparationStep, SamplePreparationStepAdmin)
admin.site.register(SamplePreparation, SamplePreparationAdmin)
admin.site.register(Data, DataAdmin)
admin.site.register(AnalysisStep, AnalysisStepAdmin)
admin.site.register(PreprocessingStep, PreprocessingStepAdmin)
admin.site.register(Preprocessing, PreprocessingAdmin)
admin.site.register(Analysis, AnalysisAdmin)
admin.site.register(Characterization, CharacterizationAdmin)
admin.site.register(Experiment, ExperimentAdmin)
