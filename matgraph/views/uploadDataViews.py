import json
from io import StringIO, BytesIO

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from neomodel import db
from rest_framework import views, status, response
from django.urls import reverse

from importing.NodeAttributeExtraction.attributeClassifier import AttributeClassifier
from importing.NodeExtraction.nodeExtractor import NodeExtractor
from importing.NodeLabelClassification.labelClassifier import NodeClassifier
from importing.RelationshipExtraction.completeRelExtractor import fullRelationshipsExtractor
from importing.importer import TableTransformer
from importing.models import ImporterCache, FullTableCache
from matgraph.models.metadata import *  # Import your models here


def upload_success(request):
    return render(request, 'upload_success.html')


@login_required
def create_file_node(uid, file_name, file_path):
    """
    Create a new node in the database representing a file.

    :param uid: The unique ID of the file.
    :param file_name: The name of the file.
    :param file_path: The path of the file in local storage.
    """
    print("create file node")

    db.cypher_query("CREATE (f:File {uid: $uid, file_name: $file_name, file_path: $file_path})",
                    {"uid": uid, "file_name": file_name, "file_path": file_path})





@method_decorator(login_required, name='dispatch')
class FileUploadView(views.APIView):

    def get(self, request, *args, **kwargs):
        return render(request, 'upload.html')

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return render(request, 'upload.html', {'error': 'No file provided'})

        file_record = self.store_file(file_obj)
        self.set_session_data(request, file_record.uid, request.POST.get('context'))

        file_obj.seek(0)
        first_line = file_obj.readline().decode('utf-8').strip().lower()
        self.request.session['first_line'] = first_line
        print("first line", first_line)

        if cached := FullTableCache.fetch(first_line):
            print("full-cache", type(cached), cached, first_line)
        else:
            print("no full-cache")

        return HttpResponseRedirect(reverse('view_data', args=[file_record.uid]))

    def store_file(self, file_obj):
        """Store the uploaded file and return the file record."""
        file_name = file_obj.name
        file_record = File(name=file_name, date_added=DateTimeProperty(default_now=True))
        file_record.file = file_obj
        file_record.save()
        return file_record

    def set_session_data(self, request, file_id, context):
        """Set necessary data in the session."""
        request.session['file_id'] = file_id
        if context:
            print('context is there', context)
            request.session['context'] = context

    @staticmethod
    def parse_error(response):
        # Existing implementation of parse_error
        pass



class TableView(TemplateView):
    template_name = 'table_view.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file = None
        self.headers = []

    def dispatch(self, request, *args, **kwargs):
        self.file_id = request.session.get('file_id')
        if not self.file_id:
            return HttpResponseRedirect('/error/')
        self.fetch_file()
        self.get_context_data()  # Ensure context data is initialized
        return super().dispatch(request, *args, **kwargs)

    def fetch_file(self):
        """Fetch file object from database based on file_id."""
        try:
            self.file = File.nodes.get(uid=self.file_id)
        except ObjectDoesNotExist:
            self.file = None

    def get_dataframe(self):
        """Fetch data from file link and return as a pandas DataFrame."""
        if not self.file:
            return None
        try:
            response = requests.get(self.file.link)
            response.raise_for_status()
            file_content = StringIO(response.content.decode('utf-8'))
            return pd.read_csv(file_content, header=None)
        except Exception as e:
            # Consider logging the error
            return None

    def get_context_data(self, **kwargs):
        """Prepare context data for the template."""
        context = super().get_context_data(**kwargs)
        df = self.get_dataframe()
        if df is not None:
            self.headers = df.iloc[0].tolist()
            data_rows = df.values.tolist()
            context['table'] = [self.headers] + data_rows
            self.request.session['headers'] = self.headers
        else:
            context['error'] = "Failed to load data."
        return context

    def convert_to_dataframe(self, edited_data):
        """Convert edited data to pandas DataFrame."""
        data_list = [self.headers] + [edited_data.getlist(key) for key in edited_data if key.endswith('[]')]
        return pd.DataFrame(data=data_list[1:], columns=data_list[0])

    def post(self, request, *args, **kwargs):
        updated_df = self.convert_to_dataframe(request.POST)
        self.save_dataframe_to_file(updated_df)
        return HttpResponseRedirect(f"/data/label-extraction/{self.file_id}")

    def save_dataframe_to_file(self, df):
        """Save DataFrame to file and update session information."""
        try:
            csv_obj = df.to_csv(index=False).encode()
            buffer = BytesIO(csv_obj)
            self.update_file_content(buffer)
            self.request.session['file_id'] = self.file.uid
        except Exception as e:
            # Consider logging the error
            pass

    def update_file_content(self, buffer):
        """Update file content in the database."""
        try:
            new_file = File(name=self.file.name, date_added=DateTimeProperty(default_now=True), file=buffer)
            new_file.save()
            self.request.session['new_file_id'] = new_file.uid
        except Exception as e:
            # Consider logging the error
            pass





