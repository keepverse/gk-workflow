# Spec: `empire-roster`

**Status: written 2026-09-19 against the approved map. Spec phase; no build authorized.** Every
`file:line` below was opened in this session. Module id `empire-roster`, row 2 of the
[counterparties map](../counterparties-map.md) (wave 1). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §7.4 (*"a world has many empires … seeded as
`Rival`-kind factions with policy ids for personality"*), principle 10. Owner decision **Q2**
(2026-09-19, recorded in the map). **Reconciled with round-4 Q5 (2026-09-19,
[../decisions-round-4.md](../decisions-round-4.md)):** *"Both shipped templates get a clan (plus the rival
already decided for `two-hearths` v2)."* Session record: `tasks/sessions/trade-network-idea-20260919.json`.

## Objective

A world holds **many enemy empires**: exactly one **dominant enemy empire** (the win condition; kind id
`zomboss` in code, unchanged) plus any number of **rival empires** (kind `Rival`). Each empire carries a
**personality**: a policy id plus one row of weights. Every empire runs the same economy and the same
command path as the player; the engine never learns which is which.

Success looks like: a synthetic world with five rival empires validates, plays, and replays
byte-identically; adding a sixth moves no other faction's AI orders; the shipped `two-hearths` template,
stamped at its new version, carries one rival (and, per `clan-seeding`, one clan) on ground that never blocks
the road between the player and the dominant enemy empire; `first-light` v2 carries a clan and no rival; a
world stamped before this module plays exactly as today.

## Scope and non-goals

**In scope:** validation rules for a multi-empire world; the personality row and its catalog check; the
`two-hearths` template version that adds one rival (Q2); a synthetic fixture recipe that seeds N rivals;
the capability flag.

