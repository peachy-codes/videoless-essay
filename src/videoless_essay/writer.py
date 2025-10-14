from sentence_transformers import SentenceTransformer
from textsplit.tools import SimpleSentenceTokenizer, get_penalty, get_segments
from textsplit.algorithm import split_optimal
import textwrap
import numpy as np
import json

def essay_writer(info:json, text:str) -> str:

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

    header_text = info['title'] + "\n\n" + "by" +  "\n\n" + info['uploader'] # technically fstrings are more performant 

    output_text = "\n\n".join(wrapped_paragraphs)  # blank line between paragraphs

    output_text = header_text + "\n\n" + output_text # gross and should be cleaned up

    return output_text