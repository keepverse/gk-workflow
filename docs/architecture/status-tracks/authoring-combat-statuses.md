# Authoring a combat status

**The status roster is a closed vocabulary.** Adding one is a reviewed change, not a content
convenience. This is the whole path: three registration points that must agree, eleven grant-overlay
keys, two count lines that move in the same commit.

The reasoning behind the two tracks is [ideal](../status-tracks-ideal.md); the build order is
[map](../status-tracks-map.md). Locked rules: [status-ssot.md](../status-ssot.md).

## 1. Three registration points that must agree

A new `statusId` lands in three files. Miss one and the parity tests fail; the registry is the
owner, so the failure is loud rather than silent.

| # | Where | What to add |
|---|---|---|
| 1 | `gk-core/src/FusionRpg.Core/Status/StatusCategoryRegistry.cs:6-35` | one `["<id>"] = StatusL2bCategory.<Dot\|Cc\|Contagion>` line in `Map` — the ONLY place the id's category is declared |
| 2 | `gk-core/src/FusionRpg.Core/Status/StatusCatalogBootstrap.cs:15` (`RegisterAll`) | one `Register(catalog, "<id>", …)` line — the helper reads the category from the registry at `StatusCatalogBootstrap.cs:89` and declares no category of its own |
| 3 | `gk-core/data/tuning/status-catalog.v1.json:5` | one entry in `entries` — the row a configured host actually loads |

Why they must agree rather than merely coexist: `StatusCatalogBootstrap.Register` calls
`StatusCategoryRegistry.GetRequiredCategory` (`StatusCatalogBootstrap.cs:89`), so an id that reaches
the bootstrap without a registry category **throws at bootstrap**, not at resist time. The reverse
— an id in the registry and the JSON but not the bootstrap — is the dangerous one: the id resolves
in tests and is absent in play.

### The tests that catch drift

All in `gk-core/tests/FusionRpg.Core.Status.Tests/Status/StatusCatalogParityTests.cs`:

- `StatusCatalogParityTests.Json_entry_ids_equal_Bootstrap_ids` — `StatusCatalogParityTests.cs:15`.
  The element-wise equality of the bootstrap id list and the JSON id list. This is the one that
  fails when point 2 and point 3 disagree; the count is implied by it, so it is never pinned twice.
- `StatusCatalogParityTests.Injected_catalog_matches_Bootstrap_kinds_and_payloads` —
  `StatusCatalogParityTests.cs:32`. Per-id equality of `Kind`, `Stacking`, `Family`,
  `PulseHealsAttacker`, `Categories` and `PayloadKinds`, plus `Categories[0] == registry category`
  (`:52-53`). A row that parses but describes a different status than the bootstrap def fails here.
- `StatusCatalogParityTests.ModifyStat_UnityCc_OverTime_rows_have_nonempty_payloadKinds_except_bond`
  — `StatusCatalogParityTests.cs:58`. `bond` is the only row allowed an empty `payloadKinds`
  array; every `UnityCc` / `OverTime` / `Contagion` / `ModifyStat` / `Buff` / `Debuff` / `Meter` /
  `CrowdControl` row must declare at least one.

The loader is closed, so a misspelled enum name is a load rejection rather than a default:
`StatusKind` (`gk-core/src/FusionRpg.Core/Status/ResistanceEvaluator.cs:6`),
`StatusStacking` (`:18`) and `StatusPayloadKind` (`:25`) are read with
`ActorSurfaceJson.EnumValue` / `ParsePayloadKinds` at
`gk-core/src/FusionRpg.Core/ActorSurface/StatusSurfaceCatalog.cs:46-49`.

## 2. The two count guards

Both are `[Fact]`s that go red on a widen. Neither is a count you can quietly leave behind.

- `SingleDeclarationTests.AllStatusIds_is_the_locked_twenty_four_member_set` —
  `gk-core/tests/FusionRpg.Core.Vocabulary.Tests/Vocabulary/SingleDeclarationTests.cs:254`. It pins
  the id **set** (`:260-268`), not a count: membership is the contract, and a count would still
  pass if one id were swapped for another. A new id turns this red on purpose — that is the review.
