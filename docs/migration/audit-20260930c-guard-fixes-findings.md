# Adversarial audit — guard fixes (`audit-20260930c`)

**Auditor:** adversarial sub-agent. **Date:** 2026-09-30. **Read-only:** no file in
`D:\Works\source\Keepverse` was created, edited or deleted. All mutations were planted in
`%TEMP%\audit\...` copies, and the one guard-suite tree mutation was a `git archive` extraction.

**Verdict in one line:** the *routing* claim survives and I could not break it, but the *"no guard was
weakened"* and *"the guard suite is 15 below baseline"* claims are **broken** — 27 previously-green tests
are red at HEAD, every one of them because the new resolver call is unguarded, and
`guard-actor-hub.py` rule R9 was left un-fixed while its commit message claims it was fixed.

---

## (a) REFUTED

### R1 — `guard-actor-hub.py` R9 was NOT fixed; the commit message says it was

`3adcd8f`'s message states:

> "R5-R9 call walk(root, INJECTOR), and walk() returns [] for a scope that is not a directory - so all
> five rules scanned an empty Injector tree and reported nothing."

Only **R5** uses `walk()`. R9 builds its path directly and was **not** given `owning_root()`, so it is
still resolved against gk-core:

`gk-core/scripts/guard-actor-hub.py:408-411`
```python
def r9_debug_emit_contributions(root: Path) -> list[dict]:
    path = root / "src" / "FusionRpg.Injector" / "CheatCommandRunner.cs"
    if not path.is_file():
        return []
```

* `gk-core\src\FusionRpg.Injector` → `is_dir: False` (the directory does not exist)
* `gk-fusion\src\FusionRpg.Injector\CheatCommandRunner.cs` → **exists**, and contains both
  `EmitActorDerived` and `ResolveDerivedWithContributions`, i.e. R9's subject is live and real.
* `git show 3adcd8f~1:scripts/guard-actor-hub.py` and `3adcd8f:` both contain the identical line
  `path = root / "src" / "FusionRpg.Injector" / "CheatCommandRunner.cs"` — **the line was not touched.**

**Falsifier** (temp copy of gk-fusion's `src`, `KEEPVERSE_FUSION_ROOT` pointed at it; the file contains
`EmitActorDerived` and no occurrence of `ResolveDerivedWithContributions`, asserted on raw text *and*
after `cscan.strip_whole_line_comments`):

```
$ python %TEMP%\audit\p5_r9_clean.py
### falsifier file, asserted on RAW text
   'EmitActorDerived' present              : True
   'ResolveDerivedWithContributions' absent: True
   same after whole-line comment stripping : True
   => R9's condition (emit AND not resolve) is SATISFIED on this file.

(a) --root gk-core  +  KEEPVERSE_FUSION_ROOT=fakfusion2  (the shipped configuration)
   exit=0 verdict=OK by_rule={}
   R9 findings = 0  []
```

Exit 0, verdict OK, zero findings — on a file that satisfies R9's condition. **Positive control, same
harness**, proving the cross-repo walk itself is live (this is the part that *was* fixed):

```
### POSITIVE CONTROL - a new file in the cross-repo Injector scope with Stats.Resolve
   EXIT: 1
   verdict: FAIL  findings_by_rule: {'stats-resolve-bypass': 1}
   FINDING: stats-resolve-bypass | gk-fusion/src/FusionRpg.Injector/ZZFalsifier.cs
```

So R5 is genuinely repaired; **R9 is a residual instance of the exact defect the commit claims to have
removed**, and the commit's "MEASURED non-vacuity" evidence (128 Injector files) is R5's scope, which
does not cover R9.

**Also dead in the same commit:** `_CROSS_REPO_SCOPE = ("src/FusionRpg.Injector", "src/FusionRpg.Launcher")`
(`guard-actor-hub.py:77`). `src/FusionRpg.Launcher` appears **once in the whole file** — the tuple entry.
The only `walk()` call sites are lines 311, 325, 357 (`"src"`, `"src"`, `INJECTOR`). The Launcher entry
configures nothing.

---

### R2 — 27 previously-green tests are red at HEAD; the suite summary is presented as an improvement

Reproduced, in this order:

