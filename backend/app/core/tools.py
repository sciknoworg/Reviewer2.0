import json
import ssl
import time

import certifi
import os

os.environ["SSL_CERT_FILE"] = certifi.where()
ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.OPENAI_KEY)


def call_openai(messages, llm, function, temperature=0, max_retries=3):
    """One-shot structured extraction via the legacy OpenAI function-calling API.

    Used for small, single-purpose lookups (section-header matching, reference
    parsing) rather than the full agentic review loops, which go through
    LangGraph's create_react_agent instead.
    """
    attempt = 0
    while True:
        try:
            response = client.chat.completions.create(
                model=llm,
                messages=messages,
                temperature=temperature,
                functions=function
            )
            return json.loads(response.choices[0].message.function_call.arguments)
        except Exception as e:
            attempt += 1
            if attempt >= max_retries:
                raise RuntimeError(f"OpenAI call failed after {max_retries} attempts: {e}") from e
            print(f"OpenAI call failed ({e}); retrying in 5 seconds (attempt {attempt}/{max_retries})")
            time.sleep(5)
