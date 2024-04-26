from django.core.management.base import BaseCommand

from skills.ai.embeddings import get_embeddings_for_vocations


class Command(BaseCommand):
    help = 'Get embeddings for vocational trainings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--resume',
            action='store_true',
            help='only get missing embeddings'
        )

    def handle(self, *args, **options):
        get_embeddings_for_vocations(self, resume=options['resume'])
