import uuid
from datetime import date, datetime

from neo4j.time import Date
from neomodel import DateTimeProperty, DateProperty

from importing.OntologyMapper.OntologyMapper import OntologyMapper
from matgraph.models.ontology import EMMOMatter, EMMOProcess, EMMOQuantity


class Neo4JHandler:
    def __init__(self):
        self.ontology_list = None

    def add_to_ontology(self):
        """
        Takes the list of dictionaries returned by _save_to_neo4j and uses OntologyMapper
        to create or match them in the ontology. Then connects them (via is_a or parent/child
        relationships) and stores the original uid on each ontology node.

        :param data_list: A list of dicts in the format:
            [
                {
                    "class": "EMMOMatter" | "EMMOProcess" | "EMMOQuantity",
                    "uid": "some-neo4j-generated-uuid",
                    "name": "the-node-name-or-value"
                },
                ...
            ]
        :return: A list of dicts with details about how each item was mapped, e.g.:
            [
                {
                    "neo4j_uid": "the-uuid-from-neo4j",
                    "mapped_node_name": "Name in Ontology",
                    "mapped_node_uid": "UID or IRI from Ontology",
                    "class": "EMMOMatter" (etc.)
                },
                ...
            ]
        """
        # 1) We need to map "EMMOMatter", "EMMOProcess", "EMMOQuantity"
        #    to the actual classes or their python wrappers.
        #    Below is a hypothetical mapping to your EMMO python classes:
        class_map = {
            "EMMOMatter": (EMMOMatter),
            "EMMOProcess": (EMMOProcess, "manufacturing"),
            "EMMOQuantity": (EMMOQuantity, "property")
        }

        mapped_results = []

        for item in self.ontology_list:
            class_type = item.get("class", "")
            neo4j_uid  = item.get("uid", "")
            name_value = item.get("name", "")

            if not class_type or not neo4j_uid or not name_value:
                # Skip entries missing essential info
                continue

            # 2) Determine which ontology class & label to use.
            #    "label" is what you pass to OntologyMapper.__init__(...)
            #    If "EMMOProcess" can also mean "measurement", "fabrication", etc.,
            #    add logic to decide the label.
            if class_type not in class_map:
                # Not recognized—skip or handle error
                continue

            ontology_class, mapper_label = class_map[class_type]

            # 3) Instantiate the OntologyMapper
            #    The "context" argument might be your domain context or provenance info.
            #    "label" is the category label for the name (e.g. 'matter', 'property').
            mapper = OntologyMapper(
                context="",
                label=mapper_label,
                ontology_class=ontology_class
            )

            # 4) Map the name_value to an ontology node. If needed, the mapper
            #    will create a new node or find an existing match.
            ontology_node = mapper.map_name(name_value)

            # 5) Store the Neo4j uid on the ontology node for round-tripping.
            #    Adjust the property name as needed (e.g., 'onto_uid', 'neo4j_uid', etc.).
            query = f"""
            MATCH (n:{ontology_class.__label__} {{uid: '{ontology_node.uid}'}})
            MATCH (m {{uid: '{neo4j_uid}'}})
            MERGE (m)-[:IS_A]->(n)
            """
            db.cypher_query(query)

            # 6) The OntologyMapper internally calls _connect_to_ontology for
            #    parent/child linking. If you need custom linking here (like an explicit
            #    is_a connection to an anchor node in your ontology), do it below:
            #
            #    anchor_node = EMMOMatter.get(name="Material")  # Example
            #    if anchor_node:
            #        ontology_node.is_a.connect(anchor_node)

            # 7) Collect the result so you can see which node was created or matched.
            mapped_results.append({
                "neo4j_uid": neo4j_uid,
                "mapped_node_name": ontology_node.name,
                "mapped_node_uid": getattr(ontology_node, "onto_uid", None)
                                   or getattr(ontology_node, "uid", None),
                "class": class_type
            })

        return mapped_results