```
HEAD  (0f0bd3e):  Failed: 154, Passed: 567, Total: 721        <- claim reproduces EXACTLY
base  (b85fc87~1): Failed: 136, Passed: 584, Total: 720
```

**Method note, because the first attempt was invalid:** extracting `b85fc87~1` with `git archive` into a
bare temp dir produced `634 failed / 85 passed` in **5 s**, and every message was
`System.IO.DirectoryNotFoundException : No legacy repository (FusionRpg.slnx ...) or Keepverse
workspace ... above '...prev_b85fc87\tests\F...'`. That is a fixture artifact (no siblings), not a
regression — I would have reported a 480-test "recovery" that never happened. Re-run inside a correct
sibling layout (`gk-core` = the extraction, plus directory symlinks to the real `gk-data`/`gk-fusion`/
`gk-forge`/`gk-web`/`gk-content`/`docs`/`tasks`) it is 136, with **0** occurrences of that exception.

**Set difference — 27 gained, 9 lost, net +18:**

| gained (red now, green at `b85fc87~1`) | n |
|---|---|
| `ClassSystemGuardTests` | 14 |
| `PowerGuardTests` | 6 |
| `StatTaxonomyGuardTests` | 6 |
| `ActorHubGuardTests` | 1 |

**All 24 failures in those four classes share one mechanism**: the guard calls a new resolver accessor,
`_layout()` finds no workspace above the test's planted fixture, and `RootNotFound` — which is **not**
a `Refusal` and is not caught — escapes as a raw traceback. Decisive lines:

```
PowerGuardTests.G4_passes_on_the_real_shipped_pin
  G4 should pass on the real pin, got exit=1 Traceback (most recent call last):
    File "...\scripts\guard-power.py", line 337, in check
      inventory_path = workspace_root(root).joinpath(*INVENTORY)
    File "...\scripts\lib\keepverse_roots.py", line 136, in workspace_root
      return _layout(_start(start))[1]
    File "...\scripts\lib\keepverse_roots.py", line 50, in _layout
      raise RootNotFound(f"no legacy repo or Keepverse workspace above {here}")
    keepverse_roots.RootNotFound: no legacy repo or Keepverse workspace above
      C:\Users\...\Temp\fusionrpg-powerguard-cc4e85a1e3874056b13b75624186da75
```
(the same shape for `guard-class-system.py:241 content_root(root)` and
`guard-stat-pairs.py:127 content_root(root)`)

Manual reproduction of the same shape outside the test harness:

```
$ python %TEMP%\audit\p26_fixture.py
### guard-power.py --root <planted fixture with a G2 violation, no workspace above>
    exit: 1
    stdout: ''
    stderr tail: ['  File "...keepverse_roots.py", line 50, in _layout',
                  '    raise RootNotFound(f"no legacy repo or Keepverse workspace above {here}")', ...]
    => the guard cannot report G2 at all on a fixture; it dies in the resolver first.
```

`ActorHubGuardTests.Guard_script_exits_nonzero_when_GameHooks_uses_Stats_Resolve` — the R5 falsifier the
`3adcd8f` message cites as its non-vacuity proof — is in this set: `Not found: "ACTOR-HUB GUARD FAILED"`,
`String: "Traceback (most recent call last):..."`.

**Against the claim.** `0f0bd3e` says *"154 failed / 567 passed / 721 total. That is 15 below the
clean-HEAD baseline of 169."* The count is right; the framing is not. 154 is **worse** than the
136 I measured immediately before these commits. The 9 that went red→green are the genuine progress and
are worth naming: `ActorHubGuardTests.Guard_script_exits_zero`,
`ClassSystemGuardTests.ClassSystemGuard_script_exitsZeroOnTheRealTree`,
`StatTaxonomyGuardTests.StatPairsGuard_script_exits_zero_on_the_real_tree`,
`TestSubstrateGuardTests.Guard_exits_zero_on_the_current_tree`, `RepoBoundaryGuardTests.The_real_tree_passes`,
`CoreTestProjectPolicyTests.W2`, `CoreTestProjectPolicyTests.W5`, and two `VerificationTopologyTests`.
So the honest summary is **9 real-tree checks recovered, 27 falsifier/contract checks broken** — not
"15 below baseline", and the commit messages never mention the 27 at all.

---

