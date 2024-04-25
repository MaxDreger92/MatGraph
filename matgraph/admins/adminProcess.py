"""
All admin classes that are required for "matter" models. classes by certain properties and the model admins.
AdminClasses register the models on the admin site and allow reading writing and deleting of their instances via the
admin interface.
Contains:
    ProcessAdmin(NodeModelAdmin)
    MeasurementAdmin(ProcessAdmin)
    ManufacturingAdmin(NodeModelAdmin)
"""
from django.contrib import admin as dj_admin

from matgraph.admins.adminBase import (NodeModelAdmin)

from matgraph.models.processes import Measurement, Manufacturing



class ProcessAdmin(NodeModelAdmin):
    """
    ProcessAdmin is the parent class to MeasurementAdmin and ManufacturingAdmin. It contains _fields, which is defining
    the attributes seen on the admin page. It also contains a  getter and setter function for _fields. save() allows
    """
    list_display = ("uid",)
    _fields = (('run_title', 'run_id'),
               'is_a',
               'parameter',
               ('researcher', 'instrument', 'publication'),
               ('next_step_manufacturing', 'next_step_measurement'),
               ('subprocess_manufacturing', 'subprocess_measurement'),
               ('molecule_input', 'material_input', 'component_input', 'device_input'))

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value):
        self._fields = value

    def save(self, commit=True):
        instance = super().save(commit)
        instance.save()

        return instance

    actions = ['delete_model']


@dj_admin.register(Measurement)
class MeasurementAdmin(ProcessAdmin):
    """
    MeasurementAdmin extends the _fields property by the measurement specific outputs and registers the Measurement
    model at the admin page.
    """

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields += (('file_output', 'property_output'),)
    #
    # form = MeasurementAdminForm
    pass

@dj_admin.register(Manufacturing)
class ManufacturingAdmin(ProcessAdmin):
    """
    ManufacturingAdmin extends the _fields property by the manufacturing specific outputs and registers the
    Measurement model at the admin page.
    """

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields += (('material_output', 'molecule_output'), ('component_output', 'device_output'))
    #
    # form = ManufacturingAdminForm

    pass


# @dj_admin.register(Simulation)
# class SimulationAdmin(ProcessAdmin):
#     """
#     ManufacturingAdmin extends the _fields property by the manufacturing specific outputs and registers the
#     Measurement model at the admin page.
#     """
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields += (('file_output', 'property_output'))
#
#     form = SimulationAdminForm
#
#
# @dj_admin.register(DataProcessing)
# class DataProcessingAdmin(ProcessAdmin):
#     """
#     ManufacturingAdmin extends the _fields property by the manufacturing specific outputs and registers the
#     Measurement model at the admin page.
#     """
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields += (('file_output', 'property_output'))
#
#     form = DataProcessingAdminForm
