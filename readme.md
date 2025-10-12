Video essays are too long

We want to read!

This is an early version of this script.

Uses yt-dl, whisper, sentence transformers

Methodology: Rip YT, save mp3, transcribe with whisper(small), and using embeddings to segment into suspected paragraphs for easy reading

Usage:

mac users

python3 -m venv videoless-essay

cd videoless-essay

source bin/activate

pip install -r requirements.txt

python3 main.py --url fullYoutubeURL

windows users

idk lol