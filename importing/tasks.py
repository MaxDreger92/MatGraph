import json
import csv
import logging
from io import StringIO

from django.db import connection, close_old_connections

from matgraph.models.metadata import File
from importing.NodeLabelClassification.labelClassifier import NodeClassifier
from importing.NodeAttributeExtraction.attributeClassifier import AttributeClassifier
from importing.NodeExtraction.nodeExtractor import NodeExtractor
from importing.RelationshipExtraction.completeRelExtractor import (
    fullRelationshipsExtractor,
)
from importing.importer import TableImporter
from importing.models import FullTableCache, ImportProcessStatus, ImportProcessKeys
from importing.utils.data_processing import sanitize_data
from importing.utils.callback import send_importing_callback

logger = logging.getLogger(__name__)

def extract_labels(task, process):
    close_old_connections()
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

        if task.is_cancelled():
            task_cancelled(process)
            return

        process.labels = sanitized_labels
        process.status = ImportProcessStatus.COMPLETED
        process.save()
    except Exception as e:
        import traceback
        logger.error(
            f"Exception occurred while creating import process: {e}", exc_info=True
        )
        process.status = ImportProcessStatus.FAILED
        process.error_message = traceback.format_exc()
        process.save()
    finally:
        send_importing_callback(process.process_id, ImportProcessKeys.LABELS)
        connection.close()
        
def extract_attributes(task, process):
    close_old_connections()
    try:
        if task.is_cancelled():
            task_cancelled(process)
            return

        file_id = process.file_id
        file_record = File.nodes.get(uid=file_id)
        file_link = file_record.link
        file_name = file_record.name
        
        labels = process.labels
        label_input = prepare_attribute_data(labels)

        attribute_classifier = AttributeClassifier(
            label_input,
            context=process.context,
            file_link=file_link,
            file_name=file_name,
        )

        if task.is_cancelled():
            task_cancelled(process)
            return

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

        process.attributes = attributes
        process.status = ImportProcessStatus.COMPLETED
        process.save()
    except Exception as e:
        import traceback
        logger.error(
            f"Exception occurred while creating import process: {e}", exc_info=True
        )
        process.status = ImportProcessStatus.FAILED
        process.error_message = traceback.format_exc()
        process.save()
    finally:
        send_importing_callback(process.process_id, ImportProcessKeys.ATTRIBUTES)
        connection.close()

def extract_nodes(task, process):
    close_old_connections()
    try:
        if task.is_cancelled():
            task_cancelled(process)
            return

        file_id = process.file_id
        file_record = File.nodes.get(uid=file_id)
        file_link = file_record.link
        file_name = file_record.name

        attributes = process.attributes
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

        graph = json.loads(str(node_extractor.results).replace("'", '"'))

        process.nodes = graph
        process.status = ImportProcessStatus.COMPLETED
        process.save()
    except Exception as e:
        import traceback
        logger.error(
            f"Exception occurred while creating import process: {e}", exc_info=True
        )
        process.status = ImportProcessStatus.FAILED
        process.error_message = traceback.format_exc()
        process.save()
    finally:
        send_importing_callback(process.process_id, ImportProcessKeys.NODES)
        connection.close()

def extract_relationships(task, process):
    close_old_connections()
    try:
        if task.is_cancelled():
            task_cancelled(process)
            return

        graph = process.nodes
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

        process.graph = graph
        process.status = ImportProcessStatus.COMPLETED
        process.save()
    except Exception as e:
        import traceback
        logger.error(
            f"Exception occurred while creating import process: {e}", exc_info=True
        )
        process.status = ImportProcessStatus.FAILED
        process.error_message = traceback.format_exc()
        process.save()
    finally:
        send_importing_callback(process.process_id, ImportProcessKeys.GRAPH)
        connection.close()

def import_graph(task, process, request_data):
    close_old_connections()
    try:
        if task.is_cancelled():
            task_cancelled(process)
            return

        file_id = process.file_id
        file_record = File.nodes.get(uid=file_id)
        file_link = file_record.link

        graph = process.graph
        context = process.context

        importer = TableImporter(graph, file_link, context)

        if task.is_cancelled():
            task_cancelled(process)
            return

        importer.run()

        if task.is_cancelled():
            task_cancelled(process)
            return

        FullTableCache.update(request_data["session"], graph)
        
        process.status = ImportProcessStatus.COMPLETED
        process.save()
    except Exception as e:
        import traceback
        logger.error(
            f"Exception occurred while creating import process: {e}", exc_info=True
        )
        process.status = ImportProcessStatus.FAILED
        process.error_message = traceback.format_exc()
        process.save()
    finally:
        send_importing_callback(process.process_id, ImportProcessKeys.IMPORT)
        connection.close()
        
def prepare_attribute_data(labels):
    input_data = [
        {"column_values": [value[1]], "header": key, "1_label": value[0]}
        for key, value in labels.items()
    ]
    for index, item in enumerate(input_data):
        item["index"] = index
    return input_data

def prepare_node_data(file_id, attributes):
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
            "1_label": attributes[header]['Label'],
            "1_attribute": attributes[header]['Attribute']
        }
        for i, header in enumerate(first_line)
    ]
    return input

def prepare_graph_data(file_id):
    file_record = File.nodes.get(uid=file_id)
    file_obj_bytes = file_record.get_file()
    file_obj_str = file_obj_bytes.decode("utf-8")
    file_obj = StringIO(file_obj_str)
    csv_reader = csv.reader(file_obj)

    header = next(csv_reader)
    first_row = next(csv_reader)

    return header, first_row

def task_cancelled(process):
    process.status = ImportProcessStatus.CANCELLED
    process.error_message = "Task was cancelled by the user."
    process.save()
    logger.info(f"Task {process.process_id} was cancelled.")