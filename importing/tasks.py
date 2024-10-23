import json
import csv
import logging
from io import StringIO

from matgraph.models.metadata import File
from importing.NodeLabelClassification.labelClassifier import NodeClassifier
from importing.NodeAttributeExtraction.attributeClassifier import AttributeClassifier
from importing.NodeExtraction.nodeExtractor import NodeExtractor
from importing.RelationshipExtraction.completeRelExtractor import (
    fullRelationshipsExtractor,
)
from importing.importer import TableImporter
from importing.models import FullTableCache
from importing.utils.data_processing import sanitize_data

logger = logging.getLogger(__name__)

def extract_labels(task, process):
    try:
        if task.is_cancelled():
            task_cancelled(process)
            return

        file_id = process.file_id
        file_record = File.nodes.get(uid=file_id)
        file_obj_bytes = file_record.get_file()
        file_obj_str = file_obj_bytes.decode("utf-8")
        file_obj = StringIO(file_obj_str)

        node_classifier = NodeClassifier(
            data=file_obj,
            context=process.context,
            file_link=file_record.link,
            file_name=file_record.name,
        )

        if task.is_cancelled():
            task_cancelled(process)
            return

        node_classifier.run()

        if task.is_cancelled():
            task_cancelled(process)
            return

        labels = {
            element["header"]: [element["1_label"], element["column_values"][0]]
            for element in node_classifier.results
        }
        sanitized_labels = sanitize_data(labels)
        sanitized_labels_str = json.dumps(sanitized_labels)

        if task.is_cancelled():
            task_cancelled(process)
            return

        process.labels = sanitized_labels_str
        process.status = "idle"
        process.save()
    except Exception as e:
        process.delete()
        logger.error(f"Error during label extraction: {e}", exc_info=True)
        
def extract_attributes(task, process):
    try:
        if task.is_cancelled():
            task_cancelled(process)
            return
        print('begin')

        file_id = process.file_id
        file_record = File.nodes.get(uid=file_id)
        file_link = file_record.link
        file_name = file_record.name
        
        print("got file")

        # labels = json.loads(process.labels)
        # print("labels")
        # print(labels)
        label_input = prepare_attribute_data(process.labels)
        print("label input")
        print(label_input)

        attribute_classifier = AttributeClassifier(
            label_input,
            context=process.context,
            file_link=file_link,
            file_name=file_name,
        )

        if task.is_cancelled():
            task_cancelled(process)
            return

        print('run')
        attribute_classifier.run()

        if task.is_cancelled():
            task_cancelled(process)
            return

        attributes = {
            element["header"]: {
                "Label": element["1_label"],
                "Attribute": element["1_attribute"],
            }
            for element in attribute_classifier.results
        }
        attributes_str = json.dumps(attributes)

        process.attributes = attributes_str
        process.status = "idle"
        process.save()

    except Exception as e:
        process.status = "idle"
        process.save()
        logger.error(f"Error during attribute extraction: {e}", exc_info=True)

def extract_nodes(task, process):
    try:
        if task.is_cancelled():
            task_cancelled(process)
            return

        file_id = process.file_id
        file_record = File.nodes.get(uid=file_id)
        file_link = file_record.link
        file_name = file_record.name

        attributes = json.loads(process.attributes)
        attribute_input = prepare_node_data(file_id, attributes)

        node_extractor = NodeExtractor(
            context=process.context,
            file_link=file_link,
            file_name=file_name,
            data=attribute_input,
        )

        if task.is_cancelled():
            task_cancelled(process)
            return

        node_extractor.run()

        if task.is_cancelled():
            task_cancelled(process)
            return

        graph = str(node_extractor.results).replace("'", '"')
        graph_str = json.dumps(graph)

        process.graph = graph_str
        process.status = "idle"
        process.save()
    except Exception as e:
        process.status = "error"
        process.save()
        logger.error(f"Error during node extraction: {e}", exc_info=True)

def extract_relationships(self, task, process):
    try:
        if task.is_cancelled():
            task_cancelled(process)
            return

        graph = json.loads(process.graph)
        context = process.context
        header, first_row = prepare_graph_data(process.file_id)
        relationships_extractor = fullRelationshipsExtractor(
            graph, context, header, first_row
        )

        if task.is_cancelled():
            task_cancelled(process)
            return

        relationships_extractor.run()

        if task.is_cancelled():
            task_cancelled(process)
            return

        graph = relationships_extractor.results
        graph = (
            str(graph)
            .replace("'", '"')
            .replace("has_manufacturing_output", "is_manufacturing_output")
        )
        graph_str = json.dumps(graph)

        process.graph = graph_str
        process.status = "idle"
        process.save()
    except Exception as e:
        process.status = "error"
        process.save()
        logger.error(f"Error during graph extraction: {e}", exc_info=True)

def import_graph(self, task, process):
    try:
        if task.is_cancelled():
            task_cancelled(process)
            return

        file_id = process.file_id
        file_record = File.nodes.get(uid=file_id)
        file_link = file_record.link

        graph = json.loads(process.graph)
        context = process.context

        importer = TableImporter(graph, file_link, context)

        if task.is_cancelled():
            task_cancelled(process)
            return

        importer.run()

        if task.is_cancelled():
            task_cancelled(process)
            return

        FullTableCache.update(self.request.session.get("first_line"), graph)
        
        process.status = "imported"
        process.save()
    except Exception as e:
        process.status = "error"
        process.save()
        logger.error(f"Error during graph import: {e}", exc_info=True)
        
def prepare_attribute_data(labels):
    input_data = [
        {"column_values": [value[1]], "header": key, "1_label": value[0]}
        for key, value in labels.items()
    ]
    for index, item in enumerate(input_data):
        item["index"] = index
    return input_data

def prepare_node_data(self, file_id, attributes):
    file_record = File.nodes.get(uid=file_id)
    file_obj_bytes = file_record.get_file()
    file_obj_str = file_obj_bytes.decode("utf-8")
    file_obj = StringIO(file_obj_str)
    csv_reader = csv.reader(file_obj)

    first_row = next(csv_reader)
    column_values = [[] for _ in range(len(first_row))]

    for row in csv_reader:
        for i, value in enumerate(row):
            if value != "" and len(column_values[i]) < 4:
                column_values[i].append(value)

    file_obj.seek(0)

    first_line = file_obj.readline().strip()
    first_line = first_line.split(",")
    input = [
        {
            "index": i,
            "column_values": column_values[i],
            "header": header,
            "1_label": attributes[header][0],
            "1_attribute": attributes[header][1],
        }
        for i, header in enumerate(first_line)
    ]
    return input

def prepare_graph_data(self, file_id):
    file_record = File.nodes.get(uid=file_id)
    file_obj_bytes = file_record.get_file()
    file_obj_str = file_obj_bytes.decode("utf-8")
    file_obj = StringIO(file_obj_str)
    csv_reader = csv.reader(file_obj)

    header = next(csv_reader)
    first_row = next(csv_reader)

    return header, first_row

def task_cancelled(self, process):
    process.status = "cancelled"
    process.save()
    logger.info(f"Task {process.process_id} was cancelled.")