class Neo4jOrganizationalDataHandler(Neo4JHandler):
    def _save_to_neo4j(self):
        # Ensure the OrganizationalData instance is linked to an Experiment
        if not self.experiment:
            print("No associated Experiment found. Skipping Neo4j synchronization.")
            return []

        experiment_uid = str(self.experiment.uid)
        organizational_data_uid = str(self.uid)

        # Parse fields that may contain multiple entries
        authors = self.author.split('\n') if self.author else []
        authors = [author.strip() for author in authors if author.strip()]

        # Handle publication fields
        publications = []
        if self.publication:
            publications.append({
                "uid": str(uuid.uuid4()),
                "key": "publication",
                "value": self.publication,
                "specific_label": "Publication"
            })

        # Handle authors as separate metadata entries
        author_entries = []
        for author in authors:
            author_entries.append({
                "uid": str(uuid.uuid4()),
                "key": "author",
                "value": author,
                "specific_label": "Author"
            })

        # Handle other metadata fields with their specific labels
        metadata_entries = []

        # Institution
        if self.institution:
            metadata_entries.append({
                "uid": str(uuid.uuid4()),
                "key": "institution",
                "value": self.institution,
                "specific_label": "Institution"
            })

        # Founding Body
        if self.founding_body:
            metadata_entries.append({
                "uid": str(uuid.uuid4()),
                "key": "founding_body",
                "value": self.founding_body,
                "specific_label": "FoundingBody"
            })

        # Additional Metadata with specific labels
        additional_metadata = {
            "country": "Country",
            "topic": "Topic",
            "device": "Device",
            "component": "Component",
            "subcomponent": "Subcomponent",
            "granularity_level": "GranularityLevel",
            "format": "Format",
            "file_size": "FileSize",
            "file_size_unit": "FileSizeUnit",
            "file_name": "File",
            "dimension_x": "DimensionX",
            "dimension_y": "DimensionY",
            "dimension_z": "DimensionZ",
            "pixel_per_metric": "PixelPerMetric",
            "link": "Link",
            "mask_exist": "MaskExist",
            "mask_link": "MaskLink",
            "doi": "DOI",
            "journal": "Journal",
            "volume": "Volume",
            "issue": "Issue",
            "pages": "Pages",
            "publication_date": "PublicationDate",
            "orcid": "ORCID",
            "email": "Email",
            "published": "Published",
            # Add other fields as necessary
        }

        for key, label in additional_metadata.items():
            value = getattr(self, key, None)
            if value:
                if isinstance(value, list):
                    for item in value:
                        metadata_entries.append({
                            "uid": str(uuid.uuid4()),
                            "key": key,
                            "value": item,
                            "specific_label": label
                        })
                else:
                    metadata_entries.append({
                        "uid": str(uuid.uuid4()),
                        "key": key,
                        "value": value,
                        "specific_label": label
                    })

        # Combine all metadata entries
        all_metadata = publications + author_entries + metadata_entries

        # Prepare the Cypher query
        cypher_query = """
        // Merge the Experiment node
        MERGE (e:Experiment {uid: $experiment_uid})
        WITH *
        // Iterate over each metadata entry
        UNWIND $metadata_entries AS meta
        CALL {
            WITH e, meta
            // Create the Metadata node with the base label
            MERGE (m:Metadata {uid: meta.uid})
            SET m.value = meta.value
            WITH *

            // Dynamically add the specific label based on meta.key
            CALL apoc.create.addLabels(m, [meta.specific_label]) YIELD node
            MERGE (e)-[:HAS_METADATA]->(m)
            RETURN node
        }
        RETURN True
        """

        parameters = {
            "experiment_uid": experiment_uid,
            "metadata_entries": all_metadata,
        }

        # Execute the Cypher query
        try:
            output, meta = db.cypher_query(cypher_query, params=parameters)
        except Exception as e:
            print("Error executing Neo4j OrganizationalData query:", e)

        # ---------------------------------------------------------------------
        # Additional query to fetch the desired nodes (Matter, Manufacturing,
        # Measurement, Parameter, Property) and return them in the requested format
        # ---------------------------------------------------------------------
        result_query = """
        MATCH (n)
        WHERE n:Matter OR n:Manufacturing OR n:Measurement OR n:Parameter OR n:Property
        RETURN 
            CASE 
                WHEN n:Matter THEN 'EMMOMatter'
                WHEN n:Manufacturing THEN 'EMMOProcess'
                WHEN n:Measurement THEN 'EMMOProcess'
                WHEN n:Parameter THEN 'EMMOQuantity'
                WHEN n:Property THEN 'EMMOQuantity'
            END AS class,
            n.uid AS uid,
            CASE
                WHEN n.name IS NOT NULL THEN n.name
                WHEN n.value IS NOT NULL THEN toString(n.value)
                ELSE "N/A"
            END AS name
        """

        results, meta = db.cypher_query(result_query)

        output_list = []
        for row in results:
            output_list.append({
                "class": row[0],
                "uid": row[1],
                "name": row[2],
            })

        self.ontology_list = output_list
        self.add_to_ontology()



