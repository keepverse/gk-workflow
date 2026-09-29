# Spec: `hold-allowance`

**Status: written against shipped code 2026-09-15** — every `file:line` below was opened this
session in the worktree. Module id `hold-allowance`, row 3 of the
[world-action-economy map](../world-action-economy-map.md) (wave 1, depends on `act-price-table`).
Ideal: [world-action-economy-ideal.md](../world-action-economy-ideal.md) (Locked constraint §2
hold fan-out; Q2 "Small allowance" resolution; Q5/Q6 "Flat, march-free"). Dependency:
[spec-act-price-table.md](spec-act-price-table.md) (the `holdAllowanceMilli` key + provisional 250
— consumed exactly, never re-minted here).

## Objective

Hold stance budgets 0 today, so under a literal same-pool rule a garrison could never act. The
owner resolved Q2 as "Small allowance" — a holding garrison may spend one dowse-sized act per
turn. This module implements that allowance and the FULL fan-out the ideal's Locked constraint §2
names: the refill number, `ReachMap` semantics for allowance-holding garrisons, the admission
held-gate carve-out, the AI single-order-slot handling (including Recover-to-Hold healers), the
`Hold => 0` comment rewrite, and the ash-waste hold fixture update. Nothing else moves.

Success looks like: a legion that ends the turn in `hold` refills to `holdAllowanceMilli` (250
provisional) instead of 0; it still cannot march (`entity.held` still drops `Move`); it can pay
for exactly one 250-cost priced act through `budget-debit`'s own debit site; `ReachMap` still
answers empty for it; the AI never files two orders for it; upkeep still counts it the same as
any legion.

## Locked anchors

- **The number is consumed, not chosen.** `movement.holdAllowanceMilli`, provisional **250** —
  key name, units (per-mille budget points), and default all come from `spec-act-price-table.md`
  §Design 1 verbatim. This spec never re-spells the key, never re-justifies the integer, never
  ships a second default. The balance pass moves it in `world.v{n}.json` first, exactly as
  dowse-250 was *"a starting value, not a measured one"* — code reads it through
  `WorldTuningHub`, never a `const` (tunables-ssot T1/T3/T6).
- **Extend `MovementRemaining`, never a second pool** (Owner resolution Q1; ideal Fork A). The
  allowance is a refill amount for the existing budget field, not an `ActionsRemaining` field, not
  a count cap, not a level curve (one power ladder — flat spends need no ladder read). Fork B/C
  stay rejected; choosing either needs its own overturn evidence, not implementation latitude.
- **Flat per-act-per-legion, march-free** (Owner resolutions Q5/Q6). No member-count scaling, no
  stance discount beyond the refill itself, no Reveal reservation: marching still spends first and
  acts spend what is left — and a holder never marched, so its whole allowance is act money.
- **Allowance is act money, never march money.** Nothing in this module lets a 250-point refill
  move a legion one lane. Any reading under which the allowance pays for `LaneCost.For` distance
  is a misread of this spec, not an edge in it.
