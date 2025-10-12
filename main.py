"""
Usage:
    python3 --url <url> --output_filename <file_name> --save_video <flag> --save_audio <flag>
"""


#import libraries
 
import yt_dlp
import whisper
import subprocess
import argparse
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from textsplit.tools import SimpleSentenceTokenizer, get_penalty, get_segments
from textsplit.algorithm import split_optimal
import textwrap

def arguments_parser():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--url",
        type=str,
        required=True,
        help="Entire YouTube URL: https://www.youtube.come/watch?v=<VIDEO_ID>"
        )
    
    p.add_argument(
        "--output_filename",
        type=str,
        default="output.txt",
        help="The output filename for the transcribed audio: <output_filename>.txt"
    )

    return p.parse_args()




if __name__ == "__main__":
    args = arguments_parser()
    print(f"url: {args.url}")
    print(f"output name: {args.output_filename}")

    URL = [args.url]

    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }

    ydl = yt_dlp.YoutubeDL(ydl_opts)

    info = ydl.extract_info(URL[0], download=True)
    #info = json.dumps(ydl.sanitize_info(info))
    #error_code = ydl.download(test_URL)
    #print(info)
    #print(f"Expected filename is: {info['title']} [{info['id']}].mp3")

    audio_file = f"{info['title']} [{info['id']}].mp3"

    model = whisper.load_model("small")  # pick "base", "small", "medium", "large" if desired

    result = model.transcribe(
        audio_file,
        task="transcribe",
        language="en",
        temperature=0.0,
        best_of=1,
        beam_size=1,
        condition_on_previous_text=False,
        fp16=False
    )

    text = result['text']
    sentences = SimpleSentenceTokenizer()(text)  # regex-based sentence splitter

    # 2) Encode sentences to embeddings (L2-normalized)
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    emb = model.encode(sentences, normalize_embeddings=True, show_progress_bar=False)
    docmat = np.asarray(emb, dtype=np.float32)

    # 3) Choose average sentences per paragraph (target granularity)
    avg_sentences_per_paragraph = 5

    # 4) Calibrate penalty from desired segment length, then run optimal DP
    #    get_penalty expects a list of docmats and returns a penalty scalar.
    penalty = get_penalty([docmat], segment_len=avg_sentences_per_paragraph)
    seg = split_optimal(docmat, penalty=penalty)  # seg.splits are cut indices

    # 5) Materialize paragraphs from sentence list + segmentation
    segments = get_segments(sentences, seg)  # list of lists of sentences
    paragraphs = [" ".join(seg).strip() for seg in segments if seg]

    wrapped_paragraphs = []
    for p in paragraphs:
        wrapped = textwrap.fill(p, width=80)  # 80 chars per line is standard
        wrapped_paragraphs.append(wrapped)

    output_text = "\n\n".join(wrapped_paragraphs)  # blank line between paragraphs

    destination_file_title = f"No-Video Essay{info['title']} [{info['id']}"

    Path(f"{destination_file_title}.txt").write_text(output_text, encoding="utf-8")
    print(f"Saved nicely formatted paragraphs to {destination_file_title}.txt")