# Balance anchors owned by passive-tree-repair — the ideal

**Status:** idea phase, 2026-09-15. Not a spec. No build authorized.

> **Updated 2026-09-18.** **2 owner rulings landed 2026-09-18** (R-PR1–R-PR2): intervals are `Milliseconds`, not a fourteenth `UnitClass`; the status cliff gets **both** a rescale and an m1 floor. Both unblock suppressed rows.

## Which loop this extends

Spine **A. Level up and power** (`docs/guide/the-loops.md`): passive trees are the Vision item on
that loop, and every number in this doc exists to make a tree node price, bind, and pay out. Spine
**C. Item collection and progression** secondarily: the same anchors price affix-family magnitudes,
so the tree and the item corpus stop disagreeing about what a channel is worth. Places: lawn and
battle/sim reads, where the numbers land — no new loop, no loop edit.

## What this is

The passive-tree repair program is refused honest numbers in three places: 20 derived channels have
no reference base for a Flat magnitude, `status.apply` families have no balanced chance/duration
anchor, and two interval channels have no unit class at all. The standing plan says "the power
program publishes them; this program requests and consumes." There is no active power-program
session, so the request has nowhere to go. This doc proposes the reverse: **this program authors
the anchors itself, as versioned tuning data, in the exact shapes the consumers already read.**
Nothing here invents a curve, a system, or a loop. It fills named holes in tables that already
exist.

## Principles, stated inline because they constrain choices below

- **RPG layer, never PvZ.** Anchors are tuning data for the RPG's own stat/effect stack
  (channels, ladders, the expander). No PvZ concept is touched, read, or required. A tree node
  priced by these anchors resolves through `DamagePacket` → dispatcher → shield/combat math →
  Funnel → FA10 like every other RPG number.
- **Gameless-first is capability.** Expansion is deterministic and file-driven; the census, the
  `--check` gates, and the anchor-consumption tests all run with Fusion closed. That is not a
  concession — it is the acceptance shape (CI-provable, per the Standalone-first lock).
- **One ladder, no new `f(level)`.** Nothing here grows with level on its own. Growth comes from
  the three shapes already locked: the tier ladder (`1.75^(t−1)`, five rungs), the duration ladder
  (`1.4^(t−1)`), and `ChannelLadder`'s per-channel `B_ch` share of the one `P(Θ)` ladder. What this
  doc adds are **pins** (values at the reference level 20) and **shares**, never curves.
- **The balance surface is versioned data.** New files (`power-scale.v3.json`,
  `tier-bands.v6.json`, one status anchor addition), never edits to frozen ones (`bands.v1.json`
  stays frozen; `power-scale.v2.json` untouched). A missing anchor stays a load rejection naming
  it (T5) — never a built-in default, never a guessed base.
- **No hard ceilings.** Chance ladders approach but never reach certainty through stacking; duration
  is uncapped; the sigmoid multiplier class is already bounded (1.0×–2.0×) by its math, not by a
  clamp anyone added.

## What already exists

### Built

- **Per-channel growth shares.** `ChannelLadder` (`gk-core/src/FusionRpg.Core/Power/ChannelLadder.cs:24`)
  carries one `B_ch` per channel (`PowerChannelTuning(CMilli, PinValue)`, `:8`); `BattleModels`
  already reads it for `atk`/`defense` (`gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:337-340`).
  Proven by the shipped `BaseAtk(20)=92` / `BaseDefense(20)=22` pins (`gk-core/data/tuning/power-scale.v2.json`).
- **Θ-linear rate bases.** `BaseAccuracy(θ)=220+26θ`, `BaseDodge=26θ`, `BaseCritRate=10θ`,
  `BaseCritResist=10θ+250` (`BattleModels.cs:358-361`) — the §10.1-row-2 verdict ("rates read Θ")
  already shipped as code.
- **The sigmoid consumers.** Rate channels read through `CombatProbability` Sigmoid with divisor
  `100.0` (`gk-core/src/FusionRpg.Core/Stats/Derived/CombatPolicies.cs:10-12`); crit-damage through the
  bounded (1.0×, 2.0×) multiplier (`docs/design/spec-magnitude-and-units.md:82`). The UnitClass
  ledger verifies each class against its consumer (`spec-magnitude-and-units.md:77-91`).