### R3 — `guard-class-system.py` (a2e4ab6) contains a verbatim duplicated block, and the commit's stated rationale is not what the code does

`gk-core/scripts/guard-class-system.py:238-247`:
```python
    # data/seed/** is the gk-data content PACK; data/tuning/** is THIS
    # repository's. One guard reading two repositories is why the root is
    # named per path - the monorepo had one root and never asked.
    pack = content_root(root)
    roster_doc = _read_json(pack.joinpath(*ROSTER), "aptitudes roster.json")
    # data/seed/** is the gk-data content PACK; data/tuning/** is THIS
    # repository's. One guard reading two repositories is why the root is
    # named per path - the monorepo had one root and never asked.
    pack = content_root(root)
    catalog_doc = _read_json(pack.joinpath(*CATALOG), "catalog.json")
```

The commit message says *"the root is named per path there rather than once for the run."* It is not.
`ROSTER` and `CATALOG` are **both** under `data/seed` (lines 79-80) and both go through the same
`pack`. The `data/tuning` read is `shipped_tuning_file(root)` at line 194, `root.joinpath(*TUNING_DIR)` —
correct against `root` already, and correctly left alone. So: two identical statements, one identical
comment, and a comment describing a per-path scheme the code does not implement.

---

### R4 — the manifest now declares the same tool twice, and one of the two declarations points at a file that does not exist

`b85fc87` **added** a declaration and left the pre-existing one in place
(`tests/core-test-projects.v1.json`, `FusionRpg.Core.Balance.Tests.references`):

```
   $(GkForgeRoot)tools/DominanceBaseline/DominanceBaseline.csproj     <- added by b85fc87
   tools/DominanceBaseline/DominanceBaseline.csproj                   <- pre-existing, STALE
```

* `gk-core\tools\DominanceBaseline\DominanceBaseline.csproj` → **`Test-Path` = False** (the tool moved to gk-forge)
* `gk-forge\tools\DominanceBaseline\DominanceBaseline.csproj` → `True`
* the csproj itself references only `$(GkForgeRoot)tools\DominanceBaseline\DominanceBaseline.csproj`

So the manifest asserts two contradictory locations for one file, one of which is a path in gk-core that
has not existed since the split. W2 is a **subset** check (csproj references ⊆ declared), so it is
structurally incapable of noticing a declared-but-absent reference. A sweep of all 67 projects' declared
references against disk returns exactly this one entry.

---

## (b) SURVIVED

* **The routing mechanism itself.** For every path I could test, each guard now resolves the correct
  owner. Measured file counts: `guard-funnel-delta.py` → `src/FusionRpg.Core/Effects/Plugins` 6
  (gk-core), `src/FusionRpg.Core` 1127 (gk-core), `src/FusionRpg.Injector` 128 (gk-fusion) — matching
  `ad0ecb6`'s table exactly, with `first=` paths confirming the right tree in each case. `guard-power.py`
  now reads its inventory from `workspace_root()`, and `guard-class-system.py`/`guard-stat-pairs.py` from
  `content_root()`. I could not find a path that is still resolved against the wrong root **except R9
  (R1) and the standalone-clone case (c) below**.

* **`repo_relative()` did NOT gain a fallback.** `guard-clock-seam.py:218-227` takes `extra_roots` as an
  explicit parameter and the `raise Refusal("FILE-OUTSIDE-ROOT", ...)` still terminates the loop. A
  file under no declared root is still refused, and the message now names every root tried. This is the
  distinction the commit message claims and it holds.

* **`walk()` did NOT gain a fallback.** `guard-actor-hub.py:258-262` still returns `[]` for a
  non-directory — unchanged — and `owning_root()` routes the two declared cross-repo scopes to
  `fusion_root()`. I tried to make it vacuously green via
  `KEEPVERSE_FUSION_ROOT=<non-existent>`; it did **not** go green, it produced two `hub-required`
  findings and exit 1. R4's `is_file()` check is load-bearing and caught it.

