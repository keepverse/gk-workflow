# Audit 2026-09-30d — adversarial audit of the gk-core guard-hardening commits

**Sub-agent role:** adversarial. The job was to REFUTE five commits' claims, not confirm them.
**Verdict in one line:** all four headline numbers reproduce exactly, but **ten specific claims
inside those commits are false**, three of them reintroducing the exact defect class the commits say
they closed.

- Scope read: `cd9d43f`, `821fedd`, `3e5c29b`, `42e8d38`, `278f099` in `D:\Works\source\Keepverse\gk-core`.
- HEAD under audit: `278f099`, branch `main`, working tree clean at start and at end.
- Nothing in `D:\Works\source` was modified. Scratch scripts and the f2db59f A/B tree live in
  `%TEMP%\audit2\`. (Two short-lived probe files were created inside gk-core/gk-fusion `scripts/` and
  **deleted in the same call**; `git status --porcelain` is unchanged.)

---

## (a) REFUTED

Each item: the claim as written, the reproducing command, the decisive output.

### R1 — "Root-first can only ever find data the caller explicitly named" (821fedd, `guard_subjects.py`)

The commit argues the direction (root-then-owner, never owner-then-root) is what makes the rule
*safe*: a root carrying a stale copy is authoritative, so the guard reports on the file the caller
named. Constructed exactly that.

```
python %TEMP%\audit2\probe_a3.py
```

A fixture root inside a directory that **can** reach the owner (so the pre-fix arm runs), with G2
suppressed by `--g2-allowlist-file SneakyCurve.cs` so the only discriminator left is G3:

```
HEAD  (278f099)  root carries NO inventory
  exit=1  G3=['G3 src/.../SneakyCurve.cs:2: power-shaped method not listed in inventory.json']
PRE   (cd9d43f)  root carries NO inventory
  exit=1  G3=['G3 src/.../SneakyCurve.cs:2: power-shaped method not listed in inventory.json']

HEAD  (278f099)  root carries a BOGUS inventory licensing the curve
  exit=0  G3=NONE (the curve IS licensed)      <-- REPO GREEN
PRE   (cd9d43f)  root carries a BOGUS inventory licensing the curve
  exit=1  G3=['G3 src/.../SneakyCurve.cs:2: power-shaped method not listed in inventory.json']
