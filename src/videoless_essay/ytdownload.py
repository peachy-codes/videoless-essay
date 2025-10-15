import yt_dlp
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# directory resolution, audio save, log save
repo_root = Path(__file__).resolve().parents[2]
data_root = repo_root / "data"
audio_dir = data_root / "audio"
info_dir = data_root / "info"
video_dir = data_root / "video" # not used for now
audio_dir.mkdir(parents=True, exist_ok=True)
info_dir.mkdir(parents=True, exist_ok=True)
video_dir.mkdir(parents=True, exist_ok=True)


# parameters
ydl_opts = {
        'paths' : {"home": str(video_dir)},
        'outtmpl': {"default" :  '%(id)s.%(ext)s'},
        "format": "best[height<=360][ext=mp4]",
        'merge_output_format' : "mp4",
        "overwrites" : False,
        "nopart" : True
    }

def _ffmpeg_extract_mp3(src_video: Path, dest_audio: Path) -> None:

    dest_audio.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(src_video),
        "-vn",
        "-acodec", "libmp3lame",
        "-q:a", "2",
        str(dest_audio),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def youtube_downloader(URL:list) -> tuple[Path, Path, Path]:
    """
    Returns:
        (audio_file_path, video_file_path, metadata_file_path)
    """

    if not URL or not isinstance(URL[0],str):
        raise ValueError("function youtube_downloader expects single URL string in list")
    
    url = URL[0]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
 
       info = ydl.extract_info(url, download=True)

    video_filename = None
    if "requested_downloads" in info and info["requested_downloads"]:
        # last post-processed file typically has 'filepath'
        for d in info["requested_downloads"]:
            if "filepath" in d:
                video_filename = d["filepath"]
    if not video_filename:
        # fallback: assume mp4 in video_dir with id.ext
        ext = info.get("ext", "mp4")
        video_filename = str(video_dir / f"{info['id']}.{ext}")

    video_file = Path(video_filename)


    
    audio_file = audio_dir / f"{info['id']}.mp3"
    if not audio_file.exists():
        _ffmpeg_extract_mp3(video_file, audio_file)

    

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
        "saved_video":str(video_file),
        "saved_audio": str(audio_file),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    return audio_file, video_file, metadata_file
