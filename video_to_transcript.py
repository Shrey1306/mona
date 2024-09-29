import boto3
import time
import json
import os
from moviepy.editor import VideoFileClip
from pydub import AudioSegment


def transcribe_mp4_in_segments(
    mp4_file_path, bucket_name, segment_duration=20, output_folder="transcripts"
):
    # Step 1: Extract Audio from MP4
    video = VideoFileClip(mp4_file_path)
    audio_file_path = "extracted_audio.wav"
    video.audio.write_audiofile(audio_file_path)

    # Step 2: Split the extracted audio into 20-second segments
    audio = AudioSegment.from_file(audio_file_path)
    segment_duration_ms = segment_duration * 1000  # Convert seconds to milliseconds
    total_segments = len(audio) // segment_duration_ms + (
        1 if len(audio) % segment_duration_ms != 0 else 0
    )

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Initialize AWS clients
    s3_client = boto3.client("s3")
    transcribe_client = boto3.client("transcribe")

    for idx in range(total_segments):
        # Start time for the segment in milliseconds
        start_ms = idx * segment_duration_ms
        end_ms = min((idx + 1) * segment_duration_ms, len(audio))
        segment = audio[start_ms:end_ms]

        segment_file_name = f"segment_{idx}.wav"
        segment_file_path = os.path.join(output_folder, segment_file_name)
        segment.export(
            segment_file_path, format="wav"
        )  # AWS Transcribe supports WAV format

        # Upload the segment to S3
        s3_key = f"audio_segments/{segment_file_name}"
        s3_client.upload_file(segment_file_path, bucket_name, s3_key)

        # Start a transcription job
        job_name = f"transcription_job_{int(time.time())}_{idx}"
        media_uri = f"s3://{bucket_name}/{s3_key}"

        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": media_uri},
            MediaFormat="wav",
            LanguageCode="en-US",  # Change as per your audio language
            Settings={
                "ShowSpeakerLabels": True,
                "MaxSpeakerLabels": 2,  # Adjust based on expected number of speakers
            },
            OutputBucketName=bucket_name,
            OutputKey=f"transcripts/{job_name}.json",
        )

        # Wait for the transcription job to complete
        print(f"Waiting for transcription job {job_name} to complete...")
        while True:
            status = transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            job_status = status["TranscriptionJob"]["TranscriptionJobStatus"]
            if job_status in ["COMPLETED", "FAILED"]:
                break
            time.sleep(5)

        if job_status == "COMPLETED":
            # Download the transcription result from S3
            transcript_file_name = f"transcript_{idx}.json"
            transcript_file_path = os.path.join(output_folder, transcript_file_name)

            # Download the transcript file
            s3_client.download_file(
                bucket_name, f"transcripts/{job_name}.json", transcript_file_path
            )

            print(f"Transcription for segment {idx} saved to {transcript_file_path}")
        else:
            print(f"Transcription job {job_name} failed.")

        # Clean up: Delete the audio segment from S3 and local storage
        s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
        os.remove(segment_file_path)

        # Delete the transcription job (optional)
        transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)

        # Wait for 20 seconds before processing the next segment (optional)
        # Uncomment the next line if you want to simulate processing every 20 seconds
        # time.sleep(20)

    # Clean up: Delete the extracted audio file
    os.remove(audio_file_path)


# Example usage
mp4_file = "mohs.mp4"
bucket_name = "hackgt"
output_folder = "transcripts"

transcribe_mp4_in_segments(mp4_file, bucket_name, output_folder=output_folder)