```

**The pre-fix guard could not be moved that way at all.** Same command, same tree, same curve — the
only difference is a three-line `inventory.json` inside the `--root`. So the rule is not
"strictly NARROWER than what it replaces"; it moved G3's deciding authority from the owning
repository to whatever the caller wrote. The commit's own words: *"root-first can only ever find
data the caller explicitly named."* True, and that is the hazard, not the safety property.

**The half that does survive:** the real gk-core tree carries none of the three subjects, so the
owner still wins there (a throwaway probe script, `probe_a_subject_root.py`, which does not exist in
any repository — A1 — `data/seed/aptitudes/roster.json`,
`data/seed/derived-stats/catalog.json`, `docs/architecture/power/inventory.json` all `exists=False`;
`data/tuning` present with 202 JSON files). The claim is true for the real tree and false as a rule.

### R2 — "A scale that is not located cannot license anything" (42e8d38, `_strip_repo_prefix`)

The module docstring states the hole it closed: an empty location token satisfies
`$relFwd.StartsWith("")` **for every file**, so one unlocated scale licensed every power-shaped
method everywhere. `inventory_locations` rejects an absent/empty `location` — good. But the prefix
strip, added in the same commit, re-creates the empty token one layer up:

```
python %TEMP%\audit2\probe_b_power_prefix.py
```

```
'gk-core/'                    -> ''                (prefix with an EMPTY tail)
licenses src/FusionRpg.Core/Progression/RpgProgression.cs? True   'gk-core/'
licenses src/FusionRpg.Core/Progression/RpgProgression.cs? True   'gk-core/src'
```

`_strip_repo_prefix("gk-core/")` → `""`; `_is_listed` then evaluates `rel_fwd.startswith("")`, which
is `True` for every path in the repository. Before `42e8d38` the token stayed `"gk-core/"` and
`startswith("gk-core/")` was `False` for a `src/...` path, so **42e8d38 introduced the fail-open the
docstring says it closed.** A one-segment location (`gk-core/`) or a directory-level one (`gk-core/src`,
`gk-core/src/FusionRpg.Core`) licenses the whole subtree — confirmed end-to-end: `location =
'gk-core/src/FusionRpg.Core/Balance/Analytic'` → `exit=0, G3=NONE -> licensed`.

### R3 — "token gk-forge/tools/X/Y.cs against src/... -> False (wrong repo)" (42e8d38)

The commit lists that probe as proof the wrong-repository case is handled. It is handled **only
because that particular tail is `tools/`, not `src/`**. `_strip_repo_prefix` does not check *which*
repository the token names — it strips all nine names identically:

```
licenses src/.../RpgProgression.cs? True   'gk-web/src/FusionRpg.Core/Progression/RpgProgression.cs'
licenses src/.../RpgProgression.cs? True   'gk-fusion/src/...'
licenses src/.../RpgProgression.cs? True   'gk-data/src/...'
licenses src/.../RpgProgression.cs? True   'gk-workflow/src/...'
```

End to end, each of these licenses a gk-core file:

```
location='gk-web/src/FusionRpg.Core/Balance/Analytic/SneakyCurve.cs'     exit=0  G3=NONE -> licensed
location='gk-fusion/src/FusionRpg.Core/Balance/Analytic/SneakyCurve.cs'  exit=0  G3=NONE -> licensed
location='gk-workflow/src/.../SneakyCurve.cs'                            exit=0  G3=NONE -> licensed
```

A token naming a repository this guard does not walk at all (gk-web, gk-fusion, gk-data) now licenses
gk-core's file of the same repo-relative path. "Wrong repo" is not a property the code enforces; it
was a property of the one token the author happened to test.

### R4 — "It also fails if the tool ever stops emitting a hex digest" (278f099, the P1 rewrite)

```
python %TEMP%\audit2\probe_de.py
```

The assertion is `assertEqual(hashlib.sha256().digest_size * 2, len(envelope["out"]["sha256"]))`.
`digest_size * 2` **is 64** — the rewrite is numerically identical to the literal it replaced, and no
looser. It observes length, and length cannot observe an alphabet:

```
real tool run: sha256='79594dfe...086d'  len=64  all-lowercase-hex=True   accepted: True
substituted 'z'*64 (64 NON-HEX chars)                                   accepted: True
assertEqual(64, len('a'*31 + ' ' + 'b'*32))  -> PASSES
```

The claim is false. The rewrite silences the population-pin guard's P1 regex (which matches
`assertEqual(<digit>, …)`) without adding any discriminating power. It is a 64 spelled differently.

### R5 — "one change covering all seven accessors rather than seven near-identical ones" (3e5c29b, `_env`)

There are **three modules**, not one. The `_env` validation landed in one of them.

```
python %TEMP%\audit2\probe_de.py   (section E1)   and   probe_final.py (FINAL 3)
```

```
gk-fusion/scripts/lib/keepverse_roots.py                    _env body: ['return Path(v) if v else None']
gk-forge/.../seedsmith/workspace_roots.py                   _env body: ['return Path(v) if v else None']
gk-core/scripts/lib/keepverse_roots.py                      validated (is_dir) -> REFUSED