- **T7 separation: this module prices nothing.** Per-verb costs belong to `act-price-table` (the
  table) and `budget-debit` (the debit); this module only sets the holder's refill and keeps every
  consumer of that refill honest. It retunes no frame value (`PointsPerTurn` 1000, scout 500,
  dowse 250 stay exactly where they are).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Hold budgets 0: `BudgetFor(Hold) => 0`, with the "Holding gives it up entirely" comment | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:46-49` |
| Snapshot refill reads the NEW posture: stance orders land in Snapshot, then every legion's budget becomes `BudgetFor(newStance)` | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:405-423` (comment `:405-407`, refill `:420`) |
| `ReachMap.For` returns EMPTY when `budget <= 0` — "a garrison is a garrison" — so holders reach nowhere and cannot divide by zero | `gk-core/src/FusionRpg.Core/World/Ai/ReachMap.cs:29-32` |
| The held gate drops `Move` for hold-stance entities at Reveal with `entity.held`, never silently | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:217-226` |
| The held gate is `Move`-only today: no priced-act kind is matched by it | `TurnEngine.cs:219` (`command.Kind == WorldCommandKinds.Move`) |
| AI files **at most one order per entity**: ordered rules, first match wins, `Defend ?? Abandon ?? Finish ?? Take ?? Sever ?? Recover ?? Explore ?? Expand ?? Hold` | `gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:46-73` |
| `Recover` digs a hurt legion in (`Stance` → `hold`) and, once holding, files `StandFast` ("holding position, still recovering") while wounds remain — consuming the slot every healing turn | `FrontierRulesPolicy.cs:309-328` |
| `Defend`/`Sever`/`Expand`/`Explore` all require `reach.ContainsKey(sectorId)` — an empty reach map yields null and falls through | `FrontierRulesPolicy.cs:103, 287, 356, 388` |
| The ash-waste fixture parks the wild pack in `hold` with `MovementRemaining = 0` | `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:219-227` |
| Upkeep is stance-agnostic: it counts `garrisonMembers` (a headcount sum over `AtSectorId`), takes no stance parameter on either overload | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:61-63` (truth side), `:90-106` (belief side + pure builder) |
| One-move-last-wins: two marches for one legion → the later order wins (Reveal already sorted stable) | `gk-core/src/FusionRpg.Core/World/Movement/MovementPhase.cs:36-41` |
| Routed-drops: recovering entities' orders drop at Reveal (`entity.routed`); claims re-drop routed legions at settle (`entity.routed`) | `TurnEngine.cs:209-215`; `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:58-62` |
| Dowse tunable-cost precedent: `movement.dowseBudgetMilli`, currently 250, read through `WorldTuningHub` | `LaneCost.cs:55`; `gk-core/src/FusionRpg.Core/World/WorldTuning.cs:19`; `gk-core/data/tuning/world.v5.json:83-85` (per `spec-act-price-table.md` §What already exists) |
| Hold-empty is pinned by test: a hold legion's reach asserts `Empty` | `gk-core/tests/FusionRpg.Core.Tests/World/Ai/ReachMapTests.cs:88-90` |
| Held-march-drop is pinned by test: hold then march drops `entity.held`, legion stays put | `gk-core/tests/FusionRpg.Core.Tests/World/StanceTests.cs:115-123` |
| Digging in costs the turn: stance-to-hold refills to 0 at the closing refill | `gk-core/tests/FusionRpg.Core.Tests/World/StanceTests.cs:78-89` |

### Real gap

| Gap | What this module builds |
|---|---|
| `BudgetFor(Hold)` is 0, so a priced garrison act has no budget to spend | §Design 1: refill reads `holdAllowanceMilli` (250 provisional) |
| `ReachMap`'s emptiness is keyed on `budget <= 0` — a 250 allowance would silently light the map for garrisons if the refill changes first | §Design 2: gate emptiness on stance, not on budget |
| The held gate's `Move`-only shape is accidental today, not locked — a later edit could widen it onto priced acts and re-imprison garrisons | §Design 3: lock the gate as `Move`-only with a priced-act carve-out by construction |
| The AI's single-order slot has no allowance rule: a healing holder's `StandFast` and a priced act would collide the day acts become orders | §Design 4: Recover keeps the slot while healing; holder acts flow only through the existing rule ladder |
| `Hold => 0` comment ("gives it up entirely") becomes false the moment the refill changes | §Design 5: rewrite the comment to the allowance shape |
| The ash-waste fixture authors `MovementRemaining = 0` for a holder — false under the new refill | §Design 5: fixture authors the allowance number |

## Design

### 1. The allowance rule — one refill arm, no new field

```csharp
// LaneCost.cs — BudgetFor gains one tuned arm; Hold stops being a literal 0.
Hold => WorldTuningHub.Tuning.Movement.HoldAllowanceMilli,
```

