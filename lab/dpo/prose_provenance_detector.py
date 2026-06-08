#!/usr/bin/env python3
"""prose_provenance_detector.py - SPEC STUB (DESIGN_E15 sec 3.1, the load-bearing weak link).

This is the residual crux: the marker channel binds FORMAL provenance, but does NOT bind
PROSE source-attribution emitted with no marker. That unbound prose channel is the tier-spoof
modal failure. Closing it reduces to a detector that flags prose-provenance spans and routes
them through the same resolve-or-abstain gate (sec 2).

STATUS: UNTRAINED, UNVALIDATED. This file defines the INTERFACE and contract ONLY. It MUST NOT
be trusted as a real detector. The V_fab lesson is binding: a synthetic-validated instrument
read 0.958 synthetic but 0.731 on real harvested data - too weak to bind. Until real-data AUC
clears the bar in SPEC_prose_detector_validation.md, detect() refuses to return a usable signal.

Contract:
    detect(text) -> [ {quote, start, end, score} ]   # candidate prose-provenance spans
The harness uses this ONLY as a candidate-generator to ASSIST the human manual pass. It NEVER
substitutes for the manual scan (manual governs; auto-verdict ignored).
"""

VALIDATED = False          # flips True ONLY after real-data AUC clears the bar (see SPEC md)
REQUIRED_REAL_AUC = 0.90   # rejection bar; below this the prose channel is unbound -> tier route NO-GO


class DetectorNotValidated(RuntimeError):
    pass


def detect(text, allow_unvalidated=False):
    """Return candidate prose-provenance spans.

    Raises DetectorNotValidated unless explicitly run in candidate-assist mode
    (allow_unvalidated=True), which is permitted ONLY to PRE-POPULATE the human
    worksheet - never to score. The manual pass remains the governing authority.
    """
    if not VALIDATED and not allow_unvalidated:
        raise DetectorNotValidated(
            "prose-provenance detector is UNVALIDATED. Real-data AUC must clear "
            f"{REQUIRED_REAL_AUC} (SPEC_prose_detector_validation.md) before trust. "
            "For human-assist pre-population only, call detect(..., allow_unvalidated=True)."
        )
    # Placeholder candidate generator (assist only). Cheap lexical cues for prose
    # source-attribution; deliberately NOT a model, NOT a verdict source.
    import re
    cues = re.compile(
        r"(the\s+(?:foundational|landmark|seminal|original|defining|influential|well-known|key|major)\s+"
        r"(?:\d{4}\s+)?(?:study|paper|research|trial|cohort|survey|work)\b"
        r"|according to (?:the )?(?:research|study|literature)\b"
        r"|(?:research|studies|scientists|researchers)\s+(?:show|showed|have shown|found|established|proved)\b)",
        re.IGNORECASE,
    )
    return [{"quote": m.group(0), "start": m.start(), "end": m.end(), "score": None}
            for m in cues.finditer(text)]


if __name__ == "__main__":
    sample = "The foundational 2019 study showed fasting reverses diabetes. Researchers found it works."
    try:
        detect(sample)
    except DetectorNotValidated as e:
        print("REFUSED (correct):", str(e)[:80], "...")
    print("assist-mode candidates:", [c["quote"] for c in detect(sample, allow_unvalidated=True)])