* **The 19/19 clock number — reproduced, and it does mean 19 matched.** `python scripts/guard-clock-seam.py`
  → `clock seam guard: source files=1536 ambient reads=21 (clock type=2, allowlisted=19, entries=19)`,
  exit 0. `entries=19` is a **declared** count (`entries_total`), so on its own it proves nothing; the
  proof is the **zero-violation verdict**, because line 302 reports `(rel, fragment) not in matched` as a
  stale entry. I confirmed the counter and the matched-count are independent by deleting the text one
  entry matches in a temp copy: `allowlisted_reads` fell 19→18, `allowlist_entries` stayed 19, and the
  guard reported
  `stale allowlist entry in scripts/guard-clock-seam.py: 'src/FusionRpg.Core/Effects/EffectModels.cs' no longer contains 'public DateTimeOffset UtcNow => DateTimeOffset.UtcN…'`
  with exit 1. **The ratchet is live and 19/19 is real.**

* **The test-substrate ratchet — reproduced exactly, and no entry is unchecked or double-counted.**
  `--json` → `verdict OK, files_scanned 1652, baseline_entries 24, problems 0`. All 24 declared entries
  resolve to a real file (12 in gk-core, 3 in gk-forge, 9 in gk-fusion — **exactly 12 siblings**, as
  claimed); **no** entry is orphaned; **no** duplicate key in the baseline, so nothing is double-counted;
  and the sibling loop `break`s after the first owner that has the file, while `(root / rel).is_file()`
  short-circuits gk-core, so an entry cannot be counted twice. The `if codes:` guard is real: an emptied
  violation list does **not** insert the key, so a fixed file is still reported. Not refuted.

* **The gk-fusion resolver copy is byte-identical.** sha256 `bd178091e3d1ab7e2f7ff38351e101ff732d7f0241bb85049e34045ba05b9d8f`,
  6250 bytes, identical across `gk-core/scripts/lib/keepverse_roots.py`,
  `gk-fusion/scripts/lib/keepverse_roots.py` **and** `gk-forge/tools/seedsmith/seedsmith/workspace_roots.py`
  — matching `ad0ecb6`'s stated `sha256[:16] bd178091e3d1ab7e`.

* **The folded-CI fix.** Parsed with PyYAML, `gk-fusion/.github/workflows/ci.yml`'s test step is
  genuinely two commands:
  `1| dotnet test FusionRpg.slnx --no-build …` /
  `2| if ($LASTEXITCODE -ne 0) { throw "the gk-fusion test run failed" }`.
  A sweep of **all 9 repos plus the workspace root** (6 workflow files) for a single-line `run:` carrying
  `||`, `&&`, `;` or `$(` found **0**.

* **`release.yml` is genuinely generated, complete, and correctly paired.** Parsed (not regex-read):
  67 manifest projects, 67/67 with a csproj on disk, **all 67 invoked**, plus the declared
  `residual: FusionRpg.Core.Tests` — so 68 invocations, and `invoked but NOT in the manifest` is only
  that declared residual, not an undeclared project. **68/68** test lines are immediately followed by
  their own correctly-named `if ($LASTEXITCODE -ne 0) { throw "<project> failed" }`; zero unpaired.
  No referenced csproj is missing from disk. `ci.yml` invokes 76 projects and omits none of the 67.
  (First attempt reported "0 correctly paired" — that was **my** regex forgetting the ` failed` suffix
  in the throw string, not a defect in the file.)

* **W2's real contract is intact.** Running the actual test with the tree redirected via
  `KEEPVERSE_CORE_ROOT`: control PASS; a csproj reference to a non-existent project **not** declared →
  **FAIL** (`W2 -> FAIL`). So "every csproj reference is declared" still bites. See (c) for the hole W2
  does have, which is pre-existing.

* **gk-fusion's two guards are now real greens.** `guard-single-writer.py` → `SINGLE-WRITER GUARD OK`; and
  `cscan` genuinely resolves through `core_root` (`sys.path` gains `…\gk-core\scripts`, module imports).
  `source_files` on a scope that exists nowhere still raises `Refusal(MISSING_SCOPE: src/FusionRpg.NotAThing)`
  — **not widened**, which is the specific thing `ad0ecb6` says it refused to do.

* **A6/A7 clean.** `gk-core 0f0bd3e`, `gk-fusion ad0ecb6`, `gk-forge e6999d9`, `gk-web de8ebcd`; all four
  `ahead/behind = 0/0`; zero dirt excluding `TestResults`/`*.trx` — re-checked *after* running the
  suites, so the builds did not leave anything.