- **The chance carrier.** `when.chance` (per-mille int, default 1000) is read by the compiler
  (`AtomCompiler.cs:219-220`), the runner (`AtomRunner.cs:37`), and priced by
  `CostFunction` (`Power/CostFunction.cs:201`). A status row's chance has a home today.
- **The ratio shapes.** `twoLadderRule` (`gk-data/packs/fusion/data/seed/items/_registry/bands.v1.json`,
  `powerBand.channelFamilyGroups.statusMagnitudeAndDuration`): chance/magnitude ladder at
  1750‰ default, duration at 1400‰ mandatory. Shape locked; only the balanced base is missing.
- **20 named `status.apply` member families** in the same registry node, with an illustrative
  t1 (`freezing`: 25‰ chance, 800 ms — stamped "illustrative, inherited, not balanced").

### Wiring gap

- **E43 never stamps `when.chance`.** `FamilyExpansion.Expand` emits `WhenJson = "{}"` unconditionally
  (`gk-core/src/FusionRpg.Core/Effects/Atoms/Generation/FamilyExpansion.cs:247`). The chance ladder the
  registry names has no emitter — the field exists downstream, the writer just never writes it.
  This is an inert line, not an architectural limit.
- **`FlatReferenceBase` knows 3 channels.** `gk-forge/tools/FamilyExpandGen/Program.cs:138-144` maps
  `maxHp/hp/atk/defense` and returns null for everything else. Adding a channel is a one-line
  map entry reading the new pin file — the delegate shape already anticipates it.

### Real gap

- **Pins for GameUnits channels: `arm1Max`, `arm2Max`, `combat.shield.capacity/pen/toughness.*`,
  and a per-second pin for `combat.shield.regen.*`.** No `BattleRuleset` value, no tuning row,
  anywhere. The ledger classifies them (`GameUnits`, `GameUnitsPerSecond`) but the pin table has
  exactly two rows (`atk`, `defense`).
- **A balanced t1 anchor for `status.apply` chance AND duration, plus per-family shares.**
  The ratios exist (1.75/1.4); the worked example's t1 (25‰ / 800 ms) is explicitly not balanced;
  `sharePermilleOwnership` has no entry for the group (`spec-numerics.md:210-212` defers shares
  "until their families are resolved" — that time is now).
- **The `status.power.*` / `status.resist.*` normalization.** `spec-magnitude-and-units.md:214-233`
  documents it precisely: `delta = totalPower − totalResist` feeds `Sigmoid(delta/scale)` for
  landing and `netFactor = Clamp(delta, 0, 10000)` multiplying magnitude AND duration, with
  `+1 power` doubling everything at default scale. The doc suppresses the context part until this
  is answered. An anchor here is a scale choice (`effectiveApplyScale`) plus an m1 that does not
  start at a 2× cliff — a balance authorship, not a code change.
- **No UnitClass for `attackInterval` / `produceInterval`.** The thirteen-class ledger covers
  every other channel in the 20; intervals appear in no row. Either they are `Milliseconds`
  (durations between events) or they need a fourteenth row with a verified consumer. Today a
  Flat family on either is unpriceable by classification, not just by missing curve.
- **The `channel-policy/defaults.json` stub** (`gk-data/packs/fusion/data/seed/channel-policy/defaults.json`: 2 entries,
  both intervals) stays a stub until the interval classification above lands — it cannot grow
  principled entries for unclassified channels.

## Prior art

