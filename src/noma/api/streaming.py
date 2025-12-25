"""Video streaming with GraphRAG analysis."""

import threading
import time

import cv2

from noma.rag import create_graph_instance

ANALYSIS_INTERVAL_SECONDS = 20

ANALYSIS_PROMPT = """
This is a CLIP from Moh's Cancer surgery. Identify ALL ENTITIES, 
their ROLES, RELATIONSHIPS, operations, and if ANY cancer treatment 
guidelines were violated or the patient responded abnormally 
BY DESCRIBING EACH STEP. FORMAT THIS IN HTML TAGS (<p></p> outermost). 
Append **** (4 ASTERISKS) at the end if anything was violated.
"""


class VideoStreamer:
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = 0
        self.elapsed_time = 0.0
        self._lock = threading.Lock()
        self._text_update = ""
        self._last_query_time = -ANALYSIS_INTERVAL_SECONDS
        self._graph = create_graph_instance()

    def generate_frames(self):
        frame_duration = 1.0 / self.fps

        while True:
            success, frame = self.cap.read()
            if not success:
                break

            with self._lock:
                self.frame_count += 1
                self.elapsed_time = self.frame_count / self.fps
                self._maybe_run_analysis()

            _, buffer = cv2.imencode(".jpg", frame)
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )
            time.sleep(frame_duration)

        self.cap.release()

    def _maybe_run_analysis(self):
        current_second = int(self.elapsed_time)
        if (
            current_second % ANALYSIS_INTERVAL_SECONDS == 0
            and current_second != self._last_query_time
        ):
            result = self._graph.query(ANALYSIS_PROMPT)
            self._text_update = result
            self._last_query_time = current_second

    def get_text_update(self) -> str:
        with self._lock:
            return self._text_update

