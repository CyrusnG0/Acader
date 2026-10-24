"""Parser-independent scan check: does the PDF have a text layer?

Uses pypdfium2 (BSD-3/Apache-2.0; already a Docling dependency). Run before
parsing so a scan gets status "scan" without loading any model.
Usage: python scancheck.py data/*.pdf
"""
import sys
import time

import pypdfium2 as pdfium

from blocks import SCAN_MIN_CHARS_PER_PAGE


def text_layer_status(path: str) -> tuple[str, int, int]:
    pdf = pdfium.PdfDocument(path)
    chars = 0
    for page in pdf:
        chars += len(page.get_textpage().get_text_range().strip())
    pages = len(pdf)
    status = "scan" if chars < SCAN_MIN_CHARS_PER_PAGE * max(pages, 1) else "ok"
    return status, pages, chars


if __name__ == "__main__":
    for p in sys.argv[1:]:
        t0 = time.perf_counter()
        status, pages, chars = text_layer_status(p)
        print(f"{p}: {status} ({pages} pages, {chars} chars, {time.perf_counter() - t0:.2f}s)")
