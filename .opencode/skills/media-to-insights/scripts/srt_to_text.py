#!/usr/bin/env python3
"""Convert srt/vtt subtitle files into clean timestamped plain text.

Usage:
    python3 srt_to_text.py <file.srt|file.vtt> [out.txt]

Detects the container format automatically (srt and vtt cues both use
HH:MM:SS(.ddd) --> ... lines). Strips HTML tags, cue styling, timing lines,
index numbers, and empty cues. Writes lines as  [HH:MM:SS] <text> and a
second plain file (stem + "_plain.txt") without timestamps.

Prints a summary (cue count / word count) to stdout.
"""
import re
import sys
from pathlib import Path

TIME_RE = re.compile(
    r"^\s*(?P<start>\d{1,2}:\d{2}:\d{2})(?:[.,]\d{1,3})?\s*-->\s*\d{1,2}:\d{2}:\d{2}"
)
HTML_RE = re.compile(r"<[^>]+>")


def parse_cues(text: str):
    """Yield (start_ts, cleaned_text) for each cue in srt or vtt text."""
    text = text.replace("\ufeff", "").replace("\r\n", "\n")
    cues = []
    for block in re.split(r"\n\n+", text.strip()):
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        ts = None
        ts_index = None
        for i, l in enumerate(lines):
            m = TIME_RE.match(l)
            if m:
                ts, ts_index = m.group("start"), i
                break
        if ts is None:
            continue  # not a cue block (index-only / header)
        body = lines[ts_index + 1:]
        t = clean(" ".join(body))
        if t:
            cues.append((ts, t))
    return cues


def clean(text: str) -> str:
    text = HTML_RE.sub("", text)          # html fragments (<c>, <i>, <v ...>)
    text = re.sub(r"{\\[^}]+}", "", text) # ASS-style inline styling
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = Path(sys.argv[1])
    raw = src.read_text(encoding="utf-8", errors="replace")
    cues = [(ts, t) for ts, t in parse_cues(raw) if t]

    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".txt")

    with out.open("w", encoding="utf-8") as f:
        for ts, t in cues:
            f.write(f"[{ts}] {t}\n")

    plain = out.with_name(out.stem + "_plain.txt")
    with plain.open("w", encoding="utf-8") as f:
        for _, t in cues:
            f.write(t + "\n")

    words = sum(len(t.split()) for _, t in cues)
    print(f"cues={len(cues)} words={words} -> {out.name} (+ {plain.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())