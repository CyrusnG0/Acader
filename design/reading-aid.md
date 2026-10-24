# Sources, the reading aid and citation help

Status: **reviewed (CEO + eng) 2026-10-23** · Last updated: 2026-10-23
Implements: D-027 ("help students read; never summarise"), laws 1, 3, 4 and 8; CEO-1, CEO-9; D1, D4 ([eng record](../docs/designs/eng-review-v1.md)). Answers OL-033; folds in OL-004 (citation backend).

## 1. The rule

> Nobody should have to read 40 pages cold when tools exist, but the tool must not read *for* the student.

The aid **points to places to read**. The student reads them and writes the takeaway in their own words, as an idea card anchored to the passage. That card starts a traced chain. A summary would break the chain and break law 1.

**Allowed:** "Table 3 splits results by tenure." · "The limitations are on p. 14." · definitions of terms.
**Not allowed:** "This paper argues…" · "The key finding is…" · "In summary…" · any sentence the student could paste as an argument.

## 2. Where sources come from (v1)

| Origin | How it enters | Parsed? |
|---|---|---|
| Teacher readings | Upload PDF/DOCX/text at assignment setup | Yes |
| Lecture material | Slides, notes or transcripts as text/PDF (no video mining) | Yes |
| The Door | Pasted text or uploaded files, declared by the student. **URLs are stored as links and never fetched** (CEO-9) | Text and files only |

Student scholarly search (OpenAlex/Crossref) is deferred to TODOS (CEO-1).
Licensing **[ASSUMPTION]**: we parse only teacher uploads under the school's licence. Check with the pilot school.

## 3. Parsing into blocks (D4)

Each source becomes **blocks**: `{block_id, page, bbox, section, kind, text}`.
- `kind` ∈ abstract, introduction, method, results, table, figure_caption, discussion, limitation, conclusion, reference, other.
- Parser: **Docling** (spike S2, D-043): OCR off, table structure on, models baked into the image, one converter per worker, one parse at a time. It runs **hosted, in the jobs loop**. No PyMuPDF in product code (AGPL-3.0). GROBID for reference metadata is deferred (TODOS).
- **Text-layer check first:** pypdfium2 (a Docling dependency); fewer than 50 characters per page → status "scan", no model loaded.
- **Host:** at least 8 GB RAM. Before M2, measure Docling's peak memory and time a 300-page reading on the real host; if it misses the 300 s cap, parse in page ranges.
- **Caps:** 50 MB, 300 pages, 300 s per parse. Over the cap → rejected with the limit shown.
- **Status shown to the teacher per reading:** processing, ok, scan (no text layer: "This PDF is a scan; upload a text version"), failed.
- **Immutable after first student open.** A re-upload creates a new version; existing anchors keep pointing at the old one.
- Limitation passages inside discussion sections are tagged by one LLM call per discussion block at parse time (task `limitation_tag`), cached per source, not per student.
- No embeddings in v1 (D1).

## 4. Reading pins (v1: by section kind only)

For an open source, the aid shows pins by block kind:

| Pin | Retrieval | Text shown (a pointer, fixed template) |
|---|---|---|
| Limitation | `kind = limitation`, or a tagged discussion block | "p. 14: limitations" |
| Data | `kind = table / figure_caption` | "Table 2" |
| Method | `kind = method` | "§3: method" |
| Results | `kind = results` | "p. 6: results" |

- Pointers come from fixed templates, so no LLM text is shown and nothing can leak.
- Pins are logged (`aid.pins_shown`, `aid.pin_opened`). Opening a limitation pin feeds "thinking moments".
- **Deferred to TODOS** (CEO-1): LLM-directed support/skeptical pins per claim, lecture pins, and the Triad suggestion.

## 5. Reader actions

| Action | Effect | Event |
|---|---|---|
| Select a passage → "Make a card" | Card editor opens beside the passage (not pre-filled); the student types the takeaway. Pasted characters in the card are recorded (D26) | `card.create`, `card.anchor` |
| "Quote this" | Inserts the exact quote with citation into the draft, marked `quote` (checked at compile, D29) | `editor.insert_quote`, `cite.format` |
| "Where does it say…?" | Helper search inside this source; returns block locations | `helper.serve` |
| "What does this term mean?" | Helper definition (general, not about the paper's argument) | `helper.serve` |
| "Set aside" | Reason pill (different setting / out of scope / method concern / will address in text) + optional note | `card.set_aside` |

All single clicks, keyboard-reachable, targets ≥ 24 px.

## 6. Citation help

- **Formatting:** CSL styles (APA 7 default) via citeproc. Metadata from Crossref by DOI, else manual entry.
- **Verification:** the DOI resolves; a `quote` matches its block (exact, or fuzzy ≥ 0.95).
- A failed check is an open note to the student ("We couldn't find this DOI. Check it?"). It is **feedback, never a provenance signal** (v0.4: outside AI cites accurately).

## 7. Cost

Parsing and limitation tagging run once per source per course. Pins use no LLM calls in v1.

## 8. Open questions

- Should "Make a card" hide the passage while typing to push paraphrase? Default: side by side. Revisit with the pilot teacher.
