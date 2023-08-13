from importlib import import_module

from dbcommunication.ai.createEmbeddings import get_embeddings_for_model
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
class Command(BaseCommand):
    help = 'Generate and store embeddings for ontology nodes'

    def add_arguments(self, parser):
        # here you can add any command line arguments you need
        # for example, you might need to specify the model name:
        parser.add_argument('model_name', type=str)

    def handle(self, *args, **options):
        # this method will be called when you run the command
        model_name = options['model_name']
        try:
            ModelModule = import_module('matgraph.models.ontology')
            Model = getattr(ModelModule, model_name)
            # You would need to provide necessary parameters for the function
            get_embeddings_for_model(
                self,
                Model=Model,
                fetch_properties= ['name', 'description'],
                combine_func=lambda s: ' '.join([s['name'], s['description']])
                # add other parameters here...
            )
            self.stdout.write(self.style.SUCCESS('Successfully generated embeddings.'))
        except Exception as e:
            raise CommandError('Failed to generate embeddings: ' + str(e))