- Reads `movement.holdAllowanceMilli` through the existing `WorldTuningHub` path — the same seam
  the dowse arm already uses (`LaneCost.cs:55`). No `const`, no second file, no parallel loader.
  The key, units, and provisional 250 arrive from `act-price-table` §Design 1; this spec adds no
  tuning row of its own.
- The Snapshot refill (`TurnEngine.cs:413-423`) is UNCHANGED in shape: it already reads
  `BudgetFor(stance)`, so holders refill to the allowance with zero engine edits. A legion that
  ends the turn in `hold` starts next turn with exactly `holdAllowanceMilli` points of act money.
- Arithmetic: `int` per-mille, matching `DowseBudgetMilli` and every sibling key
  (`act-price-table` §Design 4). The debit arithmetic (widen-before-multiply, divide-by-1000-last,
  overflow throws) belongs to `budget-debit`, not here.
- What 250 buys: exactly one 250-cost act (claim), or two 100-cost acts with 50 left over, or five
  50-cost acts — per the provisional price order (load/unload < deposit/withdraw < claim). The
  sentence is illustrative, not a lock: the balance pass moves both sides of it.

### 2. `ReachMap` semantics — allowance-holding garrisons still reach nowhere

The current gate (`ReachMap.cs:31-32`) keys emptiness on `budget <= 0`. The day §Design 1 lands,
that condition is never true for a holder again — and every AI rule that gates on
`reach.ContainsKey` (`FrontierRulesPolicy.cs:103,287,356,388`) would start routing garrisons to
marches the held gate then drops. That is the exact fan-out the ideal's Locked constraint §2
names. The fix:

```csharp
// ReachMap.For — gate on STANCE, not on budget. A holder's allowance is act money;
// asking how many march-turns it is from anywhere is still a category error.
if (string.Equals(entity.Stance, MovementPolicy.Hold, StringComparison.Ordinal))
    return turns;   // empty: "no route", never "far away" (existing contract, :20-24)
var budget = MovementPolicy.BudgetFor(entity.Stance);
if (budget <= 0) return turns;   // retained as the structural backstop (scout/dowse frame)
```

- The empty-dictionary contract (`ReachMap.cs:20-24` — absent means unreachable, never far) is
  unchanged. The hold-empty test (`ReachMapTests.cs:88-90`) stays green BY CONSTRUCTION, not by
  re-bless: it asserts `Empty` for a holder, and a holder still answers empty.
- No caller changes: `Defend`/`Sever`/`Expand`/`Explore` keep reading `reach.ContainsKey` and keep
  yielding null for garrisons — which is what routes holders down the ladder to `Recover`/`Hold`
  instead of filing marches that Reveal would drop.
- Explicitly NOT an option: dividing the Dijkstra costs by the allowance to produce "act-turns".
  March-turns and act money share units (per-mille) but not meaning; mixing them re-mints
  `LaneCost` as a parallel price engine (ideal §Rejected).

### 3. Admission held-gate carve-out — `Move` stays dropped, priced acts stay admitted

The held gate (`TurnEngine.cs:217-226`) drops `Move` for hold-stance entities with `entity.held`.
Under the command-kind seam (Owner resolution Q4), priced acts arrive as `WorldCommandKind`s
admitted at Reveal and spent at settle. The gate rule:

- `Move` for a holder: still dropped, still `entity.held`, still reported — the held-march test
  (`StanceTests.cs:115-123`) stays green unchanged.
