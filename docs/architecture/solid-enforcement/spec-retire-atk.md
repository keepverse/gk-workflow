# Spec: `retire-atk`

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 1** · depends on:
`guard-runner`.

## Objective

Remove the `progression.bonus.atk` channel. The owner ruled it on 2026-09-18: *"my design don't have
atk, it only have power and defense, seem like atk is adundant need to retire."*

In SOLID terms this is a single-responsibility defect. Two channels answer "how hard does this actor
hit". `combat.power.*` is the one the game reads, and `progression.bonus.atk` is a parallel term that
Might and Ferocity also pay into. `guard-class-system`'s G3 has reported exactly this double payment
since 2026-08-27.

### What the channel does today, measured (so the change is judged against facts)

| Surface | What happens to `progression.bonus.atk` | Effect of retiring it |
|---|---|---|
| Lawn | composed into `AppliedCombat.Atk` (`ActorHub.cs:92`), but the Unity write is commented out (`EntityStatWriter.cs:120`, `:199`) | **none**; the telemetry fields `bonusAtk` / `bonusAtkContribs` go away |
| Battle / delve / siege | composed into the snapshot by `BattleHubCompose`; **nothing under `Battle/` reads it** | **none** |
| Standalone sim | `SimEngine.cs:247,313` applies `final.Atk` | the sim stops paying a bonus live battle never paid. **This is a parity fix** (the L in SOLID) |
| Passive tree | 16 seed nodes name it as their *only* effect; all 16 are already **unbound** in `gk-data/packs/fusion/data/generated/passive-tree/` (refused for an unrelated pool-reference reason) | **none** on the bound tree |
| Species magnitudes | 11 generated creatures carry an `atk` magnitude, baked from `aptitudes.v2.json` | the key disappears on regeneration |

**No lawn or battle behaviour changes.** The one player-visible consequence is in the gameless sim,
and there it brings the sim into line with battle.

### Closes a standing decision

`tasks/class-system-plan.md` decision 12 (2026-08-27) made G3 permanently red *"until
`battle-adoption` ships **or the design changes**"*, and
`ClassSystemGuardTests.ClassSystemGuard_script_exitsOneOnTheRealTree_onlyG3_permanentlyByDesign` pins
that red. The owner's ruling is the design change. This module closes decision 12 and turns G3 green,
after which `class-system` can gate like any other guard.

## Design

### R1 — "retired" is a first-class registry state, not a deletion

Deleting the channel outright crashes things. `AptitudeResolver.cs:39` throws on any edge whose
channel is unregistered, and tuning history is immutable, so `aptitudes.v1`–`v8` will contain the
Might/Ferocity → atk edges forever. `gk-forge/tools/CreatureSpeciesGen/Program.cs:70` still bakes species
from **`aptitudes.v2.json`**. Unregister the channel naively and every load of an old version
throws.

So retirement gets one owner:

```csharp
// DerivedStatChannels.cs
/// <summary>Channels the design has RETIRED. Owner ruling 2026-09-18 retired progression.bonus.atk
/// ("my design don't have atk, it only have power and defense"). A retired id is not registered, is
/// never composed, and is DROPPED — with a count — wherever historical tuning names it, because
/// published tuning versions are immutable and must stay loadable. Closed vocabulary: adding an id is
/// a reviewed change. An id that is neither registered nor retired still throws.</summary>
public static readonly IReadOnlySet<string> Retired = new HashSet<string>(StringComparer.Ordinal)
{
    "progression.bonus.atk",
};
```

The distinction the resolver's throw exists to catch is preserved exactly. A **typo or an unknown
channel still throws.** Only a channel the design deliberately retired is dropped.

### R2 — the loader drops retired edges, once, for every caller

`AptitudeTuning.Parse` (`gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeTuning.cs:200-214`), inside the existing edge loop and before the
`familyRead` lookup: an edge whose channel is in `DerivedStatChannels.Retired` is skipped and counted
into a new `AptitudeTuning.DroppedRetiredEdges`. A `familyRead` key naming a retired channel is
ignored the same way. Every consumer (hosts on the live version, the species bake on v2, tests on
any version) gets clean edges from one place. No consumer grows its own filter, which would be the
dual-fold defect in miniature.

