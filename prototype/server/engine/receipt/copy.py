"""Every user-facing string the receipt compiler writes (receipt.md §2-§5). Written by the lead;
workers never change wording. Every string here still passes the wording filter at compile."""

# ---- summary (receipt.md §2 item 2): built from facts only ------------------------------------
SUMMARY_SOURCES = {0: "with no sources", 1: "with 1 source", "n": "with {n} sources"}
SUMMARY_CLAIMS_LEAD = {1: "Of 1 claim", "n": "Of {n} claims"}
# one part per non-zero band count, in band order; {n} is the count
SUMMARY_CLAIM_PARTS = {
    "traced_source": {1: "1 traces to a source or lecture", "n": "{n} trace to a source or lecture"},
    "traced_coach": {1: "1 traces to a Coach exchange", "n": "{n} trace to a Coach exchange"},
    "declared": {1: "1 is declared outside help", "n": "{n} are declared outside help"},
    "student_linked": {1: "1 is linked by the student, not checked",
                       "n": "{n} are linked by the student, not checked"},
    "untraced": {1: "1 has no record here of where it came from",
                 "n": "{n} have no record here of where they came from"},
}
SUMMARY_PASTES = {1: "1 passage came in by paste from outside the platform",
                  "n": "{n} passages came in by paste from outside the platform"}
SUMMARY_DECLARED = "Outside help was declared ({tools})"
SUMMARY_COACH_LEAD = {1: "The Coach asked 1 question", "n": "The Coach asked {n} questions"}
SUMMARY_COACH_PARTS = {"answered": "{n} answered", "revised": "{n} revised",
                       "disagreed": "{n} disagreed", "declined": "{n} declined"}
SUMMARY_MECHANICS = {1: "1 word of references and formatting is counted apart",
                     "n": "{n} words of references and formatting are counted apart"}
SUMMARY_EMPTY = "No written work was recorded before submission"

# ---- where to ask (receipt.md §2 item 3, §4) -------------------------------------------------
WHY_TEXT = {
    "untraced_claim": "This part carries the argument, and there is no record here of where it came from.",
    "added_proposition": "This sentence adds a point that its linked card does not contain.",
    "contradiction": "This part and another paragraph seem to point in different directions.",
    "inconsistent_standard": "A reason given for setting one source aside also applies to a source the work relies on.",
    "declared_not_anchored": "This claim came from declared outside help and was never connected to a source.",
    "student_linked_claim": "This part carries the argument and is linked by the student, not checked against a source.",
    "map_finding_unconnected_paragraph": "This paragraph isn't connected to the claim map.",
    "map_finding_claim_without_source": "This claim has no source behind it in the platform.",
}
RETRY_NOTE = ("\nYour previous reply could not be used (reason: {reason}). "
              "Write a different question that follows every rule.")
GROUNDING_CLAIM = '{label} (a claim from the student\'s claim map): "{text}"'
GROUNDING_DECLARED = '{label} (a claim from outside help the student declared): "{text}"'
GROUNDING_BLOCK = '{label} (a passage from the reading "{title}"): "{text}"'
GROUNDING_BLOCK_UNTITLED = '{label} (a passage from a reading the student used): "{text}"'

# ---- other notes -------------------------------------------------------------------------------
REPLAY_NOTE = "Built from the browser's copy (replay mismatch)."
REPLACEMENT_REPORTED_BY = "browser"

# ---- wording-filter fallbacks (receipt.md §5) --------------------------------------------------
FALLBACK_SUMMARY = "A summary isn't available for this receipt; the details are below."
FALLBACK_TOOL = "a named tool"
FALLBACK_TITLE = "a source"
FALLBACK_TEXT = "(not shown)"


def plural(table: dict, n: int, **kw) -> str:
    """table[n] if present, else table['n'] formatted with n."""
    t = table.get(n, table["n"])
    return t.format(n=n, **kw)