**Non-goals:** clans (`clan-seeding`); the policies that read personality (`trade-ai` registers them);
diplomacy between empires (`diplomacy-facts`, `diplomatic-stance`); generator placement (the world
generator, filed ask A3). No new faction kind: `Rival` already exists.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `Rival` is a declared faction kind, *"a rival summoner — the mirror, running the same rules"* | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:14-15` |
| `PolicyId` is on the faction row and inside the state hash | `gk-core/src/FusionRpg.Core/World/WorldState.cs:76-77`; `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:29-30` |
| `WorldValidation` rejects an unknown policy id | `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:115-120` |
| The AI fill walks every policy faction in ordinal order, each on its own `DeriveStream` stream, so adding one shifts nobody | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:218-245` |
| The AI's order bound is one per entity plus one | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:251-254` |
| A player faction is required and owns the one homeworld | `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:201-215` |
| A faction with no rootbed anywhere pays no loam upkeep (rule G-C) | `gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs:51-58` |
| Replay rebuilds a world from its template id and seed | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:770` |

### Wiring gap

| Gap | Evidence |
|---|---|
| No template or fixture seeds a `Rival`; both shipped templates seed player, dominant enemy empire and wild | `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:76-84`; `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs:25-31` |
| `FactionPolicies` knows two ids | `gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs:13-18` |

### Real gap

No rule that a world has exactly one dominant enemy empire (validation checks only the player and the
homeworld, `WorldValidation.cs:201-215`); no personality; no template version.

## Design

### 1. Validation (gated by `counterparties.roster`)

On a world whose stamp grants `counterparties.roster`, `WorldValidation` adds one rule:

1. Exactly **one** faction of kind `Zomboss` (the dominant enemy empire).
2. Every `Rival` faction and the dominant enemy empire have a non-null, known `PolicyId`.
3. Every empire (`Rival` and dominant) **that holds any sector at world creation** holds among them at
   least one sector with a `Seat` slot and at least one sector with a `Rootbed` slot. The second clause is
   principle 10 applied at the seed: an empire seeded with ground but without a loam source would be exempt
   from all upkeep under G-C (`LoamUpkeep.cs:51-58`). If it later loses every rootbed, G-C applies to it
   exactly as it applies to the player and to the dominant enemy empire — symmetric, not a special case.
   **An empire seeded with no ground at all is outside the rule** (corrected 2026-09-19 for round-4 Q5):
   `first-light`'s dominant enemy empire holds no sector at creation — its faction row exists
   (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:83`) and its seat `black-gate` is unowned behind a
   heavy guard (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:101-107`). It pays no upkeep because it
   has no territory, which is P2 (territorial income needs territorial upkeep) working, not an exemption;
   without this clause, Q5's clan on `first-light` v2 would force a roster rejection or a redesign of the
   teaching map.
4. Every empire's `PolicyId` has a personality row (§2).

A legacy-stamped world skips the rule, so no existing fixture is forced to grow a dominant empire it
never had.

### 2. Personality

Personality is **a policy id plus one row of weights**, never a per-empire script:

```jsonc
// data/tuning/trade.v{n}.json
"personality": {
  "<policyId>": { "tradeAppetiteMilli": 1000, "warAppetiteMilli": 1000, "treatyWillingnessMilli": 1000 }
}
```

- Keyed by policy id, a closed code-owned vocabulary (`FactionPolicies`), so the key set is a
  declaration, not a population.
- This module owns the rows and the check that every empire's policy has one. `trade-ai` registers the
  personality policy ids and is the only reader of the weights.
- Until `trade-ai` lands, rivals run `frontier-rules`, which gets a neutral row (all 1000). A world never
  runs an empire with a policy that has no row.

### 3. Where many empires first appear (owner decision Q2)

1. **Synthetic worlds first.** `trade-foundation` `synthetic-graph` builds worlds with one dominant enemy
   empire and N rivals (filed ask A4 widened: exactly one dominant, each empire with a seat and a
   rootbed). Every many-empire path is proven there.
2. **One rival on `two-hearths`.** Template version 2 of `two-hearths` adds one `Rival` faction on a
   **spur**: a new home sector with a `Seat`, a `Rootbed`, one element-typed deposit and two `Wildland`
   slots for the start kit (§3a), joined by one
   lane to the contested middle sector. `two-hearths` is a single corridor between the two capitals
   (`WorldTemplateCatalog.TwoHearths.cs:252-270`), so a rival placed on the corridor would, at peace with
   closed borders (`diplomatic-stance`), sever the only road to the win condition. The spur keeps the
   road clear. The rival's climate is an element neither capital's sectors use, so it has something to
   trade (P12).
3. **Clans on both shipped templates (round-4 Q5).** `first-light` v2 gains one clan and no rival;
   `two-hearths` v2 gains one clan beside its rival. The clan content, its placement and its seeded
   Trading Post are `clan-seeding`'s (§4 there); this module owns only that both template versions pass
   roster validation (rule 3 as corrected above) and the shared path rule (acceptance 5).
4. **Scale** comes from the world generator (A3); this module adds no size-tier rule.

### 3a. The seat start kit (round 5 A1)

*"Every empire's seat (player and AI) starts with a tier-1 Counting House and a tier-1 Storehouse;
everything else is built"* ([../decisions-round-4.md](../decisions-round-4.md) R5-A A1). **Placement is
`world-continuity`'s** (`../../world-continuity/spec-world-creation.md` §5a: every empire seat sector the
empire owns at creation, chosen by feature, placed inside `WorldCreation.Rebuild` so creation and replay
agree; a landless empire such as `first-light`'s dominant one gets none). This module adds no second
placement and no second check. What it owes is **template content**: both kit rows stand on `Wildland`
(`../../empire-seed/spec-trade-structure-rows.md` §5.1), and today's seat sectors cannot hold two —
`first-light`'s home has one `Wildland` slot (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:143-149`),
`two-hearths`' home none (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs:43-48`) and its
`Zomboss` seat one (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs:198-203`). So the template
versions this module already cuts (`first-light` v2, `two-hearths` v2, §3) give **every empire seat sector
the empire owns at creation at least two free `Wildland` slots**, the rival's new spur home included — one
re-bless for the roster, clan and kit changes together (world-continuity's recommended resolution).
Synthetic worlds (§3 item 1) seed the same slots.

A template version is part of the per-world stamp (`trade-foundation` `world-stamp`). Replay rebuilds a
world from its template (`RpgStore.WorldTurns.cs:770`), so `WorldTemplateCatalog.Build` must take the
stamped template version and a legacy `two-hearths` world must rebuild the version-1 faction list.
That is filed on `trade-foundation` (ask A4, widened); this module only supplies version 2's content.

### 4. The capability flag

`counterparties.roster` joins `world-stamp`'s closed flag registry in this module's change — in
**`counterparties` wave 1**, whose **one** `RulesetVersion` bump it shares with `counterparties.needs`,
`.diplomacy` and `.treasury` (round 6 C1: one flag never spans waves, one bump per wave; row 15 of
[../landing-order.md](../landing-order.md) §2). New `two-hearths` worlds and synthetic trade worlds carry
it.

## Tunables

`personality.<policyId>.{tradeAppetiteMilli, warAppetiteMilli, treatyWillingnessMilli}` in
`data/tuning/trade.v{n}.json` (added by `publish.py --add-key`). Per-mille, 1000 neutral. A missing row
for a used policy is a world-validation rejection; a missing key inside a row is a load rejection (T5).

## Numeric types

Weights are `int` per-mille ratios (bounded ratios, exempt from the magnitude rules; PRINCIPLES §5). No
magnitude is produced here.

## Acceptance (contract)

1. A roster-stamped world with N ≥ 0 rivals validates for every N the synthetic builder produces; zero or
   two dominant enemy empires is a validation rejection naming the rule.
2. An empire that holds any sector at creation but no seat or no rootbed is a validation rejection; an empire
   seeded with no ground at all (`first-light`'s dominant enemy empire) validates (rule 3 as corrected for
   round-4 Q5 — this acceptance line still stated the uncorrected rule until the 2026-09-20 audit).
3. **Stream independence, asserted for the new kind:** adding a rival to a world leaves every other
   faction's AI commands for the same turn byte-identical (already true of the fill,
   `RpgStore.WorldTurns.cs:245`; asserted here for `Rival`).
4. An unknown personality policy id is a rejection, never a silent default.
5. On `two-hearths` v2 **and `first-light` v2** there is a lane path from the player's homeworld to the
   dominant enemy empire's seat that crosses no rival **or clan** sector (at peace, borders are closed —
   `diplomatic-stance` §3).
6. A legacy-stamped `two-hearths` world rebuilds and replays byte-identically (with A4's version-aware
   build).
7. No test pins the number of rivals, sectors or policies; tests assert validation outcomes and joins.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/RosterValidationTests.cs` (new, beside `WorldInvariantTests.cs`): the four rules, each positive and
  negative; legacy skip.
- `tests/FusionRpg.Core.Tests/World/Synthetic/` (`trade-foundation`'s builder): N-rival worlds validate
  and replay.
- `gk-core/tests/FusionRpg.Data.Tests/`: the commit fill with a rival added leaves other factions' command rows
  identical (the fill is Data-side).
- Template: `two-hearths` v2 path test; v1 byte-identity.

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/WorldValidation.cs','gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs','tests/FusionRpg.Core.Tests/World/RosterValidationTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurn"
```

## Hard edges

- **Template content under replay.** Editing `two-hearths` in place would break every existing world's
  replay (`RpgStore.WorldTurns.cs:770`). Version 2 lands only together with, or after, a version-aware
  `WorldTemplateCatalog.Build` (A4). Order: stamp first, content second.
- **Campaign scenarios** built on `two-hearths` (`TwoHearthsCampaignTests`, `TwoHearthsTenTurnProbeTests`)
  stay on version 1 unless a test opts into version 2; they are run and reported.

## Dependencies

| Consumes | From |
|---|---|
| Per-world stamp, capability flag registry, template version, version-aware template build | `trade-foundation` `world-stamp` (A4) |
| Synthetic N-empire worlds | `trade-foundation` `synthetic-graph` (A4) |

| Exposes | To |
|---|---|
| The dominant-enemy-empire rule (`Roster.Dominant(world)`) | `diplomatic-stance` (the locked war pair), `conquest-consequences` |
| Personality rows and their catalog check | `trade-ai` (`ai-treaty-policy`, `ai-bidding`) |
| `Roster.Empires(world)` (dominant + rivals, ordinal order) | `empire-treasury`, `empire-goods-sinks`, `trade-ai` |

## Contradictions found

1. **`trade-foundation` `synthetic-graph`** describes factions as *"a player, several `Rival` empires,
   clans"* (`trade-foundation-map.md` §2.1) with no dominant enemy empire; this module's rule 1 would
   reject such a world under the roster flag. Filed as a widening of ask A4 (the builder seeds exactly one
   dominant enemy empire), not fixed in their map (fence).

## Open questions

None for the owner. Q2 is decided; the spur placement follows from Q1's closed borders at peace; round-4 Q5
decides which templates gain a clan (both).

## Design-gate checklist

```
[x] Subsystems: world model and validation, templates, AI fill, tunables.
[~] Session boundary: trade-network-idea-20260919; session-boundary-check.py not re-run for this
    docs-only file.
[x] Read this session: as spec-need-vector.md's checklist, plus spec-ai-commander §Who gets which
    policy and the two-hearths template body.
[x] decisions.md: no lock on faction counts; Empire resource registry respected.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: 0 HIGH.
[x] Verified against code: FactionKindCatalog, FactionPolicies, WorldValidation rules 1 and 4, the AI
    fill loop and its bound, LoamUpkeep G-C, both templates' faction and lane lists, replay's Build call.
[x] Surrounding sections read (ideal §7.4, principle 10).
[x] No "moves goldens" claim; campaign scenarios named to run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: A4 widened in the map.
[x] No population pinned; "exactly one dominant enemy empire" is a design rule of the world, not a
    count of content.
[x] No event-refreshed cache.
[x] Stream independence stated and tested; no ordering fixed.
[x] No actor magnitude.
[x] No SOLID-violating path: one kind, one fill, one validation.
[ ] Registry row: none proposed.
```

## Audit 2026-09-20

Fixed here: acceptance 2 still stated the pre-round-4 rule (every empire needs a seat and a rootbed), which
would reject `first-light` v2's landless dominant enemy empire that rule 3 now admits. Checked and clean: exactly
one dominant enemy empire is a design rule of the world, not a content count; stream independence for the AI
fill is asserted for the new kind; personality weights are per-mille multipliers keyed by the closed policy-id
vocabulary, with a missing row a rejection; template content changes only through a stamped template version.
**Verification boundary:** `WorldValidation.cs` and the template files stay on `core-fallback`; the Data fill
test uses its existing Data owner.

