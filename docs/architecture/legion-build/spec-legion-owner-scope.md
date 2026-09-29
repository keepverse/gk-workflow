# Spec: `legion-owner-scope`

**Status: written against shipped code 2026-09-19.** Module id `legion-owner-scope`, row 6 of the
[legion-build map](../legion-build-map.md) (wave 2; depends on `member-stack`). Owner decision **L1**
(layer 5c and `OwnerKind.Legion` approved), [legion-build-ideal.md](../legion-build-ideal.md) §6.2.

## Objective

Layer 5c exists. A legion is a durable owner scope. `world-buff.*` containers bind to it and are withdrawn
from it; one registered reader turns a legion's bound atoms into contributions for each of its fighting
members, each named by a SourceId a sheet can explain. Standards, traditions, doctrine and cohesion all
reach an actor through this module and no other path.

Success looks like: a `world-buff` container bound to a legion contributes to every fighting member of
that legion and to no other actor; when the legion disbands, routs or is destroyed, or when the state that
justified a binding changes, the contribution is gone in the same commit; every contribution carries a
non-empty SourceId; `guard-actor-hub.py` stays green.

## Scope and non-goals

- **In:** `OwnerKind.Legion`; its grammar and bind rule; the binder (reconcile against a desired set); the
  reader; the SourceId; the Θ scaling of 5c magnitudes; the three register rows.
- **Out:** what a standard, tradition, doctrine or cohesion band **contains** (modules 10–13 name the
  desired bindings; `empire-seed` `legion-bands` resolves their seed numbers). Legion equipment is layer 3,
  not 5c (`legion-equipment`).

## The five layer answers (`actor-layer-compose-ideal.md`, "What a new feature owes this stack")

| Question | Answer |
|---|---|
| Which layer | **5c legion** — new, approved (L1); placed between 5b empire title and 6 aura |
| Scope | The fighting members of one legion in one world. **Not** an empire scope: it does not answer the empire-scope question `world-buff`/`world-map-scope`/`empire-title` compete for |
| Lifetime | Live, derived: exists while the legion exists and the state behind it holds (a standard while its carrier lives, traditions until rout or disband, doctrine while adopted, cohesion while the roster qualifies) |
| Carrier | A `world-buff.*` atom container, bound to `OwnerKind.Legion` — the existing container carrier, not a third one |
| Provenance | `legion:{entityId}:{containerId}`, minted by `ContributionSourceIds.Legion`, labelled by `FictionLabel` |

## What already exists

| Kind | Finding | Evidence |
|---|---|---|
| Built, inert | `ContainerKind.WorldBuff`, prefix `world-buff`, validated and stored; nothing binds or reads it | `gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs:38,203`; `gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerValidator.cs:35`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Containers.cs:575` |
| Built | `OwnerKind` has eight members; `Name`/`Validate` switch on each | `gk-core/src/FusionRpg.Core/Effects/Atoms/OwnerScope.cs:20-30,53-64,108-164` |
| Built | World scopes refuse without a world host | `gk-core/src/FusionRpg.Core/Effects/Atoms/BindGate.cs:47-51` |
| Built | Bindings live in one global table keyed by owner kind and key — **no world column** | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AtomInstances.cs:83-96` |
| Built | `BoundDerivedAtom(Channel, Op, Amount, SourceId)` → `AtomDerivedSubsystem`, fed to battle through `BattleHubInputs.BoundAtoms` | `gk-core/src/FusionRpg.Core/Stats/Derived/Subsystems/AtomDerivedSubsystem.cs:91-92`; `gk-core/src/FusionRpg.Core/Battle/BattleHubInputs.cs:21`; `gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs:72` |
| Built | SourceId helpers and `FictionLabel` | `gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs:19-71` |
| Built | The one content-scale funnel for `P(Θ)` magnitudes | `gk-core/src/FusionRpg.Core/Power/ContentScale.cs:15-31` |
| Real gap | No `Legion` owner, no binder, no reader, no SourceId | — |

### Finding: the owner key must name the world

Entity ids repeat across worlds — every world built from a template holds `e-dave-legion-1`
(`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:184`) — and `effect_binding` has no world column
(`RpgStore.AtomInstances.cs:83-96`). A key of the entity id alone would bind one save's standard to every
save's legion of the same id. The map's `legion:{entityId}` grammar is corrected here.

## Design

### 1. `OwnerKind.Legion`

