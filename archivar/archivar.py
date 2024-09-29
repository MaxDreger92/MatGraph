from django.db import transaction
from archivar.models import Experiment, Campaign
from matgraph.models.matter import Material
from matgraph.models.ontology import EMMOProcess, EMMOQuantity, EMMOMatter
from matgraph.models.processes import Measurement, Manufacturing
from matgraph.models.properties import Parameter, Property

class ExperimentImporter:
    @transaction.atomic
    def import_experiment(self, json_data):
        # Create or get Campaign
        campaign = Campaign.get_or_create({"uid": json_data['campaign_uuid'],
                                           "name": json_data['campaign_name']})[0]

        # Create Experiment
        exp = Experiment(
            name=json_data["name"],
            uid=json_data['exp_uuid'],
            created_at=json_data['end_time'],
        )
        exp.save()
        campaign.experiment.connect(exp)

        modules = {}
        samples = {}

        # Process samples
        for key, value in json_data['samples'].items():
            matter = Material(name=value['name'])
            matter.save()
            labels = EMMOMatter.nodes.get_by_string(string=value['name'], limit=10)
            if labels:
                label = labels[0]
                matter.is_a.connect(label)
            else:
                # Handle missing label
                pass
            samples[key] = matter

        # Process modules
        for module_data in json_data['workflow_status']['modules']:
            module_name = module_data['name']
            if "measurement" in module_name.lower():
                process = Measurement(name=module_name)
                process.save()
                exp.measurement.connect(process)
            else:
                process = Manufacturing(name=module_name)
                process.save()
                exp.manufacturing.connect(process)
            labels = EMMOProcess.nodes.get_by_string(string=module_name, limit=10)
            if labels:
                label = labels[0]
                process.is_a.connect(label)
            else:
                # Handle missing label
                pass
            modules[module_name] = process
            # Connect input samples
            for input_sample in module_data['samples']['input']:
                material = samples.get(str(input_sample))
                if material:
                    process.material_input.connect(material)
            # Connect output samples
            for output_sample in module_data['samples']['output']:
                material = samples.get(str(output_sample))
                if material:
                    process.material_output.connect(material)

        # Process inputs
        for input_data in json_data['details']['inputs']:
            module_name = input_data['data']['module_name']
            if module_name not in modules:
                continue
            process = modules[module_name]
            data = input_data['data']
            name = input_data['name']
            value = data['value_request']
            units = data['units']
            labels = EMMOQuantity.nodes.get_by_string(string=name, limit=10)
            label = labels[0] if labels else None
            if isinstance(process, Measurement):
                quantity = Property(name=name, value=value, unit=units)
            elif isinstance(process, Manufacturing):
                quantity = Parameter(name=name, value=value, unit=units)
            else:
                continue
            quantity.save()
            if label:
                quantity.is_a.connect(label)
            process.parameter.connect(quantity)

        # Process scalar outputs
        for output_data in json_data['details']['scalaroutputs']:
            data = output_data['data']
            module_name = data['module_name']
            if module_name not in modules:
                continue
            process = modules[module_name]
            name = output_data['name']
            value = data['value']
            units = data['units']
            sample_index = str(data.get('sample_index'))
            labels = EMMOQuantity.nodes.get_by_string(string=name, limit=10)
            label = labels[0] if labels else None
            if isinstance(process, Measurement):
                quantity = Property(name=name, value=value, unit=units)
                quantity.save()
                if label:
                    quantity.is_a.connect(label)
                if sample_index in samples:
                    samples[sample_index].properties.connect(quantity)
            elif isinstance(process, Manufacturing):
                quantity = Parameter(name=name, value=value, unit=units)
                quantity.save()
                if label:
                    quantity.is_a.connect(label)
                process.parameter.connect(quantity)

        return exp