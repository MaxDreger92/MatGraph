from django.test import TestCase

# Create your tests here.
# manufacturing/tests.py

from django.test import TestCase
from unittest.mock import patch
from uuid import uuid4

from schema_ingestion.models import (
    Synthesis,
    SynthesisStep,
    Technique,
    Material,
    Quantity,
    Metadata,
)

class SynthesisModelTest(TestCase):
    @patch('schema_ingestion.models.db.cypher_query', autospec=True)
    def test_synthesis_save_inserts_into_neo4j(self, mock_execute_query):
        """
        Test that saving a Synthesis instance correctly triggers a Neo4j query
        with the expected Cypher and parameters.
        """
        # Create related Technique
        technique = Technique.objects.create(
            uid=uuid4(),
            name="Chemical Vapor Deposition",
            description="CVD technique"
        )

        # Create precursor and target Materials
        precursor_material = Material.objects.create(
            uid=uuid4(),
            name="Material A",
            amount=10.0,
            unit="g"
        )
        target_material = Material.objects.create(
            uid=uuid4(),
            name="Material B",
            amount=5.0,
            unit="g"
        )

        # Create Parameters
        parameter = Quantity.objects.create(
            uid=uuid4(),
            name="Temperature",
            value="500",
            unit="C",
            error=None  # Assuming 'error' is optional
        )

        # Create Metadata
        metadata = Metadata.objects.create(
            uid=uuid4(),
            key="Batch Size",
            value="100 units"
        )

        # Create SynthesisStep
        synthesis_step = SynthesisStep.objects.create(
            uid=uuid4(),
            technique=technique,
            order=1
        )
        synthesis_step.precursor_materials.add(precursor_material)
        synthesis_step.target_materials.add(target_material)
        synthesis_step.parameter.add(parameter)
        synthesis_step.metadata.add(metadata)

        # Create Synthesis and associate steps
        synthesis = Synthesis.objects.create(
            uid=uuid4()
        )
        synthesis.synthesis_steps.add(synthesis_step)

        # Save Synthesis (triggers _save_to_neo4j)
        synthesis.save()

        # Assert that execute_query was called once
        self.assertEqual(mock_execute_query.call_count, 2)

        # Retrieve the call arguments
        called_query, called_params = mock_execute_query.call_args
        print(called_query)
        print(called_params)

        # Verify the Cypher query contains expected snippets
        self.assertIn("MERGE (s:Synthesis {uid: $synthesis_uid})", called_query[0])
        self.assertIn("MERGE (ss:SynthesisStep {uid: step.uid})", called_query[0])
        self.assertIn("MERGE (current)-[:FOLLOWED_BY]->(next)", called_query[0])

        # Verify that the parameters contain the correct synthesis UID and steps
        expected_parameters = {
            'synthesis_uid': str(synthesis.uid),
            'steps': [
                {
                    'uid': str(synthesis_step.uid),
                    'order': synthesis_step.order,
                    'technique_id': str(technique.uid) if technique.uid else None,
                    'technique': technique.name,
                    'precursor_materials': [
                        {
                            'uid': str(precursor_material.uid),
                            'name': precursor_material.name,
                            'amount': precursor_material.amount,
                            'unit': precursor_material.unit
                        }
                    ],
                    'target_materials': [
                        {
                            'uid': str(target_material.uid),
                            'name': target_material.name,
                            'amount': target_material.amount,
                            'unit': target_material.unit
                        }
                    ],
                    'parameters': [
                        {
                            'uid': str(parameter.uid),
                            'name': parameter.name,
                            'value': float(parameter.value),
                            'unit': parameter.unit,
                            'error': parameter.error
                        }
                    ],
                    'metadatas': [
                        {
                            'uid': str(metadata.uid),
                            'key': metadata.key,
                            'value': metadata.value
                        }
                    ]
                }
            ]
        }
        print(called_params)
        print(expected_parameters)
        self.assertEqual(called_params['params'], expected_parameters)

    @patch('schema_ingestion.models.db.cypher_query', autospec=True)
    def test_synthesis_save_handles_missing_optional_fields(self, mock_execute_query):
        """
        Test that saving a Synthesis instance correctly handles missing optional fields
        (e.g., 'error' in Parameter, 'amount' in Material).
        """
        # Create related Technique
        technique = Technique.objects.create(
            uid=uuid4(),
            name="Plasma Processing",
            description="Plasma-based technique"
        )

        # Create precursor and target Materials with missing 'amount' and 'unit'
        precursor_material = Material.objects.create(
            uid=uuid4(),
            name="Material C",
            amount=None,  # Assuming 'amount' can be null
            unit=None      # Assuming 'unit' can be null
        )
        target_material = Material.objects.create(
            uid=uuid4(),
            name="Material D",
            amount=7.5,
            unit="g"
        )

        # Create Parameters with 'error' as None
        parameter = Quantity.objects.create(
            uid=uuid4(),
            name="Pressure",
            value="1",
            unit="atm",     # Assuming 'unit' can be null
            error=None
        )
        parameter = Quantity.objects.create(
            uid=uuid4(),
            name="Temperature",
            value="300",
            unit="K",
            error=None
        )

        # Create Metadata
        metadata = Metadata.objects.create(
            uid=uuid4(),
            key="Instrument",
            value="Microscope"
        )

        # Create SynthesisStep
        synthesis_step = SynthesisStep.objects.create(
            uid=uuid4(),
            technique=technique,
            order=2
        )
        synthesis_step.precursor_materials.add(precursor_material)
        synthesis_step.target_materials.add(target_material)
        synthesis_step.parameter.add(parameter)
        synthesis_step.metadata.add(metadata)

        # Create Synthesis and associate steps
        synthesis = Synthesis.objects.create(
            uid=uuid4()
        )
        synthesis.synthesis_steps.add(synthesis_step)

        # Save Synthesis (triggers _save_to_neo4j)
        synthesis.save()

        # Assert that execute_query was called once
        self.assertEqual(mock_execute_query.call_count, 2)

        # Retrieve the call arguments
        called_query, called_params = mock_execute_query.call_args

        # Verify that optional fields are handled correctly in parameters
        expected_parameters = {
            'synthesis_uid': str(synthesis.uid),
            'steps': [
                {
                    'uid': str(synthesis_step.uid),
                    'technique': technique.name,
                    'order': synthesis_step.order,
                    'precursor_materials': [
                        {
                            'uid': str(precursor_material.uid),
                            'name': precursor_material.name,
                            'amount': precursor_material.amount,  # None
                            'unit': precursor_material.unit       # None
                        }
                    ],
                    'target_materials': [
                        {
                            'uid': str(target_material.uid),
                            'name': target_material.name,
                            'amount': target_material.amount,
                            'unit': target_material.unit
                        }
                    ],
                    'parameters': [
                        {
                            'uid': str(parameter.uid),
                            'name': parameter.name,
                            'value': parameter.value,
                            'unit': parameter.unit,    # None
                            'error': parameter.error   # None
                        }
                    ],
                    'metadatas': [
                        {
                            'uid': str(metadata.uid),
                            'key': metadata.key,
                            'value': metadata.value
                        }
                    ]
                }
            ]
        }

        self.assertEqual(called_params['params'], expected_parameters)
