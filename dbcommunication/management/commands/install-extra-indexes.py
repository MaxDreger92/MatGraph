from django.core.management.base import BaseCommand
from neomodel import db


# indexes on node properties are created by django_neomodel's install-labels management command.
# this command installs other relevant indexes (esp. on relationship properties)

class Command(BaseCommand):
    help = 'Install important neo4j indexes that are not installed by install_labels'

    def handle(self, *args, **options):

        db.cypher_query('''
            CREATE INDEX skill_similarity IF NOT EXISTS FOR ()-[r:SIMILAR]-() ON (r.similarity)
        ''')

        db.cypher_query('''
            CREATE INDEX requires_relevance IF NOT EXISTS FOR ()-[r:REQUIRES]-() ON (r.relevance)
        ''')

        db.cypher_query('''
            CREATE INDEX relevant_for_relevance IF NOT EXISTS FOR ()-[r:RELEVANT_FOR]-() ON (r.relevance)
        ''')

        db.cypher_query('''
            CREATE INDEX skill_level IF NOT EXISTS FOR ()-[r:HAS_SKILL]-() ON (r.level)
        ''')
