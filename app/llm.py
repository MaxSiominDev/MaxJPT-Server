from __future__ import annotations

import os
from typing import TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from llama_cpp import Llama

MODEL_DIR = "/app/model"
MOCK_RESPONSE = "Mock response: LLM_MOCK is enabled."


def get_model_path() -> str:
    model_url = os.environ.get("MODEL_URL", "")
    if not model_url:
        raise RuntimeError("MODEL_URL environment variable is not set")
    filename = os.path.basename(urlparse(model_url).path)
    return os.path.join(MODEL_DIR, filename)


def load_model() -> Llama | None:
    if os.environ.get("LLM_MOCK"):
        return None

    from llama_cpp import Llama

    n_ctx = int(os.environ.get("N_CTX", 65536))
    n_threads = int(os.environ.get("N_THREADS", 32))
    return Llama(
        model_path=get_model_path(),
        n_ctx=n_ctx,
        n_threads=n_threads,
        verbose=False,
    )


def run_inference(llm: Llama | None, system_prompt: str, user_prompt: str) -> str:
    if os.environ.get("LLM_MOCK"):
        return MOCK_RESPONSE

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    result = llm.create_chat_completion(  # type: ignore[union-attr]
        messages=messages,
        max_tokens=512,
        temperature=0.8,
        top_p=0.9,
        repeat_penalty=1.1,
    )
    return result["choices"][0]["message"]["content"]
