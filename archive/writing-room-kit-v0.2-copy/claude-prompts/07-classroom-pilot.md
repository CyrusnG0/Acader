# Classroom pilot kit (when a real course says yes)

## Recruitment blurb (post/LMS announcement)
"Volunteers for a 40-minute writing session (2x20 min). You will write one short essay inside a new study tool and one outside it, on the same topic. Your session log is exported for research; nothing is uploaded, nothing affects any grade. [name]"

## Think-aloud card (give each participant)
"Work as you normally would. Say out loud what you are looking for and why. If the tool gets in your way, say it out loud — that is the most useful data."

## Observation log (one CSV per session)
run_id, participant, condition (A-outside / B-platform / C-hybrid), start, end,
queries_count, retrievals_count, hooks_count,
librarian_misfire (Y/N), misfire_query, misfire_returned,
stuck_over_60s (count), participant_comment, would_use_again (Y/N)

## After each session
- export session JSON, file as runs/pilot-<participant>.json
- node scripts/score.js runs/pilot-*.json
- log librarian misfires — the scripted librarian WILL misfire; every misfire is a spec for the real backend.

## The one question the pilot must answer
"Did the process receipt show anything the final essay alone could not?" — if yes twice, that is your CLEAR poster.
