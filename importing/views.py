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
        node_labels = {element['header']: [[element['1_label']], element['column_values'][0]] for element in node_classifier.results}
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
        input_data = [{'column_values': value['Attribute'], 'header': key, '1_label': value['Label']} for key, value in labels.items()]
        for index, key in enumerate(input_data):
            key['index'] = index
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
        nodes = str(nodes).replace("'", '"')
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
        header, first_row = self.prepare_data(file_link)
        graph = self.extract_relationships(node_json, context, header, first_row)
        graph = str(graph).replace("'", '"').replace("has_manufacturing_output", "is_manufacturing_output")
        return response.Response({'graph_json': graph})

    def prepare_data(self, file_link):
        file = File.nodes.get(link=file_link)
        file_obj_bytes = file.get_file()

        # Decode the bytes object to a string
        file_obj_str = file_obj_bytes.decode('utf-8')


        # Use StringIO on the decoded string
        file_obj = StringIO(file_obj_str)
        csv_reader = csv.reader(file_obj)
        header = next(csv_reader)
        first_row = next(csv_reader)

        return header, first_row


    def extract_relationships(self, nodes, context, header, first_row):
        relationships_extractor = fullRelationshipsExtractor(nodes, context, header, first_row)
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



        self.import_graph(file_link, graph, context)
        FullTableCache.update(self.request.session.get('first_line'), graph)
        return response.Response({'message': 'Graph imported successfully'})


    def import_graph(self, file_link, graph, context):
        importer = TableImporter(graph, file_link, context)
        importer.run()