- Every other kind for a holder — including each priced act kind `budget-debit`/`claim-pricing`
  wires — is NEVER matched by this gate. The gate's `Kind == Move` condition (`TurnEngine.cs:219`)
  is the carve-out: it stays exactly as narrow as it is, and gains a comment saying so
  ("priced acts for holders pass here; their budget refusal is `entity.spent`-shaped at the debit
  site, never `entity.held`").
- No new refusal string is minted here. A holder whose allowance cannot cover a priced act is
  refused by `budget-debit`'s own named reason at the debit site — the gate must not pre-refuse
  what it cannot price.
- `WorldCommandAdmission.Admit` needs no arm: admission judges well-formedness and entitlement,
  never legality-at-reveal (`WorldCommandAdmission.cs:4-11`). Stance/ownership shape is unchanged.

### 4. AI order-slot handling — one order per entity, including Recover-to-Hold healers

The slot rule (`FrontierRulesPolicy.cs:46-73`) is unchanged: one order per entity per turn, first
match wins. The allowance changes WHAT the ladder yields for holders, never its shape:

- `Defend`/`Sever`/`Expand`/`Explore` yield null for holders (§Design 2 — empty reach), so a
  garrison never files a `Move` the held gate would drop. This also fixes the standing waste the
  ideal names ("wasted `Move`s"): holders stop filing marches entirely by construction.
- `Recover` keeps its exact current behavior (`FrontierRulesPolicy.cs:309-328`): a hurt legion in
  supply files `Stance → hold`; an already-holding legion with `wounded > 0` files `StandFast`
  ("holding position, still recovering"). That `StandFast` CONSUMES the turn's single slot — a
  healing garrison does not also file a priced act in the same turn. Healing and acting are
  sequential across turns, never simultaneous within one.
- Holder acts flow through the existing ladder positions, not a new rule: `Finish` (clear the slot
  in front of you) and `Take` (claim the ground you stand on) already file non-`Move` kinds for a
  stationary entity — under the command-kind seam those are exactly the orders that will carry
  prices. No new AI rule, no reordering of the ladder, no second slot. A holder with nothing to
  do falls to `Hold` (`StandFast`, "nothing worth doing", `:458-459`) as today.
- `Route`/`SurvivesTheRoute`/momentum are untouched: they only run on paths the reach gate
  already refused for holders.

### 5. Comment + fixture updates — the two literals that become false

| Site | Current literal | New text |
|---|---|---|
| `LaneCost.cs:46` (`BudgetFor` doc + `Hold => 0`) | "A turn's march budget for a given posture. Holding gives it up entirely." + `Hold => 0` | `Hold => WorldTuningHub.Tuning.Movement.HoldAllowanceMilli` with doc: "Holding gives up marching entirely and refills to the garrison act allowance (`movement.holdAllowanceMilli`, provisional 250) — act money, never march money. A balance number, never a const, for the same reason the dowse arm says so (`:51-55`)." |
| `WorldTemplateCatalog.cs:221` (`e-wild-pack-1`) | `Stance = "hold", MovementRemaining = 0` | `MovementRemaining` authors the provisional allowance (250) with comment naming `movement.holdAllowanceMilli` as its source. The template authors a literal (it cannot read tuning at build time); the comment is what keeps the next balance pass from missing it. |

## What does NOT change

- **Upkeep stays stance-agnostic.** `LoamUpkeep` counts `garrisonMembers` over `AtSectorId`
  (`LoamUpkeep.cs:61-63`) on both the truth and belief paths (`:90-106`); stance appears in
  neither signature. A holder eats exactly what a marcher eats. Any "holders eat less because
  they move less" proposal is a new spec, not latitude in this one.
- **One-move-last-wins stays.** `MovementPhase.cs:36-41` — two marches, later order wins. The
  allowance touches no march path, so the rule has no new interaction to handle.
- **Routed-drops stay.** `TurnEngine.cs:209-215` (`entity.routed` at Reveal) and
  `ClaimResolver.cs:58-62` (`entity.routed` at settle) are the only routed handling. Hold and
  routed are orthogonal: a routed holder's orders drop for being routed, not for being held —
  and the Reveal order (routed check before held check) is unchanged, so the report reason for a
  routed holder stays `entity.routed`.
- **The Snapshot refill shape stays** (`TurnEngine.cs:405-423`). Postures land, then
  `BudgetFor(stance)` refills. This spec changes what `BudgetFor` returns for one stance, never
  when the refill runs or what it overwrites.
- **`PointsPerTurn` 1000 / scout 500 / dowse 250 stay.** Fixed frame (`act-price-table` Locked
  anchors); moving any of them with this module is a T7 violation, not a drive-by.

## Golden / fixture consequences (named, not assumed)

| Consequence | Fate |
|---|---|
| `ReachMapTests` hold-empty (`ReachMapTests.cs:88-90`) | STAYS GREEN by construction (§Design 2 gates on stance). If it reddens, §Design 2 is wrong, not the test. |
| `StanceTests` held-march-drop (`StanceTests.cs:115-123`) | STAYS GREEN unchanged (§Design 3 keeps `Move` dropped as `entity.held`). |
| `StanceTests` dig-in-refills-0 (`StanceTests.cs:78-89`) | MOVES to the allowance: asserts `HoldAllowanceMilli` (250 provisional) instead of 0. Re-bless with the reason named (this spec), never silently. |
| `MovementTurnTests` wild-pack `MovementRemaining == 0` (`MovementTurnTests.cs:111`) | MOVES to the allowance for the same reason (fixture + refill both change). |
| `FrontierRulesTests` Recover-to-Hold assertions (`FrontierRulesTests.cs:373,384,402,413-417`) | STAY GREEN: Recover behavior is byte-identical; holders still dig in and still report "still recovering". |
| World-map golden set + `RulesetVersion` (live value 12, `TurnEngine.cs:114`) | AS BUILT 2026-09-15: this module (4A.7) landed first and carries 10→11; `budget-debit` (4A.6) rides 11 and bumps 11→12. The bump is earned by a moved golden (`decisions.md` RulesetVersion-history precedent), never pre-claimed. |
| Template goldens snapshotting `e-wild-pack-1` / `ash-waste` | Re-bless naming this spec (fixture `MovementRemaining` 0 → allowance). |

## Tunables

| Number | Owner | Notes |
|---|---|---|
| `holdAllowanceMilli` | `data/tuning/world.v{n}.json` `movement` (ships in `act-price-table`, NOT here) | This module READS it; `int` per-mille, provisional 250. No row is added, moved, or defaulted here. |

## Numeric types

`HoldAllowanceMilli` is `int` per-mille, matching `DowseBudgetMilli` (`WorldTuning.cs:19`) and
every sibling key — a 250-point allowance on a 1000-point turn budget cannot approach `int`
range, and consistency with the sibling key beats a solitary `long` (`act-price-table` §Design 4
applies verbatim). The `long`/checked discipline applies at the debit arithmetic, which
`budget-debit` owns, not here. No literals in code besides the fixture's own authored 250 (with
its source-naming comment, §Design 5): the loader path reads every number from JSON.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Ai.ReachMap"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Stance"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Ai.FrontierRules"
```

## Structure

```
gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs   EXTEND — BudgetFor(Hold) reads HoldAllowanceMilli (§Design 1); doc rewrite (§Design 5)
gk-core/src/FusionRpg.Core/World/Ai/ReachMap.cs         EXTEND — stance-gated emptiness (§Design 2); budget<=0 backstop retained
gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs     COMMENT — held gate carve-out locked as Move-only (§Design 3); refill untouched
gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs FIXTURE — e-wild-pack-1 MovementRemaining 0 → allowance (§Design 5)
tests/.../StanceTests + MovementTurnTests        RE-BLESS — refill-0 assertions → allowance (§Golden consequences)
UNTOUCHED: LoamUpkeep.cs (stance-agnostic), MovementPhase.cs (one-move-last-wins),
           ClaimResolver.cs (routed-drops), WorldCommandAdmission.cs (no new arm),
           FrontierRulesPolicy.cs ladder order (no new rule, no second slot),
           PointsPerTurn / ScoutPointsPerTurn / dowseBudgetMilli values