class NodeLabelView(TemplateView):
    template_name = 'label_analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        file_id = self.request.session.get('new_file_id')
        self.file_id = file_id

        if file_id:
            file = File.nodes.get(uid=file_id)
            print("File link: ", file.link)
            response = requests.get(file.link)
            if response.status_code == 200:
                file_obj = StringIO(response.content.decode('utf-8'))
                context['analysis_results'] = self.extract_labels(file_obj, context, file.link, file.name, file_id)
            else:
                context['error'] = "Could not fetch the file."
        else:
            context['error'] = "No file ID found in session."

        return context

    def post(self, request, *args, **kwargs):
        node_labels = request.session.get('node_labels')
        if node_labels:
            updated_labels = {key: value for key, value in request.POST.items() if key != 'csrfmiddlewaretoken'}
            self.update_results(updated_labels)
            file_id = self.request.session.get('new_file_id')
            self.file_id = file_id
            return HttpResponseRedirect(reverse('attribute-extraction', args=[self.file_id]))
        else:
            context = {'error': "TableTransformer instance not found in session."}
            return render(request, self.template_name, context)

    def update_results(self, updated_labels):
        # Fetch current labels and labels output from the session
        current_labels = self.request.session.get('node_labels', {})
        node_labels_output = self.request.session.get('node_labels_output', [])
        updated = False  # Flag to track if any update occurred

        for key, new_label in updated_labels.items():
            # Update current labels if necessary
            if key in current_labels and current_labels[key] != new_label:
                ImporterCache.update(key, column_label=new_label, attribute_type="column_label")
                current_labels[key] = new_label
                updated = True

            # Update node_labels_output if necessary
            for label_dict in node_labels_output:
                if label_dict.get('header') == key and label_dict.get('1_label') != new_label:
                    label_dict['1_label'] = new_label
                    updated = True

        # Save updates to the session if any updates have occurred
        if updated:
            self.request.session['node_labels'] = current_labels
            self.request.session['node_labels_output'] = node_labels_output
            self.request.session.modified = True  # Explicitly mark the session as modified



    def extract_labels(self, file_obj, context, file_link, file_name, file_id):
        table_transformer = TableTransformer(file_obj, context, file_link, file_name)

        table_transformer.create_data()
        table_transformer.classify_node_labels()
        node_classifier = NodeClassifier(data = file_obj,
                                              context = context,
                                              file_link = file_link,
                                              file_name = file_name)
        node_classifier.run()
        node_classifier.results

        # Optionally, store table_transformer in the session

        node_labels = {element['header']: element['1_label'] for element in node_classifier.results}
        print(f"Node labels: {node_labels}")
        self.request.session['node_labels'] = node_labels
        self.request.session['node_labels_output'] = node_classifier.results

        return node_labels



