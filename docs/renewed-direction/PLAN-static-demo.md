# PLAN — Static "video player" demo (from renew_proposal_v3.md)

Written 2026-10-20 by Opus for the next executor. Owner: Cyrus.
Input: [renew_proposal_v3.md](renew_proposal_v3.md) (owner's storyboard + master prompt). Do not edit it.

## What Cyrus asked for

"A slider / video, static only, with placeholder and nothing more."

So:
- **One HTML file that plays like a video.** 3 cases × 5 steps = 15 frames. Each frame is a fixed picture of the Room with a subtitle underneath.
- **No live parts.** No typing, no AI, no server, no internet. Nothing the audience can break.
- **Placeholder** = the student text, student names and course are clearly-marked sample content.
- **Nothing more.** No extra tabs, no games, no settings. Just the player.

## Why not use the v3 master prompt as-is

v3 is a great storyboard (the player bar, 3 cases × 5 steps and the "Git for ideas" look all stay). But it brings back problems we already fixed in v2:

| Problem in v3 | Why it hurts | Fix |
|---|---|---|
| Bloom "2023, +13.5%, N=1,000 data-entry" | Wrong. It's 2013, 13%, 249 call-centre volunteers | Use [sources-verified.md](sources-verified.md) S1 |
| Gibbs "Table 3", "−42% mentorship", "junior −11.4%, senior +4.2%", "N=1,200" | **Not in the paper.** Real: 10,000+ staff, hours +~30%, output flat, productivity −~20%, less coaching | Use S2. Delete Table 3 |
| Pentland 2022 "3.2x patents" | Could not be found. Looks invented | Replace with S3 Emanuel et al. (+18.3% feedback, mostly less-tenured staff) |
| Q2 "15.6-point tenure gap", Q3 "3.2x" | Built on the fake numbers | New questions below |
| "Cheater", "Caught", "Detected", "X-Ray", "Liability", "Boomerang Trap" | Breaks CLAUDE.md law 10 | v2 wording table |
| "90s Oral Viva", `01:30` countdown | We promised no timers | "Request a spoken answer", no clock |
| "PR Blocked" until you anchor, "You must revise Para 1 and 3" | Brings back #5 (extra work for honest students) and works as a free editing service | Coach *asks*, never blocks. Neutral note: "Paragraph 2 and Paragraph 1 now say different things" |
| "Authorship Verified via commit lineage" | Overclaims. Typing history isn't proof (law 5) | "Idea history: 'seniority tax' first appears in commit 103c" |
| "85% of the paste rewritten" | Made-up number | "Rewritten: 3 of 3 paragraphs" (counted from our own frames) |
| Tailwind + Lucide from CDN | Dies without wifi in the meeting room | Inline CSS + inline SVG. Works offline by double-click |

Good news: the real data tells the "seniority tax" story *better*. Gibbs says longer-tenure staff raised output slightly and coaching fell. Emanuel says sitting near teammates gives feedback mostly to less-tenured engineers, while experienced engineers write less code. That's a real seniority tax, with real citations.

---

## Step 1 — Build `demo.html`

- **Where:** `writing-room-kit/web/static/demo.html`. Also add a `/demo` route in [app.py](../../writing-room-kit/web/app.py), the same way `/vision` was added. The file must also work opened straight from Finder (`file://`).
- **Leave `vision.html` alone.** It stays as the clickable version.
- **No external files at all.** No CDN, no fonts from the web, no images. System font stack.

### Screen layout (one frame)

```
┌ Top bar: "The Writing Room" · [Case 1 Honest] [Case 2 Pasted draft] [Case 3 Full offload] ┐
├──────────────┬──────────────────────────────┬──────────────────────────┤
│ Sources (3)  │ Essay (3 paragraphs)          │ Commit log + Coach note  │
│ + Set aside  │ red/green diff when the frame │ (newest commit on top)   │
│   box        │ says so                       │                          │
├──────────────┴──────────────────────────────┴──────────────────────────┤
│ Subtitle: "Step 2 of 5 — ..." (big, high contrast)                       │
│ [⏮] [◀] [▶ Play / ⏸] [▶▶]   ●──●──○──○──○  progress line                 │
└──────────────────────────────────────────────────────────────────────────┘
```

- Narrow screens (400px): the columns stack and the player bar stays pinned at the bottom.
- A small grey label in the corner says: "Sample student work · Source quotes are real (see sources)".

### Player behaviour (the only "logic")

- Next and Prev buttons, the → ← keys and Space for play/pause. Restart.
- Play moves one step every **7 seconds** (3.5s is too short to read a subtitle aloud). At step 5 it goes on to the next case and stops at the end of case 3. This is the presenter's autoplay, never a clock shown to a student.
- Clicking a step dot or a case pill jumps there.
- The thing that changed in this frame gets a soft highlight (no motion if the computer has reduce-motion turned on).
- `#case2-step3`-style hash so a link can open a given frame.
- **One live extra (recommended, easy to cut):** on Case 3 step 5, a "🔊 Read question 1 aloud" button using `speechSynthesis`. It's the best moment in the pitch and needs no server.

### Data: build every frame from a single `FRAMES` array

Each frame holds the source states, paragraphs (with `<del>`/`<ins>` where needed), commits, coach note, an optional banner and the subtitle. No frame may contain a number that isn't in `sources-verified.md`.

---

## Step 2 — The storyboard (real data, safe wording)

### Sources (left column, the same in every case)

- **S1 Confirming:** Bloom, Liang, Roberts & Ying (2013), NBER WP 18871.
  - Quote: "Home working led to a 13% performance increase, of which about 9% was from working more minutes per shift (fewer breaks and sick-days) and 4% from more calls per minute…"
  - Method note: one company (CTrip), call-centre volunteers, 9 months, 249 employees.
- **S2 Complicating:** Gibbs, Mengel & Siemroth (2021), IZA DP 14336.
  - Quotes: "Total hours worked increased by roughly 30%…" / "Average output did not significantly change. Therefore, productivity fell by about 20%." / "…received less coaching and 1:1 meetings with supervisors."
  - Method note: one company (a large Asian IT services firm), 10,000+ professionals, Covid period.
- **S3 Adjacent:** Emanuel, Harrington & Pallais, NBER WP 31880 (June 2026 revision).
  - Quotes: "sitting near teammates increases coding feedback by 18.3%…" / "Gains are concentrated among less-tenured and younger employees…" / "experienced engineers write less code when sitting near teammates."

Badges per frame: `✓ Used in Para N` / `⚠ Not yet addressed` / `⤵ Set aside`. Each badge has an icon and a text label as well as a colour.

### Case 1 — Honest (0 → 1)

| Step | Commit | What changes on screen | Subtitle |
|---|---|---|---|
| 1 | 101a "My hunch before reading" | Para 1: "Remote work is good for tech firms: people skip the commute and focus at home." Coach: "Hunch saved. Three sources are open on the left." | The student writes a rough hunch first, before reading anything. |
| 2 | 102b "Bloom fits, Gibbs doesn't — why?" | Para 1 links S1. Para 2 note: "Bloom: +13%. Gibbs: hours up ~30% but output flat. Why so different?" Coach asks: "Look at who each study measured. Does your Para 1 claim fit both?" | The Coach asks. It never writes a sentence for the student. |
| 3 | 103c "New idea: a seniority tax" | Diff. Para 1: ~~Remote work is good for tech firms.~~ → "Remote work can lift output in routine, measurable jobs (+13% at one call centre [S1]), but in skilled team work it quietly shifts costs onto newer staff: a 'seniority tax'." Para 2: "At one large IT firm, hours rose ~30%, output stayed flat, and coaching and 1:1s fell [S2]." | The student's own idea appears here, and the diff keeps a record of it. |
| 4 | 104d "Added S3: who loses feedback" | Para 3: "Sitting near teammates raised coding feedback by 18.3%, mostly for less-tenured engineers, while experienced engineers wrote less code [S3]. Someone pays the tax either way." Coach: "All three sources are used." | Every claim points to a real passage in a real paper. |
| 5 | 105e "Smoothed sentences with an AI tool; kept my structure" | Polished prose. Badge: "Idea history: 'seniority tax' first appears in commit 103c, in the student's words." | Using AI to polish is fine. The thinking is visible in the history. |

### Case 2 — Pasted draft

| Step | Commit | What changes on screen | Subtitle |
|---|---|---|---|
| 1 | (pasted, no message) | 3 smooth generic paragraphs. P1 "…boosts productivity and innovation at every level". P2 "…with async tools and daily video stand-ups, mentorship stays strong". P3 "…firms should close offices; there are no real downsides." Sources: S2 and S3 show "⚠ Not yet addressed". Coach: "Para 2 talks about mentorship. Which passage supports it?" | No accusation. Every student gets the same question. |
| 2 | 201a "Added Gibbs to Para 2" | Diff in P2: ~~mentorship stays strong~~ → "staff received less coaching and fewer 1:1s with supervisors [S2]." Amber note between paragraphs: "Paragraph 2 and Paragraph 1 now say different things." Also P2 vs P3. | A quick patch in one paragraph breaks the others. Faking gets expensive. |
| 3 | 202b "Narrowed Para 1 to call-centre work" | P1 rewritten to limit Bloom to call-centre volunteers [S1]. The note now shows P2 vs P3 only. | To fix Para 1 they have to read who Bloom actually studied. |
| 4 | 203c "Rewrote the conclusion" | P3 rewritten using S3: keep new hires near teammates. Notes clear. | Para 2 forced Para 1, which forced Para 3. |
| 5 | 204d "Final" | Summary chip: "Pasted: 3 paragraphs · Rewritten: 3 of 3". | We don't claim we stopped them. Faking cost about as much as thinking, and the 3 questions still come with the essay. |

### Case 3 — Full offload

| Step | Commit | What changes on screen | Subtitle |
|---|---|---|---|
| 1 | 301a "Thesis built on Bloom" | One-sided essay, every claim on S1. Neat commits. | A strong AI tool can fake neat, step-by-step commits. |
| 2 | 302b "Set aside Gibbs" | S2 moves to Set aside with the pill "One company only, can't generalise" and a slick AI-written note. | Instead of facing Gibbs, the student sets it aside with a smart-sounding reason. |
| 3 | 303c "AI chat tools replace in-person feedback" | P3 makes a claim with no source. | On the surface everything is filled in. Can a stronger AI win here? Inside the screen, yes. |
| 4 | — Same standard? check | Side by side: **Set aside:** Gibbs, one company. **Relied on:** Bloom, also one company (CTrip). Label: "A reasoning check, not a verdict." | The same filter was used on one source but not the other. |
| 5 | — Understanding Receipt | Process profile (not a verdict). Suggested next step: "A short spoken answer is recommended. The teacher decides." 3 defend-it questions (below). "🔊 Read question 1 aloud" button. | The real check is a person hearing a 30-second answer. A student who did the thinking finds it easy. |

### The 3 defend-it questions (Case 3)

1. "You set aside Gibbs et al. because it studies one company. Your Paragraph 1 rests on Bloom et al., which also studies one company. Why did that filter apply to one and not the other?"
2. "Gibbs et al. found hours rose about 30% while output stayed flat. Your essay says remote work 'boosts productivity'. What does productivity mean in your essay, and is that what Gibbs measured?"
3. "Emanuel et al. found that sitting near teammates raised feedback mostly for less-tenured engineers. Your Paragraph 3 says AI chat tools replace that. What evidence would convince you?"

---

## Step 3 — Self-check

- [ ] Every number and quote is in `sources-verified.md`. Grep for `13.5|1,000|1,200|42|11.4|4.2|3.2x|Pentland|Table 3`: zero hits.
- [ ] Banned words: grep `detect|catch|caught|cheat|liabilit|x-ray|landmine|boomerang|verified authorship|spyware` gives zero hits.
- [ ] No timers: grep `countdown|01:30|90s|90-second` gives zero hits.
- [ ] Opens offline by double-click. There are no `http` URLs in `src=` or `href=` for scripts or styles.
- [ ] All 15 frames render at 1440px and 400px. Keys and Play work. Play stops after case 3 step 5.
- [ ] Light and dark mode are both readable.
- [ ] Test with jsdom (as was done for vision.html) and do one real check in a browser.

## Step 4 — Optional: an actual video file (MP4)

Only if Cyrus wants a backup that plays without a browser:
- Simplest: Cyrus records the screen with QuickTime while pressing Play.
- Automatic: use headless Chrome to screenshot the 15 frames, then ffmpeg to join them at 7s each. Check first that both tools are installed.

## Not in scope

The 15-student test, live citation check, bookkeeping docs and commits all wait until Cyrus asks.
