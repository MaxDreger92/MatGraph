from tenacity import retry, stop_after_attempt, wait_random_exponential
from typing import List
import openai
from src.utils.config import EMBEDDING_MODEL, OPENAI_API_KEY


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
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

    # Replace newlines in the input text with spaces, as they can negatively affect performance.
    text = str(text).replace("\n", " ").strip().replace("'", "")
    # Call the OpenAI Embedding API to create an embedding for the input text.
    # The API response contains the embedding data in a nested structure.
    embedding_response = openai.Embedding.create(input=[text], engine=EMBEDDING_MODEL, api_key=OPENAI_API_KEY
                                                 )

    # Extract the embedding data from the response and return it as a list of floating-point numbers.
    return embedding_response["data"][0]["embedding"]


def chat_with_gpt4(setup_message=[], prompt='', api_key=OPENAI_API_KEY):
    openai.api_key = api_key

    conversation_history = setup_message
    conversation_history.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=conversation_history,
        max_tokens=2500,
        n=4,
        stop=None,
        temperature=0.5,
    )
    return response["choices"][0]["message"]["content"]
