from django.core.management.base import BaseCommand

from dbcommunication.ai.embeddings import get_embeddings_for_ontology


class Command(BaseCommand):
    help = 'Get embeddings for all ontology branches'

    def add_arguments(self, parser):
        parser.add_argument(
            '--resume',
            action='store_true',
            help='only get missing embeddings'
        )

    def handle(self, *args, **options):
        get_embeddings_for_ontology(self, resume=options['resume'])