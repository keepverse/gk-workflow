# SOLID enforcement — capability map

**Status:** spec phase, Phase 0, written 2026-09-18 under the owner's `/goal` directive to take the
program through specification and planning. **Not yet reviewed by the owner.** Every module spec in
`docs/architecture/solid-enforcement/` was written against this map. The owner's review of this page
is **Checkpoint 0** in the plan. It is a review of work already written, not a gate that stops the
writing: a boundary the owner redraws means editing specs, not throwing them away.

**Program id: `solid-enforcement`.** This is **phase 3** of the SOLID program:

| Phase | Program | What it did | State (measured 2026-09-18) |
|---|---|---|---|
| 1 | `actor-hub-and-combat-power-solid-fixing` | Fused one subsystem's dual compose (`BattleStatComposer` deleted) | 191 done / 1 open, and that one item is the owner accepting the close |
| 2 | `solid-remediation` | Fixed the repo-wide register of SOLID instances | 96 done / 1 open: T4.4's S7, **deferred by the owner** on 2026-09-17 |
| **3** | **`solid-enforcement`** | **Make each class of violation impossible to merge, not just findable** | this map |

Plan and todo: [`tasks/solid-enforcement-plan.md`](../../tasks/solid-enforcement-plan.md),
[`tasks/solid-enforcement-todo.md`](../../tasks/solid-enforcement-todo.md).

---

## The owner's rulings this map is built on (2026-09-18)

1. **Scope: "Everything SOLID, one program."** Every SOLID invariant, its guard, its backlog, and the
   structural instances still open belong to this one program, including items earlier programs had
   parked or handed off. Where that contradicts an earlier hand-off, this ruling wins and the hand-off
   is recorded as superseded in the module that absorbs it. (SOLID's own S: one owner per
   responsibility, so no piece of SOLID debt keeps two programs claiming it.)
2. **Backlog policy: "Green-first, then gate."** When a guard is new, or newly wired into CI, and finds
   existing violations, the module clears them first and then flips the guard to failing. A permanent
   "report-only" state and a frozen "known-red allowlist" are both ruled out. This matches
   `solid-remediation`'s decision 1 (*"clear the reds and make 'all green' literal, rather than
   freezing a known-red baseline"*).
3. **`atk` is retired.** The owner: *"my design don't have atk, it only have power and defense, seem
   like atk is adundant need to retire."* The code agrees, see the next section.

## What the inventory found — the program's evidence

Everything here was measured on `features/mega-merge` on 2026-09-18, and is a reading rather than a
constant.

### Guards exist; enforcement does not

There are **18** `scripts/guard-*.ps1`. They are listed by hand in **three** places that disagree:

| Where | Guards it runs |
|---|---|
| `.github/workflows/ci.yml` (merge gate) | 8 |
| `gk-fusion/scripts/deploy-play.py` (local deploy) | 16 |
| `gk-core/scripts/verify-change.py` via `verification-boundaries.v1.json` | per-boundary subset |

Of the **9 guards CI never runs**, running each one today gives:

| Guard | Result | What it means |
|---|---|---|
| `debug-scope` | ✅ green, 102 routes | Can gate today |
| `magic-numbers` | ✅ green (28 M3 notes, 0 gating) | Can gate today |
| `overflow` | ✅ green (46 A3 notes, 0 critical) | Can gate today |
| `power` | ✅ green | Can gate today |
| `stat-pairs` | ✅ green | Can gate today |
| `class-system` | ❌ **red**: G3 Might and Ferocity both feed `combat.power.*` **and** `progression.bonus.atk` | Fixed by `retire-atk` |
| `commit-policy` | ❌ **red**: 5 GitHub web-merge commits (author `'Lê Tú Hào'`, committer `GitHub`) fail the identity allowlist | Fixed by `commit-policy-green` |
| `game-profile` | needs `-GameDir` | **Cannot** run in CI: it needs the game install, and the hard boundary forbids game binaries on a runner |
| `injector-compile` | ✅ green locally | **Cannot** run in CI for the same reason (`CiWiringGuardTests` already records the matching exemption for `Injector.Tests`) |

