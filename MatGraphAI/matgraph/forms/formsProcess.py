from graphutils.forms import NeoModelForm, RelationMultipleChoiceField, DateInput


class ProcessAdminForm(NeoModelForm):
    subprocess_manufacturing = RelationMultipleChoiceField("Measurement", "Measurements", primary_key='uid', label_field='name')
    next_step_manufacturing = RelationMultipleChoiceField("Measurement", "Measurements", primary_key='uid', label_field='name')
    subprocess_measurement = RelationMultipleChoiceField("Manufacturing", "Measurements", primary_key='uid', label_field='name')
    next_step_measurement = RelationMultipleChoiceField("Measurement", "Measurements", primary_key='uid', label_field='name')
    researcher = RelationMultipleChoiceField("Researcher", "Researchers", primary_key='uid', label_field='name')
    parameter = RelationMultipleChoiceField("Parameter", "Parameters", primary_key='uid', label_field='name')
    # institution = RelationMultipleChoiceField("Institution", "Institutions", primary_key = 'uid',label_field='name')
    publication = RelationMultipleChoiceField("Publication", "Publications", primary_key='uid', label_field='name')
    instrument = RelationMultipleChoiceField("Instrument", "Instrument", primary_key='uid', label_field='name')

    is_a = RelationMultipleChoiceField("EMMOProcess", "EMMO Processes", primary_key='uid', label_field='name')
    material_input = RelationMultipleChoiceField("Material", "Materials", primary_key="uid", label_field='name')
    molecule_input = RelationMultipleChoiceField("Molecule", "Molecules", primary_key="uid", label_field='name')
    component_input = RelationMultipleChoiceField("Component", "Components", primary_key="uid", label_field='name')
    device_input = RelationMultipleChoiceField("Device", "Devices", primary_key="uid", label_field='name')
    date_added = DateInput()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class ManufacturingAdminForm(ProcessAdminForm):
    material_output = RelationMultipleChoiceField("Material", "Materials", primary_key="uid", label_field='name')
    molecule_output = RelationMultipleChoiceField("Molecule", "Molecules", primary_key="uid", label_field='name')
    component_output = RelationMultipleChoiceField("Component", "Component", primary_key="uid", label_field='name')
    device_output = RelationMultipleChoiceField("Device", "Device", primary_key="uid", label_field='name')


class MeasurementAdminForm(ProcessAdminForm):
    property_output = RelationMultipleChoiceField("Property", "Properties", primary_key="uid", label_field='uid + ""')
    file_output = RelationMultipleChoiceField("File", "Files", primary_key="uid", label_field='link')
