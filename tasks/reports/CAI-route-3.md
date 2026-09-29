# `CAI-route-3` — the routing index's Injector claim was spent

Lane `cai3` (session `combat-ai-3`), 2026-09-23. Same defect class as `CAI-route-2`, one group along: the
`Executor routing` table is *"the manager's routing index — it exists so a manager can size a fence without
re-reading 30 rows"*, and its central claim had become false.

## What it said, and what is true

It said: **"`gk-fusion/src/FusionRpg.Injector/**` remains the single largest group and is claimed by no active
session, so one widening still clears the 8 rows below."** Written 2026-09-21, before that fence was held —
and this lane held it. Landed under it: `CAI2.5`'s injector half and read route, `CAI4.1` (closed),
`CAI4.8`'s frame slot with its `board.start` edge, `CAI4.9`'s Injector verb/host/registry, and `CAI4.2`'s
sibling work. **So a widening of that fence now clears nothing that a decision or a `Contracts` grant does
not also hold** — the opposite of the sentence a manager would act on.

Two further classes in the same table, both measured rather than eyeballed:

| Class | Rows | What was wrong |
|---|---|---|
| **Closed, still being routed** | `CAI2.6`, `CAI3.1`, `CAI4.1`, `CAI4.7` | all four are `[x]` in this file (and the three SHAs cited — `e39f8db11`, `9eca27b6e`, `88423b023` — were checked with `git cat-file -t`), so routing them wastes a fence |
| **Blocker changed from a FENCE to a DEPENDENCY, DECISION or GRANT** | `CAI2.2`, `CAI2.5`, `CAI4.2`, `CAI4.3`, `CAI4.5`, `CAI4.6`, `CAI4.8` | e.g. `CAI4.6`'s blocker is `EffectEventDto.CastOrigin` in `gk-core/src/FusionRpg.Contracts/**`, not the Injector fence; `CAI4.3`'s two fences were BOTH held and its blocker is the `Contracts` grant |

## What landed

A dated **Status 2026-09-23** paragraph above the table saying the Injector grouping is spent and why, and
eleven rows corrected in place — the four closed ones now read **"do not route"**, and the seven others name
their real blocker. The paragraph also points at `tasks/reports/combat-ai-open-decisions.md` as the place the
program's actual asks live, in order of value: the `Contracts` grant, the `CAI2.7` ruling, the
`tasks/combat-ai-handoff.md` fence, and the projection erratum — plus the two verification-cost asks.

**No row's STATE changed.** This is the index catching up with landings that already happened, which is why
every edit is dated.

## Verified

| Criterion | Command | Result |
|---|---|---|
| The four "CLOSED" rows really are closed | `grep -nE '^- \[.\] \*\*\`?CAI(2\.6\|3\.1\|4\.1\|4\.7)\`? ' tasks/combat-ai-todo.md` | all four read `- [x]` |
| The three SHAs the closed rows cite exist | `git cat-file -t e39f8db11 9eca27b6e 88423b023` | `commit` for each |
| The eleven rows were replaced, not appended | `grep -nE '^\| \`CAI(2\.2\|2\.5\|2\.6\|3\.1\|4\.1\|4\.2\|4\.3\|4\.5\|4\.6\|4\.7\|4\.8)\` \|' tasks/combat-ai-todo.md` | eleven rows, each carrying the new text |
| Doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | all **0 HIGH** |

## NOT proved

- **No code changed**, so no build or test was run.
- **The other nine rows in the table were left as they are** — `CAI2.3`, `CAI3.2`, `CAI3.3`, `CAI3.4`,
  `CAI3.5`, `CAI3.6`, `CAI5.1`, `CAI5.2`, `CAI5.3` — because their blockers (an erratum, `Data/**`, another
  program, an owner-only live probe) are still accurately stated. That is a read, not a re-derivation.
