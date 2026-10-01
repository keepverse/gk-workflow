# Spec: `legion-bands`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `legion-bands` · **Map row:** 14 ·
**Wave:** 4
**Depends on:** `legion-seed-contract`, `band-reader` · **Cross-map (hard):** `legion-build`'s
stack-scoped equipment layer and layer 5c, which are where these numbers enter `ActorHub`
**Model calls:** none
**Status:** spec phase, 2026-09-19; reconciled 2026-09-19 with the round-4 owner decisions
([decisions-round-4.md](../trade-network/decisions-round-4.md) Q12 — the file split — and §B — the Workshop
chain gates the best producible piece tier). No build authorized until this spec is approved and
`legion-seed-contract` has landed.

---

## 1. Objective

Legion seed ordinals resolve to numbers through `band-reader`, and they resolve **once**, identically for
every player. There is no roll seed, no per-player state and no `Instantiator` call. The primary product
is a legion-equipment piece's fixed stats: its `tierBand` selects a reference rarity rung and a power band.
Its atoms are the family's already-generated atoms at that tier, and its total price is held strictly
below a unique item's allowance at the same rung by a tunable share (owner ruling L5,
`docs/architecture/legion-build-ideal.md` §8).

**Done means:**
- `LegionEquipmentCatalog` resolves every committed piece into a fixed atom list.
- A load fails naming the key when a band row is missing.
- A piece whose priced budget reaches the share bound is a load rejection.
- The same inputs give the same pieces in the same order for every player.

## 2. Scope and non-goals

**In scope — every legion *seed magnitude* (owner Q12, 2026-09-19).** `data/tuning/legion-seed.v1.json`
(proposed; does not exist yet) holds:
- the equipment `tierBand` ladder, each rung's reference rarity rung and atom power band, and the weaker
  budget share (`shareMilli`);
- the **tier ladders** the 5c containers scale by: the standard tier multipliers (the `Tier` a
  `forge-standard` names, `legion-build/spec-legion-standards.md` §3, §5), the tradition rank tier
  multipliers (`legion-build/spec-legion-traditions.md` Tunables) and the doctrine combat band
  (`legion-build/spec-legion-doctrine.md` Tunables). **The standard tier ladder has three rungs**
  (owner, 2026-09-20): the Standard Hall's three named building tiers gate one standard tier each, and a
  building tier with no standard tier to unlock would be an empty upgrade
  (`empire-seed/spec-trade-structure-rows.md` §5.1a). The rung *count* is therefore authored; the rung
  *multipliers* still wait on the `ssot-power-scale.md` §10.2 row (criterion 9);
- the legion planner budget block (`spec-world-budgets.md` §5.4).

The C# catalog that resolves pieces, and the budget check, are also in scope.

**Not in scope — mechanics numbers** (`data/tuning/legion.v1.json`, proposed; does not exist yet;
`legion-build` owns it): tradition rank **thresholds**, standard forge quantities, doctrine world-side
terms, cohesion bands, the legion-count cost curve, field-board sizes, equipment recipe quantities and
production batches. Q12's rule: a number indexed by a **seed** ordinal or a tier is a seed magnitude; a
number a resolver or pricer reads about play is a mechanic. No key appears in both files.
- Folding any number into an actor. The resolved pieces are consumed by `legion-build`'s
  `legion-equipment` module through `general-member-hub`, with SourceId `legion-equip:{slot}:{pieceId}`
  (`docs/architecture/legion-build-map.md` §5.14).

## 3. Current state and corrections (verified 2026-09-19)

| Bucket | What | Evidence |
|---|---|---|
| Built | The unique-item allowance per rarity rung, in AE × 100 | `gk-core/src/FusionRpg.Core/Items/Uniques/UniqueBudget.cs:65-66` (`AllowanceAeHundredths`) |
| Built | Pricing a power band at a rung, range-safe (widen, then divide last) | `gk-core/src/FusionRpg.Core/Items/Uniques/UniqueBudget.cs:74-90` (`AeHundredthsOf`, `AeHundredthsOfBand`) |
| Built | The five power bands → atom tiers 1–5 | `gk-core/src/FusionRpg.Core/Items/Uniques/UniqueBudget.cs:35-44` |
| Built | Every atom family already expanded per tier, committed | `data/seed/atoms/generated/family-expand.*.json` (FamilyExpandGen; `gk-core/src/FusionRpg.Core/Effects/Atoms/Generation/FamilyExpansion.cs`) |
| Real gap | The legion seed ladder, the share, the piece resolver | — |