```

## Code style

```csharp
// Allowance is act money, never march money — a holder reaches nowhere even with 250 to spend.
if (string.Equals(entity.Stance, MovementPolicy.Hold, StringComparison.Ordinal))
    return turns;
```

## Testing strategy

- **Holder refills to the allowance:** stance-to-hold closes the turn with
  `MovementRemaining == HoldAllowanceMilli` (re-blessed `StanceTests` dig-in test).
- **Holder still cannot march:** hold then `Move` drops `entity.held`, legion unmoved (existing
  test, unchanged).
- **Holder reach stays empty:** `ReachMap.For` on a hold-stance legion asserts `Empty` even
  though its refill is now nonzero (existing test, unchanged — the regression this spec exists
  to prevent).
- **Holder priced act admitted, not held-dropped:** a holder's non-`Move` command (claim-shaped)
  passes Reveal without `entity.held`; its budget refusal, if any, arrives from the debit site,
  never from the gate.
- **Healing holder spends its slot healing:** a holding legion with wounds files `StandFast`
  ("still recovering") and no second order in the same `Decide` output (existing Recover tests,
  unchanged).
- **Upkeep ignores stance:** a holder and a marcher with identical garrisons produce identical
  `LoamUpkeep` totals (stance-agnosticism pinned, not assumed).
- **No golden moves beyond the named re-bless set:** the full world-map golden set is
  byte-identical except the fixture/refill-valued rows in §Golden consequences. Any other move
  is this module's defect, not "also a rebalance" (T7).

## Boundaries

- **Always:** read the allowance through `WorldTuningHub` (T5: missing key throws naming it —
  inherited from `act-price-table`'s loader, never re-implemented); `*Milli` per-mille units
  (T6); allowance spends on acts only, never on lanes.
- **Ask first:** moving the provisional 250 for balance reasons outside a declared balance pass
  (T7); pricing or exempting any verb (that is `budget-debit`/`claim-pricing`'s decision);
  reordering the AI ladder or adding a holder-specific rule.
- **Never:** a second pool/field/count cap/level curve (Fork B/C stay rejected — ideal §Rejected);
  widening the held gate onto priced acts; dividing `ReachMap` costs by the allowance;
  `const` allowance in code (T1/T3); stance-conditioned upkeep; touching Status/ActorHub/
  Combat/Injector/FE surfaces.

## Success criteria

1. Holders refill to `holdAllowanceMilli` (250 provisional) at Snapshot. 2. Holders still reach
   nowhere (`ReachMap` empty) and still cannot march (`entity.held`). 3. Holders' priced acts
   pass the held gate and spend through the debit site. 4. AI files exactly one order per holder;
   healing holders file `StandFast`, never act + heal. 5. Upkeep, one-move-last-wins, and
   routed-drops byte-identical. 6. Only the named golden/fixture rows move.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `BudgetFor(Hold) == HoldAllowanceMilli` refill | `budget-debit` (module 2) — the budget a holder's priced act spends from; `claim-pricing` (module 4) — the budget a holder's claim spends from |
| `ReachMap.For` empty-for-holders guarantee (stance-gated) | AI policy + any future route planner — may rely on "holder ⇒ no `reach` keys" without re-checking stance |
| Held gate `Move`-only lock (`entity.held` never names a priced act) | `budget-debit` / `claim-pricing` — may admit holder acts without fearing a gate pre-refusal |
| Single-order-slot preservation (Recover consumes the slot while healing) | future AI act rules — a holder act and a heal never co-file |

## Non-touch list (explicit)

This module does not: add tuning rows or loader arms (`act-price-table` owns the key); implement
debit-after-refill or any debit logic (`budget-debit`); create `WorldCommandKind`s or
payload/admission arms (`claim-pricing` / plan Task 4A.1); change the Snapshot refill shape or
phase order; retune `PointsPerTurn`/scout/dowse; condition upkeep on stance; reorder the AI
ladder or add an AI rule; touch Status/ActorHub/Combat/Injector/FE surfaces.

## Design-gate checklist

```
[x] Subsystems: world-map turn engine + movement budget + AI policy (Core), world tuning. No
    Status/ActorHub/Combat/Injector/FE subsystem touched.
