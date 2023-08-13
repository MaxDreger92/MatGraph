from importlib import import_module

from django.core.management.base import BaseCommand, CommandError

from dbcommunication.ai.createEmbeddings import get_embeddings_for_model


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
            # get_embeddings_for_model(
            #     self,
            #     Model=Model,
            #     fetch_properties= ['name', 'description'],
            #     combine_func=lambda s: ' '.join([s['name'], s['description']])
            #     # add other parameters here...
            # )
            self.stdout.write(self.style.SUCCESS('Successfully generated normal embeddings.'))
            get_embeddings_for_model(
                self,
                Model=Model,
                fetch_properties= ['name'],
                combine_func=lambda s: s['name'],

                # add other parameters here...
            )
            self.stdout.write(self.style.SUCCESS('Successfully generated light embeddings.'))
            get_embeddings_for_model(
                self,
                Model=Model,
                fetch_properties= ['name'],
                combine_func=lambda s: s['name'],
                unwind_alternative_labels= False
                # add other parameters here...
            )
            self.stdout.write(self.style.SUCCESS('Successfully generated ultra light embeddings.'))
        except Exception as e:
            raise CommandError('Failed to generate embeddings: ' + str(e))
