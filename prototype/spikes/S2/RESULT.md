# Spike S2: which PDF parser? (result)

- **Task:** T-006 · **Spec:** [design/reading-aid.md §3](../../../design/reading-aid.md), [design/evaluation.md §1 (S2)](../../../design/evaluation.md) · **Date:** 2026-10-24 · **By:** lead-opus-T006
- **Question (evaluation.md):** can we parse real readings into usable blocks?
- **Pass bar:** block kinds and tables usable on ≥ 2 of 3 readings; limitation passages found; the scan reports "scan".

## Verdict

**GO with Docling** (OCR off), preceded by a pypdfium2 text-layer check that gives a scan the status "scan" before any model loads. Docling is the only parser of the three that passes the S2 bar on all three readings. Two things must be settled before it ships: the memory it needs (4.3 GB peak on an 86-page paper) and baking its models into the image. The parser choice is a **proposed decision** for the founder, not a decision (see the T-006 handoff).

| Parser | S2 bar | Why |
|---|---|---|
| **Docling 2.142.1** | **pass, 3/3** | Kinds 22/22, tables 27/27 with cell structure, headings 37/38, references ≈ 1 block per entry, scan → "scan" |
| PyMuPDF 2.0 | pass on quality, but see licence | Kinds 21/22, tables 29/27 (two extra), but noisy headings (108 spurious), references split into 1.6–1.9 blocks per entry. **AGPL-3.0** (see below) |
| GROBID 0.8.2 (CRF image) | **fail** | Tables 5/27: the nursing tables come back as figures, so tables are usable on only 1 of 3. The scan returns HTTP 500 instead of a status |

## Corpus

All openly licensed. The PDFs are **not committed**: `fetch.py` downloads them into `data/` (gitignored); [corpus.json](corpus.json) holds each URL and licence.

| id | Role (evaluation.md) | Source | Licence | Pages |
|---|---|---|---|---|
| nursing | nursing paper with tables | Fukuda, Sakurai, Kashiwagi, *PLOS ONE* 15(2): e0228458 (2020), doi:10.1371/journal.pone.0228458 | CC BY 4.0 | 9 |
| socsci | social-science working paper | *Unintended Consequences of Sanitation Investment…*, arXiv:2607.29371v1 [econ.GN] | CC BY 4.0 | 86 |
| cs | CS paper | *Tracing Recurrent and Emergent Hallucination Patterns in Decomposed Text-to-SQL Generation*, arXiv:2610.27720v1 [cs.CL] | CC BY 4.0 | 11 |
| scan | scanned PDF | First 4 pages of *nursing*, rasterised at 150 dpi greyscale, no text layer (`make_scan()` in fetch.py) | CC BY 4.0 (derivative) | 4 |

The scan is **synthetic**: a real photocopy with no text layer looks the same to a parser, but a scanner that adds its own OCR layer would not (see Limits).

Ground truth is in [gold.json](gold.json), labelled by hand from the PDFs: the main section headings, the kinds a reader would expect, table count, an approximate reference count, one limitation passage, and two "probe" phrases that cross a hyphenated line break (quote matching at compile, D29, needs `struc-`/`tured` joined).

## Method

`run_s2.py` runs each parser and maps its output onto the reading-aid block shape `{block_id, page, bbox, section, kind, text}` through **one shared rule** (`blocks.py`): section headings set the kind by keyword (method, results, discussion, limitation…), unmatched headings inherit the kind of their parent, captions starting "Table n" or "Figure n" become `table` or `figure_caption`. All three parsers share this rule, so the comparison measures segmentation, headings, tables and coordinates, not three different classifiers.

- **PyMuPDF:** text blocks from `get_text("dict")`; a heading is a short block in larger or bold type; tables from `find_tables()`; running headers and footers dropped by position; a line-join rule that removes end-of-line hyphens.
- **Docling:** `DocumentConverter` with `do_ocr=False`, table structure on; items in reading order; page headers, footers and pictures dropped.
- **GROBID:** `processFulltextDocument` with coordinates on heads, paragraphs, sentences, figures and references; TEI mapped to blocks (abstract from the header, `biblStruct` entries as references). Run as the official `grobid/grobid:0.8.2-crf` Docker image (the lighter image without deep-learning models). It is linux/amd64 only, so it ran under emulation on this arm64 Mac.

Hardware: Apple M5 Pro, 18 cores, 48 GB RAM, macOS; Python 3.14 in a scratch venv (the prototype targets 3.12).

## Results

