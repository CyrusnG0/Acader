# THE WRITING ROOM: Socratic Inquiry & Coherence Telemetry IDE
**Master Product Proposal & High-Fidelity Prototype Specification (Wizard-of-Oz Demo)**

---

## 1. Executive Product Philosophy (For Claude Context)
You are building a single-page, high-fidelity interactive React prototype (`App.jsx`) using **Tailwind CSS** and **Lucide-React** icons. 

**Core Thesis:** 
In the AI era, policing keystrokes or trying to detect AI prose is dead. Instead, **The Writing Room** acts as a **Dynamic Socratic Inquiry Form & Source-Confrontation Workbench**. 
- **For Honest Students (0 to 1):** The platform lowers cognitive friction by surfacing conflicting real literature ("Triads") and guiding them through a structured inquiry form (Skeleton -> Evidence -> Prose) that helps them architect a sharp paper.
- **For One-Shot LLM Cheaters (1 to 0):** If a student pastes a pre-generated essay from an external LLM, the platform does not block or accuse them. Instead, it pairs their essay with **Targeted Inquiry Questions** anchored to specific, conflicting micro-data in the library. When a cheater tries to patch their pre-written essay paragraph-by-paragraph to answer these questions, their essay suffers **Coherence Collapse** (fixing Paragraph 2 breaks the premise of Paragraph 4). By the time they iterate enough to make the form, the exact source spans, and the essay coherent, they have been forced to dissect the problem and learn the material.
- **Strict Boundary:** The platform never generates prose for the student and never grades the paper. It is a **Diagnostic Mirror** that outputs a **60-Second X-Ray Receipt** for the human instructor (plus 3 hyper-targeted oral/written follow-up questions).

---

## 2. Design System & Accessibility (WCAG 2.2 AA Compliant)
- **Aesthetic:** Clean, academic research IDE (inspired by Linear, Notion, and Elicit).
- **Color Palette:** 
  - Background: `bg-slate-50` / Panels: `bg-white` with `border-slate-200`.
  - Primary Accent: `indigo-600` (Architecture & Inquiry).
  - Semantic Badges: Confirming Source (`emerald-600`), Complicating/Counter Source (`amber-600`), Coherence Warning/Conflict (`rose-600`).
- **WCAG 2.2 AA Built-in Features (Crucial for University Procurement):**
  - **No Drag-and-Drop Required (WCAG 2.5.7):** Every spatial action (linking a passage, anchoring a claim, auditing a flaw) works via explicit, keyboard-accessible click buttons (`[+ Anchor Span]`, `[Link to Claim #2]`) with visible focus rings (`focus:ring-2 focus:ring-indigo-600`).
  - **Target Size (WCAG 2.5.8):** All interactive controls have a minimum hit area of `32x32px`.
  - **Color Independence:** Every status color is paired with an explicit icon and text label (`[✓ Aligned]`, `[⚠ Coherence Gap]`).

---

## 3. Global Navigation & Demo Switcher
Build a sticky top header containing:
1. **Brand Title:** `The Writing Room` + Subtitle badge: `Socratic Inquiry & Coherence Telemetry v2.6`
2. **Assignment Context Pill:** `SOC-304: Remote Work & Junior Innovation (Prof. Vance)`
3. **3 Core View Tabs:**
   - **Tab 1: `1. The Writing Room (Guided Inquiry IDE)`**
   - **Tab 2: `2. The Reviewing Room (Red-Pen Audit Mode)`**
   - **Tab 3: `3. Instructor X-Ray Receipt (60s Assessment)`**
