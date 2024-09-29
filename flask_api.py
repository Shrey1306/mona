from flask import Flask, render_template, Response
import threading
import cv2
import time

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

app = Flask(__name__)

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


class VideoStreamer:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print("Error: Cannot open video file.")
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = 0
        self.elapsed_time = 0
        self.lock = threading.Lock()
        self.text_update = ""
        self.last_query_time = -20  # Initialize to -20 to allow immediate query
        self.graph_func = graph_func  # Assume graph_func is already defined

    def generate_frames(self):
        """Yields video frames for streaming at real-time speed."""
        frame_time = 1.0 / self.fps  # Calculate the time per frame

        while True:
            success, frame = self.cap.read()
            if not success:
                print("End of video or cannot read frame.")
                break  # Exit when the video ends

            # Increment frame count and calculate elapsed time
            with self.lock:
                self.frame_count += 1
                self.elapsed_time = self.frame_count / self.fps

                # Every 20 seconds, query the database and update text
                if (
                    int(self.elapsed_time) % 20 == 0
                    and int(self.elapsed_time) != self.last_query_time
                ):
                    # Perform the database query
                    query_temp = """
                    This is a CLIP from Moh's Cancer surgery. Identify ALL ENTITIES, their ROLES, RELATIONSHIPS, operations, and if ANY cancer treatment guidelines were violated or the patient responded abnormally BY DESCRIBING EACH STEP. FORMAT THIS IN HTML TAGS (<p></p> outermost). Append **** (4 ASTERISKS) at the end if anything was violated.
                    """
                    result = self.graph_func.query(query_temp)
                    self.text_update = result
                    self.last_query_time = int(self.elapsed_time)

            # Encode the frame as JPEG
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()

            # Stream the frame
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

            # Sleep to match the frame rate
            time.sleep(frame_time)

        self.cap.release()  # Release the video capture when done

    def get_text_update(self):
        with self.lock:
            return self.text_update


# Initialize the VideoStreamer
video_streamer = VideoStreamer("mohs.mp4")  # Replace with your video file


@app.route("/video_feed")
def video_feed():
    return Response(
        video_streamer.generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


def event_stream():
    previous_update = ""
    while True:
        text_update = video_streamer.get_text_update()
        if text_update and text_update != previous_update:
            yield f"data: {text_update}\n\n"
            previous_update = text_update
            print(previous_update)
        time.sleep(1)


@app.route("/text_feed")
def text_feed():
    return Response(event_stream(), mimetype="text/event-stream")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", threaded=True)
