import argparse
import json
from pathlib import Path
from .ytdownload import youtube_downloader
from .transcribe import audio_transcriber
from .writer import essay_writer

repo_root = Path(__file__).resolve().parents[2]
text_dir = repo_root / "data" / "text"
text_dir.mkdir(parents=True, exist_ok=True)

def arguments_parser():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--url",
        type=str,
        required=True,
        help="Entire YouTube URL: https://www.youtube.come/watch?v=<VIDEO_ID>"
        )
    

    return p.parse_args()

def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c not in r'\/:*?"<>|').strip()


def main() -> None:
    args = arguments_parser()

    audio_file, metadata_file = youtube_downloader([args.url])

    print(f"Audio saved to: {audio_file}")
    print(f"Metadata saved to: {metadata_file}")

    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    raw_transcribe_text = audio_transcriber(audio_file)

    essay = essay_writer(metadata, raw_transcribe_text)
    
    title = sanitize_filename(metadata["title"])

    video_id = metadata.get("id", audio_file.stem)
    dest_path = text_dir / f"No-Video Essay {title} [{video_id}].txt"

    dest_path.write_text(essay, encoding="utf-8")

    print(f"Saved essay to {dest_path}.txt")

if __name__ == "__main__":

    main()