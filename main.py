#!/usr/bin/env python3
"""Entry point for the make.fun news-image bounty, 26 November 2026.

Copies the finished front page (entry.png, shipped in this repo) to
/output/entry.png, where the grader looks for it. Pure standard library
— it reads and writes bytes only and never draws, edits, or re-renders
the image, so the output is byte-identical to entry.png every run.
"""

import os
import shutil


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    target_dir = "/output"
    os.makedirs(target_dir, exist_ok=True)
    shutil.copyfile(source, os.path.join(target_dir, "entry.png"))


if __name__ == "__main__":
    main()
