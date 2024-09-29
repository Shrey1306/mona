# Incremental GraphRAG
# Neo4j Database
# Ollama Client (MediTron 7B)
# Uses 4o, 4o-Mini for Planning
from nano_graphrag import GraphRAG
from nano_graphrag._storage import Neo4jStorage
import os
import os
import logging
import ollama
from nano_graphrag import GraphRAG, QueryParam
from nano_graphrag import GraphRAG, QueryParam
from nano_graphrag.base import BaseKVStorage
from nano_graphrag._utils import compute_args_hash
from neo4j_vis import (
    visualize_neo4j_graph,
)  # Visualize the Knowledge Graph on every Upsert
from nano_graphrag._llm import gpt_4o_complete
import cv2
import json
import os

logging.basicConfig(level=logging.WARNING)
logging.getLogger("nano-graphrag").setLevel(logging.INFO)

# OpenAI API Key
os.environ["OPENAI_API_KEY"] = (
    "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"
)

# Ollama Model (Medical Domain Specific)
MODEL = "meditron"


async def ollama_model_if_cache(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    # remove kwargs that are not supported by ollama
    kwargs.pop("max_tokens", None)
    kwargs.pop("response_format", None)

    ollama_client = ollama.AsyncClient()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    # Get the cached response if having-------------------
    hashing_kv: BaseKVStorage = kwargs.pop("hashing_kv", None)
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})
    if hashing_kv is not None:
        args_hash = compute_args_hash(MODEL, messages)
        if_cache_return = await hashing_kv.get_by_id(args_hash)
        if if_cache_return is not None:
            return if_cache_return["return"]
    # -----------------------------------------------------
    response = await ollama_client.chat(model=MODEL, messages=messages, **kwargs)
    print(response)
    result = response["message"]["content"]
    # Cache the response if having-------------------
    if hashing_kv is not None:
        await hashing_kv.upsert({args_hash: {"return": result, "model": MODEL}})
    # -----------------------------------------------------
    return result


def remove_if_exist(file):
    if os.path.exists(file):
        os.remove(file)


neo4j_config = {
    "neo4j_url": os.environ.get("NEO4J_URL", "neo4j://localhost:7687"),
    "neo4j_auth": (
        os.environ.get("NEO4J_USER", "neo4j"),
        os.environ.get("NEO4J_PASSWORD", "12345678"),
    ),
}

graph_func = GraphRAG(
    graph_storage_cls=Neo4jStorage,
    addon_params=neo4j_config,
    working_dir="./mohs",  # Can reload faster
)

import asyncio


# To insert it into the knowledge graph and visualize
# def insert_and_visualize(path, vis_output):
#     with open(path) as f:
#         graph_func.insert(f.read())
#     visualize_neo4j_graph(output_file=vis_output)


# with open("transcripts/lita_transcript.txt") as f:
#     graph_func.insert(f.read())
#     visualize_neo4j_graph(output_file="three_js/base_graph.html")


# Starting REAL-TIME PROCESSING

import time


def process_video(video_path, json_folder):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return

    # Get frames per second (fps) and total frame count
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0

    while cap.isOpened():
        # Read the next frame
        ret, frame = cap.read()

        if not ret:
            break

        # Increment frame count
        frame_count += 1

        # Calculate elapsed time in seconds
        elapsed_time = frame_count / fps

        # Every 20 seconds, process the corresponding transcript file
        if (
            int(elapsed_time) % 20 == 0 and frame_count % fps == 0
        ):  # On every 20th second
            # json_file_name = f"transcript_{int(elapsed_time // 20)}.json"
            # json_file_path = "transcripts/" + json_file_name

            # # Check if the JSON file exists
            # if os.path.exists(json_file_path):
            #     vis_file = f"three_js/transcript_{int(elapsed_time // 20)}.html"
            #     insert_and_visualize(json_file_path, vis_file)
            #     time.sleep(2)
            # else:
            #     print(f"Warning: {json_file_name} not found.")

            # Query the Database
            query_temp = """
            This is a CLIP from Moh's Cancer surgery. Identify ALL ENTITIES, their ROLES, RELATIONSHIPS, operations, and if ANY cancer treatment guidelines were violated or the patient responded abnormally BY DESCRIBING EACH STEP. FORMAT THIS IN HTML TAGS (<p></p> outermost). Append **** (4 ASTERIKS) at the end if anything was violated.
            """

            # # Perform global graphrag search
            print(graph_func.query(query_temp))

        # Display the frame (optional)
        cv2.imshow("Video", frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release video capture and close windows
    cap.release()
    cv2.destroyAllWindows()


video_path = "mohs.mp4"  # Path to your video file
json_folder = (
    "/transcripts"  # Folder containing transcript_0.json, transcript_1.json, etc.
)
process_video(video_path, json_folder)
