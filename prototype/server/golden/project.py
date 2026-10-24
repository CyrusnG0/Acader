"""Project an L1 result onto the frozen `expected_receipt` shape (fixtures/README.md)."""
from __future__ import annotations


def project(l1: dict, compile_json: dict) -> dict:
    bands = l1["bands"]
    sentences = {s["id"]: s for s in l1["sentences"]}
    para_of = {s["id"]: s["paragraph_id"] for s in l1["sentences"]}
    per_para = {}
    for p in l1["paragraphs"]:
        if p["sentence_ids"]:
            per_para[p["id"]] = [f"{sentences[i]['band']} {sentences[i]['words']}"
                                 for i in p["sentence_ids"]]
    facts = l1["facts"]
    return {
        "status": l1["status"],
        "total_words": bands["total_words"],
        "bands_by_words": dict(bands["by_words"]),
        "bands_by_claims": dict(bands["by_claims"]),
        "quoted_words": bands["quoted_words"],
        "inferred_links": bands["inferred_links"],
        "map_suggestions": bands["map_suggestions"],
        "sentences": per_para,
        "claim_units": {u["id"]: u["band"] for u in l1["claims"]},
        "notes": {n: sum(1 for s in l1["sentences"] if n in s["notes"])
                  for n in ("label_not_confirmed", "pasted_linked_not_checked")},
        "unconfirmed_marks": [f"{r['kind']} {r['ref']} {r['reason']}"
                              for r in compile_json["runs"] if not r["confirmed"]],
        "moments": [{k: v for k, v in m.items() if k not in ("seq", "ts", "pin_seq")}
                    for m in facts["moments"]],
        "question_targets": [f"{q['sentence_id']} {para_of[q['sentence_id']]} "
                             f"{','.join(q['reasons'])}" for q in l1["l3b_queue"]],
        "facts": {
            "editor_pastes": facts["pastes"]["editor"]["count"],
            "paste_surviving_chars": facts["pastes"]["editor"]["surviving_chars"],
            "cards_with_paste": facts["pastes"]["cards"]["cards_with_paste"],
            "coach_answers_with_paste": facts["pastes"]["coach_answers"]["answers_with_paste"],
            "declared_claims": facts["declared"]["declared_claims"],
            "declared_claims_anchored": facts["declared"]["declared_claims_anchored"],
        },
    }
