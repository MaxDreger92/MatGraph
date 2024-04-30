import os

import pandas as pd
from dotenv import load_dotenv
from neomodel import db
from pandarallel import pandarallel

from graphutils.config import EMBEDDING_FETCHING_PROCESSES
from graphutils.embeddings import request_embedding
from matgraph.models.ontology import EMMOMatter, EMMOProcess, EMMOQuantity


def build_cypher_query(Model, fetch_properties, fetch_filter='', unwind_alternative_labels=False, id_property='uid'):
    """
    This function builds a Cypher query for fetching data from a Neo4j graph database.

    :param Model: The Django model for which data is to be fetched
    :param fetch_properties: The properties of the model to be fetched
    :param fetch_filter: The filter condition for the query
    :param unwind_alternative_labels: Boolean flag indicating whether to unwind alternative labels
    :param id_property: The id property of the model (default 'uid')
    :return: Cypher query as a string
    """
    query = f'MATCH (n:{Model.__label__}) '
    if unwind_alternative_labels:
        query += f'OPTIONAL MATCH (n:{Model.__label__})-[:HAS_LABEL]-(a:AlternativeLabel) '
    if fetch_filter:
        fetch_filter += ' AND COALESCE(n.disable_embedding, false)=false '
    if fetch_filter:
        query += f'WHERE {fetch_filter} '
    query += f'RETURN DISTINCT n.{id_property} as uid, '+', '.join([f'n.{prop} as {prop}' for prop in fetch_properties])
    if unwind_alternative_labels:
        fetch_properties.append('alternative_labels')
        query += ', collect(a.label) as alternative_labels'
    # query += ' Limit 1'
    return query

def fetch_data(query, db, required_properties, fetch_properties, id_property):
    """
    Fetches data from a Neo4j database using the provided Cypher query.

    :param query: The Cypher query to be executed
    :param db: The database connection object
    :param required_properties: The properties that are required for each row of the fetched data
    :param fetch_properties: The properties to fetch for each row of data
    :param id_property: The id property of the model
    :return: DataFrame containing fetched data, total rows, and processable rows
    """
    rows, meta = db.cypher_query(query)
    df_all = pd.DataFrame(rows, columns=[id_property] + fetch_properties )
    total = len(df_all.index)
    df_all = df_all.dropna(subset=required_properties)
    processable = len(df_all.index)
    return df_all, total, processable

def apply_combine_func(df_all, combine_func, fetch_properties, unwind_alternative_labels):
    """
    Applies a function to combine data in a DataFrame.

    :param df_all: The DataFrame to apply the function on
    :param combine_func: The function to be applied
    :param fetch_properties: The properties to fetch for each row of data
    :param unwind_alternative_labels: Boolean flag indicating whether to unwind alternative labels
    :return: DataFrame with combined data
    """
    def combine(item):
        print(item['name'])
        labels = []
        labels.append(item['name'])
        labels.append(item['description'].replace("'", "").replace('[', '').replace(']', ''))
        for alt_label in item['alternative_labels']:
            labels.append(alt_label.replace("'", ""))
        return labels
    df_all["combined"] = df_all.apply(combine, axis=1)
    return df_all

def fetch_embedding_from_db(input_string):
    """
    Fetches an embedding from the Neo4j database given an input string.

    :param input_string: The input string used to fetch the corresponding embedding.
    :return: The fetched embedding or None if not found.
    """

    # Build the Cypher query to fetch the embedding
    query = f"MATCH (n:ModelEmbedding) WHERE n.input = '{input_string}' RETURN n.vector"

    # Execute the Cypher query
    results, meta = db.cypher_query(query)

    # # If a result was found, return the embedding
    # if results:
    #     # The query returns a list of results, each of which is a tuple. The embedding is the first element of the tuple.
    #     # Therefore, we return the first element of the first result.
    #     return results[0][0]

    # If no result was found, return None
    return None

def iterate_over_inputs(input_list):
    embeddings =[]
    for input in input_list:
        if fetch_embedding_from_db(input) == None:
            embeddings.append(request_embedding(input))
    return embeddings

def apply_embedding(df_all, resume):
    pandarallel.initialize(nb_workers=EMBEDDING_FETCHING_PROCESSES, progress_bar=True, use_memory_fs=False)
    if resume:
        df_all['embedding'] = df_all['combined'].apply(lambda x: iterate_over_inputs(x))
    else:
        df_all['embedding'] = df_all.combined.swifter.apply(request_embedding)
    return df_all

