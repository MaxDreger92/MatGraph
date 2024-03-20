import csv
import json
from io import StringIO

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from neomodel import DateTimeProperty
from rest_framework import response, status
from rest_framework.views import APIView

from importing.NodeAttributeExtraction.attributeClassifier import AttributeClassifier
from importing.NodeExtraction.nodeExtractor import NodeExtractor
from importing.NodeLabelClassification.labelClassifier import NodeClassifier
from importing.RelationshipExtraction.completeRelExtractor import fullRelationshipsExtractor
from importing.importer import TableImporter
from importing.models import FullTableCache
from matgraph.models.metadata import File


@method_decorator(csrf_exempt, name='dispatch')
class LabelExtractView(APIView):

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        print("labels")
        if 'file' not in request.FILES:
            return response.Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.FILES['file']
        file = StringIO(file_obj.read().decode('utf-8'))

        context = request.POST['context']  # Assuming context is JSON string in POST data
        # Basic validation (can be more specific based on requirements)
        if not file_obj.name.endswith('.csv'):
            return response.Response({'error': 'Invalid file type'}, status=status.HTTP_400_BAD_REQUEST)

        file_obj.seek(0)
        first_line = str(file_obj.readline().decode('utf-8')).strip().lower()
        file_record = self.store_file(file_obj)
        if cached := FullTableCache.fetch(first_line):
            cached = str(cached).replace("'", "\"")
            return response.Response({'graph_json': cached,
                                      'file_link': file_record.link,
                                      'file_name': file_record.name
                                      })

        labels = self.extract_labels(file, context, file_record.link, file_record.name)

        return response.Response({
            'label_dict': labels,
            'file_link': file_record.link,
            'file_name': file_record.name
        })





    def extract_labels(self, file_obj, context, file_link, file_name):
        """Extract labels from the uploaded file."""
        node_classifier = NodeClassifier(data = file_obj,
                                         context = context,
                                         file_link = file_link,
                                         file_name = file_name)
        node_classifier.run()
        node_classifier.results
        node_labels = {element['header']: [element['1_label']] for element in node_classifier.results}
        return node_labels
    def store_file(self, file_obj):
        """Store the uploaded file and return the file record."""
        file_name = file_obj.name
        file_record = File(name=file_name, date_added=DateTimeProperty(default_now=True))
        file_record.file = file_obj
        file_record.save()
        return file_record


@method_decorator(csrf_exempt, name='dispatch')
class AttributeExtractView(APIView):

    ATTRIBUTE_MAPPER = {
        "Matter": ["name", "ratio", "concentration", "batch number", "identifier"],
        "Parameter": [ "value", "unit", "average", "std", "error"],
        "Measurement": ["name", "identifier"],
        "Manufacturing": ["name", "identifier"],
        "Metadata": ["name", "identifier"]
    }

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        print("AttributeExtractView")
        data = json.loads(request.body)
        labels = data['params']['label_dict']
        context = data['params']['context']
        file_name = data['params']['file_name']
        file_link = data['params']['file_link']

        if not labels or not context:
            return response.Response({'error': 'Missing labels or context'}, status=status.HTTP_400_BAD_REQUEST)
        label_input = self.prepare_data(labels)
        attributes = self.extract_attributes(label_input, file_link, file_name, context)
        return response.Response({"attribute_dict": attributes,
                                    "file_link": file_link,
                                    "file_name": file_name
        })

    def prepare_data(self, labels):
        print("prepare_data")
        input_data = [{'column_values': ['test'], 'header': key, '1_label': value['Label']} for key, value in labels.items()]
        for index, key in enumerate(input_data):
            key['index'] = index
        print(input_data)
        return input_data

    def extract_attributes(self, labels, file_link, file_name, context):
        attribute_classifier = AttributeClassifier(
            labels,
            context=context,
            file_link=file_link,
            file_name=file_name
        )
        attribute_classifier.run()
        _predicted_attributes = attribute_classifier.results
        attributes = {element['header']: {"Label": element["1_label"],
                                         "Attribute": element['1_attribute']} for element in _predicted_attributes}
        return attributes


