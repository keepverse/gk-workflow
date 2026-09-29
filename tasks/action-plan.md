# Implementation Plan: Action program — closing the gap to playable (A26–A32)

**Program:** `action`. **Map:** [docs/architecture/action-map.md](../docs/architecture/action-map.md)
§17. **Specs:** [docs/architecture/action/](../docs/architecture/action/)
`spec-unlock-tuning-activation.md` · `spec-specimen-loadout-endpoints.md` ·
`spec-unlock-discard-endpoint.md` · `spec-action-corpus-import-completion.md` ·
`spec-actions-tab-fe-wiring.md` · `spec-action-choice-rung-tiebreak.md` ·
`spec-action-choice-condition-awareness.md`. **Ideal docs:**
[action-playability-ideal.md](../docs/architecture/action-playability-ideal.md) ·
[action-choice-ideal.md](../docs/architecture/action-choice-ideal.md). **Todo:**
[action-todo.md](action-todo.md) (this program's existing tracked pair — extends it rather than
displacing the A1–A25 history already there).

## Overview

A1–A25 built a fully correct, fully tested action engine. It is inert for every real player because one
call is missing (`UnlockTuningPolicy.Configure`) and, once fixed, which action fires is decided by
`action_id` alphabetical order rather than build intent. This plan closes both, plus the REST/FE surface
a player needs to see and act on the result. Seven module specs (A26–A32), already audited and
strengthened (2026-09-13 review pass) — this plan sequences their implementation.

## Architecture decisions (already settled in the specs — not reopened here)

- **A26 is the root cause and ships first.** Everything else is either untestable (A27/A28/A30 have
  nothing real to show) or unmeasurable (A31/A32 have no real multi-action loadout to reorder) without
  it.
- **Two owner scopes, not one** (audit finding, A27/A28): loadout *slot assignment* is
  `OwnerKind.Entity` (session-scoped); unlock-ladder *grants* are `OwnerKind.UniqueActor` (durable).
  A28 uses the grant scope; A27's `isHeld` check merges both grant scopes; A27's `SetLoadout`/
  `GetLoadout` calls use the `Entity` scope. Getting this backwards silently breaks either persistence
  or progression — see each spec's Design section.
- **A32 is a loop lookahead, not a comparer change** (audit finding): `ActionTagPreference.Compare` is
  static and runs once at freeze time; it cannot see live target facts. A32 adds a bounded lookahead
  inside the decision loop, extracted into one shared helper both `StubIntentSource` and
  `SiegeAiIntentSource` call — never duplicated into two loops.