Times are for the parse call only, with models already loaded. "Docling cpu2" is Docling forced to CPU with 2 threads, closer to a small hosted machine. GROBID's first request took 22.5 s (JVM warm-up); the times below are warm.

| Parser | Doc | Pages | Seconds | Status | Blocks | page+bbox | Headings | Spurious headings | Kinds | Tables | Refs (blocks/≈gold) | Limitation passage | Hyphen probes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pymupdf | nursing | 9 | 1.4 | ok | 100 | 100% | 15/16 | 7 | 8/8 | 3/3 | 28/28 | discussion p7 | 2/2 |
| pymupdf | socsci | 86 | 10.5 | ok | 646 | 100% | 10/11 | 69 | 6/7 (no abstract) | 23/21 | 110/~68 | results p27 | 2/2 |
| pymupdf | cs | 11 | 1.6 | ok | 186 | 100% | 11/11 | 32 | 7/7 | 3/3 | 46/~25 | limitation p8 | 2/2 |
| pymupdf | scan | 4 | 0.2 | **scan** | 0 | | | | | | | | |
| docling | nursing | 9 | 4.9 (cpu2 4.0) | ok | 102 | 100% | 16/16 | 8 | 8/8 | 3/3 | 28/28 | discussion p7 | 2/2 |
| docling | socsci | 86 | 20.1 (cpu2 31.3) | ok | 490 | 100% | 11/11 | 43 | 7/7 | 21/21 | 77/~68 | results p27 | 2/2 |
| docling | cs | 11 | 2.0 (cpu2 3.5) | ok | 150 | 100% | 10/11 | 30 | 7/7 | 3/3 | 25/~25 | limitation p8 | 2/2 |
| docling | scan | 4 | 0.4 | **scan** | 0 | | | | | | | | |
| docling + OCR | scan | 4 | 12.8 | ok (text recovered) | 39 | 100% | | | | | | | |
| grobid | nursing | 9 | 1.8 | ok | 71 | 100% | 16/16 | 10 | 8/8 | **0/3** | 28/28 | discussion p7 | 2/2 |
| grobid | socsci | 86 | 4.5 | ok | 347 | 98% | 11/11 | 40 | 7/7 | **5/21** | 75/~68 | results p27 | 2/2 |
| grobid | cs | 11 | 1.9 | ok | 142 | 99% | 10/11 | 32 | 7/7 | **0/3** | 25/~25 | limitation p8 | 1/2 |
| grobid | scan | 4 | 1.1 | **failed** (HTTP 500 `NO_BLOCKS`) | 0 | | | | | | | | |

"Spurious headings" counts every heading the parser returned that is not in the gold list. Many are real subsections and appendix headings that gold does not list, so the numbers compare parsers with each other; they are not error rates. Gold reference counts for socsci and cs are approximate.

### What the numbers mean for reading-aid.md §3

- **Blocks and page mapping.** All three give every block a page and a box. Spot-checks of Docling boxes against the PDF text under the box matched (4/4). Paragraph segmentation is comparable; PyMuPDF splits more (646 vs 490 blocks on socsci) because it follows PDF drawing blocks, not paragraphs.
- **Headings and kinds.** Docling and GROBID found 37/38 gold headings, PyMuPDF 36/38. PyMuPDF's misses and noise come from its font rule: the socsci "Abstract" is set smaller than body text, so no abstract kind; author lines, the arXiv stamp and bold run-in phrases become "headings". Docling merges words in a few headings ("RelatedWork", "EvaluationMetrics": missing glyph spaces). GROBID missed "3 Dataset" in cs and turned a table header and an author-contribution line into headings.
- **Tables.** Docling returns all 27 tables with rows and columns (Markdown export), with the caption attached. PyMuPDF's `find_tables()` found every table plus two extra, with some header cells duplicated. GROBID's CRF image labelled the nursing tables as figures and found 5 of 21 socsci tables. GROBID's full image with deep-learning models might do better: **[ASSUMPTION]**, not tested (the image is far larger).
- **References.** GROBID and Docling give about one block per entry. GROBID also parses each entry into authors, title, year and DOI, which the citation help (§6) could use later. PyMuPDF splits entries across blocks (1.6–1.9 blocks per entry), so it cannot count or link references without extra rules.
- **Limitation passages.** All three put the passage in the same block and section, so the result depends on the paper, not the parser. cs has a "Limitations" heading → `kind = limitation` directly. nursing has the sentence inside Discussion → found only through the `limitation_tag` LLM call that §3 already plans. socsci has no Discussion section; its one limitation remark sits in Results, so **neither the limitation pin nor `limitation_tag` (discussion blocks only) would surface it**. That is a design observation for the reading-aid owner, not a parser issue.
- **Scan.** PyMuPDF and Docling (OCR off) return no text, so the rule "fewer than 50 characters per page → scan" gives the status "scan". GROBID returns an HTTP 500 error, which the caller would have to map. A pypdfium2 text-layer check (`scancheck.py`) gets the same answer in under 0.1 s for all four PDFs and does not depend on the parser, so it should run first. Docling with OCR on recovered the scan's text in 12.8 s for 4 pages; v1 does not need this (§3 tells the teacher to upload a text version), but it is available later.
- **Speed vs the 300 s cap.** Docling on 2 CPU threads: 0.36 s per page → a 300-page reading ≈ 110 s on this machine. A small cloud vCPU may be 2–3× slower (≈ 220–330 s): **[ASSUMPTION]**, so the 300 s cap could bite on the longest readings. PyMuPDF: 0.12 s per page. GROBID: 0.05 s per page warm, but on a separate service.

