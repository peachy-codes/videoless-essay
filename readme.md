Videoless Essay

Video essays are too long. We want to read them instead.

This project converts YouTube video essays into readable text by downloading the audio, transcribing it, and segmenting the result into structured paragraphs.

⸻

Methodology
	1.	Download audio from a YouTube URL
	2.	Save it as an .mp3 file in data/audio/
	3.	Transcribe the audio into text with whisper
	4.	Segment the text into suspected paragraphs using embeddings

⸻

Setup

Create and activate a virtual environment:

python3 -m venv videoless-essay
cd videoless-essay
source bin/activate

Install dependencies:

pip install -r requirements.txt


⸻

Usage

From the root directory of the repository:

export PYTHONPATH=src
python3 -m videoless_essay.main --url FULL_YOUTUBE_URL

This will:
	•	Download the video’s audio
	•	Save the transcription
	•	Generate a text version of the video essay in data/text/

⸻

Future Work
	•	Add screencaps from the video in appropriate sections
	•	Make the essay more nicely formatted
	•	Possible browser UI
    

⸻