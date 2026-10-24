"""S2 spike: parse the corpus with PyMuPDF, Docling and GROBID into blocks
and score each against gold.json.

Usage:
    python fetch.py
    python run_s2.py [--parsers pymupdf,docling,grobid] [--grobid-url http://localhost:8070]

Writes results/<parser>-<doc>.json (blocks) and results/summary.json
(gitignored) and prints a markdown table.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict

from blocks import BlockBuilder, ParseResult, score, status_from_blocks

HERE = pathlib.Path(__file__).parent
DATA = HERE / "data"
RESULTS = HERE / "results"
CAP_SECONDS = 300  # reading-aid.md §3


def page_count(path: pathlib.Path) -> int:
    import pymupdf
    with pymupdf.open(path) as d:
        return d.page_count


# --------------------------------------------------------------- PyMuPDF
def join_lines(lines) -> str:
    """Join PDF lines; 'struc-' + 'tured' -> 'structured' when the next line starts lower-case."""
    out = ""
    for line in lines:
        line = line.strip()
        if out.endswith("-") and line[:1].islower() and out[-2:-1].isalpha():
            out = out[:-1] + line
        else:
            out = f"{out} {line}" if out else line
    return out


def parse_pymupdf(path: pathlib.Path, doc_id: str) -> ParseResult:
    """Text only; headings by font size/weight; kind from headings by rule."""
    import pymupdf

    t0 = time.perf_counter()
    doc = pymupdf.open(path)
    flags = pymupdf.TEXT_DEHYPHENATE | pymupdf.TEXT_PRESERVE_WHITESPACE
    pages = [p.get_text("dict", flags=flags) for p in doc]
    sizes = Counter()
    for pd in pages:
        for b in pd["blocks"]:
            for line in b.get("lines", []):
                for s in line["spans"]:
                    sizes[round(s["size"])] += len(s["text"])
    body = sizes.most_common(1)[0][0] if sizes else 10
    bb = BlockBuilder(doc_id)
    for pno, (page, pd) in enumerate(zip(doc, pages), 1):
        height = page.rect.height
        tabs = page.find_tables().tables
        trects = [pymupdf.Rect(t.bbox) for t in tabs]
        placed = set()
        for b in pd["blocks"]:
            if b["type"] != 0:
                continue
            r = pymupdf.Rect(b["bbox"])
            for i, tr in enumerate(trects):
                if i not in placed and r.y0 >= tr.y0 - 2:
                    t = tabs[i]
                    bb.table(t.to_markdown(), pno, tuple(t.bbox))
                    placed.add(i)
            if any((r & tr).get_area() > 0.5 * max(r.get_area(), 1) for tr in trects):
                continue
            lines = b["lines"]
            text = join_lines("".join(s["text"] for s in ln["spans"]) for ln in lines)
            if not text:
                continue
            if (r.y1 < 0.07 * height or r.y0 > 0.93 * height) and len(text) < 120:
                continue  # running header or footer
            s0 = lines[0]["spans"][0]
            bold = bool(s0["flags"] & 16) or "bold" in s0["font"].lower()
            looks_heading = (len(text) < 100 and len(lines) <= 3 and not text.endswith(".")
                             and not re.match(r"^(table|fig)", text, re.I)
                             and (s0["size"] >= body + 1 or (bold and s0["size"] >= body - 0.6)))
            if looks_heading:
                bb.heading(text)
            else:
                bb.add(text, pno, tuple(b["bbox"]))
        for i, t in enumerate(tabs):
            if i not in placed:
                bb.table(t.to_markdown(), pno, tuple(t.bbox))
    res = ParseResult("pymupdf", doc_id, doc.page_count, time.perf_counter() - t0, "ok",
                      bb.blocks, bb.headings, bb.tables)
    res.status = status_from_blocks(res.blocks, res.pages)
    return res


# --------------------------------------------------------------- Docling
_DOCLING = {}
DOCLING_ACCEL = {"device": "auto", "threads": None}  # set from --docling-device / --docling-threads


def docling_converter(ocr: bool):
    if ocr not in _DOCLING:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import AcceleratorOptions, PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption
        opts = PdfPipelineOptions()
        opts.do_ocr = ocr
        opts.do_table_structure = True
        accel = {"device": DOCLING_ACCEL["device"]}
        if DOCLING_ACCEL["threads"]:
            accel["num_threads"] = DOCLING_ACCEL["threads"]
        opts.accelerator_options = AcceleratorOptions(**accel)
        _DOCLING[ocr] = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})
    return _DOCLING[ocr]


def parse_docling(path: pathlib.Path, doc_id: str, ocr: bool = False) -> ParseResult:
    from docling_core.types.doc import DocItemLabel

    conv = docling_converter(ocr)
    t0 = time.perf_counter()
    doc = conv.convert(str(path)).document
    bb = BlockBuilder(doc_id)
    skip = {DocItemLabel.PAGE_HEADER, DocItemLabel.PAGE_FOOTER, DocItemLabel.PICTURE}
    for item, _level in doc.iterate_items():
        if item.label in skip:
            continue
        prov = item.prov[0] if getattr(item, "prov", None) else None
        page = bbox = None
        if prov:
            page = prov.page_no
            h = doc.pages[page].size.height
            bbox = prov.bbox.to_top_left_origin(page_height=h).as_tuple()
        if item.label in (DocItemLabel.SECTION_HEADER, DocItemLabel.TITLE):
            if item.label == DocItemLabel.SECTION_HEADER:
                bb.heading(item.text)
            else:
                bb.add(item.text, page, bbox, kind="other")
        elif item.label == DocItemLabel.TABLE:
            bb.table(item.export_to_markdown(doc=doc), page, bbox)
        else:
            bb.add(getattr(item, "text", ""), page, bbox)
    name = "docling+ocr" if ocr else "docling"
    res = ParseResult(name, doc_id, page_count(path), time.perf_counter() - t0, "ok",
                      bb.blocks, bb.headings, bb.tables)
    res.status = status_from_blocks(res.blocks, res.pages)
    return res


# --------------------------------------------------------------- GROBID
TEI = "{http://www.tei-c.org/ns/1.0}"


def _coords(el) -> tuple[int | None, tuple | None]:
    """First page and the union bbox on that page from GROBID 'coords' (page,x,y,w,h;...)."""
    raw = el.get("coords")
    if not raw:
        for child in el.iter():
            if child.get("coords"):
                raw = child.get("coords")
                break
    if not raw:
        return None, None
    boxes = [tuple(float(v) for v in part.split(",")) for part in raw.split(";") if part]
    page = int(boxes[0][0])
    same = [b for b in boxes if int(b[0]) == page]
    x0 = min(b[1] for b in same); y0 = min(b[2] for b in same)
    x1 = max(b[1] + b[3] for b in same); y1 = max(b[2] + b[4] for b in same)
    return page, (x0, y0, x1, y1)


def _text(el) -> str:
    return " ".join("".join(el.itertext()).split())


def parse_grobid(path: pathlib.Path, doc_id: str, url: str) -> ParseResult:
    import requests

    t0 = time.perf_counter()
    with open(path, "rb") as fh:
        r = requests.post(
            f"{url}/api/processFulltextDocument",
            files={"input": fh},
            data=[("teiCoordinates", c) for c in ("head", "p", "s", "figure", "biblStruct")]
                 + [("segmentSentences", "1")],
            timeout=CAP_SECONDS)
    seconds = time.perf_counter() - t0
    pages = page_count(path)
    if r.status_code != 200:
        return ParseResult("grobid", doc_id, pages, seconds, "failed",
                           error=f"HTTP {r.status_code}: {r.text[:200]}")
    root = ET.fromstring(r.content)
    bb = BlockBuilder(doc_id)
    abstract = root.find(f".//{TEI}profileDesc/{TEI}abstract")
    if abstract is not None and _text(abstract):
        bb.heading("Abstract")  # GROBID gives the abstract as a field, not a heading
        for p in abstract.iter(f"{TEI}p"):
            bb.add(_text(p), *_coords(p))

    def walk_div(div):
        for child in div:
            tag = child.tag.replace(TEI, "")
            if tag == "head":
                bb.heading(((child.get("n") or "") + " " + _text(child)).strip())
            elif tag in ("p", "formula", "list"):
                bb.add(_text(child), *_coords(child))
            elif tag == "div":
                walk_div(child)
            elif tag == "figure":
                handle_figure(child)

    def handle_figure(fig):
        page, bbox = _coords(fig)
        label = _text(fig.find(f"{TEI}head")) if fig.find(f"{TEI}head") is not None else ""
        desc = _text(fig.find(f"{TEI}figDesc")) if fig.find(f"{TEI}figDesc") is not None else ""
        if fig.get("type") == "table":
            table = fig.find(f"{TEI}table")
            bb.table(" ".join(x for x in (label, desc, _text(table) if table is not None else "") if x),
                     page, bbox)
        else:
            bb.add(" ".join(x for x in (label, desc) if x) or "[figure]", page, bbox, kind="figure_caption")

    body = root.find(f".//{TEI}text/{TEI}body")
    if body is not None:
        for el in body:
            tag = el.tag.replace(TEI, "")
            if tag == "div":
                walk_div(el)
            elif tag == "figure":
                handle_figure(el)
            elif tag in ("p", "formula"):
                bb.add(_text(el), *_coords(el))
    back = root.find(f".//{TEI}text/{TEI}back")
    if back is not None:
        for div in back.iter(f"{TEI}div"):
            if div.get("type") == "references":
                bibls = list(div.iter(f"{TEI}biblStruct"))
                if bibls:
                    bb.heading("References")
                for bs in bibls:
                    bb.add(_text(bs), *_coords(bs), kind="reference")
            elif div.get("type") in ("acknowledgement", "annex", "funding", "availability", "contribution"):
                if div.find(f"{TEI}head") is None:
                    bb.heading(div.get("type"))
                walk_div(div)
    res = ParseResult("grobid", doc_id, pages, seconds, "ok", bb.blocks, bb.headings, bb.tables)
    res.status = status_from_blocks(res.blocks, res.pages)
    return res


# --------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parsers", default="pymupdf,docling,grobid")
    ap.add_argument("--docs", default="nursing,socsci,cs,scan")
    ap.add_argument("--grobid-url", default="http://localhost:8070")
    ap.add_argument("--ocr-scan", action="store_true", help="also run Docling with OCR on the scan")
    ap.add_argument("--docling-device", default="auto", help="auto | cpu | mps | cuda")
    ap.add_argument("--docling-threads", type=int, default=None)
    ap.add_argument("--tag", default="", help="suffix for the summary file, e.g. -cpu2")
    args = ap.parse_args()
    DOCLING_ACCEL.update(device=args.docling_device, threads=args.docling_threads)
    gold = json.loads((HERE / "gold.json").read_text())
    RESULTS.mkdir(exist_ok=True)
    rows = []
    for parser in args.parsers.split(","):
        if parser == "docling":
            t0 = time.perf_counter()
            docling_converter(False).initialize_pipeline(
                __import__("docling.datamodel.base_models", fromlist=["InputFormat"]).InputFormat.PDF)
            print(f"docling model load: {time.perf_counter() - t0:.1f}s", file=sys.stderr)
        for doc_id in args.docs.split(","):
            path = DATA / f"{doc_id}.pdf"
            runs = [(parser, lambda: PARSERS[parser](path, doc_id, args))]
            if parser == "docling" and doc_id == "scan" and args.ocr_scan:
                runs.append(("docling+ocr", lambda: parse_docling(path, doc_id, ocr=True)))
            for name, fn in runs:
                try:
                    res = fn()
                except Exception as e:  # noqa: BLE001 - a spike records failures
                    res = ParseResult(name, doc_id, page_count(path), 0.0, "failed", error=repr(e)[:300])
                (RESULTS / f"{name}-{doc_id}.json").write_text(json.dumps(asdict(res), indent=1))
                row = score(res, gold[doc_id])
                rows.append(row)
                print(json.dumps(row), file=sys.stderr)
    (RESULTS / f"summary{args.tag}.json").write_text(json.dumps(rows, indent=1))
    cols = ["parser", "doc", "pages", "seconds", "status", "blocks", "page_bbox_pct", "headings",
            "spurious_headings", "kinds", "tables", "references", "limitation", "probes"]
    print("| " + " | ".join(cols) + " |")
    print("|" + "---|" * len(cols))
    for r in rows:
        print("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")


PARSERS = {
    "pymupdf": lambda path, doc_id, args: parse_pymupdf(path, doc_id),
    "docling": lambda path, doc_id, args: parse_docling(path, doc_id),
    "grobid": lambda path, doc_id, args: parse_grobid(path, doc_id, args.grobid_url),
}

if __name__ == "__main__":
    main()