[gk-fusion copy] HANDED BACK: ...\nope-does-not-exist is_dir= False
[gk-core copy]   REFUSED: KEEPVERSE_FUSION_ROOT=... does not name a directory
```

The gk-fusion copy still hands back a directory that is not there — the exact defect 3e5c29b names
("the caller received a confident path to a directory that was not there and carried on"). And
gk-fusion's own guards consume it: `gk-fusion/scripts/guard-funnel-delta.py:65` and
`guard-single-writer.py:67` call `core_root(...)` at **import time**, with the unvalidated copy.

### R6 — "The two Python copies are byte-identical … a test asserts that" (`gk-core/scripts/lib/keepverse_roots.py:29-34`)

**Closed 2026-10-02 — this finding no longer reproduces.** It was true when written: `difflib` over
the two files showed **31 differing lines**, all of them the `_env` body, and no test compared the
copies. Both halves are now fixed. Measured on this commit: all three Python copies share one
SHA-256 (`gk-core/scripts/lib/keepverse_roots.py`, `gk-fusion/scripts/lib/keepverse_roots.py`,
`gk-forge/tools/seedsmith/seedsmith/workspace_roots.py`), and the asserted test exists —
`gk-core/tests/FusionRpg.Guard.Tests/ResolverCopyParityTests.cs`, whose own docstring records this
exact 31-line drift. It holds the copies byte-identical, checks they expose the same seven
accessors, and asserts an override naming an absent directory is **refused** rather than handed back,
which is the behaviour the unchecked `_env` broke. The docstring's claim is now enforced rather than
asserted.

### R7 — "the target must still be a real, **tracked**, VERSIONED tuning file" (278f099, `immutable_path_is_valid`)

`immutable_path_is_valid` ends in `(repo_dir / normalized).is_file()`. It never consults git.

```
python %TEMP%\audit2\probe_cd.py   (section C2)
a brand-new, untracked, never-committed file: ...\gk-core\data\tuning\brandnew.v99.json
immutable_path_is_valid('gk-core/data/tuning/brandnew.v99.json', tmp) = True
immutable_path_is_valid('data/tuning/brandnew.v99.json', tmp)            = True
```

This is the eighth case the brief asked for. It is **pre-existing** (the pre-fix implementation also
used `is_file()`), so it is not a regression — but the commit's sentence describes the rule as
untouched *and* describes "tracked" as part of it, and the code has never checked it. A deleted-then-
never-committed tuning file satisfies the pin.

Everything else in the shape rule holds: `../../etc/passwd` → False, `..\..\etc\passwd` → False,
`gk-core/../../../etc/passwd` → False, `gk-core/data/tuning/../../../etc/passwd` → False. The last
three probes are **hypothetical** fixtures the probe itself created — a path such as
`gk-core/data/tuning/sub/deep.v1.json` does not exist in any repository, so neither does `x.V1.json`,
and a **directory** named `adir.v7.json`, equally hypothetical, → False (`is_file()` saves it). All
**seven** of the commit's own probes reproduce with 0 mismatches.

### R8 — "resolved against the repository that OWNS it" (278f099)

It is resolved against the guard's own `repo_root`. The standard writes pins *workspace-qualified*,
so a pin like the hypothetical `gk-fusion/data/tuning/x.v1.json` — a fixture that does not exist in any
repository — names a sibling's file, and the fix resolves it as
`gk-core/gk-fusion/…`, which does not exist, so it returns False. Latent today (no sibling ships
`data/tuning`; only gk-core does, 202 files), live the moment one does. The fix handles exactly the
one case where the named repository is the guard's own, and the commit says so itself for the
`gk-core/` spelling — while the stated rule is the general one.

### R9 — "a refusal a CI operator can distinguish from a finding is not a refusal" (3e5c29b)

**The distinction is destroyed one layer up, by the runner.**

`gk-core/scripts/run_guards.py:392`:

```python
return (f"guards failed: {', '.join(report.red_gating)}{report.environment_note}",
        report.results[-1]["exit"] or EXIT_FAILED)
```

The runner's exit code is the **last guard's** exit code, verbatim. So the same two results — one
real finding, one refusal — produce a different runner exit code depending only on ordering:

```
python %TEMP%\audit2\probe_f2.py

F4  --only verification-boundaries --only power   ->  run_guards.py exit = 64
      verification-boundaries  exit=1  (VERIFICATION BOUNDARY GUARD FAILED: project file missing: elementenumgen)
      power                    exit=64 (power REFUSED: WORKSPACE-ROOT-MISSING)
      red_gating = ['verification-boundaries', 'power']