### Install weight, licence and runtime

| | PyMuPDF 2.0 | Docling 2.142.1 | GROBID 0.8.2-crf |
|---|---|---|---|
| Runs as | Python library, in process | Python library, in process (fits "in the jobs loop") | Separate Java service (Docker), called over HTTP |
| Install | 264 MB venv (PyMuPDF 110 MB; 2.0 now also pulls onnxruntime, numpy, networkx) | 1.6 GB venv (torch 590 MB, transformers 119 MB) + ~1.0 GB models (layout 328 MB, table/other 683 MB) downloaded on first use | Image 537 MB compressed, 1.73 GB on disk; linux/amd64 only |
| Peak memory (socsci, 86 pages) | 0.64 GB | **4.3 GB** (cpu, 2 threads) | 2.5 GB resident when idle |
| Model load | none | 4.5 s warm; 75 s on first run (download) | JVM warm-up ≈ 20 s on first request |
| Licence | **AGPL-3.0 or Artifex commercial** | MIT (code); models CDLA-Permissive-2.0 and Apache-2.0; RapidOCR Apache-2.0 | Apache-2.0 |

**The PyMuPDF licence matters.** We would run it inside a hosted service. AGPL-3.0 §13 then obliges us to offer the source of the whole service to its users, unless we buy Artifex's commercial licence. That is a founder and legal question, not an engineering one, and it rules PyMuPDF out as the default unless the founder accepts it. (This spike uses PyMuPDF only as a measuring tool, outside the product.)

## Recommendation

1. **Docling, OCR off, table structure on**, in the jobs loop, with the shared heading rule in `blocks.py` as the starting point for `sources/parse`.
2. **Text-layer check first** with pypdfium2 (already a Docling dependency): under 50 characters per page → status "scan" without loading Docling.
3. **Bake the models into the image** (no download at boot) and load the converter once per worker.
4. **Size the host for it:** one parse at a time, at least 8 GB RAM. Before M2, test whether Docling's page batch size lowers the 4.3 GB peak, and time a 300-page reading on the real host. If it misses the 300 s cap, parse in page ranges.
5. **Don't use GROBID for v1 parsing.** Keep it in mind for reference metadata in citation help (§6) after the pilot.
6. **Don't use PyMuPDF in product code** unless the founder accepts AGPL or buys a licence.

## Limits of this spike

- 3 readings + 1 scan, one machine (Apple M5 Pro), Python 3.14 rather than 3.12. Timings on the pilot host will differ.
- The scan is synthetic. A real scan that carries a poor OCR layer from the scanner passes the text-layer check and gets parsed as text; S2 did not test that case.
- Gold labels were set by the same person who wrote the adapters; the reference counts for socsci and cs are approximate.
- GROBID was tested only in its CRF image, under amd64 emulation; its full deep-learning image was assessed from documentation only: **[ASSUMPTION]**.
- Docling's memory was measured once, with default batch settings.

## Reproduce

```bash
cd prototype/spikes/S2
python3.12 -m venv .venv && .venv/bin/pip install -r requirements-spike.txt   # .venv is gitignored
docker run -d --rm --name s2-grobid -p 8070:8070 grobid/grobid:0.8.2-crf
.venv/bin/python fetch.py                       # downloads into data/ and builds data/scan.pdf
.venv/bin/python scancheck.py data/*.pdf
.venv/bin/python run_s2.py --ocr-scan           # all parsers, table on stdout, blocks in results/
.venv/bin/python run_s2.py --parsers docling,grobid --docs nursing,socsci,cs \
    --docling-device cpu --docling-threads 2 --tag=-cpu2
```
