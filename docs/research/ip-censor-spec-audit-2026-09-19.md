# ip-censor spec audit — 2026-09-19

**Scope:** the `ip-censor` capability map and its six module specs, audited against code in this
session. Every finding below was reproduced, not reasoned about.

**Verdict: the design holds. Three findings are load-bearing defects — one of them makes the specs
unbuildable as written, and one is a correctness bug in the scanner's own contract.**

Companion: [ip-censor-map.md](../architecture/ip-censor-map.md) ·
[ip-censor-ideal.md](../architecture/ip-censor-ideal.md) · specs in
[docs/architecture/ip-censor/](../architecture/ip-censor/).

---

## Findings, ranked

### A1 — BLOCKER: no file the specs propose can be verified by `verify-change.py`

Reproduced: `gk-core/scripts/verify-change.py:771` **throws** on any path with no owner boundary:

```
if ($hits.Count -eq 0) { throw "VERIFICATION BOUNDARY MISSING: $path. Add an owner mapping; do not
run a broad suite as a fallback." }
```

`gk-core/scripts/verification-boundaries.v1.json` maps **101 boundaries over 12 C# projects**
(`core`, `data`, `server`, `guard`, …). It contains **zero** entries for `gk-core/tools/ip-censor/**` or
`gk-data/packs/fusion/data/seed/ip-censor/**` (verified by loading the registry:
`[b["id"] for b in boundaries if any("ip-censor" in p ...)] == []`).

So the first agent to implement `ipcensor/scan.py` runs the mandated command and gets a throw instead
of a test plan. `AGENTS.md` names this exact class — *"An unmapped production path is a
verification-boundary defect: add/repair its mapping or report it"* — which means the mapping is a
**deliverable the specs owe**, not an implementation detail.

Complicating facts:
- **There is no Python project lane.** The `projects` registry is entirely `*.csproj`. The closest
  precedent, `tuning-publish-tool` (`verification-boundaries.v1.json#tuning-publish-tool`), maps
  `gk-core/tools/tuning/publish.py` → `project: "guard"` — a **C#** test project. `verify-change` therefore
  runs `FusionRpg.Guard.Tests` for a change to a Python file; the tool's own pytest is run only by a
  bespoke CI step (R15, `spec-rulings-2026-09-18.md`: *"a `gk-core/tools/tuning` pytest step in
  `ci.yml`/`release.yml`"*).
- **CI does not catch a missing mapping for `tools/**`.** `guard-verification-boundaries.py:80-97`
  asserts ownership only while walking `Get-ChildItem (Join-Path $Root 'src')`. An unmapped
  `gk-core/tools/ip-censor/*.py` passes CI and fails only in the builder's hands.

**Strengthening (resolved 2026-09-19):** the owner decided `ip-censor` is an **independent Python tool
shaped like `gk-forge/tools/seedsmith`**, not a C#-lane mapping. That decision selects the honest fix: a real
`runner: "pytest"` project. Its runner kind is owned by the binding, **unbuilt** spec
`docs/architecture/test-verification-boundary/spec-python-test-lane.md` (Wave 3, TVB3.1/TVB3.2 — all
`[ ]`), so the 7th module id **`wiring`** lands in two halves: the seedsmith-shaped package + pinned
deps + CI step now (on the shipped `TVB0.3` precedent, `.github/workflows/ci.yml:308-314`), and the
boundary once that lane ships. See `docs/architecture/ip-censor/spec-wiring.md`.

### A2 — HIGH: the scanner's own artifacts are inside its scan scope (unbounded self-reference)

Reproduced by census over the tracked tree:

| Path | IP marks |
|---|---|
| `docs/architecture/ip-censor-ideal.md` | **69** |
| `docs/architecture/ip-censor/*.md` (the seven specs) | **31** |
| `docs/architecture/ip-censor-map.md` | **10** |
| `tasks/**` (393 files — where the plan is written) | **247** |

**Measurement correction (same session):** a first pass reported "97" for the specs. That number was
wrong — the filter `f.startswith("docs/architecture/ip-censor")` is a **prefix** match and swept
`ip-censor-ideal.md` and `ip-censor-map.md` into the spec count. Re-measured by exact directory glob
and counted per file (census 5, registry 11, report 1, scan 11, source 0, suggest 3, wiring 0). The
conclusion is unchanged; the per-class figure is now exact.

`spec-registry.md` declared `self_paths` as **only the four authored registry files**. That is
insufficient twice over:

1. The program's **own documentation** names the marks it bans — necessarily, because that is how it
   explains itself.
2. The **plan output** (`tasks/ip-censor/plan.json`) contains every finding. Committed, it becomes
   input to the next scan: a scan that flags its own previous scan, growing each run.

The demon→creature run solved this with a deliberate trick the ideal already recorded — keeping the
tool out of the tree so it could not self-reference. The specs must make that structural, and
`self_paths` cannot be a hand-maintained list that a future author forgets to extend.

**Strengthening:** `self_paths` becomes three classes, each with a test — (a) the four registry files,
(b) `docs/architecture/ip-censor/**` + `ip-censor-map.md` + `ip-censor-ideal.md`, (c)
`tasks/ip-censor/**`. Plus one derived rule: any path the plan writer targets is self-excluded by
construction, so a new output location cannot silently reopen the loop.

### A3 — HIGH: the plan cannot express the generated-tree rule, so "execute" would hand-edit generated data

`AGENTS.md` calls generated-seed hand-editing a **hard rule** violation: a tree whose entries carry
`_meta.model`/`promptVersion`/`batch` is generator output, and *"the only sanctioned path is: change
the generator/tuning/registry, then regenerate."*

But the plan's only classification axis is `bucket` (`player-name`, `generator-prompt`,
`code-identifier`, …). `bucket: "player-name"` cannot distinguish:

