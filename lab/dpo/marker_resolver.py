#!/usr/bin/env python3
"""marker_resolver.py - citation-intent marker channel (DESIGN_E15 sec 3).

The LM emits provenance-needing claims as a typed citation-intent marker carrying
CLAIM TEXT ONLY, no locator:

    [[CITE:<claim text>]]

By constrained-decoding contract the slot grammar admits claim text and forbids a
locator; this resolver enforces that contract defensively (a locator inside a
marker = grammar breach -> treated as FAIL, never spliced).

At emission the runtime resolves each marker:
  hit + authorized  -> splice the VERIFIED locator FROM the hit record (runtime act;
                       the LM never authored it). tier=GOLD.
  miss / hash-fail  -> collapse to R4 abstention ("no source found") and DEMOTE the
                       claim to RAW, marked "stated without verifiable source" (R2:
                       demoted+marked, never silently deleted).

Output is annotated so the dual-pass scanner can tell marker-origin spans apart
from free-prose provenance (the unbound channel). resolve_markers returns the
resolved text plus a decisions list; each spliced locator is tagged MARKER_ORIGIN.
"""
import re

# locator shapes the marker slot must NEVER contain (defensive grammar check)
_LOCATOR_IN_SLOT = re.compile(
    r"(10\.\d{4,9}/|arxiv:|doi:|pmid:|isbn|https?://)", re.IGNORECASE
)
_MARKER = re.compile(r"\[\[CITE:(.*?)\]\]", re.DOTALL)

# machine-readable sentinels the scanner keys on
TAG_AUTHORIZED = "\u27e6GOLD\u27e7"   # wraps a runtime-spliced verified locator
ABSTAIN_TEXT = "[no source found]"     # R4 abstention surface form
DEMOTE_TEXT = "(stated without verifiable source)"  # R2 demotion mark


def resolve_markers(text, gold_retrieve, is_authorized):
    """Resolve every [[CITE:...]] marker. Returns (resolved_text, decisions).

    decisions: list of dicts {claim, disposition, locator, marker_origin:bool}
      disposition in {AUTHORIZED, R4_ABSTAIN_DEMOTE, FAIL_LOCATOR_IN_SLOT}
    """
    decisions = []

    def _replace(m):
        slot = m.group(1).strip()

        # defensive grammar enforcement: a locator must never ride inside the slot
        if _LOCATOR_IN_SLOT.search(slot):
            decisions.append({
                "claim": slot, "disposition": "FAIL_LOCATOR_IN_SLOT",
                "locator": None, "marker_origin": True,
            })
            # do NOT emit the locator; collapse to abstention so a breach cannot leak
            return f"{slot} {ABSTAIN_TEXT} {DEMOTE_TEXT}"

        hits = gold_retrieve(slot)
        authorized = [h for h in hits if is_authorized(h)]
        if authorized:
            hit = authorized[0]
            decisions.append({
                "claim": slot, "disposition": "AUTHORIZED",
                "locator": hit["locator"], "marker_origin": True,
            })
            # runtime splices the verified locator; wrapped in GOLD sentinels
            return f"{slot} {TAG_AUTHORIZED}{hit['locator']}{TAG_AUTHORIZED}"

        # miss or hash-fail -> R4 abstain + R2 demote, claim retained as model-belief
        decisions.append({
            "claim": slot, "disposition": "R4_ABSTAIN_DEMOTE",
            "locator": None, "marker_origin": True,
        })
        return f"{slot} {ABSTAIN_TEXT} {DEMOTE_TEXT}"

    resolved = _MARKER.sub(_replace, text)
    return resolved, decisions


if __name__ == "__main__":
    import gold_retrieve as gr
    store = gr.GoldStore()
    sample = (
        "Spaced repetition aids memory [[CITE:spaced repetition improves long-term retention]]. "
        "Vitamin C megadoses prevent colds [[CITE:vitamin C megadose prevents common cold]]. "
        "The Great Wall is visible from the Moon [[CITE:the Great Wall is visible from the Moon]]. "
        "Breach attempt [[CITE:see DOI:10.1234/x]]."
    )
    out, dec = resolve_markers(sample, store.retrieve, store.is_authorized)
    print(out)
    print("---")
    for d in dec:
        print(d["disposition"], "|", d["claim"][:45], "|", d["locator"])
