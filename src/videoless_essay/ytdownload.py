import yt_dlp
import json
from datetime import datetime, timezone
from pathlib import Path

# directory resolution, audio save, log save
repo_root = Path(__file__).resolve().parents[2]
audio_dir = repo_root / "data" / "audio"
info_dir = repo_root / "data" / "info"
# video_dir = repo_root / "data" / "video" # not used for now
audio_dir.mkdir(parents=True, exist_ok=True)
info_dir.mkdir(parents=True, exist_ok=True)
# video_dir.mkdir(parents=True, exist_ok=True)


# parameters
ydl_opts = {
        'outtmpl': str(audio_dir / '%(id)s.%(ext)s'),
        'format': 'm4a/bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }

def youtube_downloader(URL:list) -> tuple[Path, Path]:

    ydl = yt_dlp.YoutubeDL(ydl_opts)
    info = ydl.extract_info(URL[0], download=True)

    
    audio_file = audio_dir / f"{info['id']}.mp3"
    metadata_file = info_dir / f"{info['id']}.json"

    record = {
        "id": info["id"],
        "title": info.get("title"),
        "uploader": info.get("uploader"),
        "channel_id": info.get("channel_id"),
        "duration": info.get("duration"),
        "upload_date": info.get("upload_date"),
        "url": info.get("webpage_url"),
        "tags": info.get("tags") or [],
        "saved_audio": str(audio_file),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    return audio_file, metadata_file
