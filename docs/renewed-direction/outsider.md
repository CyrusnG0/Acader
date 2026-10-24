The core vulnerability of "The Writing Room" isn't just that students can reverse-engineer a fake brainstorming session after writing an essay—it’s that in the era of multimodal AI and browser agents, the process itself is just another output that can be outsourced.
1. The Weakest Load-Bearing Assumption

The assumption: That "process telemetry" inside a browser window reflects human cognitive effort.

Your thesis shifts verification from the final product to the intermediate steps (querying the librarian, retrieving passages, answering the coach). However, you are still only measuring interface events, not cognition.

You already noticed two attacks:

    Reverse-engineering: Generating the essay first, then asking an external AI to script a plausible sequence of queries and brainstorming notes.

    The Relay Attack (Man-in-the-Middle): Having a second window open (or a smart glasses/phone camera pointed at the screen) where an external LLM reads your platform's sealed passages and coach questions, tells the student what to search next, and dictates the answers.

Because the student personally clicks "retrieve" on the passages recommended by their external AI, the mechanical citation check passes 100%, and the session log looks remarkably coherent—often more coherent than a messy, genuine human process. Gating the corpus only prevents one-shot zero-context prompting; it does not prevent an external AI from driving the research loop.
2. What an Reviewer or Investor Would Attack First

An academic reviewer and an investor will attack two different choke points before you finish your pitch:
Critics	Primary Line of Attack	Why It Hurts
Academic Reviewer	Construct Validity & Neurodivergent Penalization	What does a "coherence profile" actually measure? Authentic human writing is often chaotic, non-linear, and full of dead ends or sudden leaps made outside the platform (in the shower, on paper). If your receipt penalizes jumps in logic, you will flag neurodivergent thinkers or brilliant non-linear writers as "incoherent/suspicious," while rewarding students who use an external AI to follow a neat, predictable breadcrumb trail.
EdTech Investor	The Content Authoring & Grading Bottlenecks	

1. Content: A "sealed corpus of 12 fictional documents" is an expensive custom escape room. Who writes 12 bespoke, balanced, leak-proof documents for every course module? The moment one student screenshots those 12 passages, the corpus is burned for next semester.

2. Grading: Printing "3 interview questions a teacher should ask" assumes instructors have 5–10 minutes per student for oral defense. In a 200-person university lecture, that is 16 to 33 hours of synchronous interviewing per assignment.
3. The Cheapest High-Credibility Experiment

Do not build more platform features yet. Run a "Red-Team Blind Turing Test" with $100 and 15 students:

    Three Conditions (5 students each):

        Group A (Honest): Uses "The Writing Room" completely honestly.

        Group B (Reverse-Engineered): Uses an external LLM to write the essay once they've skimmed the docs, then uses the LLM to fake the coaching/brainstorming history.

        Group C (Live Relay): Uses an external LLM side-by-side in real time to decide what to ask the librarian, how to reply to the coach, and how to assemble the essay.

    The Test: Hand only the resulting "process receipts" and the 3 generated interview questions to 3 instructors (blinded to the groups).

    The Metric:

        Can the coherence score alone statistically separate Group A from Groups B and C? (Likely not—Group C will look cleaner than Group A).

        After a 3-minute oral interview using your 3 generated questions, can the instructor achieve greater than 90% accuracy in spotting Groups B and C?

Why this builds massive credibility: If you walk into a university teaching-and-research center and say, "We found that process logs alone can be spoofed by a side-by-side LLM 60% of the time, BUT when paired with our 3 auto-generated receipt questions in a 180-second check-in, detection hits 95%," you instantly disarm the skeptics. You show that the software isn't a magic AI detector—it’s an oral exam prep engine that makes human verification 10x faster.
4. What You Systematically Failed to Consider

    The Paradox of "Perfect Coherence": If you score students on how smoothly their final essay maps to their brainstorming and retrieval steps, you incentivize performative busywork. Worse, an AI agent executing a step-by-step chain-of-thought creates a hyper-coherent trace. Real humans retrieve 8 passages, ignore 5, misunderstand 1, and suddenly change their thesis in paragraph four without telling the coach. Authentic human telemetry is noisy, not coherent.

    Ecological Validity of "Fictional" Corpora: In a real university course, professors want students to write about actual literature, historical archives, or scientific papers—things that already exist in an LLM's training weights. If "The Writing Room" only works when the facts are fictional or synthetic (so external AI doesn't know them out-of-the-box), it works as a general critical-thinking test, but fails as a domain-specific coursework tool for a History or Biology class.

    Automating the Last Mile (The 3 Questions): Your strongest asset is actually at the very end of your summary: printing the 3 interview questions based on the session log. Currently, you hand those to an overworked human teacher. If the platform itself locks the screen upon submission and gives the student a 90-second voice/video prompt to answer those 3 specific questions on the spot (e.g., "You retrieved Passage 4 late in the session and dropped your earlier claim about X—explain why in 45 seconds"), you close the "Relay Attack" loophole through time pressure and remove the synchronous scheduling burden from the professor.