class Neo4jFabricationWorkflowHandler(Neo4JHandler):
    def _save_to_neo4j(self):
        # Cypher query to merge Synthesis and its Steps, including ordered relationships
        cypher_query = """
        // Merge the Synthesis node
        MERGE (e:Experiment:Process {uid: $experiment_uid})
        MERGE (s:Manufacturing:Process {uid: $uid, type: $type})
        MERGE (e)-[:HAS_PART]->(s)
        WITH s, $steps AS steps, $experiment_uid AS experiment_uid
        
        // Iterate over each step
        UNWIND steps AS step
        CALL {
            // Create or merge Manufacturing node
            WITH step, experiment_uid, s
            CREATE (ss:Manufacturing {uid: step.uid})
            MERGE (s)-[:HAS_PART]->(ss)
            SET ss.name = step.technique, ss.order = step.order
            WITH ss, step, experiment_uid
        
            // Associate Precursor Materials
            CALL {
                WITH ss, step, experiment_uid
                UNWIND step.precursor_materials AS precursor
                    MERGE (mp:Matter {name: precursor.name, experiment_uid: experiment_uid})
                    ON CREATE SET mp.uid = precursor.uid
                    FOREACH(ignore IN CASE WHEN precursor.amount IS NOT NULL AND precursor.unit IS NOT NULL THEN [1] ELSE [] END |
                        CREATE (p:Property {value: precursor.amount, unit: precursor.unit, uid: apoc.create.uuid()})
                        MERGE (mp)-[:HAS_AMOUNT]->(p)
                    )
                    MERGE (mp)-[:IS_MANUFACTURING_INPUT]->(ss)
            }
        
            // Associate Target Materials
            CALL {
                WITH ss, step, experiment_uid
                UNWIND step.target_materials AS target
                    MERGE (mt:Matter {name: target.name, experiment_uid: experiment_uid})
                    ON CREATE SET mt.uid = target.uid
                    FOREACH(ignore IN CASE WHEN target.amount IS NOT NULL AND target.unit IS NOT NULL THEN [1] ELSE [] END |
                        CREATE (p:Property {value: target.amount, unit: target.unit, uid: apoc.create.uuid()})
                        MERGE (mt)-[:HAS_AMOUNT]->(p)
                    )
                    MERGE (ss)-[:HAS_MANUFACTURING_OUTPUT]->(mt)
            }
        
            // Associate Parameters
            CALL {
                WITH ss, step
                UNWIND step.parameters AS param
                    CREATE (pa:Parameter {uid: param.uid})
                    SET pa.name = param.name, pa.value = param.value, pa.unit = param.unit
                    FOREACH(ignore IN CASE WHEN param.error IS NOT NULL THEN [1] ELSE [] END |
                        SET pa.error = param.error
                    )
                    MERGE (ss)-[:HAS_PARAMETER]->(pa)
            }
        
            // Associate Metadata
            CALL {
                WITH ss, step
                UNWIND step.metadatas AS meta
                    CREATE (md:Metadata {uid: meta.uid})
                    SET md.key = meta.key, md.value = meta.value
                    MERGE (ss)-[:HAS_METADATA]->(md)
            }
        }
        
        // After processing all steps, create ordered relationships between them
        WITH steps
        UNWIND range(0, size(steps) - 2) AS idx
            MATCH (current:Manufacturing {uid: steps[idx].uid})
            MATCH (next:Manufacturing {uid: steps[idx + 1].uid})
            MERGE (current)-[:FOLLOWED_BY]->(next)
        """

        # Prepare parameters
        steps_queryset = self.steps.all().order_by('order')
        steps_data = []
        for step in steps_queryset:
            step_data = {
                "uid": str(step.uid),  # Convert UUID to string
                "order": step.order,
                "technique_id": str(step.technique.uid) if step.technique else None,  # Convert UUID to string
                "technique": step.technique.name if step.technique else None,
                "precursor_materials": [
                    {
                        "uid": str(material['uid']),
                        "name": material['name'],
                        "amount": material['amount'],
                        "unit": material['unit']
                    }
                    for material in step.precursor_materials.all().values('uid', 'name', 'amount', 'unit')
                ],
                "target_materials": [
                    {
                        "uid": str(material['uid']),
                        "name": material['name'],
                        "amount": material['amount'],
                        "unit": material['unit']
                    }
                    for material in step.target_materials.all().values('uid', 'name', 'amount', 'unit')
                ],
                "parameters": [
                    {
                        "uid": str(param['uid']),
                        "name": param['name'],
                        "value": param['value'],
                        "unit": param['unit'],
                        "error": param['error']
                    }
                    for param in step.parameter.all().values('uid', 'name', 'value', 'unit', 'error')
                ],
                "metadatas": [
                    {
                        "uid": str(meta['uid']),
                        "key": meta['key'],
                        "value": meta['value']
                    }
                    for meta in step.metadata.all().values('uid', 'key', 'value')
                ],
            }
            steps_data.append(step_data)

        parameters = {
            "step_number": len(steps_data),
            "experiment_uid": str(self.experiment.uid),
            "uid": str(self.uid),
            "steps": steps_data,
            "type": self.__class__.__name__,
        }

        # Execute the Cypher query
        try:
            output, meta = db.cypher_query(cypher_query, params=parameters)
            print("Neo4j FabricationWorkflow Query Output:", output)
        except Exception as e:
            print("Error executing Neo4j FabricationWorkflow query:", e)

        # ---------------------------------------------------------------------
        # Additional query to fetch the desired nodes and return them in the requested format
        # ---------------------------------------------------------------------
        result_query = """
        MATCH (n)
        WHERE n:Matter OR n:Manufacturing OR n:Measurement OR n:Parameter OR n:Property
        RETURN 
            CASE 
                WHEN n:Matter THEN 'EMMOMatter'
                WHEN n:Manufacturing THEN 'EMMOProcess'
                WHEN n:Measurement THEN 'EMMOProcess'
                WHEN n:Parameter THEN 'EMMOQuantity'
                WHEN n:Property THEN 'EMMOQuantity'
            END AS class,
            n.uid AS uid,
            CASE
                WHEN n.name IS NOT NULL THEN n.name
                WHEN n.value IS NOT NULL THEN toString(n.value)
                ELSE "N/A"
            END AS name
        """

        results, meta = db.cypher_query(result_query)

        output_list = []
        for row in results:
            output_list.append({
                "class": row[0],
                "uid": row[1],
                "name": row[2],
            })

        self.ontology_list = output_list
        self.add_to_ontology()