class NodeAttributeView(TemplateView):
    template_name = 'attribute_analysis.html'
    ATTRIBUTE_MAPPER = {
    "Matter": ["name", "ratio", "concentration", "batch_number", "identifier"],
    "Parameter": [ "value", "unit", "average", "std", "error"],
    "Measurement": ["name", "identifier"],
    "Manufacturing": ["name", "identifier"],
    "Metadata": ["name", "identifier"]
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.file_id = self.request.session.get('new_file_id')
        node_labels = self.request.session.get('node_labels')

        if self.file_id and node_labels:
            file = File.nodes.get(uid=self.file_id)
            response = requests.get(file.link)
            if response.status_code == 200:
                file_obj = StringIO(response.content.decode('utf-8'))
                # Extract attributes and add to context
                attributes = self.extract_attributes(file_obj, file.link, file.name, node_labels, self.request.session['context'])
                context['attributes'] = attributes
            else:
                context['error'] = "Could not fetch the file."
        else:
            context['error'] = "No file ID or node labels found in session."

        return context


    def post(self, request, *args, **kwargs):
        updated_attributes = {}
        for header, selected_attribute in request.POST.items():
            if header not in ['csrfmiddlewaretoken']:  # Exclude CSRF token
                # Update the selected attribute for each header
                updated_attributes[header] = selected_attribute
                print(f"Header: {header}, Selected attribute: {selected_attribute}")

        # Save the updated attributes to the session or database as needed
        self.update_attributes(updated_attributes)

        # Redirect to the next step or refresh the page
        self.file_id = self.request.session.get('new_file_id')

        return HttpResponseRedirect(reverse('node-aggregation', args=[self.file_id]))
    # def post(self, request, *args, **kwargs):
    #     return HttpResponseRedirect(reverse(f"/data/label-extraction/{self.file_id}"))  # Redirect to the next step

    def update_attributes(self, updated_attributes):
        # Assuming attributes are stored in session
        current_attributes = self.request.session.get('attributes', {})
        for header, selected_attribute in updated_attributes.items():
            if header in current_attributes:
                current_attributes[header]['selected_attribute'] = selected_attribute

    def extract_attributes(self, file_obj, file_link, file_name, node_labels, context):
        attribute_classifier = AttributeClassifier(
            self.request.session['node_labels_output'],
            context=context,
            file_link=file_link,
            file_name=file_name
        )
        attribute_classifier.run()
        _predicted_attributes = attribute_classifier.results
        self.request.session['predicted_attributes'] = _predicted_attributes
        self.request.session['attributes'] = {element['header']: {"label": element["1_label"],
                                                                  "attributes": self.ATTRIBUTE_MAPPER[element['1_label']],
                                                                  "selected_attribute": element['1_attribute']} for element in _predicted_attributes}
        self.request.session['node_attributes_output'] = _predicted_attributes
        return self.request.session['attributes']


class NodeView(TemplateView):
    template_name = 'node_analysis.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file = None

    def dispatch(self, request, *args, **kwargs):
        self.file_id = request.session.get('file_id') or request.session.get('new_file_id')
        if not self.file_id:
            return HttpResponseRedirect('/error/')
        self.fetch_file()
        return super().dispatch(request, *args, **kwargs)

    def fetch_file(self):
        """Fetch file object from database based on file_id."""
        try:
            self.file = File.nodes.get(uid=self.file_id)
        except File.DoesNotExist:
            self.file = None
            # You might want to handle this case, such as logging the error or redirecting

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.file_id = self.request.session.get('new_file_id')
        node_attributes = self.request.session.get('attributes')

        if self.file_id and node_attributes:
            file = File.nodes.get(uid=self.file_id)
            response = requests.get(file.link)
            if response.status_code == 200:
                file_obj = StringIO(response.content.decode('utf-8'))
                # Extract attributes and add to context
                nodes = self.extract_nodes(file_obj, file.link, file.name, node_attributes, self.request.session['context'])
                context['nodes'] = nodes
                self.request.session['nodes'] = nodes  # Store nodes in session

                print("NODES:", context['nodes'])
            else:
                context['error'] = "Could not fetch the file."
        else:
            context['error'] = "No file ID or node labels found in session."

        return context

    def extract_nodes(self, file_obj, file_link, file_name, node_labels, context ):
        node_extractor = NodeExtractor(
            context=context,
            file_link=file_link,
            file_name=file_name,
            data = self.request.session['node_attributes_output'],
        )
        node_extractor.run()
        return node_extractor.results


    def post(self, request, *args, **kwargs):
        nodes = request.session.get('nodes')
        if nodes:
            for key, value in request.POST.items():
                if key.startswith('attr-'):
                    parts = key.split('-')
                    if len(parts) == 4:
                        node_id, attribute, attr_type = parts[1], parts[2], parts[3]
                        for node in nodes['nodes']:
                            if str(node['node_id']) == node_id:
                                if attr_type == 'value':
                                    index = request.POST.get(f'attr-{node_id}-{attribute}-index')
                                    if index != 'inferred':
                                        node['attributes'][attribute] = [[value, int(index)]]
                                    else:
                                        node['attributes'][attribute] = [[value, index]]
        request.session['nodes'] = nodes
        self.file_id = self.request.session.get('new_file_id')

        return HttpResponseRedirect(reverse('graph-construction', args=[self.file_id]))

class GraphView(TemplateView):
    template_name = 'node_analysis.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file = None

    def dispatch(self, request, *args, **kwargs):
        self.file_id = request.session.get('file_id') or request.session.get('new_file_id')
        if not self.file_id:
            return HttpResponseRedirect('/error/')
        self.fetch_file()
        return super().dispatch(request, *args, **kwargs)

    def fetch_file(self):
        """Fetch file object from database based on file_id."""
        try:
            self.file = File.nodes.get(uid=self.file_id)
        except File.DoesNotExist:
            self.file = None
            # You might want to handle this case, such as logging the error or redirecting

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.file_id = self.request.session.get('new_file_id')
        node_attributes = self.request.session.get('attributes')

        if self.file_id and node_attributes:
            file = File.nodes.get(uid=self.file_id)
            response = requests.get(file.link)
            if response.status_code == 200:
                file_obj = StringIO(response.content.decode('utf-8'))
                # Extract attributes and add to context
                nodes = self.extract_nodes(file_obj, file.link, file.name, node_attributes, self.request.session['context'])
                context['nodes'] = nodes
                self.request.session['nodes'] = nodes  # Store nodes in session

            else:
                context['error'] = "Could not fetch the file."
        else:
            context['error'] = "No file ID or node labels found in session."

        return context

    def extract_nodes(self, file_obj, file_link, file_name, node_labels, context ):
        node_extractor = NodeExtractor(
            context=context,
            file_link=file_link,
            file_name=file_name,
            data = self.request.session['node_attributes_output'],
        )
        node_extractor.run()
        return node_extractor.results
    def post(self, request, *args, **kwargs):
        nodes = request.session.get('nodes')
        if nodes:
            for key, value in request.POST.items():
                parts = key.split('-')
                if len(parts) == 3:
                    node_id, _, attribute = parts
                    # Update the specific node's attribute
                    for node in nodes['nodes']:
                        # print(node['node_id'], node_id)
                        if str(node['node_id']) == node_id:
                            node['attributes'][attribute] = [value]
                            print("miau", value, key)
                else:
                    # Handle the case where the key does not match the expected format
                    pass
            request.session['nodes'] = nodes
        return redirect('upload_success')

class GraphView(TemplateView):
    template_name = 'node_analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        nodes = self.request.session.get('nodes')
        if nodes:
            graph = self.extract_relationships(nodes)
            context['nodes'] = graph
            self.request.session['nodes'] = json.dumps(graph)
        else:
            context['error'] = "No nodes data available."

        return context

    def extract_relationships(self, nodes):
        print("NODES:", nodes)
        relationships_extractor = fullRelationshipsExtractor(nodes)
        relationships_extractor.run()
        relationships = relationships_extractor.results
        return relationships
    def post(self, request, *args, **kwargs):
        # Similar to NodeView, but include logic to handle updates to relationships
        print('update cache')
        self.request.session['nodes'] = json.loads(self.request.session['nodes'])
        print(type(self.request.session['nodes']))

        FullTableCache.update(self.request.session.get('first_line'), 'graph', graph=self.request.session['nodes'])
        return redirect('upload_success')
