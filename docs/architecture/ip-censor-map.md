# Capability map: ip-censor

**Status: spec phase, written 2026-09-19. Map approved by the owner 2026-09-19 ("approve, go"). Module specs authorized; no build authorized.**
**Amended 2026-09-19 (owner rulings IC-1 to IC-6, and narrative rulings R8–R12)** — the map and specs
were first written before the owner answered the ideal's questions; every changed section says so.

Ideal: [ip-censor-ideal.md](ip-censor-ideal.md) (idea phase, 2026-09-19). This map does not reopen its
decisions; it decomposes the tool into modules that can be specced and verified one at a time.

**Loops (the-loops.md):** **none, stated explicitly.** This program adds no player loop, currency,
stat, or surface. It is a cross-cutting content gate protecting names already surfaced by Spine A/B/C
and Places 3/6/7. It invents no parallel pitch — the genre is unchanged (RPG + empire over a legal PvZ
Fusion install). Same statement as the ideal's "Which loop this extends" section.

**Scope of THIS program: the detection-and-plan tool, plus the two pieces the owner rulings add.** Its
core deliverable is a token pool, a list of files and locations, and a suggested censor token per
finding. **Applying the change is a separate program** (owner: *"about execute change will be other
plan"*). Consequences recorded now so no downstream session guesses:

- **Amended 2026-09-19 (owner rulings IC-1b, R9, R11, R12).** Display and prose `PvZ` /
  `Plants vs. Zombies` → `Fusion`, and the lead names on existing surfaces → *the Garden Keeper*,
  *Hourbloom*, *the Rotwright*, are done by the **identity-rename program**
  ([tasks/identity-rename-plan.md](../../tasks/identity-rename-plan.md)). This tool's plan output must
  express them; the replacement pairs are already owner-authored. Code identifiers (`pvz.*`,
  `drop.pvz.run`, `EmpireId` members) are never in scope.
- The tool must therefore distinguish a **content rename** (zero-cost, re-run tests) from a
  **code rename** (a code change — the demon→creature class of cost). The `remediation` axis does this.
- **Added 2026-09-19 (owner rulings IC-2, IC-3).** Two modules the rulings require: `curate` (the
  two-stage registry build) and `avoid-list` (the shared seedsmith brief helper, the only
  generation-time prevention the owner kept).
- **Added 2026-09-19 (owner ruling IC-4).** Two live findings are fixed **before release**; see
  *Release-blocking fixes* below.

---

## Owner rulings, and where each one lands (amended 2026-09-19)

| Ruling | What it says | Lands in |
|---|---|---|
| IC-1 | In scope: game and franchise marks, real-person names, company and brand names. Film, song and book titles out; citations out | `registry` (`Category` has three members; `title` removed); `scan` (citations report-only) |
| IC-1b | Display and prose `PvZ` → `Fusion` everywhere player-facing; code identifiers untouched; the rename itself is the identity-rename program's | `registry` (`pvz` group scoped to `player-name`, `player-prose` only; authored replacement); `report` (execute routes) |
| IC-2 | Registry built in two stages: dataset import curated to game-related marks, then census and model proposals confirmed by a person; each row records its stage | `registry` (`admission` record); `curate` (new) |
| IC-3 | The scan is a **release gate**; it never blocks generation; briefs keep only a free avoid-list from one shared seedsmith helper | `scan`, `report`, `wiring` (release hook, advisory CI); `avoid-list` (new) |
| IC-4 | Fix `Overwatch Protocol` and the `Jackson*` family before release | *Release-blocking fixes* below; `avoid-list` |
| IC-5 | The registry is tracked in the repo | `registry` |
| IC-6 | An alias under 4 characters is rejected unless the alias declares a narrow scope | `registry` |
| R8–R12 | Story uses our own names; the EA lead names are registry entries in the player-facing scope; species names barred from narrative prose; new narrative surfaces join scope; prompts never cite other franchises | `registry` (surfaces, entries); `scan` (`player-prose` bucket, narrative fixtures); `avoid-list` (prompt hygiene) |

---

## Module table

| Module id | Responsibility | Depends on |
|---|---|---|
| `source` | Tracked-tree reader: `git ls-files`, extension filter, ignore list (lockfiles, `tsbuildinfo`, binaries, the `self_paths` set), encoding, stable line indexing. Pure I/O, no policy. | — |
| `registry` | The authored alias-group registry (canonical mark + spellings + category + **scope + remediation + admission**), the scope policy, the boundary policy, the `self_paths` set, and the authored replacement map. Pure parser; a missing/mistyped field **throws, never defaults**. **Amended (IC-1, IC-2, IC-5, IC-6):** three categories; `player-prose` surface; stage provenance per row; an alias under 4 characters carries its own scope. | — |
| `census` | Distinct-token census over `source`: token, total count, per-tree distribution, per-surface category. Read-only. **Amended (IC-2):** its output is `curate reconfirm`'s evidence. | `source` |
| `scan` | Match every alias group against `source` text (case-folded, longest-match-first, explicit boundary policy — **not** bare `\b`), then bucket each finding by scope: *player-name* · *player-prose* · *generator-prompt* · *code-identifier* · *docs-prose-citation* · *deliberate-identity* · *registry-self*, and carry the **remediation** route. Read-only. **Amended (IC-3):** the release gate; enforced buckets are player-name, player-prose, generator-prompt. | `source`, `registry` |
| `suggest` | Resolve a replacement per finding: the authored replacement map first; the LLM proposes for the remainder, every proposal marked `proposed — needs owner confirm`. Never invents a replacement for a `code-identifier` / `code-change` finding. | `registry`, `scan` |
| **`curate`** | **Added (IC-2).** Import a trademark dataset through an authored filter into candidates; re-confirm from census hits and model proposals; admit only rows a person decided, recording the stage. | `registry`, `census` |
| **`avoid-list`** | **Added (IC-3, IC-4).** One seedsmith helper (`seedsmith.briefkit`) that renders the registry's player-facing aliases into every brief that produces player-facing text; no model call, no retry. Owns the "briefs never cite another franchise" rule and the `Overwatch Protocol` fix. Reads the registry's data file, never `ipcensor` code. | `registry` (data contract) |
| `report` | Emit the machine-readable plan (JSON) a future execute program consumes, plus the human-readable Markdown report. This is the composition root / CLI entry. | `scan`, `suggest`, `census`, `curate` |
| **`wiring`** | **Amendment, audit A1/A6.** `ip-censor` is an **independent Python tool shaped like `gk-forge/tools/seedsmith`** (owner decision 2026-09-19): own package, own exact-pinned `requirements.lock`, own `tests/`, own **`pytest` verification lane**. Two halves — (1) package + pinned deps + CI step, landable now on the `TVB0.3` precedent; (2) the `runner: "pytest"` project + owner boundary, after `python-test-lane` Wave 3. **Amended (IC-3):** also the release-gate step and the advisory CI scan. | `report`, **externally on `test-verification-boundary` `python-test-lane` TVB3.1/TVB3.2** |

**Dependency direction is acyclic** — `source` and `registry` are the two roots, nothing depends on
`report` except `wiring`, and `census` and `scan` do not depend on each other (both may run
independently over the same `source`). `curate` depends on `census`, never the reverse. `avoid-list`
lives in a different tool and depends only on the registry's committed data file.

**The CLI is the composition root, not a module.** `report` owns the entry point. **Amended 2026-09-19
(owner ruling IC-3):** the only blocking caller is the **release** — a step in
`.github/workflows/release.yml` and a line in `docs/runbook/release-prove.md`, both owned by `wiring`.
The earlier design of a per-change guard script (`guard-ip-vocabulary.ps1`, never built) is withdrawn:
no commit, `verify-change.py` run or CI job blocks on a finding. CI may run the scan advisory.

### Why `wiring` is a module and not a task (amendment 2026-09-19)

Found by audit (`docs/research/ip-censor-spec-audit-2026-09-19.md` A1). `gk-core/scripts/verify-change.py:771`
**throws** `VERIFICATION BOUNDARY MISSING` for any path with no owner boundary; the registry's 101
boundaries cover 12 **C#** projects and contain **zero** entries for `gk-core/tools/ip-censor/**` or
`gk-data/packs/fusion/data/seed/ip-censor/**` (verified by loading the registry). The nearest precedent,
`tuning-publish-tool` (`gk-core/scripts/verification-boundaries.v1.json:863`), maps a `.py` file to a **C#**
test project and runs the tool's real pytest only in a bespoke CI step (R15). And
`gk-core/tests/FusionRpg.Guard.Tests/CiWiringGuardTests.cs:49` walks `*.Tests.csproj` only, so nothing catches
a missing Python CI step.

Without `wiring`, the very first line of code this program writes is unverifiable by the repo's
mandated command. Its criterion is distinct from `report`'s ("is the plan correct?" vs "can the
repository verify and run this at all"), so it is a separate, independently testable module rather than
a task inside another — Phase 0's own test.

### Why `curate` and `avoid-list` are modules (added 2026-09-19)

- **`curate`** has its own criterion — "every registry row was admitted by a person, at a recorded
  stage" — which is neither `registry`'s (does the file parse?) nor `suggest`'s (what replaces a
  finding?). Folding it into `registry` would put I/O and a model call into a pure parser.
