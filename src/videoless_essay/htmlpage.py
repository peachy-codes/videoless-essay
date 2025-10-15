from pathlib import Path
from typing import List, Dict
import html

def _mmss(t: float) -> str:
    m = int(t // 60); s = int(round(t - m*60))
    return f"{m:02d}:{s:02d}"

def html_writer(
    metadata: Dict,
    paragraphs_manifest: List[Dict],
    screencaps_dir: Path,
    out_path: Path,
    embed_images: bool = True,
) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    title = metadata.get("title", "")
    uploader = metadata.get("uploader", "")
    video_id = metadata.get("id", "")

    css = """
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.55;margin:2rem auto;max-width:820px;padding:0 1rem;color:#111}
    h1{font-size:1.8rem;margin:0 0 .25rem}
    .meta{color:#555;margin:0 0 1.25rem}
    .para{margin:1.25rem 0 2rem}
    .stamp{font-size:.875rem;color:#666;margin:.25rem 0 .5rem}
    img{display:block;max-width:100%;height:auto;border-radius:10px;margin:.25rem 0 0.75rem}
    hr{border:0;border-top:1px solid #eee;margin:1.5rem 0}
    """

    def rel_to_out(p: Path) -> str:
        try:
            return str(p.resolve().relative_to(out_path.parent.resolve()))
        except Exception:
            return str(p)

    items = sorted(paragraphs_manifest, key=lambda x: int(x.get("para_idx", 0)))

    parts = [
        "<!doctype html><html lang='en'><head>",
        "<meta charset='utf-8'>",
        f"<title>{html.escape(title)} — {html.escape(uploader)}</title>",
        f"<style>{css}</style></head><body>",
        f"<h1>{html.escape(title)}</h1>",
        f"<p class='meta'>by {html.escape(uploader)} · ID: {html.escape(video_id)}</p>",
        "<hr>"
    ]

    for item in items:
        idx = int(item.get("para_idx", 0))
        text = html.escape(item.get("text", ""))
        start = float(item.get("start", 0.0))
        end = float(item.get("end", start))

        img_tag = ""
        if embed_images and screencaps_dir:
            img_path = screencaps_dir / f"para-{idx:03d}.jpg"
            if img_path.exists():
                img_tag = f"<img src='{html.escape(rel_to_out(img_path))}' alt='Paragraph {idx:03d} frame'>"

        parts.append("<section class='para'>")
        if img_tag:
            parts.append(img_tag)
        parts.append(f"<div class='stamp'>[{_mmss(start)}–{_mmss(end)}]</div>")
        safe_text = text.replace("\n", "<br>")
        parts.append(f"<p>{safe_text}</p>")
        parts.append("</section>")

    parts.append("</body></html>")
    out_path.write_text("".join(parts), encoding="utf-8")
    return out_path