# Capability map — `strain-splice-host`

**Status:** spec phase, 2026-09-18. Map + eight module specs written; **not approved, no build
authorized.** Graduates [strain-splice-host-ideal.md](strain-splice-host-ideal.md) under its six owner
rulings of 2026-09-18 (ruling 6: *"this doc graduates to its own map"*). **Reconciled the same day** to
owner rulings R11–R13 of [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md) — helm to 4 sockets, no
per-actor combination count cap, blocked cells reported by id; see §7 *Rulings applied 2026-09-18*.
**Strengthened the same day** (adversarial pass, session `strengthen-ssh-20260918`) — findings and fixes
in §9.2; one owner question raised in §7.1, **answered by R20** the same day (session
`rulings-r20-r24-20260918`): the `forge-gem` souls leg is a pricing lever, derived by `combo-budget`.

**Program:** `strain-splice-host` · **Parent:** `item` (lane I4 sockets, module 16 `sockets`, module 21
`strain-splice-gen`) · **Specs:** `docs/architecture/strain-splice-host/spec-<module-id>.md` · **Plan
(when approved):** `tasks/strain-splice-host-plan.md` + `tasks/strain-splice-host-todo.md`.

**Sealed, referenced, never amended here (ruling 6):** [item-ideal.md](item-ideal.md),
[item/ssot-sockets.md](item/ssot-sockets.md), [item/spec-sockets.md](item/spec-sockets.md),
[item/spec-strain-splice-gen.md](item/spec-strain-splice-gen.md). Where this program finds one of them
stale or wrong, the finding is recorded in §6 below with a `file:line`, not edited into the sealed doc.

---

## 1. Which loop, and what the program is for

**Spine C — item collection and progression** ([the-loops.md](../guide/the-loops.md) §C: *find, vault,
equip, compare, craft, socket, salvage*). A Strain or Splice is a four-rune word built inside one cheap
item; the base is the plan, the word is the prize. **Combat depth** carries it (a Strain grants a
mechanism). No new loop, no new clock, no fourth stock.

The ideal settled three rules — the host never changes (ruling 1), host pins stay coarse (ruling 2),
every slot keeps its own tuning-row ceiling (ruling 3; the helm's *value* revised to 4 by R11, the
tuning-row *shape* unchanged) — plus the ladder shape (ruling 4) and the
sequence (ruling 5). **This map adds what the ideal's own survey did not find**, each verified against
code this session:

| # | Finding | Evidence | Kind |
|---|---|---|---|
| F1 | **A firing Strain/Splice never reaches the actor.** The projector binds each socketed *insert*; nothing binds the *combination* | `gk-core/src/FusionRpg.Core/Items/EquipProjector.cs:105` (inserts only) vs [spec-sockets.md](item/spec-sockets.md) line 45 (*"every satisfied combination's atoms bind together"*) | wiring gap |
| F2 | **The 76 shipped combinations never load.** Boot seeds only the 25 generated resonances | `gk-core/src/FusionRpg.Server/Program.cs:458`, `gk-core/src/FusionRpg.Server/Program.cs:491`; no reader of `gk-data/packs/fusion/data/seed/items/combinations/` exists in `src/` | wiring gap |
| F3 | **The per-actor cap has zero production callers** | `SocketCombinationCap.Apply` at `gk-core/src/FusionRpg.Core/Items/Sockets/SocketOperations.cs:237`; `git grep SocketCombinationCap.` finds no caller outside the file (only `gk-core/tests/FusionRpg.Core.Items.Tests/Items/CombinationEvaluatorTests.cs:404`, `:429`) | ~~wiring gap~~ **retired by R12** — the cap is deleted, not wired (`combo-bind` §2) |
| F4 | ~~A second host gate and a second multiset matcher exist.~~ **CLOSED by strain-splice-host SSH1.1** — the preview and the evaluator now call one matcher | `gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs` (`HostAdmits`, `Match`), called from `gk-core/src/FusionRpg.Core/Items/Surfaces/CombinationDistance.cs:139,181` and `gk-core/src/FusionRpg.Core/Items/Sockets/CombinationEvaluator.cs:45,42,49` | **SOLID (S/DRY) debt — CLOSED 2026-09-20, `tasks/evidence-fragments/SSH1.1.md`** |
| F4 | ✅ **RESOLVED by SSH1.1 (host-gate).** Was: a second host gate and a second multiset matcher existed, the preview copying the evaluator's arithmetic against its own doc comment. Both were extracted into one shared `gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs` (`HostAdmits` at `:46`, `Match` at `:68`), called by both `CombinationEvaluator` and `CombinationDistance`; neither old duplicate exists any more | `gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs:46` and `:68` | **SOLID (S/DRY) debt — closed** |
| F5 | **The combinations endpoint builds a fake host** — hard-coded `ArmamentPrimary`, empty frame, never a set piece — so every role/frame-pinned recipe previews wrong | `gk-core/src/FusionRpg.Server/ItemSurfaceEndpoints.cs:183` vs the real builder at `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ItemCard.cs:411` | defect |
| F6 | **Reachability reads opened sockets, not capacity**, so a chaff breastplate with 0 opened / 4 max reads *undiscovered* for every Strain — contradicting the top-up economy | `gk-core/src/FusionRpg.Core/Items/Surfaces/CombinationDistance.cs:177`, `gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs:104` (no capacity field) vs [ssot-sockets.md](item/ssot-sockets.md) line 136 | defect |
| F7 | **"Granted tier is unbounded above" meets a five-row atom ladder.** A combination atom resolves by `(family, tier)`; the atom layer materialises tiers 1..5 only | `gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs:139`, `gk-core/src/FusionRpg.Core/Effects/Atoms/Generation/FamilyExpansion.cs:28` | technical contradiction, resolved in `combo-bind` + `tier-ladder` |
| F8 | **The corpus bakes the tier floor and the granted tier.** `minTier` is zipped onto family-sorted picks and `grantedTier` is written per entry, so a ladder step can only move by regenerating — the opposite of ruling 4's *"every specific lives in data, the generator only knows shapes"* | `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py` (the cited lines are gone: SSH7.3, `6efef718a`, removed `minTier`/`grantedTier` from the generator) | technical contradiction, resolved in `tier-ladder` |

