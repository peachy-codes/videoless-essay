import whisper
import json
from pathlib import Path


repo_root = Path(__file__).resolve().parents[2]
data_root = repo_root / "data"
transcribe_dir = data_root / "transcriptions"
transcribe_dir.mkdir(parents=True, exist_ok=True)

def audio_transcriber(audio_path:Path) -> dict:
    if not audio_path.is_file():
        raise FileNotFoundError(audio_path)
    
    model = whisper.load_model("small")  # pick "base", "small", "medium", "large" if desired

    result = model.transcribe(
        str(audio_path),
        task="transcribe",
        language="en",
        temperature=0.0,
        best_of=1,
        beam_size=1,
        condition_on_previous_text=False,
        fp16=False
    )

    video_id = audio_path.stem
    transcript_file = transcribe_dir / f"{video_id}.whisper.json"
    with open(transcript_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    

    return {"result" : result, "transcript_file": transcript_file}