class Neo4jDataHandler(Neo4JHandler):
    def _save_to_neo4j(self):
        # Cypher query to merge Analysis and its Steps, including ordered relationships
        cypher_query = """
            // Merge the Analysis node
            MERGE (e:Experiment:Process {uid: $experiment_uid})
            MERGE (a:Process:DataProcessing {uid: $uid, type: $type})
            MERGE (e)-[:HAS_PART]->(a)
            WITH a, $steps AS steps, $experiment_uid AS experiment_uid
            
            // Iterate over each step
            UNWIND steps AS step
            CALL {
                // Create or merge AnalysisStep node
                WITH step, experiment_uid, a
                MERGE (as:DataProcessing {uid: step.uid})
                MERGE (a)-[:HAS_PART]->(as)
                SET as.technique = step.technique, as.order = step.order
                WITH as, step, experiment_uid
    
                // Associate Data Inputs
                CALL {
                WITH as, step, experiment_uid
                UNWIND step.data_inputs AS data_in
                    MERGE (di:Data {uid: data_in.uid})
                    SET di.data_type = data_in.data_type,
                        di.data_format = data_in.data_format,
                        di.link = data_in.link
                    MERGE (di)-[:IS_DATA_PROCESSING_INPUT]->(as)
                }
                WITH as, step, experiment_uid
    
                // Associate Quantity Inputs
                CALL {
                WITH as, step, experiment_uid
                UNWIND step.quantity_inputs AS qty_in
                    MERGE (qi:Property {uid: qty_in.uid})
                    SET qi.name = qty_in.name,
                        qi.value = qty_in.value,
                        qi.unit = qty_in.unit,
                        qi.error = qty_in.error
                    MERGE (qi)-[:IS_DATA_PROCESSING_INPUT]->(as)
                }
                WITH as, step, experiment_uid
    
                // Associate Parameters
                CALL {
                WITH as, step, experiment_uid
                UNWIND step.parameters AS param
                    MERGE (p:Quantity {uid: param.uid})
                    SET p.name = param.name,
                        p.value = param.value,
                        p.unit = param.unit,
                        p.error = param.error
                    MERGE (as)-[:HAS_PARAMETER]->(p)
                }
                WITH as, step, experiment_uid
    
                // Associate Data Results
                CALL {
                WITH as, step, experiment_uid
                UNWIND step.data_results AS data_res
                    MERGE (dr:Data {uid: data_res.uid})
                    SET dr.data_type = data_res.data_type,
                        dr.data_format = data_res.data_format,
                        dr.link = data_res.link
                    MERGE (as)-[:GENERATES_DATA]->(dr)
                }
                WITH as, step, experiment_uid
    
                // Associate Quantity Results
                CALL {
                WITH as, step, experiment_uid
                UNWIND step.quantity_results AS qty_res
                    MERGE (qr:Quantity {uid: qty_res.uid})
                    SET qr.name = qty_res.name,
                        qr.value = qty_res.value,
                        qr.unit = qty_res.unit,
                        qr.error = qty_res.error
                    MERGE (as)-[:GENERATES_QUANTITY]->(qr)
                }
                WITH as, step, experiment_uid
    
                // Associate Metadata
                CALL {
                WITH as, step, experiment_uid
                UNWIND step.metadatas AS meta
                    MERGE (m:Metadata {uid: meta.uid})
                    SET m.key = meta.key,
                        m.value = meta.value
                    MERGE (as)-[:HAS_METADATA]->(m)
                }
            }
            
            // After processing all steps, create ordered relationships between them
            WITH steps
            UNWIND range(0, size(steps) - 2) AS idx
                MATCH (current:AnalysisStep {uid: steps[idx].uid})
                MATCH (next:AnalysisStep {uid: steps[idx + 1].uid})
                MERGE (current)-[:FOLLOWED_BY]->(next)
        """

        # Prepare parameters
        steps_queryset = self.steps.all().order_by('order')
        steps_data = []
        for step in steps_queryset:
            step_data = {
                "uid": str(step.uid),  # Convert UUID to string
                "order": step.order,
                "technique": step.technique if step.technique else "",
                "data_inputs": [
                    {
                        "uid": str(data.uid),
                        "data_type": data.data_type,
                        "data_format": data.data_format,
                        "link": data.link
                    }
                    for data in step.data_inputs.all()
                ],
                "quantity_inputs": [
                    {
                        "uid": str(qty.uid),
                        "name": qty.name,
                        "value": qty.value,
                        "unit": qty.unit,
                        "error": qty.error
                    }
                    for qty in step.quantity_inputs.all()
                ],
                "parameters": [
                    {
                        "uid": str(param.uid),
                        "name": param.name,
                        "value": param.value,
                        "unit": param.unit,
                        "error": param.error
                    }
                    for param in step.parameter.all()
                ],
                "data_results": [
                    {
                        "uid": str(data.uid),
                        "data_type": data.data_type,
                        "data_format": data.data_format,
                        "link": data.link
                    }
                    for data in step.data_results.all()
                ],
                "quantity_results": [
                    {
                        "uid": str(qty.uid),
                        "name": qty.name,
                        "value": qty.value,
                        "unit": qty.unit,
                        "error": qty.error
                    }
                    for qty in step.quantity_results.all()
                ],
                "metadatas": [
                    {
                        "uid": str(meta.uid),
                        "key": meta.key,
                        "value": meta.value
                    }
                    for meta in step.metadata.all()
                ],
            }
            steps_data.append(step_data)

        parameters = {
            "uid": str(self.uid),
            "experiment_uid": str(self.experiment.uid) if self.experiment else "",
            "steps": steps_data,
            "type": self.__class__.__name__,
        }

        # Execute the Cypher query
        try:
            output, meta = db.cypher_query(cypher_query, params=parameters)
            print("Neo4j DataHandler (Analysis) Query Output:", output)
        except Exception as e:
            print("Error executing Neo4j Analysis query:", e)

        # ---------------------------------------------------------------------
        # Additional query to fetch the desired nodes and return them in the requested format
        # ---------------------------------------------------------------------
        result_query = """
        MATCH (n)
        WHERE n:Matter OR n:Manufacturing OR n:Measurement OR n:Parameter OR n:Property
        RETURN 
            CASE 
                WHEN n:Matter THEN 'EMMOMatter'
                WHEN n:Manufacturing THEN 'EMMOProcess'
                WHEN n:Measurement THEN 'EMMOProcess'
                WHEN n:Parameter THEN 'EMMOQuantity'
                WHEN n:Property THEN 'EMMOQuantity'
            END AS class,
            n.uid AS uid,
            CASE
                WHEN n.name IS NOT NULL THEN n.name
                WHEN n.value IS NOT NULL THEN toString(n.value)
                ELSE "N/A"
            END AS name
        """

        results, meta = db.cypher_query(result_query)

        output_list = []
        for row in results:
            output_list.append({
                "class": row[0],
                "uid": row[1],
                "name": row[2],
            })

        self.ontology_list = output_list
        self.add_to_ontology()