## 2. Modules

| # | Module id | Responsibility | Depends on | Ruling / finding |
|---:|---|---|---|---|
| 1 | [`host-gate`](strain-splice-host/spec-host-gate.md) | **One** host predicate and **one** multiset matcher (fold F4), the real host at every read site (F5), capacity-aware reachability (F6), the coarse-pin grammar and the preservation invariant as tests, the craft-path role-ceiling hardening | — | rulings 1, 2, 3; F4, F5, F6 |
| 2 | [`combination-regen`](strain-splice-host/spec-combination-regen.md) | The 25→102 regenerate migration as **this program's exit gate**: retire `socket-word`, re-run the blocked cells once, **report any still-blocked cell by id for the owner to rule (R13 — never withdrawn automatically)**, keep the gating metric gating; after `circuit-topology`, a second re-run offers `head-guard` as a host (R11) and reports host-role diversity | — (5 for the R11 re-run) | ruling 5 step 1; R11, R13 |
| 3 | [`recipe-import`](strain-splice-host/spec-recipe-import.md) | Boot loads the generated Strains/Splices into `socket_combo_recipe` beside the 25 resonances, through the existing grid validator, refusing by name | 2 | F2 |
| 4 | [`combo-bind`](strain-splice-host/spec-combo-bind.md) | A firing combination becomes a `combo.*` container, binds through the one equip projection, contributes to ActorHub under a new SourceId. **Every firing combination binds — no per-actor count cap (R12)**; `SocketCombinationCap` and `SocketTuning.MaxCombosPerActor` are deleted here | 1, 3 | F1, F3, F7; R12 |
| 5 | [`circuit-topology`](strain-splice-host/spec-circuit-topology.md) | The versioned eight-socket revision: `sockets.v2.json` (new), 0–8 ceilings with **`head-guard` 4 (R11)**, four-socket circuits in the one evaluator, every reader switched, `maxCombosPerActor` removed from the revision (R12), base-type `socketMax` re-resolved by a generator verb | 1, 2 | ruling 5 step 2, ruling 3 as revised by R11; R12 |
| 6 | [`combo-budget`](strain-splice-host/spec-combo-budget.md) | **Measure combination power against its price** over the post-migration corpus and the circuit topology; the report proves pricing bounds it and publishes its provenance (R12 — no count to re-measure). **Gates module 7 and 8** | 2, 4, 5 | ruling 5's re-measure clause, as re-read by R12 |
| 7 | [`tier-ladder`](strain-splice-host/spec-tier-ladder.md) | The graduated ladder in `strain-splice.v2.json` (new), read by the one matcher; the corpus stops carrying tier numbers (F8); top rung bounded by the atom ladder (F7) | 1, 4, 6 | ruling 4, ruling 5 step 3 |
| 8 | [`socket-pricing`](strain-splice-host/spec-socket-pricing.md) | Module-14 pricing that makes the chassis a plan **and carries the combination scarcity (R12)**: an `imbue` recipe row per frame emitted deterministically, `bore` confirmed rung-scaled, and any price leg `combo-budget` finds under-priced republished with the tool | 5, 6 | ruling 5 step 3; D23, D24; R12 |

**Build order:**

```text
host-gate ─┬──────────────────────────────► combo-bind ──┐
           │                                   ▲          │
combination-regen ──► recipe-import ───────────┘          ▼
           │                                         combo-budget ──┬──► tier-ladder
           │                                              ▲         └──► socket-pricing
           └──► circuit-topology ──► combination-regen ───┘
                                     (R11 helm-host re-run)
```

`host-gate` → `combination-regen` → `recipe-import` → `combo-bind` → `circuit-topology` →
`combination-regen` (R11 helm-host re-run) → `combo-budget` → `tier-ladder`, `socket-pricing` (the last
two in parallel).

**How this honours ruling 5.** Ruling 5 orders three named steps: regenerate migration → eight-socket
revision → tier ladder + module-14 pricing, with the budget re-measured before any of it binds. Modules
2 → 5 → 7/8 keep that order exactly, and module 6 is the re-measure placed where the ruling puts it
(after migration and revision, before the ladder binds). **R12 changes what is re-measured, not where:**
with no count cap there is no budget number to re-measure, so module 6 measures what a combination buys
against what it costs, and the ladder and pricing still wait for it. **R11 adds one step inside module 2's
exit, not a new module:** once module 5 publishes `head-guard` 4, module 2's generator re-run offers the
helm as a host (the `circuit-topology ──► combination-regen` arrow above) — still before module 6
measures, so the measurement sees the helm-hosted corpus — and only after module 5's ask-first
`resocket --write` has landed, because the generator derives hosts from *tuning* ceilings and would
otherwise author helm words no helm base can hold (§9.2 S9). **The ladder carries its own re-measure:**
module 6 can price only the one rung that exists when it runs, so module 7 re-runs module 6's report
against the ladder it publishes and republishes the provenance (§9.2 S1). The four modules the ruling does not name are
placed by necessity, not preference: `host-gate` is the SOLID remediation that CLAUDE.md requires to be
*"named and sequenced first"* before the ladder extends a forked matcher (F4); `recipe-import` and
`combo-bind` are wiring gaps without which nothing the other modules tune ever reaches a fight.

