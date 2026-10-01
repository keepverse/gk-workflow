# Capability map — `ps1-ban`

**Program:** port every PowerShell tool in this repository to reliable Python, prove each port, merge
to `features/mega-merge`.

**Owner ruling (2026-09-26):** the repo bans `.ps1`/`.bat` tools. This supersedes the `AGENTS.md`
line "Existing `.ps1` files are **not** to be rewritten wholesale".

**Status of this document:** the index. Module ids are stable kebab-case and are referenced by
`tasks/ps1-ban-plan.md` and `tasks/ps1-ban-todo.md`. Every count here is a **reading** reproduced at
the commit named in §0 — never a constant.

---

## 0. The measured baseline

Reproduce with `git ls-files '*.ps1' | Measure-Object` and
`python -c "import json;print(len(json.load(open('gk-core/scripts/enforcement-registry.v1.json'))['guards']))"`.

| Fact | Reading | How to reproduce |
|---|---|---|
| Tracked `.ps1` | **109** | `git ls-files '*.ps1'` |
| Tracked `.bat` / `.cmd` | **0** | `git ls-files '*.bat' '*.cmd'` |
| `.ps1` code lines (excl. comments/blanks) | **11,545** | non-blank, non-`#` pass over all 109 |
| Enforcement-registry guard rows | **29** | `len(json.load(...)['guards'])` |
| Registry rows naming a `.ps1` | **29 of 29** | same, `endswith('.ps1')` |
| `scripts/*.py` already present | **26** | `git ls-files 'scripts/*.py'` |
| `gk-core/scripts/lib/*.py` already present | **2** | `git ls-files 'gk-core/scripts/lib/*.py'` |
| Guards already wrapping a real `.py` | **5** | §2 `shim-guards` |
| `shell: pwsh` steps in CI | **54** (ci 37, nightly 4, release 13) | `grep -c 'shell: pwsh'` per workflow |
| `.ps1` tools CI invokes that have no `.py` | **9** | §4 `ci-shell-bash` |
| Citation lines naming a `.ps1` path | **~2,580** (lower bound) | `git grep -c -F <path>` summed |

⚠️ **The citation total is a lower bound.** A reconnaissance lane's capped search produced *higher*
per-file figures than the uncapped `git grep` on 5 of 11 names. Treat ~2,580 as an order of
magnitude for capacity planning, never as a completion metric.

⚠️ **110 `.ps1` exist on disk; 109 are tracked.** The difference is `.kilo/setup-script.ps1`, which is
machine-local and excluded through `.git/info/exclude`. It is **not** in scope and must never be
renamed.

---

## 1. The constraint that orders the whole program

**`dispatcher-interpreter` is Wave 0 and contains no port.**

Every guard reaches the outside world through a small set of dispatchers, and every one of them is
PowerShell-specific. Every `.ps1` site in this table was deleted with the PowerShell retirement,
completed 2026-09-28; the rows are the program's record of the sites as they were.

| Dispatcher site | What it does | Consequence for a `.py` guard |
|---|---|---|
| retired `scripts/run-guards.ps1:191` — `& $pwsh -NoProfile -File $script @guardArgs` | runs **all 29** guards | `pwsh -File guard-x.py` does not execute Python |
| retired `scripts/verify-change.ps1:359` — `& (Join-Path $Root $scriptRel)` | runs every selected `script` check | the PS call operator cannot invoke `.py` (`PATHEXT` has no `.py`) |
| retired `scripts/verify-change.ps1:29` — `powershell -File …guard-verification-boundaries.py` | hardcoded interpreter | same |
| retired `scripts/verify-change.ps1:188-190` — `powershell -File …session-boundary-check.py` | hardcoded interpreter | same |
| retired `scripts/test-fast.ps1:45` — `& (Join-Path $Root "scripts\guard-test-substrate.py")` | the default local profile's gate | same |
| `Directory.Build.targets:53` — `<Exec … -File "$(FusionRpgProfileGuardScript)">` | runs **before every `Build;CoreCompile`** of the three injector host projects | same, and it takes the whole injector build with it |
| retired `scripts/publish-player.ps1:165` | release packaging | same |
| `gk-fusion/scripts/deploy-play.py:397-403` — a `pwsh -Command` string with a PS **hashtable literal** interpolated from Python | the deploy's positioned precondition | the call must be rebuilt, not renamed |
| `.github/workflows/{ci,nightly,release}.yml` — `run-guards.ps1 -Tier ci` | the merge, nightly and release gates | same |
| `gk-core/.github/workflows/ci.yml:435-441` — `guard-verification-boundaries.py` | its own CI step (`ciEntry: own-step`) | same |

**Until `dispatcher-interpreter` lands, a guard cannot shed its `.ps1` at all.**

