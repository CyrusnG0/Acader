"""Fetch the S2 corpus into data/ (gitignored) and build the scanned PDF.

Usage: python fetch.py        (needs pymupdf; see RESULT.md "Reproduce")
PDFs are never committed: corpus.json holds each source URL and licence.
"""
import json
import pathlib
import urllib.request

import pymupdf

HERE = pathlib.Path(__file__).parent
DATA = HERE / "data"
SCAN_PAGES = 4
SCAN_DPI = 150


def download(url: str, dest: pathlib.Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Acader-S2-spike/0.1 (research)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read()
    if not body.startswith(b"%PDF"):
        raise RuntimeError(f"{url} did not return a PDF")
    dest.write_bytes(body)


def make_scan(src: pathlib.Path, dest: pathlib.Path) -> None:
    """Rasterise the first pages to images: a PDF with no text layer, like a photocopy scan."""
    doc = pymupdf.open(src)
    out = pymupdf.open()
    for page in list(doc)[:SCAN_PAGES]:
        pix = page.get_pixmap(dpi=SCAN_DPI, colorspace=pymupdf.csGRAY)
        new = out.new_page(width=page.rect.width, height=page.rect.height)
        new.insert_image(new.rect, pixmap=pix)
    out.save(dest, deflate=True)


def main() -> None:
    DATA.mkdir(exist_ok=True)
    corpus = json.loads((HERE / "corpus.json").read_text())
    for item in corpus:
        dest = DATA / f"{item['id']}.pdf"
        if not dest.exists():
            if item["url"]:
                download(item["url"], dest)
            else:
                make_scan(DATA / f"{item['derived_from']}.pdf", dest)
        print(f"{item['id']}: {dest.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