F5  --only power --only verification-boundaries   ->  run_guards.py exit = 1
      power                    exit=64
      verification-boundaries  exit=1
```

`gk-core/.github/workflows/ci.yml:433` and `gk-fusion/.github/workflows/release.yml:104` only test
`$LASTEXITCODE -ne 0`, so CI does not regress. But the **stated purpose** — that a refusal is
distinguishable from a finding — does not survive the runner: a green-looking refusal code (64) is
emitted by a run in which a real violation was found, and the runner's code is order-dependent.
Before 3e5c29b all four guards exited 1, so this was order-independent.

### R10 — "guard-verification-boundaries.py reports 7 missing project files" (G)

**Eight**, and the total finding count is far larger.

```
python %TEMP%\audit2\probe_g2.py
```

```
project file missing: elementenumgen / proveliveprobe / lawncombatobserver / treebinder /
                       launcher / atomimporter / itemseedvalidator / passivetreerostergen   = 8
pytest root missing:  seedsmith: tools/seedsmith
pytest root missing:  manager-fail-closed: .claude/cmdc-agents/scripts
stale exact path:     channel-policy-tuning, fe-debt-register, gen-build-plan-data,
                      gen-fusion-recipe-data, launcher-loader-install (x3), launcher-overlay-pipe,
                      core-resource-regen-unit, magnitude-ledger-doc, manager-fail-closed (x2) …
VerificationId has no matching test trait: launcher.loader-install, launcher.overlay-pipe
```

`"7 missing project files"` understates it and mis-scopes it: the red is not a project-file problem,
it is the whole split topology — 8 project files, 2 pytest roots, 12+ stale exact paths and 2
orphaned verificationIds. Every one of these names a path in a repository gk-core no longer holds.

**Is the owner gone or merged? No — and this is the part worth acting on.**

```
ps1-ban-l1-harness-20260926.json   status=merged    branch=ps1ban/l1-harness
ps1-ban-l2-deletes-20260926.json   status=merged    branch=ps1ban/l2-deletes
ps1-ban-l4-artifacts-20260926.json status=active    branch=ps1ban/l4-artifacts
ps1-ban-manager-20260926.json      status=active    mode=direct  branch=features/mega-merge
    paths include: 'scripts/verification-boundaries.v1.json',
                   'scripts/guard-verification-boundaries.py',
                   'docs/architecture/verification-boundaries/*'