---

## (c) NEW DEFECTS

### C1 — `RootNotFound` escapes every guard as an unhandled traceback, on the layout the resolver's own docstring calls supported

`keepverse_roots.RootNotFound` subclasses `RuntimeError`; the guards catch only their own `Refusal`.
So the documented "named refusal" contract is not what a caller gets:

```
$ python %TEMP%\audit\p6_refusal.py
### 2. standalone gk-core clone (no gk-fusion / gk-forge / gk-data siblings)
   guard-actor-hub.py           exit=  1  TRACEBACK     keepverse_roots.RootNotFound: no legacy repo or Keepverse workspace above ...
   guard-clock-seam.py          exit=  1  TRACEBACK     keepverse_roots.RootNotFound: no legacy repo or Keepverse workspace above ...
   guard-test-substrate.py      exit=  1  no-traceback
```

`_sibling`'s docstring names this exact scenario as supported — *"Without the check a standalone
gk-core clone - **the layout ADDITION 9 asks us to support** - gets a confident path…"* — and that layout
produces a traceback at **exit 1, the same code a real finding uses**, which is the precise confusion
`a2e4ab6` opens by calling "the most expensive kind of wrong". This is also the direct cause of R2.

### C2 — the test-substrate ratchet reverts to reporting its own blindness in that same supported layout

In a standalone clone, `sibling_roots()` swallows the resolver failure and the 12 sibling entries become
absent from `found`, so `evaluate()` reports each as stale — the precise instruction the commit calls "a
lie":

```
$ python %TEMP%\audit\p7_subs.py
### guard-test-substrate.py in a standalone gk-core clone (documented ADDITION 9 layout)
exit: 1
"verdict": "FAIL",
"problems": [
  "tests/FusionRpg.AtomImporter.Tests/RealColdProcessTests.cs: baseline entry no longer violated — remove the line (the ratchet only shrinks)",
  … 11 more, all gk-fusion and gk-forge entries …
```

All 12 still violate. Following the instruction drops 12 live exemptions. The commit fixed this for the
full-workspace case only; the layout its own resolver docstring advertises still produces it. Root cause:
`except Exception: continue` in `sibling_roots()` treats "I could not find the repository" and "the entry
is genuinely gone" as the same thing.

### C3 — every accessor's `KEEPVERSE_*_ROOT` override is unchecked, and the refusal message recommends it

```
$ python %TEMP%\audit\p2_envfallback.py
### resolver behaviour: every KEEPVERSE_*_ROOT override -> a NON-EXISTENT dir
fusion_root            -> D:\...\__audit_no_such_repo__   is_dir= False
forge_root             -> D:\...\__audit_no_such_repo__   is_dir= False
web_root               -> D:\...\__audit_no_such_repo__   is_dir= False
core_root              -> D:\...\__audit_no_such_repo__   is_dir= False
content_root           -> D:\...\__audit_no_such_repo__   is_dir= False
workspace_root         -> D:\...\__audit_no_such_repo__   is_dir= False
```

`_sibling` checks `target.is_dir()` on the **discovery** path and returns the env value **before** the
check. So the module docstring's "Nothing found raises; a root is never guessed" holds for the walk and
not for the override. `core_root` never checks at all, on either path. And the refusal text is
self-defeating: *"a sibling repository cannot be reached by walking upward, so **set the matching
KEEPVERSE_\*_ROOT override** or place it beside gk-core"* — the documented remedy is the one path that
does not verify. (Mitigated downstream: `guard-clock-seam.py` re-checks `fusion.is_dir()`, and
`guard-actor-hub.py` is caught by R4 — which is C1/R1 in another guise.)

### C4 — W2 accepts a declaration of a project that does not exist (pre-existing, now load-bearing)

`$ python %TEMP%\audit\p15_w2.py` — the real test, tree redirected via `KEEPVERSE_CORE_ROOT`:

```
   F0 control: unmutated copy                                            W2 -> PASS
   F1 declare a NON-EXISTENT csproj in the manifest, csproj unchanged     W2 -> PASS
   F2 csproj references a NON-EXISTENT csproj, declared in manifest       W2 -> PASS
   F3 csproj references a NON-EXISTENT csproj, NOT declared               W2 -> FAIL
```

