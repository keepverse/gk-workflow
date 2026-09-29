# Lane sgc-6 — consolidated summary (`species-gear-chain`, 2026-09-23)

Session `species-gear-chain-6` · branch `cmdc/sgc-6` · 34 commits from `8958d88d6` (a clean fast-forward
merge of `features/mega-merge`). This file exists so the manager can read ONE artifact instead of 34
commit messages and 10 fragments; each claim below names the fragment or commit that carries its evidence.

## 1. What actually changed in the repo (the five substantive commits)

| Commit | What it does | Why it matters |
|---|---|---|
| `2b99dd4d2` | SGC5-F1: commits `gk-data/packs/fusion/data/seed/actions/_fixtures/general/round-1.json` (tracked, hand-authored), declares `_fixtures/` `exclude` in `_manifest.json`, points `prompts.py` and the test at it, and gives `usage_stats._round_corpus_root` a runtime-first fallback | the six seedsmith tests that read the gitignored `_candidates/` scratch go **6 failed → 110 passed** on a checkout with no scratch |
| `a41d5d152` | `seedsmith/tooling.py::run_tool` — a missing executable now raises the CALLER'S own documented refusal, naming it; 8 call sites in 6 modules | a missing `dotnet` used to surface as a bare `FileNotFoundError`, defeating six modules' contract and making six rows look like content failures. **No skip added** |
| `11977b375` | `open_checkpointer` raises `WorkflowEngineMissing` naming the `workflow` extra | same class as above for a missing optional dependency (nested `ModuleNotFoundError`). **No skip added** |
| `193431770` + `d001fd79b` + `cbfa040cd` | `is_authored` excludes files whose own `_meta.authored` declares them authored from the description-backfill `plan()` (both modes), and the over-broad test contract is corrected | the plan targeted the HAND-AUTHORED `act.attack`, so a real run would have overwritten authored prose and destroyed the marker separating authored from generated content |
| `07f9220dd` | six cases pinning the new fallback seam (runtime-first, fixture-fallback, the excluded-by-name case, the fixture's own contract) | the first pass left that seam untested |

Everything else this lane committed is a **reading, a correction, or a filed row** — see §2 and §3.

## 2. The program's state, measured

| Surface | Reading |
|---|---|
| the six ruled-row acceptance tests | **110 passed, 12 subtests passed** (was `6 failed, 98 passed`) |
| seedsmith suite, program-wide | **8 failed / 4618 passed / 4 skipped**, every third a direct printed run; all 8 from three causes (the passed count read 4617 before this lane added a case to `test_actions_description_completeness.py`) |
| gear-chain C# surface | Core.Items.Tests **1470/0**; Data.Tests items-surface **323/0**; Server.Tests **859/0**; plus 32 + 16 focused |
| T37's verify block | **4 of 5 boxes measured green**, the fifth annotated as its own external blocker |
| T57's fence-blocked box | substance green (`audit-magic-numbers` TOTAL 0 0 0 0 0; `gk-core/tools/tuning/` 76 passed); only the FORM is blocked |
| open task blocks | **2** (T37, T55), both externally blocked. The brief's "26" is the census's line-level artifact |
| whole `gk-core/tests/FusionRpg.Data.Tests` | **not run** — CI/nightly owns unfiltered full evidence; its gear-chain slice was run filtered instead |

Fragments: `sgc6-t55-redset.md` (suite + register sweep), `sgc6-verify-lines.md` (verify blocks + C# surface),
`sgc6-open-blocks.md` (the block-rule decomposition), `sgc6-f1.md` (fixture + seam).

## 3. What is blocked, and on exactly what

| Row | Blocker |
|---|---|
| **SGC5-F2** | an owner erratum: (a) re-author `act.attack`'s `atomFamilies` into the 125, or (b) widen the contract and `load.py:250` to the **UNION** of the 125 affix families and the 105 atom-registry families (169). Option (b) as first published would have refused 60 families / 205 rows |
| **SGC5-F3** | a manifest-only rehash mode in `gk-forge/tools/CreatureCorpusDump/**` (outside this fence); re-recording from a live DB rewrites the corpus (baselines 82→913, recipes 1295→0) |
| **SGC5-F4** | already registered as **`SR-25`** (`stub-register.md:77`); this lane adds the 1-of-181 figure, the row's absence from the backfill ledger's 179, and the 4/1 test split |
| **SGC5-F5** | **not registered**: bare-name process starts in test code are a 10-project class (35 call-site files, 5 executables) |
| **SGC5-F6** | **half registered** (`SR-25` covers the corpus half): owner is **effect-atom module E43** (`spec-family-expand.md`); the action program owns `gk-core/src/FusionRpg.Server/Program.cs:765` discarding the `ImportResult` |
| **SGC5-F7** | **not registered**: the SEALED `action-ideal.md` contradicts its own "0 open questions" at `:499` ("⛔ Open (§0.2 A)", where §0.2 carries only Linkage and decision 26 calls it a deferred measurement) and `:137` ("Recommended, not yet ratified"). Owner: the action program |
| **SGC5-F8** | **not registered**: the same SEALED ideal states `12 kinds / 7 triggers` at `:656`/`:657` where `gk-core/src/FusionRpg.Core/Effects/Atoms/AtomKindRegistry.cs` says `18` (`:43`) and `13` (`:48`) — the exact drift `DESIGN-GATE` §1's atom row warns has already happened four times. Owner: the action program |
| **T37** | the denied `gk-forge/tools/ItemSeedValidator/**` exemption (ready patch in `T37-validator-successor-edge-exemption.patch`) and item module 24's P7.3/P7.4 |
| **T55** | a registry disposition (its mapping half holds: 191/191 tuning files resolve) and a guard change in the pipeline-guarded `guard-verification-boundaries.py` |
| **T57's box** | no active session record lists `gk-core/tools/tuning/**`, and this lane's brief does not either |

## 4. The process lesson, stated plainly

This lane **corrected eleven of its own published claims**, and **three findings turned out to be already
documented** (SGC5-F4 = `SR-25`; SGC5-F6 twice, in a test docstring and a sealed spec; part of SGC5-F2).
SGC5-F6 alone took six commits, five of them corrections, and only the DESIGN-GATE reads
(`0469b6ad2`, `9acea2e2e`, `94f1e4252`) got its ownership right (effect-atom E43, not the action program).

**For the next lane on this program: read `docs/DESIGN-GATE.md` §1's rows for the subsystem AND
`docs/architecture/stub-register.md` BEFORE filing anything.** Both are cheap; both would have saved the
majority of this lane's later commits. The readings themselves stand — the corrections were about
ownership and framing, never about a measured fact.

## 5. Where the evidence lives

`tasks/species-gear-chain-sgc6-{f1,f2,f3,open-blocks,verify-lines,citations,t55-redset,tool-refusal,`
`authored-guard,compose-join}.md` — ten fragments, each with its own `| Criterion | Command | Result |`
table. They are NOT under `tasks/evidence-fragments/`, which is outside this lane's allowed paths; each
fragment says so in its header. The run state is in `tasks/species-gear-chain-ledger.jsonl` (append-only,
written only through `gk-core/scripts/anchor-ledger.py`, `check` exits 0).
