from django.core.management import BaseCommand

from skills.ai.similarity import update_similarities


class Command(BaseCommand):
    help = 'Calculate skill similarities based on embeddings'

    def handle(self, *args, **options):
        update_similarities(self)
