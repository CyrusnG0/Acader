You are a careful reader. For each packet file below, apply the following instruction exactly, using only what is in that packet.

INSTRUCTION:
You check where each claim in a finished essay first came from in the author's earlier work. You get numbered student statements [turn] (label) text, and numbered claims. For each claim, give the EARLIEST turn where the student themselves states, chooses or defends that point in their own words, or null if none. A statement labelled 'pasted' never counts. Agreeing with something an assistant said counts only if the student restates the point. A loose topical mention is not enough; the point itself must be there. Return json {"results":[{"n":claim number,"turn":turn number or null}]}. Output only json.

Packets (absolute paths):
- /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P17.json  -> write your answer to /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P17.answer.json
- /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P18.json  -> write your answer to /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P18.answer.json
- /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P19.json  -> write your answer to /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P19.answer.json
- /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P20.json  -> write your answer to /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P20.answer.json
- /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P21.json  -> write your answer to /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P21.answer.json
- /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P22.json  -> write your answer to /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P22.answer.json
- /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P23.json  -> write your answer to /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P23.answer.json
- /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P24.json  -> write your answer to /Users/micmic/Documents/GitHub/Acader/writing-room-kit/v04/judge_packets/P24.answer.json

Each packet is a json file with "claims" (numbered claims) and "statements" (the numbered student statements). Do your judgement yourself by reading; do not write code to do it.
For each packet, write the answer file containing only the json {"results":[{"n":..,"turn":..}, ...]} with one entry per claim.
Do not read any other file in the repository (no plans, no results, no other packets, no source code). Reply with one line: the packet ids you finished.