def generate_ingest_query(Model, id_property):
    """
    Generates a Cypher query to ingest data into a Neo4j database.

    :param Model: The Django model for which data is to be ingested
    :param id_property: The id property of the model
    :return: Cypher query as a string
    """
    return f'''
                UNWIND $vectors as row
                MATCH
                    (n:{Model.__label__} {{{id_property}: row[0]}})
                MERGE
                    (emb:ModelEmbedding {{vector: row[1], input: row[2]}})-[:FOR]->(n)
                ON CREATE SET
                    emb.uid = RandomUUID()

            '''

def ingest_data_into_db(chunks, db, query):
    """
    Ingests data into a Neo4j database using a provided Cypher query.

    :param chunks: The data to be ingested
    :param db: The database connection object
    :param query: The Cypher query to be executed
    """
    current = 1
    for chunk in chunks:
        current += 1
        db_rows = [ # to python array
            [r[0], r[1], r[2]] for r in chunk.to_records(index=False)
        ]
        db.cypher_query(query, {'vectors': db_rows})

def get_embeddings_for_model(cmd, Model, fetch_properties, combine_func, fetch_filter='', required_properties=None, resume=True, id_property='uid', unwind_alternative_labels=False):
    """
     Retrieve and store embeddings for the specified model using OpenAI's API.

     Args:
         cmd: A command object to handle logging and output.
         Model: The model class for which embeddings should be fetched.
         fetch_properties: A list of properties to fetch from the model nodes.
         combine_func: A function to combine fetched properties before sending them for embedding generation.
         fetch_filter (str, optional): A Cypher query filter to apply when fetching nodes. Defaults to ''.
         required_properties (list, optional): A list of properties that must be present for a node to be processed. Defaults to None.
         resume (bool, optional): Whether to resume the process by skipping nodes that already have embeddings. Defaults to True.
         id_property (str, optional): The property to use as the unique identifier for nodes. Defaults to 'uid'.
         unwind_alternative_labels (bool, optional): Whether to create a separate embedding for every label. Defaults to False.
     """
    query = build_cypher_query(Model, fetch_properties, fetch_filter, unwind_alternative_labels, id_property)
    df_all, total, processable = fetch_data(query, db, required_properties, fetch_properties, id_property)
    # cmd.stdout.write(f'total nodes: {total}')
    # cmd.stdout.write(f'processable nodes: {processable}')
    # cmd.stdout.write(f'skipping {total-processable} nodes...')

    if processable == 0:
        return

    # Apply your functions
    df_all = apply_combine_func(df_all, combine_func, fetch_properties, unwind_alternative_labels)
    df_all = apply_embedding(df_all, resume)

    # Filter out rows where 'embedding' is an empty list
    df_all = df_all[df_all['embedding'].apply(len) > 0]

    # Continue with your existing code
    list_length = len(df_all['embedding'][0])
    min_length = min([len(x) for x in df_all['embedding']])

    # Create a list to hold each chunk dataframe
    chunks = []

    for i in range(list_length):
        # Create a new dataframe for each element in the lists
        chunk_df = df_all[[id_property]].copy()  # Copy the id_property column

        # Safely extract elements from 'embedding', handling out-of-range indices
        chunk_df['embedding_element_' + str(i)] = df_all['embedding'].apply(
            lambda x: x[i] if i < len(x) else x[0])  # Changed fallback from x[0] to None

        # Safely extract elements from 'combined', handling out-of-range indices
        chunk_df['combined_element_' + str(i)] = df_all['combined'].apply(
            lambda x: x[i] if i < len(x) else x[0])  # Changed fallback from x[0] to None

        # Append this new dataframe to the chunks list
        chunks.append(chunk_df)

    # Continue with the rest of your code
    query = generate_ingest_query(Model, id_property)
    ingest_data_into_db(chunks, db, query)

    # cmd.stdout.write(cmd.style.SUCCESS('Successfully stored embeddings in db'))







def main():
    # Get the project root directory
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mat2devplatform.settings")

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    load_dotenv()
    from neomodel import config

    config.DATABASE_URL = os.getenv('NEOMODEL_NEO4J_BOLT_URL')
    # get_embeddings_for_model(
    #     "",
    #     Model=EMMOProcess,
    #     fetch_properties= ['name', 'description'],
    #     combine_func=lambda s: s['name'],
    #     unwind_alternative_labels = True
    #     # add other parameters here...
    # )
    get_embeddings_for_model(
        "",
        Model=EMMOMatter,
        fetch_properties= ['name', 'description'],
        combine_func=lambda s: s['name'],
        unwind_alternative_labels = True
        # add other parameters here...
    )
    # get_embeddings_for_model(
    #     "",
    #     Model=EMMOQuantity,
    #     fetch_properties= ['name', 'description'],
    #     combine_func=lambda s: s['name'],
    #     unwind_alternative_labels = True
    #     # add other parameters here...
    # )


if __name__ == '__main__':
    main()