class Neo4jMeasurementHandler(Neo4JHandler):
    def _save_to_neo4j(self):
        # Ensure the Measurement instance is linked to an Experiment
        if not self.experiment:
            print("No associated Experiment found. Skipping Neo4j synchronization.")
            return []

        experiment_uid = str(self.experiment.uid)
        measurement_uid = str(self.uid)

        # Prepare the Cypher query
        cypher_query = """
        // Merge the Experiment node
        MERGE (e:Experiment {uid: $experiment_uid})
        
        // Merge the Measurement node
        MERGE (m:Measurement {uid: $measurement_uid, name: $measurement_method})
        MERGE (m)-[:HAS_PARAMETER]->(p1:Parameter {uid: apoc.create.uuid(), name: "temperature", value: $temperature, unit: $temperature_unit})
        MERGE (m)-[:HAS_PARAMETER]->(p2:Parameter {uid: apoc.create.uuid(), name: "pressure", value: $pressure, unit: $pressure_unit})
        MERGE (m)-[:HAS_METADATA]->(meta1:Metadata {uid: apoc.create.uuid(), type: "atmosphere", value: $atmosphere})
        MERGE (m)-[:HAS_METADATA]->(meta2:Metadata {uid: apoc.create.uuid(), type: "specimen", value: $specimen})
        MERGE (m)-[:HAS_METADATA]->(meta3:Metadata {uid: apoc.create.uuid(), type: "measurement_type", value: $measurement_type})
        
        SET m.measurement_method = $measurement_method,
            m.created_at = $created_at,
            m.updated_at = $updated_at
        
        MERGE (e)-[:HAS_MEASUREMENT]->(m)
        MERGE (e)-[:HAS_PART]->(m)
        RETURN m
        """

        parameters = {
            "experiment_uid": experiment_uid,
            "measurement_uid": measurement_uid,
            "measurement_method": self.measurement_method,
            "measurement_type": self.measurement_type,
            "specimen": self.specimen,
            "temperature": self.temperature,
            "temperature_unit": self.temperature_unit,
            "pressure": self.pressure,
            "pressure_unit": self.pressure_unit,
            "atmosphere": self.atmosphere,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        try:
            output, meta = db.cypher_query(cypher_query, params=parameters)
            print("Neo4j Measurement Query Output:", output)
        except Exception as e:
            print("Error executing Neo4j Measurement query:", e)

        # ---------------------------------------------------------------------
        # Additional query to fetch the desired nodes and return them in the requested format
        # ---------------------------------------------------------------------
        result_query = """
        MATCH (n)
        WHERE n:Matter OR n:Manufacturing OR n:Measurement OR n:Parameter OR n:Property
        RETURN 
            CASE 
                WHEN n:Matter THEN 'EMMOMatter'
                WHEN n:Manufacturing THEN 'EMMOProcess'
                WHEN n:Measurement THEN 'EMMOProcess'
                WHEN n:Parameter THEN 'EMMOQuantity'
                WHEN n:Property THEN 'EMMOQuantity'
            END AS class,
            n.uid AS uid,
            CASE
                WHEN n.name IS NOT NULL THEN n.name
                WHEN n.value IS NOT NULL THEN toString(n.value)
                ELSE "N/A"
            END AS name
        """

        results, meta = db.cypher_query(result_query)

        output_list = []
        for row in results:
            output_list.append({
                "class": row[0],
                "uid": row[1],
                "name": row[2],
            })

        self.ontology_list = output_list
        self.add_to_ontology()



import os
import json
import csv
from neomodel import db

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime, DateTimeProperty, DateProperty, Date)):
            return obj.isoformat()
        return super().default(obj)

