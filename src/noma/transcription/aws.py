"""AWS Transcribe integration for video transcription."""

import os
import time
from pathlib import Path

import boto3
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

from noma.config import get_config

SEGMENT_DURATION_SECONDS = 20


def transcribe_video(
    video_path: str,
    output_dir: str = "transcripts",
    segment_duration: int = SEGMENT_DURATION_SECONDS,
) -> list[str]:
    config = get_config()
    if not config.aws.bucket:
        raise ValueError("AWS_S3_BUCKET environment variable required")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    audio_path = _extract_audio(video_path)
    segments = _split_audio(audio_path, segment_duration)

    s3 = boto3.client("s3")
    transcribe = boto3.client("transcribe")

    transcript_files = []
    for idx, segment in enumerate(segments):
        transcript_path = _process_segment(
            segment, idx, config.aws.bucket, s3, transcribe, output_path
        )
        if transcript_path:
            transcript_files.append(transcript_path)

    os.remove(audio_path)
    return transcript_files


def _extract_audio(video_path: str) -> str:
    audio_path = "extracted_audio.wav"
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)
    return audio_path


def _split_audio(audio_path: str, segment_duration: int) -> list[AudioSegment]:
    audio = AudioSegment.from_file(audio_path)
    segment_ms = segment_duration * 1000
    total_segments = len(audio) // segment_ms + (1 if len(audio) % segment_ms else 0)

    segments = []
    for idx in range(total_segments):
        start = idx * segment_ms
        end = min((idx + 1) * segment_ms, len(audio))
        segments.append(audio[start:end])
    return segments


def _process_segment(
    segment: AudioSegment,
    idx: int,
    bucket: str,
    s3,
    transcribe,
    output_path: Path,
) -> str | None:
    segment_file = output_path / f"segment_{idx}.wav"
    segment.export(str(segment_file), format="wav")

    s3_key = f"audio_segments/segment_{idx}.wav"
    s3.upload_file(str(segment_file), bucket, s3_key)

    job_name = f"transcription_job_{int(time.time())}_{idx}"
    media_uri = f"s3://{bucket}/{s3_key}"

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": media_uri},
        MediaFormat="wav",
        LanguageCode="en-US",
        Settings={"ShowSpeakerLabels": True, "MaxSpeakerLabels": 2},
        OutputBucketName=bucket,
        OutputKey=f"transcripts/{job_name}.json",
    )

    transcript_path = _wait_for_transcription(
        job_name, idx, bucket, s3, transcribe, output_path
    )

    s3.delete_object(Bucket=bucket, Key=s3_key)
    os.remove(segment_file)
    transcribe.delete_transcription_job(TranscriptionJobName=job_name)

    return transcript_path


def _wait_for_transcription(
    job_name: str,
    idx: int,
    bucket: str,
    s3,
    transcribe,
    output_path: Path,
) -> str | None:
    """Wait for transcription job to complete and download result."""
    print(f"Waiting for transcription job {job_name}...")

    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        job_status = status["TranscriptionJob"]["TranscriptionJobStatus"]
        if job_status in ["COMPLETED", "FAILED"]:
            break
        time.sleep(5)

    if job_status == "COMPLETED":
        transcript_file = output_path / f"transcript_{idx}.json"
        s3.download_file(bucket, f"transcripts/{job_name}.json", str(transcript_file))
        print(f"Transcription for segment {idx} saved to {transcript_file}")
        return str(transcript_file)

    print(f"Transcription job {job_name} failed.")
    return None