**The brief's question, answered directly: yes — you can add a reference to a csproj that does not exist,
declare it, and W2 passes.** But this is **not** a weakening introduced by `b85fc87`: F1/F2 pass because
W2 is a subset check that never resolved existence, which was equally true before. What `b85fc87` did was
use that hole **honestly** — the csproj really does reference `$(GkForgeRoot)tools\DominanceBaseline\…`
and the declaration matches after W2's normalisation (F3 proves the undeclared case still fails). The
residual problem is R4: the stale sibling declaration the commit left behind.

### C5 — pre-existing red contract test, and the resolver's coverage does not match its 7 accessors

`gk-core/tests/tools/test_keepverse_roots.py` is **1 failed, 20 passed**:

```
$ python -m pytest tests/tools/test_keepverse_roots.py -q
FAILED tests/tools/test_keepverse_roots.py::TheModule::test_it_states_WHERE_THE_TWIN_LIVES_and_asks_for_them_to_agree
E  AssertionError: 'keep the two identical' not found in '"""the roots a path is resolved from: …'
```

`0fb64ca` rewrote that docstring line (`-…keep the two identical.` → `+THIS MODULE HAS THREE
IMPLEMENTATIONS…`) without updating the test's sentinel. **Pre-existing** — it is red at `b85fc87~1`
too, and it is a Python test, so it is **not** inside the 154/567. Two related observations: the
docstring now says "**THREE** IMPLEMENTATIONS" and lists three paths, but `ad0ecb6` created a **fourth**
copy in gk-fusion that no inventory names; and both Python suites pin `ROOTS = ("content_root",
"core_root", "workspace_root")` — the four sibling accessors all eight fixed guards now depend on
(`fusion_root`, `forge_root`, `web_root`, `authored_content_root`) have **no** Python contract test.

---

## (d) COULD NOT REPRODUCE

1. **"the clean-HEAD baseline of 169"** (`3adcd8f`, `0f0bd3e`). I measured **136** at `b85fc87~1` in a
   correct sibling layout, and 154 at HEAD. I cannot identify which commit "169" refers to and did not
   chase it further; the figure is unsupported by anything I could measure.
2. **`3adcd8f`'s "155 failed / 566 passed / 721 total"** for that commit. I ran HEAD and `b85fc87~1`
   only; I did not build `3adcd8f` itself.
3. **`a2e4ab6`'s per-guard before/after table** (`guard-class-system.py 1 -> 0`, `guard-stat-pairs.py
   64 -> 0`, `guard-power.py 1 -> 1`, `guard-population-pin.py 1 -> 1`, and the named G3/unpinned-literal
   findings). I confirmed the **current** end states (0/0/0/0, and `power` exit 1 with 6 G3 findings,
   `population-pin` exit 1 with 11 findings) but did not re-run each guard at `a2e4ab6~1`, so I neither
   confirm nor refute the "before" column. Note the commit says population-pin reports **1** finding;
   today it reports **11** — I did not determine whether that is drift or unrelated later work.
4. **`ad0ecb6`'s "exit 1 (crash) -> 64 MISSING_SCOPE -> 0 OK"** for the two gk-fusion guards. I confirmed
   the end state (both exit 0) and that the scope is not widened, but did not re-run them at `ad0ecb6~1`
   to observe the `ModuleNotFoundError` and the intermediate 64.
5. **`guard-funnel-delta.py`'s "(declared_by sweep of src) 161"** row. The three rule scopes reproduce
   exactly (6 / 1127 / 128); the fourth number is from a sweep the guard does internally and I did not
   isolate.
6. **Whether `docs/` and `tasks/` content in my `b85fc87~1` baseline were that commit's or HEAD's.** The
   workspace-root `docs`/`tasks` were symlinked to the **current** ones, so `DocBoundaryTests`-style
   assertions in the baseline could differ from a true `b85fc87~1` workspace. This affects at most a
   few of the 136; the 27 gained / 9 lost sets are guard-contract tests that do not read `docs/`.
7. **`gk-web` has no `.github/workflows`** (nor do `gk-data`/`gk-content`/`gk-tests`/`gk-assets`), so
   "any OTHER workflow in ANY repo" in item 7 is vacuously satisfied for those five rather than verified.
