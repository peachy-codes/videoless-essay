# Videoless Essay

Video essays are too long. We want to read them instead.

This is an early version of this script.

## Overview

This project:

- Uses `yt-dlp` to download video from a YouTube video.
- Uses `whisper` (small model) to transcribe the audio.
- Uses `sentence-transformers` to segment the transcript into suspected paragraphs for easier reading.
- Uses `ffmpeg` for audio ripping and screenshots.

## Methodology

1. Rip the YouTube video.
2. Rip the `.mp3` track from the video.
3. Transcribe it with `whisper`.
4. Use embeddings to segment the transcript into readable sections.
5. Save paragraphs to .txt file.
6. Optionally save screencaps at beginning of paragraphs if flag is set.
7. Optionally save html of the transcription, with screencaps embedding if flag set.

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

### Optional Parameters

You can set the --screencaps flag to save screencaps of the video for each paragraph beginning
    
    python3 -m videoless_essay.main --url FULL_YOUTUBE_URL --screencaps

You can set the --html flag to save an html page with the screencaps embedded

    python3 -m videoless_essay.main --url FULL_YOUTUBE_URL --screencaps --html

Running --html without --screencaps will still create the html page, just without the images embedded.

You can set the --pdf flag to save a pdf with optional screencaps embedding

    python3 -m videoless_essay.main --url FULL_YOUTUBE_URL --pdf

**Note: this will force the --html flag**

You can set the --all flag to enable all possible flags

    python3 -m videoless_essay.main --url FULL_YOUTUBE_URL --all


## Future Work

- Add semantic searching for lookup.