**Geometry is not a blocker** — the ideal's re-count holds (1,178 rows carry `socketMax`; `>= 4` only
on `armament-primary` 18 and `core-guard` 13, re-counted this session over
`gk-data/packs/fusion/data/seed/items/base-types/**`). Those numbers are readings; no spec pins them (§5). After R11 the
helm joins the host set by derivation, not by a code or schema change: the generator offers as `hostRole`
every role whose ceiling reaches `ingredientCount` (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/schema.py:75`,
computed by `host_roles()` at `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:60`;
`ingredientCount` 4 at `gk-core/data/tuning/sockets.v1.json:67`), and its C# twin is
`SocketGeometry.RolesThatCanHostAStrain` (`gk-core/src/FusionRpg.Core/Items/Sockets/SocketGeometry.cs:101`).

## 3. Seedsmith / generator coverage — per module

`gk-data/packs/fusion/data/seed/items/**` is seedsmith output. Every change below goes through a generator and a regenerate;
**no module hand-edits a generated row.** P1 holds everywhere: the model emits identity (names, flavour,
family picks, closed-enum pins); deterministic code writes every count, index, tier and magnitude, and
`audit_schema` (`gk-forge/tools/seedsmith/seedsmith/pipeline/model.py:53`) refuses a numeric schema field at
`Pipeline` construction.

| Module | Adapter / stage that changes | New or changed seed fields (enums / indexes only) | Owner of magnitudes | Regenerate + check | Pytest |
|---|---|---|---|---|---|
| `host-gate` | **None.** No generator change — it guards the *absence* of a base/slot key in `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/schema.py:65` and `gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs:132` | none (asserts none are added) | `gk-core/data/tuning/sockets.v1.json` (ceilings) | `python -m seedsmith check ..\..\data\seed\items --adapter items --gate` | `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py` (extend) |
| `combination-regen` | `gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py:86` (rename `socket-word` → `combination`), `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/run.py:80` (grantable-family input for the 26 blocked cells), `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/migrate.py:1` bundle, `gk-forge/tools/seedsmith/seedsmith/metrics/linkage.py:169`; a still-blocked-cells report and a host-role diversity reading in the run summary (R11, R13) — the helm reaches the schema by derivation, no schema edit | `combination` kind (already the C# shape, `gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs:132`); `shape` enum `strain`/`splice`; no new numeric field | `gk-core/data/tuning/strain-splice.v1.json`, `gk-core/data/tuning/sockets.v1.json` | `python -m seedsmith items generate --kind combination --shape splice --write --retry-blocked` · `python -m seedsmith items combogen-migrate --dry-run` · `python -m seedsmith check ..\..\data\seed\items --adapter items --metric Registration/IngredientUnsatisfiable` | `test_strain_splice_gen.py`, `test_combogen.py`, `test_linkage.py` |
| `recipe-import` | **None** — reads the corpus module 2 writes | none | same | `python -m seedsmith items validate --deps` (pre-flight only) | none (C# only) |
| `combo-bind` | `grants` needs no change (already a closed family list, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/schema.py:107`); **deletes** `max_combos_per_actor` (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:48`, `:104`) and the run-summary key (`gk-forge/tools/seedsmith/seedsmith/report/cli.py:1262`) under R12 | none | atom family ladder (`gk-data/packs/fusion/data/seed/items/affix-families/**` → `FamilyExpansion`) and `gk-core/data/tuning/strain-splice.v1.json` | none | `test_strain_splice_gen.py` (backstop test at `:245` deleted) |
| `circuit-topology` | `gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/tuning.py:32` + `gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/tuning.py:258` (read the new revision), a `resocket` verb (new, the `gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/reslate.py` precedent), `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:22` (read the new revision; `host_roles` widens by derivation — with `head-guard` 4 it includes the helm, R11), `gk-core/tools/tuning/publish.py` gains `--remove-key` (the tool has `--add-key`/`--rename-key` but no removal; tunables-ssot T4 says extend the tool) | none — `socketMax` is already the one resolved field | `gk-core/data/tuning/sockets.v2.json` (new) + `gk-core/data/tuning/base-types-gen.v1.json` `socketMaxSplit` | `python -m seedsmith.adapters.items.basetypegen.resocket --dry-run` then `--write` (new) · `dotnet run --project gk-forge/tools/ItemSeedValidator` | `test_base_types_gen.py` (extend) |
| `combo-budget` | `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:68` `geometric_combo_ceiling` becomes a circuit-aware **reading** (per-role `floor(ceiling / circuitSize)`), no longer compared to a cap. (`max_combos_per_actor`, its summary key and its backstop test are deleted by **`combo-bind`**, module 4 — one owner, and it must precede module 5's v2 reader switch) | none | next sockets revision (`sockets.v3.json` unless another program published first) `comboPricing` — the power-per-price bound and its provenance (revisions + corpus digest) | `python -m seedsmith items combo-budget --report` (new) | `test_combogen.py` (extend) |
| `tier-ladder` | `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py` (stop zipping `minTierPlan`; done in SSH7.3, `6efef718a`, so the line number is gone), `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py` (stop writing `grantedTier`; done in SSH7.3, `6efef718a`, so the line number is gone), `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:165` (validate the ladder), re-emit from ledger via `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/authored.py:275` — **no model call** | removes `ingredients[].minTier` and `grantedTier`; `ingredients[]` becomes `{family, quantity}` | `data/tuning/strain-splice.v2.json` (new) `recipe.tierLadder` | `python -m seedsmith items combogen-reemit --write` (new; re-emits from the run ledger, no model call) · `--gate` check | `test_strain_splice_gen.py` (extend) |
| `socket-pricing` | `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/opvocab.py:60` (admit `imbue` to deterministic emission only), an `imbue` emitter (new, the `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/forgegem.py` precedent) | `operation: "imbue"` rows — enum values only; cost bands are closed enums | `gk-core/data/tuning/materials.v1.json` (`imbue` row, already priced); a `materials.v2.json` (new) only if `combo-budget`'s report names under-priced cells | `python -m seedsmith items generate --kind recipe --write` via the imbue emitter · `--gate` check · `python -m seedsmith items combo-budget --report` must pass against the published prices | `test_recipes_gen.py` (extend) |

Each spec restates its row with line-level detail in its own **Seedsmith / generator** section.

## 4. Tunables — who owns which number

| Number | File | Module |
|---|---|---|
| Role ceilings (`head-guard` 4 in v2, R11), `structuralCeiling`, rarity windows, `attunedTierBonus`, `ingredientCount` | `gk-core/data/tuning/sockets.v1.json` today; `sockets.v2.json` (new) from module 5 | 5 |
| ~~`maxCombosPerActor`~~ — **retired by R12** | still in `gk-core/data/tuning/sockets.v1.json:25` (history, never edited); **absent from `sockets.v2.json`** (removed by module 5's publish); no reader after module 4 | 4, 5 |
| `comboPricing.maxRatioToRarityRouteMilli` (the power-per-price bound, a bounded ratio) + `comboPricing.measuredAgainst` (provenance: filename revisions of sockets / strain-splice / materials + the accepted-corpus digest) | next sockets revision from module 6; re-published by module 7 after the ladder, and by module 8 after a price publish | 6 (7, 8 re-publish) |
| `baseTier` per shape, `minTierPlan` → `tierLadder` | `gk-core/data/tuning/strain-splice.v1.json` today; `strain-splice.v2.json` (new) from module 7 | 7 |
| `socketMaxSplit` per band | `gk-core/data/tuning/base-types-gen.v1.json` | 5 |
| `bore` / `imbue` / `forge-gem` price legs — **the combination scarcity lever (R12; `forge-gem` by R20)** | `gk-core/data/tuning/materials.v1.json`; the next `materials` revision (new, via `publish.py`) if module 6's report names under-priced cells — the `forge-gem` souls coefficient only at the report's derived value, sequenced against species-gear-chain's `materials` row ([species-gear-chain-map.md](species-gear-chain-map.md) § Tuning revisions) | 8 |

**Revision sequencing (strengthen pass 2026-09-18).** `vN` in these specs means *the next file
`gk-core/tools/tuning/publish.py` writes* — it derives `N` from the highest `<domain>.v{n}.json` on disk
(`gk-core/tools/tuning/publish.py:60`) and refuses to overwrite (`:556`). So two programs can never collide on a
filename, only on **order and on readers**. This program's order: `sockets` v2 (module 5) → next
(module 6, provenance) → next (module 7 re-measure; module 8 if prices move); `strain-splice` v2
(module 7); `materials` next (module 8, only if the report demands it). species-gear-chain also plans
sockets and materials changes (`spec-socket-combat-wiring.md` optional multiplier; `spec-species-cost-shaping.md`)
as **in-place `version` bumps inside the v1 files** — the route that already left `sockets.v1.json` with
internal `"version": 3` (`gk-core/data/tuning/sockets.v1.json:3`). After module 5 publishes v2, an in-place v1
edit lands in history and is never read. Both programs publish with the tool onto the latest file, and
every reader follows one current-revision constant per domain (`circuit-topology` §4). Provenance records
filename revisions, never the internal `"version"` field (§6 C16).

**What replaces the count cap (R12).** Nothing counts combinations. How many one actor wears is bounded
by **geometry** — one per complete four-socket circuit, `Σ floor(ceiling(role) / SocketCircuitSize)` over
the equipped roles, a structural reading from two structural constants — and how many it is *worth*
wearing is bounded by **price**: every circuit on a cheap chassis is bored (and optionally imbued)
socket by socket on rung-linear legs, and filled with four gems whose cost climbs with tier
(`forge-gem` priced on the output tier; the upcycle route consumes `insertTiers.upcycleInputPerOutput`
per step). The formula and the tunable are in [spec-combo-budget.md](strain-splice-host/spec-combo-budget.md) §1, §4. `combo-budget` measures power bought against that price
for every (combination, rung) and **fails** when any cell buys power more cheaply than the rarity route
does; the fix is a price publish (`socket-pricing`), never a count. **Enforcement is never at play time**
(R12/D23 forbid refusing a player on price): it is the report at publish time, the BalanceGuard CI test
over the shipped files on every commit, and a provenance check at boot that refuses any tuning revision
or combination corpus the last passing measurement did not see (`combo-budget` §5).

Structural, `const` with a why-comment, never tunable: `SocketMaxCeiling` (`gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs:41`, 4 → 8 in module 5), `SocketCircuitSize = 4` (new, module 5), `FamilyExpansion.TierCount = 5` (`gk-core/src/FusionRpg.Core/Effects/Atoms/Generation/FamilyExpansion.cs:28`).
Every revision is published with `python gk-core/tools/tuning/publish.py <domain> ...` (`set` / `--add-key`, and
`--remove-key` (new, module 5) for the retired cap),
never hand-edited (tunables-ssot T4).

**Integer widths.** Every number in this program is a count (sockets, circuits, combinations), a small
index (tier, rung, circuit), or a per-mille ratio — none is a magnitude `P(Θ)` grows. `int` is
correct and the range argument is stated in each spec. **Combination magnitudes are never computed
here**: they are the atom family ladder's, which already rides `contentScale` (one power ladder, no
private curve).

## 5. Guardrail rule (applies to every spec)

Tests assert contracts and closed vocabularies — the grid law `12 × |archetypes| + C(12,2)` computed
from `AptitudeCatalog.All`, the four combination shapes, the circuit size, join closure, determinism,
refusal-by-name. **No test pins a population**: not 76, not 102-shipped, not 1,178 base types, not
18 + 13, not 26 blocked. Those are readings, printed by reports.

## 6. Contradictions found, with resolutions

| # | Where | What | Resolution |
|---|---|---|---|
| C1 | ideal line 57 / 122 cite the eight-socket topology row by a bare `decisions.md` line number | the row is not at the line they name; line 132 was a different row. `species-gear-chain-map.md` line 195 and `spec-socket-allowance-by-kind.md` line 245 cite a line too, which is a different row | cite the row by **name** (*"Eight-socket topology (2026-09-10)"*) in every spec here; the stale line numbers in the other programs' docs are theirs to fix. ✅ closed 2026-09-21 (`CV.3`, lane `docs-citations-1`): every `decisions.md:<line>` cite with a line >= 118 now names its row |
| C2 | ideal line 47 / 57 cite `CombinationEvaluator.cs:39` as the `FirstOrDefault` | the identity pick is at `gk-core/src/FusionRpg.Core/Items/Sockets/CombinationEvaluator.cs:80`; line 28 is the `Evaluate` signature | cited correctly here; no semantic change |
| C3 | [spec-sockets.md](item/spec-sockets.md) line 163 — *"match at most one **ordered** four-ingredient Strain/Splice"* | D41 made recipes unordered (spec-sockets.md line 347; `CombinationEvaluator.cs:23`) | **D41 wins** (the later owner ruling, and the shipped code). `circuit-topology` groups by circuit but matches an unordered multiset within it |
| C4 | spec-sockets.md line 165 — suppression order `(host item, circuit index, combination id)` | shipped order is `GrantedTier desc, ComboId` (`SocketOperations.cs:245`) and a host instance id is generated, not content | ~~`combo-bind` specifies one content-derived total order~~ **Moot under R12**: with no actor-wide count there is nothing to suppress and no suppression order to define. The only "at most one" left is structural — one Strain/Splice identity per circuit, picked inside the evaluator (`CombinationEvaluator.cs:80`, made per-circuit by `circuit-topology`) |
| C11 | [spec-sockets.md](item/spec-sockets.md) §4 (line 116) — *"Keep the active-combination limit tunable … lives in `data/tuning/sockets.v{n}.json`"* | R12: no count cap; scarcity is priced | **R12 wins** (the later owner ruling). Sealed doc stays as history; `combo-bind` deletes the cap code, `circuit-topology` removes the key from v2, `combo-budget` measures price instead |
| C12 | `gk-core/data/tuning/sockets.v1.json:26` (`maxCombosPerActorNote`) and the `SocketCombinationCap` doc (`gk-core/src/FusionRpg.Core/Items/Sockets/SocketOperations.cs:218` — **R12/SSH4.1 deleted the class; the line is gone**) — *"shipped so that a later widening … cannot silently reopen the gap"* | R12 retires the backstop the note justifies | v1 is history and never edited; the doc comment went with the class (`combo-bind`, SSH4.1) |
| C13 | [strain-splice-host-ideal.md](strain-splice-host-ideal.md) lines 20, 22, 124 — *"a helm tops out at three sockets … no helm ever hosts a four-rune word"* | R11: `head-guard` 4 at `sockets.v2.json`, so a helm hosts one four-gem word | The ideal's rulings table carries the revision line; the body prose is the pre-R11 record and is read through that line. Every spec here uses 4 |
| C5 | [item-ideal.md](item-ideal.md) line 957 — D21 *"requires a low-rarity … base"* | ruling 2 enumerates the host gate as role/frame/size + non-set; no rarity gate exists in code (`SetExclusivityValidator.cs:32` is the only D21 predicate); D23 makes the chassis *economically* low-rarity (item-ideal.md line 1024) | **Not a gate.** Low rarity is enforced by price (D23) and preserved by ruling 1; a Strain in an `almanac` host still fires. Recorded so no module adds a rarity arm |
| C6 | `SocketModel.cs:139`, `StrainSpliceTuning.cs:45` — granted tier *"unbounded above"* | the atom ladder has five tiers (`FamilyExpansion.cs:28`), so tier 6 has no atom row | the bound is the atom ladder's, a structural fact: load-time validation **throws** if `top rung grant + attunedTierBonus` exceeds it (`tier-ladder`); `combo-bind` refuses by name, never clamps |
| C7 | spec-sockets.md line 45 + [ssot-sockets.md](item/ssot-sockets.md) line 83 say combinations bind; `tasks/item-todo.md` line 5384 marks module 16 built | F1 — the projector binds inserts only | `combo-bind` closes it, inside the one projection |
| C8 | [spec-strain-splice-gen.md](item/spec-strain-splice-gen.md) lines 57–73 — *"maximum `socketMax` anywhere is 2"* | superseded; already recorded at `gk-core/src/FusionRpg.Core/Items/Sockets/SocketGeometry.cs:78` | sealed doc; readings live in the ideal's 2026-09-18 re-count |
| C9 | item-ideal.md line 1020 — *"`base_type.socket_max` remains a hard structural cap (max 4)"* | superseded by the Eight-socket topology row | module 5 applies the row; the sealed doc stays as history |
| C10 | `gk-core/src/FusionRpg.Server/EquippedBoundAtoms.cs:12` doc names `BattleStatComposer` | deleted 2026-09-13 | stale comment outside this program's paths; `combo-bind` must not copy it |

| C14 | `combo-bind`'s first draft minted `combo:{role}:{host}#c{circuit}` | [actor-hub-ssot.md](actor-hub-ssot.md) §8.1 (lines 811–814) already **reserves** `combo:{role}:{hostItemRef}:{comboId}` for this producer, reviewed with species-gear-chain T21 | **The reserved form wins, plus `#c{circuit}`** — the reservation predates the eight-socket topology, and one comboId can fire in two circuits of one host. One suffix amended in §8.1 with the code (`combo-bind` §3) |
| C15 | [spec-socket-combat-wiring.md](species-gear-chain/spec-socket-combat-wiring.md) §5 and `tasks/species-gear-chain-plan.md` decision #6 name *"arm 2 (combination grants)"* as species-gear-chain's follow-on | `combo-bind` builds the same thing — two owners of one seam | **`combo-bind` owns arm 2**: it is specified, sequenced after the matcher fold and the circuit revision, and uses the reserved grammar. species-gear-chain keeps arm 1 (inserts). The species-gear-chain map is another active session's path (`strengthen-sgc-20260918`) — the matching one-line cross-reference there is handed to that session, not written from here |
| C16 | species-gear-chain specs (`spec-socket-combat-wiring.md` Tunables, `spec-gem-tier.md`, `spec-species-cost-shaping.md`) say a sockets/materials revision is *"a `version` bump inside the existing file, **not** a new `sockets.v2.json`"* | contradicts tunables-ssot T4 and the tool (`gk-core/tools/tuning/publish.py:556` writes `v{n+1}`); this program publishes `sockets.v2.json` | **T4 and the tool win.** Sequencing in §4 *Revision sequencing*; the species-gear-chain text is theirs to correct (handed to `strengthen-sgc-20260918`) |

## 7. Rulings applied 2026-09-18

The three owner questions this map raised were answered in
[spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md) (binding, *"do not reopen"*). Applied here:

| Was | Ruling | Answer | Applied in |
|---|---|---|---|
| O1 — `head-guard` 3 or 6 at `sockets.v2.json`? | **R11** | **4.** Every gem word is 4 gems (`ingredientCount` 4, `gk-core/data/tuning/sockets.v1.json:67`), and combogen offers as `hostRole` every role whose ceiling reaches it (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/schema.py:75`, `host_roles()` at `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:60`), so the helm becomes a word host through regeneration with **no code or schema change**. Revises the ideal's ruling 3 value (its shape — a tuning row, no helm branch — stands) | `circuit-topology` §1 (v2 row), `combination-regen` (helm-host re-run, host-role diversity reading), `host-gate` §4 (the ruling-3 contract, now with a derivation test) |
| O2 — the new `maxCombosPerActor` value? | **R12** | **No count cap; price it.** `maxCombosPerActor` is retired. Scarcity comes from circuit geometry and socket/imbue pricing, consistent with the no-hard-ceilings rule | `combo-bind` §2 (cap code **deleted**, not wired), `circuit-topology` §1 (key removed from v2), `combo-budget` (measures power vs price; the report proves pricing bounds it), `socket-pricing` §5 (pricing carries the scarcity) |
| O3 — may a still-blocked grid cell be withdrawn from D20's 102? | **R13** | **No automatic withdrawal.** Still-blocked cells after the re-run are **reported by id**; the owner rules each | `combination-regen` exit gate |
| §7.1 Q1 — may a `forge-gem` republish fix a gem-only cell? | **R20** | **Yes.** The combo-budget report may publish a higher `forge-gem` price for cells whose cheapest route has no bore or imbue leg; one pricing surface covers every route. Extends R12 to gems | `combo-budget` §1, §3, Testing, Open questions (report **derives** the `forge-gem` souls coefficient); `socket-pricing` §5 (the publish includes `operations.forge-gem.souls.coefficient`), Testing, Boundaries; cross-referenced in species-gear-chain [`spec-gem-tier.md`](species-gear-chain/spec-gem-tier.md) Tunables/Boundaries |

### 7.1 OWNER questions (strengthen pass 2026-09-18)

| # | Question | Why no ruling covers it | Default until ruled |
|---|---|---|---|
| ~~Q1~~ **Ruled R20** | When `combo-budget` finds a cell under-priced whose cheapest route has **no bore and no imbue leg** — a chassis at a rung whose socket window already rolls a full circuit (`sunwoven`/`almanac` today, `gk-core/data/tuning/sockets.v1.json:36` – `:37`; every rung from band 3 up in v2) — may `socket-pricing` fix it by republishing the **`forge-gem`** souls leg? | R12 names scarcity from *"circuit geometry and socket/imbue cost"*; for such a cell no socket/imbue coefficient changes its price at all. The gem leg is the only lever, and species-gear-chain's `gem-tier` marks it *"confirm, do not re-author"* | ~~The report stays red for that cell by name~~ **Ruled R20 (2026-09-18): yes** — the report derives the smallest `forge-gem` souls coefficient that passes the cell; `socket-pricing` publishes it as the next `materials` revision with the tool, sequenced per both maps' revision tables. Only a cell no leg can fix stays red by id |

No owner question remains open in this program. Deliberately **not** asked (the ideal already deferred them): exact ladder steps (tuning), the rune
downgrade path, a named-chase per-base exception, the upcycle 2:1 high leg, the effective-grade rule
beyond the ladder's positional floor.

## 8. Reading gate and DESIGN-GATE §5 (this session)

Read this session: AGENTS.md; [DESIGN-GATE.md](../DESIGN-GATE.md) rows *Anything at all*, *Stats*,
*Any tunable number*, *Any numeric magnitude*, *Power*, *The atom / Secondary effect layer*, *Affix /
container authoring*, *Item rarity* and §5; [the-loops.md](../guide/the-loops.md);
[tunables-ssot.md](tunables-ssot.md) §1–§3; [decisions.md](decisions.md) Eight-socket topology and
naming-registry rows; [item/ssot-sockets.md](item/ssot-sockets.md) banner + §2–§5, §8.2, §8.3, §8.7;
[item/spec-sockets.md](item/spec-sockets.md) §3–§5.1; [item/spec-strain-splice-gen.md](item/spec-strain-splice-gen.md)
in full; [item/ssot-rarity.md](item/ssot-rarity.md) §3.6–§3.7, §4.6; [item/spec-affix-legality.md](item/spec-affix-legality.md)
objective + design head; [item-ideal.md](item-ideal.md) D21–D24 and the chaff-inversion watch;
[ideas/crafting-coverage-engine.md](../ideas/crafting-coverage-engine.md) gem-grade section;
[species-gear-chain/spec-socket-allowance-by-kind.md](species-gear-chain/spec-socket-allowance-by-kind.md) Boundaries.
`effect-atom/definitions.md` §1 was **not** re-read in full: the one fact this program needs from it —
the `combo` container kind and its id grammar — was verified in code instead
(`gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs:42`, `gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerValidator.cs:35`).
`power/ssot-power-scale.md` was grepped, not read end to end: no socket or combination row exists in it,
and this program introduces no level-derived number.

```
[x] Subsystems identified: item sockets (I4), combination catalog, equip projection, ActorHub contribution, tuning, seedsmith combogen/basetypegen/recipegen.
[x] Session boundary recorded: tasks/sessions/strain-splice-host-spec-20260918.json (paths = this map, its spec folder, the ideal, the record).
    scripts/session-boundary-check.py was NOT run (docs-only session; paths overlap no active record — read directly).
[~] §1 rows read this session — with the two partial reads stated above.
[x] decisions.md checked: Eight-socket topology row; naming-registry combination row.
[x] Every factual claim cites file:line; counts re-counted this session.
[x] Verified against code, not comments (F1–F8 each checked at the call site, not the doc comment).
[x] Surrounding section read for each quoted rule (§5.1, §4, D21–D24).
[ ] Constraints tested — no suite was run; this is a docs-only session. Every "moves X" claim is phrased as a spec requirement, not a measured result.
[x] No §2 invariant contradicted; SOLID debt F4 named and sequenced first.
[x] No assertion pins a population (§5).
[x] ActorHub: combo-bind CONTRIBUTES via the existing equip atom path with a new ContributionSourceIds id; no private fold.
[x] No parallel path added; two existing forks (F4) are folded.
```

## 9. Self-audit — the debate pass

Each spec was re-read against the code it cites and against the other seven. What changed as a result:

| # | Challenge | Outcome |
|---|---|---|
| A1 | Is `host-gate` scope creep beyond the six rulings? | **No.** F4 is a forked matcher that `tier-ladder` must change; CLAUDE.md forbids extending a SOLID-violating seam until its remediation is sequenced first. Kept first |
| A2 | `combo-bind` closes a clause spec-sockets gives to item module 16 — is this program the right owner? | module 16 is marked built (`tasks/item-todo.md` line 5384) and nobody is building the clause; without it nothing this program tunes reaches a fight. Owned here, recorded as C7, sealed docs untouched |
| A3 | Grants need storage — a new `socket_combo_grant` table? | **Rejected** (a DDL change for data the atom layer already stores). Grants become atoms of per-tier `combo.*` containers built at boot |
| A4 | Suppression order key *"host item"* (spec-sockets line 165) | a host instance id is generated, not content — replaced by role ordinal + circuit index (C4). **Superseded by R12**: no suppression, so no order is needed |
| A5 | Resonance thresholds validated against the structural ceiling | would admit an unmatchable threshold of 5 once the ceiling is 8 — tightened to the circuit size (`circuit-topology` §2) |
| A6 | `tier-ladder` — regenerate the corpus to drop tier fields? | a model run for a shape change is waste and risks changing answers — replaced by a deterministic re-emit from the run ledger |
| A7 | The budget default was first written as *"the report's recommended value"* | that is a heuristic nobody chose wearing a default's clothes — changed to *"3, examined by the report and binding"*. **Superseded by R12**: there is no budget value; the report measures power against price |
| A8 | The ruling-1 test first named `item.rarity_id` | no such column; the shipped column is `item_generation.rarity_ordinal` — fixed |
| A9 | Should D21's *"low-rarity"* become a host-gate arm? | **No** — ruling 2 enumerates the gate; D23 prices it (C5) |
| A10 | Is `head-guard` (O1) a manufactured question? | no — ruling 3's own text defers it to *"re-confirmed then"*; default stated. **Answered by R11**: 4 |

**Gaps stated, not hidden:** `effect-atom/definitions.md` §1 verified through code rather than re-read in
full; `scripts/session-boundary-check.py` not run; no test suite run (docs-only session).

### 9.1 Reconciliation pass — rulings R11–R13 (2026-09-18, session `ssh-rulings-20260918`)

Read this pass: [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md) in full; this map and all eight
specs; the ideal's rulings section. Each claim the rulings rest on was re-checked in code:
`combogen/schema.py:75` (host roles closed to ceilings reaching the ingredient count),
`combogen/tuning.py:60` (`host_roles()` derivation), `gk-core/data/tuning/sockets.v1.json:67` (`ingredientCount` 4),
`gk-core/data/tuning/sockets.v1.json:25` (the cap — it lives in **sockets**, not `strain-splice.v1.json`, whose
`:5` only names it in the ownership note), `SocketOperations.cs:237` (no production caller; **R12/SSH4.1 deleted the class — the line is gone**).

| # | Challenge | Outcome |
|---|---|---|
| B1 | Delete `SocketCombinationCap` or keep it and drop its caller? | **Delete.** It has no production caller to remove (F3), and its one responsibility is a rule R12 retired. Keeping it — or keeping `SocketTuning.MaxCombosPerActor` "as a disabled backstop" — is a second path for a number that no longer exists (S) and an invitation to rewire it (O). `combo-bind` §2 |
| B2 | Is `comboPricing.maxRatioToRarityRouteMilli` a cap wearing a new name? | **No.** It bounds a *ratio* at content/tuning validation time — the report fails, a price is republished — and it never refuses, suppresses or clamps anything a player does. A bounded ratio is exempt from the no-hard-ceilings rule and says so in its note |
| B3 | Where does the pricing bound live — `strain-splice` or `sockets`? | `sockets.v3.json`, the revision `combo-budget` already owned; putting it in `strain-splice` would renumber `tier-ladder`'s `v2` for no gain. The cap it replaces also lived in `sockets` |
| B4 | Does R11 need a schema or generator change? | **No** — verified: `host_roles()` is computed from the ceilings, and the schema's `hostRole` enum is that list. The helm arrives by re-run. Only the run summary gains a host-role diversity reading |
| B5 | Does the helm re-run break ruling 5's order? | No: it is inside `combination-regen`'s exit, after the revision and before the re-measure — the measurement sees the corpus that will ship, which is the point of the ruling |

**New gaps named by this pass:** (1) `gk-core/tools/tuning/publish.py` cannot remove a key (`--add-key` and
`--rename-key` only) — `circuit-topology` extends it; (2) no cross-class material exchange rate exists, so
`combo-budget` prices in the **souls leg** and prints the other legs beside it; (3) the rarity-route
reference reads the per-rung power ceiling through the shipped `RarityPowerCeilings.CeilingFor`
(`gk-core/src/FusionRpg.Core/Items/Power/RarityPowerCeiling.cs:225`, key `power_ceiling` owned by module 9 at
`gk-core/src/FusionRpg.Core/Items/RarityBudgetKeys.cs:36`) — no second rarity curve is written; the gap is only
that nothing yet puts a combination's `PowerVector` and a rung ceiling in one report; (4) three shipped tests pin the
non-binding cap and go away with it (`gk-core/tests/FusionRpg.Core.Items.Tests/Items/SocketGeometryTests.cs:362`,
`gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs:183`,
`gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py:245`), and one pins the two-role host set that R11 widens
(`gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs:178`) — each is rewritten to the contract, never
bumped.

### 9.2 Strengthen pass (2026-09-18, session `strengthen-ssh-20260918`)

Adversarial re-read of the map, all eight specs and the ideal against current code. Read this pass:
[spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md); [DESIGN-GATE.md](../DESIGN-GATE.md) §1 rows
*Anything at all*, *Stats*, *Anything that changes what an actor's numbers ARE*, *Any cap*, *Any tunable
number*, *Any numeric magnitude*, *Anything that changes what happens in a BATTLE*, and §2, §5;
[actor-hub-ssot.md](actor-hub-ssot.md) §8.1; species-gear-chain's `spec-socket-combat-wiring.md` §4–§6 and
Tunables. Every cap identifier was re-grepped across `src/`, `tools/`, `tests/`, `web/`, `scripts/` and
`gk-core/data/tuning/` (`SocketCombinationCap`, `MaxCombosPerActor`, `max_combos_per_actor`, `maxCombosPerActor`):
`web/` and `scripts/` have none; every other hit is listed in `combo-bind` §2 or kept deliberately
(`SOCKETS_OWNED_KEYS`, its C# mirror, the v1 file). Each finding was argued the other way once; only the
survivors are listed.

| # | Sev | Finding | Fix |
|---|---|---|---|
| S1 | HIGH | The ladder gate checked only that *some* `measuredAgainst` existed. Module 6 runs before module 7 and can price rung 1 only, so a four-rung `strain-splice.v2.json` would load against a one-rung measurement — unpriced power through a silent path | Provenance records `strainSpliceVersion` and a combination-corpus digest; one pure `ComboPricingProvenance.Check` at boot refuses any mismatch; module 7 re-runs the report and republishes (`combo-budget` §4–§5, `tier-ladder` §1) |
| S2 | HIGH | "The derived bore/imbue coefficients make every cell pass" is false: a cell whose floor route is a chassis that rolled its circuit pays neither, so no bore/imbue price reaches it | The report names each failing cell's actual lever; a gem-only cell is owner question Q1 (§7.1) and stays red until ruled (`combo-budget` §1, `socket-pricing` §5) |
| S3 | HIGH | `combo-bind` minted a second `combo:` grammar beside the one `actor-hub-ssot` §8.1 reserved | Reserved form + `#c{circuit}` (C14) |
| S4 | HIGH | Two owners of combination binding (species-gear-chain arm 2, `combo-bind`) | `combo-bind` owns it (C15); cross-reference handed to `strengthen-sgc-20260918` |
| S5 | HIGH | The Python cap deletion was assigned to both module 4 and module 6; if it waited for module 6, module 5's v2 reader switch would hit `_require(..., "maxCombosPerActor")` and stop every generator run | Module 4 only (§3 rows, `combo-bind` §2, `combo-budget` Seedsmith), stated as `circuit-topology` §4's precondition |
| S6 | MED | Combination bindings refreshed only on equip and deploy; a word completed, broken or imbued on an equipped host stayed wrong until the next re-equip (DESIGN-GATE §2.16 key-set edge) | Trigger table + order-independent tests (`combo-bind` §2.1) |
| S7 | MED | A recipe the grid accepts but whose container cannot build would be seeded, preview as firing, and bind nothing | One acceptance set (`combo-bind` §1, `recipe-import` §2) |
| S8 | MED | Boot failure behaviour was "print and skip" only — a generator defect would ship as a quietly missing word | Skip at boot + a CI test that the shipped corpus has zero refusals (`recipe-import` §2) |
| S9 | MED | The R11 helm re-run was ordered after the v2 *publish*, not after the ask-first *re-stamp*; hosts derive from tuning ceilings (`combogen/run.py:125`), so helm words could be authored for a corpus with no four-socket helm | R11 step waits on `resocket --write`; refuses by name otherwise (`combination-regen`, `circuit-topology` §5 Boundaries) |
| S10 | MED | Host-set/max-socketMax pins under-inventoried: two named, seven exist across C# and Python | Full table and three role-free contracts (`circuit-topology` §5) |
| S11 | MED | `strain-splice.v2` and `materials.v{n}` had no reader switch (`gk-core/src/FusionRpg.Server/Program.cs`, `:324`, `combogen/tuning.py:21`) — a published file nothing loads | `circuit-topology` §4's one-constant rule extended to both domains (`tier-ladder`, `socket-pricing`) |
| S12 | MED | Provenance "versions" were ambiguous; the internal `"version"` field is not monotonic (`sockets.v1.json` carries 3; `publish.py:552` would write 2 into v2); species-gear-chain plans in-place bumps | Filename revision only; *Revision sequencing* in §4; C16 |
| S13 | LOW | The pricing comparison divided twice before comparing; rarity steps that buy nothing and the top rung were undefined; "bounds every route" overclaimed (drops are unpriced) | Cross-multiplied `checked long` comparison; exclusion rules; craft-route symmetry stated (`combo-budget` §1) |
| S14 | LOW | C10 cited `EquippedBoundAtoms.cs:11`; the `BattleStatComposer` reference is on `:12` | Fixed here and in `combo-bind` |
| S15 | LOW | The ideal still stated the retired cap as a live tunable and cited a bare `decisions.md` line number for the eight-socket row | Stale-text annotations only (ideal); ✅ the cite is a row name since 2026-09-21 (`CV.3`) |

Re-verified and **held** (no change): R11's derivation (`combogen/schema.py:75` docstring over the
`host_roles` parameter, which `combogen/run.py:125` fills from `tuning.host_roles()`, `combogen/tuning.py:60`),
so the helm arrives with no code change; ruling 5's order (2 → 5 → 6 → 7/8, R11 inside module 2's exit);
the generated-data rule (`tier-ladder` re-emits from the ledger with no model call, `resocket` and
`combogen-migrate` are deterministic verbs, imbue rows are derived); every other file:line in the specs.