⚠️ **Corrected 2026-09-26 by measurement.** This section first claimed the failure would be
*silent* — "the guard stops running and the suite reads green". **That was wrong**, and the
correction matters because an overstated risk mis-briefs every lane. Measured with a throwaway
probe on this machine:

```
pwsh -NoProfile -File probe.py  ->  exit 64
   "Processing -File '...\probe.py' failed because the file does not have a
    '.ps1' extension. Specify a valid PowerShell script file name..."
python probe.py                 ->  exit 3,  "PYTHON ACTUALLY RAN"
```

`pwsh -File <a .py>` **fails loudly** — a named reason and a non-zero code, so the runner
reports a red row. The call-operator path is loud too: `Get-Command` on a `.py` raises
`CommandNotFoundException` under `$ErrorActionPreference = 'Stop'`.

**The gate is still real** — a ported guard cannot execute until the dispatchers select an
interpreter by extension — but it fails **red and loud**, not green. The genuinely *silent*
failures are elsewhere and are listed in `contract-scan-repair` and `repo-root-probes`: the
globs that match zero files and pass vacuously, the `File.Copy` that throws in a test temp root,
and the repo-root probes that walk to the filesystem root instead of failing. **Those** are what
the same-commit rename discipline exists to prevent, and they are the reason this program is
sequenced the way it is.

`deploy-play` is the counter-example that proves the port is *possible*: it is already fully Python
and its consumers were updated in the same change.

---

## 2. Module index

### `dispatcher-interpreter` — Wave 0, no port
Make the ten dispatch sites in §1 select an interpreter per target (by extension, or by a `runner`
field on the registry row). **Zero behaviour change: every guard is still `.ps1` when this lands.**
This is the only wave whose proof is "nothing changed".

### `registry-repoint` — the 29 rows, one commit
`gk-core/scripts/enforcement-registry.v1.json` names a `.ps1` in all 29 `script` fields.
`gk-core/scripts/verification-boundaries.v1.json` carries a further **51 `.ps1` rows** in `paths` arrays.
A row and its file must move in the **same commit**; a dangling row makes `gk-core/scripts/run_guards.py:308`
throw `guard script missing` and the boundary guard throw `script file missing`.

### `shim-guards` — 5 guards, highest leverage, near-free
Each is a 7–18 line wrapper that already delegates to a substantial Python tool that exists today:

| Guard wrapper (all five retired 2026-09-26, rows repointed) | Delegates to | Real `.py` lines (measured) |
|---|---|---|
| `guard-doc-citations.ps1` (retired) | `scripts/audit-doc-citations.py` | 548 |
| `guard-magic-numbers.ps1` (retired) | `gk-core/scripts/audit-magic-numbers.py` | 348 |
| `guard-overflow.ps1` (retired) | `gk-core/scripts/audit-overflow.py` | 266 |
| `guard-population-pin.ps1` (retired) | `gk-core/scripts/guard-population-pin.py` | 215 |
| `guard-vocabulary-mirror.ps1` (retired) | `gk-core/scripts/guard-vocabulary-mirror.py` | 238 |

`guard-population-pin` and `guard-vocabulary-mirror` additionally already have **pytest** coverage
attached to the `.py`. Under the owner's ban the registry row moves to the `.py` and the wrapper is
deleted. This is the first proof that `dispatcher-interpreter` works.

### `contract-scan-repair` — the sites that break *silently*
Renaming a `.ps1` breaks more than the registry. Three distinct failure shapes, all confirmed:

1. **Globs that go vacuously green.** `EnforcementRegistryGuardTests.cs:57` globs `guard-*.ps1` and
   finds **28** (it does not match `session-boundary-check.py`). Port the guards and the "every guard
   is catalogued" invariant iterates an empty array and still reports success.
   `GeneratorCheckCiParityTests.cs:26` globs `gen-*.ps1` and finds **15** — same shape, and its
   `Every_gen_wrapper_command_matches_a_ci_step_at_the_same_working_directory` guarantee dies quietly.
2. **`File.Copy` that throws.** `VerificationBoundaryWorkflowTests.cs` has **9** sites copying
   `gk-core/scripts/guard-verification-boundaries.py`, plus one in `VerificationBoundaryMappingRepairTests.cs`.
3. **Two spellings of one contract.** `GuardWiring.cs:190` looks for `run-guards.ps1 -Tier ci`;
   `VerificationTopologyTests.cs:82` looks for `run-guards.ps1 -Tier ci -CiRange`. Update one, not
   the other, and they silently disagree.

### `cross-tool-source-reads` — the hardest coupling
Code that reads another tool's **source text** to extract a value. A port removes the literal it
matches. Six sites, all confirmed by reading:

