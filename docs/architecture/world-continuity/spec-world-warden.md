# Spec: `world-warden`

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Module 8 of the
[world-continuity map](../world-continuity-map.md) (wave 3; depends on `coarse-step`, external
legion-build standing orders / stances). Ideal: [world-continuity-ideal.md](../world-continuity-ideal.md)
§3.9, §6.4, W5. Reconciliation seam reused from the withdrawn
[warden-mortality-ideal.md](../warden-mortality-ideal.md) §The shape. Owner decision **Q3 (2026-09-19):
retire the per-sector warden verb and release existing bindings through a system-issued release
command.** House style: [../world-action-economy/spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).
**Round 4 (2026-09-19), binding** ([decisions-round-4.md](../trade-network/decisions-round-4.md)): the warden's
defence is the **power roll-up** of its warden legions (P, Q9 — §5); system-issued commands go through the
**one shared path `trade-foundation` builds** (Q10 — §3). The freeze removal shipped as `d6931e43a`
(`RulesetVersion` 13), and it placed the `bind-warden` refusal in admission — §2 is corrected to the code.

## Objective

Three things, one of them already done:

1. **The live decay-freeze is removed — SHIPPED, not this module's work.** Commit `d6931e43a`
   (2026-09-19, `TurnEngine.RulesetVersion` 12 → 13, `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:22-31`,
   `:125`) removed both freeze sites (`gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:194-203`) and made
   admission refuse every `bind-warden` with `warden.retired`
   (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:18-22`). No golden moved (its scenario binds no
   warden).
2. **Retire the per-sector `bind-warden` verb** (Q3): no new binding can be made through any route. The
   engine half shipped with item 1; the route and UI half is this module's (§2).
3. **Release every existing binding** through a system-issued `release-warden` `WorldCommand` resolved
   by the existing `WardenResolver`, and free each warden's contract slot at no cost (Q3).

And then the new job (W5): a **world warden** is a commander-role unique actor leading a legion
stationed on a world, whose Hub-read strength lowers the odds of losing frontier sectors and the seat
during coarse and idle resolution, which costs upkeep every period, and which **never freezes decay or
production losses** (ideal §3.9).

## Scope and non-goals

**In scope:** the verb retirement; the `release-warden` kind and its resolver branch; the one-time
release migration; the world-warden station as a legion stance; its defence term as a logged coarse
input; its upkeep; its availability rule; its fate when the world falls.

**Not in scope:** the freeze removal (item 1 — done elsewhere); the idle state it unlocks (`idle-world`);
the stance vocabulary's general widening machinery (legion-build owns stances; this module adds one
member through it); the FE station dialog (`multiverse-surface`), except removing the retired bind
dialog.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `bind-warden` kind, in the closed kind list | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:54`, `:125` |
| `WardenResolver` binds in `Snapshot`, re-validating ownership | `gk-core/src/FusionRpg.Core/World/Movement/WardenResolver.cs:21-63`; called at `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:439` |
| `WorldSector.WardenBindingId`, hashed | `gk-core/src/FusionRpg.Core/World/WorldState.cs:218`; `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:42-46` |
| Capture clears the binding | `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:107` |
| Admission is shared by submission and by `Reveal` inside `Step` | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:24`, `:28-34` (the `bind-warden` refusal; the old per-kind arm was removed by `d6931e43a`); callers `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:120`, `:277`, `TurnEngine.cs:233` |
| A garrison pays loam upkeep per member | `gk-core/src/FusionRpg.Core/World/Loam/LoamPolicy.cs:39` (`GarrisonUpkeepPerMember`) |
| Stances are a closed list `march`, `scout`, `hold`, `dowse` | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:10-24` |
| Commander role is a removable binding on a unique actor | `decisions.md` *Commander role* row; `warden-mortality-ideal.md` correction 2026-09-17 |
| Contracts and world command logs live in one database, one connection | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:4161` (`OpenUnlocked` → the one hot path) |

### Wiring gap — the withdrawn freeze and the permanent binding

| Gap | Evidence |
|---|---|
| **The freeze** (removed by the separate change, item 1): a warded sector is skipped as a fade target and on recovery | `gk-core/src/FusionRpg.Core/World/Loam/LoamForecast.cs:30-32`; `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:197-203` (as of this spec's reading of the main tree) |
| The verb is reachable in production | route `gk-core/src/FusionRpg.Server/WorldWardenEndpoint.cs:40-93`, mapped `gk-core/src/FusionRpg.Server/Program.cs:938`; web `gk-web/web/fusion-rpg-web/src/stages/world/confirms/BindWardenDialog.tsx`, `wardenGate.ts` |
| The bind is **non-releasable "for the life of the world"** — and worlds no longer end | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:276-283`; refusal `:351-353` (`contract.warden-permanent`) |
| The endpoint's comment says there is no cross-store transaction between the contract and the order; both live in the one hot database | `WorldWardenEndpoint.cs:18-22` vs `RpgStore.cs:4161` — a comment that is not evidence (DESIGN-GATE §3 rule 2) |

### Real gap

No `release-warden` kind (warden-mortality §The shape, never built); no world-scoped warden; no warden
defence term; no warden upkeep rule.

## Design

### 1. The freeze — precondition, done elsewhere

After the separate change lands, `WardenBindingId` no longer exempts a sector from fade or recovery.
This module's tests **assume** it (a sector with a binding moves `StabilityMilli` exactly as one
without), and fail loudly if run against a tree where it has not landed — they do not re-implement it.
`WardenBindingId` stays in `WorldState` and in its canonical row position: removing the field would
change every world's canonical text. It becomes a field that only ever returns to `null`.

