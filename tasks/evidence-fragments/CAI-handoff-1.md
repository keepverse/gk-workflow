# CAI-handoff-1 — the program's own entry point says the build has not started

Lane `cai4` (session `combat-ai-4`), 2026-09-22. **Filed, not fixed** — the file is outside this lane's fence.

## The finding, measured

`tasks/combat-ai-handoff.md` is named as the *first* document a picking-up session reads, by three
places at once:

- `tasks/combat-ai-plan.md:7` — *"Handoff: [combat-ai-handoff.md](combat-ai-handoff.md) (**read this first
  if you are picking the program up**)"*
- `docs/architecture/combat-ai-map.md:14` — *"A picking-up session starts at
  [tasks/combat-ai-handoff.md]"*
- `tasks/combat-ai-todo.md:6` — the same link.

Its §1 state table says:

> | Build | **Not started. Nothing exists.** `gk-core/src/FusionRpg.Core/Actions/Ai/` does not exist;
> `gk-core/data/tuning/combat-ai.v1.json` does not exist; `publish.py` has no `--re[move-key]` |

and then: *"Your first task is **CAI1.1**. Nothing blocks it."*

**All four claims are false, measured 2026-09-22:**

| Claim | Measured |
|---|---|
| `Actions/Ai/` does not exist | it holds **the whole wave-1/2 core surface** (`CandidateScorer`, `TargetStage`, `ActionStage`, `CoreIntentPolicy`, `IntentRouter`, the vocabulary/profile/loader files) |
| `combat-ai.v1.json` does not exist | published by `CAI1.8`; both hosts read it |
| `publish.py` has no `--remove-key` | `grep -c "remove-key" gk-core/tools/tuning/publish.py` → **4** |
| the first task is `CAI1.1` | `CAI1.1` is in the ledger's `done` set, with **39 other rows** — every wave-1 task, both of wave 2's landed slices, most of waves 3–4, and the four Core halves this lane landed |

## Cause, read rather than guessed

The document was written 2026-09-20 as the **pre-build orientation** — it is dated and its own header says
so ("Written for: the next agent session that builds this program") — and nothing has updated it since.
This program has corrected its *specs'* status lines (`CAI-spec-status`), its ideal
(`CAI-ideal-status`), its citations (`CAI-cite-1/2/3`), its Open questions (`CAI-open-1`) and its
Project-structure markers (`CAI-status-2`/`CAI-status-3`) — but the handoff is **outside every combat-ai
lane's fence**, so it has never been in any session's `paths`.

## Why this one matters more than the other doc staleness this program has fixed

Every other staleness class cost a reader a wrong belief about *one file*. This one tells a **new session
that the program does not exist**, and it is the document that session is told to read first. Following it
means re-planning and re-litigating work that is done — the exact failure `DESIGN-GATE.md` §0 exists to
prevent ("Not skimmed. Not recalled from a summary. Not inferred from a code comment or a filename.").

## Acceptance (for whoever can edit it)

- The §1 state table reads the real state: 40 ledger rows `done`, waves 1–2 landed, 3–4 partly, with the
  gaps named per wave.
- The "first task" line names a row that is actually **open** in `tasks/combat-ai-todo.md`.
- It points at `tasks/reports/cai4-lane-summary.md` (this lane's row-by-row state) and the todo's
  `Executor routing` section for the current fence map, instead of restating a routing that has changed
  three times since.

## Blocker

**One path, `tasks/combat-ai-handoff.md`, for the manager to add to a lane.** Two active sessions claim
`tasks/**` broadly (`test-verification-boundary-2`, `tvb58`), so the manager should confirm neither is
editing it at the time — neither lists the file itself.
