#!/usr/bin/env python3
"""
Convert a .srt file to a plain-text .txt, dropping index numbers, timestamps,
and blank lines.

Usage:
    python srt2txt.py input.srt [output.txt]

Note: the file you tried to attach seems to have expired—re-upload it if you’d
like me to verify the output.
"""
import re
import sys
from pathlib import Path

TS_RE = re.compile(r"\d{2}:\d{2}:\d{2},\d{3}")  # matches 00:00:00,000


def srt_to_txt(src_path: str, dst_path: str | None = None) -> None:
    src = Path(src_path)
    dst = Path(dst_path) if dst_path else src.with_suffix(".txt")

    with src.open(encoding="utf-8") as fin, dst.open("w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if (
                not line              # blank
                or line.isdigit()     # subtitle index
                or TS_RE.search(line) # timestamp line
            ):
                continue
            fout.write(line + "\n")

    print(f"Wrote {dst}")


srt_to_txt("/Users/nic/test/test.srt")