- `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538` `"Overwatch Protocol"` — **generator output**
  (`:542` carries `"promptVersion": "tree-language/3"`); fixing it means editing the tree's prompt and
  regenerating, and the regenerated file must be committed with its generator.
- a hand-authored display string in a registry — a direct edit.

Both are `player-name`. An execute program fed this plan would edit the JSON by hand, the next
generator run would revert it, and — per `guard-generated-seed.py:6-10` — the change would fail the
guard for touching a provenance-carrying file without its generator.

**Strengthening:** the plan gains a **`remediation`** axis, orthogonal to `bucket`:
`authored` (direct edit) · `generator-owned` (change the prompt/registry, regenerate, commit together)
· `upstream-imported` (the `gk-data/packs/fusion/data/seed/external-reference/**` almanac family — no generator exists) ·
`code-change` (identifiers / `pvz.*`). `remediation` is **policy**, so it belongs in `registry`, and it
is derived from provenance the file already carries — not guessed.

### A4 — HIGH: the owner's "include docs as normal findings" collides with the ideal's abandonment finding

The owner answered: include `docs/` as normal findings. The ideal measured why that is dangerous:
~3,400 hits, overwhelmingly **attributed prior-art citations** (`docs/` carries Diablo 486, Warcraft
167, Pokémon 164, Arknights 127, Genshin 96), and the ideal's §6.1 conclusion is that flagging those
*"produces the thousands-of-false-positives failure … and the tool gets disabled."*

Both cannot be true at once. The specs currently resolve it silently — `spec-scan.md` has a
`docs-prose-citation` bucket and `spec-report.md` includes it — which is a design decision standing in
for an owner decision. It needs surfacing, not smoothing: the honest options are (i) citations are
*findings in the plan* but **never** `enforced`, so the gate is quiet while the reading stays complete;
or (ii) citations are excluded from the plan. Option (i) preserves the owner's instruction and the
ideal's finding simultaneously.

### A5 — MEDIUM: `pyahocorasick` is installed on this machine and declared nowhere

The specs assert the dependency is available. Measured: `requirements.lock` (seedsmith) contains no
`ahocorasick` or `regex` line, and no other requirements file exists. `pyahocorasick` imports fine
**locally** — which is exactly the failure the dependency baseline exists to prevent:
`docs/architecture/seedsmith/spec-dependency-baseline.md` requires **exact pins, never ranges**,
because *"a range means two clones can run different code and both call themselves green."* A fresh
clone fails at import.

### A6 — MEDIUM: `CiWiringGuardTests` does not cover a Python tool, so its CI step can silently go missing

`gk-core/tests/FusionRpg.Guard.Tests/CiWiringGuardTests.cs:49-58` walks every `*.Tests.csproj` in the tree and
asserts it appears in `ci.yml` — *"the general form of the guard above: walk every `*.Tests.csproj`
actually in the tree."* A pytest suite is not a `*.Tests.csproj`, so nothing checks that
`gk-core/tools/ip-censor` is wired. The guard's own doc comment even says the W7 case exists so *"the next
`tools/*.Tests` project"* cannot go unwired — a Python tool sits outside it.

### A7 — MEDIUM: the LLM's endpoint, model and credentials have no authored home

