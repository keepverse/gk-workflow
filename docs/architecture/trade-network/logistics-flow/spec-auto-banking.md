# Spec: `auto-banking`

**Status: written against code 2026-09-19** (branch `features/mega-merge`, `b82a4098`). Every
`file:line` below was opened in this session. Module id `auto-banking`, row 7 of the
[logistics-flow map](../logistics-flow-map.md) (wave 3; depends on `lane-flow`, `transit-buffer`,
`path-cache`; `sector-yield` `bank-points` and `banking-fact`). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §8.6 (*yields flow automatically toward the nearest
bank point*), §8.5 (*auto-banking is on by default*), §8.7 (*`route-set`, `route-clear` … policy commands
set policy; they move nothing themselves*); `sector-yield-map.md` §2.9 (*"the policy commands that change
it belong to `logistics-flow`"*). **Round 5 (2026-09-20)**, [../decisions-round-4.md](../decisions-round-4.md):
A4/X15 — the default banking hold keeps enough to fill **other traders' open buy orders at this hub**; A1 —
every empire's seat starts with a tier-1 Counting House, so the default destination exists from turn 1;
X1/X13 — bank points and tiers are read through `sector-features` (via `BankPoints`). House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Make banking the default with no orders at all: every good sitting in an own sector that is not a bank
point flows to the nearest own bank point — a sector with a Counting House (round 4 §B) — and banks the
turn it arrives, up to that bank point's rate. Give every commander — human and AI alike — three policy
commands: `route-set` sends one sector's flow of one good to a named own destination, `route-clear`
restores the default, and `bank-hold` keeps a quantity of one good at a Treasury-tier bank point instead
of banking it (round 4 Q2). None of them moves a single unit itself.

Success looks like: a new player who never opens a menu sees goods bank; a player who routes fire
essence to a forge sector sees exactly that one flow change; and a route whose destination is captured
falls back to the default without losing anything.

## Locked anchors

- **One command shape, one admission gate, for every commander** (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:130-140`
  doc: *"Every commander — the human, Zomboss, a clan — submits this same shape through the same path"*;
  admission `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:24`). No player branch.
- **Admission is cheap; legality is at resolution** (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:3-11`).
  Ownership can change between filing and resolving, so it is checked again when the policy resolves.
- **Ownership-sensitive orders resolve in `Snapshot`, after claims** — the `build`/`raise`/`develop`
  precedent (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:415-433`; `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:56-74`).
- **Banking is `banking-fact`'s** — the fact, its key and its ledger credit. This module decides only
  where goods go; it never writes a treasury or a ledger row (umbrella §1a CM3).
- **Loam never flows; world stocks never bank** (ideal §3 principles 6, 7).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The closed command-kind list and its `IsKnown` gate | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:124-129` |
| Typed optional payload fields, persisted as one JSON payload per command | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:140-219`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:190-194`, `:467-473` |
| Wire DTO and its two mapping sites | `gk-core/src/FusionRpg.Contracts/WorldDtos.cs:519`; `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:138`, `:247` |
| Snapshot's resolver order: claim, build, raise, develop, warden, postures | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:415-441` |

### Wiring gap

None.

### Real gap (this module closes it)

The default-destination rule and the two policy commands through all their plumbing sites.

## Design

### 1. The default destination

For a route `(faction, source, good)` with no valid policy, the destination is the faction's **nearest
bank point by path cost** over ground open to it (`path-cache`'s bank tree; ties by sector id). Goods
produced at a bank point never flow — L3 banks them in place. A source with no reachable bank point
sends nothing and records `no-path`. Auto-banking is always on: there is no switch to turn it off, only
policies that redirect individual flows.

Only **located goods** have a default. `rubble` and `ironwork` are world stocks: they stay where they
are unless a policy moves them (`construction-chain`). Loam and recruits never form a route.

### 2. The two commands

| Kind | Fields | Effect when it resolves |
|---|---|---|
| `route-set` | `SectorId` (source), `GoodId`, `DestinationSectorId`, `Priority` (optional, default 0) | Upserts the `RoutePolicy` for `(commander, source, good)` |
| `route-clear` | `SectorId` (source), `GoodId` | Removes that policy; marks the route's `Stranded` packets `Returning` (`transit-buffer`) |

`GoodId`, `DestinationSectorId` and `Priority` are new optional fields on `WorldCommand`,
`CommandPayload` and `WorldCommandRequest`, mapped at both endpoint sites. They default to null, so every
stored payload written before this module reads back unchanged (the null-tolerant read-back the
payload record already documents, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:458-473`).

**Admission** (submit time, cheap): known kind; `SectorId` names a sector the commander holds;
`GoodId` names a located good, `rubble` or `ironwork` — `loam`, recruits or an unknown id is refused
(`good.not-routable`); for `route-set`, `DestinationSectorId` names a sector the commander holds.

**Hold (flow).** A `route-set` whose destination **is** its source is a **flow hold**: that good stays in
that sector and does not flow. Goods delivered by a policy to a non-bank destination join that sector's stock
and are subject to that sector's own policy — the default sends them on to the nearest bank point, so a
player who wants goods to stay at a hub (for `exchange` to sell, or for a `fleet` caravan to load) sets
a hold there. One rule, no special case for "final" destinations.

**Resolution** (in `Snapshot`, after `WardenResolver` and after `lane-verbs`' resolver): the same
ownership checks again against the settled turn — a claim or fade earlier in the turn has already
landed. A command that fails is dropped with its reason (`TurnReportKinds.CommandDropped`); an accepted
one writes or removes the `RoutePolicy` and nothing else. Several policy commands for one route in one
turn: the last filed wins (the stance precedent, `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:441-445`).

### 2a. `bank-hold` — the banking hold (Treasury tier)

| Kind | Fields | Effect when it resolves |
|---|---|---|
| `bank-hold` | `SectorId` (a bank point), `GoodId`, `Qty` (`long`, ≥ 0; 0 clears) | `BankingHolds.Set(sector, good, qty, setBy: commander)` — `sector-yield` `banking-fact` §3a owns the state and applies it only while the setter owns the sector |

The flow hold above keeps goods from **leaving** a sector; `bank-hold` keeps them from **banking** at a
bank point, which is what a hub selling through `exchange` needs (exchange ask E-A11; round 4: *"the home
hub keeps stock to sell through the Treasury tier's per-good hold"*). The default hold — **enough to fill
other traders' open buy orders at this hub** (round 5 A4, replacing round 4's "what open sell orders
need") — is `exchange`'s registered hold source (`banking-fact` §3a) and needs no command. `bank-hold` is
the commander's own override on top of it (the larger of the two applies).

- **Admission:** `SectorId` is held by the commander; `GoodId` is a located good that banks; `Qty ≥ 0`.
- **Resolution** (in `Snapshot`, with the route resolver): the sector is still the commander's and
  `BankPoints.TierAt(sector) ≥ 2`; otherwise dropped with `bank.hold-needs-treasury` (tier) or the
  ownership reason. `Qty` reuses the existing optional `WorldCommand.Qty` field
  (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:215-219`), so only `GoodId` is new wire surface for this
  kind.
- `trade-ai` files it for an AI owner through the same path (no player branch).

### 3. Destinations that stop being valid

A policy stays stored when its destination is lost later (capture, fade, cede); each turn the route falls
back to the default while the destination is not own, and returns to it if the sector is retaken. The
fallback is reported (`logistics.route`, detail `destination-lost`) so the player sees why goods changed
course. Nothing is lost by the fallback itself.

**A lost source makes the policy dormant (audit 2026-09-20).** A policy is keyed by its commander, so when
the **source** sector changes hands the route simply does not form (a route needs an own source,
`lane-flow` §1) and the policy stays stored, inert; the captor's own policies are separate rows and are
never shadowed by it. Retaking the source revives the policy the next turn. The same rule `banking-fact`
§3a gives policy holds, so every commander-owned policy in the phase behaves one way.

### 4. World stocks and bank points — a deviation from the map's acceptance

The map's acceptance says *"no policy can name a bank point as the destination of a world stock"*. This
spec does not refuse it. A world stock delivered to any sector lands in that sector's `RubbleStock` or
`IronworkStock` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:181`, `:187`) — never in the located-goods
warehouse — and `banking-fact` never takes a world stock (its own acceptance: *"no fact ever credits loam,
rubble, ironwork or recruits"*, `sector-yield-map.md` §2.9). Refusing the capital as a destination would
stop a player moving ironwork to where they build most. The invariant the map wanted — a world stock
never reaches a banking fact — is kept and guarded by `construction-chain`. Reported as a deviation.

### 5. Determinism and allocation

Admission and resolution iterate commands in the stable order `Reveal` already fixes; policies are kept
in `(faction, source, good)` order (`logistics-canonical`). The default-destination read is an array
lookup in the bank tree.

## Tunables

None. Priority is a player-set integer, not a balance number.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.AutoBanking|FullyQualifiedName~World.Turn"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldCommandRoundTrip|FullyQualifiedName~WorldCommandStore"
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session id>
```

## Structure

```
src/FusionRpg.Core/World/Logistics/AutoBanking.cs        (new) — default destination; RouteResolver (Snapshot)
gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs            MODIFIED — RouteSet, RouteClear, BankHold kinds;
                                                          GoodId, DestinationSectorId, Priority fields
gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs   MODIFIED — the two kinds' admission rules
gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs              MODIFIED — one resolver call in Snapshot
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs         MODIFIED — CommandPayload fields
gk-core/src/FusionRpg.Contracts/WorldDtos.cs                     MODIFIED — WorldCommandRequest fields
gk-core/src/FusionRpg.Server/WorldEndpoints.cs                   MODIFIED — both mapping sites
tests/FusionRpg.Core.Tests/World/Logistics/AutoBankingTests.cs   (new)
```

## Testing strategy

- **Default:** with no policy, every located good in an own non-bank sector flows toward the nearest bank
  point by path cost, ties by sector id; a sector with no reachable bank point sends nothing and records
  `no-path`.
- **Same-turn banking:** delivered into a bank point's warehouse on turn *t* ⇒ banked on turn *t*
  (L1 before L3), per good.
- **Scope:** `route-set` changes only the named `(sector, good)` flow; `route-clear` restores the default
  exactly (the next turn's flows equal a world that never had the policy).
- **Hold:** a `route-set` to its own source keeps that good in place; goods delivered to a policy
  destination without a hold continue to the nearest bank point next turn.
- **Refusals:** loam, recruits and unknown goods are refused at admission with `good.not-routable`.
- **Order-independent:** a `route-set` and a claim of its destination by another faction in the same
  turn resolve the same in either filing order — the policy is dropped and the default applies.
  Likewise our own claim of the destination and our `route-set` to it, in either filing order: the policy
  lands.
- **Fallback:** a destination captured two turns after the policy was set sends goods to the default and
  reports `destination-lost`; retaking it restores the policy's flow.
- **No player branch:** an AI commander's `route-set` and a human's, on mirrored worlds, produce mirrored
  state.
- **Round trip:** a stored `route-set` payload survives the command store and reloads with every field.

Verification boundary: Core (World/Logistics, World/Turn) and Data (command store). The command crosses
Core, Data, Contracts and Server — `verify-change.py` with all changed paths selects each boundary.

## Acceptance (contract)

1. With no policy, located goods flow to the nearest reachable own bank point, ties by sector id.
2. A delivery into a bank point on turn *t* banks on turn *t*.
3. `route-set` changes only its `(sector, good)` flow; `route-clear` restores the default exactly.
4. Loam and recruits can never be routed; world stocks can be routed but never bank.
5. A same-turn `route-set` and destination capture resolve the same in either filing order.
6. The AI and the player file the same three commands through the same admission path.
7. `bank-hold` resolves only at a bank point of tier ≥ 2 (`bank.hold-needs-treasury` otherwise); `Qty 0`
   clears the hold; the hold changes what banks, never what flows.
8. **Dormant, not deleted:** a policy (route or hold) whose source sector its commander no longer holds
   moves nothing and holds nothing, whether the capture resolved before or after the policy was filed in
   that turn (both orders tested); a retake revives it; the captor's policies on the same sector are
   unaffected.

## Hard edges

- **Command vocabulary:** three new kinds join the closed list — a reviewed change; the list's size is a
  closed vocabulary, asserted as such where it is pinned.
- **Wire contract:** three new optional request fields. Additive only; if the contract version policy
  requires a bump for additive fields, it is taken in this change (PRINCIPLES §6: narrowing or renaming
  bumps `CONTRACT_VERSION`; adding does not narrow).
- **Ruleset / goldens:** this module is `logistics-flow` **wave 3** and gates on that wave's flag
  **`trade.logisticsPolicy`**, registered with the wave's one `RulesetVersion` bump and shared with
  `construction-chain` and `lane-verbs` (round 6 C1; row 7 of [../landing-order.md](../landing-order.md)
  §2). It does **not** widen wave 1's `trade.logistics`: a default flow destination and three policy
  commands are behaviour, and a world stamped at wave 1 must not acquire them mid-life. New command kinds
  cannot appear in any existing command log, so no existing golden moves (the `Assaults` precedent,
  `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:131-140`, is about the *log*, not about skipping the
  capability bump).
- **Round 6 C3 — this lands before anything banks.** `banking-fact`'s step half waits on the save-identity
  re-key (its §1a), so at this wave's landing the default destination works and the `bank-hold` state is
  set and stored, but **no good leaves the map**: goods arrive at the nearest bank point and wait. The hold
  source seam registers as specified; it simply holds nothing back from a step that is not running yet. No
  acceptance criterion here asserts a banked total.
- **Deviation from the map:** world stocks may be routed to a bank point (§Design 4). Reported.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `route-set` / `route-clear` | `construction-chain` (world stocks), `trade-surface` (policy editor), `trade-ai` (AI logistics), `forecast-facts` (answers to a throttle) |
| `bank-hold` | `trade-surface` (policy editor), `trade-ai` (AI sell holds), `exchange` (E-A11) |
| Default destination read | `lane-flow`, `transit-buffer`, `forecast-facts` |

## Boundaries

- **Always:** policies only; ownership re-checked at resolution; same path for every commander.
- **Ask first:** a switch that turns auto-banking off; a policy that names a foreign destination (that is
  `exchange`'s order lifecycle, not a route policy).
- **Never:** a policy that moves goods itself; routing loam or recruits; writing a treasury or ledger.

## Design-gate checklist

```
[x] Subsystems: world commands (kinds, admission, payload, wire), turn engine (Snapshot), logistics.
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json;
    session-boundary-check.py not run (docs only).
[~] Read this session: as in spec-logistics-phase.md, plus the command pipeline's five sites. Gap:
    spec-turn-engine.md not read this session.
[x] decisions.md: Empire resource registry row (loam never moves by trade) respected.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding left.
[x] Verified against code: kind list, admission shape, Snapshot resolver order, payload record, both
    endpoint mapping sites, the null-tolerant payload read.
[x] Surrounding sections read: WorldCommandAdmission's class doc; Snapshot's resolver comments.
[x] Constraints tested, not assumed: "no golden moves" rests on new kinds, proven by acceptance tests.
[~] §2 invariants: none contradicted. One deviation from the map's acceptance named (§Design 4).
[x] Corrections propagated: deviation stated here and in the session report.
[x] No population pinned; the kind list is a closed vocabulary.
[x] Event-refreshed cache: policies feed path-cache's key (T8), tested there.
[x] Orderings: route-set vs capture, both filing orders and both owners.
[x] Actor magnitudes: none.
[x] No SOLID fork: one command shape, one admission gate, one resolver slot.
[x] Registry row: none owed.
```