- **Path of Exile: flat base durations, threshold-derived chance, capped magnitude.** Ignite lasts
  [4 seconds by default](https://www.poewiki.net/wiki/Ignite) at 90%/s of the hit's flat fire damage;
  chill lasts [2 seconds](https://www.poewiki.net/wiki/Chill) with magnitude from cold damage vs. the
  enemy's ailment threshold (30% minimum, 50% default maximum; 10% flat when applied without damage);
  shock chance is [1% per 4% of ailment threshold dealt](https://poe2db.tw/us/Ailments) as lightning,
  lasting 4s on players / 8s otherwise. The pattern: **duration is a published constant, chance is a
  ratio against a threshold, magnitude is capped** — no per-level curve anywhere in the ailment
  system. Our registry already mirrors this shape (flat duration ladder + chance ratio); what PoE
  publishes per ailment (4s / 2s / 8s bases) is exactly our missing t1 anchor row.
- **World of Warcraft: per-level divisor tables plus DR brackets, not growth curves.** Rating cost
  per 1% is published per level ([46 crit / 44 haste / 54 versatility at level 90](https://www.wowhead.com/guide/how-mastery-works-world-of-warcraft);
  costs rise as level rises — 23 crit rating buys 5.19% at level 20 but 2.66% at level 60,
  [warcraft.wiki](https://warcraft.wiki.gg/wiki/Combat_rating_system)). Above 30% from rating,
  [progressive penalties 10%→100%](https://www.wowhead.com/guide/diminishing-returns-on-secondary-stats-in-world-of-warcraft)
  apply per bracket, hard-capped at 126%. Two lessons: our SigmoidPoints channels already ARE this
  (points vs. the fixed 100.0 divisor + Θ-linear base rates), so they need pins, not curves; and a
  published per-level divisor table is the precedent for our `ChannelLadder` B_ch shares living in
  versioned data rather than code.
- **Failure modes to avoid.** PoE's ailment-threshold design discards sub-threshold applications
  silently (a "0 DPS ignite is discarded") — our T5 refusal-by-name is the deliberate opposite, and
  must survive this work. WoW's pre-Shadowlands linear ratings stacked without bound until borrowed
  power forced DR brackets mid-expansion — our sigmoid classes are bounded by construction
  (1.0×–2.0× multiplier; sigmoid asymptote), so no retrofitted bracket should ever be needed; if a
  channel needs one later, that is a new §10 row, not a silent clamp.

## The shape

Three versioned additions, owned by this program, each in the shape its consumer already reads:

1. **`gk-core/data/tuning/power-scale.v3.json` — pins, not curves.** One `(channel → CMilli/PinValue)` row
   per GameUnits channel (`arm1Max`, `arm2Max`, `combat.shield.capacity/pen/toughness.*`) plus a
   per-second pin for `combat.shield.regen.*`, at reference level 20, in the exact
   `PowerChannelTuning` shape `ChannelLadder` already consumes. `gk-core/data/tuning/power-scale.v2.json`
untouched. Rejected
   alternative: per-channel level curves — §10 forbids a second curve, and `B_ch` already grows
   every channel as a share of the one ladder.
2. **A `status.apply` anchor addition — balanced t1 + shares.** Chance t1 and duration t1 per the
   20 member families (or per-family overrides where the family justifies one), the 1.75/1.40
   ratios intact, plus the `sharePermilleOwnership` entry `spec-numerics.md` deferred. Lives as a
   reviewed addition beside frozen `bands.v1.json`, never an edit to it. Following PoE's shape:
   duration base is a flat constant per family; chance base is quoted against the
   power-vs-resist delta the resolver already computes.
3. **`status.power/resist` normalization + interval classification.** A chosen
   `effectiveApplyScale` and an m1 without the 2× cliff (unsuppressing §4.3's context part), and a
   ledger ruling placing `attackInterval`/`produceInterval` (Milliseconds or a new row with a
   verified consumer). Both are authorship decisions recorded in their SSOTs, not code.

Explicitly not in this shape: rate channels (`accuracy/dodge/crit.rate/crit.resist`,
`crit.damage/resist.damage`) get **no** v3 rows — their bases are Θ-linear and their growth is
the fixed sigmoid. If E43's Flat path needs a `referenceBase` for a SigmoidPoints channel, that
reference is the divisor (100.0 in point units), proposed here and confirmed at spec time —
not a curve, not a pin.

## Tunables

| Number | File (new version, never an edit) | Unit | Owner of the value |
|---|---|---|---|
| Per-channel `CMilli`/`PinValue` (GameUnits + regen/s) | `gk-core/data/tuning/power-scale.v3.json` | game units at Θ=20 reference | this program's balance authorship, reviewed |
| `status.apply` chance t1 / duration t1 (+ per-family overrides) | status anchor addition (new file) | ‰ chance / ms duration | same |
| `statusMagnitudeAndDuration` shares | same addition (`sharePermilleOwnership`) | ‰ | same |
| `effectiveApplyScale`, status m1 | same addition | scale divisor / points | same |
| Interval classification | ledger row or Milliseconds ruling in `spec-magnitude-and-units.md` | — | same |

All read at load; a missing row refuses naming the channel (T5). No `const` carries any of them (T1).

## What this deliberately does not decide

- The actual pin values (that is the balance authorship `/spec` + review produces, not this doc).
- Whether `status.power`'s cliff fix is a scale change, an m1 floor, or both (options named, choice at spec).
- Anything about Phase 11 (ActorHub primary producer) — still gated on the solid-run merge.
- Anything about L0 modules 11/12 (effect-pipeline program) — untouched by this shape.

## Owner rulings — 2026-09-18

### R-PR1 — `attackInterval` / `produceInterval` are **Milliseconds**, not a fourteenth UnitClass

**Ruled: reuse the existing class.** They are durations, and `Milliseconds` already means duration. A
fourteenth `UnitClass` for the same physical quantity is the *"inventing a third vocabulary"* shape this
repo refuses elsewhere, and `UnitClass` is a closed vocabulary — adding a member is a reviewed change
with real blast radius, which a unit conversion does not justify.

**Corroborated by the game's own data, captured 2026-09-17.** `PlantData.attackInterval` reads **1.5**
for Peashooter and GatlingPea (`type_base_stats`, 911 rows) — seconds on the wire. So the work is a
**conversion at the boundary**, not a new class: seconds in, milliseconds in the ladder.

**The objection that was weighed and rejected, recorded so it is not re-raised as new:** intervals are
*inverse* — lower is better, and they scale against power the other way from every other duration. That
is real, and it is a **pricing** concern, not a **unit** one. If inverse scaling genuinely breaks the
pricing math, that is an argument for how intervals are *priced*, never for what they *are*. Splitting
the class to encode a pricing rule would put balance logic in a vocabulary.

**This unblocks the v3 rows** for both channels.

### R-PR2 — status cliff: rescale **and** an m1 floor, because they fix different halves

**Ruled: both.** Not belt-and-braces — the two failures are distinct and each remedy leaves the other
standing:

| Remedy | Fixes |
|---|---|
| **Rescale** | The **shape**. The cliff stops existing, so values above the low end are correct rather than merely non-zero |
| **m1 floor** | The **bottom**. The smallest tier is guaranteed to do *something*, which is what stops a t1 node reading as broken to a player |

Rescale alone leaves a legitimate-but-invisible low end. A floor alone papers over a curve that is still
wrong everywhere above the floor. **This unblocks unsuppressing §4.3.**

**The floor needs its exemption stated when written.** An `m1` minimum is a bounded-magnitude ceiling's
mirror, and `CLAUDE.md`'s caps rule requires structural limits and bounded ratios to *say so in a
comment* — otherwise a later sweep correctly flags it as a progression floor nobody justified.

---

<details><summary>Original open questions, for the trail</summary>

## Open questions

1. **Interval classification** (owner or ledger-owning reviewer): are `attackInterval`/
   `produceInterval` Milliseconds, or a fourteenth UnitClass? Blocks their v3 rows.
2. **Status cliff remedy shape**: rescale, m1 floor, or both? Blocks unsuppressing §4.3.
3. **Sigmoid reference for E43**: confirm divisor-as-reference (100.0 in points) for pricing Flat
   families on SigmoidPoints channels. Blocks wiring the `when.chance` emitter for rate channels.

## Handoff

Written: `docs/architecture/passive-tree-repair-ideal.md` (this file). Next: `/spec` for the
anchor-publication module specs (v3 pins, status anchor, ledger ruling) once questions 1–3 are
answered. No code authorized by this doc.

</details>