So **five** guards are green and unwired. That is a wiring gap, not a missing capability, and it is the
cheapest enforcement win in the repo. A second finding is structural: nothing mechanical stops a new
guard from being written and then never wired. That is how nine guards ended up where they are.

### Invariants with no guard at all

Mapped against `DESIGN-GATE.md` §2 (16 invariants) and `CLAUDE.md`'s hard rules:

| Invariant | Guard today | This program |
|---|---|---|
| RPG never changes what PvZ is (only a closed set of Unity fields may be written) | none | `pvz-write-surface` |
| Standalone-first: Core/Data/Server/Contracts/CheatCore never touch Unity or the Injector | none (holds today: 0 violations) | `repo-boundary` |
| `gk-core/data/tuning/**` is never edited in place; a change publishes `v{n+1}` | none, and it was broken on 2026-09-17 (`a60706c0`) | `tuning-immutability` |
| `/plan` output never goes to `tasks/plan.md` / `tasks/todo.md`; no `SPEC.md` | none | `repo-boundary` |
| A guardrail pins closed vocabularies, never population counts | none | `population-pin` |
| A closed vocabulary is declared once (C# ↔ seedsmith Python mirrors) | none (seedsmith's `vocab.py` sat stale on `ActionTag` 8→9) | `vocabulary-mirror` |
| A `file:line` in a doc must resolve | report-only (`audit-doc-citations.py`, 2026-09-18) | `doc-citation-gate` |
| Open/Closed on identity: a role is a population, never an enum | none (`CommanderId` is a two-member enum) | `commander-identity` |
| One identity per role: a save is not an empire, and an empire is never a player row | none (Zomboss is a `players` row found by name, `RpgStore.ZombossDeploy.cs:25-29`, shared by every save) | `save-identity` (ruling R3) |
| One responsibility per file | none (8 C# files > 1,500 lines, 5 non-test TSX > 600) | `srp-file-budget` |
| An edge-refreshed cache enumerates its full trigger set (§2.16) | none | **Recorded `unguardable` with a reason** in the registry. It needs a per-cache declaration, not a scan |

### `atk` — the owner's question answered from code

*"Did atk increase atk in lawn run only?"* No. **It does nothing on the lawn either.**

- **Lawn:** `progression.bonus.atk` composes into `AppliedCombat.Atk`
  (`ActorHub.cs:92`), but the Unity write is commented out at `EntityStatWriter.cs:120` (plant) and
  `:199` (zombie) since 2026-09-16. It reaches telemetry only (`EntityApply.cs:402`).
- **Battle:** `BattleHubCompose.ResolveDerived` composes it into the snapshot, and nothing under
  `Battle/` reads it. Damage reads `Setup.Atk` through the ledger (`BattleEngine.cs:101`).
- **Standalone sim:** `SimEngine.cs:247,313` (`entity.Attack = final.Atk`) is **the only live
  consumer.** So the sim pays a bonus that live battle ignores, which is itself a substitution
  defect (the L in SOLID).

Its footprint is larger than one channel: 2 aptitude edges (`Might` 10000‰, `Ferocity` 6000‰ in
`aptitudes.v8.json`), **16** passive-tree nodes whose *only* effect is `progression.bonus.atk`, the
species-build magnitudes of **11** generated creatures, `derived-stat-catalog.v2.json`,
`UniqueBoundLoadout`'s atk grant, and `DerivedAuditActor`. Both the passive-tree nodes and the
creature files are **generated**, so the fix is a generator change followed by regeneration
(hard rule).

### Other findings the inventory produced

- **Test output committed into the balance surface.** `data/tuning/loopwarntest13c4c662.v{1,2}.json`
  and `loopwarnteste194b09f.v{1,2}.json`, 62–65 KB each, are written by
  `gk-core/tests/FusionRpg.Core.Balance.Tests/Balance/ResidualFitLoopTests.cs` into the real tuning tree. They were
  swept into bulk "update seeds" commits (`dcabac32`, `52713f44`) and are now copied into every
  test and tool `bin/`. Absorbed by `tuning-immutability`.
- **The standalone boundary holds.** 0 Unity/Il2Cpp/MelonLoader/BepInEx `using`s and 0 forbidden
  project references across Core, Data, Server, Contracts and CheatCore. `repo-boundary` pins that
  state so it stays true; there is no backlog to clear.
- **A live mirror drift.** Seedsmith's `adapters/actions/vocab.py` `STATUSES` has **21** members; the
  live `status-catalog.v1.json` has **24**. `nerve.afflicted`, `nerve.shaken` and `nerve.unsettled` are
  missing. Its test pins `len(STATUSES) == 21` against a hand-copied literal, so the test and the
  mirror went stale together. Absorbed by `vocabulary-mirror`.
- **Population pins, including the recorded incident recurring.** Restricted to tests that read
  committed content: 205 literal count asserts ≥ 10 in C# and 69 in seedsmith Python. They include
  **`904`** (the species roster, in `test_tree_species_roster.py`), `775` fusion recipes, and one
  closed-vocabulary count (`269` registered channels) pinned in **six** separate files. Absorbed by
  `population-pin`.
- **`CommanderId` means two things.** It is used as the **empire** (the species-allocation key, kill
  attribution, allocation scope) *and* as the **commander** (the unit). Opening it without splitting
  it would let a creature-commander re-key species progression. Absorbed by `commander-identity`,
  which splits it into `EmpireId` and `CommanderRef`.
- **258 literal count assertions ≥ 10**, across 124 test files. Most are legitimate closed-vocabulary
  pins (the most common value, **10**, is the ten-rung rarity ladder, and **12** is the twelve
  aptitudes), so `population-pin` makes the author *declare* the vocabulary rather than guessing
  from the number.

---

## Modules

| Module id | Responsibility | Depends on |
|---|---|---|
| `enforcement-registry` | One machine-readable register: invariant → guard → tier → status → backlog module. A meta-test keeps it honest | — |
| `guard-runner` | One runner (`gk-core/scripts/run_guards.py`) that CI, `deploy-play` and `verify-change` all call. Deletes the three hand-kept lists | `enforcement-registry` |
| `debt-ledger` | `stub-register.md` becomes the one ledger of SOLID debt *instances* across programs | `enforcement-registry` |
| `wire-green-guards` | The five green, unwired guards gate in CI. The two game-bound guards are classified `local` with a reason | `guard-runner` |
| `commit-policy-green` | GitHub web-merge commits pass the identity policy; the guard gates | `guard-runner` |
| `retire-atk` | `progression.bonus.atk` is gone from code, tuning and generated content; `class-system` gates | `guard-runner` |
| `tuning-immutability` | A published tuning version's values never change; test pollution is removed from the tree | `guard-runner` |
| `repo-boundary` | Standalone-first assembly boundary, plus frozen legacy paths (`SPEC.md`, `tasks/plan.md`, `tasks/todo.md`) | `guard-runner` |
| `pvz-write-surface` | **Extends `guard-single-writer`** (no new guard): the closed set of Unity fields each writer file may assign, and five retired damage-equation fields written nowhere | `guard-runner`, `retire-atk` |
| `vocabulary-mirror` | Every seedsmith Python mirror of a C# closed vocabulary matches it member-for-member | `guard-runner` |
| `population-pin` | A literal count assertion must name the closed vocabulary it pins | `guard-runner` |
| `doc-citation-gate` | Clear the citation backlog, add the status-line check, and make the audit gate | `guard-runner` |
| `commander-identity` | `CommanderId` is **split** into `EmpireId` (the faction) and `CommanderRef` (the unit), both open, resolved through one `ICommanderDirectory`; adds `guard-open-identity` | `debt-ledger` |
| `save-identity` | Rulings R3 + R17: a Save owns its empires, each keyed `(SaveId, EmpireId)`. The `players` row is the save (no id rewrite); empires live in `rpg_save_empires(save_id, empire_id, controller)`; Zomboss stops being a player row; empire-owned tables re-keyed (Tier A) or empire-typed and fail-loud (Tier B); AI-empire specimens leave the human-only paths (contracts, codex, activity facts); one ownership predicate for specimen writes; ownership carried in the spawn payload; one backed-up migration. Extends `guard-open-identity` with I3 and I4; four `decisions.md` rows drafted (S1–S4) | `commander-identity` |
| `srp-file-budget` | No production file above its line budget; the 13 over-budget files are split without changing behaviour | `guard-runner` |
| `action-base-stats` | **Wave 5, idea phase.** Every action owns its base (`BasePowerMilli`, `HitCount`); damage stops reading the creature's `atk`. Ideal: [action-base-stats-ideal.md](action-base-stats-ideal.md). Spec follows its two open questions | `retire-atk` |

Sixteen modules. **Each ends green:** its guard gates in CI (or is registered `local` or
`unguardable` with a reason), the scoped `verify-change.py` passes, and every guard still passes.

## Build order

```
Wave 0  enforcement-registry ─► guard-runner ─► debt-ledger
                                     │
Wave 1  wire-green-guards · commit-policy-green · retire-atk          (parallel)
                                     │
Wave 2  tuning-immutability · repo-boundary · vocabulary-mirror        (parallel)
        pvz-write-surface   (after retire-atk: both edit the atk write site)
                                     │
Wave 3  population-pin · doc-citation-gate                            (backlog-heavy, parallel)
                                     │
Wave 4  commander-identity ─► save-identity · srp-file-budget        (structural; srp last)
                                     │
Wave 5  action-base-stats                                             (idea phase: spec after its ideal's questions)
```

**Why this order.**

- **The registry comes first.** Every later module's exit criterion is "its row flips to `gating`",
  and that row has to exist before a module can be judged done.
- **The runner comes second.** Wiring a guard into three hand lists is the defect being removed, so
  no guard gets newly wired before a single wiring point exists.
- **`save-identity` follows `commander-identity`.** It keys empires by `EmpireId`, which that module
  creates, and both edit the empty-save seed (the name there, the empires here). It precedes
  `srp-file-budget` for the same reason every structural module does.
- **`srp-file-budget` goes last.** It moves the most code, and splitting a file while other modules
  are still editing it is a collision. Last means it splits settled files.
- **`pvz-write-surface` follows `retire-atk`.** Both touch `EntityStatWriter`'s retired atk lines,
  and one editor at a time avoids a merge conflict inside one program.

### Two couplings the specs surfaced, recorded here so the plan honours them

- **`retire-atk` cannot simply unregister the channel.** `AptitudeResolver.cs:39` throws on an edge
  to an unregistered channel, published tuning versions are immutable, and
  `gk-forge/tools/CreatureSpeciesGen/Program.cs:70` still bakes species from **`aptitudes.v2.json`**. The spec
  therefore makes "retired" a first-class, closed registry state that the aptitude loader drops, so
  every historical version stays loadable. The v2 pin itself is `lawn-tuning-profile`'s finding and is
  left alone.
- **`class-system`'s red is intentional today.** `tasks/class-system-plan.md` decision 12 made G3
  permanently red *"until `battle-adoption` ships or the design changes"*, and
  `ClassSystemGuardTests.…_permanentlyByDesign` pins exit 1. The owner's atk ruling is that design
  change. `retire-atk` supersedes decision 12, replaces that test, and only then does the guard gate.
- **Cross-program (added by the `test-verification-boundary` strengthen pass, 2026-09-18):** SE0.7
  sets `verification-boundaries.v1.json` `schemaVersion` to 2, lands before that program's
  `registry-contract` (3, then 4, then 5), and keeps today's 12 `guards` ids as catalog ids, `magic-numbers` included.
  The one sequence is in [test-verification-boundary-map.md](test-verification-boundary-map.md) §3.2 and §5.

## Module specs

| Module | Spec |
|---|---|
| `enforcement-registry` | [spec-enforcement-registry.md](solid-enforcement/spec-enforcement-registry.md) |
| `guard-runner` | [spec-guard-runner.md](solid-enforcement/spec-guard-runner.md) |
| `debt-ledger` | [spec-debt-ledger.md](solid-enforcement/spec-debt-ledger.md) |
| `wire-green-guards` | [spec-wire-green-guards.md](solid-enforcement/spec-wire-green-guards.md) |
| `commit-policy-green` | [spec-commit-policy-green.md](solid-enforcement/spec-commit-policy-green.md) |
| `retire-atk` | [spec-retire-atk.md](solid-enforcement/spec-retire-atk.md) |
| `tuning-immutability` | [spec-tuning-immutability.md](solid-enforcement/spec-tuning-immutability.md) |
| `repo-boundary` | [spec-repo-boundary.md](solid-enforcement/spec-repo-boundary.md) |
| `pvz-write-surface` | [spec-pvz-write-surface.md](solid-enforcement/spec-pvz-write-surface.md) |
| `vocabulary-mirror` | [spec-vocabulary-mirror.md](solid-enforcement/spec-vocabulary-mirror.md) |
| `population-pin` | [spec-population-pin.md](solid-enforcement/spec-population-pin.md) |
| `doc-citation-gate` | [spec-doc-citation-gate.md](solid-enforcement/spec-doc-citation-gate.md) |
| `commander-identity` | [spec-commander-identity.md](solid-enforcement/spec-commander-identity.md) |
| `save-identity` | [spec-save-identity.md](solid-enforcement/spec-save-identity.md) |
| `srp-file-budget` | [spec-srp-file-budget.md](solid-enforcement/spec-srp-file-budget.md) |

### Guards this program leaves behind

Seven new rows in the registry's catalog: `tuning-immutability`, `repo-boundary`,
`vocabulary-mirror`, `population-pin`, `doc-citations`, `open-identity` and `file-budget`. Two
existing guards are **extended** rather than duplicated (`single-writer` gains W2/W3;
`test-substrate` gains the swallowed-`File.Delete` rule), and the new `open-identity` gains rule I3
from `save-identity` (no `players` row is ever looked up by name). Seven existing guards move to `gating` in
CI: the five green ones, `class-system` and `commit-policy`. The end state has **no row at
`status: backlog`**.

## Decisions this map records

**D1. A guard is not done until it gates.** Every guard module ends with the guard at
`status: gating` in the registry. Report-only is allowed only *during* a module, as the step before
green, never as a finishing state (ruling 2).

**D2. "Unguardable" is a legal registry state, and it must justify itself.** Some invariants cannot be
checked by a scan (§2.16 cache triggers, §2.10 main-thread perf). They are registered as
`unguardable` with a written reason, and the meta-test refuses an empty reason. This is how the
program covers everything without pretending to.

**D3. "Local" is a legal tier, and it also must justify itself.** A guard that needs the game install
is `tier: local` and runs in `deploy-play`. The one legal reason is the hard boundary that keeps game
binaries off a CI runner. This extends the pattern `CiWiringGuardTests.ExemptFromCiWiring` already
uses for test projects, rather than inventing a second one (the O in SOLID, applied to the program
itself).

**D4. Markers over heuristics.** Where a scan cannot tell a legitimate case from a violation, the
author declares intent with a one-line marker that the guard reads: `citations-historical` (already
shipped), `pin: closed-vocabulary <Name>` (`population-pin`), and `srp-budget-exempt: <reason>`
(`srp-file-budget`, expected to stay empty). A marker takes a deliberate line to write, cannot be
applied by accident, and turns a fuzzy lint into a precise gate.

**D5. The `CommanderId` fix moves here from `empire-progression`.** Ruling 1 makes it this program's.
`empire-progression-ideal.md` keeps the feature (what a commander *does*: XP, delve participation,
aura per mode). This program owns only the SOLID shape change: the closed enum becomes an open
identity, so that feature lands by adding data instead of editing `switch` statements.

**D6. FE god files are in scope.** `solid-remediation`'s `fe-debt-register` handed FE structure to "a
later FE program". Ruling 1 supersedes that for *file-size* SRP. The register keeps its other
entries.

## What this program deliberately does not decide

- **What a commander does.** `empire-progression` owns that (D5).
- **The numbers inside the new action base.** The owner ruled damage moves to the action
  (wave 5). *Which* coefficients an action carries is a balance pass against a real corpus, not this
  program's decision.
- **Re-deriving `threatBand` across the corpus** with `creature-threat.v2.json`. That is R-CS5's
  follow-through in `creature-seed` and is unrelated to SOLID.
- **Closing phases 1 and 2.** Both carry one item that is genuinely the owner's (the phase 1 close,
  and the deferred S7). `debt-ledger` records them. It does not tick them.

## Owner rulings on this map's open questions (2026-09-18)

1. **Is the creature's base attack also "atk"? Answered: yes, and damage moves to the action.**
   *"use action base stats instead of atk. Each action have base stats, check attack action and
   extend it idea if missing, this idea usually use in almost rpg."* The check found the gap: an
   `ActionRow` has **no** base-stats block (`ActionRow.cs:15-60`), and the basic attack's damage reads
   the creature (`BasicAttack.cs:369` `BaseOverlayDamage = attacker.LiveAtk(...)`, which is
   `Setup.Atk`). The idea phase for it is written:
   [action-base-stats-ideal.md](action-base-stats-ideal.md). It becomes this program's **wave 5**,
   module `action-base-stats`. `retire-atk` (wave 1) stays scoped to the progression bonus channel,
   because retiring the creature's base attack needs the action base to exist first.
2. **The 16 atk-only passive-tree nodes? Answered: a deterministic function, or regeneration.**
   *"use deterministic function to resolve power or regenerate."* Chosen: **the deterministic
   function.** It needs no model run, it is reproducible, and it keeps each node's name, flavour,
   tier and budget. Each node's channel comes from a deterministic plan quota cell
   (`quotaCell.channelFamily`), and the cell already names its element (`"element": "dark"`). So the
   tree generator gets a closed successor map, `progression.bonus.atk → combat.power`, which keeps the
   cell's own element (`combat.power` + `dark`), applied in the quota stage
   (`gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/quota.py`), followed by a re-run of the
   deterministic stages. Regeneration stays the fallback for any node whose text no longer fits.
   Specified in `spec-retire-atk.md` R5.
3. **GitHub web-merge commits? Answered: yes.** `commit-policy-green` ships as specified.

4. **M3 / A3? Explained, and the default reversed.** The owner asked what these are (see the plan's
   owner-questions table). My earlier default, "don't promote", contradicted ruling 2 (no permanent
   report-only), and my description of A3 as "informational" was wrong: the overflow audit labels it
   HIGH. **New default: promote both after clearing their backlogs** (SE3.14 M3, SE3.15 A3), pending
   the owner's confirmation.
5. **The first commander's name? Answered: the player's name.** That is rift-gate decision 7, recorded
   2026-09-15 and never built (`CommanderEndpoints.cs:87` still emits the constant "Crazy Dave"), now
   owned by `commander-identity`. The owner's onboarding idea names an empty-save player "Crazy Dave";
   the code seeds `'Player 1'` (`RpgStore.cs:4018`). `commander-identity` changes the seed, so a fresh
   boot's first commander shows "Crazy Dave" and a named save shows its own name.
6. **Is Zomboss one global row or one per save? Ruled (R3, [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md)):
   neither; add a save identity.** A Save owns its empires, each keyed `(SaveId, EmpireId)`; the player
   row stops doubling as an empire; Zomboss stops being a player row. Specified as module
   `save-identity`, beside `commander-identity`, which it composes with and never duplicates.
   **R17 fixed its shape:** the player row is the save, `SaveId` is today's player id, and empires split
   into `rpg_save_empires(save_id, empire_id, controller)`. The strengthen pass (2026-09-18) added what
   the code demanded: AI specimens skip contracts (which also clears a latent stop on Zomboss's 13th
   deploy), one specimen-ownership predicate, per-spawn ownership in the injector, an evidence test that
   never archives a player's save named "Zomboss", and the cross-program keying sweep (three mismatches still open,
   each with its owner, listed in the spec).
- **Two new, from the action-base-stats ideal:** which number the lawn resolves a hit from (the
  recommendation is the action's base), and skill base power as a rung default versus authored (the
  recommendation is the rung default with an override). Both belong to `action-base-stats`, and neither
  affects waves 0–4.
