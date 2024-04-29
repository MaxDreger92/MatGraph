from graphutils.forms import RelationMultipleChoiceField, NeoModelForm

"""
Forms classes for all adminMatters. 
Contains:
    MatterAdminForm
    MoleculeAdminForm
    MaterialAdminForm
    ComponentAdminForm
    DeviceAdminForm
"""


class MatterAdminForm(NeoModelForm):
    """
    Parent class for all MatterAdminForms. Contains ontology and elements relation as well as clean function.
    """
    is_a = RelationMultipleChoiceField("EMMOMatter", "EMMO Matter", primary_key='uri', label_field='name')
    elements = RelationMultipleChoiceField("Element", "Elements", primary_key='uid', label_field='name')


def clean():
    cleaned_data = super().clean()
    return cleaned_data


class MoleculeAdminForm(MatterAdminForm):
    pass


class MaterialAdminForm(MatterAdminForm):
    molecules = RelationMultipleChoiceField("Molecule", "Molecules", primary_key='uid', label_field='name')


class ComponentAdminForm(MatterAdminForm):
    molecules = RelationMultipleChoiceField("Molecule", "Molecules", primary_key='uid', label_field='name')
    materials = RelationMultipleChoiceField("Material", "Materials", primary_key='uid', label_field='name')


class DeviceAdminForm(MatterAdminForm):
    molecules = RelationMultipleChoiceField("Molecule", "Molecules", primary_key='uid', label_field='name')
    materials = RelationMultipleChoiceField("Material", "Materials", primary_key='uid', label_field='name')
    components = RelationMultipleChoiceField("Component", "Components", primary_key='uid', label_field='name')
    devices = RelationMultipleChoiceField("Device", "Devices", primary_key='uid', label_field='name')