- **`avoid-list`** lives in another tool (`gk-forge/tools/seedsmith`), and the two tools share no code
  (`spec-wiring.md` §Tool shape). Its criterion — "every player-facing brief carries the list, at no
  model cost" — is testable only inside seedsmith.

---

## Build order

```
source ──┬─► census ──┬──────────────────────┐
         │            └─► curate ─────────────┤
         └─► scan ──┬─► suggest ──────────────┴─► report ──► wiring
registry ───────────┘
registry (data file) ──► avoid-list            (in gk-forge/tools/seedsmith)
```

`source → registry → census → scan → suggest → curate → report → wiring`; `avoid-list` after the
registry file exists.

`source` and `registry` may be built in parallel (neither depends on the other); `census` and `scan`
may then be built in parallel. `suggest` needs `scan`'s bucket classification, so it is strictly after
`scan`. `curate` needs `census`. `report` composes them. **`wiring` may be built first as a thin lane**,
since A1 blocks the first line of any module — the ordering above is the dependency order, not a
mandate to leave a blocker standing. `avoid-list` needs only the registry's committed file, so it can
start as soon as `marks.v1.json` exists; it gates the IC-4 `Overwatch Protocol` fix.

---

## Release-blocking fixes (owner ruling IC-4, added 2026-09-19)

