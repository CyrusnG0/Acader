# Data-handling note for outreach (D-021)

Give this one page to any instructor, IT or integrity office that asks "where does the data go?".

## Two different things
| | **Room demo** (`demo/`) | **Practice-viva pilot** (`runner/`) |
|---|---|---|
| Purpose | Show the idea | Run a real, ungraded practice viva |
| Content | Fictional sample sources and sample text | A real assignment and student code |
| AI provider | **DeepSeek** API (deepseek-chat) | **Anthropic** API (Claude) |
| Real student data | **Never.** Use the built-in sample text only | Yes, with consent only |
| Stored where | Your browser only (localStorage); our server keeps nothing | Our server, 30 days, then deleted |
| Who sees what | Only you | Instructor sees summary signals; full answers only if the student opts in |
| Student rights | n/a | Opt out, export, delete at any time |

## Plain statements
- The demo's Helper and Coach send the text you type to DeepSeek's API to generate replies. Do not type or paste real student work into it.
- The pilot never produces a verdict about honesty. It gives signals, and the instructor decides any follow-up.
- Pilot students see a consent note naming the AI provider, what is stored, and who can see it before they start (docs/designs/concierge-viva-pilot.md, D-014).
- We do not train models on pilot data. [ASSUMPTION: confirm the provider's API data-use terms before the first pilot and quote them here.]

## Open items before a pilot with real data
- Confirm Anthropic API data retention terms in writing and add them above.
- Hong Kong: check PDPO obligations and the university's own data-transfer rules with their IT or compliance office.
