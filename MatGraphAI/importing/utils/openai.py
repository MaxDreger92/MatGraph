from tenacity import retry, stop_after_attempt, wait_random_exponential
from typing import List
import openai
from MatGraphAI.importing.config import EMBEDDING_MODEL




def chat_with_gpt4(api_key, setup_message=[], prompt=''):
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