| Reader | Reads | Fails |
|---|---|---|
| `gk-core/scripts/verify-change.py:363` (pattern at `:83`) | `gk-core/scripts/test_fast.py:81`, regex `\$?filter\s*=\s*"([^"]+)"` | `Refusal("DEFAULT-FILTER-UNREADABLE")` — loud |
| `NarrativeGuardContractTests.cs:65-77` | `guard-narrative.py`'s `@'…'@` here-string row-map | `Assert.NotEmpty` — loud |
| `VerificationBoundaryWorkflowTests.cs:1376` | a **literal PowerShell expression** in `guard-verification-boundaries.py` | `Assert.Contains` — loud |
| `VerificationBoundaryWorkflowTests.cs:1434-1442` | `lib/VerificationBoundaries.ps1` and **textually rewrote** `$Script:EnforcedRoots`; that helper was replaced by the Python import probe at `:85-120` | loud — and it *mutated* the file it read |
| `gk-core/tests/tools/test_program_status.py:311-327` | `session-boundary-check.py`'s `$validModes`/`$validStatus`/`$required` | `assertIsNotNone` — loud |
| `gk-core/tests/tools/test_program_status.py:25,332` | `accept_lane.py`'s `ACCEPTANCE_VERDICTS` tuple — **was `accept-lane.ps1`'s `$AcceptanceVerdicts` until the port.** A HALF-RENAME happened here first: the sweep rewrote the path and left the PowerShell variable name beside it, producing a row that mixed a Python module with a PowerShell symbol and READ as updated. A mechanical rename cannot catch that — the retired thing's IDENTIFIERS are part of the prose — so a reader has to | loud, and the port turned the bare read into a refusal, so a future owner change names the missing owner instead of raising `FileNotFoundError` from the middle of a vocabulary assertion |

Note the ownership inversion in the fifth: `program_status.py` holds those three vocabularies as the
**Python source of truth** and the `.ps1` is the mirror. Porting it makes the Python the only copy and
deletes the test that proved the copy was safe.

### `repo-root-probes` — the rename tax
~40 `File.Exists(Path.Combine(dir, "scripts", "<name>.ps1"))` calls locate the repo root by walking
up. They do not throw when the name changes — they walk to the filesystem root and the test then
reports "could not locate repo root". Worst fan-out: `guard-dal` (16 files), `guard-class-system`
(13 test files + 5 `tools/*` programs, and `tools/**` is not in CI so breakage there is invisible),
`guard-secondary-no-unity` (9), `guard-power` (6).

### `guard-ports` — the 24 real guard bodies
Grouped by the coupling that forces them together; see the plan for the groups. Byte-preservation is
required for the verdict strings: **22 `Assert.Contains` on guard stdout** live in
`gk-core/tests/FusionRpg.Guard.Tests` (e.g. `ACTOR-HUB GUARD OK`, `TEST SUBSTRATE GUARD OK` ×6, and
`FunnelDeltaGuardTests` asserts the offending **symbol** name, not a formatted tuple).

`lib/SourceText.ps1` is RETIRED (deleted 2026-09-26; it had exactly **one** consumer,
`guard-battle-responsibility`), so porting that pair is what let the lib die — **done 2026-09-26**: the lib is deleted, its comment-and-string stripper is
`cscan.strip_comments_and_literals_preserving_layout` (`gk-core/scripts/cscan.py:246`), and its file walk is
`source_files` in the ported guard. Two PowerShell copies of one comment-stripping routine remain
(`guard-test-substrate`, `guard-vocabulary-mirror.py:55`) — port them independently and a divergent
third appears.

### `tool-ports` — the non-guard infrastructure
`verify-change` (a `.py` already exists, 955 lines, alongside its `.ps1`), `run-guards`,
`session-boundary-check`, `test-fast`, `test-sharded`, `publish-player`, `mutate`, `coverage`.
`session-boundary-check` is the highest-risk: its closed vocabularies are owned in Python and mirrored
in PowerShell, and a test enforces the mirror.

### `lib-ports` — `gk-core/scripts/lib/*.ps1` (5)
A `.ps1` cannot dot-source a `.py`, so each of the six dot-source sites is a real restructure.
`gk-core/scripts/lib/keepverse_roots.py` already existed beside the retired `gk-core/scripts/lib/KeepverseRoots.ps1`.

### `harness-ports` — the manager/lane tooling
`.claude/cmdc-agents/scripts/accept_lane.py` and `post_merge_check.py`. **Ported first, on purpose:**
they are the proof instrument for every other lane, so leaving them to a later wave means PowerShell
judges the Python work. Their verdict vocabulary and every refusal message are the contract.

### `checks-ports` — `gk-core/scripts/checks/*.ps1` (16)
Small wrappers around one `dotnet`/`python`/`npm` command each, registered as verification-boundary
`script` projects. `GeneratorCheckCiParityTests` extracts their command with a PowerShell-specific
regex, so the port must repoint that test in the same change.