@method_decorator(csrf_exempt, name='dispatch')
class NodeExtractView(APIView):

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        # Parsing JSON data from request body
        data = json.loads(request.body)
        print(data)


        # Validate the presence of required fields
        required_fields = ['attribute_dict', 'context', 'file_link', 'file_name']
        if not all(field in data['params'] for field in required_fields):
            return response.Response({'error': 'Missing required data'}, status=status.HTTP_400_BAD_REQUEST)

        context = data['params']['context']
        attributes = data['params']['attribute_dict']
        file_link = data['params']['file_link']
        file_name = data['params']['file_name']
        input_data = self.prepare_data(file_link, attributes)

        nodes = self.extract_nodes(file_link, file_name, input_data, context)
        # nodes  = {"nodes": [{"attributes": {"name": [{"value": "Spincoating", "index": 2}]}, "name": [["Spincoating", 2]], "label": "manufacturing", "id": "2"}, {"attributes": {"name": [{"value": "Spincoating", "index": 16}]}, "name": [["Spincoating", 16]], "label": "manufacturing", "id": "16"}, {"attributes": {"name": [{"value": "Spincoating", "index": 30}]}, "name": [["Spincoating", 30]], "label": "manufacturing", "id": "30"}, {"attributes": {"name": [{"value": "Spincoating", "index": 44}]}, "name": [["Spincoating", 44]], "label": "manufacturing", "id": "44"}, {"attributes": {"name": [{"value": "Spincoating", "index": 58}]}, "name": [["Spincoating", 58]], "label": "manufacturing", "id": "58"}, {"attributes": {"name": [{"value": "Evaporation", "index": 72}]}, "name": [["Evaporation", 72]], "label": "manufacturing", "id": "72"}, {"attributes": {"name": [{"value": "Evaporation", "index": 86}]}, "name": [["Evaporation", 86]], "label": "manufacturing", "id": "86"}, {"attributes": {"name": [{"value": "Solar Cell", "index": "inferred"}], "identifier": {"value": "13841", "index": 0}}, "name": [["Solar Cell", "inferred"]], "label": "matter", "id": "inferred_matter_0"}, {"attributes": {"name": [{"value": "ETL", "index": 1}, {"value": "ZnO", "index": 11}], "ratio": {"value": "1", "index": 8}}, "name": [["ETL", 1], ["ZnO", 11]], "label": "matter", "id": "1"}, {"attributes": {"name": [{"value": "ActiveLayer", "index": 15}, {"value": "Donor", "index": 23}, {"value": "PM6", "index": 25}], "concentration": {"value": "19.8846153846154", "index": 18}, "ratio": {"value": "0.8112", "index": 22}}, "name": [["ActiveLayer", 15], ["Donor", 23], ["PM6", 25]], "label": "matter", "id": "15"}, {"attributes": {"name": [{"value": "ActiveLayer", "index": 29}, {"value": "Acceptor", "index": 37}, {"value": "Y12", "index": 39}], "concentration": {"value": "19.4615384615385", "index": 32}, "ratio": {"value": "0.2128", "index": 36}}, "name": [["ActiveLayer", 29], ["Acceptor", 37], ["Y12", 39]], "label": "matter", "id": "29"}, {"attributes": {"name": [{"value": "ActiveLayer", "index": 43}, {"value": "Acceptor", "index": 51}, {"value": "PCBM70", "index": 53}], "concentration": {"value": "27.5000000000001", "index": 46}, "ratio": {"value": "0.0234", "index": 50}}, "name": [["ActiveLayer", 43], ["Acceptor", 51], ["PCBM70", 53]], "label": "matter", "id": "43"}, {"attributes": {"name": [{"value": "ActiveLayer", "index": 57}, {"value": "Solvent", "index": 65}, {"value": "o-Xylene", "index": 67}], "concentration": {"value": "27.5000000000001", "index": 60}, "ratio": {"value": "1", "index": 64}}, "name": [["ActiveLayer", 57], ["Solvent", 65], ["o-Xylene", 67]], "label": "matter", "id": "57"}, {"attributes": {"name": [{"value": "HTL", "index": 71}, {"value": "MoOx", "index": 81}]}, "name": [["HTL", 71], ["MoOx", 81]], "label": "matter", "id": "71"}, {"attributes": {"name": [{"value": "Electrode", "index": 85}, {"value": "Ag", "index": 95}]}, "name": [["Electrode", 85], ["Ag", 95]], "label": "matter", "id": "85"}, {"attributes": {"name": [{"value": "layer_material_temperature", "index": "inferred"}], "value": {"value": "25", "index": 5}, "unit": {"value": "C", "index": "inferred"}}, "name": [["layer_material_temperature", "inferred"]], "label": "parameter", "id": "inferred_parameter_0"}, {"attributes": {"name": [{"value": "layer_material_stirring_time", "index": "inferred"}], "value": {"value": "00:46:01", "index": 6}, "unit": {"value": "s", "index": "inferred"}}, "name": [["layer_material_stirring_time", "inferred"]], "label": "parameter", "id": "inferred_parameter_1"}, {"attributes": {"name": [{"value": "layer_material_stirring_speed", "index": "inferred"}], "value": {"value": "100", "index": 7}, "unit": {"value": "rpm", "index": "inferred"}}, "name": [["layer_material_stirring_speed", "inferred"]], "label": "parameter", "id": "inferred_parameter_2"}, {"attributes": {"name": [{"value": "material_batch_barcode", "index": "inferred"}], "value": {"value": "121800", "index": 10}}, "name": [["material_batch_barcode", "inferred"]], "label": "parameter", "id": "inferred_parameter_3"}, {"attributes": {"name": [{"value": "annealing_time", "index": "inferred"}], "value": {"value": "00:46:01", "index": 12}, "unit": {"value": "s", "index": "inferred"}}, "name": [["annealing_time", "inferred"]], "label": "parameter", "id": "inferred_parameter_4"}, {"attributes": {"name": [{"value": "annealing_temperature", "index": "inferred"}], "value": {"value": "180", "index": 13}, "unit": {"value": "C", "index": "inferred"}}, "name": [["annealing_temperature", "inferred"]], "label": "parameter", "id": "inferred_parameter_5"}, {"attributes": {"name": [{"value": "layer_material_temperature", "index": "inferred"}], "value": {"value": "24", "index": 19}, "unit": {"value": "C", "index": "inferred"}}, "name": [["layer_material_temperature", "inferred"]], "label": "parameter", "id": "inferred_parameter_6"}, {"attributes": {"name": [{"value": "layer_material_stirring_time", "index": "inferred"}], "value": {"value": "00:10:15", "index": 20}, "unit": {"value": "s", "index": "inferred"}}, "name": [["layer_material_stirring_time", "inferred"]], "label": "parameter", "id": "inferred_parameter_7"}, {"attributes": {"name": [{"value": "layer_material_stirring_speed", "index": "inferred"}], "value": {"value": "240", "index": 21}, "unit": {"value": "rpm", "index": "inferred"}}, "name": [["layer_material_stirring_speed", "inferred"]], "label": "parameter", "id": "inferred_parameter_8"}, {"attributes": {"name": [{"value": "material_batch_barcode", "index": "inferred"}], "value": {"value": "321100", "index": 24}}, "name": [["material_batch_barcode", "inferred"]], "label": "parameter", "id": "inferred_parameter_9"}, {"attributes": {"name": [{"value": "annealing_time", "index": "inferred"}], "value": {"value": "00:10:15", "index": 26}, "unit": {"value": "s", "index": "inferred"}}, "name": [["annealing_time", "inferred"]], "label": "parameter", "id": "inferred_parameter_10"}, {"attributes": {"name": [{"value": "annealing_temperature", "index": "inferred"}], "value": {"value": "160", "index": 27}, "unit": {"value": "C", "index": "inferred"}}, "name": [["annealing_temperature", "inferred"]], "label": "parameter", "id": "inferred_parameter_11"}, {"attributes": {"name": [{"value": "layer_material_temperature", "index": "inferred"}], "value": {"value": "20", "index": 33}, "unit": {"value": "C", "index": "inferred"}}, "name": [["layer_material_temperature", "inferred"]], "label": "parameter", "id": "inferred_parameter_12"}, {"attributes": {"name": [{"value": "layer_material_stirring_time", "index": "inferred"}], "value": {"value": "00:10:15", "index": 34}, "unit": {"value": "s", "index": "inferred"}}, "name": [["layer_material_stirring_time", "inferred"]], "label": "parameter", "id": "inferred_parameter_13"}, {"attributes": {"name": [{"value": "layer_material_stirring_speed", "index": "inferred"}], "value": {"value": "160", "index": 35}, "unit": {"value": "rpm", "index": "inferred"}}, "name": [["layer_material_stirring_speed", "inferred"]], "label": "parameter", "id": "inferred_parameter_14"}, {"attributes": {"name": [{"value": "material_batch_barcode", "index": "inferred"}], "value": {"value": "321116", "index": 38}}, "name": [["material_batch_barcode", "inferred"]], "label": "parameter", "id": "inferred_parameter_15"}, {"attributes": {"name": [{"value": "annealing_time", "index": "inferred"}], "value": {"value": "00:10:15", "index": 40}, "unit": {"value": "s", "index": "inferred"}}, "name": [["annealing_time", "inferred"]], "label": "parameter", "id": "inferred_parameter_16"}, {"attributes": {"name": [{"value": "annealing_temperature", "index": "inferred"}], "value": {"value": "250", "index": 41}, "unit": {"value": "C", "index": "inferred"}}, "name": [["annealing_temperature", "inferred"]], "label": "parameter", "id": "inferred_parameter_17"}, {"attributes": {"name": [{"value": "layer_material_temperature", "index": "inferred"}], "value": {"value": "22", "index": 47}, "unit": {"value": "C", "index": "inferred"}}, "name": [["layer_material_temperature", "inferred"]], "label": "parameter", "id": "inferred_parameter_18"}, {"attributes": {"name": [{"value": "layer_material_stirring_time", "index": "inferred"}], "value": {"value": "00:10:15", "index": 48}, "unit": {"value": "s", "index": "inferred"}}, "name": [["layer_material_stirring_time", "inferred"]], "label": "parameter", "id": "inferred_parameter_19"}, {"attributes": {"name": [{"value": "layer_material_stirring_speed", "index": "inferred"}], "value": {"value": "240", "index": 49}, "unit": {"value": "rpm", "index": "inferred"}}, "name": [["layer_material_stirring_speed", "inferred"]], "label": "parameter", "id": "inferred_parameter_20"}, {"attributes": {"name": [{"value": "material_batch_barcode", "index": "inferred"}], "value": {"value": "321046", "index": 52}}, "name": [["material_batch_barcode", "inferred"]], "label": "parameter", "id": "inferred_parameter_21"}, {"attributes": {"name": [{"value": "annealing_time", "index": "inferred"}], "value": {"value": "00:10:15", "index": 54}, "unit": {"value": "s", "index": "inferred"}}, "name": [["annealing_time", "inferred"]], "label": "parameter", "id": "inferred_parameter_22"}, {"attributes": {"name": [{"value": "annealing_temperature", "index": "inferred"}], "value": {"value": "288", "index": 55}, "unit": {"value": "C", "index": "inferred"}}, "name": [["annealing_temperature", "inferred"]], "label": "parameter", "id": "inferred_parameter_23"}, {"attributes": {"name": [{"value": "layer_material_temperature", "index": "inferred"}], "value": {"value": "5", "index": 61}, "unit": {"value": "C", "index": "inferred"}}, "name": [["layer_material_temperature", "inferred"]], "label": "parameter", "id": "inferred_parameter_24"}, {"attributes": {"name": [{"value": "layer_material_stirring_time", "index": "inferred"}], "value": {"value": "00:10:15", "index": 62}, "unit": {"value": "s", "index": "inferred"}}, "name": [["layer_material_stirring_time", "inferred"]], "label": "parameter", "id": "inferred_parameter_25"}, {"attributes": {"name": [{"value": "layer_material_stirring_speed", "index": "inferred"}], "value": {"value": "120", "index": 63}, "unit": {"value": "rpm", "index": "inferred"}}, "name": [["layer_material_stirring_speed", "inferred"]], "label": "parameter", "id": "inferred_parameter_26"}, {"attributes": {"name": [{"value": "material_batch_barcode", "index": "inferred"}], "value": {"value": "7", "index": 66}}, "name": [["material_batch_barcode", "inferred"]], "label": "parameter", "id": "inferred_parameter_27"}, {"attributes": {"name": [{"value": "annealing_time", "index": "inferred"}], "value": {"value": "00:20:47", "index": 68}, "unit": {"value": "s", "index": "inferred"}}, "name": [["annealing_time", "inferred"]], "label": "parameter", "id": "inferred_parameter_28"}, {"attributes": {"name": [{"value": "annealing_temperature", "index": "inferred"}], "value": {"value": "100", "index": 69}, "unit": {"value": "C", "index": "inferred"}}, "name": [["annealing_temperature", "inferred"]], "label": "parameter", "id": "inferred_parameter_29"}, {"attributes": {"name": [{"value": "layer_material_temperature", "index": "inferred"}], "value": {"value": "6", "index": 75}, "unit": {"value": "C", "index": "inferred"}}, "name": [["layer_material_temperature", "inferred"]], "label": "parameter", "id": "inferred_parameter_30"}, {"attributes": {"name": [{"value": "layer_material_stirring_time", "index": "inferred"}], "value": {"value": "00:20:47", "index": 76}, "unit": {"value": "s", "index": "inferred"}}, "name": [["layer_material_stirring_time", "inferred"]], "label": "parameter", "id": "inferred_parameter_31"}, {"attributes": {"name": [{"value": "layer_material_stirring_speed", "index": "inferred"}], "value": {"value": "100", "index": 77}, "unit": {"value": "rpm", "index": "inferred"}}, "name": [["layer_material_stirring_speed", "inferred"]], "label": "parameter", "id": "inferred_parameter_32"}], "relationships": []}
        nodes = str(nodes).replace("'", '"')
        print("nodes", nodes)
        return response.Response({'node_json': nodes
        })

    def prepare_data(self, file_link, labels):
        file = File.nodes.get(link=file_link)
        file_obj_bytes = file.get_file()

        # Decode the bytes object to a string
        file_obj_str = file_obj_bytes.decode('utf-8')


        # Use StringIO on the decoded string
        file_obj = StringIO(file_obj_str)
        csv_reader = csv.reader(file_obj)
        first_row = next(csv_reader)

        column_values = [[] for _ in range(len(first_row))]

        for row in csv_reader:
            for i, value in enumerate(row):
                if value != "" and len(column_values[i]) < 4:
                    column_values[i].append(value)

        file_obj.seek(0)

        # Read the first line
        first_line = file_obj.readline().strip()
        first_line = first_line.split(",")
        input = [{'index': i, 'column_values': column_values[i], 'header': header, '1_label': labels[header]['Label'], '1_attribute': labels[header]['Attribute']} for i, header in enumerate(first_line)]
        return input



    def extract_nodes(self, file_link, file_name, attributes, context ):
        node_extractor = NodeExtractor(
            context=context,
            file_link=file_link,
            file_name=file_name,
            data = attributes,
        )
        node_extractor.run()
        return node_extractor.results

