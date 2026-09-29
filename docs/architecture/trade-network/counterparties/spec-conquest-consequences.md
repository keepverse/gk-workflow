# Spec: `conquest-consequences`

**Status: written 2026-09-19 against the approved map. Spec phase; no build authorized.** Every
`file:line` below was opened in this session. Module id `conquest-consequences`, row 11 of the
[counterparties map](../counterparties-map.md) (wave 3; depends on `diplomatic-stance`, `relation-facts`,
`clan-economy`, `empire-treasury`). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §7.4
(*"capturing a clan sector closes its center, ends clan production there, and records a fact that moves
every clan's disposition"*), principle 9 (*"Losing a sector, even the capital, never hands your banked
treasury to anyone"*), §7.6 (a counterparty captured mid-route); [empire-economy-ssot.md](../../empire-economy-ssot.md)
§3 (*"taking his capital collapses him"*). **Reconciled 2026-09-19** with the round-4 register (a clan hub
carries a seeded Trading Post, which changes hands with its sector). Session record:
`tasks/sessions/trade-network-idea-20260919.json`.

## Objective

Say what taking ground **means** for the people you trade with and fight — once, in one pass, hooked where
ownership already changes, never as a second capture path:

- taking a **clan** sector ends the clan's trade and production there and turns every other clan's
  relation against the conqueror;
- taking an **empire** sector hands over the sector and its warehouse, never the empire's treasury;
- an empire that loses its **last seat collapses**: its treasury is destroyed, a sink the report shows.

Success looks like: a conquered clan's hub stops trading for that clan the turn it falls; every surviving
clan grows colder toward the conqueror; an enemy empire that loses its capital keeps every banked good
until it loses its last seat, and then the goods vanish rather than change hands.

## Scope and non-goals

**In scope:** detecting ownership changes of a turn (capture and fade) in one pass; the clan-capture record;
collapse and treasury destruction; the report lines the relation projector and the economy report read.

**Non-goals:** the capture itself (`ClaimResolver`, unchanged); goods in transit on a route through a
captured sector (`cargo-fate` via `logistics-flow` `transit-buffer` and `scoped-inventory`); what happens to
a collapsed empire's remaining legions (unchanged: they keep their faction and the stance rules); the win
condition and world end (`world-continuity`); access and treaty voiding after collapse (derived by
`exchange` `trade-access`, ask A9).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| **Capture is `ClaimResolver`:** sector ownership, every slot's owner and the warden binding change hands in `Snapshot` | `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:94-118`; run at `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:408` |
| Ground lost to fade goes to **no one**: owner set to null, structures cleared, `loam.lost:` reported | `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:212-224` |
| An assault changes **slot** results only; a sector changes hands through a claim | `gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:146-161` |
| `Snapshot` runs every order resolver, then postures and refill | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:400-433` |
| `Step` holds the turn's opening world alongside the evolving one | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:157-196` |
| A seat is a slot type | `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:47`, `:78` |

### Wiring gap

None.

### Real gap

Every consequence: nothing today notices that a clan or an empire lost ground.

## Design

### 1. One pass, at one place

`ConquestPass.Apply(opening, world, report, flags)` runs at the end of the `Snapshot` resolvers
(after `WardenResolver`, `TurnEngine.cs:425`), before `diplomacy-facts`' append position and before
postures land. It compares **sector ownership at the turn's opening** with ownership now, so it sees every
way ground changed hands this turn — a claim in `Snapshot` and a fade in `Pressure` — without hooking either.
`Snapshot` gains the opening world as a parameter; `ClaimResolver` and `LoamPhases` are not edited.

### 2. A clan sector changes hands

For each sector owned at the opening by a `Clan` faction `c` and now owned by a different, non-null faction
`k`:

- report `clan.conquered:<c>:<sectorId>` (kind `Event`, audience `k` and `c`, with the conqueror id in the
  detail) — the record `relation-facts` projects into one `clan.conquered` fact per surviving clan, pair
  (conqueror, clan);
- **hub closed the same turn:** a clan's hub is, by definition, a hub on a sector the clan owns; from this
  point the sector's owner is `k`, so every read of "the clan's hub" misses it. `exchange` derives the
  closure from ownership (ask A9); nothing is written for it. **The building stays** (round 4, 2026-09-19): the
  clan's seeded Trading Post passes to `k` with the sector's slots, at its tier
  (`gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:108-116`), so the conqueror gains a working Trading
  Post there — the clan's trade ends, the building's feature now serves `k`. Nothing in this module moves or
  destroys it;
- **clan production ends there from the next turn:** production is by owner (`sector-yield`), so the
  sector produces under `k`'s rules from the next `Production`; `clan-economy`'s consumption no longer
  draws from it.

A clan sector lost to **fade** (owner null) is not a conquest: no `clan.conquered`, no relation fact.

### 3. An empire sector changes hands

For a sector owned at the opening by an AI empire and now by someone else: nothing is written. The
sector's warehouse moves with the sector (`sector-yield`'s located-stock rule) and the treasury is
unlocated, so it cannot move (`empire-treasury`). This module's contribution is the **test** that the
treasury is identical before and after.