### `live-probe-ports` — the live tier
~35 scripts whose owner's bar is **a real live run**, not a unit test. Not all need a game: several
are pure `dotnet`/`file`/`download` work. **`docs/runbook/live-test-ssot.md` §7 already carries a
PowerShell→Python parity table and the rule at its line 530: "Do not delete PS1 until a Python pack
has hard-assert parity and this table says `≈`."** Nine scripts already have a Python equivalent under
`gk-fusion/tools/live_test/live_test/scenarios/`; for those the sanctioned migration is delete, not port.

### `citation-sweep` — the ~2,580 references
One tool-driven pass, never per-lane sweeps. It must be executed **by** the ported citation guard, in
the same commit as that guard's port, or the guard breaks on the commit that renames it.

⚠️ **`scripts/audit-doc-citations.py` cannot validate this sweep at its default invocation.** It reads
only tracked `.md`, only backticked paths, and **blanks fenced code blocks** — which is where most real
invocations live. `AGENTS.md` and `CLAUDE.md` are in its `EXEMPT_BASENAMES`. The invocation that sees
every markdown file is `--scope ./`, and even that sees **zero** of the contract scans in
`contract-scan-repair`. The sweep's validator is `dotnet test gk-core/tests/FusionRpg.Guard.Tests` plus an
MSBuild parse of the three injector host projects.

### `ci-shell-bash` — the 54 `shell: pwsh` steps
Owner-ruled in scope. The dominant idiom is a command plus
`if ($LASTEXITCODE -ne 0) { throw "…" }`, and the obvious plan — delete the exit checks because
`shell: bash` runs `bash --noprofile --norc -eo pipefail` — **is wrong**: five C# guard tests pin that
literal line, and deleting it produces **160 violations**. Two honest paths: keep the line verbatim as
an inert comment (`shell: bash` alone then satisfies the owner with zero guard churn), or amend the
guards in the same commit as an owner-sign-off change.

Nine `.ps1` tools are invoked by these workflows and have no `.py` yet, so **19 of the 54 steps are
blocked on the tool ports**, not on the shell change.

### `retirements` — delete, do not port
One-off artefacts with no live consumer. Each delete must be proven unreferenced first, and a file
that is *contractually* named elsewhere is **not** a retirement candidate — but "named" has to mean
named *as a thing that must exist*, not merely mentioned in a policy list.

`docs/guide/mechanisms/_gen-stubs.ps1` — **deleted 2026-09-26** — was first held back on the belief
that `VocabRenameTests.cs:462-463,477-478` asserted its existence. **That belief was wrong and the
check disproved it.** The test feeds path *strings* to a pure glob predicate
(`gk-core/scripts/vocab-rename.py:100-103`); `rendered_outputs` derives from the phase rules rather than the
filesystem. The exclude entries in `gk-core/scripts/vocab-rename/identity-rename.v1.json` are a **policy**
rule — never rewrite this generator, because its `_content/*.json` sources are the truth — and a
policy rule about a path stays true after the file is gone. The file was superseded dead data: its
own header forbids re-running it, and `_render.py` (already Python) renders all 66 mechanisms.
Deleted 2026-09-26 with no test or config amendment required.

---

## 3. Two precedents that point opposite ways

Recorded because the program must pick one deliberately, not by accident.

- **Replace:** `deploy-play.ps1` → `deploy-play.py`. The `.ps1` was **retired because it was broken**
  (it ran the full guard tier on every deploy, and every deploy died on an unrelated bug). Its ~91
  citing files were re-pointed in the same program.
- **Wrap:** all five `shim-guards`, and `verify-change` today (a 955-line `.py` beside its `.ps1`).

The owner's ruling is a ban, and `deploy-play` is the closest precedent, so the program proceeds by
**replace**. The cost is the `contract-scan-repair` and `repo-root-probes` work; the benefit is that
the ban is actually satisfied. `dispatcher-interpreter` exists because replace is impossible without
it.

---

## 4. What this map does not decide

- Whether `guard-game-profile.py` should become a **library** rather than a guard. It answers one
  question for three callers with three different invocation mechanisms; a module plus three thin
  callers is less code than a script plus a `.targets` `<Exec>` plus a hashtable-interpolated
  `pwsh -Command` built from Python. Porting it as "a guard" pays the `Directory.Build.targets`
  blast-radius cost for no benefit.
- Whether `session-boundary-check.py` should be a port or a **reduction** (delete the duplicated
  PowerShell arrays, keep the Python as the single owner, keep the `.ps1` only as the diff-fence
  executor).
- Per-script slot-minute estimates for the live tier, and which of those scripts cannot be proven in
  this environment at all.