Appended as the ninth member (ordinals of the eight are unchanged). String form `legion`. Key
`{worldId}/{entityId}`: both halves non-empty, neither containing `/`, `:` or whitespace. Grammar is
checked in `OwnerScope.Validate`; **existence** (the world exists, the entity exists in it and is a
legion-kind entity with members) is a bind-time check against the world host, the same split
`Sector`/`Slot` use (`OwnerScope.cs:141-147`). Durable: `IsSessionScoped` stays `Entity`-only
(`OwnerScope.cs:49`). `BindGate` adds `Legion` to its world-host rule (`BindGate.cs:49`).

### 2. The binder — reconcile, never append

`src/FusionRpg.Data/Sqlite/RpgStore.LegionBuffs.cs` (new; the file does not exist yet). One entry point,
run in the turn-commit transaction after `TurnEngine.Step` and the graph diff:

```text
ReconcileLegionBuffsUnlocked(db, tx, worldId, WorldState next):
  for each entity in next with members:
     desired = LegionBuffSources.For(next, entity)        // Core, pure: (containerId, sourceTag) set
     stored  = effect_binding rows where owner = legion:{worldId}/{entityId}
     bind desired − stored; withdraw stored − desired
  for each stored legion owner in this world whose entity is gone: withdraw all
```

`LegionBuffSources.For` (new; the file does not exist yet: `src/FusionRpg.Core/World/Legion/LegionBuffSources.cs`)
is a closed list of contributors, each a pure function of hashed world state, added by its
module: `legion-standards`, `legion-traditions`, `legion-doctrine`, `legion-cohesion`. The `source` column
records which (`legion-standard`, `legion-tradition`, `legion-doctrine`, `legion-cohesion`).

Why reconcile rather than bind/withdraw at each event: every lifetime rule (carrier death, rout, disband,
destruction, roster change, doctrine switch) is then one diff against hashed state, so no trigger can be
forgotten (`DESIGN-GATE.md` §2.16) and the result is order-independent and idempotent — a re-run of the
commit, or a replayed turn, converges to the same rows. It refuses any container whose kind is not
`WorldBuff`.

**Where the reconcile runs — every write of a world graph, not only the turn commit (corrected by the
2026-09-20 audit).** A diff against hashed state removes the *value* triggers, but the reconcile only
sees state it is run against, and §2.16's forgotten trigger is exactly the edge where the **key set**
moves: a legion entering a world. The first draft ran it only after `TurnEngine.Step` in the commit, so a
world created with legions, or a legion arriving by advance, would fight its first turn's battles with
no 5c at all, and a legion destroyed in a hibernating world's coarse catch-up would keep its bindings
until that world next committed. The full trigger set, each its own test:

