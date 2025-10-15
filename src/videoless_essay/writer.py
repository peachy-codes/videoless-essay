from sentence_transformers import SentenceTransformer
from textsplit.tools import SimpleSentenceTokenizer, get_penalty, get_segments
from textsplit.algorithm import split_optimal
import textwrap
import numpy as np
from typing import List, Dict, Tuple
import json

_PUNCT_END = (".", "!", "?", "…", ".”", "!”", "?”")

def _merge_segments_into_sentences(segments: List[Dict], min_chars: int = 40) -> List[Dict]:
    out: List[Dict] = []
    if not segments:
        return out

    cur_text = []
    cur_start = float(segments[0]["start"])
    first_idx = 0
    acc_len = 0

    def commit(last_idx: int, end_time: float):
        text = " ".join(t.strip() for t in cur_text).strip()
        if text:
            out.append({
                "text": text,
                "start": cur_start,
                "end": float(end_time),
                "whisper_first_idx": first_idx,
                "whisper_last_idx": last_idx
            })

    for i, seg in enumerate(segments):
        t = str(seg.get("text", "")).strip()
        if not t:
            continue
        cur_text.append(t)
        acc_len += len(t)
        end_punct = t.endswith(_PUNCT_END)

        # Lookahead signals
        next_starts_new = False
        if i + 1 < len(segments):
            nxt = segments[i + 1].get("text", "").lstrip()
            if nxt:
                # uppercase start or obvious boundary characters
                next_starts_new = (nxt[0].isupper() or nxt[0] in "\"'([“‘")

        should_commit = end_punct or (acc_len >= min_chars and next_starts_new)

        if should_commit:
            commit(i, seg["end"])
            # reset
            cur_text = []
            acc_len = 0
            if i + 1 < len(segments):
                cur_start = float(segments[i + 1]["start"])
                first_idx = i + 1

    # tail
    if cur_text:
        commit(len(segments) - 1, segments[-1]["end"])

    return out


def essay_writer(info:dict, segments: List[dict]) -> Tuple[str, List[dict]]:

    
    # whispers segments #fixed into sentences
    sent_items = _merge_segments_into_sentences(segments, min_chars=60)  # tune 40–80 if needed

    units = [s["text"] for s in sent_items]


    # embeddings
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    emb = model.encode(units, normalize_embeddings=True, show_progress_bar=True)
    docmat = np.asarray(emb, dtype=np.float32)

    # paragraph size
    avg_sentences_per_paragraph = 5

    # segmentation

    penalty = get_penalty([docmat], segment_len=avg_sentences_per_paragraph)
    seg = split_optimal(docmat, penalty=penalty)  # seg.splits are cut indices

    # index ranges from cut points
    cuts = list(seg.splits)
    boundaries = []
    prev = 0
    for c in cuts:
        boundaries.append((prev, c))
        prev = c
    boundaries.append((prev, len(units)))

    # 5) Materialize paragraphs from sentence list + segmentation w/ timestamps

    wrapped_paragraphs = []
    manifest: List[Dict] = []
    for i, (a,b) in enumerate(boundaries):
        if a >= b:
            continue
        para_text = " ".join(units[a:b]).strip()
        para_text_wrapped = textwrap.fill(para_text, width = 80)
        wrapped_paragraphs.append(para_text_wrapped)
        para_start = float(segments[a]["start"])
        para_end = float(segments[b -1]["start"])
        segment_ids = list(range(a,b))

        manifest.append({
            "para_idx": i,
            "start": para_start,
            "end": para_end,
            "segment_ids": segment_ids,
            "text": para_text
        })
    

    header_text = f"{info.get('title','')}\n\nby\n\n{info.get('uploader','')}"
    essay_text = header_text + "\n\n" + "\n\n".join(wrapped_paragraphs)

    return essay_text, manifest