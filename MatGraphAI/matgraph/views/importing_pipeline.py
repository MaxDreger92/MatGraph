import json

from django.core.exceptions import ValidationError
from django.views.generic import TemplateView
from neomodel import DateTimeProperty
from rest_framework import response, status

from importing.NodeAttributeExtraction.attributeClassifier import AttributeClassifier
from importing.NodeExtraction.nodeExtractor import NodeExtractor
from importing.NodeLabelClassification.labelClassifier import NodeClassifier
from importing.RelationshipExtraction.completeRelExtractor import fullRelationshipsExtractor
from importing.models import FullTableCache
from matgraph.models.metadata import File


class LabelExtractView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            if 'file' not in request.FILES:
                return response.Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

            file_obj = request.FILES['file']
            context = request.POST.get('context', '{}')  # Assuming context is JSON string in POST data

            # Basic validation (can be more specific based on requirements)
            if not file_obj.name.endswith('.csv'):
                return response.Response({'error': 'Invalid file type'}, status=status.HTTP_400_BAD_REQUEST)

            first_line = str(file_obj.readline().decode('utf-8')).strip().lower()

            if cached := FullTableCache.fetch(first_line, '', 'graph'):
                return response.Response({'graph': cached}, status=status.HTTP_400_BAD_REQUEST)

            file_record = self.store_file(file_obj)
            labels = self.extract_labels(file_obj, context, file_record.link, file_record.name)

            return response.Response({
                'label_dict': labels,
                'file_link': file_record.link,
                'file_name': file_record.name
            })

        except ValidationError as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the exception here
            return response.Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def extract_labels(self, file_obj, context, file_link, file_name):
        """Extract labels from the uploaded file."""
        node_classifier = NodeClassifier(data = file_obj,
                                         context = context,
                                         file_link = file_link,
                                         file_name = file_name)
        node_classifier.run()
        node_classifier.results

    def store_file(self, file_obj):
        """Store the uploaded file and return the file record."""
        file_name = file_obj.name
        file_record = File(name=file_name, date_added=DateTimeProperty(default_now=True))
        file_record.file = file_obj
        file_record.save()
        return file_record

class AttributeExtractView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            labels = data['label_dict']
            context = data['context']

            if not labels or not context:
                return response.Response({'error': 'Missing labels or context'}, status=status.HTTP_400_BAD_REQUEST)

            attributes = self.extract_attributes(labels, context)
            return response.Response({'attribute_dict': attributes})

        except Exception as e:
            # Log the exception here
            return response.Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def extract_attributes(self, labels, file_link, file_name, node_labels, context):
        attribute_classifier = AttributeClassifier(
            node_labels,
            context=context,
            file_link=file_link,
            file_name=file_name
        )
        attribute_classifier.run()
        _predicted_attributes = attribute_classifier.results
        self.request.session['predicted_attributes'] = _predicted_attributes
        self.request.session['attributes'] = {element['header']: {"label": element["1_label"],
                                                                  "attributes": self.ATTRIBUTE_MAPPER[element['1_label']]} for element in _predicted_attributes}
        self.request.session['node_attributes_output'] = _predicted_attributes
        return self.request.session['attributes']

class NodeExtractView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            # Parsing JSON data from request body
            data = json.loads(request.body)

            # Validate the presence of required fields
            required_fields = ['attribute_dict', 'context', 'file_link', 'file_name']
            if not all(field in data for field in required_fields):
                return response.Response({'error': 'Missing required data'}, status=status.HTTP_400_BAD_REQUEST)

            context = data['context']
            attributes = data['attribute_dict']
            file_link = data['file_link']
            file_name = data['file_name']

            nodes = self.extract_nodes(file_link, file_name, attributes, context)
            return response.Response({'node_json': nodes})

        except json.JSONDecodeError:
            return response.Response({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the exception here
            return response.Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def extract_nodes(self, file_link, file_name, attributes, context ):
        node_extractor = NodeExtractor(
            context=context,
            file_link=file_link,
            file_name=file_name,
            data = attributes,
            )
        node_extractor.run()
        return node_extractor.results

class GraphExtractView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            required_fields = ['node_json', 'context', 'file_link', 'file_name']
            if not all(field in data for field in required_fields):
                return response.Response({'error': 'Missing required data'}, status=status.HTTP_400_BAD_REQUEST)

            context = data['context']
            nodes = data['node_json']
            file_link = data['file_link']
            file_name = data['file_name']

            graph = self.extract_graph(file_link, file_name, nodes, context)
            return response.Response({'graph_json': graph})

        except json.JSONDecodeError:
            return response.Response({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the exception here
            return response.Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def extract_relationships(self, nodes):
        relationships_extractor = fullRelationshipsExtractor(nodes)
        relationships_extractor.run()
        relationships = relationships_extractor.results
        return relationships

class GraphImportView:
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            required_fields = ['graph_json', 'file_link']
            if not all(field in data for field in required_fields):
                return response.Response({'error': 'Missing required data'}, status=status.HTTP_400_BAD_REQUEST)

            graph = data['graph_json']
            file_link = data['file_link']


            self.import_graph(file_link, file_name, graph, context)
            return response.Response({'message': 'Graph imported successfully'})

        except json.JSONDecodeError:
            return response.Response({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the exception here
            return response.Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
