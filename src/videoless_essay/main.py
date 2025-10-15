import argparse
import json
import os
from pathlib import Path
from .ytdownload import youtube_downloader
from .transcribe import audio_transcriber
from .writer import essay_writer
from .screencapper import run_screencaps
from .htmlpage import html_writer

# suppressing hf parallelism warning for now. 
os.environ["TOKENIZERS_PARALLELISM"] = "false"

repo_root = Path(__file__).resolve().parents[2]
data_root = repo_root / "data"
text_dir = data_root / "text"
transcribe_dir = data_root / "transcriptions"
screencaps_root = data_root / "screencaps"
html_dir = data_root / "html"
pdf_dir = data_root / "pdf"
text_dir.mkdir(parents=True, exist_ok=True)
transcribe_dir.mkdir(parents=True, exist_ok=True)
screencaps_root.mkdir(parents=True, exist_ok=True)
html_dir.mkdir(parents=True, exist_ok=True)
pdf_dir.mkdir(parents=True, exist_ok=True)

def arguments_parser():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--url",
        type=str,
        required=True,
        help="Entire YouTube URL: https://www.youtube.come/watch?v=<VIDEO_ID>"
        )
    
    p.add_argument(
        "--screencaps",
        action="store_true",
        help="If set, saves one JPEG per paragraph form paragraph start time."

    )

    p.add_argument(
        "--html",
        action="store_true",
        help="Outputs html file. Embeds screencaps if screencap flag is used."
    )

    p.add_argument(
    "--pdf",
    action="store_true",
    help="Also save the HTML output as a PDF file."
    )

    p.add_argument(
    "--all",
    action="store_true",
    help="Enable all outputs: screencaps, HTML, and PDF."
    )

    return p.parse_args()

def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c not in r'\/:*?"<>|').strip()


def main() -> None:
    args = arguments_parser()
    
    if args.pdf and not args.html:
        args.html = True
    
    if args.all:
        args.screencaps = True
        args.html = True
        args.pdf = True
    
    audio_file, video_file_path, metadata_file = youtube_downloader([args.url])

    print(f"Audio saved to: {audio_file}")
    print(f"Video saved to: {video_file_path}")
    print(f"Metadata saved to: {metadata_file}")

    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # transcription
    transcription_output_dict = audio_transcriber(audio_file)
    whisper_result = transcription_output_dict['result']
    transcription_file_path = transcription_output_dict['transcript_file']

    # paragraphs with timestep pass through
    segments = whisper_result["segments"]
    essay_text, paragraph_manifest = essay_writer(metadata, segments)

    # essay writing
    title = sanitize_filename(metadata["title"])
    video_id = metadata.get("id", audio_file.stem)
    essay_path = text_dir / f"No-Video Essay {title} [{video_id}].txt"
    essay_path.write_text(essay_text, encoding="utf-8")

    # saving paragraph manifest and transcript json
    paragraphs_path = transcription_file_path.parent / f"{video_id}.paragraphs.json"
    with open(paragraphs_path, "w", encoding="utf-8") as f:
        json.dump(paragraph_manifest, f, ensure_ascii=False, indent=2)

    print(f"Transcript JSON saved to {transcription_file_path}")
    print(f"Paragraph manifest saved to: {paragraphs_path}")
    print(f"Saved essay to {essay_path}")

    # screencaps
    screendir = screencaps_root / video_id

    if args.screencaps:
        created = run_screencaps(Path(video_file_path), paragraph_manifest, screendir)
        print(f"Screencaps saved to: {screendir} ({len(created)} frames)")

    # html essay with images
    if args.html:
        out_html = html_dir / f"No-Video Essay {sanitize_filename(metadata['title'])} [{video_id}].html"
        html_writer(
            metadata=metadata,
            paragraphs_manifest=paragraph_manifest,   # manifest is the only source of truth
            screencaps_dir=screendir,
            out_path=out_html,
            embed_images=bool(args.screencaps),
        )
        print(f"HTML saved to: {out_html}")

        if args.pdf:
            from weasyprint import HTML
            pdf_path = pdf_dir / f"No-Video Essay {sanitize_filename(metadata['title'])} [{video_id}].pdf"
            HTML(filename=str(out_html)).write_pdf(str(pdf_path))
            print(f"PDF saved to: {pdf_path}")
    

    
if __name__ == "__main__":

    main()