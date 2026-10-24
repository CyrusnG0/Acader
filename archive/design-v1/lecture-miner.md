# M2 — Visual Lecture Miner

**Status:** **validated** prototype (prior session, 2026-10-11). **Code is not in this repo (OL-002).**
**Implements:** proposal §2, §8.8 · **Open loops:** OL-002, OL-011

## 1. Goal
Extract structured **board states** from real lecture video automatically, including progressive chalkboard writing. A board state is the fullest version of a board just before it is erased, with timestamps.

## 2. Pipeline (as validated)
1. **Sample:** ffmpeg at 1 fps.
2. **Downscale:** each frame becomes a 32×32 grayscale grid.
3. **Smooth:** apply an EMA over the grids (α = 0.08). The EMA absorbs transients such as the professor walking past the board.
4. **Auto-tune thresholds** from the video's own statistics, using **EMA drift** rather than raw frame drift. Raw drift breaks under constant motion.
5. **Segment:** close a segment on confirmed drift **or** sustained low ink (a wipe or erase).
6. **Representative frame = argmax ink** within the segment, which is the fullest board before erasing. Cap board-like ink at **0.45** so title cards cannot win on ink.
7. **Dedupe:** merge re-shown boards and keep the fullest version.

Output: `states.csv` (one row per state with timestamps) plus representative frames. Contact sheets are made by `make_sheet.py`.

CLI (prototype): `python3 lecture_miner.py VIDEO.mp4 --outdir out [--fps 1] [--max-seconds 600]`

## 3. Validation results
- **Real video:** MIT 18.06 Lecture 1 (Gilbert Strang, chalkboard, 40 min, 480×360). Source: archive.org `MIT18.06S05_MP4/01.mp4`. Produced **159 board states** in about 1 min of CPU with no ML cost.
- **Ground truth:** a synthetic chalkboard video from `gen_synth.py` with known answers. Snapshots landed within **~0.3 s** of truth, and re-shown boards merged into their fullest version.

## 4. Calibration lessons (do not rediscover these)
- **dHash cannot see thin chalk.** Different boards differ by ≤ 6/64 bits, so do not use perceptual hashes for change detection on chalk.
- **Professor walk-throughs are transients** that only the EMA absorbs.
- **Naive auto-thresholds break under constant motion.** Threshold on EMA drift, not raw drift.
- **Title cards game ink metrics.** Cap board-like ink at 0.45.

## 5. Known limits → production work (OL-011)
- State lists are fine-grained **ladders**. That suits a teaching KB, but production needs a **semantic-clustering pass** to group a ladder into one teaching moment.
- Board re-appearances shorter than about 8 s can be missed.
- Title cards and non-board frames need **VLM QA** (M6). Hybrid rule: pixels scan, the VLM judges, and only candidates are sent to it.
- Validated only on chalkboard so far. **[ASSUMPTION]** Slide decks and whiteboards should be easier, but they need their own test videos.

## 6. Files (from prior session; to be committed under `miner/`)
| File | Purpose |
|---|---|
| `lecture_miner.py` | Working extractor |
| `make_sheet.py` | Contact sheets for visual review |
| `gen_synth.py` | Synthetic ground-truth video generator |
| `strang_out/states.csv` | 159 states from MIT 18.06 L1 |
| demo contact sheets | Visual evidence |
