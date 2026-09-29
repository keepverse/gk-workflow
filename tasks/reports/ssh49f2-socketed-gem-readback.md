# ssh49f2 — `SSH4.9-F2` re-measured: the mint and the read path agree; the word fires

**Lane:** `ssh49f2` · **Program:** strain-splice-host · **Branch:** `cmdc/ssh49f2` · **Date:** 2026-09-22
**Subject:** `SSH4.9-F2` ("the mint's container id and the read path's corpus key disagree").

## Verdict

**The seam does not exist.** `item_socket.insert_container_id` holds the shipped gem corpus's own `id`
(`gem.g1-023`), and both the mint and every read path key on that same `id`. The `gem.sturdy-layering` /
`gem.bulwark-core` the finding quoted are those gems' **`nameKey` display keys** — `ssot-presentation.md`
§2.4 ("atom ids, family ids, container ids, instance ids. Debug surfaces only.") is why the card carries
`insertKey` instead of the container id. No production line changes; the responsible layer is the reading,
not the code.

**The sentences that decide it (the spec is not silent).**

- `docs/architecture/item/ssot-sockets.md:406` — `insert_container_id` is *"TEXT | nullable — the `gem.*`
  container filling it; NULL = empty"*. The column's referent is the **container**, and a `gem.*`
  container's id is the one the corpus authors (`gk-data/packs/fusion/data/seed/items/gems/*.json`'s `id`).
- `docs/architecture/item/spec-sockets.md` §7 — *"An insert is a `gem.*` container with
  `prefix_rolls = 0` AND `suffix_rolls = 0` … so every `gem.ember-shard.t3` is identical everywhere and
  an insert in the bag is a **quantity**"*: one insert = one corpus container id, everywhere, by
  construction. A name-derived id would make the same gem two different things in two places.

So the corpus `id` is canonical and **neither side moves** — the mint already writes it and the read path
already resolves it. The only name-derived value on the surface is the display key, which the spec's
§2.4 requires the card to carry instead of the container id.