### 2. Retire the verb — the engine refusal shipped in admission; this module removes the route

**Corrected to the code (2026-09-19).** This spec first placed the refusal at submission, to keep old logs
replaying as they did. The shipped change chose the other way and bumped the ruleset for it: admission
refuses every `bind-warden` with `warden.retired` (`WorldCommandAdmission.cs:18-22`), `Reveal` re-admits so a
bind filed under ruleset 12 is dropped (`TurnEngine.cs:436-437`), and the ruleset bump to 13 makes the replay
change honest (`TurnEngine.cs:22-31`). Code wins; this module does **not** add a second refusal at submission.

- Remove `POST /api/world/{worldId}/bind-warden` (`WorldWardenEndpoint.cs`, `gk-core/src/FusionRpg.Server/Program.cs`), its DTOs'
  use, and the web's `BindWardenDialog` and `wardenGate` (world-stage `world-confirms` loses the
  bind-a-warden confirm, `docs/architecture/world-stage-map.md:83`). The endpoint already asks admission
  first, so today it refuses before charging anything (`WorldWardenEndpoint.cs:30-34`); removing it is
  clean-up, not a behaviour fix.
- `bind-warden` stays in the closed kind list, so old logs still parse. No AI policy files it
  (searched `gk-core/src/FusionRpg.Core/World/Ai`).
- `RpgStore.BindAsWarden` (`RpgStore.Contracts.cs:283`) loses its only caller and is deleted with its
  tests; the `warden` contract column stays (it becomes always 0 after §3).

### 3. Release every existing binding — system-issued, replayable

New kind `release-warden` (payload `SectorId`, `WardenId`), added to the closed kind list as a reviewed
change. No existing log contains it, so it is a pure addition — the new-kind no-bump precedent
(`TurnEngine.cs:131-140`). `WardenResolver.Run` gains one branch:

```
release-warden: sector gone                      -> drop "sector.gone"
                sector.WardenBindingId != WardenId -> drop "warden.not-bound"   (capture already cleared it; idempotent)
                else                              -> WardenBindingId = null; report "warden.released:<id>"
```

**Migration — one time, idempotent, one transaction per save**, run in schema setup after
`world-state-vocabulary` and `coarse-step` have landed:

