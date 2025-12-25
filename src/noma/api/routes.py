"""API route definitions."""

import time
from flask import Flask, Response, render_template, jsonify

from .streaming import VideoStreamer

_streamer: VideoStreamer | None = None


def get_streamer() -> VideoStreamer:
    global _streamer
    if _streamer is None:
        _streamer = VideoStreamer("media/mohs.mp4")
    return _streamer


def register_routes(app: Flask) -> None:
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/video_feed")
    def video_feed():
        return Response(
            get_streamer().generate_frames(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    @app.route("/text_feed")
    def text_feed():
        return Response(_text_event_stream(), mimetype="text/event-stream")

    @app.route("/api/status")
    def status():
        streamer = get_streamer()
        return jsonify({
            "status": "ok",
            "frame_count": streamer.frame_count,
            "elapsed_time": streamer.elapsed_time,
        })


def _text_event_stream():
    previous_update = ""
    while True:
        text_update = get_streamer().get_text_update()
        if text_update and text_update != previous_update:
            yield f"data: {text_update}\n\n"
            previous_update = text_update
        time.sleep(1)

