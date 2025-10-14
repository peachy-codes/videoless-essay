Video essays are too long

We want to read!

This is an early version of this script.

Uses yt-dl, whisper, sentence transformers

Methodology: Rip YT, save mp3, transcribe with whisper(small), and using embeddings to segment into suspected paragraphs for easy reading

Usage:

python3 -m venv videoless-essay

cd videoless-essay

source bin/activate

pip install -r requirements.txt


If running videoless-essay/main.py

from root directory:

python3 main.py --url fullYoutubeURL


**Please note this will soon be deprecated**


If running src/videoless_essay/main.py

from root directory:

export PYTHONPATH=src
python3 -m videoless_essay.main --url fullYoutubeURL

**Please note this will be the behavior in future versions**

FUTURE INTENTIONS:

Add screencaps from videos in appropriate sections