1. For every map world of the save, for every sector with `WardenBindingId` set: file a `release-warden`
   through **the shared system-command path `trade-foundation` owns (`trade-foundation` `system-commands`)** (owner Q10; `rift-trade-map.md` ask A7
   names its contract: a closed system-kind set that admission refuses from every commander, one Data filing
   path inside the commit transaction, deterministic command ids). `release-warden` is registered in that
   system-kind set; this module adds no filing path of its own. `CommandId =
   SystemCommandId.For("release-warden", sectorId, wardenId)` (`trade-foundation/spec-system-commands.md`
   §5 — the one id helper, which hashes a long id into the 64-character bound; a hand-built
   `"release-warden:{sectorId}:{wardenId}"` could exceed it), and the filing runs in the migration's own
   transaction (the path runs in its **caller's** transaction, same spec §4), commander = the sector's owner faction,
   `reason = "system:warden-retired"`. An existing `CommandId` is a replay (`CommandExistsUnlocked`,
   `RpgStore.WorldTurns.cs:143`), so a second run files nothing.
2. For every contract row with `warden = 1` of that save: set `warden = 0, bound = 0` — the slot is
   freed at no cost and the creature keeps its loyalty (the `ReleaseContract` semantics,
   `RpgStore.Contracts.cs:329-330` comment), without the `contract.warden-permanent` refusal.

Both steps share one transaction because both tables are in the one hot database (`RpgStore.cs:4161`).
The binding clears when that world next resolves: the active world's next End Turn (`Step`), or a
hibernating world's next coarse record (`coarse-step` §3 resolves system commands first). **Nothing
writes `WardenBindingId` from the Data layer** — that is the side-channel write warden-mortality
§The shape rules out, because replay would never reproduce it.

### 4. The world warden — a stance on one legion architecture

Owner ruling (legion-build ideal principle 6): caravan, escort, garrison and warden are **orders and
stances on one legion architecture**, never separate entity kinds. So:

- A **warden** is a legion in the world holding the new stance `warden` (added to `MovementPolicy.Stances`,
  `LaneCost.cs:21`, as a reviewed widening under legion-build's stance vocabulary), standing on a sector
  its faction owns, with a member whose unique actor holds the commander role. `BudgetFor(warden)` is 0
  (it does not march) — the `hold` frame.
- It is set by the ordinary `stance` order while the world is **active** (the player stations it, then
  leaves). There is no cross-world stationing verb in v1: to station on a hibernating world the player
  selects it, sets the stance and switches back.
- ~~At most one warden per world~~ — **corrected by the 2026-09-20 audit.** Owner decision P says *"an old
  world's defence = the sum of its **warden legions**"*, and §5 sums over them, so a one-per-world cap
  contradicted a binding decision (and was an unregistered count cap). A world may hold several warden
  legions; **each** must contain a commander-role member (W5: *"a warden is a commander with a legion"*),
  so every extra warden costs a commander who is then unavailable everywhere else, plus its own garrison
  upkeep (§6) — the price, not a cap. A `warden` stance order for a legion with no commander-role member
  drops `warden.no-commander`.
- **Availability:** a stationed commander cannot be seated or deployed in another world or mode; the
  commander-role binding's existing exclusivity check reads "stationed as warden" as occupied. Its
  legion is in that world, so it is physically unavailable elsewhere by construction.

### 5. Strength — the power roll-up of the warden legions (round 4, P / Q9)

**Warden defence = the rolled-up power of the world's warden legions** (owner decisions P and Q9):
`wardenPower = Σ legion-build LegionPower.Of(legion)` over the legions holding the `warden` stance
(`legion-build/spec-legion-power.md` §3: each legion is Σ fighting stacks of unit Standing × `Count`, Hub
output only). It is computed **Data-side** inside the transaction that runs the coarse record or the idle
collect — the same seam as `HubInputsFor` (`RpgStore.WorldTurns.cs:548-600`) — and **logged** in the coarse
record's inputs as the `long` roll-up; replay reads the logged value and never re-reads the Hub.

During coarse and idle resolution the warden term enters its world's frontier contests
(`coarse-step` §5: `p = Sigmoid(ΔΘ − defenceΘ, scale) × pressure`), where
`defenceΘ = ContestTheta(wardenPower) × wardenDefenceWeightMilli / 1000`. **`ContestTheta` is the power
program's conversion** (the §10 row `legion-power` §5 requests; `PowerLadder` has no inverse today,
`gk-core/src/FusionRpg.Core/Power/PowerLadder.cs:26-65`). Until that row lands, **the term is 0** (round 4 P: *"until it
lands, the warden defence term is 0"*): the roll-up is still computed and logged, the digest shows it, and
`defenceΘ = 0`. A flat bonus in the meantime is rejected: it would not be read from the Hub, which W5
requires. Everything else (retirement, release, stance, upkeep, availability) does not wait.

This replaces the first draft's recommendation (`P⁻¹(Σ member combat power)` over members): the owner chose
the container roll-up, so a warden's strength is the same number the escort and the AI read for any legion.

Monotone by construction: `Sigmoid` is increasing in its argument, so a larger `defenceΘ` never raises
loss odds, for every Θ gap.

### 6. Upkeep — the garrison sink, no new number

A warden legion is a garrison: it pays `GarrisonUpkeepPerMember` (`LoamPolicy.cs:39`) from its anchor
component every turn, which the coarse step measures through the stock-delta rates it already reads
(`coarse-step` §2) — **not** scaled down in the background. The commander's contract upkeep in souls
continues as for any bound contract (`ContractPolicy.UpkeepPerDay`, used at `RpgStore.Contracts.cs:263`).
So "a warden costs upkeep every period" is satisfied by two sinks that already exist; adding a third
number would be a second price for the same act. If the anchor cannot pay, the component fades as any
unpaid component does, and the warden legion is subject to legion supply like any other.

### 7. Fate

- The warden legion can be destroyed by a coarse contest; its cargo follows `cargo-fate`, and the
  commander's specimen follows the shared `Retired` path (warden-mortality: *"a Warden is not a new kind
  of entity"*).
- A world that falls (`world-fall`) with its warden alive: the warden stays stationed on whatever the
  player still holds; with no owned sector left, the stance drops at the next record with
  `warden.no-ground` and the legion stays as an ordinary legion.

## Built / wiring gap / real gap (summary)

| Bucket | Item | Closed by |
|---|---|---|
| Wiring gap | freeze | **already done** by the separate change (§1) |
| Wiring gap | per-sector verb reachable; permanent binding | §2, §3 |
| Real gap | release kind; world warden; defence term; upkeep rule | §3–§6 |
| Blocked | defence term's Θ conversion (the roll-up itself is `legion-build` `legion-power`) | power-scale §10 row (§5); term is 0 until then |

## Acceptance (contract)

1. (Precondition, proven by the separate change and re-asserted here) with a binding present,
   `StabilityMilli` moves exactly as without one.
2. No route accepts `bind-warden`: the endpoint is gone (404), and admission's shipped `warden.retired`
   refusal is the only refusal (no second one at submission); a log recorded under ruleset 13 replays to its
   stored hashes.
3. After the migration and one resolution per world, no sector has a `WardenBindingId`; every former
   warden contract is unbound with `warden = 0`, loyalty unchanged, no soul ledger row written.
4. The migration is idempotent (second run files nothing, writes nothing).
5. `release-warden` over an already-cleared binding drops `warden.not-bound` and changes no state.
6. Warden strength is the logged `legion-power` roll-up of the warden legions, read from Hub output only;
   replay of a coarse record with a warden never calls the Hub (a replay with the Hub delegate absent
   succeeds); with no §10 row, `defenceΘ` is 0 whatever the roll-up.
7. Loss odds with a warden are ≤ without, for every Θ gap (monotone; property test over the gap range).
8. A warden's garrison upkeep is charged every turn it is stationed, in full step and coarse step alike.
9. A stationed commander is refused for any other seat or deployment with a named reason.
10. (Audit 2026-09-20) Two warden legions on one world each pay their own garrison upkeep, and the logged
    `wardenPower` is their sum (order-independent over legion order); a `warden` stance on a legion with no
    commander-role member drops `warden.no-commander`.

## Test plan and verification boundary

- `gk-core/tests/FusionRpg.Core.Tests/World/BindWardenThreadingTests.cs` (rework to `WardenRetireTests`): 1, 5.
- `gk-core/tests/FusionRpg.Core.Tests/World/WorldCommandAdmissionTests.cs` (extend): `release-warden` admission;
  `bind-warden` admission unchanged (replay).
- `gk-core/tests/FusionRpg.Data.Tests/WardenContractTests.cs` (rework): 3, 4.
- `gk-core/tests/FusionRpg.Server.Tests/WorldBindWardenEndpointTests.cs` → replaced by a retirement test: 2.
- `tests/FusionRpg.Core.Tests/World/Continuity/CoarseStepTests.cs` (extend): 6, 7, 8.
- Web: remove `BindWardenDialog.test.tsx`, `wardenGate.test.ts` with their components; `npm test`,
  `npm run build`.

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
python gk-core/scripts/guard-actor-hub.py
python gk-core/scripts/guard-dal.py
```

Crosses Core, Data, Server and web: the full suite once at module end.

## Hard edges

- **`rpg_worlds` schema:** none. `rpg_world_commands` receives system-issued rows (same schema).
- **Replay:** `bind-warden` stays parseable; `release-warden` is a new kind resolved inside `Step` or
  `CoarseStep`, so replay reproduces every clear. The freeze removal's own bump belongs to the separate
  change (it landed as `RulesetVersion` 13, `d6931e43a`).
- **Wave and ruleset bump (round 6 C1).** One capability flag and one `RulesetVersion` bump **per wave**, so a
  world's rules never change mid-life. This module is world-continuity **wave 3** and grants a player-facing
  feature (the resumed warden, its defence term and the `warden` stance), so it does **not** claim "no bump":
  it rides **wave 3's single bump**, taken at landing, never pre-assigned (map *Audit 2026-09-20* R1) and
  recorded in [../trade-network/landing-order.md](../trade-network/landing-order.md). ~~this module adds only a
  new kind (no bump) … the `warden` stance is a new stance value no old log contains (no bump).~~ Those facts
  still explain why **no old log is invalidated and no golden moves here** — the bump is about the stamp, not
  the bytes.
- **Corpse-cache tick key:** none.
- **Goldens:** none from this module (the freeze removal's re-bless is the separate change's).

## Dependencies

`coarse-step` (logged inputs, system-command resolution), `world-state-vocabulary` (the not-active gate);
external `trade-foundation`'s shared system-command path (Q10), legion-build stance vocabulary (the `warden`
stance) and `legion-power` (the roll-up), the power program (the §10 row for §5), scoped-inventory
`cargo-fate`. Consumed by `idle-world` (entry condition), `multiverse-surface`.

**Rift ask A9 does not apply here:** a warden is stationed by an in-step `stance` order and never moves a
legion between worlds Data-side, so there is no crossing-anchor view to republish (A9 binds
`advance-carry`).

## Tunables

| Key | Unit | Provisional | Home |
|---|---|---|---|
| `wardenDefenceWeightMilli` | per-mille weight on the Θ term | 1000 | `data/tuning/world-continuity.v1.json` |

Upkeep uses the existing `GarrisonUpkeepPerMember` and contract upkeep; no new upkeep key.

## Boundaries

- **Always:** clear bindings only through `release-warden`; log the defence term; the garrison sink.
- **Ask first:** a cross-world stationing verb; a warden defence term not read from the Hub.
- **Never:** a decay or production freeze in any form; a Data-side write to `WardenBindingId`; a
  **second** `bind-warden` refusal at submission beside the shipped admission refusal (§2 — corrected by
  the 2026-09-20 audit: this line said "refusing `bind-warden` inside admission", the opposite of the
  shipped code and of §2); a new warden entity kind.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `release-warden` kind + `WardenResolver` branch | this module's migration; `world-reclaim` later |
| `warden` stance, one per world | `idle-world`, `multiverse-surface` |
| `wardenPower` (logged roll-up) and `defenceΘ` | `coarse-step`, `idle-world`, `away-digest` (warden fights) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: turn engine (Snapshot, Reveal admission), loam fade (freeze — precondition only),
    contracts store, world endpoints, web confirms, stances, ActorHub read seam.
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json; check not re-run.
    The freeze removal runs in another session's worktree; this spec touches none of its files.
[x] Read this session: warden-mortality-ideal.md in full; world-continuity-ideal.md §3.9, §6.4;
    legion-build-ideal.md principle 6, §6.3; legion-build-map.md standing-orders row; plus the rows
    listed in spec-world-state-vocabulary.md.
[x] decisions.md checked: Commander role row; no warden lock beyond the withdrawn one.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: both freeze sites, the endpoint, BindAsWarden and its refusal, admission's
    two callers, the one hot connection, stance list, garrison upkeep.
[x] Surrounding sections read (the endpoint's accepted-risk comment — and found it wrong).
[ ] Constraint tested: none run here; the freeze removal's golden movement is the other change's.
[x] No §2 invariant contradicted: one ActorHub read; no private fold (the Θ conversion is filed to the
    power SSOT rather than invented).
[x] Corrections propagated: map module 8 row, map decisions (Q3).
[x] No population pinned.
[x] No cache.
[x] Migration order-independent across worlds and saves (per-save transaction, idempotent).
[x] Actor magnitude consumed from Hub output only.
[x] No SOLID fork: one resolver extended; warden is a stance, not an entity kind.
[ ] Registry row: "no Data-side write to WardenBindingId" — added when built (source-scan guard).
```
