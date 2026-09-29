# Spec: `world-fall`

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Module 7 of the
[world-continuity map](../world-continuity-map.md) (wave 2; depends on `seat-outcome`, `coarse-step`).
Ideal: [world-continuity-ideal.md](../world-continuity-ideal.md) §6.5, W4. Owner decision **Q2
(2026-09-19): losing the active world makes it `fallen`; the save never ends.** The Lose row in
`docs/guide/the-game.md` is reworded by `continuity-doc-amendment` (now reads *"Enemy empires take your
seat. That world becomes fallen — hostile ground you can revisit — and your save continues"*,
`docs/guide/the-game.md:40`). House style: [../world-action-economy/spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).

## Objective

When the player's own seat is lost — in a full step or in a coarse step, in the active world or an old
one — the world's outcome becomes `fallen`, the same rule everywhere. Each frontier loss before that is a
digest fact as it happens, never a surprise wipe. A fallen world stays listed as hostile ground; nothing
is deleted, so `world-reclaim` can later read its history. **No game over:** the save continues.

## Scope and non-goals

**In scope:** the `fallen` branch of the shared outcome helper; its report facts; what a fallen world
still allows (End Turn while active; advance; never select); the fate of what stays behind; the
end-of-game wording removed from code paths, if any.

**Not in scope:** reclaim (`world-reclaim`, reserved); the digest's rendering (`away-digest`); the carry
limit's number (`advance-carry`; Q2 makes a fallen world use the not-won limit).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Sector capture moves ownership and slot ownership and clears the per-sector warden binding | `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:96-115` |
| Fade can leave a sector unowned | `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:219` |
| A destroyed legion's cargo becomes a revisit-lootable cache | scoped-inventory `cargo-fate` (`docs/architecture/scoped-inventory-hierarchy-map.md:53`); `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoFate.cs` |
| World validation runs only at creation, so a world with a lost `Home` still loads | `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:42-43`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:226` |

### Real gap

No fallen state; no rule for the active world losing its seat. Nothing in `src/` ends a save on a lost
homeworld either — the Lose condition existed only in the guide (`the-game.md` before the amendment),
so there is no game-over path to remove.

## Design

### 1. One helper, one rule (Q2)

`OutcomeTransition.Apply` (`world-victory` §2) handles `SeatReading.SeatLost`:

```
if world.Outcome != Fallen and SeatOutcome.Read(...) == SeatLost:
    report: "world.fallen", home sector id, cause ("captured:<faction>" | "faded")
    world with { Outcome = Fallen, OutcomeTurn = turn }            // WonAtTurn kept if it was won