The owner ruled both live findings fixed before release. Neither is a JSON edit of generated data.

| # | Finding | Route | Done when |
|---|---|---|---|
| IC-4.1 | `"Overwatch Protocol"`, `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538`, generator-owned (`"promptVersion": "tree-language/3"` at `:542`) | The tree node brief adopts the avoid-list helper, its prompt version moves on, and node `skill.command-def-t8-n0` is regenerated through the tree generator's own run. Steps in [spec-avoid-list.md](ip-censor/spec-avoid-list.md) | The regenerated row carries the new prompt version; the release scan reports no `overwatch` finding in `gk-data/packs/fusion/data/seed/passive-tree/**` |
| IC-4.2 | The `Jackson*` species family (`gk-data/packs/fusion/data/seed/creatures/species/_index.json:382-387`; `species/zombie/undead.json:2290`; `species/zombie/performer-undead.json:75,80`), traced to real-person names in the upstream almanac (`gk-data/packs/fusion/data/seed/external-reference/almanac-enrichment/pvz-fusion-almanac-3.6.1.json:5247,5677,5772`) | Upstream data cannot be regenerated, so an **authored import-time rename map** is applied where the upstream names enter the corpus, then the derived trees are regenerated (`data/generated/creatures/Jackson*.json` are generated from the species rows). `remediation: "upstream-imported"` routes it to the execute side. The identity-rename plan covers the PvZ and lead names only. *Audit 2026-09-19:* owned by `tasks/ip-censor-plan.md` (T17–T20); the owner answered its gate G1 **yes**, so the species ids are re-keyed too (T19b: generators read the map's `ids` section; one backed-up, idempotent, single-transaction save migration in `FusionRpg.Data`; the host's `types` table and `gameTypeId` are read, never written) | A test over the import output asserts that no key of the rename map survives in a player-visible name or in a derived species id. The scan alone cannot prove this: `JacksonZombie` is a compound identifier the boundary policy deliberately does not split |

The release gate (`scan --fail-on enforced`) and these two criteria are the program's release
readiness. A test never pins "zero hits" over the real tree (ideal, principle 3); the gate's outcome is
an operational result, not a suite assertion.

---

## What the gate reading found in code (2026-09-19)

Every row was re-read in this session; code beats the ideal where they disagree.

