# PACK_SPEC v1 - session pack contract (permanent)

Every ONTO_SESSION_PACK_vN.zip MUST contain:

1. 00_SESSION_PACK.md  - sections fixed:
   0 PACK META (version, primary plane = ONE, session type A/B/C, start trigger)
   1 ROUTING (file -> disk path under C:\Projects\onto-research\lab\dpo\)
   2 LADDER STATE (one line per experiment, verdicts only)
   3 NEXT SESSION TASK (exact commands, pass/fail criteria)
   4 NEXT+1 PREVIEW (one paragraph)
   5 LOAD-BEARING LEARNINGS (do not relitigate)
   6 CARRY-OVER / TAIL DEBT
   7 ARTIFACT MANIFEST (md5 per file; mismatch in transit = STOP)
2. Artifacts for the NEXT session only (minimal, 1 plane). No "just in case".
3. md5 manifest covers every artifact in the zip.

Intake protocol (Claude side, automatic on receiving pack):
  unzip -> md5 vs manifest -> counts/gate -> verdict PACK VALID / INVALID.
  INVALID = stop, rebuild pack. No work on unverified artifacts.

Pipeline (fixed):
  pack vN -> [TYPE C] pack_runpod.ps1 -E N -> 1 zip -> pod: unzip+pip / bash run_eN.sh
  -> download deliverable -> file_results.ps1 -E N -> commit+push
  -> Claude builds pack v(N+1). Tommy's manual surface: 2 PS scripts + 2 pod cells + drag files.