@method_decorator(csrf_exempt, name='dispatch')
class GraphExtractView(APIView):

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        node_json = data['params']['node_json']
        context = data['params']['context']
        file_link = data['params']['file_link']
        file_name = data['params']['file_name']


        required_fields = ['node_json', 'context', 'file_link', 'file_name']
        if not all(field in data['params'] for field in required_fields):
            return response.Response({'error': 'Missing required data'}, status=status.HTTP_400_BAD_REQUEST)

        graph = self.extract_relationships(node_json, context)
        graph = str(graph).replace("'", '"')
        return response.Response({'graph_json': graph})



    def extract_relationships(self, nodes, context):
        relationships_extractor = fullRelationshipsExtractor(nodes, context)
        relationships_extractor.run()
        relationships = relationships_extractor.results
        return relationships


@method_decorator(csrf_exempt, name='dispatch')
class GraphImportView(APIView):

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        print("GraphImporter")
        data = json.loads(request.body)
        graph = json.loads(data['params']['graph_json'])
        file_link = data['params']['file_link']
        file_name = data['params']['file_name']
        context = data['params']['context']


        required_fields = ['graph_json', 'file_link']
        if not all(field in data['params'] for field in required_fields):
            return response.Response({'error': 'Missing required data'}, status=status.HTTP_400_BAD_REQUEST)


        print('start import', file_link)

        self.import_graph(file_link, graph, context)
        print('imported data')
        FullTableCache.update(self.request.session.get('first_line'), graph)
        print('updated cache')
        return response.Response({'message': 'Graph imported successfully'})


    def import_graph(self, file_link, graph, context):
        importer = TableImporter(graph, file_link, context)
        importer.run()