- **No new tunables** across A26–A32 except none — every module reuses an already-authored, already-
  priced number (`Rung`, `action-unlock.v1.json`, `DiscardPolicy`'s existing coefficient). Confirmed
  per-spec.

## Dependency graph

```
A26 (unlock-tuning-activation)
    │
    ├──► A27 (specimen-loadout-endpoints) ──► A28 (unlock-discard-endpoint) ──► A30 (actions-tab-fe-wiring)
    │                                                                                 ▲
    ├──► A29 (action-corpus-import-completion)  ── independent, parallel-safe ───────┘ (no dependency,
    │                                                                                    just shares no files)
    └──► A31 (action-choice-rung-tiebreak) ──► A32 (action-choice-condition-awareness)
```

**Coordination note, not a gate**: A26 and A29 both touch `Program.cs` (different lines — the Configure
block vs. the corpus-import file list). Land A26 first and rebase A29 on it to avoid a trivial merge
conflict; this is sequencing for convenience, not a dependency — A29's own logic does not need A26.

## Phase table (Phase 14, with the 2026-09-18 A33 addendum)

| Module | Tasks | Size | Depends on | Checkpoint |
|---|---|---|---|---|
| A26 unlock-tuning-activation | T62, T63 | XS, S | — | M |
| A27 specimen-loadout-endpoints | T64 | M | T62 | N |
| A29 action-corpus-import-completion | T65, T66 | XS, S | — (rebase on T62) | N |
| A31 action-choice-rung-tiebreak | T67 | XS | — | N |
| A28 unlock-discard-endpoint | T68 | M | T62, T64 | O |
| A30 actions-tab-fe-wiring | T69, T70 | S, M | T64, T68 | P |
| A32 action-choice-condition-awareness | T71, T72 | M, S | T67 | Q |
| **A33 battle-holder-wiring** *(added 2026-09-18)* | **T74** | M (split at the Delve/District boundary if it goes past 5 files) | T62 | Q.1 |
| docs propagation | T73 | XS | T62–T72, T74 | — |

**A33** comes from `action-map.md` §17 (filed 2026-09-18 by the `action-enrich` and
`action-skill-tiers` maps as an unowned gap). Its spec is still owed, and T74's first step writes it. It
is lane A of [summoner-convergence-plan.md](summoner-convergence-plan.md), and it can run in parallel
with A27–A32 once T62 lands. It is **not** in the parent's H1 golden chain. If it moves a golden, it
re-blesses in its own commit, never sharing one with `ST2.3`, `ST1.3`, `AE1.5` or `SP` 6.1. Until T74
lands, every held action in a production battle reads its authored rung (the A23 fallback). That makes
`action-skill-tiers` ST2's window bound, and `action-enrich`'s effective-rung base, correct but inert in
production. Neither program waits on it.

## Gates vs. checkpoints — no hard gate in this plan

Checked against `planning-and-task-breakdown`'s two questions for every candidate stopping point:

| Candidate | Irreversible? | Verdict |
|---|---|---|
| A28's per-specimen Θ source (spec's own "ask first" item) | No — a codebase search, answerable same-session, and `CostLedger` (T17) already established the exact fallback shape for this situation (`thetaScaleMilliOf` seam, default inert, "the real anchor formula is a follow-up, not decided here") | **Not a gate.** Task 8 below resolves it inline: search first; if no existing per-actor Θ reader is found within the task, ship the same seam-with-inert-default T17 used and flag the real wiring as a named follow-up, never block A28 on it |
| A29's schema-compat check (does the importer handle the two newer files) | No — a two-minute test run | **Not a gate**, just Task 5's own first step, gating only Task 6 (not the rest of the plan) |
| A30's FE state-model question (4th cooldown state design) | No — reversible, a component detail | **Not a gate.** Ship a plain 4th state; escalate to `/idea-ui` only if the visual treatment turns out non-trivial during implementation |

No task in this plan blocks on an external approval, another team, or an irreversible shared-state
collision. Every open item above has a named resolver (the implementing session, inline) and a stated
default.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| A26's test proves the wrong thing (calls `Configure` in test setup instead of proving the real host does) | High — the exact way this gap survived until now | Task 2 requires `RpgApiFactory : WebApplicationFactory<Program>` specifically (verified in this session to boot the real bootstrap), not a hand-rolled host |
| A27/A28 owner-scope mix-up ships anyway | High — silently breaks persistence (wrong writes) or progression (wrong reads) | Task 3/8 acceptance criteria include the two-scope-merge test cases named in each spec, not just a happy path |
| A29's cross-file id collision (proven historical bug, `audit-2026-09-13-distribution.md` §7) recurs | Medium — silent data corruption | Task 6 requires the reject-loudly guard as an acceptance line, with a planted-collision test |
| A32 duplicated into two intent sources | Medium — the audit's own "silently absent in siege" failure shape | Task 11/12 require the shared helper and a `SiegeAiIntentSource` proof, not just `StubIntentSource` |
| Any module moves a golden | Low, but checked every time (A17's own precedent) | Every task's verification step includes the full suite + all 8 goldens, never assumed zero-mover |
| **T64/T68's endpoints ship compiled but never registered** (audit finding, 2026-09-13 plan review) — `LoadoutEndpoints.MapLoadout()` does nothing until `Program.cs:782` calls it; the same shape applies to the two new endpoint classes | High — would repeat A26's own root-cause defect class (correct code, silently unreachable) inside this very fix | `Program.cs` is explicitly listed in T64/T68's Files, and each task's acceptance requires a real HTTP round-trip against a booted host, not just a unit test on the handler delegate |
| Documentation drift after the fix lands (ideal docs / §17 keep describing pre-fix gaps as current) | Medium — the exact "corrected on paper, unreachable in practice" mismatch this session has already flagged twice for other reasons | T73 closes it explicitly, gated on all other tasks |
| Boundary guards / web checks (`guard-dal`, `guard-test-substrate`, `npm run check:bundle`, `npm run extract`) skipped because they're not "the feature" | Medium — AGENTS.md hard requirement, easy to forget on a REST/FE-shaped task | Named explicitly in each relevant task's Verify line and in the final Phase 14 checklist, not left implicit |

## Open questions

None blocking. The three "not a gate" items above are resolved inline during their own task, per the
stated defaults.