| # | Trigger | Where | Key-set edge? |
|---|---|---|---|
| T1 | Turn commit, after `Step` and the graph diff | `RpgStore.WorldTurns.cs` commit (as above) | yes (raise, destruction, disband) and value edges |
| T2 | World creation, including a genesis arrival manifest | `world-continuity` `world-creation` §1 / `advance-carry` §3 — after the graph write in `CreateWorldUnlocked` | **yes — legions enter the world** |
| T3 | Advance — both worlds, same transaction | `world-continuity` `advance-carry` §3 step 6 | **yes — a legion leaves one world and enters another** |
| T4 | Coarse record (hibernating catch-up, idle collect) | `world-continuity` `coarse-step` §4 — after its one graph write | yes (a legion destroyed by a coarse contest) |
| T5 | Any other Data-side graph write that adds or removes a legion (for example `rift-trade`'s crossing) | the writer's own transaction | yes |

Rule: **a Data path that writes a world graph and does not run this reconcile is a defect.** The guard is
a source-scan test that every caller of the graph writers (`WriteWorldGraphUnlocked`,
`DiffWorldGraphUnlocked`) in `FusionRpg.Data` also calls `ReconcileLegionBuffsUnlocked`, with an
allow-list for delve worlds (no legions), stated in the test.

### 3. The reader

```text
LegionBoundAtomsUnlocked(db, tx, worldId, WorldEntity legion, WorldEntityMember member)
  → IReadOnlyList<BoundDerivedAtom>
  empty unless WorldEntityMemberRoles.Fights(member.Role)            (role-aware-placement)
  for each binding on legion:{worldId}/{legion.EntityId}, each stat.derived atom of its container:
     amount = ContentScale.Apply(atom.Amount, ContentScale.Milli(Θ(member), PowerTuningHub.Tuning))
     yield BoundDerivedAtom(atom.Channel, atom.Op, amount,
                            ContributionSourceIds.Legion(legion.EntityId, containerId))
```

`Θ(member)` is the member's level, the same `ThetaActor ?? Level` reading battle uses
(`BattleHubCompose.cs:55`). Scaling happens **here, once** — the container carries the band value, the
reader applies the one ladder, and no content module multiplies anything (`PRINCIPLES.md` §5, "a magnitude
is scaled once"). `general-member-hub`'s `LegionMemberAtoms` calls this reader for every fighting member,
general or unique.

### 4. SourceId

`ContributionSourceIds.Legion(string entityId, string containerId) => $"legion:{entityId}:{containerId}"`;
`FictionLabel` arm: `Legion · {containerId}`. The world id is not in the SourceId: a SourceId names a
contribution inside one resolve, and a resolve is always inside one world.

### 5. When 5c is read

Battles resolve inside `Step`, before the reconcile runs, so a battle reads the bindings as the legion
stood **at the start of the turn**. A standard forged this turn counts from next turn's battles; a carrier
killed in this turn's first battle still counts for the rest of this turn's battles. Stated, tested, and
the same for every contributor.

## Tunables

None of its own. The `P(Θ)` curve is `PowerTuning`'s; band values are `legion-seed.v1.json`'s (proposed; the file does not exist yet)
(`empire-seed`); mechanics thresholds are `legion.v1.json`'s (proposed; the file does not exist yet) (modules 10–13).

## Numeric types

Atom amounts after scaling are `long` through `ContentScale.Apply` (`ContentScale.cs:22-31`, *"the one
funnel every content-scaled magnitude passes through"*), converted to the `double` `BoundDerivedAtom.Amount`
at the end — floating point is allowed for a composed channel value (`PRINCIPLES.md` §5).

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~OwnerScope|FullyQualifiedName~BindGate"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~LegionBuff|FullyQualifiedName~WorldTurn"
python gk-core/scripts/guard-actor-hub.py
python gk-core/scripts/guard-dal.py
```

## Structure

```
gk-core/src/FusionRpg.Core/Effects/Atoms/OwnerScope.cs              MODIFIED  Legion member, name, grammar
gk-core/src/FusionRpg.Core/Effects/Atoms/BindGate.cs                MODIFIED  world-host rule includes Legion
src/FusionRpg.Core/World/Legion/LegionBuffSources.cs        NEW       closed contributor list (empty at landing)
gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs   MODIFIED  Legion(...) + FictionLabel arm
src/FusionRpg.Data/Sqlite/RpgStore.LegionBuffs.cs           NEW       reconcile + reader
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs            MODIFIED  call reconcile post-Step
docs/architecture/decisions.md, effect-atom/definitions.md §6, actor-hub-ssot.md §8.1   (required rows)
gk-core/scripts/enforcement-registry.v1.json                         MODIFIED  one rule row
```

## Testing strategy

- **Grammar.** `legion:w/e` parses; missing half, extra `/`, `:` or whitespace each reject `BadOwnerKey`;
  `Name(Legion) == "legion"`; the enum ordinal of every existing member is unchanged.
- **Bind gate.** `Legion` without a world host → `ScopeUnsupported`; a non-`world-buff` container → refused.
- **Scope.** A binding on `legion:w/a` contributes to `a`'s fighting members only — not to `a`'s bearers,
  not to legion `b`, not to the same entity id in world `w2`.
- **Withdrawal — one test per trigger**, each in both orders where play allows: legion destroyed; legion
  disbanded; legion routed (sources tagged standard/tradition withdrawn by their modules' rules); desired
  set shrinks (roster change, doctrine switch); desired set grows. Re-running reconcile is a no-op.
- **Key-set edges — one test per trigger T1–T5** (audit 2026-09-20): a world created with a legion that
  holds a standard binds it before the first battle; an advanced legion's bindings leave the old world and
  appear in the new one in the same transaction; a legion destroyed in a coarse record has no binding
  after that record; the graph-writer source scan fails when a writer skips the reconcile.
- **Timing.** A battle in the turn a standard is forged does not see it; the next turn's does.
- **Scaling.** Two members of different levels get `ContentScale`-scaled amounts from the same binding;
  no other code multiplies.
- **Provenance.** Every contribution's SourceId is non-empty and `FictionLabel` renders it.
- **Guard.** `guard-actor-hub.py` green.

## Boundaries

- **Always:** bind through reconcile; read through the one reader; scale once, there.
- **Ask first:** letting 5c reach the lawn or the sheet (legions do not deploy to either today).
- **Never:** an empire-scope use of `OwnerKind.Legion`; a second reader or binder for any 5c kind; a
  content module computing a 5c magnitude.

## Success criteria

1. `OwnerKind.Legion` with a world-qualified key, durable, gated on a world host.
2. Reconcile keeps bindings equal to the desired set every commit, idempotently.
3. The reader delivers scaled, attributed contributions to fighting members only.
4. The three register rows and the enforcement row land in the same change.

## Interface exposed to dependents

`LegionBuffSources` (modules 10–13 add their contributor), `LegionBoundAtomsUnlocked` (called by
`general-member-hub`), `ContributionSourceIds.Legion`.

## Hard edges

- **Closed vocabularies widened:** `OwnerKind` 8 → 9; the actor layer list gains 5c.
- **Register rows, required in the same change (not made by this spec session):**
  1. `decisions.md` *Actor layer stack*: add **5c legion** (scope: one legion's fighting members, one world;
     lifetime: live, derived from hashed legion state; carrier: `world-buff.*` bound to `OwnerKind.Legion`;
     SourceId `legion:{entityId}:{containerId}`).
  2. `effect-atom/definitions.md` §6: a `legion` row (`owner_key` `{worldId}/{entityId}`, existence checked
     at bind against the world host); the table also still omits `unique-actor`, noted in its own
     correction box (`definitions.md` §6).
  3. `actor-hub-ssot.md` §8.1: a `Legion` producer row.
- **Enforcement registry:** "a 5c contribution reaches the fold only through `LegionBoundAtomsUnlocked`" —
  guard: a source scan that `ContributionSourceIds.Legion` has exactly one production caller. And (audit
  2026-09-20) "every world-graph write runs the legion reconcile" — guard: the graph-writer source scan
  (§2, trigger table).
- **No golden moves**: bindings are Data-side bookkeeping, and with an empty contributor list the reconcile
  writes nothing. **Round 6 C1:** this module is **wave 2**; it grants no capability flag and no player-facing
  feature of its own (its dependents do), so it adds nothing to wave 2's single `RulesetVersion` bump and
  claims none of its own. It names its wave all the same
  ([landing-order.md](../trade-network/landing-order.md)).

## Dependencies

`member-stack` (members); `role-aware-placement` (`Fights`). External: none to land. Cross-program
**obligations** (audit 2026-09-20): `world-continuity`'s `world-creation`, `advance-carry` and
`coarse-step` each call the reconcile in their graph-writing transaction (triggers T2–T4) once this module
has landed; their specs carry the call.

## Design-gate checklist

```
[x] Subsystems: atom layer (owner scopes, containers, bind gate), stats (ActorHub, layer stack), world.
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: definitions.md §0-§6 (wins over any spec), actor-layer-compose-ideal.md (whole,
    including "Layer 5 is in build"), actor-hub-ssot.md §2, §6, §8. NOT read: atom-catalog-ssot.md,
    effect-atom-map.md (the atom row's other documents), ssot-power-scale.md.
[x] decisions.md checked: Actor layer stack (5c not yet recorded — this module records it).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code: OwnerScope, BindGate, ContainerRow/Validator, effect_binding schema, the
    world-qualified-key finding (template ids, no world column), ContentScale, AtomDerivedSubsystem.
[x] Read the surrounding section of every rule quoted.
[~] No suite run; acceptance tests named.
[x] No §2 invariant contradicted. 5c is legion scope, not a fourth empire axis.
[~] Corrections propagated: the owner-key grammar correction is in map §10; register rows listed, not made.
[x] No population count pinned; OwnerKind membership (9) is a closed vocabulary with a stated reason.
[x] §2.16: reconcile replaces a trigger list with a diff against hashed state; each lifetime edge still
    has its own test, including the key-set edge (a legion appearing or disappearing).
[x] Order-independent: reconcile converges regardless of which event happened first; tested both ways.
[x] Contributes via ActorHub (AtomDerivedSubsystem through BoundAtoms) with SourceId legion:...
[x] No parallel path: one binder, one reader, one scaling funnel.
[x] New rule has a registry row (owed in the same change; named above).
```
