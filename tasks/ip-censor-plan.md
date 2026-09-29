# Plan: ip-censor — detection tool, release gate, avoid-list, and the two IC-4 fixes

**Status: approved 2026-09-22, ready for lanes.** Plan written 2026-09-19; owner approved implementation
2026-09-22. No task started. Premises re-verified at the convergence head 2026-09-22 — see
[§13 Addendum](#13-addendum-2026-09-22--premise-verification-against-the-convergence-head). **One
external dependency closed**: TVB3.1/TVB3.2 have landed, so T13 no longer waits.
Task list: [ip-censor-todo.md](ip-censor-todo.md). Program id: `ip-censor`.
Inputs: [ip-censor-ideal.md](../docs/architecture/ip-censor-ideal.md) (owner rulings IC-1 to IC-6 at
`:430-443`, Narrative generation at `:366-392`), [ip-censor-map.md](../docs/architecture/ip-censor-map.md)
(approved 2026-09-19, `:3`), and the nine module specs under
[docs/architecture/ip-censor/](../docs/architecture/ip-censor/). This plan does not reopen any of them.
Where code disagrees with a spec, the disagreement is named in §5 and routed to a task, a gate or a
report line.

---

## 1. What the owner ruled — the input, not reopened here

| Ruling | Content | Where it lands in this plan |
|---|---|---|
| IC-1 | In scope: game and franchise marks, real-person names, company and brand names. Titles out; citations out | T3 (`Category` has three members), T6 (citations are report-only) |
| IC-1b | Display and prose "PvZ" / "Plants vs. Zombies" → "Fusion" on player-facing surfaces; code identifiers untouched. **The rename is the identity-rename program's** | T4 (`pvz` group scoped to `player-name`, `player-prose`); §6 coordination. No rename task here |
| IC-2 | Registry built in two stages: curated dataset import, then census and model proposals confirmed by a person | T8, T9 (tool); T21, T22 (real rounds) |
| IC-3 | The scan is a **release gate**; never blocks generation, a commit, `verify-change.ps1` or CI; CI may run it advisory. Briefs carry a free avoid-list | T11 (advisory CI), T12 (release gate), T14–T16 (avoid-list) |
| IC-4 | Fix both live findings before release: `Overwatch Protocol` via the tree generator's avoid-list and a regenerate; the `Jackson*` family via an authored import-time rename map | T16 (IC-4.1); T17–T20 and T19b (IC-4.2). **No program owned IC-4.2 until now** (`ip-censor-map.md:132` said it "needs an owning task"); this plan owns it, names **and** ids |
| G1 (this plan) | **Answered 2026-09-19: yes, re-key the `Jackson*` species ids too** | T19b — the program's one save migration (backed up, idempotent, one transaction). *Audit 2026-09-19: row added; the answer was recorded only in the todo before.* |
| IC-5 | Registry tracked in the repo | T4 (`gk-data/packs/fusion/data/seed/ip-censor/_registry/`) |
| IC-6 | An alias under 4 characters needs its own narrow scope | T3 |
| R8–R12 | Our own names in narrative; lead names are registry rows in the player-facing scope; new narrative surfaces join scope; prompts never cite other franchises | T4 (rows, surface rules), T15 (uniques brief loses its franchise citation) |

---

## 2. Scope

**In scope.** The independent Python tool `gk-core/tools/ip-censor` (modules `source`, `registry`, `census`,
`scan`, `suggest`, `curate`, `report`), its tracked registry under `gk-data/packs/fusion/data/seed/ip-censor/_registry/`,
its CI and release wiring (`wiring`), the shared seedsmith avoid-list helper (`avoid-list`), and the two
release-blocking fixes IC-4.1 and IC-4.2.

**Out of scope, stated so no task drifts into it.**

- Renaming "PvZ" and the three lead names on shipped surfaces: `identity-rename`
  ([identity-rename-plan.md](identity-rename-plan.md), rules D3 at `:136-156`, tool
  `gk-core/scripts/vocab-rename.py`). This program scans; it never renames those surfaces and builds no second
  rename tool.
- Any "execute" pass over findings (`ip-censor-map.md:15-18`). The plan JSON is the hand-off.
- Code identifiers (`pvz.*`, `drop.pvz.run`, `EmpireId` members, species ids) — with **one** owner-ruled
  exception: the `Jackson*` species ids, re-keyed by T19b (gate G1 answered yes). *Audit 2026-09-19:*
  no other identifier is renamed; `pvz.*` and every identity-rename allow-listed identifier stay.
- A per-change guard (`guard-ip-vocabulary.ps1`). Withdrawn by IC-3 (`ip-censor-map.md:73-74`).
- Legal clearance. The tool screens; a person decides (ideal `:418-419`).

---

## 3. Architecture decisions

### D1 — One independent Python tool, one tracked registry

`gk-core/tools/ip-censor/` mirrors `gk-forge/tools/seedsmith` (package, exact-pinned `pyproject.toml` and
`requirements.lock`, `tests/`, `python -m ipcensor.report <verb>`), per `spec-wiring.md` §Tool shape.
The registry lives in `gk-data/packs/fusion/data/seed/ip-censor/_registry/` (IC-5). `ipcensor` and `seedsmith` share no
code; the seedsmith avoid-list helper reads the registry's **data file** by its versioned shape.

### D2 — Build order is the map's, with `wiring` half 1 first

The map's order is `source → registry → census → scan → suggest → curate → report → wiring`, and
`avoid-list` after the registry file exists (`ip-censor-map.md:113-121`). The map also says
`wiring` "may be built first as a thin lane" because an unverifiable first commit is a blocker
(`:118-120`). So T1 lands `wiring` half 1 (package, lockfile, CI pytest step) with the first code file;
the CI gate and release hooks land after `report` (T11, T12); half 2 lands after its external
dependency (T13).

### D3 — Verification: what `verify-change.ps1` can and cannot select today

Measured on 2026-09-19 with `verify-change.ps1 -PlanOnly -AllowUnscoped`: every one of
`gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/passive-tree/**`, `gk-data/packs/fusion/data/seed/creatures/**` and
`gk-data/packs/fusion/data/generated/creatures/**` throws `VERIFICATION BOUNDARY MISSING` (`scripts/verify-change.ps1:114`);
`gk-core/tools/ip-censor/**` and `gk-data/packs/fusion/data/seed/ip-censor/**` do not exist yet and have no mapping either. **All four
of those paths are mapped as of the addendum 2026-09-22 — see §13; this paragraph is the 2026-09-19
reading, and the mapped list below is the part tasks should follow.** Mapped:
`.github/workflows/**` → `ci-workflows` (`guard.workflows`), `docs/**` → `docs-and-assistant-config`,
`tasks/**` → `session-and-program-records`, `gk-core/src/FusionRpg.Server/**` → `server-fallback`,
`gk-core/src/FusionRpg.Data/**` → `data-fallback`. *Audit 2026-09-19, re-measured:* also mapped are
`gk-core/tests/FusionRpg.Guard.Tests/**` → `guard-tests-fallback`, `gk-core/scripts/enforcement-registry.v1.json` →
`enforcement-registry`, `gk-core/scripts/verification-boundaries.v1.json` → `guard-verification-boundary-tests`;
`scripts/guard-*.ps1` is **not** mapped (T19b runs `guard-dal.ps1`; it never passes it to `-Paths`) —
still true 2026-09-22.

Rules every task follows:

1. Pass **only mapped paths** to `verify-change.ps1 -Paths … -Session <sid>`; run the named focused
   pytest command for the rest. Never compensate with a broad suite (AGENTS.md "Verification boundary").
2. The unmapped paths are boundary defects with named owners, not this program's to patch around:
   `gk-core/tools/ip-censor/**` and `gk-data/packs/fusion/data/seed/ip-censor/**` are closed by **T13** (its dependency has landed —
   §13); `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/generated/**` and `gk-data/packs/fusion/data/seed/**` are **already closed** (TVB3.3,
   TVB4.6, TVB4.7 landed 2026-09-21 — §13), so Phase 5–6 paths select today. Each task's ledger line
   says which of its paths were unmapped.
3. The full suite runs once, at the final checkpoint (the program crosses `tools/`, `data/`,
   `.github/`, and possibly `gk-core/src/FusionRpg.Data`), per AGENTS.md's three named points.

### D4 — The release gate: where it goes and what it runs

`.github/workflows/release.yml` runs on a `v*` tag (`:3-6`). The new step goes **after**
`Unit tests (pre-publish)` (`:40`) and **before** `Prepare injector refs` (*addendum 2026-09-22: now
`:236` — T12's own gate step landed at `:212`, so the two numbers after it moved; this line said
`:59`*), so it precedes `Publish player pack` (*now `:258`; said `:81`*). It
installs the tool from its lockfile (the release job sets up .NET and
Node only, `:26-38`, and uses the runner's Python exactly as `ci.yml` does at `:295-309`), then runs
`python -m ipcensor.report scan --format json --fail-on enforced --authored-only`. *Audit 2026-09-19:* the install runs
with `working-directory: gk-core/tools/ip-censor`, the **scan** runs from the repository root, and `report`
resolves the scanned tree from `git rev-parse --show-toplevel` (never the working directory), because
`git ls-files` run inside `gk-core/tools/ip-censor` would enumerate only that folder and the gate would pass
vacuously (T10 acceptance). Every command is followed by
`if ($LASTEXITCODE -ne 0) { throw … }`, the form `WorkflowExitCheckTests` checks
(`gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs:24-26`). That guard only recognises test
command prefixes (`:17-22`), so T12 adds the scan command as a recognised prefix; otherwise nothing
would catch a later edit that drops the check.

The release checklist gains one line under "Before tagging" (`docs/runbook/release-prove.md:5`).
The gate needs no model and no network, and it is `--authored-only` that makes that true: without the
flag `gk-core/tools/ip-censor/ipcensor/cli.py:154-160` builds the LLM proposer and `suggest` asks it once per
mark with no authored replacement pair (*erratum 2026-09-23, ip-censor T12 — the command line here
omitted the flag while this same paragraph claimed the property*).

### D5 — The day-one registry holds only rows the owner has already confirmed

T4 ships the rows whose confirmation is on record: `pvz` (IC-1b), `crazy-dave`, `penny`, `dr-zomboss`
(R8, R9, R11), and `overwatch` (IC-4). Each carries `stage: "reconfirm"`, `evidence: "census"`, the
ideal's measured census as `source`, and `confirmedBy: "owner"` with the ruling date. Every other mark
(Diablo, the real-person `jackson` row, anything from the dataset) enters through `curate` with a
person's decision (T21, T22). No row is admitted on this plan's judgement. Consequence, stated: until
T22 admits a `diablo` row, the release scan does not report
`gk-forge/tools/seedsmith/seedsmith/adapters/items/uniques/briefs.py:284` (*addendum 2026-09-22: this line said
`:267`; the `Diablo-style` string is now `:284`*); T15 removes that citation anyway.

### D6 — IC-4.1 needs a one-node selector on the tree generator

`trees generate --write --supersede` re-generates **every** ledger row whose `promptVersion` differs
from the current `PROMPT_VERSION` (*addendum 2026-09-22: the decision point is
`gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py:421` — `if subject_id in duplicate_ids or
(supersede_stale and _stale(entry))`; the CLI flag is `report/cli.py:3739-3742` and its call site
`:2428`. This line cited `report/cli.py:3019-3024`, which now holds the creature-anchor pipeline*). Bumping
`PROMPT_VERSION` (`adapters/trees/nodegen/brief.py:57`) and running `--tree command --supersede` would
therefore re-roll the whole `command` tree, not the one node the spec names. T16 adds a `--node <id>`
selector to `trees generate` (a generator change, the sanctioned route) so only
`skill.command-def-t8-n0` regenerates. Other nodes keep `tree-language/3`; mixed vintages already
coexist by design (`gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/brief.py:55-56`). The generator change, the regenerated `command.json` and the ledger
(`gk-data/packs/fusion/data/seed/passive-tree/_runs/tree-language.ledger.json:28510-28511`) land in **one** commit: that
is the generated-seed rule's "change the generator, regenerate, commit the diff".

### D7 — IC-4.2: trace first, one authored rename map, applied at import; species ids re-keyed (G1 = yes, T19b)

Verified against code on 2026-09-19:

- The species ids are the host game's own type names: `gk-data/packs/fusion/data/seed/creatures/_dump/almanac/zombie.json:225`
  (`"typeName": "JacksonZombie"`), carried into species rows with `"gameTypeId": 10`.
- Upstream prose names the real person: the same dump's flavor text at `:134` and `:218`
  ("Michael Jackson"), and the almanac export at
  `gk-data/packs/fusion/data/seed/external-reference/almanac-enrichment/pvz-fusion-almanac-3.6.1.json:5247,5677,5772`.
- The dump's flavor text enters seedsmith's creature adapters
  (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/family/extract.py:61-65`, `generate_motifs.py:45`,
  `generate_themes.py:94`); that is where the trait `moonwalking`
  (`gk-data/packs/fusion/data/seed/creatures/species/zombie/performer-undead.json:80`) was derived.
- The almanac export enters the server only through the admin endpoint `POST /api/almanac/seed/enrich`
  (`gk-core/src/FusionRpg.Server/Program.cs:1423-1445`), which calls
  `RpgStore.ImportAlmanacEnrichment` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AlmanacSeedEnrichment.cs:36`).
  That import matches rows by name and stores enrichment text; species display names come from the
  game's `types` table (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AlmanacSeed.cs:474`).
- Species ids are persisted (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Creatures.cs:73`) and shown
  (`gk-web/web/fusion-rpg-web/src/features/aptitudes/AptitudePresetConsoleHost.tsx:138`), and `Jackson`
  appears in about 900 lines under `data/**` (a reading).

So the fix has two separable halves. **Names and prose** that reach a player are fixed by an authored
map, `data/seed/ip-censor/_registry/import-renames.v1.json`, applied where upstream text enters the
corpus, then the derived trees regenerate (T17–T20). The map must sit in `self_paths` class 1 because
its keys are the real names. **Re-keying species ids** is a persisted-identity change across saves, and
the ids are the host game's own identifiers (the RPG-layer rule: we observe PvZ, we do not rewrite it).
The map's done-when names both halves (`ip-censor-map.md:132`). *Audit 2026-09-19:* the id half was gate
G1 (§7); the owner answered **yes**, so the id half is task **T19b**. It keeps the RPG-layer rule by
re-keying only **our** species rows and saves: the host's `types.type_name` and each row's
`gameTypeId` are read, never written, and remain the link to the game entity. The seed-side ids are
generated rows (`species/zombie/undead.json` carries `_provenance`), so they change through the
generators reading the map's `ids` section, never a JSON edit; the save side changes through one
`FusionRpg.Data` migration on the `Migrations/ShardRungs.cs` precedent (idempotent re-key inside
`RpgStore.Init`) with a backup on the `LegacyMonoMigrator.cs` precedent (`BakSuffix`, copy once).

### D8 — Remediation is derived from the provenance shapes that actually exist

`spec-registry.md` §remediation derives `generator-owned` from `_meta.model` / `promptVersion` /
`batch`. The files this program must classify use other shapes: `command.json` has a top-level
`_provenance` with `promptVersion` and `model` (`gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:2-5`) and a
per-node `promptVersion` (`:542`); species files are arrays with a per-row `_provenance`. T4's
derivation recognises all three shapes, each with a fixture. A related defect outside this program's
paths is reported, not fixed: `guard-generated-seed.py` inspects only a top-level `_meta`
(`gk-core/scripts/guard-generated-seed.py:117-124`), so it never sees a hand edit to `command.json` or a
species file.

### D9 — Self-exclusion covers this plan pair

`self_paths` class 2 lists the program's docs, and class 3 is `tasks/ip-censor/**`
(`spec-registry.md` §self_paths). This plan and its todo are `tasks/ip-censor-plan.md` and
`tasks/ip-censor-todo.md`, which class 3 does not match (hyphen, not slash) and which name marks. T4
adds both to class 2.

### D10 — The surface classifier is path-based; mixed code files are not player surfaces (audit 2026-09-19)

*Audit 2026-09-19 (HIGH, cross-plan).* The classifier maps a **path** to a surface (`spec-census.md`
§Open Questions 1, `spec-registry.md` §Categories). identity-rename keeps identifiers such as
`WorldFactionKind.Zomboss`, `EmpireId.Dave` and `commander:dave` in the **same files** whose display
literals it renames (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:78,83`). A path rule cannot
split one file, so either the gate never goes green (identifiers enforced forever, owned by nobody) or
it misses the literals. Resolution, applied in T4: source-code roots (`src/**`, `web/**/src/**/*.ts(x)`,
`tests/**`, `tools/**` except `gk-forge/tools/seedsmith/**`, which stays the enforced `generator-prompt` surface) classify as `code-identifier`; only pure display
files are player surfaces (`*.po` catalogs, `docs/guide/**`, the display registries under
`gk-data/packs/fusion/data/seed/**/_registry/**`, `gk-data/packs/fusion/data/seed/narrative/**`, rendered site pages). Player literals inside
code are identity-rename's to prove (its tool `check` and `vocabularyGuard.ts`, identity-rename T18),
not this gate's. T4 pins the contract with a fixture: every identity-rename allow-list form yields no
enforced finding. Checkpoint 3 then requires every enforced finding to name its owning task.

---

## 4. Phases and task index

Full detail, acceptance criteria and verification: [ip-censor-todo.md](ip-censor-todo.md). One task =
one commit (code, tests, evidence and the todo ledger line together), explicit paths, no push.

**Phase 0 — Boundary**
- T0 Session record

**Phase 1 — Foundation (`wiring` half 1, `source`, `registry`)**
- T1 Tool package, lockfile, wiring test, CI pytest step
- T2 `source`
- T3 `registry` parser
- T4 Shipped registry files, surface classifier, remediation derivation
- **Checkpoint 1**

**Phase 2 — Readings (`census`, `scan`, `suggest`)**
- T5 `census`
- T6 `scan`
- T7 `suggest` and the tool's one LLM client
- **Checkpoint 2**

**Phase 3 — Curation and composition (`curate`, `report`)**
- T8 `curate import` and the USPTO adapter
- T9 `curate reconfirm` and `curate admit`
- T10 `report`: composition root, CLI, plan and report writers
- **Checkpoint 3** (first real plan and report)

**Phase 4 — Gate wiring (`wiring`)**
- T11 Advisory CI scan
- T12 Release gate step, checklist line, exit-check guard, enforcement row
- T13 `wiring` half 2: the `ipcensor` pytest lane (after TVB3.1/TVB3.2)
- **Checkpoint 4**

**Phase 5 — Avoid-list and IC-4.1 (may start after T4)**
- T14 `seedsmith.briefkit.avoid_list`
- T15 Uniques brief adopts the avoid line and drops its franchise citation
- T16 Tree brief adopts the avoid line, `--node` selector, regenerate the `Overwatch Protocol` node
- **Checkpoint 5**

**Phase 6 — IC-4.2 `Jackson*` (may start after T5)**
- T17 Trace every entry point and player-visible surface
- T18 The authored rename map, its validation and its seedsmith reader
- T19 Apply the map in the creature adapters; regenerate the derived trees
- T19b Re-key the `Jackson*` species ids (G1 answered yes): generator `ids` section, regenerate, one
  backed-up idempotent store migration (*audit 2026-09-19: added to the index*)
- T20 Apply the map on the server import path (conditional on T17)
- **Checkpoint 6**

**Phase 7 — Registry content, with the owner**
- T21 First dataset import round
- T22 First reconfirm round (census, model proposals, identity-rename hand-off)

**Phase 8 — Release readiness**
- T23 Release-gate reading, residue list, full suite
- **Final checkpoint**

25 tasks (T0–T23 plus T19b), 7 checkpoints, 1 gate (G1, **answered yes 2026-09-19**; it adds T19b and
blocks nothing else). *Audit 2026-09-19: count corrected.*

**Parallel work.** After Checkpoint 1: Phase 2–3 (`gk-core/tools/ip-censor`), Phase 5 (`gk-forge/tools/seedsmith`) and
T17 (read-only trace) touch disjoint files. T13 waits on another program. Phase 7 waits on owner
decisions per candidate file, not on code.

---

## 5. Findings from verification that change a task

| Finding | Evidence | Task |
|---|---|---|
| `--supersede` re-rolls a whole tree, not one node | `nodegen/run.py:421` (*addendum 2026-09-22: re-pointed from `report/cli.py:3019-3024`*) | T16 adds `--node` |
| Remediation provenance shapes differ from the spec's list | `command.json:2-5,542`; species rows' per-row `_provenance` | T4 (D8) |
| `guard-generated-seed.py` reads only top-level `_meta` | `gk-core/scripts/guard-generated-seed.py:117-124` | Reported in T4's ledger line; not fixed here |
| Species ids are the host game's persisted type names | `_dump/almanac/zombie.json:225`; `RpgStore.Creatures.cs:73` | Gate G1 (D7) → answered yes → T19b |
| *Audit 2026-09-19:* species ids sit in several save tables (`creature_species` `RpgStore.Species.cs:34`, `player_species` `RpgStore.PlayerSpecies.cs:47`, `rpg_species_respec` `RpgStore.SpeciesRespec.cs:36`, `RpgStore.World.cs:126`, `rpg_creature_profiles`/`rpg_creature_codex` `RpgStore.cs:612,626`, …) | `git grep "species_id TEXT" -- gk-core/src/FusionRpg.Data` | T19b enumerates them from the live schema, not from this list |
| *Audit 2026-09-19:* a path-based classifier cannot split a file holding both a kept identifier and a renamed literal | `WorldTemplateCatalog.cs:78,83` | D10, T4 |
| The almanac import is an admin endpoint, not a boot step, and stores enrichment only | `gk-core/src/FusionRpg.Server/Program.cs:1423-1445`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AlmanacSeedEnrichment.cs:36` | T17 decides whether T20 is needed |
| The release job has no Python setup | `release.yml:26-38` | T12 installs from the lockfile in its own step |
| `WorkflowExitCheckTests` does not recognise a non-test command | `WorkflowExitCheckTests.cs:17-22` | T12 extends the prefix list |
| This plan pair is outside every `self_paths` class | `spec-registry.md` §self_paths | T4 (D9) |
| The Overwatch mark also sits in the generator ledger | `tree-language.ledger.json:28510-28511` | T16 commits the ledger with the row |
| The registry is at `schemaVersion` 2, not the 1 `spec-wiring.md` recorded | `scripts/verify-change.ps1:28` refuses anything but 2 | T13 targets whatever schema TVB3.1 publishes (4 per its spec) |

---

## 6. Coordination with other programs

| Program | Relationship | Contract |
|---|---|---|
| `identity-rename` ([plan](identity-rename-plan.md)) | **It renames; this program scans.** Its phases 3–4 (`identity-rename-plan.md` §6) rename the leads and "PvZ" on player-facing surfaces with `gk-core/scripts/vocab-rename.py` (its D3). Its T18 hands this program candidate alias rows (`identity-rename-todo.md:296-297`, hand-off section `:322-324`) | T4 ships the four identity rows already owner-confirmed, so the release gate reports every unrenamed player-facing hit from the day T12 lands. That red release gate is the gate working, not a defect. T22 admits the hand-off rows through `curate admit`. Neither program writes the other's files. *Audit 2026-09-19 — migrations, exactly one owner each:* this program owns the **only** save migration of either plan (T19b, `Jackson*` species ids). identity-rename owns **none**: its G1 was answered "no migration of names stored in saves" (`players.name` and stored faction names keep their text). T19b never touches a name column; identity-rename never touches a species id. Classifier contract: every identity-rename allow-listed identifier is non-enforced here (D10) |
| `narrative-seed` ([map](../docs/architecture/narrative-seed-map.md)) | Consumer of the avoid-list helper: module 15 `lore-packet` puts "the free IP avoid-list rendered from the `ip-censor` registry" into every call's packet (`narrative-seed-map.md` module table, row 15); a soft edge, empty until the registry exists (same row). *Audit 2026-09-19: the line citations `:214`, `:277-278` drifted after the round-3 amendment; cited by row* | The consumer API is `load_avoid_terms()` and `render_avoid_line()` in `gk-forge/tools/seedsmith/seedsmith/briefkit/avoid_list.py` (T14), reading `gk-data/packs/fusion/data/seed/ip-censor/_registry/marks.v1.json` `schemaVersion` 1. A breaking change publishes `marks.v2.json` and moves every reader in the same change. The names registry `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json` is scanned as a `player-name` surface by a `scope-policy.v1.json` path rule (T4) |
| `test-verification-boundary` (lane D, `cmdc/lane-d`, worktree) | Owned TVB3.1/TVB3.2 (the pytest runner) that `wiring` half 2 consumes, and TVB3.3/TVB4.6/TVB4.7 that mapped seedsmith and `data/**` | **Closed as of the addendum 2026-09-22** — TVB3.1/TVB3.2 landed (`test-verification-boundary-todo.md:135,139`), so T13 starts with no external wait; TVB3.3/TVB4.6/TVB4.7 also landed (`:144,209,212`), so Phase 5–6 paths select locally |
| `keepverse-split` (direct) | Its public snapshot KS7.3 requires an "ip-censor guard clean" tree (`tasks/keepverse-split-todo.md:151`; `decisions.md` — 'Repository topology — Keepverse split (2026-09-19)') | Same command as the release gate: `scan --fail-on enforced`. If migration gate GM opens before this program closes, unfinished tasks retarget paths; no task depends on a path the move renames |

---

## 7. Gates

| Gate | Blocks | Why it is a gate | Resolver | Default if unanswered |
|---|---|---|---|---|
| **G1** Re-key the `Jackson*` species ids (`JacksonZombie`, `Jackson_a`, …) — **answered 2026-09-19: YES, rename the ids too** | Nothing else. The yes adds task **T19b** after T19 (`tasks/ip-censor-todo.md` Phase 6) | Species ids are persisted in the owner's real save (`RpgStore.Creatures.cs:73`) and are the host game's own type names (`_dump/almanac/zombie.json:225`); re-keying stored rows cannot be undone without a backup | Owner | ~~No re-key~~ — *Audit 2026-09-19: superseded by the answer.* T19b ships the re-key; its migration refuses to run without a backup, so the irreversible step keeps its safety net |

There are no other gates. Owner decisions on curate candidate rows (T21, T22) and on the replacement
strings in the rename map (T18) are ordinary review inputs: each has the owner as resolver, and each
default is stated in its task.

---

## 8. Shared files — active sessions and the clean-or-skip rule

Read from `tasks/sessions/*.json` on 2026-09-19, **active records only**. A **worktree** lane meets
this program only at its merge; a **direct** session shares this working tree.

| File(s) this plan edits | Also claimed by | Mode |
|---|---|---|
| `.github/workflows/ci.yml` | `summoner-convergence-lane-c` (`.github/workflows/ci.yml`), `summoner-convergence-lane-d` (`.github/workflows/**`) | worktree |
| `.github/workflows/release.yml` | lane D | worktree |
| `gk-forge/tools/seedsmith/**` (briefkit, trees and uniques adapters, creature adapters, `report/cli.py`) | lanes B (`tools/**`), C (`gk-forge/tools/seedsmith/**`), D (`tools/**`); `keepverse-split` claims only `gk-forge/tools/seedsmith/seedsmith/workspace_roots.py` | worktree; direct (one file, not edited here) |
| `gk-data/packs/fusion/data/seed/passive-tree/**`, `gk-data/packs/fusion/data/seed/creatures/**`, `gk-data/packs/fusion/data/generated/creatures/**` | lanes C (`gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`), D (`data/**`) | worktree |
| `gk-core/scripts/verification-boundaries.v1.json` (T13) | `keepverse-split`; lanes A2, B, C, D | direct; worktrees |
| `gk-core/scripts/enforcement-registry.v1.json` (T12) | lanes B, D | worktree |
| `gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs` (T12) | lanes B, C (`gk-core/tests/FusionRpg.Guard.Tests/**`), D (`tests/**`) | worktree |
| `docs/runbook/release-prove.md` (T12) | lanes B, D (`docs/**`) | worktree |
| `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/src/FusionRpg.Data/Sqlite/**` (T20, conditional) | lanes A2 (`Program.cs`), B, C | worktree |
| *Audit 2026-09-19:* `gk-core/src/FusionRpg.Data/Sqlite/Migrations/**`, `RpgStore.cs` (the `Init` call site), `gk-core/tests/FusionRpg.Data.Tests/**`, `gk-forge/tools/CreatureSpeciesGen/**`, `gk-forge/tools/CreatureBuildPlanGen/**` and the regenerated `gk-data/packs/fusion/data/seed/creatures/**`, `gk-data/packs/fusion/data/generated/creatures/**` (T19b) | lanes B, C, D (broad globs); identity-rename T13 edits `RpgStore.cs:4032` (a different region) | worktree; direct — region check per step 2 below |
| `tasks/ip-censor-plan.md`, `tasks/ip-censor-todo.md` | `narrative-programs-spec2-20260919` (this plan's author, direct) | direct; the implementing session claims them at T0 |
| `gk-core/tools/ip-censor/**`, `gk-data/packs/fusion/data/seed/ip-censor/**`, `tasks/ip-censor/**` | nobody | — |

**Clean-or-skip, for every shared file, before the edit:**

1. `git status --porcelain -- <file>` is empty. If the file is dirty (another direct session's
   uncommitted work), **skip it**: commit the task's other files only if they stand alone, otherwise
   defer the whole task, and record the skip in the ledger.
2. For each worktree lane that claims it, `git diff $(git merge-base HEAD <branch>)..<branch> -- <file>`
   does not touch the region being edited (`session-boundary.md` §5). A region overlap is resolved with
   the owner; a different region merges cleanly.
3. **Never** `git stash`, `git checkout -- <file>` or `git reset` around another session's work, and
   never `git add -A`.

---

## 9. Release readiness — what "ready" means for this program

All four, recorded at T23:

1. `python -m ipcensor.report scan --fail-on enforced` exits 0 on the release commit (an operational
   result, never a suite assertion — ideal principle 3, `ip-censor-ideal.md:48-52`).
2. IC-4.1: the regenerated node carries the new `promptVersion` and the scan reports no `overwatch`
   finding under `gk-data/packs/fusion/data/seed/passive-tree/**` (T16).
3. IC-4.2: T19's import-output test is green **and** T19b's migration and id-closure tests are green
   (G1 answered yes). *Audit 2026-09-19: was "G1's answer is recorded", which the yes made insufficient.*
4. The release workflow runs the gate before publishing (T12).

Item 1 also depends on identity-rename finishing its Phases 3–4 and on `curate` rounds admitting any
further marks; T23 lists what still blocks rather than waiting.

---

## 10. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| A short or common alias floods the scan (the measured `wow` case, ideal `:256-258`) | High: the tool gets ignored | IC-6 enforced by the parser (T3); every admitted row passes through a person (T9); the advisory CI report shows the reading before any release |
| The regenerated `command` node picks another third-party name | Medium: IC-4.1 not closed | The avoid-list covers registry marks only, so T16 runs the scan on the output before committing; a new hit is added through `curate` and the node regenerates again |
| The local model endpoint is not running when T16 or T19 needs it | Low: those tasks wait | Named environment dependency, not a gate; every other task continues |
| A rename-map replacement string is invented by a tool | High: principle 4 violation | `suggest` proposals carry `proposed — needs owner confirm`; T18's parser refuses a pair without `confirmedBy` |
| The registry file shape drifts under the seedsmith reader | Medium: briefs silently lose the list | The helper throws on any unknown shape (T14); versioned file name |
| A lane merge rewrites `ci.yml` or `release.yml` around the new steps | Medium | Region check before the edit (§8); `WorkflowExitCheckTests` keeps the exit checks honest |
| *Audit 2026-09-19:* T19b's re-key misses a table or a JSON-in-TEXT column that embeds a species id, orphaning owned creatures | High: silent loss in the owner's save | The id-closure check sweeps **every** text column of the live schema for an old id (a contract over the id set, not a table list), and the migration refuses without a backup |

---

## 11. External dependencies

| Dependency | Needed by | Status 2026-09-22 (addendum) | If not ready |
|---|---|---|---|
| TVB3.1 + TVB3.2 (pytest runner lane) | T13 only | **LANDED** — `tasks/test-verification-boundary-todo.md:135,139` both `[x]`; the registry carries `pytest` runner projects (`seedsmith`, `tuning-py`) at `gk-core/scripts/verification-boundaries.v1.json:68,72`. T13's dependency is satisfied and **T13 no longer waits** | — |
| TVB3.3, TVB4.6, TVB4.7 (seedsmith and `data/**` mapping) | Local selection for Phase 5–6 paths | **LANDED 2026-09-21** — `test-verification-boundary-todo.md:144,209,212` all `[x]` (TVB4.7: 38 new boundaries, 293 → 331; every one of the 2176 files under `gk-data/packs/fusion/data/seed/**` resolves) | — |
| identity-rename Phases 3–4 | Release readiness item 1 | **Approved 2026-09-22, ready for lanes** (`identity-rename-plan.md` status line; its premises verified clean) | The gate reports the remaining hits; T23 lists them |
| USPTO trademark bulk export (not committed) | T21 | Not downloaded | T8 is built and tested on fixtures; T21 waits for the export |
| Local LLM endpoint (`IPCENSOR_LLM_*`, seedsmith's own for regeneration) | T16, T19, T22's model half | Machine-local | `curate reconfirm --no-model` and `suggest --authored-only` need none |

---

## 12. DESIGN-GATE §5 checklist

```
[x] Subsystems: a new offline Python tool; seedsmith briefkit, passive-tree and creature adapters;
    CI and release workflows; the almanac import path (read, possibly T20).
[ ] Session boundary recorded: NOT for implementation. This plan was written under
    narrative-programs-spec2-20260919, whose paths include only the two plan files. The implementing
    session records its own boundary at T0.
[x] Read this session: ip-censor ideal (rulings, Narrative generation), map, all nine module specs,
    identity-rename plan and todo T18, narrative-seed map (§4 rows 9/15, §5, §7), session-boundary.md,
    agent-git.md, testing-standard.md, AGENTS.md verification boundary, the plan skill and command.
[x] decisions.md checked: no lock covers the IP gate; row :143 (Keepverse) consumes it (§6).
[x] Every factual claim cites file:line.
[x] audit-doc-citations run on this file (result in the hand-off).
[x] Verified against code: release.yml, ci.yml, WorkflowExitCheckTests, verify-change.ps1 and the
    boundary registry (-PlanOnly per path), guard-generated-seed.py, command.json and its ledger,
    nodegen brief/run/cli, uniques briefs, the creature dump, species rows, the almanac import.
[x] Surrounding sections read for every quoted rule (IC rulings table, map Release-blocking fixes,
    spec-wiring release hook, spec-avoid-list IC-4 fix).
[ ] Constraints tested: the --write precondition of `trees generate` (one PassiveTree/* gates=True
    metric) is NOT run here; T16's first step runs --dry-run and reports it.
[x] No §2 invariant contradicted: no composer, no Funnel/Writer change, no magnitude. G1 existed
    because re-keying species ids touches persisted saves; answered yes, T19b re-keys only our rows
    and never writes the host's `types` table or `gameTypeId` (audit 2026-09-19).
[x] No assertion pins a population: tests pin the registry's closed vocabularies (Category, Surface,
    Remediation, Stage, Evidence, Bucket) and fixture contents; hit counts are readings.
[x] No event-refreshed cache introduced.
[x] No ordering assumption in play; outputs are sorted by construction.
[x] No ActorHub or combat magnitude involved.
[x] No SOLID-violating parallel path: one registry, one avoid-list helper, one LLM client, one
    rename tool (identity-rename's) — this program adds no second one.
[x] New rule has a registry row: T12 adds the release-gate invariant to enforcement-registry.v1.json.
```

---

## Standards audit (2026-09-19)

Independent adversarial audit against the owner rulings (ideal IC-1 to IC-6, G1 = yes; npc-story-events
§10 R8–R12), the planning standard (`.claude/commands/plan.md`, `planning-and-task-breakdown`),
`agent-git.md`, `session-boundary.md`, the AGENTS.md verification boundary and `testing-standard.md`.
Fixed items are marked *Audit 2026-09-19* in place.

| # | Severity | Finding | Status |
|---|---|---|---|
| A1 | HIGH | G1 was answered **yes** but §4 (index, count), D7, §7 (default "no re-key"), §9 item 3 and the todo's T19/CP6/Final/Gate still carried the no-re-key default; T19b was absent from the index | Fixed: §1 row, §2, D7, §4, §7, §9, §12; todo re-sequenced |
| A2 | HIGH | T19b (todo) lacked files, an exact verify command with `-Session`, a commit message and a checkbox; it did not route the seed-side id change through the generators (the ids are generated rows) and did not say how an in-memory test proves a backup | Fixed in the todo (T19b rewritten in place in Phase 6) |
| A3 | HIGH | Cross-plan: the path-based surface classifier cannot split files that hold both identity-rename's kept identifiers and its renamed literals, so the release gate could never go green, or misses literals | Fixed: D10, T4 acceptance, CP3 owner check |
| A4 | MEDIUM | The scan steps (T11, T12) ran with `working-directory: gk-core/tools/ip-censor`; `git ls-files` there enumerates only the tool — a vacuous pass | Fixed: D4, T10/T11/T12 acceptance (root from `git rev-parse --show-toplevel`) |
| A5 | MEDIUM | Migration ownership between the two plans was implicit | Fixed: §6 identity-rename row (T19b is the only save migration; identity-rename owns none) |
| A6 | MEDIUM | Citation drift: `verify-change.ps1:95` (now `:118`), `ci.yml:284-298`/`:300-306` (now `:295-309`/`:311-317`), `keepverse-split-todo.md:129` KS6.3 (now `:151` KS7.3), `identity-rename-plan.md:136-176` (D3, not phases), `narrative-seed-map.md:214,277-278` | Fixed |
| A7 | LOW | D3's mapped list omitted `guard-tests-fallback` and `enforcement-registry`; `scripts/guard-*.ps1` is unmapped | Fixed (D3) |
| A8 | LOW | The lead-name replacement pairs live in three files (`replacements.v1.json`, identity-rename's rules file, the names registry) | Deferred: `replacements.v1.json` only feeds `suggest` proposals, so drift yields a wrong suggestion, not a wrong rename; a consistency check would couple two programs before the names registry exists. Revisit at T22 |
| A9 | LOW | The ideal's IC-4 row still says the `Jackson*` fix is "an authored import-time rename map" only | Deferred: the ideal is not in this audit's edit set; the map and plan now record G1 = yes |

Verified against code this session (sample): `release.yml` step names and lines `:3-6,:26,:33,:40,:59,:81`;
`WorkflowExitCheckTests.cs:17-22,24-26`; `command.json:538,542`; `brief.py:57,114,157`; `run.py:462,665`;
`cli.py:2985,3019`; `uniques/briefs.py:267`; `zombie.json:134,218,225`; `gk-data/packs/fusion/data/seed/creatures/species/_index.json:382-387`
(*addendum 2026-09-22: this line cited a bare `_index.json`, which resolves to none of the eight tracked
files of that name — the Jackson id map is the species index, at those lines*);
`RpgStore.Creatures.cs:73`; `Program.cs:1423,1426`; `RpgStore.AlmanacSeedEnrichment.cs:36`;
`RpgStore.AlmanacSeed.cs:474`; `enforcement-registry.v1.json` row shape (`id`, `source`, `guards`,
`unguardableReason`). Boundary mappings re-measured with `verify-change.ps1 -PlanOnly -AllowUnscoped`.

**Proposed enforcement-registry rows** (the implementing session adds them in the named task; this audit
edits no shared file):

- `ip-release-gate` — source `docs/architecture/ip-censor-map.md` (release gate); `guards: []`;
  `unguardableReason`: "enforced by the release.yml step and guard.workflows' exit-check prefix, not a
  per-change guard (IC-3)" — T12.
- `species-id-rekey-in-data` — source `tasks/ip-censor-plan.md` D7; `guards: ["dal"]` (the SQL stays in
  `FusionRpg.Data`) — T19b.
- `save-migration-backup-first` — source `tasks/ip-censor-plan.md` D7; `guards: []`;
  `unguardableReason`: "no scan can prove a migration takes a backup before it writes; T19b's test does"
  — T19b.

**Verification-boundary asks** (reported, not worked around): `gk-core/tools/ip-censor/**`,
`gk-data/packs/fusion/data/seed/ip-censor/**` (T13, after TVB3.1/3.2); `gk-forge/tools/seedsmith/**` (TVB3.3); `gk-data/packs/fusion/data/seed/**` incl.
`creatures/**`, `passive-tree/**` (TVB4.7); `gk-data/packs/fusion/data/generated/**` (TVB4.6); `scripts/guard-*.ps1`
(no owner row — whoever owns the guard scripts).

---

## 13. Addendum (2026-09-22) — premise verification against the convergence head

Verified at `15baa1454` (worktree `cmdc-arch-d`, session `arch-d-20260922`) before the status line moved to
"approved, ready for lanes". Nothing here reopens a ruling or a module spec; it records what holds, what
moved, and the one dependency that closed.

### Verified clean — no task changes

| Premise | Evidence at this head |
|---|---|
| The tool and its registry do not exist (T1–T23 all unstarted) | `gk-core/tools/ip-censor/` absent; `gk-data/packs/fusion/data/seed/ip-censor/` absent; all nine specs present under `docs/architecture/ip-censor/`; map approved at `ip-censor-map.md:3` |
| IC-4.1's mark is still live (T16's premise) | `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538` `"name": "Overwatch Protocol"`, `:539` its `nameKey`; the ledger row at `_runs/tree-language.ledger.json:28510-28511` |
| IC-4.2's chain (T17–T20) | `_dump/almanac/zombie.json:225` `"typeName": "JacksonZombie"`; the real-person prose at `:134` and `:218`; the derived trait `"moonwalking"` at `species/zombie/performer-undead.json:80`; species ids persisted at `RpgStore.Creatures.cs:73` |
| Species ids live in several tables (T19b) | `git grep -c "species_id TEXT" -- gk-core/src/FusionRpg.Data` → `RpgStore.Species.cs` 2, `RpgStore.PlayerSpecies.cs` 1, `RpgStore.World.cs` 1, `RpgStore.cs` 2 — T19b still enumerates from the live schema, as it says |
| T16 still needs `--node` | no `"--node"` CLI flag exists anywhere under `gk-forge/tools/seedsmith/`; `--supersede` is `report/cli.py:3739-3742`, consumed at `:2428` |
| `PROMPT_VERSION` vintage rule | `adapters/trees/nodegen/brief.py:57` is `PROMPT_VERSION = "tree-language/3"`; the mixed-vintage comment is `:55-56` |
| T12's guard shape | `WorkflowExitCheckTests.cs:17-22` is `TestCommandPrefixes` (three dotnet/pytest/sharded prefixes — the scan command is still unrecognised); `:24-26` is the `$LASTEXITCODE` regex |
| `guard-generated-seed.py` reads only top-level `_meta` | `gk-core/scripts/guard-generated-seed.py:117-121` — `$meta = $doc._meta`, then only `model`/`promptVersion`/`batch` |
| D3's mapped list | re-measured: `.github/workflows/**` → `ci-workflows`; `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json` → `seed-passive-tree-corpus` + `gen-passive-tree` + `generated-seed`; `gk-core/scripts/enforcement-registry.v1.json` → `enforcement-registry`; `gk-core/tests/FusionRpg.Guard.Tests/**` → `guard-tests-fallback` |
| `scripts/guard-*.ps1` is **not** mapped | `scripts/guard-dal.ps1` → `VERIFICATION BOUNDARY MISSING` (T19b's decision to run it outside `-Paths` still holds) |

### Drift — citations only, except one dependency that closed

| Cited as | At this head | Effect |
|---|---|---|
| `report/cli.py:3019-3024` — the `--supersede` staleness rule (D6, §5) | the decision is `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py:421`; `report/cli.py:3019-3024` now holds the creature-anchor pipeline | D6's **substance is unchanged** (still a whole-tree re-roll, still no `--node`); only the anchor moved — re-pointed in D6 and §5 |
| `uniques/briefs.py:267` — the franchise citation (D5) | `:284` (`"You author identity for a Diablo-style unique item …"`) | **`overwatch` is not in any seedsmith `.py`** at this head; the mark lives only in the tree node and ledger, which is what T16 regenerates. D5's sentence holds; the anchor is re-pointed |
| `release.yml` — `Prepare injector refs` `:59`, `Publish player pack` `:81` (D4) | `:155` and `:177`; `Unit tests (pre-publish)` is still `:40`; `.NET`/`Node` setup still `:26`/`:33` | the **insertion window is unchanged** (after `:40`, before `:155`); re-pointed in D4 |
| `scripts/verify-change.ps1:118` (D3, todo) | `:114` | re-pointed |
| `tasks/test-verification-boundary-todo.md:182,267,273` for TVB3.3/4.6/4.7 | TVB3.3 `:144`, TVB4.6 `:209`, TVB4.7 `:212` — all `[x]` | see below |

### The one substantive change: the external dependency closed

**TVB3.1 and TVB3.2 landed** (`tasks/test-verification-boundary-todo.md:135,139`, both `[x]`), and the
registry now carries Python runner projects (`gk-forge/tools/seedsmith` → `pytest` at
`gk-core/scripts/verification-boundaries.v1.json:68-71`, `gk-core/tools/tuning` at `:72-76`). **T13's stated wait is
satisfied: T13 can start now and is no longer on a dependency.** TVB3.3, TVB4.6 and TVB4.7 also landed
2026-09-21 (`:144,209,212`; TVB4.7 added 38 boundaries, 293 → 331, and every file under `gk-data/packs/fusion/data/seed/**`
resolves), so:

- D3's claim that `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/passive-tree/**`, `gk-data/packs/fusion/data/seed/creatures/**` and
  `gk-data/packs/fusion/data/generated/creatures/**` throw `VERIFICATION BOUNDARY MISSING` is **stale** — all four now resolve
  (`seedsmith-trees` focused + the `seedsmith` pytest lane; `seed-passive-tree-corpus`;
  `seed-creatures-corpus` + three seams; `gen-build-plan-data`). Phase 5–6 tasks may pass these paths to
  `verify-change.ps1` today; where a task still names a focused pytest command, that is now a choice, not a
  forced workaround.
- §11's two "Unbuilt" rows are superseded and the table is re-pointed above.
- `tasks/ip-censor-todo.md`'s header still lists the old unmapped set; the todo's pointer to §13 covers it.

### Not re-measured here

The 2026-09-19 census figures in D5 and the ideal are readings that T5/T21/T22 re-measure. The `Jackson`
line count under `data/**` (about 900) is a reading, never an assertion. T16's `--write` precondition and
T19b's migration are still their own first steps.

### Verdict

Premises hold; the tool, its registry and its tests are all still to be written. Three anchors moved and are
re-pointed above; one external dependency (the pytest lane) closed and removes T13's wait. **Status set to
"approved 2026-09-22, ready for lanes".**