- `ResistanceEvaluatorTests.Bootstrap_registers_24_ids` —
  `gk-core/tests/FusionRpg.Core.Status.Tests/Status/ResistanceEvaluatorTests.cs:461`, asserting
  `Assert.Equal(24, catalog.All().Count)` at `:464`. The literal is the id count; bump it.

There is a third, deliberately weaker one: `All_twenty_four_locked_ids_are_registered`
(`ResistanceEvaluatorTests.cs:440`) asserts the locked ids are a **subset** of
`StatusCategoryRegistry.AllStatusIds` and that the bootstrap lists 24 — it does not pin the
registry's total, because `StatusCategoryRegistry.Register` is a real additive seam and
`ExhaustionPolicy` uses it.

Both names above are themselves asserted to exist, in
`gk-core/tests/FusionRpg.Core.Status.Tests/Status/StatusAuthoringContractTests.cs:199` — so a
rename that left this document pointing at nothing fails the suite rather than quietly rotting.

## 3. The overlay keys a grant may carry

Read by `StatusEffectBridge.BuildApplyInput`
(`gk-core/src/FusionRpg.Core/Status/StatusEffectBridge.cs:226`). Keys are matched
case-insensitively by the overlay reader, not by the bridge.

| Key | Default (verified) | Source |
|---|---|---|
| `periodMs` | `1000` | `StatusEffectBridge.cs:237` — flat read defaults to `0` (`:233`), so a non-positive value falls back to `delivery.periodMs` |
| `durationMs` | `5000` | `StatusEffectBridge.cs:244` — same shape: flat `0` (`:240`) then `delivery.durationMs` |
| `amount` | `0` | `StatusEffectBridge.cs:247` — taken **verbatim**; only an absent-or-zero value falls back to `-abs(magnitude)` (`:248-249`) |
| `chance` | `1.0` | `StatusEffectBridge.cs:250` |
| `status_icd_ms` | `0` | `StatusEffectBridge.cs:251` |
| `statusIcdMs` | `0` | `StatusEffectBridge.cs:253` — a second spelling of the SAME gate, read only when the snake form is non-positive (`:252-253`). Not two clocks. |
| `tickBudget` | `1` | `StatusEffectBridge.cs:259` — flat `0` (`:255`) then `delivery.tickBudget` |
| `spread` | absent → no spread | `StatusEffectBridge.cs:267`; sub-keys `chance` (default `0`, `:270`), `statusId` (defaults to the **host status's own id**, `:271`), `maxHops` (`0`, `:272`), `icd_ms` (`0`, `:273`), `target` (`:274-276`) |
| `immunityTags` | `null` | `StatusEffectBridge.cs:279`, parsed at `:318`; a string is accepted as a one-element list (`:333`) |
| `stat` | `null` | `StatusEffectBridge.cs:301`, parsed at `:311`; a block that yields no composing modifier becomes `null` rather than half a payload |

Two consequences worth knowing before you author:

- **`amount` is a sign, not a magnitude.** An explicit `"amount": 12` is a **heal** and is not
  flipped. A DoT is a negative number. Only the `magnitude` alias — which is *not* on the
  allowlist — is coerced to negative.
- **`durationMs` fills both duration slots** (`StatusEffectBridge.cs:287-289`): `DurationMs` and
  `BaseDuration` are the same number.

### An unknown key is refused, loudly

`EffectBag.Grant` calls `EffectOverlayMerge.TryValidateOverlayForDef` for **every** grant,
unconditionally — `gk-core/src/FusionRpg.Core/Effects/EffectBag.cs:280-281` — and throws
`InvalidOperationException` with the offending key named. The allowlist is the closed
`AllowedByAction` map in `gk-core/src/FusionRpg.Core/Effects/EffectProcAndOwner.cs:276-289` for
`ApplyResourceDelta`, and the refusal is raised at
`gk-core/src/FusionRpg.Core/Effects/EffectProcAndOwner.cs:353-359`.

So the keys in the table are the status vocabulary for **one action only**. The two neighbouring
actions have their own, narrower and differently shaped grammars: FA1 `ModifyStat` refuses a `stat`
block (it takes `channel` plus flat `increased` / `more` / `flat` keys), and FA2 `ApplyStatus`
speaks `status`, not `statusId`. A `stat` block on a status whose def does not declare `ModifyStat`
is refused again at apply time with the named reason `status-stat-overlay-without-ModifyStat`
(`StatusEffectBridge.cs:370-375`).

## 4. The same-commit doc rule

A widen is not finished until **both** count lines move in the commit that adds the id:

- `docs/architecture/status-ssot.md:74-76` — "the live id count is whatever the injected catalog
  lists (today 24 including `nerve.*`) … DESIGN-GATE's status row and this spec's §9 move with it."
- `docs/design-gate/combat.md:14` — the *Status effects* row, which currently reads "Count is
  derived from the injected catalog (today 24 including `nerve.*`); a widen is not finished until
  this line moves." Because that file wins over any spec, a stale count there outranks every
  correct one downstream — the atom row above it has gone stale four times for exactly this reason.

Verified 2026-10-02: both lines still say 24.

## 5. Categories are a resist axis, not a behaviour taxonomy

Exactly three values exist: `dot`, `cc`, `contagion` — `gk-core/src/FusionRpg.Core/Status/StatusPolicy.cs:70-75`.
`StatusCategoryRegistry.Register` **throws** on anything else
(`gk-core/src/FusionRpg.Core/Status/StatusCategoryRegistry.cs:49-50`), including `"slow"`.

The category is not descriptive. It is the suffix of the channel the target contests:
`StatusCategoryRegistry.ResistChannel` / `PowerChannel`
(`gk-core/src/FusionRpg.Core/Status/StatusCategoryRegistry.cs:64-68`) answer
`status.resist.<category>` and `status.power.<category>`. And `cc` is not a label — it is the
crowd-control gate, read at apply time as
`def.Categories.Contains(StatusL2bCategory.Cc)` in `gk-core/src/FusionRpg.Core/Status/StatusRuntime.cs:286`.

**So: there is no "slow".** A slow is not a category you may invent; it is a `cc` status that
happens to also carry a `stat` block, and it is resisted by the CC stat, not by a speed one. A
debuff that is neither crowd control nor a contagion should be `dot` and get `status.resist.dot`.
Choosing a category is choosing which resistance stat contests the effect — nothing more.

## 6. The additive seam, for runtime-generated ids

An id that is generated at runtime (per resource, per entity, per seed) has no business in a
closed vocabulary. For those, `StatusCategoryRegistry.Register(id, category)` plus
`catalog.Register(new StatusDef(...))` is the sanctioned path — exactly what
`gk-core/src/FusionRpg.Core/Actions/Cost/ExhaustionPolicy.cs:69-77` does for
`exhaustion.{resourceId}`.

What such an id gets, and what it does not:

- **No** bootstrap row, **no** JSON row, and therefore **no** parity test, **no** count guard and
  **no** doc-count line. None of §1, §2 or §4 applies.
- **No HUD token.** The token resolver reads the injected *surface* catalog, not the runtime one, so
  an unregistered id renders the placeholder `·` with its neutral colour —
  `gk-core/src/FusionRpg.Core/Hud/ActorHudDisplayTokens.cs:13` and `:20-25`. Never id-slice initials.
- It is still a first-class status: the registry owns its resist category, and the runtime applies
  it through the same `StatusApplyInput`.

If the effect is player-facing and needs a glyph, a name and a colour, it is a catalog row, not a
registered-at-runtime id.

## 7. Worked example

A `cc` DoT-adjacent debuff that slows through a stat block. The JSON row, in the shape the closed
loader accepts — note the `categories` value is the resist axis, and the kind/payload vocabularies
are the C# enums verbatim:

```json
{
  "id": "chill",
  "kind": "Debuff",
  "family": "elemental",
  "categories": [ "cc" ],
  "stacking": "Refresh",
  "payloadKinds": [ "ModifyStat" ],
  "displayName": "Chill",
  "reading": "The limbs are slower.",
  "hudToken": "C",
  "color": "#8fd0ff"
}
```

The three registration points for it, in the same commit:

1. `StatusCategoryRegistry.cs:6-35` — `["chill"] = StatusL2bCategory.Cc,`
2. `StatusCatalogBootstrap.cs:15` (`RegisterAll`) —
   `Register(catalog, "chill", StatusKind.Debuff, "elemental", StatusStacking.Refresh, StatusPayloadKind.ModifyStat);`
   (the shipped `nerve.*` triple at `StatusCatalogBootstrap.cs:66-68` is the shape to copy)
3. `status-catalog.v1.json:5` — the entry above

And the grant that applies it, as an `ApplyResourceDelta` overlay:

```json
{
  "statusId": "chill",
  "amount": -6,
  "periodMs": 1000,
  "durationMs": 4000,
  "chance": 0.8,
  "status_icd_ms": 2500,
  "tickBudget": 4,
  "stat": { "fireRate": { "more": -0.2 } }
}
```

Every key in that overlay is on the `ApplyResourceDelta` allowlist
(`gk-core/src/FusionRpg.Core/Effects/EffectProcAndOwner.cs:276-289`); one that is not throws at
grant time, naming itself.

## 8. What a widen costs

Seven files, one commit. The three registration points of §1, the two count guards of §2, and the two
doc count lines of §4. Nothing here is optional; a widen that leaves any of the five code/test files
behind is caught by the suite, and one that leaves either doc line behind is caught only by review.

### The five code/test files

| # | File | What moves |
|---|---|---|
| 1 | `gk-core/src/FusionRpg.Core/Status/StatusCategoryRegistry.cs:6-35` | one `["<id>"] = StatusL2bCategory.<…>` line |
| 2 | `gk-core/src/FusionRpg.Core/Status/StatusCatalogBootstrap.cs:15` (`RegisterAll`) | one `Register(catalog, "<id>", …)` line |
| 3 | `gk-core/data/tuning/status-catalog.v1.json:5` | one `entries` row |
| 4 | `gk-core/tests/FusionRpg.Core.Vocabulary.Tests/Vocabulary/SingleDeclarationTests.cs:254` | the id **set** (`:260-268`), not a count |
| 5 | `gk-core/tests/FusionRpg.Core.Status.Tests/Status/ResistanceEvaluatorTests.cs:461` | the literal `24` at `:464` |

**The two count guards are in two different test projects, and that is deliberate, not accidental.**
Guard 4 is in `FusionRpg.Core.Vocabulary.Tests` and pins the *membership set* — a swap would still
pass under a count. Guard 5 is in `FusionRpg.Core.Status.Tests` and pins the *literal* `24`. Neither
project subsumes the other, so neither test project going green is evidence the other was updated.

### The two doc count lines, in the SAME commit

- `docs/architecture/status-ssot.md:74-76` — *"the live id count is whatever the injected catalog
  lists (today 24 including `nerve.*`)"*.
- `docs/design-gate/combat.md:14` — the *Status effects* row: *"Count is derived from the injected
  catalog (today 24 including `nerve.*`); a widen is not finished until this line moves."*

Both still read 24 as of 2026-10-02. The design-gate line outranks every spec downstream, so a stale
count there is worse than one in `status-ssot.md`.

### What is *not* part of a widen

Widening `StatusKind` or `StatusPayloadKind` is a **separate, larger reviewed change** and is never a
consequence of adding an id. The enums are closed in C#
(`gk-core/src/FusionRpg.Core/Status/ResistanceEvaluator.cs:6` and `:25`), and a new value there is
refused at load rather than defaulted
(`gk-core/src/FusionRpg.Core/ActorSurface/StatusSurfaceCatalog.cs:46-49`). A new status that seems to
need a new payload kind is a design problem to route back through [ideal](../status-tracks-ideal.md),
not a value to append.

### Cost by route

An id in the **closed vocabulary** costs the seven files above. A **runtime-generated** id
(`exhaustion.{resourceId}` and its kind, §6) costs neither count guard, no parity test, and no doc
count line — it is `StatusCategoryRegistry.Register` plus a `catalog.Register`. If a new id seems
expensive for no benefit, that is usually the signal it should be runtime-generated instead.