### 4. Collapse

After §2 and §3, for each AI empire (dominant or rival) that owns **no sector holding a `Seat` slot**:

- if its treasury is non-empty, `EmpireTreasury.Destroy` zeroes it — a sink, recorded as stock deltas of
  kind `collapse` and reported `empire.collapsed:<factionId>`;
- collapse is **derived** each turn from "holds no seat", never stored. An empire that later retakes a seat
  is simply not collapsed; its treasury starts from zero. `Destroy` on an empty treasury does nothing, so the
  pass is idempotent.

Diplomacy with a collapsed empire (its treaties end, access closes) is derived by `exchange` `trade-access`
from the same predicate (`Collapse.IsCollapsed(world, factionId)`, exposed here) — no fact is written for it.

### 5. The capability flag

`counterparties.conquest` joins `world-stamp`'s registry — in **`counterparties` wave 3**, whose **one**
`RulesetVersion` bump it shares with `counterparties.clanEconomy` and `.sinks` (round 6 C1; row 17 of
[../landing-order.md](../landing-order.md) §2). A legacy world runs no pass. This module reads
`relation-facts`' emitter, which lands in wave 2 (row 16) — the in-cluster cycle the audit flagged is
resolved by that wave order, not by a seam.

## Tunables

None. What conquest does to relations is `npc-story-events`' shift for `clan.conquered` (ask A7).

## Numeric types

No new arithmetic; `Destroy` subtracts `long` balances to zero through `empire-treasury`.

## Acceptance (contract)

1. **Clan capture:** capturing a clan sector writes one `clan.conquered` report entry naming clan,
   conqueror and sector; the clan's hub reads closed to every `exchange` query that turn; the sector's
   production in the next `Production` is the conqueror's.
2. **Fade is not conquest:** a clan sector lost to fade writes no `clan.conquered`.
3. **Treasury is unlocated:** for a surviving AI empire, every treasury entry is identical before and after
   losing any sector, including a seat while another seat remains.
4. **Collapse:** an AI empire with no seat after `Snapshot` has an empty treasury; the destroyed amount
   appears as `collapse` stock deltas equal to the pre-destruction balance, and as a sink line in the economy
   report.
5. **Idempotent:** a collapsed empire with an empty treasury produces no delta on later turns.
6. **One capture path:** a source scan finds no write of `WorldSector.OwnerFactionId` outside
   `ClaimResolver` and `LoamPhases`' fade branch (the existing sites, `ClaimResolver.cs:101`,
   `LoamPhases.cs:219` — re-cited by the 2026-09-20 audit from `:218`) — this module writes none. The scan is
   about the **sector** owner; slot owners are also written by an assault
   (`gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:161`) and by a claim (`ClaimResolver.cs:115`), and the
   scan must not flag those.
7. **Legacy:** without the flag, no pass runs and the hash is unchanged.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Trade/ConquestPassTests.cs` (new): clan capture, fade, empire capture
  with treasury invariance, collapse and idempotence, legacy.
- Extend `gk-core/tests/FusionRpg.Core.Tests/World/ClaimTests.cs` with a clan-owned and an empire-owned target on a
  conquest-stamped world.

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs','src/FusionRpg.Core/World/Trade/ConquestPass.cs','tests/FusionRpg.Core.Tests/World/Trade/ConquestPassTests.cs','gk-core/tests/FusionRpg.Core.Tests/World/ClaimTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Trade|FullyQualifiedName~ClaimTests|FullyQualifiedName~TurnEngine"
```