```

It runs at the end of `Snapshot` in the full step and at the end of every coarse record, so an active
world and an old world fall by the same code. `fallen` is **terminal for this program**: no rule here
leaves it (`world-reclaim` may). Retaking the `Home` sector afterwards does not un-fall the world.

### 2. Losses before the fall are facts, in order

Every sector lost in a coarse record is one digest fact `(save, world, record, sector, turn, cause)`
emitted by `coarse-step` §5 in capture order; in the full step the existing capture and fade report lines
already carry the loss. The seat loss is the last fact of its record. `away-digest` renders them; this
module guarantees they exist before `world.fallen` in the same record.

### 3. What a fallen world allows

| Verb | Active and fallen | Hibernating/idle and fallen |
|---|---|---|
| End Turn / orders | **allowed** — the war goes on; remaining legions can fight or withdraw | refused (`world.not-active`, as for any non-active world) |
| Advance (`advance-carry`) | allowed, with the **not-won** carry limit (Q2), even if `WonAtTurn` is set | n/a (advance is from the active world) |
| Select (`world-state-vocabulary` §4) | n/a | refused `world.fallen` — only `world-reclaim` may select one |
| Coarse catch-up | n/a | continues: enemy empires keep acting on it (W4); the digest keeps reporting |
| Idle (`idle-world`) | n/a | refused: a warden cannot hold a world whose seat is gone |

Decided by principle: an active fallen world keeps its End Turn because the save never ends (Q2) and the
player needs a turn-based way to pull remaining legions toward the advance. It stays `active` until the
player advances or selects another world.

### 4. What stays behind is never deleted

Nothing is deleted when a world falls: sectors keep their new owners, structures stay (they now belong to
whoever holds the sector — slot ownership already follows capture, `ClaimResolver.cs:108-115`), and a
legion destroyed in a coarse contest leaves its cargo as a cache through `cargo-fate`. A stationed
warden's fate is `world-warden`'s (§5 there). The world row, its command log and its turn log stay, so
`world-reclaim` can replay its history.

### 5. `RulesetVersion` — the wave's one bump (round 6 C1)

**Round 6 C1: one capability flag and one ruleset bump per wave.** This module is world-continuity **wave 2**
and rides **wave 2's single bump**, shared with `world-victory` and `coarse-step` — not *"shares when both land
in the same wave; if it lands alone it bumps once itself"*, which left the number depending on the order two
branches merged in. The bump is taken at landing, never pre-assigned (map *Audit 2026-09-20* R1), and recorded
in [../trade-network/landing-order.md](../trade-network/landing-order.md). A command log that never loses the
`Home` sector is unaffected (the outcome row is emitted only when not `contested`), so this module moves no
golden of its own.

## Built / wiring gap / real gap (summary)

| Bucket | Item | Closed by |
|---|---|---|
| Built | capture, fade, cargo fate | reused |
| Real gap | fallen transition; per-loss facts before it; allowed verbs | §1–§3 |

## Acceptance (contract)

1. Losing `Home` (capture or fade) in a full step sets `Outcome = Fallen` in that step; in a coarse
   record, at the end of that record.
2. `fallen` is terminal: retaking `Home` later leaves `Fallen`; `WonAtTurn` survives a fall.
3. Every sector lost in a coarse record appears as one fact, in capture order, before `world.fallen`.
4. An active fallen world accepts End Turn; a non-active fallen world refuses select and idle with named
   reasons.
5. No row is deleted by a fall (world, sectors, logs, caches — asserted by row counts).
6. The rule is identical for the active world and an old world (the same helper; tested through both
   `Step` and `CoarseStep`).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Continuity/OutcomeTransitionTests.cs` (extend): 1, 2, 6.
- `tests/FusionRpg.Core.Tests/World/Continuity/CoarseStepTests.cs` (extend): 3.
- `gk-core/tests/FusionRpg.Data.Tests/WorldTurnCommitTests.cs`, `WorldStoreTests.cs` (extend): 4, 5.

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
```

## Hard edges

- **`rpg_worlds` schema:** none new (the outcome columns are `world-victory`'s).
- **Replay:** the fall is produced inside `Step`/`CoarseStep`, so replay reproduces it.
- **Corpse-cache tick key:** none; caches left by a fall decay on the save counter like any other.

## Dependencies

`seat-outcome`, `coarse-step`, `world-victory` (shared helper and bump). Consumed by `world-warden`,
`advance-carry`, `away-digest`, `multiverse-surface`, reserved `world-reclaim`.

## Boundaries

- **Always:** one rule for every world; facts before the fall; never delete.
- **Ask first:** any path out of `fallen` (that is `world-reclaim`).
- **Never:** a game-over; a second seat-loss predicate; deleting a fallen world's rows.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `world.fallen` report fact + `Outcome = Fallen` | `away-digest`, `multiverse-surface`, `advance-carry` |
| Allowed-verb table (§3) | `world-state-vocabulary` (select refusal), `idle-world` (refusal) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: turn engine Snapshot, coarse step, world store.
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json; check not re-run.
[x] Read this session: see spec-world-state-vocabulary.md.
[x] decisions.md checked: no lock on world loss.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: capture body, fade ownership write, validation call sites; searched src/ for
    a game-over path (none).
[x] Surrounding sections read.
[ ] Constraint tested: none run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: the-game.md Lose row already reworded by the doc amendment.
[x] No population pinned.
[x] No cache.
[x] No ordering-fixed criterion beyond capture order, which is the contract.
[x] No actor magnitude.
[x] No SOLID fork: one helper.
[x] No new cross-cutting rule.
```
