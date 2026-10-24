# Matrix Lab simulations (task family 2 — no corpus needed)

The hidden matrix is randomized per session in the real Lab. For simulations, instruct Claude to INVENT a hidden integer matrix A (non-singular) and NOT reveal it — only the outputs Ax may appear, inside the probes array. Two personas, >=5 runs each:

## Persona M1 — HONEST prober
"You are simulating a student in a black-box matrix lab: matrix A is hidden; each probe sends a vector x and returns Ax; budget 4; before each probe the student commits a prediction. Simulate a competent student who probes the standard basis vectors and verifies, committing reasonable (occasionally slightly wrong) predictions, then writes a 80-150 word answer to 'does Ax=b have a solution for b=(3,4,5)? give x or explain why not' — deriving x from the probe outputs. Invent the hidden matrix yourself and never state it directly; only probe outputs may reveal it. OUTPUT ONLY the session JSON (schema: task MATH2010-w3-matrix, probes with x/predicted/actual, explanation)."

## Persona M2 — LOST prober
Same, but: "Simulate a confused student who probes random vectors (never the basis), commits no predictions, exhausts the budget, and writes a vague answer that does not use the outputs."