[x] Session boundary: worktree empire-development-20260915-b7e2 only; main checkout untouched.
    (Spec-only session: one new file under docs/architecture/world-action-economy/.)
[ ] Session-boundary record + scripts/session-boundary-check.py — NOT run this session
    (no code edited, no commit attempted; honest gap, one sentence).
[x] Read this session: world-action-economy-map.md row 3; world-action-economy-ideal.md
    (Locked constraint §2, Q2/Q5/Q6 resolutions, §Module breakdown row 4, §Rejected);
    spec-act-price-table.md (full — holdAllowanceMilli key + provisional 250, consumed exactly);
    tunables-ssot.md (T1/T3/T4/T5/T6/T7, §7.2 host discipline, via act-price-table precedent);
    DESIGN-GATE.md §1 Tunable-number row + §2 invariants 11/12/13 + §5 checklist.
[x] Checked decisions.md for a lock: Owner resolutions 2026-09-15 (Q1 extend budget, Q2 small
    allowance, Q3 claim+deposit, Q4 command kind, Q5/Q6 flat march-free) are the governing
    locks; no other "action economy" lock exists — greenfield confirmed by the ideal doc's
    own decisions.md grep.
[x] Every factual claim cites file:line (see §What already exists table).
[x] Verified claims against CODE, not comments: ReachMap.cs (:29-32), TurnEngine.cs
    (:209-226, :405-423), FrontierRulesPolicy.cs (:46-73, :309-328, :458-459),
    LaneCost.cs (:46-57), WorldTemplateCatalog.cs (:219-227), LoamUpkeep.cs
    (:61-63, :90-106), MovementPhase.cs (:36-41), ClaimResolver.cs (:58-62),
    WorldCommandAdmission.cs (:4-11), WorldTuning.cs (:19) all opened in-session in the
    worktree.