### R3 — publish `aptitudes.v9.json` without the dead edges

R2 makes old versions *safe*. The **live** file should still say what is *true*. Balance-pass
readers look at the latest version, and two edges that do nothing are misleading. `publish.py` has no
removal operation today (`set`, `--add-edge`, `--rename-key` only), so, per AGENTS.md's rule
*"extend the tool when a domain lacks support"*:

- **`--remove-edge "channel=…,source=…"`** removes exactly one edge, and refuses if it matches zero
  or more than one.
- **`--remove-key container.path:leaf`** removes one dict key, and refuses if it is absent.

Then:

```powershell
python gk-core/tools/tuning/publish.py aptitudes --label "retire atk (owner 2026-09-18)" `
  --remove-edge "channel=progression.bonus.atk,source=Might" `
  --remove-edge "channel=progression.bonus.atk,source=Ferocity" `
  --remove-key "familyRead:progression.bonus.atk"
```

Every host that loads `aptitudes.v8.json` moves to `v9` in the same commit (`Program.cs`,
`RpgHost.cs:185`, and every other hit of `aptitudes.v8` in `src/`, measured at build time).
**`CreatureSpeciesGen`'s v2 pin is left alone.** It is `lawn-tuning-profile`'s known finding, and
moving it would change every species' magnitudes, which is a balance decision outside this module.
R2 makes the v2 bake drop the edges anyway.

### R4 — code removals

| Site | Change |
|---|---|
| `DerivedStatChannels.cs:8` `ProgressionBonusAtk` | removed; id added to `Retired` |
| `DerivedStatRegistry.cs:71` registration | removed |
| `ActorHub.cs:92` `MergeAppliedCombat` | drop the `bonusAtk` term; `Atk = primary.Atk` |
| `UniqueBoundLoadout.cs:105,134` | drop both `GrantBonus(…"atk"…)` calls. A bound loadout's `atk` field no longer grants anything; its maxHp and hp grants are unchanged |
| `DerivedAuditActor.cs:39` | row removed |
| `EntityApply.cs:407,413` telemetry | `bonusAtk` / `bonusAtkContribs` removed; `primaryAtk` / `appliedAtk` stay, and are now always equal, which the trace comment states |
| `gk-core/data/tuning/derived-stat-catalog.v2.json` → publish **v3** without the entry; hosts that load v2 (`gk-core/src/FusionRpg.Server/Program.cs`, `RpgHost.cs:96`) move to v3 | tool extension as in R3 if the catalog's shape needs it |
| `gk-data/packs/fusion/data/seed/derived-stats/catalog.json` | **check provenance first.** If authored (a registry), remove the entry. If it carries generator provenance, fix its generator and regenerate |

### R5 — generated content

- **Species:** run `dotnet run --project gk-forge/tools/CreatureSpeciesGen`. Through R2 the v2 bake drops the
  edges, and the 11 creature files lose their `progression.bonus.atk` magnitude. Commit the diff. The
  `--check` mode (CI) confirms there is no drift. **Never hand-edit the 11 files** (hard rule).
- **Passive tree: resolved by a deterministic function (owner ruling 2026-09-18, map question 2).**
  Each of the 16 atk-only nodes takes its channel from a deterministic plan **quota cell**
  (`quotaCell.channelFamily: "progression.bonus.atk"`), and that cell already names an element
  (`"element": "dark"`). The tree generator gains a closed **successor map**, applied in the quota
  stage (`gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/quota.py`):

  ```python
  # Owner ruling 2026-09-18: atk is retired, and a node that granted it is resolved
  # deterministically to power. The cell keeps its element (combat.power + 'dark'),
  # its tier, its budget share, and the node keeps its name and flavour. Closed map:
  # a new entry is a reviewed change. No model call.
  RETIRED_FAMILY_SUCCESSOR = {"progression.bonus.atk": "combat.power"}
  ```

  Then re-run the **deterministic** stages (quota → emit → `TreeBinder`); no stage that calls a
  model is re-run. `gk-data/packs/fusion/data/seed/passive-tree/plan.v1.json:433` also stops listing the retired family
  at its source, so no future plan draws it. **Why the successor lives in the tree generator and
  not in `DerivedStatChannels.Retired`:** consumers retire differently. The aptitude loader
  *drops* an atk edge, because Might and Ferocity already pay `combat.power`, and converting would
  double-pay. A tree node must still grant *something*, so it *re-targets*. One registry state and
  two consumer policies, each owned where its invariant lives. **Regeneration** is the fallback,
  used only for a node whose name or flavour no longer fits its new channel, and never by default.
  The 16 nodes are unbound today for an unrelated pool-reference reason (`TreeBinder`'s refusal
  text), so this changes the seed truth without changing the live tree until that separate refusal
  is fixed.
- **FE bundle:** `src/FusionRpg.Server/wwwroot/assets/index-*.js` contains the string, but that is
  build output. Rebuild it; never edit it.

### R6 — the guard, its test, its decision

- `guard-class-system.py` G3 now finds nothing, so the real tree exits 0.
- `ClassSystemGuardTests.ClassSystemGuard_script_exitsOneOnTheRealTree_onlyG3_permanentlyByDesign`
  is replaced by `…_exitsZeroOnTheRealTree`. The **G3 rule stays in the guard**, unchanged: it now
  protects against the channel ever being reintroduced. Add a falsifier that injects a Might →
  retired-atk edge into an in-memory tuning document and asserts G3 fires.
- `deploy-play.py`'s G3 tolerance block is deleted, if `guard-runner` has not already removed it.
- Registry: `class-system` → `ci` / `gating`.
- `tasks/class-system-plan.md` decision 12 gets a **superseded** note: *"Closed 2026-09-18 by the
  owner's ruling retiring `progression.bonus.atk` (`solid-enforcement` `retire-atk`). G3 remains as a
  regression guard and gates in CI."*
- `stub-register.md` `SR-19` is struck through with the closing SHA (`debt-ledger`'s append rule).

### R7 — closed-vocabulary pins that move, as reviewed changes

`AtomCatalogSsotDriftTests.cs:49` `Assert.Equal(269, registry.AllRegistered.Count)` becomes **268**.
It is a registry, a closed vocabulary, so pinning it is correct, and the comment gains one line in
the file's existing style: *"269 -> 268 (solid-enforcement retire-atk, 2026-09-18):
`progression.bonus.atk` retired by owner ruling."* Every other doc or test stating 269 is found with
`grep -rn "269" docs tests | grep -i "regist"` and updated in the same commit.

## Commands

```powershell
python gk-core/tools/tuning/publish.py aptitudes … (R3)
dotnet run --project gk-forge/tools/CreatureSpeciesGen
dotnet run --project gk-forge/tools/CreatureSpeciesGen -- --check
.\scripts\run-guards.ps1 -Only class-system
dotnet test tests\FusionRpg.Core.Tests --filter "Category=BalanceGuard"
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>
```

## Testing strategy

- **The resolver keeps its protection:** an edge to a never-registered channel **still throws**.
  `AptitudeResolverTests.cs:117` holds an `Assert.Throws<InvalidOperationException>`. Confirm at
  build that it is the unregistered-channel case (add one if it is not), and add a retired-channel
  counterpart that loads without throwing and reports `DroppedRetiredEdges == 2` for v8.
- **The reader-census tests keep passing without edits:**
  `AptitudeTuningTests.EveryEdgeChannel_isRegistered_inDerivedStatRegistry` (`AptitudeTuningTests.cs:154`)
  and `AptitudeMatrixTests.cs:553` iterate the **parsed** edge list, and R2 removes retired edges
  before anything iterates them. If either reads the raw JSON instead, that is a second filter site,
  so route it through the loader rather than teaching it about retirement.
- **Every published aptitudes version v1–v9 loads.** A theory over the files on disk. It asserts
  loadability and never a per-version edge count, because those are readings.
- **Parity:** a sim actor with a Might allocation now has `Attack == primary Atk`. Assert equality
  with the battle composition of the same actor, not a literal.
- **`Category=BalanceGuard` and sim-dependent goldens run before and after.** Any golden that moves is
  triaged in the commit body as the expected consequence of dropping a sim-only bonus. A move with any
  other explanation stops the module.
- **Cross-boundary** (Core, Data, Server, Injector, tuning, generated data): per AGENTS.md this is one
  of the three sanctioned full-suite points, and the full suite runs once, at the end of the module.

## Boundaries

- **Always:** drop retired channels in the loader, never in consumers. Regenerate generated content.
- **Ask first:** moving `CreatureSpeciesGen` off `aptitudes.v2` (a `lawn-tuning-profile` balance
  question).
- **Out of this module, by the owner's ruling:** `BattleActorSetup.Atk` and species `attackBase` as
  a damage input. Damage moves to the action in wave 5 (`action-base-stats`), which needs its own
  spec. `StatChannels.Atk` observes PvZ's field and is unaffected either way.
- **Never:** hand-edit generated creatures, passive-tree nodes or the FE bundle. Never edit
  `aptitudes.v1`–`v8`. Never delete G3.

## Success criteria

- [ ] `progression.bonus.atk` is absent from `src/`, from the latest `aptitudes` and
      `derived-stat-catalog`, from `gk-data/packs/fusion/data/generated/creatures/**` and from the rebuilt FE bundle.
      Historical tuning versions keep it and load cleanly.
- [ ] `guard-class-system` exits 0 on the real tree and gates in CI. Its falsifier proves G3 is live.
- [ ] Unknown channels still throw; retired ones are dropped and counted.
- [ ] Decision 12 is marked superseded, and SR-19 is struck with a SHA.
- [ ] Full suite green once at module end, with every moved golden explained.

## Self-audit — the debate

**Objection: "Just delete the channel. 'Retired' is ceremony."** Deleting it crashes every load of
`aptitudes.v1`–`v8`, including the species bake's v2 (`AptitudeResolver.cs:39` throws). The
alternatives are editing immutable history (forbidden), or teaching each consumer to skip it (a
filter in N places, which is the dual-fold defect). One closed set, read by one loader, is the
smallest correct design.

**Objection: "Doesn't a `Retired` set invite retiring things instead of designing them out?"** It is a
closed vocabulary with a pinned size and a reviewed-change rule, the same discipline as `KindCount`.
Its only job is keeping immutable history loadable after a design change, and every retirement
carries a dated ruling in the code comment.

**Objection: "The owner said 'atk is redundant'. Why keep `Setup.Atk` / `attackBase` in this
module?"** Because `combat.power` is a multiplier and needs a base magnitude, and today the creature's
attack *is* that base. The owner has since ruled where the base goes, onto the action (2026-09-18).
That is a battle-damage redesign with goldens, and it gets its own wave (`action-base-stats`) and
spec, not a cleanup module. This module removes the one channel that is inert everywhere except the
sim, so it lands with no lawn or battle behaviour change.

**Objection: "Why publish v9 when R2 already neutralises v8?"** Because the latest tuning file is
documentation a balance pass reads. Two edges that do nothing would invite someone to tune them.

**Objection: "Is the sim change a balance regression?"** It is a correction. The sim was the only
place paying a bonus live battle never paid, which is exactly the kind of mismatch that makes a
simulated balance pass lie about the real game.

## Gaps found and closed while writing

- **The first draft said "remove the channel and regenerate".** Reading `AptitudeResolver.cs:39`
  showed that crashes. That is what produced R1 and R2.
- **The v2 species bake** would have been missed entirely by a plan that only moved hosts to v9.
  Found at `CreatureSpeciesGen/Program.cs:70`, and handled by R2 without touching the v2 pin.
- **The G3 red was intentional** (decision 12, plus a test pinning it). A plan that just "made the
  guard green" would have left a test asserting red. R6 replaces the test and supersedes the decision
  explicitly.
- **The 16 passive-tree nodes looked like a content decision.** Measuring the generated tree showed
  all 16 are already unbound, so the default is a no-op on live content, and the owner question is
  only about future re-rolls.
