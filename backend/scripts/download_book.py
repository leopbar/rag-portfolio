"""
Downloads The Wealth of Nations from Project Gutenberg and strips the
Gutenberg header/footer, leaving only the book's actual content.

Usage:
    python scripts/download_book.py
"""

import re
from pathlib import Path

import httpx

GUTENBERG_URL = "https://www.gutenberg.org/files/3300/3300-0.txt"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "wealth-of-nations.txt"

START_MARKER = "INTRODUCTION AND PLAN OF THE WORK"
END_MARKER = "End of the Project Gutenberg"


def download(url: str) -> str:
    print(f"Downloading from {url} ...")
    response = httpx.get(url, follow_redirects=True, timeout=60)
    response.raise_for_status()
    return response.text


def clean(raw: str) -> str:
    start = raw.find(START_MARKER)
    end = raw.find(END_MARKER)

    if start == -1:
        print("WARNING: start marker not found — check the Gutenberg file format")
        start = 0
    if end == -1:
        print("WARNING: end marker not found — using full file")
        end = len(raw)

    content = raw[start:end]

    # Normalize excessive blank lines (3+ → 2)
    content = re.sub(r"\n{3,}", "\n\n", content)

    return content.strip()


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    raw = download(GUTENBERG_URL)
    cleaned = clean(raw)

    OUTPUT_PATH.write_text(cleaned, encoding="utf-8")
    size_kb = OUTPUT_PATH.stat().st_size // 1024
    print(f"Saved to {OUTPUT_PATH} ({size_kb} KB, {len(cleaned):,} characters)")


if __name__ == "__main__":
    main()