```

- The manager record is **`status: active`** and its `paths` list **does** own the registry and its
  guard. The owner is not gone.
- `features/mega-merge` is **absent as a local branch** in the source repo but **present on origin**
  (`remotes/origin/features/mega-merge`), and the source repo's HEAD is `main` at `566eb4a36` — so
  the branch is **not merged into main**. The local-branch check alone would have read "merged".
- The registry's own history in the Keepverse repo is one commit: `34bf27d Import snapshot from legacy
  repo effc51d9…`. It has **never been edited** since the import. The red is caused by the split, not
  by ps1-ban.

So: the last red guard is **not** unblocked by "the owner is gone". It is blocked on an active,
unmerged program whose registry is a verbatim pre-split import, and the fix is a topology rewrite of
~24 rows across 8 missing projects, 2 missing pytest roots, 12 stale paths and 2 orphaned
verificationIds — the owner's ruling, not a stale-record cleanup.

### R11 — "a refusal … is not a finding" is applied to 4 guards; a fifth uses the word and returns 1

`gk-core/scripts/guard-test-content-root.py` prints a REFUSED banner and a `"verdict": "REFUSED"`
JSON envelope, then returns `EXIT_FAILED`:

```
L363:  print(json.dumps({"guard": GUARD_ID, "verdict": "REFUSED", "reason": refusal.reason, ...
L367:  print(f"TEST CONTENT-ROOT GUARD REFUSED: {refusal.reason}", file=sys.stderr)
L370:  return EXIT_FAILED          # EXIT_FAILED = 1  (L93)

run: exit=1   stderr[0]='TEST CONTENT-ROOT GUARD REFUSED: TESTS-MISSING'
```

A machine consumer reading the exit code sees a finding. A machine consumer reading the JSON sees a
refusal. `cd9d43f` added this guard's `Refusal` class and did not give it the code.

---

## (b) SURVIVED

Attacked and could not break. Stating exactly what was tried.

### S1 — Claim 1, both numbers, and the per-class claim. **Reproduced to the digit.**

`f2db59f` was measured on a **clone** at `%TEMP%\audit2\base\gk-core` (`git clone --no-hardlinks`
+ `git checkout f2db59f`), with NTFS junctions to the real `gk-data`, `gk-forge`, `gk-fusion`,
`gk-web`, `gk-content`, `gk-assets`, `gk-tests`, `docs`, `tasks`, `scripts`, `tools`, `BepInEx` so the
workspace layout resolves exactly as in place. This was chosen over the brief's
`git checkout f2db59f -- <paths>` specifically to keep the source tree read-only; the brief's
warning about the all-or-nothing pathspec abort is real and was avoided by not using it.

```
HEAD   (278f099):  Failed: 127, Passed: 594, Skipped: 0, Total: 721   (1 m 11 s)
f2db59f:           Failed: 134, Passed: 586, Skipped: 0, Total: 720   (   50 s)
```

Seven better, and **0 test classes worse** — confirmed per class, not per total:

```
classes WORSE than f2db59f: 0   better: 6   same: 36
fully green at HEAD that were red at f2db59f:
  ClassSystemGuardTests 1->0   CoreTestProjectPolicyTests 2->0
  StatTaxonomyGuardTests 1->0  TestSubstrateGuardTests 1->0
also improved: PowerGuardTests 2->1, VerificationTopologyTests 4->3
```

Both figures and the class claim survive. A count going *up* would not have been progress; here it
went down and the per-class table shows the movement is spread over 4 fully-recovered classes, which
is what a fixture-contract repair looks like.

### S2 — Claim 2: 20 of 21 guards exit 0.

```
python %TEMP%\audit2\probe_f2.py   (F8, no overrides set)
total=21  exit0=20  non-zero=1
  NOT zero: guard-verification-boundaries.py exit=1
```

Survives. (See R10 for why *that* guard is red — and it is red for more than 7 reasons.)

### S3 — Claim 3, the absent-sibling census. **Exact.**

```
python %TEMP%\audit2\probe_g.py
siblings absent: total=21  OK=12  REFUSED(64|2)=6  FINDINGS(1)=3  CRASH/other=0
  REFUSED  guard-actor-hub.py          exit=64  FUSION-ROOT-MISSING
  REFUSED  guard-class-system.py       exit=64  CONTENT-ROOT-MISSING
  REFUSED  guard-clock-seam.py         exit=64  FUSION-ROOT-MISSING
  REFUSED  guard-power.py              exit=64  WORKSPACE-ROOT-MISSING
  REFUSED  guard-stat-pairs.py         exit=64  CONTENT-ROOT-MISSING
  REFUSED  guard-vocabulary-mirror.py  exit=2   EXIT_FORGE_ROOT_MISSING
  FINDINGS guard-population-pin.py            exit=1
  FINDINGS guard-test-substrate.py            exit=1
  FINDINGS guard-verification-boundaries.py   exit=1
```

0 crashes / 12 green / 6 refusals / 3 findings — the claim's own four numbers, exactly. I tried to
turn a refusal back into a crash by pointing each override at a **file** rather than a missing
directory, and by removing the overrides one at a time; no crash reproduced. The `_env` validation
does fail closed in the module that has it.

### S4 — Claim 4: three of the four guards, and the guard still fails on a real undeclared curve.

```
python %TEMP%\audit2\probe_f2.py (F7)   siblings absent
  guard-clock-seam.py      exit=64  REFUSAL
  guard-class-system.py    exit=64  REFUSAL
  guard-power.py           exit=64  REFUSAL
  guard-test-substrate.py  exit=1   FINDING   <-- see "could not reproduce" below
```

And the discrimination the strip was supposed to buy is real:

```
python %TEMP%\audit2\probe_b_power_prefix.py (B4/B5)
  real inventory in the root, curve NOT listed: exit=1
     ['G3 src/.../SneakyCurve.cs:2: power-shaped method not listed in inventory.json']
  the REAL gk-core tree: exit=0  'POWER GUARD OK — one ladder, pin holds, no private f(level)'
  location tokens: 40   unlocated scales: []
  reachable at 42e8d38^ : []            <-- the defect 42e8d38 names
  reachable at HEAD     : 1 token       <-- the fix works
```

So 42e8d38's *primary* claim — 29 of 33 scales were permanently unreachable — reproduces, and the
fix makes them reachable. R2/R3 are about the edges the same change opened, not about the centre.

---

## (c) NEW DEFECTS — not on the brief's list

### N1 — `guard-class-system.py` prints a green verdict from a scan that examined nothing

```
cd D:\Works\source\Keepverse && python gk-core/scripts/guard-class-system.py --root .
  exit=0
  CLASS-SYSTEM GUARD OK — aptitude ids collision-free, edges registered, no atk double-count,
  every null unitClass noted, at most one AptitudeReadFunctions, DominantPosture unwired,
  closed form calls shipped combat symbols
  --json: verdict=OK  failures=0  skipped=18
```

The workspace root has no `src/` and no `data/tuning/`. G2, G3, G5, G6 and all eight G7 checks did
not run — 18 `SKIPPED` notices, zero coverage — and the OK string asserts every one of them anyway
("at most one AptitudeReadFunctions", "DominantPosture unwired", "closed form calls shipped combat
symbols"). The notices go to stderr, the verdict to stdout, and the exit code is 0. This is the
blindness-as-verdict class at the aggregate level, still open: `guard_subjects.py:28` states "It is
never an empty scan and never a green verdict" as a rule, and the guard that enforces the rule
violates it. Six of the seven G7 skips are individually reported, so the per-file mechanism works;
the *verdict* is what lies.

### N2 — `subject_root`'s owner half is unreachable from a fixture root

`subject_root` calls `accessor(root)` — the **caller's** root as the walk-up start:

```python
def subject_root(root, relative, accessor):
    if root.joinpath(*relative).exists():
        return root
    return accessor(root)          # keepverse_roots._layout walks up from the CALLER's root
```

A temp fixture (`%TEMP%\...`) has no `gk-core`+`gk-data` above it, so the owner lookup raises:

```
python %TEMP%\audit2\probe_a_subject_root.py
[root without an inventory]  exit=64
  stderr: power REFUSED: WORKSPACE-ROOT-MISSING no legacy repo or Keepverse workspace above
          C:\Users\...\Temp\audit2\work\A\A2b-no
```

This is the same shape as the A2b "A4/A5" arms. So the second half of the rule — "otherwise resolve
the owning repository" — only ever fires for a root that is already inside the workspace. Every
guard contract test that plants a fixture in `%TEMP%` gets the *first* half or a refusal, never the
fallback. The rule is correct for the real tree and inert for the tests it was written for.

### N3 — `subject_root` keys on `.exists()`, so a DIRECTORY at the subject path wins the root

```
python %TEMP%\audit2\probe_a_subject_root.py (A4)
  subject_root returned C:\...\A4\gk-core   (root wins on a DIRECTORY named roster.json)
  guard-class-system on that root: exit=64
    stderr: class-system REFUSED: SOURCE-MISSING aptitudes roster.json missing: .../roster.json
```

It refuses (so it is not a green verdict), but the *routing decision* is made on the wrong predicate:
`guard-power.py` then reports `INVENTORY-MISSING` on a path that exists, because `subject_root`
promised a root and the caller found a directory. `is_file()` at the call sites would be the honest
predicate; the docstring says "a root that **carries the subject**", and a directory does not.

### N4 — Half a subject now refuses where the owner used to answer

```
python %TEMP%\audit2\probe_a_subject_root.py (A5)
  root carries the ROSTER but not the CATALOG: exit=64
    stderr: class-system REFUSED: SOURCE-MISSING catalog.json missing: .../catalog.json
```

`ROSTER` is resolved through `subject_root`; `CATALOG` is then read from the *same* `pack` without a
second decision (`guard-class-system.py:254-258`). Before 821fedd the pack was the owner's, so a
partially-planted fixture worked. Now a root carrying one of the two subjects takes the whole pack
and refuses on the other. The two subjects are resolved as a unit but only one of them is checked.

### N5 — gk-core's own CI step `pytest tests/tools` cannot collect 9 files, 4 of them guard contract tests

```
cd D:\Works\source\Keepverse\gk-core && python -m pytest tests/tools -q
  Interrupted: 9 errors during collection !
  test_bcu212_full_run.py            test_guard_funnel_delta.py
  test_f13_schema_upgrade_proof.py   test_guard_game_profile.py
  test_guard_injector_compile.py     test_guard_single_writer.py
  test_reemit_colliding_item_names.py  test_session_boundary_check.py
  test_union_append_only.py
```

`gk-core/.github/workflows/ci.yml:521` runs exactly this. `278f099` names one of the nine
(`test_union_append_only.py`) and calls it "the same monorepo-root class" — correct, but it is **nine
files, not one**, and four of them are the contract tests for the gk-fusion guards
(`test_guard_funnel_delta`, `test_guard_game_profile`, `test_guard_injector_compile`,
`test_guard_single_writer`). Verified pre-existing: the identical 9 errors reproduce at `f2db59f`.
The consequence is concrete: **the exit-64 change and the cross-repo resolution in gk-fusion have no
executable test coverage**, because the tests that would pin them cannot be collected.

### N6 — `guard-game-profile.py` is not wired to a root resolver and cannot run without two flags

```
python %TEMP%\audit2\probe_h2.py (H(i)-2)
  guard-game-profile.py  exit=2  usage: guard-game-profile.py [-h] --game-dir GAME_DIR --profile PROFILE
```

`gk-fusion/scripts/guard-game-profile.py:187` is `root = Path(__file__).resolve().parent.parent` —
no resolver, unlike its four siblings. In a run where the other four exit 0, this one exits 2 with a
usage error. Outside the five commits' scope, but it is the same census gap (H-i) the commits were
answering.

---

## (d) COULD NOT REPRODUCE

Stated plainly.

1. **The in-place `f2db59f` measurement.** The brief specifies `git checkout f2db59f -- <paths>`
   into the live tree. I did **not** do that, because the read-only constraint forbids mutating
   `D:\Works\source`. I used a clone plus layout junctions instead. The result matched the claimed
   figure to the digit (134/586/720), which is strong evidence the environments are equivalent, but
   it is a different physical tree and I am not claiming byte-identity of the two runs.

2. **`guard-test-substrate.py` never reaches its own 64 path.** The code has it
   (`EXIT_REFUSED = 64` at L99, `return EXIT_REFUSED` at L433) and I could not reach it. Every
   `Refusal` it raises is local — `BASELINE-UNREADABLE`, `TESTS-FILE-UNREADABLE`, `TESTS-MISSING`,
   `PATH-OUTSIDE-ROOT` — and `sibling_roots()` **swallows** `RootNotFound` at L317. I forced it four
   ways (forge absent, fusion absent, both absent, override pointing at a *file*) and it returned
   **exit 1 with real findings** every time. So of claim 4's four guards, three are demonstrably
   distinguishable and the fourth's 64 is **structurally present but not reachable by the condition
   the commit is about**. Its sibling-absence behaviour is still the blindness-as-verdict shape,
   mitigated by the `unreachable` third state rather than by the exit code. I could not build a
   failing case for the 64 path itself, so I am not calling it unreachable — only unexercised.

3. **`"4 of the power ladder's 33 scales"` vs `40 location tokens`.** The inventory has 33 scales
   and 40 location tokens (one scale names several, comma-separated). The commit's "29 of its 33
   location tokens" is 29 of **40** tokens / 33 scales — the reachable count I measured is 1 token
   for the specific path `RpgProgression.cs` both before and after, so I could not reproduce a
   per-scale count either way without deciding which denominator the commit meant. The *direction*
   (0 → 1 reachable for that path; 40 tokens total, all but 4 now reachable) is unambiguous.

4. **"20 of 21 green" as stated in 821fedd.** That commit says "18 of 21 green; the three red are
   unchanged". The census I ran is 20 green / 1 red. So 821fedd's own census figure was **wrong at
   the time it was written** (it reported 3 red where there is 1), even though the brief's claim 2
   (20/21 at HEAD) is correct. I could not reproduce 821fedd's 18/21 at that commit without
   checking it out, so I report the discrepancy as a reading of the commit text against HEAD rather
   than as a reproduced measurement.

5. **Whether `subject_root`'s root-first order has bitten anything real.** No directory in the
   workspace other than gk-core itself carries `docs/architecture/power/inventory.json`,
   `data/seed/aptitudes/roster.json` or `data/seed/derived-stats/catalog.json`, and the real gk-core
   carries none of them, so **no live invocation is currently affected** by R1. It is a rule defect
   with a constructed failing case, not an observed one. I did not find and do not claim an incident.

---

## Reproducing every number in this report

```powershell
# S1  both suite figures + the per-class table
cd D:\Works\source\Keepverse\gk-core
dotnet test tests/FusionRpg.Guard.Tests --nologo -v q          # -> 127/594/721
# the f2db59f arm
git clone --no-hardlinks D:\Works\source\Keepverse\gk-core $env:TEMP\audit2\base\gk-core
cd $env:TEMP\audit2\base\gk-core; git checkout f2db59f
# junction the siblings, then:
dotnet test tests/FusionRpg.Guard.Tests --nologo -v q          # -> 134/586/720
python $env:TEMP\audit2\class_diff.py                           # per-class, 0 worse

# S2/S3  both censuses
python $env:TEMP\audit2\probe_f2.py                             # F8 (present) + F7
python $env:TEMP\audit2\probe_g.py                              # both censuses + claim 4

# R1..R11
python $env:TEMP\audit2\probe_a_subject_root.py                 # A1..A5
python $env:TEMP\audit2\probe_a2.py
python $env:TEMP\audit2\probe_a3.py                             # the G3 differential
python $env:TEMP\audit2\probe_b_power_prefix.py                 # B1..B5
python $env:TEMP\audit2\probe_cd.py                             # C1..C5, D1..D4
python $env:TEMP\audit2\probe_de.py                             # D3, D5, E1..E6
python $env:TEMP\audit2\probe_efg.py                            # F1..F3
python $env:TEMP\audit2\probe_f2.py                             # F4..F8
python $env:TEMP\audit2\probe_g.py                              # G
python $env:TEMP\audit2\probe_g2.py                             # G detail
python $env:TEMP\audit2\probe_h2.py                             # H(i), H(iii)
python $env:TEMP\audit2\probe_final.py                          # R11, R5, R6
```

### The one-line summary for the ledger

The four numbers are honest and reproduce exactly; the **arguments** built on them are not. Three
changes (`821fedd`, `42e8d38`, `3e5c29b`) each state a safety property and each fails it at its own
edge — fixture precedence hands G3 to the caller, the prefix strip re-creates the empty-token fail-open
it documents closing, and the override validation reached one module of three while the docstring
claims a test holds them in step. The eighth `immutable_path_is_valid` case is *untracked*, not
non-existent. The last red guard is owned by an **active, unmerged** session, and the brief's
"7 missing project files" is 8 plus 2 pytest roots plus 12 stale paths plus 2 orphaned verificationIds.