| Fact | Evidence |
|---|---|
| **A repo-wide word-boundary, case-preserving rename was proven, then discarded** — no committed tool exists | Recorded only as history: `docs/guide/glossary.md:61`; `docs/architecture/gameplay-tiers-ideal.md:71` (`740920d2`, "3,914-path rename"). Throwaway script in `%TEMP%` is deleted. |
| **A ban enforced at prompt + answer + emit already exists** — the exact shape `scan`+`suggest` need | `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/grid.py:32,199-207`; call sites `combogen/emit.py:50`, `combogen/brief.py:121-123`, `workflow/graphs/item_combination.py:94-96`. **Amended (IC-3):** the IP avoid-list copies only its prompt half; the answer-side refusal is not copied, because the owner ruled out blocking during generation. |
| **A shared seedsmith brief package exists** — the home for the one avoid-list helper (IC-3) | `gk-forge/tools/seedsmith/seedsmith/briefkit/__init__.py:1-6` (every closed vocabulary a brief depends on is written into the brief literally); the tree node brief already prints `Avoid entirely:` at `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/brief.py:157`. |
| **A brief cites another franchise by name** (narrative ruling: prompts never cite franchises) | `gk-forge/tools/seedsmith/seedsmith/adapters/items/uniques/briefs.py:267` ("a Diablo-style unique item"). The first release scan reports it as `generator-prompt`, enforced. |
| **A scope-aware, word-boundary player-copy scanner already exists** | `gk-web/web/fusion-rpg-web/src/i18n/vocabularyGuard.ts:16-37,42-70,137`; boundary tests at `vocabularyGuard.test.ts:110,181` |
| **Protected-span strippers already exist** (comments/strings) | `gk-core/scripts/cscan.py:246` (`strip_comments_and_literals_preserving_layout`); `gk-core/scripts/guard-test-substrate.py:55-101` |
| **`pyahocorasick` is installed; `regex` 2026.3.32 installed; `flashtext2` 1.1.0 on PyPI** | Verified this session: `python -c "import ahocorasick"` OK; measured 2,046 ms vs `re` 17,038 ms over 195.6 MB. **But neither is declared anywhere** — `gk-forge/tools/seedsmith/requirements.lock` has no such line and no other lockfile exists (audit A5). |
| **`\b` is wrong for this corpus** — matches inside `pvz-fusion-almanac`, `pvz.*`, `drop.pvz.run`; **misses** `PvZ融合版` entirely | Measured this session |
| **`.lower()` misses `Pokémon`** (`é`≠`e`); repo has 149 `pokémon` + 18 `pokemon` hits | Measured this session |
| **`pvz` is an ownership-prefix code namespace, not only a word** | `docs/architecture/software-architecture.md:13` (`pvz.*` = game foundation) |
| **The commander display name is data now** — corrected 2026-09-19; the earlier row said a hardcoded switch was still live, which is no longer true | `PlayerEmpireCommanders.ForPlayer` takes an `ICommanderDirectory` (`gk-core/src/FusionRpg.Core/Commanders/PlayerEmpireCommanders.cs:15`), served by `DataCommanderDirectory` (`gk-core/src/FusionRpg.Core/Commanders/DataCommanderDirectory.cs:23`). The display string is `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json:15` (`"displayName": "Dr. Zomboss"`) — an authored row in the player-name scope (R9), renamed by the identity-rename program. |
| **`Penny` is docs-only** — zero occurrences in `data/`, one comment in `src/` | Measured this session: `WorldTemplateCatalog.cs:165`; 0 in `data/**` |
| **No third-party-IP deny-list or registry exists anywhere** | The former commit-tool policy file (`scripts/commit-tool/policy.json`, deleted with the git gate on 2026-09-19) banned only AI/vendor watermarks. |
| **The live shipped collision** | `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:537-539` (`"Overwatch Protocol"`), produced by the unguarded prompt at `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/brief.py:62-68`. `:542` carries `"promptVersion": "tree-language/3"` — so it is generator-owned, not a direct edit (A3). Fixed before release (IC-4.1). |
| **The upstream almanac is imported by the server** | `gk-core/src/FusionRpg.Server/Program.cs:1426-1445` reads `pvz-fusion-almanac-3.6.1.json` and calls `store.ImportAlmanacEnrichment` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AlmanacSeedEnrichment.cs:36`). The ideal's citation of `gk-core/src/FusionRpg.Server/Program.cs:1382` has drifted. |
| **Both release surfaces exist** (IC-3 hook points) | `.github/workflows/release.yml` runs on a `v*` tag (`:3-6`), `Unit tests (pre-publish)` at `:40` before `Publish player pack` at `:81`; `docs/runbook/release-prove.md` §"Before tagging" at `:5`. `gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs` requires every workflow command's exit code to be checked. |
| **No Python lane exists in the verification registry** (audit A1) | `gk-core/scripts/verify-change.py:771` throws `VERIFICATION BOUNDARY MISSING`; `gk-core/scripts/verification-boundaries.v1.json` has 101 boundaries over 12 `*.csproj` projects and zero `gk-core/tools/ip-censor/**` entries. |
| **The program's own docs carry 110 of the marks it bans** (audit A2) | Measured by exact directory glob: `ip-censor-ideal.md` 69, the seven specs 31, the map 10; plus `tasks/**` 247 across 393 files. A reading at the time of the audit, not a constant. |
| **All 10,338 text-extension tracked files are valid UTF-8** (audit A8) | Measured this session, zero exceptions — so `source` throws on a decode failure rather than guessing. |

---

## Open questions this map does not answer

These belong to the individual module specs (each spec carries its own):

1. **`scan`** — the exact boundary separator tuple, in particular whether `_` separates (the demon
   rename protected `Enslave_Demon`). Measured evidence says the obvious default (`\b`) is wrong twice.
2. **`suggest`** — the LLM client seam (reuse seedsmith's LM Studio client or not) and the exact
   `proposed — needs owner confirm` marker shape. The **configuration key shape** is specified
   (audit A7): `IPCENSOR_LLM_*`, mirroring `gk-forge/tools/seedsmith/.env.example`; the client is one file shared
   with `curate`.

**Answered by the owner on 2026-09-19 and removed from this list (kept as a trail):**

- ~~`registry` — where the registry lives and whether it is tracked~~ → **IC-5**: tracked, under
  `gk-data/packs/fusion/data/seed/ip-censor/`.
- ~~`report` — advisory, or fail `verify-change.ps1`~~ → **IC-3**: a release gate; CI advisory; no
  per-change blocking.
- ~~`scan` — the `docs/` enforcement split~~ → **IC-1**: citations are out of scope, so they are
  report-only findings, never enforced.
- ~~`wiring` — C#-lane precedent or a real Python project~~ → resolved earlier on 2026-09-19 by owner
  decision: an independent Python tool like seedsmith. Half 2 still depends on the binding, unbuilt
  `test-verification-boundary/spec-python-test-lane.md` (Wave 3); see `spec-wiring.md`.

**Audit:** all ten findings and their resolutions are recorded in
[docs/research/ip-censor-spec-audit-2026-09-19.md](../research/ip-censor-spec-audit-2026-09-19.md).

---

## Standards audit (2026-09-19)

Independent adversarial audit of this map, the nine specs under `ip-censor/`, `tasks/ip-censor-plan.md`
/ `-todo.md` and `tasks/identity-rename-plan.md` / `-todo.md` against the owner rulings (IC-1 to IC-6;
the plan's G1 = yes; `npc-story-events-ideal.md` §10 R8–R12; identity-rename's G1 = no save-name
migration), the planning standard, `agent-git.md`, `session-boundary.md`, the AGENTS.md verification
boundary, `testing-standard.md`, the generated-seed rule and the population rule. Plan-level findings
are recorded in each plan's own audit section.

| # | Severity | Finding | Status |
|---|---|---|---|
| M1 | HIGH | IC-4.2 row said the family "needs an owning task in the execute program"; the ip-censor plan owns it, and G1 = yes adds the id re-key (T19b) | Fixed in the row |
| M2 | HIGH | The path-based surface classifier (`registry`, consumed by `census`/`scan`) cannot split a code file holding both an identity-rename kept identifier and a renamed literal; the release gate would never go green, or would miss literals | Fixed: `spec-registry.md`, `spec-scan.md` audit notes; plan D10, todo T4, CP3 |
| M3 | MEDIUM | Release and CI scans specified with `working-directory: gk-core/tools/ip-censor`, where `git ls-files` lists only the tool | Fixed: `spec-wiring.md`; plan D4; todo T10–T12 |
| M4 | MEDIUM | `spec-registry.md` omitted the `overwatch` day-one group, two of the three provenance shapes, the `import-renames.v1.json` file (with its `ids` section) and the plan pair in `self_paths` | Fixed: audit note in `spec-registry.md` |
| M5 | MEDIUM | `spec-avoid-list.md` step 3 did not name the `--node` selector without which `--supersede` re-rolls the whole tree | Fixed: audit note |
| M6 | LOW | Citation drift: the unmapped-path throw (`:95`, then `:118`) here and in `spec-report`, `spec-source`, `spec-wiring`; `ci.yml:300-306` (now `:311-317`) in `spec-wiring` | Fixed — the throw is `gk-core/scripts/verify-change.py:771` |
| M7 | LOW | `spec-report.md`'s execute table routed the `Jackson*` family as names only | Fixed |
| M8 | LOW | The ideal's IC-4 row still describes the `Jackson*` fix as a rename map only | Deferred: the ideal is outside this audit's edit set; the map and plan record G1 = yes |

No generated seed is edited by any task (IC-4.1 and IC-4.2 go through generators); no test pins a
population (the registry member list and closed enums only); the IC-3 ruling holds everywhere (no
generation, commit, `verify-change.py` or CI blocking; CI advisory only).

**Proposed enforcement-registry rows** and **verification-boundary asks:** see
`tasks/ip-censor-plan.md` §"Standards audit (2026-09-19)" (this audit edits no shared file).