| Side | Site | Key |
|---|---|---|
| mint builds the container | `gk-core/src/FusionRpg.Core/Items/Gems/GemContainerBuild.cs:67` | `ContainerId = seed.ContainerId` — the corpus `id` |
| socket row is written | `gk-core/src/FusionRpg.Core/Items/Sockets/SocketOperations.cs:102` | `InsertContainerId = insert.ContainerId` |
| the insert def comes from | `gk-core/src/FusionRpg.Server/ItemCardEndpoints.cs:179` | `new InsertDef(id, family, element, tier)`, `byId[id]` |
| read path resolves it | `gk-core/src/FusionRpg.Server/ItemSurfaceEndpoints.cs:240-245` | `lookupInsert(id)?.Def` — the same corpus delegate |
| equip projection resolves it | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EquipCombinations.cs:95-96` | `inputs.LookupInsert(insertContainerId)` |
| the surface shows a key | `gk-core/src/FusionRpg.Core/Items/Display/ItemCard.cs:552` | `insertKey` = `CardSocketCell.InsertNameKey` = the corpus `nameKey` |

A filled socket the corpus does **not** carry cannot render at all: `RpgStore.ItemCard.cs:448` throws
and `ItemCardEndpoints.cs:631` turns it into `409 item.card-unrenderable`. The probe's card returned 200,
so the lookup HIT.

## Why the probe's word did not fire — two product rules, both by design

1. **The chassis is a set piece.** `item.humanoid-torso-a-005` is a member of 8 shipped sets, so
   `SocketHostFor` reports `IsSetPiece: true` and D21 (`SetExclusivityValidator.MayFire`, applied at
   `CombinationEvaluator.cs:79` and `CombinationDistance.cs:191`) withholds every Strain/Splice.
2. **The recipe is frame-pinned.** `combo.splice-agility-bulwark` declares `hostFrame: "plant"`; the
   chassis is `humanoid`, and `ComboMatcher.HostAdmits` (`ComboMatcher.cs:73`) refuses it before the
   multiset is checked.

`/combinations` answered `[]` because an Active row is the only row `CompendiumReveal.Render`
(`CompendiumReveal.cs:107-118`) shows once the four gems have been spent out of stock — nothing Active,
nothing revealed.

## Regression proof (new)

`gk-core/tests/FusionRpg.E2E.Tests/SocketedGemCombinationE2ETests.cs` — the live chain through the real routes on
the in-process `RpgApiFactory` host, no game:

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the word fires on a chassis that admits the recipe | `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet` | `Passed! - Failed: 0, Passed: 236, Skipped: 0, Total: 236` | this commit |
| `SSH4.9-F2`'s premise (row id ≠ corpus key) | same | refuted: rows read back as `gem.g2-002`, `gem.g1-023`, `gem.g3-009`, `gem.g1-019` | this commit |
| the fired word binds on a real specimen | same | `/combinations` `state: "Active"`, `ComboTargetsFor` -> `cmb:{chassis}#c0:combo.splice-vigor-bulwark-t1`, then equip -> binding present in `ResolveBindings` | this commit |
| the probe's own chassis fires nothing | same | set piece: no splice row, no target | this commit |
| test substrate | `python gk-core/scripts/guard-test-substrate.py` | `TEST SUBSTRATE GUARD OK` | this commit |
| session boundary (lane worktree root) | `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/cmdc-ssh49f2 --session ssh49f2` | `[session-boundary] clean for 'ssh49f2'` | this commit |
| session boundary (brief's main root) | `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner --session ssh49f2` | `DRIFT (1): no session record for 'ssh49f2'` — the record lands with this branch, so the main checkout cannot see it until the merge | `tasks/sessions/ssh49f2.json` |
| the standard path-verification | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths @('gk-core/tests/FusionRpg.E2E.Tests/SocketedGemCombinationE2ETests.cs','tasks/strain-splice-host-todo.md','tasks/reports/ssh49f2-socketed-gem-readback.md','tasks/sessions/ssh49f2.json') -Session ssh49f2"` | **fail (pre-existing, `SSH4.9-F6`)**: the doc-citation gate exits 1 on 14 HIGHs already in `tasks/strain-splice-host-todo.md` before any guard or test runs (`@@ -989,5 +989,20 @@` is this lane's only hunk there) | see `SSH4.9-F6` |

## NOT proved

- The live re-probe (owner/manager): nothing here touched a running game or the owner's install.
- `SSH4.9`'s own steps (3)/(4) — the manager's.
- The first full-suite run after this test landed failed `RpgScenarioSlice0E2ETests` once
  (`Failed: 1, Passed: 235`); the next three runs passed 236/236, and the suite passes 234/234 with this
  file filtered out. Not reproduced, message not captured — recorded as a flake, not as fixed.
- No unit test for `SSH4.9-P2`'s three grant routes (unchanged by this lane).
- `verify-change.ps1`'s doc-citation gate is red on the todo file for a reason that predates this lane
  (`SSH4.9-F6`); the E2E suite and both guards it would have run were run directly instead and are green.
- The brief's main-root session-boundary check reports the unmerged record as drift; the record is
  committed on this branch and the same check is clean against this lane's worktree root.
- **Substrate head.** This lane's run is on `5709cffca` (branch `cmdc/ssh49f2`), which is an ANCESTOR of
  the TARGET 0 memory-plan commit `30928541b` on `features/mega-merge` — so this worktree does NOT carry
  the memory plan, and the E2E numbers above were taken on the pre-TARGET-0 `RpgApiFactory`. The new test
  needs nothing from the disk: it takes the host from `factory.CreateClient()` and the store from
  `factory.Services.GetRequiredService<RpgStore>()`, creates no store of its own, and touches no
  `DataDir`, so it is compatible with the memory plan by construction — but the merged-head run is the
  manager's `post_merge_check.py`, not a claim here.

## Findings routed (rows added to `tasks/strain-splice-host-todo.md`)

- `SSH4.9-F3` — `gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj` has no copy rule for `gk-data/packs/fusion/data/seed/rarity/**`,
  so `SeedImportRunner.FindUp` stops at the exe's partial `gk-data/packs/fusion/data/seed` and a boot-seeded install has an
  empty rarity ladder. Masked in `deploy-play.ps1` runs only because `gk-forge/tools/AtomImporter` seeds the DB.
- `SSH4.9-F4` — `item.plant-stem-a-005` names implicit family `atom.regeneration`, which no shipped atom
  row carries, so `/api/debug/grant-item` refuses it (`the base type's implicit atom 'atom.regeneration.t1'
  is not in the loaded atom catalog`).
- `SSH4.9-F5` — `/api/test/reset` does not clear `rpg_material_spend_log`, so two tests sharing a
  correlation id replay each other's op and the replay names the other test's instance.
- `SSH4.9-F6` — 13 D3 + 1 D2 doc-citation HIGHs already in `tasks/strain-splice-host-todo.md` make
  `verify-change.ps1` exit 1 on that file before any guard or test runs, for every lane that must
  touch it. Pre-existing (this lane's only hunk there starts at line 989); filed, not guessed at.
