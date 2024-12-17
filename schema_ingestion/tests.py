from django.test import TestCase

# Create your tests here.
#Test for models .save() method to directly save data to neo4j database

from schema_ingestion.models import Synthesis, Analysis, Preprocessing, Experiment, OrganizationalData



class SynthesisTestCase(TestCase):
    # Test for Synthesis model save method to save data to neo4j database
    # The test creates a new Synthesis object and saves it to the database
    #
    # class SynthesisStep(Step):
    #     precursor_materials = models.ManyToManyField(Material, related_name="s_precursors", blank=True)
    #     technique = models.ForeignKey(Technique, on_delete=models.CASCADE)
    #     parameter = models.ManyToManyField(Metadata, related_name="s_parameters")
    #     target_materials = models.ManyToManyField(Material, related_name="s_targets")
    #     metadata = models.ManyToManyField(Metadata, related_name="s_metadata")
    #
    #
    # class Synthesis(models.Model):
    #     synthesis_steps = models.ManyToManyField(SynthesisStep, related_name="steps")

    def test_synthesis_save(self):
        synthesis = Synthesis()
        synthesis.save()
        self.assertEqual(synthesis.pk, 1)

class AnalysisTestCase(TestCase):