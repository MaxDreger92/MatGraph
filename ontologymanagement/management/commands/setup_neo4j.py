from django.core.management import BaseCommand

from ontologymanagement.setup_neo4j import run_setup


class Command(BaseCommand):
    help = "Setup the Neo4j database (vector indices, ontologies, cleanups)"

    def handle(self, *args, **kwargs):
        run_setup()