`spec-suggest.md` specifies an injected callable and correctly refuses to import seedsmith — but never
says where the endpoint, model, timeout or attempts come from. `gk-forge/tools/seedsmith/.env.example` defines
exactly this surface (`SEEDSMITH_LLM_ENDPOINT`, `SEEDSMITH_LLM_MODEL`, `SEEDSMITH_LLM_TIMEOUT`,
`SEEDSMITH_LLM_ATTEMPTS`, `SEEDSMITH_LLM_RETRY_DELAY`). Without a named equivalent, the implementer
invents env keys or hardcodes `localhost:1234`.

### A8 — LOW: two open questions are already answered by measurement

- **Encoding** (`spec-source.md` Q1 / fallback policy). Measured: **all 10,338 text-extension tracked
  files decode as UTF-8; zero non-UTF-8.** The honest policy is **throw**, not guess — a silent
  replacement decode in a scanner is a correctness hazard, because a mangled byte changes what matched.
- **Han segmentation** (`spec-census.md` Q3). The measured need is **boundary** handling on
  `PvZ融合版`, not segmentation. `jieba` is only needed if CJK *tokens* belong in the pool — a scope
  question, not a correctness one.

### A9 — LOW: the specs have no test that proves the pipeline finds the one known live collision

`gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538` is a *known* shipped third-party name in a
player-facing field. Nothing in the specs as first written asserts the tool finds it. That is the strongest single
acceptance criterion available and it is free.

### A10 — LOW: map drift after `census` Open Question 1

`spec-census.md` Q1 proposes moving the surface classifier into `registry` (it is policy, and it keeps
`census` and `scan` independent). That is a real interface change — the classifier's owner — and the
map still implies the bucket vocabulary is `scan`'s. The map must be updated or the proposal rejected;
either way it cannot stay ambiguous.

---

## Verified-clean (so the record shows what was checked and held)

| Claim | Verification |
|---|---|
| `gk-data/packs/fusion/data/seed/ip-censor/_registry/**` will not trip `guard-generated-seed.py` | The guard's tree table (`:41-68`) lists items/actions/atoms/passive-tree/creatures/dungeon/structures — no catch-all `^gk-data/packs/fusion/data/seed/`; and it *"correctly ignores"* authored registries by requiring provenance (`:18-19`). |
| The live collision is real and player-facing | `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538` `"name": "Overwatch Protocol"`, `:542` `"promptVersion": "tree-language/3"`. |
| The identifier hazard is real | `docs/architecture/software-architecture.md:13` defines `pvz.*` as the **ownership prefix** ("who may write what"). |
| The commander de-hardcode target is already built as a mechanism | `DataCommanderDirectory.cs:21` exists and parses `default-commanders.v1.json`; the live hardcode is `PlayerEmpireCommanders.cs:14-15`. |
| The enforcement shape to copy exists | `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/grid.py:32` (`BANNED_WORD = "runeword"`) + its three call sites. |
| A Python tool's own tests can run in CI | Precedent: the `gk-core/tools/tuning` pytest step in `ci.yml` (R15). |
| The measured engine numbers in the specs | `pyahocorasick` 2,046 ms vs `re` 17,038 ms over 195.6 MB; `\b` misses `PvZ融合版`; `.lower()` misses `Pokémon`. |

---

## Proposed map amendment (needs owner approval — the map is the approved gate)

Add a 7th module so A1 and A6 have an owner instead of being nobody's problem:

| Module id | Responsibility | Depends on |
|---|---|---|
| `wiring` | An **independent Python tool, shaped like `gk-forge/tools/seedsmith`**: package, exact-pinned `requirements.lock`, `tests/`, and a real **`pytest` verification project** (not a C# mapping). Proves `verify-change.py -Paths gk-core/tools/ip-censor/**` returns a **plan naming the ipcensor lane**. | `report`, **externally `python-test-lane` TVB3.1/TVB3.2** |

Build order becomes `source → registry → census → scan → suggest → report → wiring`. `wiring` is
independently testable (does the mandated command work?) and could be built first as a thin
placeholder lane, since A1 blocks the first line of code.

**Alternative considered and rejected:** fold this into `report`. Rejected because `report`'s
criterion is "the plan is correct"; `wiring`'s is "the repository can verify and run the tool at all".
Different consumers, separately verifiable — Phase 0's own test for when to split.

---

## What this audit did not do

- **No legal opinion.** A4 is a product decision, not a legal one.
- **No fix applied to the two live findings** (`Overwatch Protocol`, the `Jackson*` family). They are
  execute-phase targets.
- **No code written.** The strengthening is spec text; nothing here authorizes a build.
