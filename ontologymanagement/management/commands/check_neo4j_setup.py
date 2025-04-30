from django.core.management.base import BaseCommand
from neomodel import db

class Command(BaseCommand):
    help = "Check if Neo4j setup is needed."

    def handle(self, *args, **kwargs):
        query = "show indexes YIELD name RETURN name"
        results, _ = db.cypher_query(query)
        index_names = {name for (name,) in results}

        needed_indices = {
            "matter-attribute-embeddings",
            "process-attribute-embeddings",
            "quantity-attribute-embeddings",
            "matter-embeddings",
            "process-embeddings",
            "quantity-embeddings",
        }

        if needed_indices.issubset(index_names):
            self.stdout.write("True")
        else:
            self.stdout.write("False")