[x] Read the surrounding section of every rule quoted (held/routed gates cited with their
    Reveal-section context; upkeep cited with its additive-operand section; ReachMap cited
    with its absent-vs-far contract section).
[x] Tested (not assumed) constraints: no suite run — spec phase, and this module's core
    constraint claims ("named goldens move, all others byte-identical") are stated as
    acceptance tests for implementation, not as measured results.
[x] Nothing contradicts a §2 invariant: SQL untouched (no Data change); no magnitude cap
    (allowance is a tuned refill number with named refusals downstream, not a progression
    ceiling); no f(level); no second pool/composer/path (Fork B/C rejections restated in
    Boundaries, not relitigated).
[x] Corrections propagated: Q2 allowance scope (claim+deposit verbs spend it, build exempt per
    Q3) appears in Objective, Design, and Non-touch list identically; the stance-vs-budget
    ReachMap correction appears in Design, Code style, and Testing identically.
[x] No assertion pins a derived-population count, item total, generated name/description
    text, or per-cycle outcome. (Integers named: 250/100/50 are provisional content
    defaults consumed from act-price-table with a stated balance-pass owner, not guardrails;
    1000/500/0/250 frame values are cited live-code readings.)
[x] No event-refreshed cache introduced. (N/A — no cache, no triggers.)
[x] No acceptance criterion fixes an ordering. (Reveal-before-settle and ladder-first-match
    are cited engine/policy facts, not proposed orderings; criteria assert co-filing never
    happens, which is order-independent.)
[x] No actor combat/derived magnitude produced or consumed — no Hub-adjacent subsystem touched.
[x] No SOLID-violating parallel path: one budget field, one refill, one gate, one ladder —
    reuse throughout; the parallel pool is named in §Rejected-by-reference (ideal §Rejected)
    and restated as a Never in Boundaries.
```
