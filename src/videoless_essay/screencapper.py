import subprocess
from pathlib import Path
from typing import List, Dict

def run_screencaps(video_file: Path, paragraphs_manifest: List[Dict], out_dir: Path) -> List[Path]:

    created: List[Path] = []
    if not isinstance(video_file,Path):
        video_file = Path(video_file)
    if not video_file.is_file():
        return created
    
    out_dir.mkdir(parents=True, exist_ok=True)

    #ensure para idx ordering

    items = sorted(paragraphs_manifest, key = lambda x : x.get("para_idx",0))

    for item in items:
        i = int(item.get("para_idx",0))
        t = float(item["start"])
        out_path = out_dir / f"para-{i:03d}.jpg"

        cmd = [
            "ffmpeg", "-y",
            "-ss", f"{t}",
            "-i", str(video_file),
            "-frames:v", "1",
            "-q:v", "2",
            str(out_path),
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            created.append(out_path)
        except FileNotFoundError as e:
            raise RuntimeError("ffmpeg is not available on PATH") from e
        except subprocess.CalledProcessError:
            print(f"Couldn't call ffmpeg on paragraph: {i} ... Skipping!")
            continue

    return created