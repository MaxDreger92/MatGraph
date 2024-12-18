from neomodel import db


class Neo4jFabricationWorkflowHandler:
    def _save_to_neo4j(self):
        # Cypher query to merge Synthesis and its Steps, including ordered relationships
        cypher_query = """
    // Merge the Synthesis node
    MERGE (s:Manufacturing {uid: $synthesis_uid})
    WITH s, $steps AS steps, $experiment_uid AS experiment_uid
    
    // Iterate over each step
    UNWIND steps AS step
    CALL {
        // Create or merge Manufacturing node
        WITH step, experiment_uid, s
        CREATE (ss:Manufacturing {uid: step.uid})
        MERGE (s)-[:HAS_PART]->(ss)
        SET ss.name = step.technique, ss.order = step.order
        WITH *
    
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
        steps_queryset = self.synthesis_steps.all().order_by('order')
        steps_data = []
        for step in steps_queryset:
            step_data = {

                "uid": str(step.uid),  # Convert UUID to string
                "order": step.order,
                "technique_id": str(step.technique.uid) if step.technique else None,  # Convert UUID to string
                'technique': step.technique.name if step.technique else None,
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
            "synthesis_uid": str(self.uid),
            "steps": steps_data,
        }
        output = db.cypher_query(cypher_query, params=parameters)