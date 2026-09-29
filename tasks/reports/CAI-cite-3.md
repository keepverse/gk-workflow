# CAI-cite-3 — the two remaining in-fence citation sweeps

Lane `cai4` (session `combat-ai-4`), 2026-09-22. Filed and closed in the same session: this is the work
`CAI-cite-1`'s row left as its remaining queue, and this lane's fence is what it was waiting on
(`docs/architecture/combat-ai/**` **and** `docs/research/combat-ai/**`).

## The measured result

| Scope | Before | After | Command |
|---|---|---|---|
| `docs/architecture/combat-ai/**` (21 docs, 938 resolvable citations) | `D1 4, D2 0, D3 0, D4 0` | **`D1 0, D2 0, D3 0, D4 0`** | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` |
| `docs/research/combat-ai/**` (9 docs, 253 citations) | `D1 0, D2 0, D3 0, D4 0` (bounds were already clean after CAI-cite-2) | **unchanged, and the 9 content sites are now annotated** | `python scripts/audit-doc-citations.py --scope docs/research/combat-ai --summary` |
| Strict guard | — | **0 `combat-ai/` lines** | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` |

## What was wrong, and why each fix is the right KIND of fix

**Re-anchored (prose describes CURRENT behaviour, the number moved):**

| Site | Was | Now | Why |
|---|---|---|---|
| `spec-aggression-tier-map.md:35,128,236,261,308,375` (6 sites) | `BattleRunState.cs:1025-1033` / `:1032-1033` | `:1037-1044` / `:1043-1044` | `:1025-1033` is `ObjectivePositionOf`; the `ai.aggression` composition is `AggressionOf` (`:1043-1044`) with its comment at `:1037-1042`. **Verified by reading both windows.** |
| `spec-lawn-held-actions.md:238` | `BattleRunState.cs:582-624` | `:582-638` | The prose claims the "compile-and-order shape"; `:624` stops before the `ActionTagPreference` sort at `:635`. |
| `spec-lawn-held-actions.md:120` | `CheatState.cs:215-220` | `:280-285` | `:215-220` is `ApplySpeciesAllocations`; the ptr→Bound-instance resolver the row names is `ResolveBoundInstanceId` at `:280-285`. |
| `spec-core-scorer.md:387` | `SiegeTuning.cs:333-375` | `:333-367` + a dated note | The range resolves, but the prose said "until module 2 lands" — **it has** (`CAI1.8` moved the ten keys), and the cited comment now says so. A reader following the citation learned the opposite of the prose. |

**Annotated, not re-anchored (prose describes a CLOSED defect — bumping the number would claim current
behaviour for a historical audit, the refusal `CAI-cite-1` recorded for its four past-state sites):**

`docs/research/combat-ai/AUDIT.md:32,37,39,62,66`, `S1-battle-core.md:10`, `S4-lawn.md:33`,
`REVIEW-B.md:57,61` — nine sites citing `BasicAttack.cs:163-165`, `:152`, `:165`, `:189-191`,
`:193-216`, `:489`, `:494-501`, `TimelineDispatch.cs:79-80` and `CostLedger.cs:69-78` at pre-fix line
numbers. Each now carries a dated note naming what closed it (`CAI1.10`, `CAI1.11`, `CAI1.14`) and the
successor site (`BasicAttack.cs:175-179` for the one `IntentRouter.Compose` chain, `:179` for the
`LoyalTargetRedirect` decorator, `:177` for the ledger pass, `:215-232` for the `OnActivate` raise).

**Marked as not-yet-existing (a proposal, or another program's owed file):**
`spec-lawn-cast-trigger.md:457` (`lawn-combat-ai.v1.json`, never created — the program took option (a)),
`spec-replay-identity.md:67` (the Data third's and CAI2.2's test files, unbuilt), `:135`
(`mode-profiles.v1.json`, owned by `lawn-tuning-profile`, does not exist yet).

## The 18 suspects that are NOT defects

`CAI-cite-1`'s heuristic (every backticked identifier on the citing line must appear within ±30 lines of
the cited line) reports 18 remaining sites. **Every one was read and judged an artifact** — the symbol
belongs to the *next clause* of the same sentence, not to the cited file: e.g. `spec-lawn-actor-view.md:348`
cites `IBattleView.cs:17` (which IS the interface declaration) and then says "…, the same interface
`BattleRunState` and …"; `spec-decision-perf.md:19` cites the scorer's doc comment at `:147-149` and then
names `maxCandidatesScored`. The heuristic's window is a prompt to read, never a defect count — the same
conclusion `CAI-cite-1` reached for its own 101.

## Out of fence, and named rather than left silent

`docs/architecture/combat-ai-ideal.md:171` still cites `BattleRunState.cs:628-630` for
`NoStanceHeld.Instance`; that seam is now `BattleRunState.Stance { get; set; } = NoStanceHeld.Instance;`
at `:194` (`CAI3.1`). `combat-ai-ideal.md` is a **sibling file**, not inside this lane's
`docs/architecture/combat-ai/**` fence — the same shape `CAI-cite-1` reported for the ideal's other three
sites. One line for whoever holds that file.
