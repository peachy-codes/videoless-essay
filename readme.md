# Videoless Essay

Video essays are too long. We want to read them instead.

This is an early version of this script.

## Overview

This project:

- Uses `yt-dlp` to download audio from a YouTube video.
- Uses `whisper` (small model) to transcribe the audio.
- Uses `sentence-transformers` to segment the transcript into suspected paragraphs for easier reading.

## Methodology

1. Rip the YouTube audio.
2. Save the `.mp3` file to `data/audio/`.
3. Transcribe it with `whisper`.
4. Use embeddings to segment the transcript into readable sections.

## Setup

Create and activate a virtual environment:

    python3 -m venv videoless-essay
    cd videoless-essay
    source bin/activate

Install dependencies:

    pip install -r requirements.txt

## Usage

From the root directory:

    export PYTHONPATH=src
    python3 -m videoless_essay.main --url FULL_YOUTUBE_URL

This will:

- Download the video’s audio.
- Save the transcription.
- Generate a text version of the essay in `data/text/`.

## Future Work

- Add screencaps from videos in appropriate sections.