class Neo4jDataRetrievalHandler:
    """
    A handler that retrieves all data related to a given Experiment from Neo4j.
    It can return the data in JSON format or write CSV files to disk.
    """

    def get_experiment_data(self, experiment_uid, output_format='json', base_path='.'):
        """
        Main entry point to retrieve data for a given experiment UID.

        :param experiment_uid: (str) The UID of the Experiment node.
        :param output_format: (str) 'json' or 'csv'
        :param base_path: (str) Path where CSV files will be saved if output_format='csv'.
        :return:
            - If 'json', returns a JSON string with the entire data.
            - If 'csv', writes multiple CSV files to `base_path` and returns a
              dict describing the written files.
        """
        # 1) Retrieve basic experiment node info
        print("Fetching experiment data...")
        experiment_data = self._fetch_experiment(experiment_uid)
        print("Experiment data:", experiment_data)

        # 2) Retrieve organizational data (Metadata attached directly to experiment)
        organizational_data = self._fetch_organizational_data(experiment_uid)

        # 3) Retrieve measurement data
        measurement_data = self._fetch_measurements(experiment_uid)

        # 4) Retrieve manufacturing (synthesis) data
        synthesis_data = self._fetch_synthesis(experiment_uid)

        # 5) Retrieve data processing (analysis, etc.) steps
        analysis_data = self._fetch_data_processing(experiment_uid)

        # Combine everything in a single Python dictionary
        result = {
            "experiment": experiment_data,              # Basic experiment node
            "organizational_data": organizational_data, # List of metadata nodes
            "measurements": measurement_data,           # List of measurement nodes
            "fabrication_workflow": synthesis_data,     # Synthesis steps
            "data_processing": analysis_data            # Analysis steps
        }

        if output_format == 'json':
            return json.dumps(result, cls= DateTimeEncoder, indent=2)
        elif output_format == 'csv':
            return self._write_csv_files(result, base_path)
        else:
            raise ValueError("Output format must be either 'json' or 'csv'.")

    # --------------------------------------------------------------------------
    #                             INTERNAL METHODS
    # --------------------------------------------------------------------------

    def _fetch_experiment(self, experiment_uid):
        """
        Fetches basic info of the Experiment node.
        Adjust the return structure to your liking (e.g., collecting more properties).
        """
        query = """
        MATCH (e:Experiment {uid: $uid})
        RETURN e.uid AS uid
        """
        results, meta = db.cypher_query(query, {"uid": experiment_uid})
        print("res",results)
        if not results:
            return {}
        row = results[0]
        return {
            "uid": row[0]
        }

    def _fetch_organizational_data(self, experiment_uid):
        """
        Fetch all `Metadata` nodes attached directly to the Experiment.
        This corresponds to your organizational data (authors, publication, etc.).
        """
        query = """
        MATCH (e:Experiment {uid: $uid})-[:HAS_METADATA]->(m:Metadata)
        RETURN m.uid AS uid, m.value AS value, labels(m) AS labels
        ORDER BY m.uid
        """
        results, meta = db.cypher_query(query, {"uid": experiment_uid})
        data = []
        for row in results:
            data.append({
                "uid": row[0],
                "value": row[1],
                "labels": row[2]  # e.g. ["Metadata","Author"] or ["Metadata","Publication"], etc.
            })
        return data

    def _fetch_measurements(self, experiment_uid):
        """
        Fetch `Measurement` nodes attached to the Experiment.
        """
        query = """
        MATCH (e:Experiment {uid: $uid})-[:HAS_MEASUREMENT]->(m:Measurement)
        RETURN m.uid AS uid,
               m.measurement_method AS measurement_method,
               m.measurement_type AS measurement_type,
               m.specimen AS specimen,
               m.temperature AS temperature,
               m.temperature_unit AS temperature_unit,
               m.pressure AS pressure,
               m.pressure_unit AS pressure_unit,
               m.atmosphere AS atmosphere,
               m.created_at AS created_at,
               m.updated_at AS updated_at
        ORDER BY m.uid
        """
        results, meta = db.cypher_query(query, {"uid": experiment_uid})
        data = []
        for row in results:
            data.append({
                "uid": row[0],
                "measurement_method": row[1],
                "measurement_type": row[2],
                "specimen": row[3],
                "temperature": row[4],
                "temperature_unit": row[5],
                "pressure": row[6],
                "pressure_unit": row[7],
                "atmosphere": row[8],
                "created_at": row[9],
                "updated_at": row[10],
            })
        return data

    def _fetch_synthesis(self, experiment_uid):
        """
        Retrieve the manufacturing processes (FabricationWorkflow).
        This can be as detailed as you like, e.g. also fetch step details, parameters, etc.
        Below is a simplified example returning nodes and basic relationship structure.
        """
        query = """
        // For top-level Synthesis processes
        MATCH (e:Experiment {uid: $uid})-[:HAS_PART]->(s:Manufacturing:Process)
        RETURN s.uid AS synthesis_uid, s.type AS type
        """
        results, meta = db.cypher_query(query, {"uid": experiment_uid})
        synthesis_list = []
        for row in results:
            synthesis_uid = row[0]
            synthesis_list.append({
                "uid": synthesis_uid,
                "type": row[1],
                "steps": self._fetch_synthesis_steps(synthesis_uid)
            })
        return synthesis_list

    def _fetch_synthesis_steps(self, synthesis_uid):
        """
        Example of retrieving child steps from a Synthesis node.
        """
        query = """
        MATCH (s:Manufacturing:Process {uid: $uid})-[:HAS_PART]->(step:Manufacturing)
        OPTIONAL MATCH (step)-[:HAS_PARAMETER]->(param:Parameter)
        RETURN step.uid AS step_uid,
               step.name AS step_name,
               step.order AS step_order,
               collect(distinct param) AS parameters
        ORDER BY step.order
        """
        results, meta = db.cypher_query(query, {"uid": synthesis_uid})
        step_data = []
        for row in results:
            step_params = []
            if row[3]:  # param objects
                for param_node in row[3]:
                    param_dict = {
                        "uid": param_node["uid"],
                        "name": param_node.get("name"),
                        "value": param_node.get("value"),
                        "unit": param_node.get("unit"),
                        "error": param_node.get("error")
                    }
                    step_params.append(param_dict)

            step_data.append({
                "uid": row[0],
                "name": row[1],
                "order": row[2],
                "parameters": step_params
            })
        return step_data

    def _fetch_data_processing(self, experiment_uid):
        """
        Retrieves data/analysis steps (DataProcessing).
        """
        query = """
        MATCH (e:Experiment {uid: $uid})-[:HAS_PART]->(dp:DataProcessing)
        RETURN dp.uid AS dp_uid, dp.type AS type
        """
        results, meta = db.cypher_query(query, {"uid": experiment_uid})
        data_processes = []
        for row in results:
            dp_uid = row[0]
            data_processes.append({
                "uid": dp_uid,
                "type": row[1],
                "steps": self._fetch_data_processing_steps(dp_uid)
            })
        return data_processes

    def _fetch_data_processing_steps(self, dp_uid):
        """
        Example of retrieving child steps for a data/analysis process.
        You can expand this to fetch data inputs, data outputs, parameters, etc.
        """
        query = """
        MATCH (dp:DataProcessing {uid: $uid})-[:HAS_PART]->(child:DataProcessing)
        OPTIONAL MATCH (child)-[:HAS_PARAMETER]->(param:Quantity)
        RETURN child.uid AS step_uid,
               child.technique AS step_technique,
               child.order AS step_order,
               collect(distinct param) AS parameters
        ORDER BY child.order
        """
        results, meta = db.cypher_query(query, {"uid": dp_uid})
        step_data = []
        for row in results:
            params = []
            if row[3]:
                for param_node in row[3]:
                    params.append({
                        "uid": param_node["uid"],
                        "name": param_node.get("name"),
                        "value": param_node.get("value"),
                        "unit": param_node.get("unit"),
                        "error": param_node.get("error")
                    })
            step_data.append({
                "uid": row[0],
                "technique": row[1],
                "order": row[2],
                "parameters": params
            })
        return step_data

    # --------------------------------------------------------------------------
    #                      CSV WRITING LOGIC (SEPARATE FILES)
    # --------------------------------------------------------------------------
    def _write_csv_files(self, data_dict, base_path):
        """
        Writes separate CSV files for each major section of data in `data_dict`.
        Returns a dict containing the file paths that were generated.

        :param data_dict: The combined dictionary of experiment data.
        :param base_path: Directory where CSV files should be saved.
        :return: A dict with file labels -> paths (str).
        """

        # Ensure the base_path directory exists
        if not os.path.isdir(base_path):
            os.makedirs(base_path, exist_ok=True)

        output_files = {}

        # 1) Experiment data to experiment.csv
        exp_file = os.path.join(base_path, 'experiment.csv')
        self._write_experiment_csv(exp_file, data_dict["experiment"])
        output_files["experiment"] = exp_file

        # 2) Organizational data to organizational_data.csv
        org_file = os.path.join(base_path, 'organizational_data.csv')
        self._write_organizational_data_csv(org_file, data_dict["organizational_data"])
        output_files["organizational_data"] = org_file

        # 3) Measurements to measurements.csv
        meas_file = os.path.join(base_path, 'measurements.csv')
        self._write_measurements_csv(meas_file, data_dict["measurements"])
        output_files["measurements"] = meas_file

        # 4) Fabrication workflow (synthesis) to fabrication_workflow.csv
        #    and separate steps to fabrication_steps.csv
        fab_file = os.path.join(base_path, 'fabrication_workflow.csv')
        fab_steps_file = os.path.join(base_path, 'fabrication_steps.csv')
        self._write_fabrication_csv(fab_file, fab_steps_file, data_dict["fabrication_workflow"])
        output_files["fabrication_workflow"] = fab_file
        output_files["fabrication_steps"] = fab_steps_file

        # 5) Data processing to data_processing.csv
        #    and separate steps to data_processing_steps.csv
        dp_file = os.path.join(base_path, 'data_processing.csv')
        dp_steps_file = os.path.join(base_path, 'data_processing_steps.csv')
        self._write_data_processing_csv(dp_file, dp_steps_file, data_dict["data_processing"])
        output_files["data_processing"] = dp_file
        output_files["data_processing_steps"] = dp_steps_file

        return output_files

    def _write_experiment_csv(self, filepath, experiment_data):
        """
        Writes the top-level Experiment data to CSV.
        """
        fieldnames = ["uid"]
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            # If experiment_data is empty, do nothing
            if experiment_data:
                writer.writerow(experiment_data)

    def _write_organizational_data_csv(self, filepath, org_data):
        """
        Writes organizational (metadata) entries to CSV.
        """
        fieldnames = ["uid", "value", "labels"]
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in org_data:
                # Convert labels list to a string or join them with commas
                row = {
                    "uid": item["uid"],
                    "value": item["value"],
                    "labels": ",".join(item["labels"]) if item["labels"] else ""
                }
                writer.writerow(row)

    def _write_measurements_csv(self, filepath, measurements):
        """
        Writes measurement data to CSV.
        """
        fieldnames = [
            "uid",
            "measurement_method",
            "measurement_type",
            "specimen",
            "temperature",
            "temperature_unit",
            "pressure",
            "pressure_unit",
            "atmosphere",
            "created_at",
            "updated_at"
        ]
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in measurements:
                writer.writerow(item)

    def _write_fabrication_csv(self, fab_file, fab_steps_file, fabrication_data):
        """
        Writes top-level fabrication workflow CSV and steps to a separate file.
        """
        # Write top-level data
        fab_fieldnames = ["uid", "type"]
        with open(fab_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fab_fieldnames)
            writer.writeheader()
            for fab_item in fabrication_data:
                writer.writerow({
                    "uid": fab_item["uid"],
                    "type": fab_item["type"],
                })

        # Write steps (flatten each "steps" list for each top-level item)
        fab_steps_fieldnames = ["parent_uid", "step_uid", "step_name", "step_order", "param_uid", "param_name", "param_value", "param_unit", "param_error"]
        with open(fab_steps_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fab_steps_fieldnames)
            writer.writeheader()

            for fab_item in fabrication_data:
                parent_uid = fab_item["uid"]
                for step in fab_item["steps"]:
                    if not step["parameters"]:
                        # If no parameters, still write one row indicating the step
                        writer.writerow({
                            "parent_uid": parent_uid,
                            "step_uid": step["uid"],
                            "step_name": step["name"],
                            "step_order": step["order"],
                            "param_uid": "",
                            "param_name": "",
                            "param_value": "",
                            "param_unit": "",
                            "param_error": ""
                        })
                    else:
                        # If there are parameters, write one row per parameter
                        for param in step["parameters"]:
                            writer.writerow({
                                "parent_uid": parent_uid,
                                "step_uid": step["uid"],
                                "step_name": step["name"],
                                "step_order": step["order"],
                                "param_uid": param["uid"],
                                "param_name": param["name"],
                                "param_value": param["value"],
                                "param_unit": param["unit"],
                                "param_error": param["error"]
                            })

    def _write_data_processing_csv(self, dp_file, dp_steps_file, data_processing_data):
        """
        Writes top-level data processing CSV and steps to a separate file.
        """
        # Write top-level data
        dp_fieldnames = ["uid", "type"]
        with open(dp_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=dp_fieldnames)
            writer.writeheader()
            for dp_item in data_processing_data:
                writer.writerow({
                    "uid": dp_item["uid"],
                    "type": dp_item["type"],
                })

        # Write child steps
        dp_steps_fieldnames = ["parent_uid", "step_uid", "technique", "order", "param_uid", "param_name", "param_value", "param_unit", "param_error"]
        with open(dp_steps_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=dp_steps_fieldnames)
            writer.writeheader()

            for dp_item in data_processing_data:
                parent_uid = dp_item["uid"]
                for step in dp_item["steps"]:
                    if not step["parameters"]:
                        # If no parameters, still write one row indicating the step
                        writer.writerow({
                            "parent_uid": parent_uid,
                            "step_uid": step["uid"],
                            "technique": step["technique"],
                            "order": step["order"],
                            "param_uid": "",
                            "param_name": "",
                            "param_value": "",
                            "param_unit": "",
                            "param_error": ""
                        })
                    else:
                        # If there are parameters, write one row per parameter
                        for param in step["parameters"]:
                            writer.writerow({
                                "parent_uid": parent_uid,
                                "step_uid": step["uid"],
                                "technique": step["technique"],
                                "order": step["order"],
                                "param_uid": param["uid"],
                                "param_name": param["name"],
                                "param_value": param["value"],
                                "param_unit": param["unit"],
                                "param_error": param["error"]
                            })


class SearchHandler:
    """
    A class that handles advanced experiment filtering logic
    by multiple criteria: materials, techniques, parameters, properties, metadata, etc.

    Example search_instructions dict structure:
    {
        "materials": ["A", "B"],
        "techniques": ["Technique1", "Technique2"],
        "parameters": ["ParamName1", "ParamName2"],
        "properties": ["PropertyName1", "PropertyName2"],
        "metadata": [
            {"key": "some_key", "value": "some_value"},
            ...
        ]
        // Potentially other fields
    }
    """

    def search_experiments(self, search_instructions: dict) -> list:
        """
        Takes a dictionary of search instructions and returns
        a list of matching Experiment objects.

        You can define the logic to combine multiple criteria with either 'AND' or 'OR' logic.
        Below is an example that uses 'AND' across categories, but 'OR' within each category.
        """

        return []