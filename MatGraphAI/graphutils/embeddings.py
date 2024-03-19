import logging
from typing import List

from openai import OpenAI

client = OpenAI()
from neomodel import db
from tenacity import wait_random_exponential, retry, stop_after_attempt

from graphutils.config import EMBEDDING_MODEL, EMBEDDING_DIMENSIONS
from django.conf import settings

@retry(wait=wait_random_exponential(min=1, max=2), stop=stop_after_attempt(6))
def request_embedding(text: str) -> List[float]:
    """
    Retrieve the embedding of the given text using OpenAI's API.

    This function attempts to generate an embedding for the input text using OpenAI's Embedding API.
    If the request fails, it will retry up to 6 times, with an exponential backoff strategy for waiting
    between retries.

    Args:
        text (str): The input text to get the embedding for.

    Returns:
        List[float]: A list of floating-point numbers representing the embedding.
    """
    print("Requesting embedding for text: ", text)
    # Replace newlines in the input text with spaces, as they can negatively affect performance.
    text = str(text).replace("\n", " ").strip().replace("'", "")
    # Call the OpenAI Embedding API to create an embedding for the input text.
    # The API response contains the embedding data in a nested structure.
    embedding_response = client.embeddings.create(input=[text], engine=EMBEDDING_MODEL, api_key = settings.OPENAI_API_KEY)

    # Extract the embedding data from the response and return it as a list of floating-point numbers.
    return embedding_response.data[0].embedding




# class  EmbeddingSearch:
#     """
#     Loads embeddings for a model into RAM and enables fast search using FAISS.
#     The index is fetched and built on instance creation.
#
#     Attributes:
#         Model: The Django model class to fetch embeddings for.
#         id_property (str): The property to use as the identifier.
#     """
#
#     def __init__(self, Model, fetch_filter="true", id_property='uid'):
#         """
#         Initialize the EmbeddingSearch instance.
#
#         Args:
#             Model: The Django model class to fetch embeddings for.
#             fetch_filter (str): The filter to apply when fetching embeddings from the database.
#             id_property (str): The property to use as the identifier.
#         """
#
#         # import here to avoid loading faiss for everything django does
#         import faiss
#         import numpy as np
#
#         self.Model = Model
#         self.id_property = id_property
#
#         logging.info(f'Fetching embeddings for label {Model.__label__}')
#         query = f'''
#             MATCH (n:{Model.__label__})<-[:FOR]-(emb:ModelEmbedding)
#             WHERE COALESCE(n.disable_embedding, false)=false AND {fetch_filter}
#             RETURN n.{id_property} as {id_property}, emb.vector as vector
#         '''
#         # Fetch embeddings from the database
#         result, meta = db.cypher_query(query)
#
#         if not len(result):
#             raise ValueError(f'no embeddings found for {Model.__label__}')
#
#         logging.info(f'Creating embedding index for label {Model.__label__}')
#
#         # Create FAISS index
#         self.index = faiss.IndexFlatIP(EMBEDDING_DIMENSIONS)
#         self.index.add(np.array([
#             np.array(row[1]) for row in result
#         ]))
#
#         self.model_ids = [row[0] for row in result]
#
#
#     def find_vector(self, vector, n=1, include_similarities=False):
#         """
#         Find the closest embeddings in the index to the input vector.
#
#         Args:
#             vector (np.array): The input vector to find the closest embeddings for.
#             n (int): The number of closest embeddings to return.
#             include_similarities (bool): Whether to include similarities in the output.
#
#         Returns:
#             If `include_similarities` is False, returns a list of ids or a single id (if n=1).
#             If `include_similarities` is True, returns a list of tuples (id, similarity) or a tuple (id, similarity) if n=1.
#         """
#
#         import numpy as np
#
#         D, I = self.index.search(np.array([vector]), n)
#         ids = [self.model_ids[i] for i in I[0]]
#
#         if include_similarities:
#             return ids[0], D[0][0] if n == 1 else [(ids[i], D[0][i]) for i in range(len(ids))]
#
#         return ids[0] if n == 1 else ids
#
#
#     def find_string(self, query, return_model=False, include_similarity=False, **kwargs):
#         """
#         Find the closest embeddings in the index to the input query.
#
#         Args:
#             query (str): The input string to find the closest embeddings for.
#             return_model (bool): Whether to return a model instance instead of the id.
#             include_similarity (bool): Whether to include similarities in the output.
#             **kwargs: Additional keyword arguments to pass to the `find_vector` method.
#
#         Returns:
#             Depending on the input arguments, returns:
#             - An instance of the model or an id
#             - A list of tuples (model instance, similarity) or a list of tuples (id, similarity)
#         """
#
#         if not query:
#             return (None, 0) if include_similarity else None
#         res = self.find_vector(request_embedding(query), include_similarities=include_similarity, **kwargs)
#
#         if include_similarity:
#             if return_model:
#                 return self.Model.nodes.get(**{self.id_property: res[0]}), res[1]
#             else:
#                 return res
#         else:
#             return self.Model.nodes.get(**{self.id_property: res}) if return_model else res