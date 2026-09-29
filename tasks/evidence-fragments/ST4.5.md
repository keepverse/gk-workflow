# ST4.5 — the first reading over the real imported catalog (R8 input)

**Status: DONE.** Taken by the manager on the real published server; the report is committed at
`docs/research/action-corpus/_budget-2026-09-19.json`.

## How the reading was taken (acceptance row 1: the re-import is confirmed BEFORE the reading)

`features/mega-merge` @ **7a1974ba** (this lane's branch tip at the time), `deploy-play.ps1 -NoGame
-NoServer` then `Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe` — the acceptance's own
mechanism, run by the owner from their own terminal rather than from an agent session (which is why this
task was recorded BLOCKED until now; the blocking note is kept at the end of this fragment for the
record). The fresh publish plus boot re-ran the import, and **`power_trigger_frequency` came back with 5
rows** — the direct confirmation that ST4.5c's seed landed in the deployed database, the table that had
been empty before it and the reason six of the ten zeros existed.

## The reading

| Field | Value |
|---|---|
| `pricedActionCount` | **18** |
| `recommendedReferencePower` | **1512** |
| `recommendedBy` | **`action.general.0004`** (rung 4 — the only action that sets it) |
| `unpricedActions` | 3, named and bounded below |

Per rung, from the committed file:

| rung | n | min | p50 | p90 | max | aboveP90 |
|---|---|---|---|---|---|---|
| 1 | 1 | 0 | 0 | 0 | 0 | — |
| 4 | 3 | 0 | 245 | 1511 | 1511 | — (n<10, so p90 IS max) |
| 7 | 10 | 0 | 21 | 65 | 998 | **`action.family.pea.002`** |
| 10 | 4 | 118 | 118 | 685 | 685 | — (n<10) |

Rungs 2, 3, 5, 6, 8 and 9 carry no content (no percentiles reported rather than four zeros). Every
other rung's `aboveP90` is empty **by construction** — nearest-rank p90 equals max below ten actions —
which is exactly why ST4.5f added `recommendedBy`: it names `action.general.0004` on rung 4, where the
scalar is actually set and `aboveP90` cannot say so. **Actions above the report's p90, by id:
`action.family.pea.002` (rung 7).** Nothing else is above any rung's p90.

## The three unpriced actions (bounded in ST4.5e — not a defect in this reading)

| Action | Rung | Atoms the pricing refused |
|---|---|---|
| `action.family.fruit.001` | 7 | `atom.evd-harden.t4`, `atom.shld-surge.t4` |
| `action.family.hypno.002` | 7 | `atom.evd-harden.t4` |
| `action.general.0005` | 4 | `atom.evasion.t2` |

Pooled-channel atoms (`params.channel` is a pool reference) and `RpgStore` has no channel-pool catalog to
resolve them, so they are genuinely unpriced — and ST4.5e made the report name them instead of folding
them in as zeros. Its bound: they would need realized ≥ **3501** (rung 4, divisor 1×2315) or ≥ **16206**
(rung 7, 2×5359) to move the scalar; priced, they would imply roughly **13 / 19 / 9**. **The scalar is
not affected by them.** Follow-up: E30's channel-pool store surface.

## What this reading does NOT do

It does **not** publish v4 — H7 and the todo both say that is ST5.2's own commit. It also does not
activate the budget check: the table production loads is still `action-rungs.v1.json` (`Program.cs:256`),
which predates the `powerBudgetMilli` column, visible in the report as `powerBudgetMilli: null` and
`aboveLoadedScalar: []` on every rung. The scalar is computed from `poolRolls`/`qPowerMilli`, which
v1–v4 share, so the reading is valid for the value it exists to produce; making the column live is ST5.2
(publish) and ST5.3 (check).

## Why the zeros are what they are (the diagnosis this task produced)

See `tasks/evidence-fragments/ST4.5a.md` and its correction. The 10 zeros were **6** from an empty
frequency table (fixed by ST4.5c's seed and ST4.5d's refusal), **3** pooled channels (named by ST4.5e,
bounded as above) and **1** overlay magnitude (`act.attack`, bounded in ST4.5g: 0 → 100 against a
threshold of 1512, so it cannot move the scalar). No zero in this reading is an unresolved atom — the
published DB has 0 missing atoms, 0 missing containers and 0 empty containers.

## The earlier blocking note, kept for the record

This task was BLOCKED for a session because its Verify line starts
`dist\FusionRpg.Server\FusionRpg.Server.exe` and curls a running server: `dist/` does not exist in a
fresh worktree, and starting a server is outside an agent session's operating protocol ("no leftover
processes"; `Start-Process` opens the console that steals the owner's keyboard focus). That was the right
call — a report produced by a fixture would have been worse than no report, because R8 makes this file
the *source* of v4's `referencePower`. The owner's own run is what satisfied the acceptance.
