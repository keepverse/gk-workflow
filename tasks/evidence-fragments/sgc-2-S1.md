# S1 — `set-species-binding` revision 2: the set-planning system, ruled

Task: `species-gear-chain` T27 `setClass` half, lane `sgc-2`, queue step S1 ·
spec: docs/architecture/species-gear-chain/spec-set-species-binding.md

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The spec records the 2026-09-21 ruling (classes adopted, not `legacy`) and `setClass` as a build deliverable | `grep -n "revision 2, 2026-09-21\|build the set-planning system" docs/architecture/species-gear-chain/spec-set-species-binding.md` | exit=0 :: status line `revision 2, 2026-09-21` + owner quote + the new `## The set-planning system` section | docs/architecture/species-gear-chain/spec-set-species-binding.md |
| The three classes' member-role counts and thresholds are recorded as versioned data, not code | `grep -n "set-topology.v1.json" docs/architecture/species-gear-chain/spec-set-species-binding.md` | exit=0 :: 6 hits (Tunables table, class section, Project structure) | same file |
| The Ask at `:246` (`build.*` / `theme.*`) is answered from the class design | `grep -n "ANSWERED 2026-09-21" docs/architecture/species-gear-chain/spec-set-species-binding.md` | exit=0 :: Open question 1 marked answered, with the measured 36 `build.*` → `general` and 30 `theme.*` → 26 `general` / 4 `family` | same file |
| The shipped-corpus reading is measured, printed, never asserted | `python - <<'PY' … ladder tally …` | `class tally: {'general': 906, 'family': 4}`; `unresolved: 0`; by prefix `creature {general: 844}`, `build {general: 36}`, `theme {general: 26, family: 4}` | spec § The shipped corpus is re-planned onto the ladder |
| Stale `decisions.md` line citation inside the fence re-anchored to the real row | `grep -n "Set topology classes" docs/architecture/decisions.md` | exit=0 :: `141:` (was cited as `134`) | spec § Tunables / § The set-planning system |
| Doc citations still resolve | `powershell -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit=0 | — |

**No commit for the ladder tally:** it is a throwaway in-memory reading over the committed tree, run
once to write the table into the spec; the durable reading is S4's repair report.

## Not proved

- The class assignment is not yet exercised by code — S1 is the spec only; the resolver, the loader
  and the corpus re-plan are S2–S4.
- The `family` identity contract for the four 6-role `theme.*` sets is **not** satisfied and is not
  fabricated; recorded as forward debt for module 25 in the spec and as a finding for its program's
  todo.
- `docs/architecture/species-craft-ideal.md:375` still cites `decisions.md:132` for the topology row
  (real row is `:141`); that file is outside this lane's fence.
