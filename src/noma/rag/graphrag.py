"""GraphRAG integration with Neo4j and Ollama."""

import logging

import ollama
from nano_graphrag import GraphRAG
from nano_graphrag._storage import Neo4jStorage
from nano_graphrag.base import BaseKVStorage
from nano_graphrag._utils import compute_args_hash

from noma.config import get_config

logging.basicConfig(level=logging.WARNING)
logging.getLogger("nano-graphrag").setLevel(logging.INFO)

MODEL_NAME = "meditron"


def create_graph_instance(working_dir: str = "./data/mohs") -> GraphRAG:
    config = get_config()
    neo4j_params = {
        "neo4j_url": config.neo4j.url,
        "neo4j_auth": (config.neo4j.user, config.neo4j.password),
    }
    return GraphRAG(
        graph_storage_cls=Neo4jStorage,
        addon_params=neo4j_params,
        working_dir=working_dir,
    )


async def query_ollama_with_cache(
    prompt: str,
    system_prompt: str | None = None,
    history_messages: list | None = None,
    hashing_kv: BaseKVStorage | None = None,
    **kwargs,
) -> str:
    kwargs.pop("max_tokens", None)
    kwargs.pop("response_format", None)
    history_messages = history_messages or []

    client = ollama.AsyncClient()
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    if hashing_kv is not None:
        cache_key = compute_args_hash(MODEL_NAME, messages)
        cached = await hashing_kv.get_by_id(cache_key)
        if cached is not None:
            return cached["return"]

    response = await client.chat(model=MODEL_NAME, messages=messages, **kwargs)
    result = response["message"]["content"]

    if hashing_kv is not None:
        await hashing_kv.upsert({cache_key: {"return": result, "model": MODEL_NAME}})

    return result

