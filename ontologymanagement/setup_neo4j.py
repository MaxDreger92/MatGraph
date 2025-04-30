import os
from dotenv import load_dotenv
from neomodel import db, config
from graphutils.config import EMBEDDING_DIMENSIONS
from importing.NodeAttributeExtraction.embeddings import setup_embeddings
from mat2devplatform import settings
from matgraph.models.ontology import EMMOMatter, EMMOProcess
from ontologymanagement.ontologyManager import OntologyManager


TYPE_MAPPER = {
    "LabelEmbeddings": "label-embeddings",
    "MatterAttributeEmbedding": "matter-attribute-embeddings",
    "ProcessAttributeEmbedding": "process-attribute-embeddings",
    "QuantityAttributeEmbedding": "quantity-attribute-embeddings",
    "MatterEmbedding": "matter-embeddings",
    "ProcessEmbedding": "process-embeddings",
    "QuantityEmbedding": "quantity-embeddings",
}


def setup_environment():
    """Setup environment variables and Django settings."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    load_dotenv()
    config.DATABASE_URL = os.getenv('NEOMODEL_NEO4J_BOLT_URL')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mat2devplatform.settings")
    print(f"Connected to Neo4j: {config.DATABASE_URL}")


def setup_ontology():
    """Import ontologies if needed."""
    ontology_folder = settings.BASE_DIR / "Ontology"
    ontology_manager = OntologyManager(ontology_folder)

    # Uncomment if ontology import/update is needed
    # ontology_manager.update_ontology("quantities.owl")
    ontology_manager.import_to_neo4j("quantities.owl")
    # ontology_manager.update_ontology("matter.owl")
    ontology_manager.import_to_neo4j("matter.owl")
    # ontology_manager.update_ontology("manufacturing.owl")
    ontology_manager.import_to_neo4j("manufacturing.owl")


def add_vector_index(label: str):
    """Add a vector index for a given label."""
    if label not in TYPE_MAPPER:
        raise ValueError(f"Unknown label '{label}' for vector indexing.")

    query = f"""
        CREATE VECTOR INDEX `{TYPE_MAPPER[label]}` IF NOT EXISTS
        FOR (m:{label})
        ON m.vector
        OPTIONS {{
            indexConfig: {{
                `vector.dimensions`: {EMBEDDING_DIMENSIONS},
                `vector.similarity_function`: 'cosine'
            }}
        }}
    """
    db.cypher_query(query)
    print(f"Vector index created (if not exists) for {label}")


def add_all_vector_indices():
    """Add all necessary vector indices."""
    labels = [
        "MatterAttributeEmbedding",
        "ProcessAttributeEmbedding",
        "QuantityAttributeEmbedding",
        "MatterEmbedding",
        "ProcessEmbedding",
        "QuantityEmbedding",
    ]
    for label in labels:
        add_vector_index(label)


def clean_duplicate_embeddings():
    """Clean up duplicate embeddings."""
    query = """
        MATCH (n:ModelEmbedding)-[:FOR]-(o)
        WHERE toLower(n.input) <> toLower(o.name)
        WITH toLower(n.input) AS normalizedInput, collect(n) AS nodes
        WHERE size(nodes) > 1
        UNWIND tail(nodes) AS duplicate
        DETACH DELETE duplicate
    """
    db.cypher_query(query)
    print("Duplicate embeddings cleaned up.")


def test_search():
    """Test the vector search functionality."""
    try:
        results = EMMOProcess.nodes.get_by_string(
            string="Fuel Cell",
            limit=15,
            include_similarity=True
        )
        print("Search Results:", results)
    except Exception as e:
        print("Search failed:", str(e))

def check_db():
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
        return True
    else:
        return False


def run_setup():
    """Full Neo4j setup routine."""
    if not check_db():
        setup_embeddings()
        setup_environment()
        setup_ontology()
        add_all_vector_indices()
        clean_duplicate_embeddings()
        test_search()


if __name__ == "__main__":
    run_setup()
