import os

from tenacity import retry, stop_after_attempt, wait_random_exponential
from typing import List
import openai



@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def chat_with_gpt4(setup_message=[], prompt='', api_key=os.environ.get("OPENAI_API_KEY")):
    openai.api_key = api_key

    conversation_history = setup_message
    conversation_history.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=conversation_history,
        max_tokens=2500,
        n=1,
        stop=None,
        temperature=0,
    )
    return [res["message"]["content"] for res in response["choices"]][0]


def chat_with_gpt3(setup_message=[], prompt='', api_key=os.environ.get("OPENAI_API_KEY")):
    openai.api_key = api_key

    conversation_history = setup_message
    conversation_history.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0,
    )
    return [res["message"]["content"] for res in response["choices"]][0]