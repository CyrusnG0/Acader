# PLAN — Renewed Proposal v2 (fix the demo before anyone sees it)

Written 2026-10-19 by Opus for the next executor (Sonnet). Owner: Cyrus.
Input: [renewed_proposal.md](renewed_proposal.md) (the owner's draft, including the pitch at the end).
Owner agreed to the fixes below on 2026-10-19.

## 0. Read first (10 min)

1. [CLAUDE.md](../../CLAUDE.md) §4. These are the product laws. Law 6 (never a cheat report) and law 10 (no surveillance words) matter most here.
2. [renewed_proposal.md](renewed_proposal.md), the whole file including the pitch.
3. [HANDOFF-v0.4.md](HANDOFF-v0.4.md) §2. Two rules from it apply here: honest students must never do extra work just to look honest, and there are no timers.
4. [outsider.md](outsider.md) for the relay attack and the 15-student blind test.

**Hard rules for this work**
- **Never invent a number, quote, table or author.** Every fact about a source must be copied from the real paper, with a page or table reference. If you can't verify something, drop it or mark it `[UNVERIFIED]`. This product sells "the source really says it", so a made-up quote in the demo would sink it.
- **Do not edit `renewed_proposal.md`.** It is the owner's original. Write a new file, `renewed_proposal_v2.md`.
- No commits. Don't touch the DeepSeek key or any secrets.
- Reply to Cyrus in plain, simple English.

## The two problems we're fixing

- **#2: a smart student can still fake it.** They can ask an outside AI to regenerate a whole essay that hangs together, so "Coherence Collapse" does not stop them. The new story: we don't try to win inside the screen. Faking costs about as much as thinking, and the 3 questions plus a short spoken answer are the real check.
- **#5: honest students get extra work.** The required form, required notes and highlighting all add steps. The new rule: every step must replace something the student already had to do. Otherwise it stays optional.

---

## Step 1: Verify the real sources (do this first; everything else depends on it)

Create `sources-verified.md` at the repo root. For each source, record:
- the full citation and its URL or DOI
- 2–4 **exact** quotes, each with a page, section or table reference
- the real sample size and setting
- one line: "what this source can and can't support"

Use WebFetch or WebSearch on the real PDFs:

| Slot | Paper | Known facts (check them again) | Draft errors to fix |
|---|---|---|---|
| Confirming | Bloom, Liang, Roberts & Ying, "Does Working from Home Work? Evidence from a Chinese Experiment", *QJE* 2015 (NBER WP 18871, 2013) | Run at Ctrip, a travel-agency call centre, with volunteers randomly assigned for 9 months. **+13% performance**, of which about 9 points came from more minutes worked (fewer breaks and sick days) and about 4 points from more calls per minute (quieter). Lower quitting. Promotion rate conditional on performance fell. | The draft says "2023", "13.5%" and "1,000 data-entry staff". All three are wrong. |
| Complicating | Gibbs, Mengel & Siemroth, "Work from Home and Productivity: Evidence from Personnel and Analytics Data on IT Professionals", *JPE Microeconomics* 2023 (IZA DP 14336) | More than 10,000 skilled IT professionals at one large Asian/Indian IT firm. Hours rose, **including +18% outside normal business hours**. Output was roughly flat, so productivity fell about **8–19%**. More meeting and coordination time. Less coaching and fewer 1:1s with supervisors. Longer-tenure staff fared better. | The draft says "18% total hours", "-42% junior mentorship", "Table 3 Junior -11.4%" and "sample 1,200". None of these are in the paper. Use the real table and figure numbers. |
| Junior / mentorship (new) | Emanuel, Harrington & Pallais, "The Power of Proximity: Office Interactions and Feedback" (NBER WP 2023) | Software engineers at a Fortune 500 firm, comparing teams that sat together with teams split across buildings. Sitting near teammates raised the online feedback engineers received, **especially for junior engineers**, and senior engineers produced less of their own output. **Get the exact % from the paper.** | This replaces the made-up "-42% junior mentorship". It is the real evidence for the "seniority tax" idea. |
| Mechanism (replaces "Pentland 2022") | Yang et al., "The effects of remote work on collaboration among information workers", *Nature Human Behaviour* 2022 (Microsoft) | Firm-wide remote work made collaboration networks more static and siloed, with fewer bridging ties across groups, and moved communication toward asynchronous channels. **Get the exact numbers.** | "Pentland 3x patents watercooler" could not be verified and looks invented. Drop it. |

If any of the four can't be fetched or checked, say so in `sources-verified.md` and pick a replacement you *can* verify. Don't fill gaps from memory.

**Rebuild the double-standard example on true facts.** Bloom and Gibbs are both **single-company studies**, so the cross-check still works:
> The student discards Gibbs because it is "one company only, can't generalize", but builds Paragraph 1 entirely on Bloom, which is also one company (Ctrip).

Do not use sample-size wording: Gibbs has more than 10,000 people, so a "too small" complaint would be absurd.

**Rebuild the hardcoded demo data from `sources-verified.md` only:**
- the Triad cards and their spans
- the mini data table: use a real table from the paper, or remove the table
- the inquiry questions
- the Scenario A, B and C inputs
- the Reviewing Room's three flawed sentences

Each flawed sentence must misstate a *real* finding, and the "fix" must point to the *real* quote.

## Step 2: Write `renewed_proposal_v2.md`

Copy the structure of the original, then apply all of these changes.

### 2a. Swap the wording (screen text and pitch)

| Old | New |
|---|---|
| Cheater / One-Shot LLM Cheater / Super-Prompt Cheater | Pasted draft / Full offload |
| Detected / catches / Premise Collision Detected | Reasoning gap / "These two paragraphs disagree" |
| Liability Questions / Liability Extraction | Defend-it questions |
| Instructor X-Ray Receipt | Understanding Receipt |
| "3 devastating Oral questions" | "3 questions about the student's own choices" |
| Epistemic Double-Standard Detected | Same standard? (a reasoning check) |
| Landmines Defused | Flaws found |
| Coherence Telemetry | Process profile (not a verdict) |

When you're done, grep the file for `detect|catch|cheat|liabilit|devastat|x-ray|spyware|landmine`. There must be zero hits in screen text or pitch lines. Private notes for Cyrus can keep "Mic-drop" and "Savage", but put them in a clearly marked "presenter notes only" section.

### 2b. Rewrite the claim about #2

- In §1 Core Thesis and in pitch Act 2, replace "breaks the cheater / they hit a wall" with this:

> "We don't try to win inside the screen; a strong AI will always win there. We do two things. Faking costs about as much as thinking, because the questions are about this student's own sources and choices. And every submission comes with 3 questions a student who did the thinking answers in 30 seconds."

- Keep the Coherence Collapse demo, but caption it **"faking gets expensive"**, not "we stopped them".
- Remove the live banner text "You must rewrite Para 1 & Para 3". It works as a free editing service. Use a neutral note instead: "Paragraph 2 and Paragraph 3 now say different things."
- **Move the Q1 "Welcome to the AI era" answer up so it becomes the closing line of the main pitch.** In the Q&A, replace it with a short version.
- Keep Q2 ("inside the screen a stronger model always wins…"), with the wording swapped.

### 2c. Fix the timer contradiction

- Remove the 90-second countdown everywhere: the modal, Act 4 and the spec in §4 Block 4.
- The oral becomes **"Request a spoken answer"**: one spoken answer with no visible clock, and a typed alternative for students who need it.
- Keep `speechSynthesis` reading Question 1 aloud. That's the demo moment.
- Q3's answer ("zero forced countdown timers") is then true. Keep it.

### 2d. Fix #5 (no extra work for honest students)

- The Socratic form is **optional** and is presented as "your outline". It replaces outlining instead of adding a step.
- Graveyard: **one click on a reason pill**. The 10-word note is optional.
- Highlighting a span to cite: pitch it as *less* work, because it formats the citation and checks it against the real paper in one step. This is our real-world citation selling point.
- Replace "twice as fast" with **"less busywork"** everywhere, and add `[ASSUMPTION — to be measured in pilot]`.

### 2e. Add one line to the demo end

The last beat of Act 4 links to the live room:
> "This mockup shows the vision. This part already runs for real: [live room link]."

The live room is `writing-room-kit/web/` (see [writing-room-kit/web/DEPLOY.md](../../writing-room-kit/web/DEPLOY.md)). Cyrus deploys it himself.

## Step 3: Build the clickable mockup

- **Where:** `writing-room-kit/web/static/vision.html`. Add one route in [writing-room-kit/web/app.py](../../writing-room-kit/web/app.py) (`/vision` → that file), so the mockup and the live room sit on the same host.
- **How:** a single HTML file with React 18 UMD from cdnjs (exact pinned version), Tailwind play CDN (pinned), and plain inline SVG icons (no Lucide build). There is no build step. All data is hardcoded from `sources-verified.md`.
- **What:**
  - 3 tabs: Writing Room, Reviewing Room, Understanding Receipt.
  - Scenario switcher: A Honest, B Pasted draft, C Full offload. It must update everything.
  - Paste & patch animation.
  - Reviewing Room linking with a "Flaws found n/3" counter.
  - Receipt with:
    - the Same-standard check
    - the seed-to-prose diff
    - 3 defend-it questions
    - a "Request a spoken answer" modal that speaks Q1 aloud (no countdown)
  - The footer links to `/` (the live room).
- **Accessibility, as the proposal promises:**
  - every action works by keyboard-accessible button (no drag-and-drop)
  - visible focus rings
  - targets of at least 32px
  - every colour paired with an icon and text
- It must work at 400px width.

## Step 4: Self-check before reporting

- [ ] Every number and quote in v2 and in `vision.html` appears in `sources-verified.md` with a page or table reference.
- [ ] The banned-word grep (2a) returns zero hits outside presenter notes.
- [ ] No countdown or timer anywhere (grep `countdown|90s|90-second|timer`).
- [ ] "twice as fast" is gone.
- [ ] `uvicorn app:app --port 8780` serves both `/` and `/vision`. Click through all 3 scenarios and all 3 tabs. The speech button speaks.
- [ ] Original `renewed_proposal.md` is unchanged (`git diff --stat` shows nothing for it; it is untracked, so compare against a copy you save first).

Report to Cyrus in plain English:
- what changed
- which facts you could not verify
- the local URLs

## Step 5: Next, only after Step 4 (ask Cyrus first)

1. **15-student blind test** (proof for #2). Add a section to [writing-room-kit/PILOT-PROTOCOL.md](../../writing-room-kit/PILOT-PROTOCOL.md):
   - 3 groups: honest, essay first with a faked process, outside AI driving live
   - teachers judge the receipt alone, then the receipt plus the 3 questions answered out loud
   - the measure is how much the spoken answer improves their judgement
2. **Real citation check in the live room:**
   - DOI or URL import
   - a Crossref lookup to confirm the source exists
   - a passage match against the source text
3. **Bookkeeping, only when Cyrus says go:** STATUS, UPDATE_LOG, CHANGELOG, OPEN_LOOPS and DECISIONS. Record the decision that "Real-world citation replaces the sealed corpus; spoken answer is the gate; no countdown".
