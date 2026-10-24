# Privacy, consent and data ownership

Status: **reviewed (CEO + eng) 2026-10-23; must be completed (provider terms, school approval) before any real student** · Last updated: 2026-10-23
Implements: law 7, the privacy floor in [PRODUCT.md](../PRODUCT.md) §6; CEO-6, CEO-8, CEO-12, CEO-20, CEO-22; D3, D9, D12, D14, D16, D30, D31 ([eng record](../docs/designs/eng-review-v1.md)). Answers OL-037, OL-016 and OL-019 (partly).
Replaces: [archive/design-v1/data-isolation.md](../archive/design-v1/data-isolation.md).

## 1. Principles

1. **The student owns the process record.** The school gets the receipt and derived signals. The full log goes to the school only if the student shares it.
2. **Record what changed in the text, not how you typed it.** No keystroke timing, typing rhythm, reading dwell, webcam, screen capture, biometrics, or browser activity outside the platform. Editor changes enter the record once per 5 minutes (D12, D16, D30).
3. **Tenant isolation.** Course materials and parsed blocks stay inside the school's tenant. Nothing is used to train models.
4. **Minimum to the LLM.** Each call gets only the blocks, cards and spans it needs. Never the full log, never names. **The mapper** (D-035) gets only the paragraphs changed in that 5-minute batch, the student's claim texts and the titles of anchored blocks; with `mapper_enabled` off, nothing is sent while the student writes (eng review v2 D5).
5. **Plain-language consent before any capture**, per assignment.

## 2. Data inventory

| Data | Personal data? | Stored where | Who sees it | Retention (default) |
|---|---|---|---|---|
| Account (name, email, class) from the roster | Yes | DB | Student, teacher of that class | Until the student or school deletes it |
| Event log | Yes (writing and actions) | DB (SQLite on one machine in the consented region; backups in the same region, D3) | Student; operators only for support with permission | Course end + 90 days **[ASSUMPTION: set with each school]** |
| Stored AI outputs behind each receipt (D31) | Yes (about the student's text) | DB, with the log | As the event log; in export and delete | As the event log |
| Final document and checkpoints | Yes | DB | Student, teacher (final only) | As the event log |
| Declared import raw text | Yes, possibly third-party AI output | DB | Student only, unless shared | As the event log |
| Receipt | Yes | DB; HTML (printable) | Student, teacher, school file | School's assessment-record policy |
| Course readings and blocks | Copyrighted material | DB / disk, per tenant | Course members | Course end + 90 days, or the teacher deletes them |
| Teacher audit rows (opens, exports) | Yes (teacher) | DB | Operators, school on request | As the event log |
| Logs and counters | No student text, no keys (D15) | Log files | Operators | 90 days |
| Prompt and response text at the LLM provider | Yes (spans of student writing) | Provider | Provider under its terms | Provider's terms (OL-037) |
| Sign-in emails | Email address | Transactional email provider | — | Provider's terms |

## 3. Processors and the provider question (OL-037)

Processors to name in consent and in the school's approval:
- **The Writing Room itself**, approved by the university as a data processor: DPA or privacy impact assessment, IT security review, a signing entity (CEO-22).
- **The LLM provider the school picks**: DeepSeek (D-029, China-based) or the second backend, a generic OpenAI-compatible endpoint such as the school's own Azure OpenAI tenant (CEO-6, D14).
- **The hosting provider** and region (one machine; backups in the same region).
- **The transactional email provider** for sign-in links and the seal email (CEO-8).

No embedding provider: v1 has no embeddings (D1). The PDF parser runs inside our own server.

Before the first real student:
1. Quote each provider's current data terms (retention, training use, location) in `docs/research/`.
2. Check HK PDPO cross-border duties and the university's own rules.
3. Confirm the second backend is available in HK (D14).
4. Get research-ethics approval if any survey or publication is planned (CEO-12, OL-026).

Nothing about any provider's terms is assumed here.

## 4. Consent (per assignment)

Shown before the editor opens; readable in under a minute; the teacher co-signs the wording.

**Draft text (to finalise with OL-016):**
> **What this platform records.** What you add, change and paste in your writing (saved in 5-minute steps); which parts of your readings you open and quote; your questions to the Helper and answers to the Coach; anything you choose to bring in from outside.
> **What it doesn't record.** Your typing speed or rhythm, how long you spend reading, your camera or screen, anything outside this page.
> **Who sees what.** Your teacher sees a one-page receipt about how the work was built, not your full history. You see a preview first: the facts and which parts might be asked about, but not the questions themselves. Your full history is yours to export or delete.
> **AI.** Parts of your writing and readings are sent to [provider, location] to generate questions. *[Only in the version shown when the mapper is on:]* While you write, changed paragraphs are also sent every few minutes to suggest links on your map. Suggestions never change what counts as traced; they can shape the questions your teacher may ask. It does not write your work.
> **You can stop.** You can write elsewhere and submit through your usual route instead; ask your teacher how. *(The school must offer this route for the pilot.)*

**Two versions (eng review v2 D20).** The consent text comes with and without the mapper line. The `mapper_enabled` value is fixed per record at `log.open` and stored with `consent_version`; switching the flag on mid-pilot affects only records opened afterwards.

## 5. Student rights in the product

- **Export:** the full log (JSON), stored AI outputs, the document, the receipt (HTML) and the seal hash, from one button.
- **Delete:** before submission → the log is deleted, no receipt. After submission → `record.withdrawn`; the receipt reads "record withdrawn by the student"; a copy already filed by the school stays under the school's policy. Between submit and release the wording is set in [receipt.md](receipt.md) §7 (P-15, design review 9A).
- **Correct:** notes and links after submit are new events; nothing is overwritten.
- **Accessibility route:** dictation, screen readers and assistive input are `typed`, with `input_kind` kept only as counts. They never change bands or questions.

## 6. Security for the pilot (D9, D11)

- TLS everywhere; secrets in the host's secret store (never in the repo; `.env` is gitignored).
- **Every query goes through one repo layer** that requires (tenant, role, owner). A **route-enumeration test** tries a foreign ID on every route and expects 404.
- Student text is rendered as text only, under a **strict CSP** (default-src 'self', no inline script).
- **Teacher opens and exports** are recorded in an audit table.
- **Sign-in:** roster only; an email not on the roster gets no session. The invite link opens a page, and a button POSTs the token. Tokens are single use, expire in 30 minutes, are bound to the roster email and are stored hashed.
- Rate limits and per-student LLM budgets.
- Operator access to student logs needs a recorded reason and is itself logged.
- Backups in the consented region, with a restore test before the pilot.