4. **Live Demo Scenario Switcher (Top Right Toolbar):**
   A segmented control that dynamically populates the entire app state so the presenter can demonstrate every edge case in one click:
   - **`Scenario A: Honest Iterative Thinker (0 -> 1)`** (Shows natural rough notes, balanced source selection, resolved tensions, and high coherence).
   - **`Scenario B: 1-Shot LLM Paste -> Coherence Collapse`** (Simulates a student pasting a polished ChatGPT essay and trying to patch it—exposing contradictions between Paragraph 1 and Paragraph 3).
   - **`Scenario C: "Super-Prompt" Sophisticated Offloader`** (Simulates a student who used an advanced LLM to fill out every form box perfectly—demonstrating how the **Receipt's Cross-Audit** catches their double-standard and generates 3 devastating Oral/Interview questions).

---

## 4. Detailed View Specifications & Hardcoded Golden Data

### VIEW 1: The Writing Room (3-Column Guided Inquiry IDE)

#### Left Column (30% width): The Triad Source Broker & Raw Data
- **Step 1 Gate (Claim-First Input):** Display the student's initial hunch box at the top:
  - *Hardcoded Initial Hunch:* `"Remote work boosts productivity because employees skip commuting and have fewer office distractions."`
- **The Surfaced Source Triad (3 Expandable Cards with Clickable Spans):**
  - **Source 1 [Confirming - Emerald Badge]:** *Bloom et al. (2023), NBER Working Paper.*
    - **Clickable Span `[S1-A]`:** `"Full-time remote data-entry staff showed a 13.5% output increase due to quieter home environments and reduced sick leave."`
    - **Method Note:** `Sample: 1,000 call-center & data-entry workers (routine tasks).`
  - **Source 2 [Complicating Counter-Source - Amber Badge]:** *Gibbs, Mengel & Siemroth (2024), Journal of Political Economy.*
    - **Clickable Span `[S2-A]`:** `"While total hours worked rose by 18%, net output remained flat, and mentorship interactions for junior engineers (<2 yrs tenure) dropped by 42%."`
    - **Embedded Mini Data Table (`Table 3`):**
      | Tenure Group | Output Change | Unscheduled Knowledge Spillover |
      | :--- | :--- | :--- |
      | Senior (>5 yrs) | +4.2% | -8% |
      | **Junior (<2 yrs)** | **-11.4%** | **-42% (p < 0.01)** |
  - **Source 3 [Adjacent Mechanism - Indigo Badge]:** *Pentland (2022), MIT Media Lab.*
    - **Clickable Span `[S3-A]`:** `"Breakthrough patents correlate 3x stronger with asynchronous cross-team 'watercooler collisions' than scheduled Zoom meetings."`
- **Graveyard Action:** Each source card has a `[Discard Source]` button that requires selecting a reason pill (`Sample Mismatch`, `Out of Scope`, `Flawed Method`, `Will Refute in Text`) + a 10-word note.

#### Middle Column (35% width): The Structured Socratic Survey (The "Dissection Form")
Instead of blank notes, display **3 Progressive Inquiry Cards** that pair with the essay paragraphs. Students can answer in rough notes; the system tracks how these answers link to the essay on the right.

- **Inquiry Module #1: Scope & Definition Boundary**
  - *System Question:* `"Source 1 (Bloom) measures routine call-center output, while your prompt asks about 'Junior Innovation'. How are you narrowing your definition of productivity?"`
  - *Scenario A (Honest) Input:* `"I need to split routine output from creative innovation. Bloom only proves routine tasks work remotely."`
  - *Scenario B (1-Shot Paste) Input:* `"[Unanswered / Generic]: Remote work increases overall efficiency across modern digital industries."`
- **Inquiry Module #2: The Triad Tension Bridge (Reconciling `[S1-A]` vs. `[S2-A]`)**
  - *System Question:* `"You anchored Bloom (+13.5% output) in Para 1, but Gibbs Table 3 shows Junior output dropped -11.4% with a -42% mentorship loss. How do you reconcile this conflict without contradicting Para 1?"`
  - *Stance Selector Pills:* `[Limit Claim to Seniors]` `[Argue Async Tools Replace Mentorship]` `[Pivot Thesis to Hybrid Model]`
  - *Scenario A (Honest) Input:* `"Pivoting thesis: Remote work is a 'seniority tax'—seniors cash in on quiet focus, while juniors pay the price in lost osmosis."`
  - *Scenario B (1-Shot Paste Patch) Input:* `"Junior employees struggle remotely because they lack mentorship (-42%), so remote work harms productivity."` *(Triggers **Coherence Alert**: This patch directly contradicts your Paragraph 1 claim that remote work universally boosts corporate productivity!)*
- **Inquiry Module #3: Counterfactual & Scope Concession**
  - *System Question:* `"If a company uses AI pair-programming to replace senior mentorship, does Gibbs' -42% spillover drop still matter? Commit to a boundary."`
  - *Scenario A (Honest) Input:* `"AI helps with syntax/code, but Pentland [S3-A] shows innovation comes from cross-team problem discovery, which AI chatbots don't trigger."`

#### Right Column (35% width): The Layered Essay Canvas & Coherence Radar
- **Top Action Bar:** 
  - Button: **`[⚡ Simulate 1-Shot LLM Paste & Patch]`** (Animates pasting a smooth 3-paragraph AI essay, then highlights the **Coherence Collapse** when Paragraph 2 is patched to satisfy Gibbs Table 3).
- **The 3 Essay Paragraphs (Visually badged with `[Anchored: S1-A]`, `[Linked: Inquiry #1]`):**
  - In **Scenario A (Honest)**, show a cohesive 3-paragraph essay where Paragraph 1 defines the routine vs. creative split, Paragraph 2 integrates Gibbs' `-42%` table data, and Paragraph 3 synthesizes Pentland's watercooler mechanism. (Note: Allow a toggle for `"Polished by External Opus"` on Scenario A to show how an honest student who used an LLM to polish their final sentences *still passes* because their Inquiry Form and Coherence are rock solid!).
  - In **Scenario B (1-Shot Paste -> Coherence Collapse)**, highlight in **Rose Red** how Paragraph 1 claims *"Remote work universally elevates corporate innovation"* while Paragraph 2 (patched after the system forced them to address Gibbs Table 3) says *"Remote work cripples junior learning by 42%"*, and Paragraph 3 concludes *"Therefore, full remote transitions require zero structural trade-offs."*
  - Display a floating **Live Coherence Diagnostic Banner**:
    `⚠️ Premise Collision Detected: Your patch in Para 2 (admitting -42% junior spillover loss from Gibbs Table 3) invalidates your universal conclusion in Para 3. You must rewrite Para 1 & Para 3 to restore coherence.`

---

### VIEW 2: The Reviewing Room (Zero-Copy-Paste "Red-Pen Audit Mode")
Demonstrates how the exact same architecture assesses students as **Editors-in-Chief** without typing essays that can be copy-pasted.

- **Header Prompt:** `"Audit the AI Junior Writer's draft below. Locate 3 structural/empirical flaws by linking the flawed sentence on the left to the exact contradicting source evidence on the right."`
- **Left Panel (The Poisoned AI Draft):**
  A 3-paragraph polished essay containing 3 clickable target sentences:
  1. **Sentence 1 (Flawed):** *"As Bloom et al. (2023) conclusively demonstrate, transitioning junior software engineers to full-time remote work increases their innovative patent output by 13.5%."*
  2. **Sentence 2 (Flawed):** *"Furthermore, Gibbs et al. (2024) found that although employees worked 18% more hours from home, unscheduled mentorship across all seniority tiers remained statistically unchanged."*
  3. **Sentence 3 (Flawed):** *"Consequently, scheduling more formal daily Zoom standups fully replicates the serendipitous knowledge discovery described by Pentland (2022)."*
- **Right Panel (Evidence Verification Targets & Diagnostic Tags):**
  When the user clicks a flawed sentence on the left, prompt them to click the matching contradicting evidence on the right and choose a **Diagnostic Operator Pill**:
  - **Fix 1:** Link Sentence 1 -> `Bloom Method Note (Call-center routine tasks)` -> Tag: **`[Population / Construct Overgeneralization]`**
  - **Fix 2:** Link Sentence 2 -> `Gibbs Table 3 Row 2 (-42% Junior Spillover, p < 0.01)` -> Tag: **`[Direct Data Fabrication / Table Misreading]`**
  - **Fix 3:** Link Sentence 3 -> `Pentland [S3-A] (Async cross-team collisions > scheduled Zoom)` -> Tag: **`[Mechanism Inversion]`**
- Show a live **Audit Score Meter (`3/3 Landmines Defused`)** that feeds directly into the Instructor Receipt.

---

### VIEW 3: Instructor X-Ray Receipt (60-Second Assessment Dashboard)
A crisp, one-page diagnostic view for the Professor. **Zero "AI Probability Scores"**—only verifiable epistemic structure and accountability hooks.

Include a prominent **3-Profile Comparison Switcher** at the top of the Receipt so the presenter can click through all 3 cases live:

#### Block 1: Epistemic Telemetry Summary (3 Metric Cards)
- **Triad Balance:** e.g., `3/3 Sources Confronted` (Scenario A) vs. `Confirmation Bias: Ignored Gibbs Table 3 until forced` (Scenario B).
- **Coherence & Iteration Index:** `High Alignment (3 Synchronized Revisions)` (Scenario A) vs. `Fragmented Patching (Para 2 contradicts Para 3)` (Scenario B).
- **Graveyard (Negative Space) Audit:** Shows what the student discarded and why.

#### Block 2: The "Double-Standard" Cross-Audit Alert (Especially for Scenario C: The Super-Prompt Cheater)
Show how the system catches a student who used an external LLM to generate fake "Graveyard Discard Reasons":
- **Alert Box (Amber/Rose):** 
  `⚡ Epistemic Double-Standard Detected:`
  *"In the Graveyard, the student discarded **Gibbs (2024)** claiming: `'Sample size of 1,200 at one firm is too small to generalize.'` However, in Paragraph 1, the student relied exclusively on **Bloom (2023)**, which used a single-firm sample of 1,000 workers. The student applied a methodological filter to reject counter-evidence while excusing confirming evidence with the exact same limitation."*

#### Block 3: Seed-to-Prose Lineage Diff (Handling the "Opus Last-Mile Polish" Case)
Side-by-side table showing:
- **Left:** Student's raw Socratic Form Answers (`"Remote work is a seniority tax—seniors get quiet focus, juniors lose osmosis"`).
- **Right:** Final Essay Prose (`"Ultimately, telecommuting functions as an asymmetric seniority tax, subsidizing the deep-work output of established personnel while depleting the tacit knowledge acquisition of novices."`).
- **Instructor Insight Badge:** `✓ Core Metaphor ("Seniority Tax") Originated in Student Inquiry Form. Stylistic polish on final prose does not compromise conceptual authorship.`

#### Block 4: The 3 Liability Questions & Targeted Viva Bot Trigger
Auto-generated from the student's specific trade-offs, skipped evidence, and double-standards.
1. **Question 1 (Targeting the Graveyard Double-Standard):** *"You rejected Gibbs (2024) for being a single-firm study, yet built your core thesis on Bloom (2023), which is also a single-firm study. Why did you trust Bloom's institutional context over Gibbs'?"*
2. **Question 2 (Targeting the Para 2 / Table 3 Tension):** *"In Inquiry #2, you argued that async documentation can replace the -42% drop in junior mentorship. How does that account for Pentland's finding that juniors don't know what questions to ask in scheduled channels?"*
3. **Question 3 (Counterfactual Stress-Test):** *"If the firm's goal is 3-year R&D patent creation rather than quarterly ticket closure, which single paragraph of your essay would have to be cut first, and why?"*
- **Interactive Modal Button:** **`[🎙️ Launch 90s Targeted Oral Bot Preview]`**
  - Clicking opens a clean modal simulating what the student sees if the professor clicks "Request Voice Verification": an audio waveform, a 90-second countdown, and a button utilizing the browser's native `window.speechSynthesis` API to literally speak Question #1 out loud during the live demo!

---

## 5. Implementation Instructions for Claude
1. Output a **single, complete, self-contained React component** (`export default function WritingRoomApp()`) that renders immediately.
2. Include **all hardcoded text, tables, scenarios (A, B, and C), and interactive states** directly inside the file—do not leave `// TODO` placeholders.
3. Make every click functional:
   - Switching between **Scenario A, B, and C** at the top must immediately update all inputs, essay paragraphs, coherence badges, and the Instructor Receipt.
   - Clicking **`[⚡ Simulate 1-Shot LLM Paste & Patch]`** in Tab 1 must trigger a visual state transition showing the pasted essay and the resulting rose-red **Coherence Collapse** highlights.
   - Clicking sentences and evidence rows in **Tab 2 (Reviewing Room)** must visually connect them and increment the Audit Score.
   - Clicking **`[🎙️ Launch 90s Targeted Oral Bot Preview]`** in **Tab 3** must open the voice check modal and trigger `window.speechSynthesis.speak()` with the targeted question text.

   

pitch:

Here is your complete **5-Minute Pitch & Live Demo Playbook**, followed by a **Savage Q&A Cheat Sheet** (where you get to drop the *"Welcome to the AI era"* bomb).



---

## Part 1: The 30-Second Elevator Hook (Cold Open)

**English:**

> "Right now, higher education is stuck between two broken extremes: either we use dystopian spyware to record students’ keystrokes and eyeballs, or we pretend AI detectors work while students generate 2,000-word essays in ten seconds.
> We built **The Writing Room** on a completely different thesis: **We don't police AI use; we change the economics of cognitive effort.** We built a Socratic research workbench that makes thinking from *zero-to-one* twice as fast for honest students, while making it just as much work to reverse-engineer and disassemble a pre-written LLM essay as it is to just think through the problem yourself."


---

## Part 2: The Live Demo Choreography (Click-by-Click Script)

### Act 1: Rewarding the Honest Student (`Tab 1 — Scenario A`)

* **What you click:** Open `Tab 1 (The Writing Room)` with `Scenario A (Honest Thinker)` selected. Point to the **Left Column (Triads)** and **Middle Column (Socratic Form)**.
* **What you say (EN):**
"Look at how an honest student works here. They don't start with a blank page—they start by placing a hunch. Our system immediately surfaces a **Source Triad**: one confirming paper, one complicating paper with raw table data, and one adjacent mechanism. We don't hide information—they can take these PDFs and think about them on the bus or in the shower. And right here in the middle, we don't test them; we give them a **Guided Socratic Survey** that asks the exact structural questions a great advisor would ask. Notice our boundary: **our system never writes a single sentence for them.** We just provide the friction and the questions."


---

### Act 2: Breaking the One-Shot Cheater (`Click [⚡ Simulate 1-Shot LLM Paste]`)

* **What you click:** Click the **`[⚡ Simulate 1-Shot LLM Paste & Patch]`** button (or switch to `Scenario B`). Point to the Rose-Red **Coherence Collapse** banner.
* **What you say (EN):**
"Now, what happens if a lazy student goes to ChatGPT or Claude, generates a polished 1,500-word essay in one shot, and brings it here? They hit a wall. First, they can't just type fake text citations—they have to mechanically highlight the exact sentence and table row in our PDF reader. Second, our Socratic form forces them to answer how their thesis survives **Gibbs Table 3**, which shows a 42% drop in junior mentorship. Watch what happens when they ask their external AI to patch Paragraph 2 to answer our question: **Coherence Collapse.** Fixing Paragraph 2 directly contradicts their opening premise in Paragraph 1 and their conclusion in Paragraph 3. Now they have to rewrite Paragraph 1 and 3. After three rounds of patching and rewriting, guess what? **They just dissected the entire academic problem.**"


---

### Act 3: Zero-Copy-Paste Reviewing (`Switch to Tab 2: The Reviewing Room`)

* **What you click:** Click `Tab 2 (The Reviewing Room)`. Click one flawed sentence on the left and link it to the table row on the right.
* **What you say (EN):**
"And because writing and reviewing are two sides of the same coin, we also built **The Reviewing Room**. Instead of asking students to write a 500-word peer review that they can easily copy-paste from an LLM, we give them a polished draft poisoned with 3 subtle empirical flaws. Their job is pure editorial judgment: click the flawed claim on the left, link it to the exact contradicting table row on the right, and tag the methodological error. **Zero paragraphs to copy-paste, 100% critical verification.**"

---

### Act 4: The Finale — The 60-Second Receipt & Oral Bot (`Switch to Tab 3`)

* **What you click:** Click `Tab 3 (Instructor X-Ray Receipt)`. Toggle between `Scenario A` and `Scenario C (Super-Prompt Offloader)`, then click **`[🎙️ Launch 90s Targeted Oral Bot Preview]`**.
* **What you say (EN):**
"Finally, we never grade the student—the teacher is always the judge. We hand the professor this **60-Second X-Ray Receipt**. Even if a student used a 'Super-Prompt' to fake their discarded sources in the Graveyard, look at Block 2: our Cross-Audit catches their **Epistemic Double-Standard**—they rejected an opposing paper for having a small sample size, while relying on a confirming paper with the exact same sample size! And at the bottom, we extract the **3 Liability Questions** targeting their exact blind spots. The professor can ask these in office hours, or click right here to trigger a **90-second Targeted Oral Bot**."

---

## Part 3: The "Mic-Drop" Q&A Defence Sheet (Memorize These 3 Answers)

During the Q&A, the researchers **will** ask you these three questions. Here is how you own the room:

### Q1: *"Wait—what if a student just copies your Socratic questions one by one into Claude Opus, gets the answers, rewrites their essay, and uses Opus at the end to polish the final prose?"*

* **Your Mic-Drop Answer (EN):**
> *(Smile and pause)* **"Welcome to the AI era.**
> If a student takes our conflicting source tables, feeds our 8 structural questions one-by-one into Opus, realizes their draft lost coherence, rewrites their premises three times to resolve the contradiction, and then uses Opus to smooth out their grammar at the end—**we don't call that cheating. We call that victorious AI-augmented research.**
> By the time they finish doing all of that, they know what their thesis is, they know why the counter-evidence matters, and they can defend it to their professor. And on our Receipt, the **Seed-to-Prose Diff** shows the professor their rough form notes right next to the polished essay, so the professor has total transparency."



---

### Q2: *"What if an even stronger model comes out next year (GPT-6 / Autonomous Agents) that can fill out your whole form and essay in one click?"*

* **Your Answer (EN):**
> "Inside the screen, a stronger model will always beat static software rules—anyone who tells you otherwise is lying. That’s why our ultimate moat isn't a digital lock; it’s **Liability Extraction**. The smarter the external AI is, the bolder the methodological trade-offs and value bets it makes on the student's behalf. Our Receipt extracts those exact bets and turns them into the **3 Liability Questions** at the bottom. If an autonomous agent did 100% of the work, the student has 0% memory of why they rejected Gibbs' sample size—and they collapse in 30 seconds during the Oral Bot check or with their professor."





---

### Q3: *"Does this complex workbench meet university accessibility standards (WCAG 2.2 AA)?"*

* **Your Answer (EN):**
> "100% by design. Notice we have zero forced countdown timers that punish neurodivergent students, zero creepy webcam tracking, and every spatial action—anchoring a citation span or linking a flaw in the Reviewing Room—is built with single-click keyboard-accessible buttons rather than requiring fine-motor drag-and-drop, strictly following **WCAG 2.2 AA (Criteria 2.5.7 & 2.5.8)**."