## Hard edges

- **`Snapshot`'s signature** gains the opening world. `Snapshot` is private to `TurnEngine`; no external
  caller moves.
- **Phase list unchanged:** the pass is inside `Snapshot` (`decisions.md` *World turn phase order*).

## Dependencies

| Consumes | From |
|---|---|
| `EmpireTreasury.Destroy` | `empire-treasury` |
| Clan identity | `clan-seeding` / `clan-economy` |
| Stance rules for the collapsed empire's legions | `diplomatic-stance` |
| `clan.conquered` projection | `relation-facts` |
| `stock-deltas` (`collapse`, A10), `economy-report` | `trade-foundation` |

| Exposes | To |
|---|---|
| `clan.conquered:` report entries | `relation-facts`, `trade-stories` |
| `Collapse.IsCollapsed(world, factionId)` | `exchange` `trade-access` (A9), `trade-ai`, `trade-surface` |

## Contradictions found

1. **The map's capture hook.** The map said *"`ClaimResolver.cs` (a call into this module, not a second
   capture path)"*. A call from `ClaimResolver` would miss ground lost to fade in `Pressure`
   (`LoamPhases.cs:212-224`), and collapse can follow either. This spec hooks once, at the end of
   `Snapshot`, over the opening-versus-now ownership diff; `ClaimResolver` is not edited. Corrected in the map.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: turn engine (Snapshot), claims, fade, treasury, relation facts, economy report.
[~] Session boundary: trade-network-idea-20260919; session-boundary-check.py not re-run for this
    docs-only file.
[x] Read this session: as spec-need-vector.md's checklist, plus empire-economy-ssot §3 and the Snapshot
    body.
[x] decisions.md: phase order (:7) — no phase added.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: 0 HIGH.
[x] Verified against code: ClaimResolver ownership transfer, LoamPhases fade branch, BattleApplication
    slot-only writes, Snapshot resolver order, every sector-owner write site (grep).
[x] Surrounding sections read (§7.4 counterparties bullet, principle 9, §7.6).
[x] No "moves goldens" claim; legacy identity is an acceptance test.
[x] No §2 invariant contradicted; destruction is a named sink, not a clamp.
[x] Corrections propagated: the hook location in the map.
[x] No population pinned.
[x] No cache; collapse is derived per turn.
[x] Ordering: the pass reads opening-versus-now ownership, so claim order within Snapshot cannot change
    its result.
[x] No actor magnitude.
[x] No SOLID-violating path: one pass, no second capture path.
[ ] Registry row: the "no ownership write outside the existing sites" scan is a local test; no
    enforcement-registry row proposed.
```

## Audit 2026-09-20

Fixed here: the fade write site is `LoamPhases.cs:219`, not `:218`; the one-capture-path scan now says it
concerns the **sector** owner, since an assault legitimately writes **slot** owners
(`gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:146-161`). Open gap, reported (not this program's file): an
assault can take a clan's hub **slot** (its Trading Post) without the sector; this pass compares sector owners
only, so no `clan.conquered` fires and the clan's hub may keep trading from a slot the clan no longer holds.
Whether a split building counts for anyone is the owner rule `trade-foundation` `sector-features` should own
(counterparties-map CX1); if the ruling is "inert", this pass needs no change, and if it is "the slot owner's",
this pass also compares the hub slot's owner. Checked and clean: one pass at the end of `Snapshot` over
opening-versus-now ownership (sees claims and fade); fade is not conquest; the treasury is unlocated; collapse is
derived, idempotent and a named sink (`collapse`). **Verification boundary:** the
`core-world-trade-counterparties` owner boundary (`spec-empire-goods-sinks.md` *Audit 2026-09-20*) covers
`World/Trade/**`; the `TurnEngine.cs` edit stays on `core-fallback`.
