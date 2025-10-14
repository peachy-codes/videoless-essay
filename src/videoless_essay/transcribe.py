import whisper
from pathlib import Path


def audio_transcriber(audio_path:Path) -> str:
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

    text = result['text']

    return text