**Corrections to the map (§5.14 and §11 item 6).**

1. **Which numbers this module owns — decided by the owner (Q12, 2026-09-19).** This spec's first draft
   moved the standard and tradition tier ladders to `legion.v1.json`, while `legion-build-map.md` §10 S2 and
   the `legion-standards` / `legion-traditions` specs put them in `legion-seed.v1.json`. Q12 settles it:
   **tiers and the weaker budget share are seed magnitudes** (this file); every other legion number is a
   mechanic (`legion.v1.json`). The draft's narrowing is withdrawn. `doctrine.termMilli` (the signed
   world-side term) stays a mechanic because `legion-build`'s pricers read it, not a 5c container.
2. **`tier` → `tierBand`** (`spec-legion-seed-contract.md` §3, the audit's deny list).
3. **The Workshop chain gates the best producible tier** (round 4 §B: *"The tier is the best
   legion-equipment tier the sector can produce"*). The `tierBand` ladder is aligned to the `workshop` row's
   tiers (`spec-trade-structure-rows.md` §5.1: Workshop → Armory → Foundry): rung *i* (1-based) is
   producible at a Workshop-chain tier ≥ *i*. The ladder may not be longer than the chain, because a rung no
   building can produce is content nobody can obtain; that is a load rejection naming the rung (a closure
   check between two catalogs, not a population pin).

## 4. Principles as they bind this module

- **Seed → concrete → per-player, and this middle layer does not roll** (owner, 2026-09-19: *"fixed
  stats, not generated like unique items"*). Deterministic stats are shared by every player, as species
  stats are.
- **One power ladder.** Tier and magnitude come from the existing atom tiers and the rarity ladder.
  This module writes no `f(level)`. Where a piece should scale with play, that happens inside
  `legion-build`'s reader through `P(Θ)`. It does not happen here.
- **Rarity buys breadth and ceiling, never power.** A legion piece's ceiling is a share of the unique
  allowance at its reference rung. The share is a ratio (`shareMilli` < 1000), which is a bounded ratio
  and exempt from the no-ceiling rule by being a ratio.
- **Range.** Budgets are `long` AE × 100. Arithmetic is `checked`. In integer per-mille math, divide by
  1000 last: `checked(allowance * shareMilli) / 1000`.
- **The balance surface is data.** Every value is published through `gk-core/tools/tuning/publish.py`, and a
  missing key is a load rejection naming it (T5).
- **No model.**

## 5. Design

### 5.1 `data/tuning/legion-seed.v1.json` (proposed; does not exist yet)

```jsonc
{ "schemaVersion": 1, "version": 1,
  "_meta": { "owner": "docs/architecture/empire-seed/spec-legion-bands.md",
             "note": "Legion SEED ordinals only. Mechanics numbers live in legion.v{n}.json (legion-build)." },
  "equipment": {
    "shareMilli": <int, 0 < x < 1000>,
    "tierLadder": ["<rung-1>", "..."],
    "tiers": { "<rung>": { "referenceRarity": "<RarityLadder.RungIds member>",
                           "atomPowerBand": "<trivial|low|medium|high|extreme>",
                           "maxAtoms": <int> } } },          // rung i: producible at Workshop-chain tier >= i
  "standards":  { "tierMultiplierMilli": [ ... ] },          // read by legion-standards
  "traditions": { "rankTierMultiplierMilli": [ ... ] },      // read by legion-traditions
  "doctrine":   { "combatBand": "<atomPowerBand>" },         // read by legion-doctrine's 5c container
  "budget": { ... spec-world-budgets.md §5.4 ... } }
```

`maxAtoms` is a structural count per rung (`item/seed-contract.md` §2.1: *"a count is structure, not
balance"*). It bounds how many families a piece may name.

The **values** are chosen at publish time by principle and never asked of the owner. The ladder's
reference rarities are the lower half of the rarity ladder, because legion pieces are *"a cheap and common
version"* (`legion-build-ideal.md` §6.7). `shareMilli` is set where the priced budget of a `maxAtoms`
piece first sits below the allowance. Rung *names* describe meaning (for example `crude · standard ·
fine`), never a value.

### 5.2 Resolution: once, at load

`LegionEquipmentCatalog.Configure(pieces, tuning, atomCatalog)` is host-injected (T8). For each
`legion-equipment` seed, in `pieceId` order:

1. Look up `tier = tuning.equipment.tiers[tierBand]`. A missing rung throws `SeedBandException`.
2. Require `atomFamilies.Count ≤ tier.maxAtoms`.
3. For each family, take the committed generated atom at `UniqueBudget.TierOfPowerBand(tier.atomPowerBand)`,
   with no roll. A family with no atom at that tier is a load rejection naming both. **Two rules the first
   draft left implicit (audit 2026-09-20):**
   - **Which value, when the atom is a range.** Generated atoms carry a roll range, not a value — for
     example `{"min": 23, "max": 47, "roll": "onApply"}` (`gk-data/packs/fusion/data/seed/atoms/generated/family-expand.g-attack.json`,
     `atom.ferocity` t1). "No roll" needs a stated fixed point: the piece takes the range's **midpoint**,
     `checked(min + max)` then divided by 2 last, rounded half away from zero exactly once (the
     `definitions.md` §2 rounding rule), recorded in `LegionPieceDef`. The midpoint is the band's nominal
     value, so a piece is neither a best nor a worst roll, and the budget check in steps 4–5 prices the
     band, not the point.
   - **Which atom kinds a piece may carry.** `legion-build`'s readers deliver `stat.derived` atoms only
     (`legion-build/spec-legion-owner-scope.md` §3; `legion-build/spec-legion-equipment.md` §2), while a
     generated family may be a `status.apply` proc with a `when` trigger (`family-expand.g-affliction.json`,
     `atom.blighting`). A piece naming a family whose atom at the tier is a kind the readers do not deliver
     would load and then do nothing, so it is a load rejection naming the family and the kind. The
     qualifying families are the `legionAtomFamilies` subset `legion-build` publishes in `vocab.v1.json`
     (`spec-legion-seed-contract.md` §5.3), and the planner draws only from it.
4. Price it: `spent = Σ UniqueBudget.AeHundredthsOfBand(tier.atomPowerBand, rung(referenceRarity))`.
5. Bound it: `spent < checked(UniqueBudget.AllowanceAeHundredths(rung, uniqueTuning) * shareMilli) / 1000`.
   A strict violation throws, naming the piece.
6. Produce `LegionPieceDef(pieceId, slot, tierBand, atoms, elementAffinity, spentAeHundredths)`.

No player id, no world seed and no clock enter this function.

## 6. Commands

```powershell
python gk-core/tools/tuning/publish.py legion-seed --label "legion-bands: v1"   # new domain; extend publish.py only if needed
.\scripts\verify-change.ps1 -Paths <changed C# and tests> -Session <build-session-id>
python gk-core/scripts/audit-overflow.py --targets A3
python gk-core/scripts/audit-magic-numbers.py --summary
```

## 7. Acceptance (contract level)

1. **Same for every player.** Two catalog builds from equal inputs produce equal `LegionPieceDef`
   sequences (deep equality). The function's parameters contain no player, world or seed.
2. **Weaker by design.** For every committed piece, `spentAeHundredths` is strictly below
   `allowance × shareMilli / 1000` at its reference rung, and `0 < shareMilli < 1000` is validated at
   load.
3. **Loud gaps.** A missing `tiers` rung, a missing reference rarity, a family with no atom at the tier,
   or `atomFamilies` above `maxAtoms` each throw, naming the key.
4. **No numbers in seeds.** `spec-legion-seed-contract.md`'s audit still passes, and no legion seed file
   holds a JSON number.
5. **Range.** Every budget is `long`, `checked`. A test drives `long.MaxValue` into the share product and
   expects `OverflowException`.
6. **No unique-item rule applies.** The resolver references no set, socket, affix-pool or roll type (a
   source-scan test over the resolver file).
7. No test pins how many pieces exist.
8. (Audit 2026-09-20) A piece's atom value is the midpoint of its generated range, identical on every load;
   a piece naming a family whose atom kind the legion readers do not deliver is a load rejection.
9. (Audit 2026-09-20) The standard tier and tradition rank multiplier ladders this file holds are not
   published until their `ssot-power-scale.md` §10.2 rows exist (see Hard edges).

## 8. Test plan and verification boundary

`LegionEquipmentCatalogTests` (Core.Tests) covers criteria 1-3, 5 and 6. The legion contract suite
covers criterion 4. Fixture pieces are the committed exemplars (`data/seed/legion/_exemplars/`).

**Verification boundary.** Core C# paths map to `core-fallback` / `core-tests-fallback`
(`gk-core/scripts/verification-boundaries.v1.json:802-811`, `:850-859`). **Gap:** `data/tuning/legion-seed.*`
and `data/seed/legion/**` are unmapped (`gk-core/scripts/verify-change.py:771`). The owner of the fix is
`test-verification-boundary` `python-test-lane`.

## 9. Hard edges

- **A new tuning domain.** `publish.py` may need a first-version path for `legion-seed`. Extend the
  tool, and never hand-write the file (T4).
- **Power-ladder rows owed before two blocks publish (audit 2026-09-20).** `standards.tierMultiplierMilli`
  and `traditions.rankTierMultiplierMilli` are per-tier quality multipliers on a `P(Θ)` magnitude — the
  shape of `ssot-power-scale.md` §10.2 row 7 (affix tier ladder) and row 38 (action rung quality ladder,
  which was given its own row). §10 is closed (*"a power-shaped number not in this table does not have
  permission to exist"*), so each owes a §10.2 row (PS-4: relative, bounded, never multiplied by
  `contentScale` a second time), requested from the power program by `legion-build`
  (`spec-legion-standards.md`, `spec-legion-traditions.md` Hard edges). This module publishes those two
  blocks only after the rows land; the equipment ladder needs no new row (it reuses the rarity ladder and
  the five atom power bands, rows 7–9).
- **The atom tier count is closed at five** (`gk-core/src/FusionRpg.Core/Items/Uniques/UniqueBudget.cs:30-33`),
  so a legion rung cannot reference a sixth tier.

## 10. Dependencies

- Upstream: `legion-seed-contract` (the `tierBand` field and the vocabulary), `band-reader`.
- Cross-map (hard): `legion-build` `legion-equipment` and `general-member-hub` consume
  `LegionPieceDef`; `legion-standards`, `legion-traditions` and `legion-doctrine` read their tier ladders
  here. The split with `legion.v1.json` is the owner's (Q12).
- Cross-map (content): `trade-structure-rows` — the `workshop` row's tiers bound the ladder (§3 item 3).
- Downstream: `legion-seed-rows` (the planner reads the ladder and the budget).

## 11. Open questions

None. The file split was decided by the owner on 2026-09-19 (Q12; §3 item 1).

## 12. DESIGN-GATE §5 checklist

```
[x] Subsystems: a new tuning domain, a Core legion equipment catalog (consumer of band-reader).
[~] Session boundary: spec inside trade-network-idea-20260919; the build session declares its paths.
[x] Read this session: tunables-ssot §2-§3, PRINCIPLES §5, legion-build-ideal §6.7/§8/§9,
    legion-build-map §5.14/§6, UniqueBudget.cs.
[x] decisions.md: "Legion equipment scope (2026-09-19)" row (working tree) is respected: no sets, sockets or rolls.
[x] Every claim cites file:line.
[x] audit-doc-citations: no HIGH finding for this file.
[x] Verified against code: UniqueBudget API and the generated atom files exist.
[x] Read surrounding sections.
[x] Tested: none claimed.
[x] No §2 invariant contradicted (one ladder: no new f(level); overflow: long + checked).
[x] Corrections propagated: the map's §5.14 narrowing and tier→tierBand, recorded in the map.
[x] No population pin.
[x] No cache (load-time); order-independent (sorted by pieceId).
[x] Actor magnitude: produces piece definitions only. Contribution is legion-build's, through ActorHub with
    SourceId legion-equip:{slot}:{pieceId}. No private fold here.
[x] SOLID: reuses UniqueBudget pricing and the generated atoms; no second pricer or curve.
[ ] New rule registry row: none.
```
