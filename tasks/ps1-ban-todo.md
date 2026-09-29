# Tasks — `ps1-ban`

Plan: [`tasks/ps1-ban-plan.md`](ps1-ban-plan.md) · Index:
[`docs/architecture/ps1-ban-map.md`](../docs/architecture/ps1-ban-map.md)

**Shape:** `H-task` (heading task blocks). ✅ Registered in `gk-core/scripts/todo-shapes.v1.json` as Task
0.4 (`4b41e425d`), so `python gk-core/scripts/program_status.py --program ps1-ban` now **measures** this
program rather than reporting it `unmeasured`. It reads **8 open task blocks, 2 done** — and the gap
between 8 blocks and 80 unticked `- [ ]` boxes is the point: an unchecked box is not a unit of work.
Re-run the reader rather than quoting that number; it moves as blocks close.

**Branch:** `features/mega-merge` · **Manager:** `ps1-ban-manager-20260926`

## How to read the state

A lane's commit existing is **not** acceptance. A lane merges only on green scoped verification plus
an acceptance at an exact pinned SHA — and the merge additionally waits on §Section 3 of the plan,
because the active session is still writing this branch.

---

## Task 0: Program instrument

- [x] **0.1** Capability map with the measured baseline and the module index
- [x] **0.2** Plan with the wave sequence and the reason for it
- [x] **0.3** This task list
- [ ] **0.4** Register `tasks/ps1-ban-todo.md` in `gk-core/scripts/todo-shapes.v1.json` with shape `H-task`
      and an exemplar, so the status reader stops reporting `unmeasured`
- [ ] **0.5** Re-verify the map's §0 baseline against the head this program merges into; the counts are
      readings at one commit and every wave moves them
- [ ] **0.6** Correct the `AGENTS.md` line "Existing `.ps1` files are **not** to be rewritten
      wholesale" — superseded by the owner ruling. **Fenced by two live sessions; lands last.**
- [ ] **0.7** Decide `guard-game-profile`: port as a guard, or reduce to a library with three thin
      callers. Porting it as a guard pays the `Directory.Build.targets` blast radius for no benefit.
- [ ] **0.8** Decide `session-boundary-check`: port, or reduce (drop the duplicated PowerShell
      vocabulary arrays, keep Python as the single owner, keep the `.ps1` as the diff-fence executor)

## Task 1: Wave 0 — the dispatchers (no port in this wave)

Nothing else in the program can run until this lands. A guard that sheds its `.ps1` before the
dispatchers can run a `.py` **cannot execute at all** — measured 2026-09-26: `pwsh -File x.py`
exits **64** with "the file does not have a '.ps1' extension", so this fails **loud and red**,
not silent. The silent failures are Task 3's globs, not this wave.

- [x] **1.1** `run-guards.ps1:191` selects an interpreter from the target's extension — **DONE
      2026-09-26** (`10e95d6dd`). Dispatches on the real file's extension: the `.ps1` branch is
      byte-identical, `.py` runs under `python`, anything else fails closed with a named refusal.
      `python` is resolved once at startup, `$code` is reset per guard (it was not, so a failed
      native call could inherit the previous guard's 0), and every child now runs with `$Root` as
      its CWD — a no-op for `.ps1` guards, mandatory for `.py` ones.
- [ ] **1.2** `verify-change.py` (ported from `.ps1`) can dispatch a `.py` `script` check. Measured
      refusal today: `BOUNDARY-MISSING: …/accept_lane.py`, whose text names the WRONG cause — the
      real blocker is that the dispatcher cannot launch a `.py` at all, so a caller adds a registry
      mapping and gets the identical message back.
- [ ] **1.3** `verify-change.py`'s two hardcoded `powershell -File` prefixes (registry-guard and
      session-boundary invocations)
- [ ] **1.4** `test-fast.ps1:45` dispatches its `guard-test-substrate` call by extension
- [ ] **1.5** `Directory.Build.targets:53` resolves a `.py` target, and its `FUSIONRPG0002` message no
      longer blames the game pack for a missing script
- [ ] **1.6** `publish-player.ps1:165` and `deploy-play.py:397-403` (the PS-hashtable-interpolated
      `pwsh -Command`) dispatch by extension
- [ ] **1.7** The three workflows' `run-guards.ps1 -Tier ci` lines and `ci.yml:446` still work —
      **PARTIAL**: all 25 ci-tier guards run green through the new dispatcher, but `ci.yml` itself
      still spells `run-guards.ps1`, and that is correct until 1.1's consumers are re-pointed.
- [x] **1.8** **Proof is "nothing changed":** the same guard suite green before and after — **DONE
      2026-09-26** (`10e95d6dd`). 25 guards, 0 red, exit 0, 180s, through the new dispatcher. The
      one red row that existed beforehand (`population-pin`) was proven pre-existing by running the
      pre-change runner extracted from git: identical `exit 1` in 82.1s against my 82.8s. It was a
      real P1 finding, not a false positive, and is fixed in the same commit.
- [x] **1.9** A new guard row pointing at a `.py` is executed by the runner — **DONE 2026-09-26**.
      Positive control: `overflow` names `gk-core/scripts/audit-overflow.py`; the runner executes it, exit 0,
      real output, and finds `src` when launched from a foreign CWD with `-Root` pinned. A **negative**
      control was also run, because a dispatch that always returned green would be worse than none:
      the same row temporarily pointed at a `.py` exiting 3 reported `exit 3`, runner exit 1,
      `guards failed: overflow`. Row restored, restore verified. The `.py` branch propagates a real
      exit code in both directions.

## Task 2: Shims and retirements

Cheapest first, and the first proof that Task 1 works. **Task 2.3 is done and is that proof.**

- [ ] **2.1** Move the `guard-doc-citations` registry row to `audit-doc-citations.py` (548 lines) and
      delete the 13-line wrapper
- [ ] **2.2** Same for `guard-magic-numbers` → `audit-magic-numbers.py` (348)
- [x] **2.3** Same for `guard-overflow` → `audit-overflow.py` (266) — **DONE 2026-09-26**
      (`10e95d6dd`). Registry row, the `overflow-audit` boundary owner row, and the two unfenced docs
      that named the shim all moved in the same commit; the 28-line shim is deleted. The shim's
      `OVERFLOW GUARD OK/FAILED` verdict string is asserted nowhere, so nothing depended on it. Its
      `Push-Location $Root` became the runner's contract (1.1) instead of each shim's private
      workaround. `.ps1` count 103 → 102.
- [ ] **2.4** Same for `guard-population-pin` → `guard-population-pin.py` (215) — already has pytest.
      ⚠️ Its shim passes `--root $Root`, so the repoint needs a registry `args` entry, not just a
      path swap.
- [ ] **2.5** Same for `guard-vocabulary-mirror` → `guard-vocabulary-mirror.py` (238) — already has
      pytest
- [ ] **2.6** `verification-boundaries.v1.json`: the 5 rows naming a wrapper move to the `.py`
- [ ] **2.7** `verify-change.ps1`'s direct call to `audit-doc-citations.py` is left alone — it already
      bypasses the wrapper
- [x] **2.8** Merge the 7 proven-unreferenced one-off deletions (633 lines), with each prose citation
      that named a now-missing file annotated `since deleted` — **DONE 2026-09-26** (`406b32f17`).
      Follow-up closed in `10e95d6dd`: the registry's `local-operational-scripts` exemption still
      named the pi-web service script (since deleted), so the table now has **zero** dangling paths.
- [ ] **2.9** Decide `bcu212-full-run.ps1` — it is **executed** by a Windows-live pytest and wired into
      CI, so deleting it turns CI red. Port or retire-with-its-test.
- [x] **2.10** `resolve-append-only.ps1` (RETIRED without a port, superseded by `union_append_only.py` — see the 3.5-series retirement record) needed a ~15-line port, not a delete: the existing Python twin
      is a *library* (unions two files) and does not carry the `MERGE_HEAD` precondition, the
      unmerged-path discovery, or the `git show :2:`/`:3:` extraction. `AGENTS.md` still points
      agents at the `.ps1`.

## Task 3: Checks wrappers and solo guards

- [ ] **3.1** The 16 `gk-core/scripts/checks/*.ps1` → `.py`, with `verification-boundaries.v1.json` repointed
- [ ] **3.2** `GeneratorCheckCiParityTests.cs:53-62` — the `InlineData` rows naming a `.ps1` are
      repointed **in the same commit** as 3.1
- [ ] **3.3** `GeneratorCheckCiParityTests.cs:26` — the `gen-*.ps1` glob currently matches **zero** and
      the CI-parity guarantee is passing vacuously. Rewrite it to read each module's machine-readable
      spec (`argv`, `working_directory`) instead of regexing a shell line; that also retires the
      `Push-Location` / `$LASTEXITCODE` regexes at `:100-119`
- [x] **3.4** `EnforcementRegistryGuardTests.cs:57` — the `guard-*.ps1` glob matched 28 of 29 and
      went vacuous on port. **DONE** (`fcdc4f4ff`): both extensions, via one named helper
      `DiskGuards(root)` that the invariant AND its own falsifier call, so they cannot drift apart.
      Proven by narrowing the helper back: the dedicated test goes RED while
      `R1_every_guard_on_disk_is_catalogued...` stays GREEN — which is the finding, because the
      main invariant cannot detect its own blindness. **The `session-boundary-check` half is NOT
      done**: it still escapes "every guard is catalogued" and needs its own owner row
- [ ] **3.5** Port the guards with no cross-tool coupling: `guard-open-identity`, `guard-stat-pairs`,
      `guard-funnel-delta`, `guard-actor-hub`, `guard-test-content-root`, `guard-clock-seam`
- [x] **3.5a** `guard-bench-compile` ported (`81b9b7a1c`): 17 code lines, the smallest real guard.
      Bounded `dotnet build` that could hang the tier, a `' error '` excerpt filter that needed a
      space on both sides, and a best-effort temp delete — the shape behind this repo's 65.5 GB
      leak. Both couplings repointed; 14 contract tests
- [x] **3.5b** `guard-dal` ported (`17d884e09`): the first port that **fixed** a defect rather than
      reproduce one. On one fixture the PowerShell original reported 4 findings where 3 were false
      positives (SQL named only in a trailing `//` comment or a `/* */` body); the port reports the
      1 true positive, at file:line. `gk-core/scripts/cscan.py` added as the SHARED comment stripper —
      three PowerShell copies had already drifted. Also: `-AllowlistFiles` matched on file NAME, so
      one entry silently exempted every `Foo.cs`; the capability is kept and the breadth is now
      reported. 23 contract tests. No boundary owned the script, so a `dal-guard` owner boundary
      was added
- [x] **3.5c** `gk-core/scripts/ps1-rename-sweep.py` (`023f2ffc7`): retiring `guard-dal` left **360
      dangling citations across 227 files** and 177 `audit-doc-citations` HIGH. The tail scales
      with how famous a tool is, so all 20 remaining ports inherit it. The sweep rewrites the
      **invocation form** too (`.\scripts\x.ps1` → `python scripts/x.py`), not just the path; dry
      run by default; refuses if the `.ps1` still exists or the `.py` does not; idempotent; bounded
      to explicit roots so `tasks/**` history is not rewritten. `177 HIGH → 0 HIGH`. Two gaps found
      by using it and fixed in the same commit: it globbed only `*.md` (so `architecture-map.html`
      kept a stale citation), and `AGENTS.md`/`CLAUDE.md`/`README.md` sit outside the default root
      and each carried a live invocation. It then refused a real run here for `PORT-MISSING` when I
      passed a registry id instead of a file stem — the refusal working on the actual user
- [x] **3.5d** `guard-secondary-no-unity` ported (`467a0baf0`): the first port where the right
      answer was to **change nothing**. It scans raw text, so a comment naming `UnityEngine` is a
      finding — a real false-positive source `cscan.py` removes in one call. Stripping comments
      would widen what the guard permits, and no repo statement earns that the way `guard-dal`'s
      did, so it is left and **both directions are asserted in the tests**, including one proving
      `cscan` *would* have suppressed it. The odd in-scope pattern `:\s*.*IEffectGrantPlugin` is
      carried verbatim (changing coverage is a scope change) and measured: it matches 3 files, all
      already in the plugin directory, so the second pass is **redundant on this tree, not dead**.
      21 tests, 6 subtests. 6 HIGH → 0 HIGH via the sweep
- [ ] **3.4a** **FOUND, NOT MINE, NOT FIXED — 4 red in `FusionRpg.Guard.Tests` that pre-date the
      guard ports.** `VerificationBoundaryWorkflowTests.{Integrity_guard_passes_on_the_current_
      registry, P6_the_real_registry_resolves_seedsmith_and_tuning,
      The_real_magic_number_audit_boundary_is_guard_only}` and
      `SplitCoreVerificationMappingTests.Planner_resolves_representative_split_core_files_to_area_
      owners_not_residual`. Cause MEASURED for the first: `VerificationBoundaryWorkflowTests.cs:38`
      allows `120_000` ms, and `guard-verification-boundaries.py` takes **67s standalone** with the
      full coverage walk — 56% of budget for one call, while `RunBoundaryGuard` is invoked by
      several tests inside a 22-minute suite that runs many guards at once. The guard itself
      returns `VERIFICATION BOUNDARY GUARD OK`, exit 0. So it is a **budget smaller than the work**,
      worsened by multi-agent contention, not a registry defect and not a port regression.
      Two candidate fixes, deliberately NOT chosen here: (a) pass `-SkipCoverageWalk` where the
      coverage walk is not what the test is asserting — the same flag `verify-change.py` already
      uses, and a correctness fix rather than a timeout change; (b) raise the budget. (b) inflates
      a timeout to make a test pass, which is the guard-weakening pattern the repo forbids, and it
      is also the Wave 3 answer (port the guard to Python) arriving by the back door. The 4th test's
      cause is NOT yet attributed. Owner of these tests: `test-verification-boundary`
      `guard-secondary-no-unity.ps1` (retired; now `guard-secondary-no-unity.py`) as a copy, which has no stripper at all. The real set is
      **five** — `guard-clock-seam`, `guard-debug-scope`, `guard-sim-fabrication`,
      `guard-single-writer`, `guard-test-substrate` — plus `guard-open-identity`, which does it
      inline with a line-prefix test. The list is marked as a reading with the grep that
      reproduces it. **Lesson: a plausible detail asserted from memory, twice now.** Verify with
      one command
- [x] **3.5e** `cscan.py`'s divergent-copy list corrected: it named
      `guard-secondary-no-unity.ps1` (retired; now `guard-secondary-no-unity.py`) as a copy, which has no stripper at all. The real set is
      **five** — `guard-clock-seam`, `guard-debug-scope`, `guard-sim-fabrication`,
      `guard-single-writer`, `guard-test-substrate` — plus `guard-open-identity`, which does it
      inline with a line-prefix test. The list is marked as a reading with the grep that
      reproduces it
- [x] **3.5f** The couplings a guard port actually has, learned by breaking three of them at
      once: the enforcement-registry row, the verification-boundaries owner row, a C# test that
      **shells** the guard, and — the landmine — **~45 test files across six projects that use a
      guard `.ps1` as their REPO-ROOT LANDMARK**. Deleting `guard-dal.ps1` (retired; now `guard-dal.py`) therefore broke unrelated
      tests in projects this session does not own. Marker repointed to `Directory.Build.props`,
      which this program will never delete. But 2 of the 45 walk-up loops RETURN the guard to
      execute, and rewriting those broke 11 tests (`OpenIdentityGuardTests`,
      `LawnRepositionSingleWriterGuardTests`) — reverted in `6682d3327`. The rule that follows:
      **port the guard and repoint its callers in the same commit; never pre-emptively repoint a
      path to a `.py` that does not exist yet.** Classify a call site by what its enclosing loop
      RETURNS — a repo-root finder returns `dir.FullName`, a script finder returns the path
- [x] **3.5g** `gk-core/scripts/ps1-port-census.py` (`4c04eb4d2`): runs the 3.5f census as a tool, so the
      lesson is executable rather than a note. Read-only, always exit 0, `--all` sweeps every
      remaining registry `.ps1`. **Every remaining port runs it FIRST.** It separates the MARKER
      sites (safe to repoint) from the SCRIPT sites ("do NOT repoint"), which is the distinction
      that caused the 11 failures, and it reports a coupling count of **0** as a missing mapping
      rather than omitting it. 12 tests against a throwaway git repo, so it does not break when the
      tree moves; falsified by inverting the discriminator, which turns the classification test red
- [x] **3.5h** `guard-stat-pairs` ported (`a8e68c7cf`): the first port run against the census, which
      returned **0 boundary owner rows** — a missing mapping found before anything broke. Proven by
      DIFFERENTIAL TESTING against the original: one fixture with a planted violation per rule
      gives **7 findings from each implementation, same rules, same names, same order, same exit**,
      plus byte-identical verdict on the real tree (63 rows). The fixture targets the four things a
      rewrite silently loses: group separation between `entries` and `prefixFamilies`,
      PowerShell's case-insensitive `-eq`, a boolean cap that is **not** a numeric cap
      (`isinstance(True, int)` is True), and whitespace-only-is-absent. Named refusals replace a
      bare `throw` on a missing catalog. 28 tests, falsified by dropping the bool exclusion (3 red)
- [x] **3.5i** `guard-open-identity` ported (`7fa8f1b0c`): the second census-first port, and the
      first with a **measured** behaviour change. The original's line-prefix comment filter
      scanned the BODY of a multi-line `/* */`, so a block comment containing both `EmpireId x;`
      and `switch (x)` was reported as a violation — in a guard whose own header says a doc comment
      naming these types is not one. Differential test: original 6 findings, port 5, the extra
      being exactly that false positive; real tree identical, 1534 files. The fix can only REMOVE
      false positives, and `cscan` preserves string literals so I2 stays as textual as the spec
      says (a test pins that a switch over a string literal is still not attempted — the port must
      not become a parser). Also folds one divergent PowerShell copy into `cscan.py`. 23 tests.
      **Census wording, made precise:** "do NOT repoint" means do not repoint to a *stable landmark*
      like `Directory.Build.props`; once the guard IS ported that same site must point at the `.py`

- [x] **3.5j** `guard-funnel-delta` ported: the first port whose **differential found a defect in
      shared code rather than in the port**, and the first to need a fail-closed change that
      reached the C# falsifiers.
      **Differential:** 16 findings from each implementation, same files, same patterns, same exit,
      0 divergences. The first pass reported 16 phantom divergences because the comparator did not
      normalise the path separator — .NET leaves `\`, `pathlib.as_posix()` writes `/`. A comparator
      that reports 16 differences when there are none will hide the one that matters.
      **The differential caught a wrong comment in `cscan.py`:** its docstring claimed every
      multi-line `/* */` body survives the whole-line filter. Measured: the `*` prefix is caught by
      the same test, so a CONVENTIONAL block comment is stripped in full, and only a body that does
      not begin with `*` survives. Corrected to the narrower true claim.
      **Three contract details preserved verbatim,** each because a tidy-up would change what the
      guard permits: matching is CASE-SENSITIVE (`.NET IsMatch` default), the Injector rule scans
      RAW text while the other two scan comment-stripped text, and `ctx.Bag.Grant` is listed
      alongside `Bag\.Grant` so one call yields TWO findings.
      **One deliberate divergence, and it reached the tests:** the original wrapped every scan in
      `if (Test-Path ...)`, so a wrong `--root` reported OK and exited 0. Here a missing tree is a
      named refusal (exit 64). That made three C# fixtures refuse instead of reporting a verdict, so
      `CreateFixture` now creates all three scan scopes — the fixtures were fixed, the guard was not
      weakened. 26 Python tests, 7 C#. Falsified: four mutations each turn it red (IGNORECASE,
      harmonising the raw-text asymmetry, stripping comments everywhere, passing on a missing tree).
      **Coupling 2 was 0 rows** for this guard, and the row it needed has to be a GLOB
      (`scripts/guard-funnel-delta.*`): naming the retired `.ps1` is refused as a stale exact path,
      and naming only the `.py` leaves `--deleted-paths` unmapped. `README.md` had no owner row at
      all, so it was added to `docs-and-assistant-config`, which already owned `AGENTS.md` and
      `CLAUDE.md`.
      **Sweep:** 92 citation lines across 71 files, plus 7 outside `docs/` the default sweep scope
      never covered (the tool only handles `.md`/`.html`, so the `.cs` prose citations and the
      root guides needed explicit `--root`/`--suffix`). All remaining references are `tasks/**` and
      `.claude/` briefs and acceptance artefacts — historical record, deliberately not rewritten.
      **Pre-existing defects found and fixed in passing:** `CLAUDE.md` carried a BEL (0x07) control
      character where the separator belongs, so the contributor guide named
      `scripts<BEL>udit-overflow.py` — a file that does not exist.
      **ATTRIBUTION — the content of this port is in `3307f0597`, and that commit's message does
      not mention it.** 87 of its 88 files are this port. The cause is the shared index: I staged
      the paths and then took several tool calls before committing, and another lane's bare
      `git commit` published the whole index. `git commit -- <paths>` limits *my* commit; it does
      nothing about another process's. Same incident as `1a376cc4e`/`5d296568f`, and the lesson is
      now written into `project-manager/SKILL.md` as its own commit — arrived at the hard way
      twice. **Mitigation for the remaining ports: stage and commit in ONE tool call.** Nothing is
      lost and nothing is rewritten (never amend); this entry is the correction.
- [x] **3.5k** `guard-actor-hub` ported: the port where a **transcription error shipped a false
      finding on the real tree**, caught before the original was deleted, and the port that
      established the `Alternatives` type.
      **The bug:** the original's Hub-construction check is
      `-notmatch CreateDefault -and -notmatch 'new ActorHub'` — AT LEAST ONE alternative. Written
      as a flat list of required patterns it reads as BOTH, and the port duly reported
      `UniqueActorHubCompose.cs` as not constructing a Hub — a file that calls
      `ActorHubBootstrap.CreateDefault` at :88. The original said OK on the same tree. Fixed by
      making alternatives a DISTINCT TYPE, so the difference is structural rather than a detail to
      remember: `Required` (must match) cannot be confused with `Alternatives` (any must match).
      **Contract note 1, and the reason it is written down per guard rather than per repo:** this
      guard matched with PowerShell's `-match`, which FOLDS CASE. `guard-funnel-delta` matched
      with `[regex]::IsMatch`, which does not. Copying the neighbour's `re.compile` line would have
      silently WIDENED this one to catch `derivedmodifier`, `APPLIEDCOMBAT` and `actorhub.resolve`.
      Case-folding is asserted both behaviourally and structurally (a test checks `pattern.flags`),
      so a future edit to one `re.compile` is caught even if no fixture exercises that pattern.
      **Contract note 2, an asymmetry that is the guard's purpose and not sloppiness:** a missing
      required file is a FINDING in R1/R4 (EntityApply.cs disappearing means the Hub call it was
      required to make disappeared with it) and NOT A CHECK in R7/R8/R9 (Program.cs disappearing is
      none of this guard's business). The original is inconsistent *within* R4 too — the break
      message carries `src/` and the missing message does not — and both forms are preserved.
      **Contract note 3:** the three allowlists are transcribed one-for-one, each entry carrying the
      reason it is there, and `BattleStatComposer` is asserted ABSENT so reintroducing a parallel
      composer cannot be waved through by a widened prefix.
      **Differential: 11 findings from each implementation, same files, same messages, same exit,
      0 divergences.** Every finding in the first run was a defect in MY FIXTURE, none in the port:
      `actorchannelmod` is a different word rather than a casing of `BattleChannelMod`; the
      case-fold case sat in a file not named `*Composer*` so R2 never scanned it; and `NoHubCtor.cs`
      is correctly CLEAN because R1 judges exactly two NAMED files. A fixture bug is still a bug —
      a wrong expectation would have been quietly agreed with by both sides.
      **The census missed three live citations**, which is the more useful finding: coupling 1 and 2
      know only `enforcement-registry.v1.json` and `verification-boundaries.v1.json`, and the sweep
      defaults to `docs/` with `.md`/`.html`. This guard was also cited by
      `gk-core/scripts/battle-responsibility.v1.json` — a SECOND registry — by another guard's own comment,
      and by `.kilo/command/*.md`. The checklist now says plainly that `git grep` after the sweep
      is the real check and the census is a briefing.
      **Two boundary rows added or extended:** `actor-hub-guard` as a GLOB for the same
      stale-exact-path reason as `funnel-delta-guard`, and `.kilo/**/*.md` added to
      `docs-and-assistant-config`, which already owned `.claude`/`.agents`/`.commandcode` and had
      simply never listed `.kilo`.
      Evidence: 26 Python tests, 3 C# guard tests, 7 Core tests, 31 Guard tests, 6 selected guards
      green including the ported one, audit-doc-citations --strict at 0 HIGH.
      Falsified: six mutations each turn the suite red — dropping `re.IGNORECASE`, dropping the
      lookbehind, making `Alternatives` demand all options, collapsing the R1/R4-vs-R7/R8/R9
      asymmetry, dropping the `TraitAtomSource` allowlist entry, and widening the `*Composer*` glob.
      **Four defects in my own test suite** on the first run, one of them instructive: a negative
      case written as `Required("A", ...)` matched the string `"class"` because of IGNORECASE, so
      the assertion passed for a reason unrelated to what it claimed to test. A fixture whose
      negative case passes accidentally asserts nothing.

- [x] **3.5l** `guard-single-writer` ported: the port that forced a THIRD comment-stripping
      policy into `cscan`, and the sweep defect that would have erased a port's own provenance on
      every remaining retirement.
      **THREE STRIPPER POLICIES, NOT ONE.** This guard read W1 as RAW text and W2/W3 as
      comment-stripped text, and its stripper was a third `Strip-Comments` copy that blanks the
      CONTENTS of a string literal so a pattern cannot match text inside one. That is neither
      `cscan.strip_comments` (keeps literals verbatim) nor `strip_whole_line_comments` (whole-line
      only). It is now `cscan.strip_comments_and_literals`, added under its own name rather than
      folded into a neighbour, and **verified character-for-character against the PowerShell
      original on 20 inputs** including doubled quotes, backslash escapes inside single-quoted
      literals, `http://` and `/* */` inside a literal, and unterminated comment and literal. 20/20
      identical. The distinction is load-bearing: a log message reading `"p.theHealth = 0"` is a W2
      finding under the kept-literal policy and nothing under the blanking one.
      **THE BUG THE DIFFERENTIAL FOUND.** `is_allowed_file` folded case, correctly, but the
      Pinned-List LOOKUP did not — so `entitystatwriter.cs` passed the membership test and was then
      judged against no list at all, every write reported as a violation of a list it was never
      measured against. PowerShell indexes a hashtable, and hashtable lookup is case-insensitive by
      default, so the original folds there too. `canonical_writer` is the folded lookup now.
      **The guard is case-SENSITIVE about patterns and case-INSENSITIVE about tables**, and both
      are asserted structurally so a future edit to one `re.compile` is caught even when no fixture
      exercises it.
      **TWO ASYMMETRIES PRESERVED, both of which a tidy-up would silently remove:** the three
      directory carve-outs (`Bridges/`, `Fx/`, `Hud/`) hide a file from W1 and from NOTHING else,
      so a VFX or HUD file is fully scanned by W3; and W1 does not skip `obj/`/`bin/` while W2/W3
      do, so a stale generated file is still a W1 finding. Both may be oversights in the original.
      Neither is mine to narrow.
      **Differential: 13 findings from each implementation, same messages, same exit, 0
      divergences.** Two of the pinned lists surprise and both surprises are the contract:
      `UniqueBoundLoadout.cs`'s list is EMPTY (every grant goes through the RPG-layer Funnel), and
      `EntityStatWriter.cs` may NOT write `theHealth` — that field belongs to
      `ZombieCombatFields.cs`, whose list is exactly (theHealth, theMaxHealth). The lists
      deliberately do not overlap.
      **A FIXTURE BUG FOUND BY A CASE-SENSITIVE FILESYSTEM.** The fixture carried
      `entitystatwriter.cs` and `EntityStatWriter.cs` as two files. On Windows they are ONE file, so
      the per-file table could not say which content it had and unlinking one name twice raised
      `FileNotFoundError`. The case-folding property moved to a unit-level test, which is where it
      belongs: it is a property of the lookup, not of a tree.
      **THE SWEEP WAS ABOUT TO ERASE PROVENANCE.** `ps1-rename-sweep.py` planned to rewrite
      `gk-fusion/scripts/guard-single-writer.py`'s own docstring — the "Replaces
      `guard-single-writer.ps1` (since retired)" sentence that the port standard REQUIRES so the reason for the
      deletion survives it. A port is not a citation, so a file whose stem IS a map target is now
      skipped, and the skip is REPORTED on stderr rather than looking like full coverage. Its
      summary also had to learn that a skipped file is not a changed file: it summed
      `f["changed_lines"]` over every entry and raised `KeyError` on the new shape.
      **A TEST THAT PINNED A POPULATION, NOT A CONTRACT.** `test_verify_change.py` used `README.md`
      as its stand-in for an unmapped path, and went red when the previous port gave `README.md`
      the owner row it should always have had — red on a FIX, not a defect. The probe is now
      `.editorconfig`, which is unmapped by the registry's own SCOPE (the rows cover code and
      documents; dotfile config is neither) rather than by accident, so a future boundary repair is
      unlikely to claim it.
      Evidence: 33 Python contract tests and 20 subtests, 15 C# tests across the three consuming
      classes, both implementations agreeing on the real tree, and audit-doc-citations --strict at
      0 HIGH. Falsified: seven mutations each turn the suite red, including the exact
      case-sensitive-lookup bug the differential found.

- [x] **3.5m** `cscan.strip_comments_preserving_layout` added, and `gk-core/tests/tools/test_cscan.py`:
      the shared scanner's FOURTH policy and its first committed contract test. The
      `guard-sim-fabrication` port is what forced this; it is recorded here rather than in 3.5n
      because the reference implementation is the point, and the guard is a separate lane.
      **The four copies are not one drifted function.** `cscan` now holds four policies, and the
      difference between them changes what a guard REPORTS rather than how it is written:
        `strip_comments`                      literals kept; a block collapses to one space
        `strip_comments_and_literals`         literal contents blanked; same collapse
        `strip_whole_line_comments`           whole-line only; line numbers kept
        `strip_comments_preserving_layout`    each comment char becomes a SPACE, so length and
                                               LINE COUNT are kept; literals kept
      Two questions pick between them, and both are in the checklist: may a pattern match text
      inside a string (a SQL/DAL boundary wants `strip_comments`, because a `CREATE TABLE` in a
      string is real SQL handed to a driver), and does the guard report a line number (then it wants
      the layout-preserving one, because under the collapsing policies a hypothetical `file.cs:412` is a line that
      does not exist in the source).
      **The new policy was verified 18/18 against the PowerShell original**, including the cases
      that separate it from its siblings: a multi-line block comment keeps its line count, a
      literal's `//` and `/*` are not comments, and an unterminated block or string is consumed to
      end of input rather than looping.
      **THE CLASSIFICATION ITSELF NEEDED THREE CORRECTIONS before it measured anything**, and that
      is the part worth keeping. Selecting a guard's stripper by SUBSTRING on `function
      Strip-Comments` matches `Strip-CommentsPreservingLayout` and then invokes a name that does
      not exist, which scores 0/11 against an error string. Selecting the FIRST top-level function
      picks `New-Allow` in `guard-clock-seam` and `Get-Baseline` in `guard-test-substrate`. And
      matching the sequences `//` and `/*` in the body finds nothing, because no PowerShell body
      spells them out - the scanner tests the CHARACTERS `/` and `*`. Every one of those reported
      a confident, wrong answer.
      **The shared scanner had NO test file** while four guards imported it. That is the gap this
      closes, and the class that matters most is `TheFourPoliciesAreDistinct`: a change that made
      two policies identical would leave every behaviour test green while changing what a guard
      catches. `EveryPolicyTerminates` checks each against eight hostile inputs, because a guard
      that hangs is a deploy that hangs.
      Evidence: 32 tests and 74 subtests, 4 mutations each turning it red - removing comment
      characters instead of spacing them, stopping the literal blanking, upgrading the whole-line
      filter to a trailing-comment skipper, and teaching the blanking policy to treat a backslash as
      an escape inside single quotes as well.

- [x] **3.5n** `gk-core/scripts/stage-fence.py`: the third cross-lane publish had a CAUSE, and this
      fixes it rather than the instance.
      **What happened.** `ace893432`, titled for the cscan policy, also published two
      `BuildPresets` test files belonging to a salvage lane - a real, substantive fix (a
      process-global tuning hub restored on every test path) that the commit message never mentions.
      Nothing was lost and nothing was rewritten. But the cause was mine, not the shared index's:
      I built the stage list from `git status` MINUS A DENYLIST of path fragments I had happened to
      learn - seedsmith, `.commandcode/taste`, ip-censor, numeric-types, union-append. That is a
      record of what I noticed, and it failed the moment a lane touched a path I was not told about.
      **A denylist fails open.** Every path is staged unless something excluded it, so the cost of
      a name I do not know is another lane's work in my commit. The FENCE inverts that: stage what
      the session record declares, and a path it does not cover is simply not staged. The failure
      becomes "a path I edited is missing from the commit" - visible, harmless, and fixed by adding
      one line to the record - instead of "a path I did not edit is in the commit", which is silent.
      **It also fails CLOSED on a dirty index.** If the index already holds a path the fence does
      not cover, the tool exits 2 and says which, because that is precisely the situation the shared
      index creates and the reason three commits here went wrong.
      Evidence: 10 tests and 5 subtests. The class that matters is the direction of the failure -
      `test_a_path_outside_the_fence_does_not_match` asserts that a `seedsmith` path, a
      `.commandcode` path, another session's record and a `BuildPresets` test are all left ALONE.
      A suite that only checked "my files get staged" would have passed under the denylist rule
      too, which is why it does not exist in that form.

- [x] **3.5o** `gk-core/tests/tools/test_registry_markers.py`: closes a gap the guard suite had, found by
      committing one.
      **A registry with merge-conflict markers reached HEAD and the integrity guard said OK.**
      `gk-core/scripts/verification-boundaries.v1.json` contained `<<<<<<< Updated upstream` / `=======` /
      `>>>>>>> Stashed changes`, from a stash-merge on this shared registry - the `union-append-only`
      lane's own subject. `guard-verification-boundaries.py` returned **OK**, because it validates
      structure and coverage, and a file carrying conflict markers still has valid structure and
      full coverage. Every structural check passed on a file a human reads as broken.
      **A fence answers "may I touch this", not "is this file sane."** The registry is in this
      session's fence as a disclosed crossing, `stage-fence.py` correctly staged it as in-fence, and
      nobody read the CONTENT because the path was authorised. Authorisation and validity are
      different questions, and only one of them had a check.
      **The consequence, which is the part that matters:** a marker inside a row's `paths` entry
      produces a boundary that matches nothing, so the planner is green and the path is unmapped.
      Silent green is the failure class this program keeps paying for, arrived at from a direction
      nobody was watching.
      The check is a test rather than a guard edit because the guard is still PowerShell and this
      program is porting it; when `guard-verification-boundaries` is ported the check belongs in the
      port and this file should shrink to a pointer. What must not happen is the gap closing over:
      nothing else in the tree looks for these markers, so an absence of complaints is not evidence.
      **Its own known limitation is asserted rather than hidden:** a `=======` inside a string is a
      markdown rule, not a conflict marker, and the check is line-based so it cannot tell them
      apart. `TheCheckCanFail` pins that as a documented false positive instead of pretending the
      check is clever.
      Falsified: planting the exact markers into the real registry turns 3 tests red; restoring
      returns 5 green.

- [x] **3.5p** `guard-injector-compile` ported: the smallest guard left, and the first whose
      retirement is about a TIMEOUT rather than a stream.
      **It had no timeout at all.** `& dotnet build ... 2>&1` waits forever, so a stalled restore
      turned a guard into a hang with no report. Every external call now carries a bounded
      `--timeout` (default 900s) and a timeout is a NAMED verdict with an exit code, not a raised
      traceback and not a silent pass. The original also lost the partial build output, which is the
      only evidence of where a build stopped, so it is kept.
      **EXIT 0 FROM THE COMPILER IS NOT A COMPILE, and that is the rule the guard exists for.**
      `dotnet build` exits 0 when the project decides it has no interop references and prints
      `NOT COMPILED - skipping FusionRpg.Injector.MelonLoader.39`. The original reads the log for
      that and calls it a FAILURE, and so does this: a guard that says OK for a project that declined
      to build is worse than no guard, because it gets trusted.
      **SKIP IS A THIRD VERDICT.** The original exits 0 for a skip AND for a compile, so a caller
      reading the exit code cannot tell evidence from its absence - which is the defect being
      retired. The exit code stays 0 so no caller changes, and the verdict (`OK` / `SKIPPED` /
      `FAILED`) plus `game_dir_source` go into `--json`. A test asserts BOTH halves: identical exit
      codes are only acceptable while the verdict differs.
      **The env precedence is transcribed, not tidied.** Cell, then loader, then `.env`. The middle
      one loses because the cell must be pvzrh-3.9 and a caller that set only the loader-wide
      variable to a 3.8.1 pack would compile the Int64 bridge against a 3.8.1 interop's Int32 fields.
      `resolve_game_dir` also REPORTS which variable decided the answer, because "which one" is the
      question an operator has when a build skips and a guard that cannot answer it makes the skip
      unactionable.
      **Two defects the port and its tests found.** `run_build` set `cwd=project.parents[2]`, which
      raises IndexError on a project path with fewer than three segments - a crash in a guard,
      surfaced by a test that passed a bare relative path. MSBuild resolves Directory.Build.props by
      walking up from the PROJECT, so the `cwd` was never needed; removing it is both correct and
      impossible to get wrong. And `ps1-rename-sweep.py`'s `apply_plan` skipped on the absence of
      `"error"`, so the deliberate port-provenance skip reached `entry.pop("_new")` and raised
      KeyError MID-RUN - leaving the sweep half applied and the remaining citations stale, with an
      exception as the only report. It now keys on `"_new" in entry`.
      **THE CENSUS REPORTED 0 DISPATCHERS and Directory.Build.props names this guard**, because the
      census scans `.github/` and the file is at the REPO ROOT - the same class of gap as the
      second registry and `.kilo` found on the actor-hub port. `git grep` remains the real check, and
      it is the third time that has been the thing which found what the briefing missed.
      **A COVERAGE GAP A MUTATION DEMONSTRATED.** Every timeout test replaced `run_build`, so the
      branch turning a `TimeoutExpired` into `timed_out=True` never ran: removing that branch left
      all 34 tests green. The suite now drives the real `run_build` with a patched `subprocess.run`,
      and the mutation bites. A coverage gap found this way is worth more than the mutation.
      Evidence: 36 Python contract tests and 2 subtests, 7 mutations each turning it red, the guard
      compiling the MelonLoader host for real against the same tree where the .ps1 also compiled,
      the four ported guards green, and audit-doc-citations --strict back at 0 HIGH.

- [x] **3.5q** `guard-game-profile` ported: the first port whose real work was making the
      BUILD speak Python, and the first guard where an UNKNOWN profile is deliberately allowed.
      **THE PORT IS NOT DONE UNTIL `Directory.Build.targets` EXECUTES THE `.py`.** A build that
      Execs a deleted `.ps1` is a broken build for every cell, so the port could not land half-way.
      The build now resolves the guard's path from its extension, and because the Python form
      differs in prefix AND argument spelling, both are resolved from the same flag rather than
      hardcoded: `--game-dir`/`--profile` versus `-GameDir`/`-ExpectedProfile`. The `.ps1` arm is
      kept as a FALLBACK so the file still builds on a branch where the port has not landed, which
      is the interpreter-aware shape `run-guards.ps1` already uses for the enforcement registry and
      the reason a port can land without editing every caller. It is also the THIRD place a
      deliberate `.ps1` reference now survives, and the checklist names all three so the next port
      does not "fix" one of them.
      **PROVEN THROUGH MSBUILD, not asserted.** Built the pvzrh-3.9 x MelonLoader cell against the
      real pack: exit 0. Then built the SAME cell with `-p:FusionRpgCellProfile=pvzrh-3.8.1`:
      exit 1 with `error FUSIONRPG0002` and the guard's own FAILED line. A build-time gate proven
      only on the green path is half-proven, and this one now has both.
      `publish-player.ps1:165` was the second caller, repointed in the same commit - a stale
      `& path.ps1` there fails only when a player pack is BUILT, which is the worst place to
      discover it.
      **AN UNKNOWN PROFILE IS ALLOWED, DELIBERATELY.** A profile id with no catalog row exits 0 and
      says so. The question this guard asks is "is this pack the version you said it was", and a
      profile nobody has fingerprinted has nothing to disagree with. It is REPORTED rather than
      silent, so the allowance is visible. A profile that EXISTS but carries no fingerprints is a
      different case and FAILS: there is a claim to check and nothing to check it against.
      **A MISSING GameDir AND A FINGERPRINT MISMATCH USED TO SHARE AN EXIT CODE.** The original
      `throw`s for a missing catalog or game dir and PowerShell exits 1 - the same code as a real
      mismatch - so "you pointed me at nothing" and "this is the wrong game version" were
      indistinguishable, and they have different fixes. They are separate named refusals now.
      **THREE RULES OF THE OR-MATCH, each of which a rewrite loses silently.** A pack matches when
      ANY signal agrees: the GameAssembly length OR any catalogued Assembly-CSharp length, and it
      need not be the same fingerprint on both. A MISSING `GameAssembly.dll` is length -1 and never
      0, or an absent file could match a row that happened to carry 0. The path/length zip is
      bounded by the SHORTER list, or a hand-maintained pair that disagrees in length turns every
      earlier pair into a mismatch. An absent, null or zero `gameAssemblyLength` SKIPS the signal
      rather than comparing against nothing.
      **A DUPLICATE PROFILE ID IS RESOLVED FIRST-WINS, and a test that asserted the opposite was
      wrong.** `Select-Object -First 1` takes the first row, so a later appended row cannot quietly
      widen what a profile accepts; the test now says that.
      **TWO FIXTURES COULD NOT SEE THE MUTATIONS THEY WERE MEANT TO CATCH**, found by falsifying
      rather than by reading. A zip-bound fixture whose FIRST pair matches never reaches the second
      index, so `min` and `max` were indistinguishable; and no fixture paired a missing
      `GameAssembly.dll` with a fingerprint carrying no `gameAssemblyLength`, so dropping the
      truthiness guard changed nothing. Both are now discriminating cases. A third mutation -
      resolving catalog paths without splitting on `/` - is PLATFORM-EQUIVALENT on Windows, since
      `pathlib` accepts forward slashes there, and that is reported rather than claimed as covered.
      Evidence: 35 Python contract tests and 11 subtests, 9 mutations attempted of which 7 bite and
      2 are platform-equivalent, the real-pack differential in both directions agreeing with the
      .ps1 on verdict and exit code, both build paths proven through MSBuild, and
      audit-doc-citations --strict back at 0 HIGH.

- [x] **3.5r** The fifteen `scripts/checks/gen-*.ps1` wrappers, as ONE batch: 15 `.ps1` retired
      in a single increment, which is the largest single reduction available and the clearest test of
      whether a shared runner is the right shape.
      **THEIR REAL DEFECT WAS THAT THEY WERE ONLY PARSEABLE BY LINE ORDER.** Each wrapper's command
      was "the line before the LAST `if ($LASTEXITCODE -ne 0) {{ throw `", a positional convention
      nothing enforced, and its working directory came from the first `Push-Location (Join-Path
      $Root "...")`. Reorder a line or insert a comment and the wrapper becomes unparseable - and
      the failure surfaced as a PARITY failure pointing at `ci.yml`, when the defect was in the
      wrapper. `GeneratorCheckCiParityTests` was a test of a convention, not of a contract.
      Each Python wrapper now DECLARES `CHECK`, `PREFLIGHT`, `WORKING_DIRECTORY` and `FAIL_HINT` as
      module-level constants, and the test reads those. A wrapper declaring nothing is reported by
      name instead of matching nothing.
      **A GLOB THAT MATCHES NOTHING IS NOT A PASS, so the test now asserts its own coverage.** The
      `.ps1` filter over a deleted set would return an empty list, every assertion would be vacuously
      satisfied, and fifteen absent wrappers would read as parity GREEN. `Assert.NotEmpty(wrappers)`
      closes that, and the reason is in the assertion's comment rather than in a commit message.
      **A MISSING TOOLCHAIN AND A FAILED CHECK ARE DIFFERENT EVENTS.** The `.ps1` `throw` for both,
      so a caller could not tell "the check found something" from "the check could not run", and
      they have different fixes. Refusals are now named with exit 64; a failure is exit 1.
      **ONE WRAPPER HAS REAL LOGIC, and the seam for it is one parameter.** `gen-content-validate`
      owns a scratch database directory, because CI's `$env:RUNNER_TEMP/...` resolves to nothing on a
      developer machine. `common.execute` takes an optional command override for exactly that, and it
      is an argv rather than a mapping - a mapping would have had to invent a rule for repeated
      tokens, and none is needed.
      **The registry needed a RECURSIVE rewrite, twice over.** The 15 `script` values sit nested
      inside row sub-objects, so a walk of the row's own keys found ZERO of them and reported success.
      The docs held three further shapes the first pattern missed: the `gen-<id>.ps1` PLACEHOLDER
      (angle brackets are not in a filename character class) and BARE filenames with no
      `gk-core/scripts/checks/` prefix. Found by grepping per wrapper name rather than trusting a pattern.
      Evidence: `GeneratorCheckCiParityTests` 3/3 green against the new shape, `gen-resource-ownership`
      passing a REAL run, both refusal paths exiting 64, `--json` carrying the rendered command, and
      audit-doc-citations --strict at 0 HIGH. `gk-core/scripts/checks/common.py` states once why the
      PowerShell form was retired; each wrapper points at it rather than repeating the argument.

- [x] **3.5s** `cscan`'s FIFTH policy,
      `strip_comments_and_literals_preserving_layout` — the enabler for `guard-battle-responsibility`,
      which dot-sources the retired `lib/SourceText.ps1` and so could not be ported without it.
      **THE TWO AXES ARE INDEPENDENT, and that is the finding.** Whether a pattern can match text
      inside a string is one axis; whether the source's own SPACING survives is the other.
      `Log("p.theHealth = 0")` separates the first. A block comment between two pattern tokens
      separates the second, because the collapsing policies turn it into ONE space where the
      layout-preserving one leaves one per character — and a `\s{3,}` quantifier then stops
      matching. The battle-responsibility guard asks for both at once, which is why a fifth policy
      was added rather than the second being stretched. `cscan`'s table is now five rows, and the
      module docstring says why the number is a reading rather than a preference.
      **A CORRECTION TO THE RATIONALE, measured rather than asserted.** This entry first claimed the
      layout half was required "because findings cite a line number". **That was false**: the guard's
      findings cite a FILE (`second owner in '<path>'`), never a line. And the truth is weaker than
      the claim — all 6 patterns in `battle-responsibility.v1.json` use `\s*` (zero-or-more), which
      matches whether a comment became one space or five, so **no pattern in the register today
      distinguishes the two policies**. A `\s{3,}` fixture across a block comment does. So the
      layout half is FIDELITY to the original's choice, not a current requirement; the port honours
      it because substituting the collapsing policy would be a latent behaviour change that the next
      whitespace-sensitive pattern would discover, with no test able to say when. Recorded as a
      correction rather than an amendment, per the no-amend rule.
      **Verified 23/23 against the original**, with the length and line-count invariant checked on
      every probe, including the two behaviours no other policy has: `@"..."` verbatim strings, and
      an unterminated literal that STOPS AT THE NEWLINE. That second one is the opposite choice from
      `strip_comments_preserving_layout`, whose own original consumes to end of input; both are
      transcribed and each is right for the guard that carries it, because a stray apostrophe would
      otherwise blank every following line and turn a guard silently blind.
      **A BRANCH NO TEST CAN PIN, found by falsifying rather than by reading.** The `""` escape
      inside a verbatim string is DEFENSIVE: the scan leaves the verbatim string at the same place
      with the branch on or off, and everything after it is blanked either way. Six candidate inputs
      — including ones carrying a `//`, a `/* */` and a following real literal — produce IDENTICAL
      stripped text. A mutation dropping the branch left all 41 tests green, and the first
      explanation I reached ("a coverage gap") was wrong: the branch is simply not observable
      through the output, because the output is all a guard ever sees. It is kept because the
      original has it and a scanner that mis-tracks its own position is a latent bug. The test that
      appeared to cover it now asserts only the OBSERVABLE consequence (the literal's contents do
      not survive) and says in its comment why it does not claim the branch. A test that cannot fail
      is worse than no test, and this one had to be corrected rather than deleted.
      Four other mutations each turn the suite red: dropping `@"` recognition, letting an unterminated
      literal consume to end of input, and removing rather than blanking comments.
      Evidence: 41 tests and 102 subtests, 23/23 differential against the PowerShell original.

- [x] **3.5t** `guard-battle-responsibility` + `lib/SourceText.ps1`, ported together — **2 `.ps1` retired
      in one commit**, and the pair was the reason they had to go together: the lib had exactly one
      consumer, so porting the guard without it was impossible and porting the lib without the guard
      would have left a shared helper with no user.
      **Differential: 21 fixtures, one per rule, identical in exit code and every emitted line.** The
      rules each got a fixture: one owner, a second owner, an owner that owns nothing, a `banned`
      shape still spelled by its own owner, a `banned` shape nobody writes, an allowlist entry with
      and without a module, a row with no patterns and with a note, case folding, a pattern inside a
      string / comment / verbatim string, an apostrophe in a comment, scan roots, the empty-`scan`
      fallback, build output, several mechanisms, and an empty register. Two normalisations were
      needed and both are traps: PowerShell leaves `\` where `pathlib` writes `/`, and `Join-Path`
      with a forward-slash argument produces a MIXED path. The missing-register refusal is compared on
      its CONTRACT (exit 1, FAILED, the path named) rather than its prose, because naming the refusal
      is the port standard the original did not meet.
      **The rationale I first wrote was wrong, and measuring it is what caught that.** The port
      docstring claimed the layout-preserving stripper was required "because findings cite a line
      number". False: the guard's findings cite a FILE (`second owner in '<path>'`). And the true
      answer is weaker than the claim — all 6 patterns in the register use `\s*` (zero-or-more),
      which matches whether a comment became one space or five, so **no pattern in the register today
      distinguishes the two policies**; a `\s{3,}` fixture across a block comment does. So the
      layout half is FIDELITY to the original's choice, not a current requirement, and the port
      honours it because substituting the cheaper collapsing policy is a latent behaviour change that
      the next whitespace-sensitive pattern would discover with no test able to say when.
      **Three real defects, all found by doing the work rather than by reading.**
      (1) **A FENCE VIOLATION.** `ps1-rename-sweep.py --root .claude` rewrote **1,180 files across
      ~20 other sessions' worktrees**. They are git-IGNORED, so `git status` showed nothing and no
      commit could have carried the damage; it was caught only by reading the tool's own `--json`,
      and undone by hand. Undoing it is where the cost showed: a full `rglob` over that tree does not
      finish, and a blanket `git checkout` inside a shared worktree would have destroyed the other
      session's uncommitted work — which this repo has already paid for once. The tool now asks git
      for the linked worktrees and PRUNES them (`dirnames[:] = []` at the directory level, so a
      directory never entered cannot be written to), refuses a `--root` that points into one, and
      names each pruned tree in the envelope. It is also **faster for the reason that matters**:
      pruning at 1.3s versus 63.5s enumerating-then-filtering. `ps1-rename-sweep.py` had **no test
      file at all** until now; `gk-core/tests/tools/test_ps1_rename_sweep.py` adds 14, first among them the
      fence.
      (2) **A PRUNED TREE WAS BEING MEASURED.** The first fix counted the files inside each excluded
      worktree in order to report "candidates left alone" — which meant walking the very trees the
      guard exists to avoid, and publishing a number read out of a tree the run had refused to read.
      That is the same error class as quoting a population, so the count is gone: a pruned worktree
      is NAMED (`"action": "pruned-not-entered"`), not measured.
      (3) **A REFUSAL THAT REACHED NOBODY.** `ROOT-MISSING` printed to stderr and returned 1 without
      emitting its `--json` envelope, while the other four refusals did — so a machine caller got an
      EMPTY stdout and a non-zero exit, indistinguishable from "the sweep found nothing to do". That
      is the silent-green reading, wearing a Python costume. Now every refusal honours `--json`.
      **Coupling 2 was refused by the registry's own integrity guard, which is the guard working.**
      Putting `gk-core/scripts/cscan.py` in the new owner row made it ambiguous against `dal-guard`, and
      `verify-change` refused the plan outright. This has bitten the repo TWICE before, and the
      recorded precedent was to drop the weaker claim. Here the claim was TRUE — the port genuinely
      imports the scanner — so the repair taken instead is the better one: the path keeps its single
      owner and that owner's `guards` array widens to list BOTH guards, which a row may do
      (`battle-effect-math` already lists two). Dropping it, the previous repair, would have left an
      edit to the scanner selecting only `dal`.
      **FALSIFIED, and one of the five first appeared to pass.** Five mutations of the new fence code
      were each turned red: un-pruning the walk, letting a `--root` into a worktree through,
      `ROOT-MISSING` dropping its `--json`, the worktree lookup becoming a string-prefix test, and an
      unknown worktree list being read as an empty one. The fifth initially "bit" only because my
      replacement broke the syntax, which is a test that cannot fail for the reason it claims - so it
      was redone cleanly (`if False:` guard rather than a mangled literal) and only then counted: 1
      failed, 5 passed, the failure being `WORKTREE-LIST-UNAVAILABLE` no longer raised. A mutation that
      turns the suite red because the code no longer parses has demonstrated nothing, and reporting it
      as a kill would have been the same class of error as the test that cannot fail.
      **A COST WORTH READING: un-pruning the walk took the suite from 6s to 18m53s.** That is the
      prune's whole value in one number - the enumerate-then-filter version was CORRECT and walked 20+
      complete checkouts including their `bin`/`obj/` before throwing the result away.
      Evidence: 21/21 differential, 37 new contract tests for the guard, 14 for the sweep, 5/5 falsified, 675 tests
      and 270 subtests in `gk-core/tests/tools` green, `run-guards -Only battle-responsibility` exit 0 from
      the `.py`, `verify-change` selecting the boundary for BOTH the deleted `.ps1` (via the `.*`
      glob) and the new `.py`, and `audit-doc-citations --strict` at 0 HIGH.

- [x] **3.5u** `guard-narrative` (151 lines) — the smallest remaining guard body, and the first
      where the census was wrong **twice** in the same run.
      **Differential: 11 fixtures, one per rule, identical in exit code and every emitted line**, with
      the two DECLARED divergences accounted for: the flag's spelling and the move of findings to
      stderr. A third is reported rather than hidden — a harness that merges stdout first sees the
      verdict BEFORE the diagnostic note, where PowerShell's single stream printed the note first, so
      four fixtures compare equal as multisets and differ in order. Sorting them away silently would
      also hide a genuine reordering, so the harness names it per case.
      **A BUG IN MY OWN HARNESS, caught by the fourth fixture disagreeing.** The PowerShell side was
      never given `-RunTraitFilter`, so check 3 ran on the Python side ONLY and one case compared a
      skip against a run. A differential that does not drive both implementations identically proves
      nothing, and it looked like a behavioural divergence rather than a harness bug.
      **A REAL DEFECT THE TEST CAUGHT IN THE PORT: `--json` WAS UNPARSEABLE.** The "trait filter NOT
      run" note went to stdout ahead of the envelope, so `json.loads` failed on it — the process said
      everything and the machine reader got nothing, which is the silent-green shape the standard
      exists to remove. The note now goes to stderr in both modes; the envelope's
      `trait_filter_run: false` already said the same thing to a machine.
      **COUPLING 2 WAS ALREADY BROKEN, and the port is what made it visible.** The `guard-narrative`
      owner row existed and carried `guards: []` — so no edit under it ever reached the guard, and
      `scripts/guard-narrative*.ps1` matches nothing once the script is deleted. **The narrative guard
      was unreachable through `verify-change` before this port touched it.** The row now claims the
      `.py` glob plus both test files and carries `guards: ["narrative"]`, and `verify-change` selects
      it for the deleted `.ps1` and the new `.py` alike. The failure mode is precisely the one
      coupling 2 exists to close, and it had been open the whole time.
      **THE CENSUS MISSED A PASSTHROUGH FLAG — the fourth time it has done so.** It reported "0 CI /
      dispatcher" for this guard, and the registry's `args.ci` carried `-RunTraitFilter`. Repointing
      only the script extension would have shipped CI invoking `python guard-narrative.py
      -RunTraitFilter`, i.e. an argparse error on every run. The census is a briefing; `git grep` and
      reading the registry row are the check.
      **THE PART A MECHANICAL RENAME MISSES.** `NarrativeGuardContractTests` asserted its three
      falsifier findings on **stdout**. With findings moved to stderr, stdout is EMPTY on a failing
      run, so those assertions would have passed **vacuously** — the silent-green shape, inside the
      very tests written to catch it. They now read stderr, and the two OK assertions stay on stdout.
      That class also produced a fixture bug here worth naming: `classes={}` in a test helper means
      "create no class files", so the test exercised the missing-class rule while claiming to check
      the passing one.
      A TIMEOUT TEST THAT COULD NOT TIME OUT: `dotnet test` on a stub `<Project />` fails in a few
      hundred milliseconds, so a one-second budget never fires and the branch is never entered. The
      timeout path is now exercised against a REAL csproj. The original shelled `dotnet test` with no
      timeout at all — a wedged test host hung the guard forever, and a hang is not a verdict; the
      port takes `--dotnet-timeout` and treats expiry as a named refusal.
      **ONE CITATION REPOINTED BY HAND, LINE NUMBER INCLUDED.** `audit-status-vfx-identity.ps1` cited
      `guard-narrative.ps1:130` (retired; now `guard-narrative.py`) in a comment about "a filter that matches no test exits 0" — the exact
      lesson this guard exists to enforce. The mechanical rename would have left a deleted path with a
      plausible-looking line number. **Left alone deliberately:** `npc-story-events-ledger.jsonl` and
      `npc-story-events-1.json` still name the `.ps1`; an append-only ledger and another session's
      record are evidence of what was true at the time, and rewriting either destroys the thing it
      exists to preserve.
      **FALSIFIED 11 WAYS, AND THE ONE THAT MISSED WAS A REAL GAP.** Ten mutations turned the suite
      red on the first pass. The eleventh did not: **deleting the `is_file()` check left the guard
      FAILING anyway**, because the read then raised and the *unreadable* branch reported it instead —
      so the verdict was unchanged and a verdict-only assertion could not see the difference. The
      mutation passed a suite that claimed to cover the rule. The two are not the same defect to
      whoever reads the output: a class that is ABSENT is a committed-row problem, a class that cannot
      be READ is a permissions or checkout problem, and they lead to different fixes. A test was added
      that pins them as distinguishable, and the mutation then bites.
      **A HARNESS CRASH THAT LOOKED LIKE A SKIP.** The first falsification attempt died with
      `re.error: bad escape \s` — `re.subn` reads escapes in the REPLACEMENT template, and the
      replacement carried `\s`. Had that been summarised as "skipped" it would have read as a coverage
      gap that did not exist. A callable replacement makes it literal.
      Evidence: 11/11 differential, 38 contract tests, 11/11 mutations falsified, 5/5 C# tests,
      `run-guards -Only narrative` exit 0, 712 tests and 289 subtests in `gk-core/tests/tools` green,
      `audit-doc-citations --strict` at 0 HIGH.

- [x] **3.5v** `guard-power` (161 lines) — **THREE FAIL-OPEN HOLES CLOSED, one of which made the guard
      point at files that do not exist.** None was found by reading; all three were found by the
      differential, and the third only because the harness was made to run the way production runs.
      **Differential: 27 fixtures identical in exit code and every emitted line, plus 5 DECLARED
      divergences where the port catches what the original missed.** A declared divergence is asserted
      *directionally and per finding* — "the port carries a G3/G4 finding the original does not" — not
      by exit code. The first version asserted "the original exits 0 and the port exits 1" and it
      FAILED while the claim it tested turned out to be correct: the fixture exited 1 on both sides
      because an unrelated G2 finding fired. An assertion that cannot fail for its own reason is the
      error this suite exists to catch, and mine did.
      **HOLE 1 — one unlocated scale licensed the whole repository.** `$null -split ',\s*'` yields one
      EMPTY string, and `'anything'.StartsWith('')` is true, so a single `inventory.json` row with no
      `location` satisfied G3 for every file. Confirmed against PowerShell 5.1 directly rather than
      inferred, because the claim is that the original is broken and that needed checking. An unlocated
      scale is now a finding. The shipped inventory is clean (33 scales, 0 unlocated), so the hole
      closes without reddening the tree — and a test asserts that cleanliness, so the claim stays true.
      **HOLE 2 — a tuning file missing a `curve` field read as ZERO and could PASS.** `[long]$curve.bMilli`
      on an absent property is 0, and 680000-80000 divides by 20 exactly, so a file that does not state
      its own curve passed G4 — the one check whose entire purpose is not trusting what the file claims.
      A missing, non-numeric, fractional or boolean field is now a finding. The bool case is a Python
      trap worth naming: `isinstance(True, int)` is True, so without an explicit guard a `true` would
      read as 1 — a value that happens to divide a pin exactly.
      **HOLE 3 — the reported path was often a file that does not exist.** Every finding interpolated
      `$_.FullName.Substring($Root.Length)`, and `Get-ChildItem` returns a canonicalised path while
      `$Root` is whatever the caller spelled. Under an 8.3 short root the slice dropped characters:
      measured, the original reported `G4 pin\data\tuning\power-scale.v9.json` for a file living at
      `g4-broken-pin/data/tuning/…` — a path an operator cannot open, from a guard whose whole job is to
      point at a file. `Path.relative_to` cannot mis-slice, so every finding is built from it, and a test
      asserts that every reported path resolves to a real file. **This one cost four false "divergences"
      before the harness was right:** `tempfile` returns the 8.3 form, so passing it verbatim reproduced
      the mis-slice in EVERY fixture and made the original report every listed inventory entry as
      unlisted. The comparison now passes the RESOLVED root, which is what production does, and the
      mis-slice is one case that asks for the short form on purpose.
      **A DEFAULT ALLOWLIST THAT WAS UNREACHABLE, caught by the port's own output.** `main()` passed
      `[]` when the flag was absent and `check()` tested `is not None`, so the five reasoned allowlist
      entries were silently dropped and the guard reported SIX false positives on the real tree. The
      allowlists are the safety valve; losing them turns a working guard red. Absent (`None`) and supplied
      empty (`[]`) are now different, asserted on `check` where the sentinel is consumed.
      **THREE CASE CONVENTIONS IN ONE SCRIPT, AND TWO OF THEM IN ONE PREDICATE.** G1 folds (`-match`);
      the G2/G3 signature folds (inline `(?im)`); the body-window test folds (`-notmatch`); and in the
      inventory test `$relFwd -eq $_` folds while `$relFwd.StartsWith($_)` is ORDINAL and does not. Two
      halves of a single `Where-Object` disagreeing is the detail a port gets wrong by reflex, so the
      pair is pinned in two adjacent tests that say so.
      **THE SWEEP KNEW TWO INVOCATION FORMS AND NEEDED A THIRD.** `pwsh -NoProfile -Command
      "& './scripts/guard-power.ps1'"` matched nothing: the `-File` rules want `-File`, and the
      bare-path rules' lookbehind rejects the `./` prefix. Rewriting only the path would have left
      `pwsh -Command "& './scripts/guard-power.py'"` — **PowerShell handed a Python file**, which is
      worse than the stale citation it replaced because it READS as updated. The whole invocation is now
      rewritten, `slash-invocation` accepts `./`, and 5 tests cover the shapes, including the property
      that matters: after a sweep nothing may still be a PowerShell wrapper naming a `.py`.
      **98 prose citations, and the sweep's default suffixes are `.md`/`.html`.** A first pass over docs
      and tasks fixed 72; `git grep` then found 31 more in **`.cs` doc comments and `.json` notes**,
      including the one in `docs/architecture/power/inventory.json` — the register G3 itself reads. Seven
      of those are crossings into paths this fence did not carry, disclosed and added.
      **Left alone deliberately:** `empire-progression-ledger.jsonl` (append-only gate records), this
      session's own fence entry (needed for `--deleted-paths`), and the port's provenance sentence.
      Evidence: 27/27 differential, 5 declared divergences, 55 contract tests, 9/9 C# tests driving the
      `.py`, 774 tests and 301 subtests in `gk-core/tests/tools` green, `audit-doc-citations --strict` at 0 HIGH.

- [x] **3.5w** `guard-repo-boundary` (184 lines) — **THE HOLE THAT MATTERS MOST FOR CI, and two C#
      fixtures that were passing because of it.**
      **B3 RAN GIT WITH `2>$null`, SO AN UNRESOLVABLE BASE REF REPORTED GREEN.** Measured against the
      original before writing a line of the port: `-BaseRef no-such-ref-xyz` printed the OK verdict and
      exited **0**, while git was saying `fatal: ambiguous argument 'no-such-ref-xyz': unknown
      revision`. Empty stdout was read as "nothing changed", so a typo in CI's base reference disabled
      the whole of B3 and reported success. A guard that passes without checking is the exact failure
      this program exists to eliminate, and this one did it silently.
      **Differential: 18 fixtures identical in exit code and every emitted line, plus 4 DECLARED
      divergences where the port catches what the original missed** — the bad base ref, a namespaced
      csproj PowerShell's `//ProjectReference` cannot match, a malformed csproj that threw, and B2's
      absolute path. Run BEFORE the deletion, which is the only order in which it can be run.
      **FOUR B3 FIXTURES WERE VACUOUS, AND BOTH IMPLEMENTATIONS AGREED.** They committed their change,
      so `git diff HEAD` — a WORKING-TREE diff — saw nothing, and four cases named "modified
      tasks/plan.md" and "added root SPEC.md" were asserting a CLEAN run. Both sides agreed, so the
      differential called them `ok`. This is the differential's blind spot stated plainly: it proves the
      two implementations agree, not that a fixture means what its name says. A fixture bug is still a
      bug, because a wrong expectation gets quietly agreed with by both sides.
      **TWO C# FIXTURES WERE GREEN BECAUSE OF THE HOLE.** `NewCleanFixture` built a plain directory with
      no git repository; the retired guard's suppressed git call made B3 unanswerable and it reported
      clean, so `The_clean_fixture_alone_passes` and the `InternalsVisibleTo` regression test passed for
      the wrong reason. The port reports an unanswerable B3 as a named finding and they went red. Their
      INTENT was unaffected, so the FIXTURE was made answerable — a seed commit — rather than the
      expectation weakened, and `An_unanswerable_B3_is_reported_rather_than_ignored` was added so the
      hole cannot return. Weakening the assertion would have left the defect in place with a test
      asserting it, which is worse than no test.
      **A WHOLE-RUN REFUSAL WAS THE WRONG SHAPE, found by those five red C# tests.** The first fix made
      an unanswerable B3 refuse the entire run — and the refusal printed no B1/B2 findings, so five tests
      could not see the thing they exist to check. **B1 and B2 are filesystem questions that work on any
      tree; only B3 needs git.** So an unanswerable B3 is now a finding naming the refusal plus a
      `refused` field in the envelope, the verdict is still FAIL, and the operator sees both the real
      violations and the reason the third check could not run. The hole is closed by being loud, not by
      being silent in a different place.
      **B2's raw-text scan is transcribed, not improved.** A `using UnityEngine;` inside a COMMENT is
      flagged, and that over-match is the contract: narrowing it would let a real reference hide behind
      a comment. A test says so explicitly so a later reader does not "fix" it, and a companion test
      pins the other side — a word merely CONTAINING a pattern (`usingUnityEngineHelpers`) is not
      flagged — so the over-match cannot become a blanket match.
      **A NAMESPACED CSPROJ USED TO PASS B1 VACUOUSLY.** PowerShell's `SelectNodes("//ProjectReference")`
      matches no namespaced element, so such a csproj yielded zero references and B1 found nothing to
      object to. The port matches the local tag name. No shipped csproj carries a namespace, so this
      changes nothing today and prevents a silent pass if one ever does.
      Evidence: 18/18 differential plus 4 declared divergences, 37 contract tests, 11/11 C# tests
      driving the `.py`, 811 tests and 313 subtests in `gk-core/tests/tools` green, `run-guards -Only
      repo-boundary` exit 0, `verify-change` selecting the `repo-boundary-guard` boundary for both the
      deleted `.ps1` and the new `.py`, and `audit-doc-citations --strict` at 0 HIGH.

- [x] **3.5x** `guard-generated-seed` (195 lines) — **FOUR COUPLINGS beyond the usual two, and a
      silent no-op I introduced and the differential caught.**
      **Differential: 26 fixtures identical in exit code and every emitted line, plus 3 DECLARED
      divergences** where the original THREW (the CI precondition, range+base-ref together, a git
      failure) and the port names the refusal. **No fail-open divergence is expected from this guard,
      and that asymmetry with its sibling `guard-repo-boundary` is the finding:** this one's
      `Invoke-GitLines` threw on a non-zero git exit, so it already failed closed, and the
      differential asserts the ABSENCE of a hole as well as the presence of equivalence. The port does
      not get credit for fixing something that was not broken.
      **A SILENT NO-op I INTRODUCED.** `check()` returned the CI-contract result whenever no range and
      no base ref were given, with no reference to the flag — and working-tree mode is the DEFAULT, so
      the guard inspected nothing locally and printed a clean verdict. A guard that cannot tell "not
      asked" from "asked and forbidden" is worse than one with no CI contract at all, because it looks
      like it is working. The differential found it as 25 unexplained divergences with the port
      reporting "no changes" on trees the original BLOCKED. The contract is now gated on the flag, and
      both halves are asserted: a hand-edited corpus file is caught with no flags, and the CI contract
      still refuses.
      **FOUR COUPLINGS, THREE OF THEM OUTSIDE THE FENCE, and the census only found one.**
      (1) `args.ci` is a PASSTHROUGH carrying the interpreter's flag spelling — repointing only `script`
      would have shipped CI invoking `python guard-generated-seed.py -RequireExplicitRange -Range <r>`,
      two argparse errors per run. (2) `run-guards.ps1:102` HARDCODED `@('-Range',
      '-RequireExplicitRange')` to drop the switch on a non-git fixture; the list now carries BOTH
      spellings, because the runner still launches PowerShell guards and now Python ones, and a
      one-spelling list would silently stop dropping on the other. Splitting that list across lines is
      a PowerShell **ParserError**, and `run-guards` runs every guard — caught only by RUNNING it.
      (3) `.github/workflows/release.yml` invoked the guard DIRECTLY; the step stays `shell: pwsh`
      because two sibling steps in the job still need it, so that one line now runs the `.py`.
      (4) `.github/workflows/ci.yml` named the flag only in a COMMENT, and
      `VerificationTopologyTests` asserts that comment — so the comment was repointed rather than the
      assertion weakened.
      **TWO PLACES POWERSHELL'S LANGUAGE LEAKS INTO A PREDICATE, BOTH TRANSCRIBED.**
      *Member enumeration:* `$doc._meta` on a top-level ARRAY returns each element's `_meta`, so the
      original blocks `[{_meta:{model:m}}]`. A naive `isinstance(doc, dict)` port does not. Narrowing
      is the wrong direction for a guard whose job is to notice provenance — "we saw it and did not
      look" is the failure mode — so the enumeration is reproduced and the reasoning recorded.
      *`Sort-Object -Unique` dedups CASE-INSENSITIVELY*, so a plain `set` keeps `A.json` and `a.json`
      as two entries, changing the count the verdict reports and double-reporting a file.
      **TWO FIXTURE BUGS, THE SECOND TIME THE SAME CLASS.** The corpus files were written BEFORE the
      seed commit, so every generated file was committed before the guard ran and the working-tree
      diff could not see it — and both implementations agreed on a clean run, so the case named
      "generated-with-provenance-and-no-generator" was asserting the opposite of its name. A
      differential proves the two agree; it does not prove a fixture means what its name says. A second
      case then used `TOOLS/seedsmith/x.py`, which matches no `^gk-forge/tools/seedsmith/seedsmith/adapters/…`
      pattern, so the case testing case-insensitivity of SOURCES tested nothing and read `ok`.
      **A VERDICT LINE WITH NOTHING AFTER IT.** `commit_range or base_ref` is empty in working-tree
      mode, so the clean line read `no changes vs ` with nothing following — the kind of small
      wrongness that makes a log line unusable.
      **A BOUNDARY verificationId WITH NO TRAIT.** The new owner row named `guard.generated-seed` and
      the registry's integrity guard refused the WHOLE registry, which would have blocked every
      agent's scoped verification. `VerificationTopologyTests` carries `guard.verification-topology`,
      so the class now carries a second `VerificationId` trait — a class may carry several, and this
      is the second time a port has had to add one.
      Evidence: 26/26 differential plus 3 declared divergences, 40 contract tests, 10/10 C# tests
      driving the `.py`, 851 tests and 328 subtests in `gk-core/tests/tools` green, `run-guards -Only
      generated-seed` exit 0, `verify-change` selecting the `generated-seed-guard` boundary for both
      the deleted `.ps1` and the new `.py`, the release.yml invocation smoke-tested, and
      `audit-doc-citations --strict` at 0 HIGH.

- [x] **3.5y** `guard-clock-seam` (242 lines) — **the second boundary row that selected NOTHING**, and
      a real bug the contract test found in the port itself.
      **Differential: 18 fixtures identical in exit code and every emitted line INCLUDING the counter
      summary, plus 2 declared divergences.** The summary is compared deliberately: it carries six
      counters, and a port that agrees on the verdict while disagreeing on how many reads it allowed is
      not a port.
      **THE SECOND `guards: []` BOUNDARY ROW, after `guard-narrative`.** `clock-seam-guard` existed and
      carried an EMPTY `guards` array, so no edit under it ever reached the guard: **clock-seam was
      unreachable through `verify-change`**, exactly as narrative was. The row now claims the `.py`
      glob plus its test and carries `guards: ["clock-seam"]`. The shape is identical both times — an
      owner row that exists and selects nothing — which is worth naming as a PATTERN rather than two
      coincidences.
      **A REAL BUG THE CONTRACT TEST FOUND IN MY OWN PORT: `--src-dir` SILENTLY DEFEATED THE ALLOWLIST.**
      With an absolute `--src-dir`, `root / <absolute>` keeps whatever spelling the caller used while
      `root` is resolved — so on Windows the two can be the same directory in the 8.3 short form and
      the long one. `relative_to` failed, and my first version FELL BACK to the absolute path, which
      silently defeated an allowlist keyed by repo-relative path: **39 violations on a clean tree.** A
      fallback that yields a path the rest of the guard cannot use is the `guard-power` mis-slice in a
      different costume, so there is no fallback: the source dir is resolved, and a file outside the
      root is refused by name as `FILE-OUTSIDE-ROOT`.
      **WHICH STRIPPER, AND WHY THE OBVIOUS ONE IS WRONG.** The guard's private stripper is
      `cscan.strip_comments_preserving_layout`, and the port reuses the shared policy rather than
      carrying a sixth copy. It is specifically the one that KEEPS string literals, so
      `Log("DateTime.UtcNow")` is reported — and that over-match is the contract.
      `strip_comments_and_literals_preserving_layout` would blank the literal and NARROW the guard: a
      plausible-looking "cleanup" nobody would notice. A test asserts the policy keeps literals so the
      reason is where the edit would happen.
      **THREE CASE CONVENTIONS IN ONE SCRIPT.** Rule 1's ambient pattern used `[regex]::IsMatch` and
      does NOT fold; rule 2's `ServerClock` used `-notmatch` and DOES; the allowlist test was .NET
      `String.Contains`, an ordinal case-sensitive substring. Three conventions, none of them the
      repo's default, and a pair of adjacent tests pins the fold/no-fold split so it cannot be
      "corrected" into consistency.
      **THE HAND-WRITTEN FIXTURE SATISFIED 10 OF 19 ALLOWLIST ENTRIES, SO EVERY FIXTURE WAS RED.** The
      case named "clean-with-every-allowlisted-site-present" was not clean — and because both
      implementations agreed, the differential reported 18/18 and the output said nothing was wrong. A
      differential comparing like-for-like RED trees proves far less than it appears to. The seed is
      now GENERATED from the port's own allowlist, which also removes 19 opportunities to mistype a
      fragment. A test asserts the seed is clean, so this cannot recur silently.
      **A MISLEADING CASE NAME, corrected rather than left.** A case called
      "the-clock-type-is-exempt" added a read in a DIFFERENT file under `Time/` — which is a
      violation, because the exemption names one file. The name is now
      "a-read-in-another-file-under-Time-is-a-violation"; the real exemption is covered by the clean
      seed, whose `ServerClock.cs` holds a read and still passes.
      **ONE CITATION DELIBERATELY NOT SWEPT.** `gk-core/scripts/cscan.py`'s docstring reads "Five PowerShell
      guards each carry their own comment stripper — `guard-clock-seam.ps1` (since retired as `guard-clock-seam.py`), …". That is PROVENANCE: it
      names the files the shared policies were absorbed FROM, and repointing it would make the sentence
      false. The rpg-simulator ledger is historical, and this record's own fence entry is what
      `--deleted-paths` needs.
      Evidence: 18/18 differential plus 2 declared divergences, 35 contract tests, 900 tests and 376
      subtests in `gk-core/tests/tools` green, `run-guards -Only clock-seam` exit 0, `verify-change` selecting
      the `clock-seam-guard` boundary for both the deleted `.ps1` and the new `.py`, and
      `audit-doc-citations --strict` at 0 HIGH.

- [x] **3.5z** `guard-debug-scope` (255 lines) — **the differential found a real fold bug in my own
      port, and the C# suite only ever proved the green path.**
      **Differential: 20 fixtures identical in exit code and every emitted line, plus 6 declared
      divergences.** On the real file the report is byte-identical across 109 lines, 107 routes, all
      classifications and both verdicts.
      **THE C# SUITE HAS SIX FACTS AND EVERY ONE ASSERTS `exit == 0`.** Not one fixture produces a
      banner mismatch, so the guard's entire FINDING branch -- the thing that makes it a guard rather
      than a linter -- had no coverage in either language, and no self-verification refusal did either.
      Six of the differential's cases are that missing half. (I first wrote "seven facts" in two
      docstrings and the commit-message draft; the measured number is six, corrected before it shipped.)
      **A REAL BUG THE DIFFERENTIAL FOUND IN MY OWN PORT: FIVE PATTERNS COMPILED CASE-SENSITIVELY.**
      The original tested them with PowerShell `-match` / `-notmatch`, which FOLD case, at lines
      147/164/185/186/187. Reading `-match` looks like ordinary regex, and the fold is invisible until
      you run a fixture with a lowercase `send(`. `PERSISTED_UA` looked correct by luck -- its own
      pattern is already lowercase. A test now asserts `re.IGNORECASE` on all five COMPILED patterns, so
      a pattern that loses it is caught even where no fixture reaches it, and a companion test asserts
      the route patterns have NOT gained one.
      **TWO PRE-EXISTING DEFECTS IN THE ORIGINAL, both now named refusals.** (1) A ZERO-BYTE TARGET
      CRASHED IT: `Get-Content -Raw` returns `$null` on an empty file, so `[regex]::Matches($null, ...)`
      threw "Value cannot be null. Parameter name: input" -- an uninformative .NET message about the
      wrong thing. Reading it as "no routes, nothing to check" would have made a truncated
      DebugEndpoints.cs pass VACUOUSLY, the "0 is green" shape this program treats as a defect, so the
      port refuses it as `TARGET-FILE-EMPTY`. (2) An unbraced helper body reached
      `Find-MatchingClose` with index -1, which PowerShell's negative string indexing wrapped to the LAST
      character; it refused, but for a reason that would not have survived inspection. The port checks
      the open index first.
      **A FIXTURE THAT NAMED A PATH IT DID NOT EXERCISE.** The differential's `case()` used the bare
      body whenever one was given, so NO fixture carried the self-verified helper definitions and
      `helpers=` was silently ignored: five cases passed while exercising only the Shape B branch, under
      names that claimed otherwise. Found because one case's assertion named a Shape A row that could
      not exist without the definition. The wrapper now always applies. This is the THIRD time in this
      program a fixture agreed with both implementations while testing less than its name said.
      **A TEST THAT ASSERTED A BUG.** `test_the_NEAREST_banner_wins_not_the_first` asserted that a
      correctly-classified route also disagreed with its banner. It does not, and should not. Replaced
      with a sharper probe: three routes under two banners, where the THIRD failing is the proof the
      nearest banner was used (had the first been used, it would have passed).
      **THE CENSUS SAID 0 CI/DISPATCHER SITES AND WAS RIGHT**, which is worth recording: the guard is
      reached through the registry, not by path, and `run-guards -Only debug-scope` is green on the
      `.py`. The documents' "wired into deploy-play.py" claim is still true and needed only the
      extension repointed. FOUR citation sites lived outside the sweep's roots and are disclosed:
      a design-gate RULE row whose owning session is merged, the `todo-shapes.v1.json` exemplar the
      status reader parses, and a `tools/**` doc comment.
      **THE THIRD BOUNDARY ROW WRITTEN WRONG BEFORE VALIDATION.** Coupling 2 was 0 here, so this port
      ADDED the row rather than repointing one. The first version carried a `commands` field and no
      `kind`/`level`, and `verify-change` REFUSED it -- "unsupported boundary kind" -- so the malformed
      row was caught at the boundary instead of silently selecting nothing. Both reachability proofs
      then pass: `run-guards -Tier local -Only debug-scope` exit 0, and `verify-change --plan-only`
      selecting `debug-scope-guard` for the deleted `.ps1` and the new `.py`.
      Evidence: 20/20 differential plus 6 declared divergences, 41 contract tests and 124 subtests,
      6/6 `DebugScopeGuardTests` against the `.py`, **7/7 deliberate mutations caught** (drop the fold,
      banner-check ManualReview, first-banner instead of nearest, read banners from stripped text,
      accept an empty target, skip the self-verification, fold the route patterns), 961 tests and 500
      subtests in `gk-core/tests/tools` green, and `audit-doc-citations --strict` at 0 HIGH.

- [x] **3.5aa** `guard-tuning-immutability` (257 lines) — **two shapes that reported a CLEAN guard
      while checking nothing**, both now named refusals, and one real hole in my own test suite that
      only the falsification pass found.
      **Differential: 31 fixtures identical in exit code and every emitted line, plus 5 declared
      divergences.** 36 fixtures, each a throwaway GIT REPOSITORY, because this guard's whole job is
      to read history.
      **FAIL-OPEN 1: A ROOT THAT IS NOT A GIT REPOSITORY REPORTED CLEAN.** `git -C <not-a-repo> diff`
      fails, `2>$null` swallowed the message, the changed-file set came back empty, and the guard
      printed "no gk-core/data/tuning/*.json changes vs HEAD" and **exited 0**. A typo'd `-Root` therefore
      passed a CI gate without checking anything. Now `NOT-A-GIT-REPOSITORY`.
      **FAIL-OPEN 2: A MISSING DENYLIST SILENTLY TURNED T4 OFF.** `if (Test-Path $DenylistPath)` left
      the pattern list EMPTY, and an empty list permits every domain. Proven in the differential: the
      original prints **`TUNING IMMUTABILITY GUARD OK`** for `test-x.v1.json` when pointed at a
      denylist path that does not exist. Now `DENYLIST-MISSING`.
      **FAIL-OPEN 3, THE ONE NOBODY SAW: A MODIFICATION WHOSE SIDE COULD NOT BE READ WAS SKIPPED
      INVISIBLY.** The original `continue`d on an empty before- or after-text. The port performs the
      same skip - so a case the original passed still passes - and REPORTS it on stderr, because a
      rule that silently declines to look is indistinguishable from one that looked and found nothing.
      A zero-byte committed file is the reachable trigger: `git show HEAD:path` emits nothing.
      **A REAL HOLE IN MY OWN SUITE, FOUND BY FALSIFICATION: THE ESCAPE HATCH WASN'T PROVED SCOPED.**
      The docstring says the correction marker is "scoped to the files it names, never a blanket
      pass", and that is the single most important property of the feature. A mutation turning
      `path in marked` into `bool(marked)` - a BLANKET pass - passed **46 tests green**. The reason is
      a fixture-design trap worth recording: my test's marker commit named NO path, so the marked set
      was empty, and "is this path in it" and "is it non-empty at all" both answered false. Two tests
      added: a marker naming a DIFFERENT file must not exempt this one (for a deletion AND for a T1
      edit), and one marker over two deletions exempts exactly the one it names. **A test whose marker
      names nothing cannot distinguish a scoped check from a blanket one.** 10/10 mutations now
      caught, where 9/10 was before.
      **THE FIXTURE BUG THAT FOUR CASES NEEDED, and it is the FOURTH time in this program.** This
      guard's default mode is "working tree vs HEAD", and every T2/T4 fixture seeded its file WITH a
      commit message and never made a second change - so the tree was clean, the guard correctly
      reported "no changes", and **four cases that must FAIL exited 0**. Both implementations agreed,
      so the differential reported them `ok`. Comparing two clean trees proves nothing about the rule
      a case is named after. `uncommitted(...)` now exists precisely to leave a change in the working
      tree, and the helper's docstring says why.
      **A CASE THAT PROVED T1 WHILE NAMED FOR T3, IN BOTH THE DIFFERENTIAL AND THE TEST.** A rename
      fixture COMMITTED the rename, putting the deletion in history where working-tree mode cannot see
      it; both implementations reported T1 on the new file and the differential called it `ok` under a
      name claiming the rename was what it tested. Split into the two shapes that actually exist: an
      UNCOMMITTED rename (a D) and a STAGED one (an `R100` with three fields, which the guard must
      expand to a D of the old path PLUS an A of the new one - collapsing it to the A alone would let
      a published version be renamed away unnoticed).
      **FOUR CASE CONVENTIONS, NONE THE REPO DEFAULT.** The correction marker, the denylist pattern,
      the `gk-core/data/tuning/*.json` filter and the `<domain>.v<n>.json` filename shape all FOLD (they used
      `-match`); the path named inside a correction message, `Status.StartsWith('R')` and
      `HashSet.Contains` do NOT. The filename shape folding is the surprising one - `[a-z0-9-]`
      matches `D` and `.V1.JSON` matches, so `D.V1.JSON` is accepted as well-formed. Asserted so a
      later tightening is a decision rather than a drift.
      **THE PORT IS STRICTER ON ONE NUMBER, DECLARED.** PowerShell parses `10.0` to a `Double` and
      re-renders it `10`, so the original called `10.0 -> 10` unchanged; `json` preserves the float, so
      this port reports a change. The stricter direction, and the only numeric rendering the two
      disagree on. The HOST question the original documented (`-AsHashtable` missing in PowerShell 5.1)
      does NOT matter for the comparison, and the docstring says why: both sides canonicalise with
      the SAME sort, so two identical key SETS always produce the same string under either ordering.
      **SIX C# FINDING ASSERTIONS MOVED TO STDERR.** `TuningImmutabilityGuardTests` had six
      `Assert.Contains("T1"/"T2"/"T3"/"T4", stdout)` with the stderr tuple discarded as `_`; the
      original put findings on stdout through `Write-Host`. They now read stderr, and the verdict line
      stays on stdout. 11/11 pass.
      **I NARROWED THE BOUNDARY WHILE FIXING IT, and put it back.** Replacing the path list to turn
      the `.ps1` into a glob DROPPED `gk-core/scripts/tuning-domain-denylist.v1.json` and the C# suite, both
      of which the original row carried. The guard READS the denylist, so an edit to it must select
      this guard. Restored, with a test that asserts no published domain is denylisted.
      Evidence: 31/31 differential plus 5 declared divergences, 48 contract tests and 209 subtests,
      11/11 `TuningImmutabilityGuardTests` against the `.py`, **10/10 deliberate mutations caught**,
      1009 tests and 709 subtests in `gk-core/tests/tools` green, both reachability proofs
      (`run-guards -Only tuning-immutability` exit 0; `verify-change` selecting the boundary for the
      deleted `.ps1`, the new `.py`, the denylist and the test), and `audit-doc-citations --strict`
      at 0 HIGH.

- [x] **3.5ab** TWO Tier-5 retirements, and a finding that says the L1 lane's port is INCOMPLETE.
      Retired `.claude/cmdc-agents/scripts/resolve-append-only.ps1` (51 lines) and
      `verify-no-disk-write.ps1` (71, retired). **122 lines, zero new code.**
      * `resolve-append-only.ps1` (retired) is the hand-rolled append-only conflict resolver that
        `union_append_only.py` (459 lines) replaced, and AGENTS.md already names the Python as the
        sanctioned tool. Its only two remaining references were PROVENANCE comments in
        `union_append_only.py` and its test, and both are now marked RETIRED so the tense is right.
      * `verify-no-disk-write.ps1` (retired) is a one-off verification of a completed past incident ("Target
        0c"), with **ZERO references anywhere in the tree** and a hardcoded
        `D:\Works\source\plant-vs-zombie-rise-of-summoner` in its param block - which AGENTS.md
        forbids committing ("never a drive letter"). It is evidence, not a tool.
      **THE FINDING, AND IT IS THE VALUABLE PART: `accept_lane.py` AND `post_merge_check.py` ARE
      NOT RETIRABLE, because the pipeline test still drives the PowerShell.**
      I read both `.py` twins' docstrings - each opens with "Python replacement for the retired
      `<name>.ps1`" - the twins are 993 and 764 lines against the originals' 603 and 479, and their
      own suites pass 167 tests. That reads like a finished port with leftovers. **It is not.**
      `test_fail_closed_pipeline.py` declares
      `POST_MERGE = .../post-merge-check.ps1` and `ACCEPT_LANE = .../accept-lane.ps1` and drives
      every one of its cases through a `run_pwsh` helper. Deleting the two `.ps1` turned
      **43 tests red** - the whole fail-closed pipeline suite. So:
        * the LIVE, INTEGRATION-TESTED path is still the PowerShell;
        * the Python twins are covered by UNIT tests only, and the 43 integration behaviours they are
          supposed to preserve are proven against the PowerShell alone.
      That is this program's own failure class wearing a different hat: **a port that leaves the live
      path untouched reads green.** The unit suites are real evidence, but they are not the
      integration contract, and nothing in the twins' green run said so.
      **I REVERTED MY OWN EDITS rather than landing a green tree.** Removing the two `.ps1` from the
      `manager-fail-closed` boundary row, repointing `scripts/lane-server.ps1`'s comment, and
      unfencing both files were all applied, then reverted: the row entry and the comment were BOTH
      TRUE, and repointing them would have made a live, tested path look unowned and already-migrated.
      I also checked the hazard the manager record names - a guard parsing script text as a contract -
      BEFORE deleting: nothing reads any of the four as data. `accept_lane.py`'s 19 mentions are
      docstring provenance citing the original's line numbers, and `program_status.py`'s are comments
      naming a vocabulary it HARDCODES. That check passing is why the 43 reds were a wiring problem
      and not a data dependency.
      `program_status.py`'s two citations were KEPT repointed at the `.py` and one gained a sentence
      saying the tuple is a literal, not a read of either file - the `.py` is the durable home of both
      the vocabulary and the gate, and the old comment pointed a reader at a file whose contents were
      transcribed into a literal two lines below it.
      Evidence: 224 tests in the three cmdc-agents suites green with the `.ps1` present (including the
      43 that go red without them), 37 tests in `test_union_append_only.py`, `program_status.py`
      parsing its own maps, and `audit-doc-citations --strict` at 0 HIGH.

- [x] **3.5ac** `test_fail_closed_pipeline.py` repointed to `post_merge_check.py` and
      `accept_lane.py` before those two `.ps1` can be retired. **This is the blocker 3.5ab found, and
      it is the last thing standing between the program and two more retirements.**
      * `POST_MERGE` and `ACCEPT_LANE` point at the `.ps1`; `run_pwsh` must become a
        `subprocess.run` with `capture_output=True, timeout=...` per the tool standard.
      * **The flag spellings must be mapped, not assumed** - the twins use `--kebab-case`, so every
        call site needs checking against the twin's argparse, and a missed flag is a silently
        different check rather than an error.
      * The `fake dotnet.ps1` doubles must become something the Python can execute; a PowerShell double
        is unreachable from a Python child.
      * Then, and only then: retire both `.ps1`, drop them from the `manager-fail-closed` row, and prove
        the 43 tests pass against the `.py`.
      * A test should assert the pipeline entry points are PYTHON, so the next twin cannot be added
        beside a still-live original without anyone noticing.

      **DONE. 62 tests in this file pass against the twins; 225 pass across the three cmdc-agents
      suites with the two `.ps1` DELETED.** The `& script -Flag 'value'` command string and its
      103-site PowerShell quoting layer are gone, replaced by `run_tool` plus two argv builders.
      **THE DOUBLE HAD TO CHANGE LANGUAGE, which a reading would not have found.** A `.ps1` cannot be
      launched by `subprocess` without a shell, and handing the gate a shell would put back the quoting
      surface the migration just removed - so the dotnet double is now a two-line `.cmd` shim over a
      Python implementation, in the temp fixture and never tracked. Its first version was named
      `dotnet.py` beside `dotnet.cmd`, which the fixture `.gitignore` did not list, and the gate's
      "checkout is dirty" refusal aborted **21 tests before the behaviour under test was reached**.
      **AN ARGV MIGRATION CHANGES MORE THAN SPELLING, AND THE DANGEROUS DIRECTION IS SILENT.**
      `--test-project` and `--check` are both `action="append"`, so the old
      `-TestProject @('a','b')` array cannot be transliterated: a comma-joined value arrives as ONE
      project name, the gate runs its DECLARED surface, reports green, and the caller's project never
      runs. Pinned by `RepeatingATestProjectFlagIsNotACommaList`. Same trap for an empty `--check`.
      **THE REWRITE WAS DONE BY A GENERATOR THAT REFUSES TO WRITE UNLESS THE RESULT PARSES, and that
      gate earned its keep five times**: it caught an f-string hole never unwrapped, a
      `.strip("'")` that turned `{'0' * 40}` into `0' * 40`, a `\s*\n` that asked for a newline `\s*`
      had already eaten, and two call-site patterns matching nothing at all. My first response to a
      mangling transform was to start hand-repairing its output, which is the wrong response to a tool
      that mangles; the fix was a gate, not a patch. The `.ps1` ban assert was also narrowed to the
      entry-point BINDINGS, because the docstring deliberately names both scripts as provenance and a
      blanket "no `.ps1` string" rule would have deleted the reason the migration happened.
      **FALSIFICATION THEN FOUND A HOLE IN THE RESULT: dropping `--log-root` left all 62 tests green.**
      The tool's default log root is `<temp>/cmdc-acceptance` - the SHARED system temp, not the
      fixture - so the regression would not change a single verdict; it would quietly move every
      acceptance log out of per-test isolation, where concurrent runs share one path. That is the temp
      -store leak this repo has already paid for. Now 5/5 mutations caught.
      ONE FINDING FOR THE BOUNDARY OWNER, NOT FIXED HERE: `test_accept_lane.py`'s
      `test_the_retired_two_versus_nine_distinction_was_unobservable_through_pwsh_command` measures a
      POWERSHELL fact (`pwsh -Command` collapses every non-zero script exit to 1) but sits inside a
      class gated on `accept_lane.py` existing, so it is now permanently skipped. The knowledge is
      load-bearing for this whole program - it is why exit codes are compared only as far as the
      invocation can express them - and skipping it leaves it as prose only. It should move to its own
      ungated class. Not done here because that file is the boundary owner's.


- [x] **3.5ab2** `guard-class-system` (261 lines) — **the differential found a real bug in my own
      port, and falsification found a hole behind it.**
      **Differential: 51 fixtures identical in exit code and every FINDING, plus 6 declared
      divergences.** The real tree is byte-identical, and the port selects `aptitudes.v10.json` — which
      is the correctness point the whole rule turns on.
      **THE VERSION SORT IS NOT COSMETIC AND THE TREE PROVES IT.** The tree ships v1 through **v10**,
      and the sort is NUMERIC on `n`. A lexical sort puts `v9` above `v10`, so a lexical port would
      silently validate a four-year-old config the first time the eleventh ships and G2/G3 would be
      judging superseded edges. The differential plants a CLEAN v9 and a FAILING v10 and asserts only
      v10's edge is judged.
      **A REAL BUG THE DIFFERENTIAL CAUGHT IN THE PORT: `[string]$null` IS `""`, AND `str(None)` IS
      `"None"`.** G4 asks `IsNullOrWhiteSpace([string]$e.unitClass)`, so a JSON `null` read as `""` and
      tripped the rule. In Python `str(None)` is `"None"` — non-empty, non-blank — so the guard SKIPPED
      every entry whose `unitClass` is null and **reported CLEAN on a catalog that is missing every
      note**. One `_ps_string` now stands wherever a PowerShell `[string]` cast stood, and a container
      raises rather than emitting a plausible-looking wrong string. Found by the FIRST fixture with a
      null `unitClass`; a reading would not have found it, because the cast looks equivalent.
      **EVERY COMPARISON IN THIS GUARD FOLDS CASE.** `-eq`, `-contains`, `-like`, `Group-Object`,
      `Select-Object -Unique` and every `-match` were case-insensitive; the only exception is
      `StartsWith("//", Ordinal)`, which is only ever asked about `//`. So `Might`/`might` is ONE
      aptitude id and `ARMOR.PLATE` collides with the `armor.plate` family.
      **THE FINDING NAMES THE CATALOG'S SPELLING, NOT THE ID'S.** The original interpolates `$family`,
      so the two can differ in case and the message says WHICH registered family was hit. A first
      version echoed the id and the differential caught the message difference.
      **TWO TRANSCRIBED ASYMMETRIES, ASSERTED RATHER THAN "FIXED".** G5 does NOT exclude `bin`/`obj`
      — unlike every other guard ported in this program — so a stale build-output copy reports a
      phantom duplicate. And G7's negative half skips only `//`-PREFIXED lines, so a shape inside a
      `/* */` block is still reported; adding a comment stripper would NARROW the rule. "Fixing" either
      is a behaviour change, so each is a test.
      **FALSIFICATION FOUND A REAL HOLE, AND THEN A SECOND ONE BEHIND IT.** Making G2's `-contains`
      case-sensitive left all 60 tests green — the only fold coverage was on G3. The first fixture I
      wrote for it used a channel with a PREFIX, so it exercised the parent lookup and left the EXACT
      lookup untested: **G2 tries the exact match first and falls through to the parent whenever the
      channel has a dot, so the exact lookup is only reachable for a DOTLESS channel.** A second
      mutation exposed that. 4/4 caught afterwards.
      **FIVE MORE FIXTURE CLAIMS THAT WERE FALSE, all caught by the contract test.** A case named
      "a family PREFIX registers the whole subtree" claimed to pass while both implementations agreed on
      FAIL, because the seed catalog had no `combat.power` family — a case whose name claims a positive
      and whose fixture proves a negative is worse than no case, because the differential reports it
      `ok`. A POSITIVE table carried a mangled f-string whose expression evaluated to `""`. A
      "skip the `//` line" body failed the POSITIVE half for an unrelated reason. A "the exact channel
      folds" test kept exercising the prefix. And a reachability test unioned the findings with the full
      id set, so it could not fail. Also: my `case()` default `roster=None` meant "omit", so **55 of 57
      differential cases were comparing two identical missing-source refusals** — the FIFTH
      fixture-helper bug of this shape in this program, and the fix is a SENTINEL, because a default
      that means "absent" is a trap.
      **ONE ENVELOPE, NOT TWO.** The `--json` refusal path omitted three keys the normal path carries,
      so a consumer would need a branch for "was it a refusal?" — and a key that vanishes on one path
      is a consumer's `KeyError`.
      **NINE C# FINDING ASSERTIONS MOVED TO STDERR**, in two passes: my first pattern matched neither
      `"G5:` (a colon, not a space) nor a bare `"StrikeMixture.cs"` that names no rule id, and its
      declaration regex `[^)]*` stopped at the first `)` inside `Run(fixture, FindRepoRoot())`, so all
      seven sites were reported as misses and none was repointed. 16/16 pass.
      Evidence: 51/51 differential plus 6 declared divergences, 61 contract tests and 15 subtests, 4/4
      deliberate mutations caught, 16/16 `ClassSystemGuardTests` against the `.py`, both reachability
      proofs (`run-guards -Only class-system` exit 0; `verify-change` selecting the boundary for the
      deleted `.ps1`, the new `.py` and the test), and `audit-doc-citations --strict` at 0 HIGH.

- [x] **3.5ac** `session-boundary-check` (260 lines, 5 registry guards remain and this is the first
      of them) — the FIRST port with **a caller that shells the tool AND a test that reads its source
      text AND a drift guard in another test file that reads it as data**, and all three had to move in
      the same commit as the tool. The differential is clean in a way that matters: **312 lines,
      byte-identical, 0 differences, both DRIFT(52)** on the real tree, then **43 identical / 5 declared
      / 0 unexplained** over 48 git fixtures. Three of those five declared divergences are cases where
      **the ORIGINAL IS THE BUG**, which the harness asserts the PORT's verdict for rather than
      asserting agreement:
      - **`git worktree list --porcelain` was called with NO `-C $RepoRoot`**, so every record's
        worktree path resolved against the CURRENT DIRECTORY's repository. A fixture repository with a
        real `git worktree add wt` and a record pointing at it was reported as *"worktree path 'wt' no
        longer exists"* while the directory sat there. **Invisible in production** because the CWD is
        the repository, which is exactly why it survived. The port asks the repository it was told to
        check, and a test runs the resolution **from inside a LINKED worktree** — the only assertion
        that catches `return root`.
      - the `active` FILTER folded case (`-eq`), so an `ACTIVE` record still participates in the overlap
        check. My port compared exactly, and the guard reported CLEAN on two sessions that do overlap —
        a **silent narrowing**, the worst shape a guard has. Second time a fold has been the finding.
      - **`$null` interpolates as the EMPTY STRING and `str(None)` is `"None"`** — the report line
        printed `[]` for a complete record and `[None]` for one missing `status`, so a reader could not
        tell "no status" from "the status is the text None". **Third port in a row**; `_ps_string` is now
        a named helper with that name in it.
      - `$null -eq $rec.$f` is a **NULL** test, not a truthiness test: a record with `started: 0` is
        complete. `is None` is the exact analogue, and a test pins it.
      - **A CHECK THAT WAS NEUTERED, KEPT AS IT IS.** Line 50 is `if (-not (Test-Path (Join-Path
        $RepoRoot '.git'))) { }` — an `if` with an EMPTY body. Whatever check it once carried is gone.
        NOT reinstated: reinstating it is a behaviour change this port cannot prove, and a guard that
        starts refusing because a port guessed at a deleted check is worse than one that is honestly
        inert. Recorded in the guard's docstring and left as an open question for the boundary owner,
        because "was this meant to be a check?" is not an agent's decision.
      **THE COUPLING THAT BIT, AND THE RULE IT TAUGHT.** `verify-change.py` dispatched through
      `_resolve_tool_argv`, which resolves the **FILE** by dialect but passed the **flags verbatim** —
      so the moment the `.py` appeared, `-RepoRoot`/`-RequireDiffFence` were handed to argparse and every
      one was rejected. A dialect-aware resolver for the file is not a dialect-aware caller. Fixed by
      adding a `py_args` parameter so the caller states BOTH dialects and the resolver picks the one
      matching the interpreter it found — which also keeps a revert (deleting the `.py`) working with
      the PowerShell spelling intact. `verify-change.ps1:188` hardcoded the `.ps1` path and would have
      handed a deleted file to `powershell -File`, reporting a *session-fence escape* for what is a
      *missing file*; it now resolves the `.py` first and names the refusal if neither exists.
      **A DRIFT GUARD THAT WAS PINNING THE OWNER'S DIALECT, NOT ITS VOCABULARY.**
      `test_program_status.py` read `$validModes = @(...)` out of the `.ps1` with a regex, so it went
      red on the PORT because the dialect changed while the vocabulary did not. It now **imports** the
      owner and compares the runtime tuples, which is strictly stronger: a reformat can no longer turn
      a real drift green, and only the owner actually declaring them can satisfy it. The
      `Where-Object { $_.Name -notlike '_*' }` fragment assertion became `TEMPLATE_PREFIX` /
      `SESSION_TEMPLATE_PREFIX` compared as VALUES. `program_status.py` also cited
      the retired `session-boundary-check.ps1:86` and the retired `accept-lane.ps1:30` by **LINE NUMBER** — a line citation into
      a file a port is about to delete; all three are names now.
      **THE SWEEP PRODUCED 74 BROKEN COMMANDS, AND THE HALF-RENAME CHECK IS WHAT CAUGHT IT.**
      `ps1-rename-sweep.py` rewrote 582 citations across 235 files and left the PowerShell **flags**
      behind, so the tree briefly held `python scripts/session-boundary-check.py -RepoRoot ... -Session
      ...` — a command argparse rejects. A broken command in a lane brief is worse than a stale one: a
      worker runs it, sees a usage error, and cannot tell the tool is fine and the invocation is not.
      74 files corrected by a scoped translator that rewrites only flags AFTER the tool path and
      **refuses** if a PowerShell host flag (`-File`, `-NoProfile`, `-Command`) follows it, because past
      that point it is guessing.
      **FALSIFICATION FOUND FOUR HOLES IN MY OWN SUITE, AND TWO OF MY OWN CLAIMS WERE FALSE.** 10
      mutations, first pass 5 survived. Three were **invalid mutations** — `rstrip("/*")` is *equivalent*
      to the original's three-call `TrimEnd` sequence for a trailing run, so the mutant never differed
      and the green suite was meaningless; and `get("paths") or ["**"]` **short-circuits** on a fixture
      that always has paths, so the fence mutant never applied. That first one is a FALSE CLAIM in my
      own docstring and comment ("the order matters", "a single call would strip a `*` before a `/`") —
      `rstrip` never touches a non-trailing character. Corrected in the guard, and the equivalence is now
      pinned by a test so a later single-call collapse is known-equal rather than silently different. The
      other two survivors were REAL gaps: a CI-mode test whose fixture had an existing branch (so
      dropping the `not ci` guard was invisible), and a reviewed-diff fence tested from one side only.
      And the prefix rule: I wrote `path_overlap("a/b", "a/bb")` as a negative **twice in one file**,
      once having already got it right elsewhere in the same file — `"a/bb"` starts with `"a/b"`, so it
      IS an overlap. A reasoning rule that has to be re-derived per assertion is a rule that has to be
      PINNED.
      **A FENCE GAP IN MY OWN RECORD, NOT A CROSSING.** Five files this port must touch were in no
      active record's `paths` — **including the tool being retired itself**. So the deletion could have
      read as unowned, and `.github/workflows/nightly.yml` was absent while `ci.yml` and
      `release.yml` were present, which would have let a two-of-three call-site repoint land and left
      CI's nightly run calling a deleted file. Added (fence 533 -> 538).
      Evidence: 43/48 identical + 5 declared (3 of them the original being wrong) + 0 unexplained;
      **61 contract tests, 33 subtests, 10/10 mutations caught**; 10/10 `VerificationTopologyTests`
      against the `.py`; three reachability proofs (`run-guards -Only session-boundary` launched the
      `.py`, `verify-change --plan-only` selects the guard for the new `.py` AND the test, and
      `--deleted-paths` for the retired `.ps1` through the GLOB); `audit-doc-citations --strict` 0 HIGH
      over 1720 documents and 26024 citations; 40/40 `test_program_status.py`; 63/63
      `test_fail_closed_pipeline.py` with the `.ps1` gone.

- [x] **3.5ad** `guard-verification-boundaries` (407 lines) — **the first port whose differential
      found a live defect in the SHARED LIBRARY rather than in the port**, and the first whose
      differential could not have found its own worst bug.
      **ALL THREE FLAG COMBINATIONS BYTE-IDENTICAL ON THE REAL TREE**: the bare run and
      `--skip-coverage-walk` at 1 line each, and `--report` at **191 of 191 lines**. That last one took
      three corrections to reach, and each correction is a lesson:
      - **The report is computed over `src/**` AND test sources.** The original appends to one `$resolved`
        list from both loops, and every heading is computed over it — including the one reading
        "production files mapped", which is a misnomer for "src + test sources". My first version
        collected only `src/**`, so the fallback table listed a different SET of owners and the file
        count was roughly half. A report that disagrees with the tool it reports on is worse than none.
      - **`Resolution.owners` is a tuple of plain boundary DICTS**, and `PytestDirs.test_dir` is
        snake_case. I wrote `.Owners[0].verificationId` and `.TestDir` — the PowerShell lib's spellings,
        copied from the wrong language's source. Both were crashes. **A reading of the OTHER language's
        source is how both arrived**; the twin's API has to be read, not recalled.
      - **THE DEFECT THE DIFFERENTIAL FOUND, IN `gk-core/scripts/lib/verification_boundaries.py`, NOT IN THE
        PORT.** `pattern_match`'s final-segment wildcard branch lowercased the PATH and not the
        PATTERN, compiling the regex without `re.IGNORECASE`. So any registry pattern whose final segment
        carries an uppercase letter — `RpgStore.Story*.cs`, `NarrativeText*.cs`, `DelveEvent*.cs` —
        matched NOTHING in Python while matching in PowerShell. Measured: **14 owner patterns affected**,
        and two files provably mis-resolved to a WIDER FALLBACK OWNER rather than to an error —
        `gk-core/src/FusionRpg.Contracts/NarrativeTextDtos.cs` and
        `gk-core/tests/FusionRpg.Guard.Tests/NarrativeDoctrineReadingGuardTests.cs`. `wildcard_match` said True
        for both while `pattern_match` said False, which is the cheapest possible detector.
        **The failure mode is the worst shape: `verify-change.py` reported a plausible, narrower-looking
        answer.** It is visible only in `--report`, because no verdict depends on it — the guard was
        green and correct while resolving paths wrongly. The file was claimed by no ACTIVE record (the
        one exact claim is from `verify-change-python-20260926`, MERGED), so it was a gap in this
        record, not a crossing; fence 680 -> 682.
      **THE WORST BUG IN THE PORT WAS ONE THE DIFFERENTIAL COULD NOT SEE.** `is_relative_registry_path`
        accepted a ROOTED pattern such as `/etc/**`, because `[IO.Path]::IsPathRooted` refuses one and
        `Path.is_absolute()` does NOT on Windows — there is no drive. **No registry row uses a rooted
        path, so the two implementations agreed on every input the tree contains and the real-tree
        differential reported 191/191 with the defect in place.** Only a unit test varying the input
        found it. A differential proves the two AGREE; it cannot show a shared blind spot.
      **I REPORTED A BUG THAT DID NOT EXIST AND RETRACTED IT IN THE SAME FILE.** A test using
        `.claude/**/SKILL.md` failed, and I concluded the `/**/*.md` branch had an off-by-one
        (`pattern[:-7]`). It does not: `.claude/**/*.md` is 15 characters, so `[:-7]` is the first 8,
        `.claude/`, which is exactly right. My fixture had used a pattern that is **not one of the four
        legal shapes** at all, so it measured itself. The retraction stays in the test's comments
        because a wrong finding a reader cannot see is a wrong finding that gets re-derived. The real
        lesson recorded in the test is that the GRAMMAR layer is what refuses the illegal shape.
      **OVER-CLOSING, IN THE DIRECTION THAT COSTS THE MOST.** The port made an unreadable
        `enforcement-registry.v1.json` a REFUSAL. The original ACCUMULATED it as one finding and carried
        on with an empty catalog. So a valid boundary registry plus a missing catalog produced one
        refusal naming the catalog **instead of the twenty boundary problems it actually had**, and
        **sixteen C# tests asserting a specific boundary finding went red on it.** "Fail closed" is not
        free: the distinction is by ROLE — the guard's SUBJECT refuses when unreadable (there is nothing
        to validate), a CATALOG it consults is a finding. Pinned in both directions, because leniency in
        one place must not widen into "never refuse".
      **A DISPATCHER THAT RESOLVES THE FILE IS NOT A DISPATCHER THAT RESOLVES THE ARGUMENTS.** The same
        defect appeared a THIRD time: `verify-change.py`'s integrity pre-check passed `-Root`/
        `-SkipCoverageWalk` through `_resolve_tool_argv`, which picks the interpreter for the FILE and
        hands the flags through verbatim. Fixed with the `py_args` parameter the first occurrence
        introduced. `verify-change.ps1` had hardcoded the `.ps1` in three separate places (diff fence,
        guard execution, integrity pre-check); all three now prefer the `.py` and name the refusal when
        neither exists. Each site had to be found separately, which is the argument for the rule rather
        than against it.
      **A C# TEST DID TEXTUAL SURGERY ON THE POWERSHELL LIB WHILE RUNNING A `.py`.** `S4` regex-replaced
        `$Script:EnforcedRoots` in `lib/VerificationBoundaries.ps1` and then invoked
        `powershell -File <the .py>` — which printed PowerShell's own banner and exited 0, so the test
        would have recorded "the guard accepted an unmapped file". Rewritten to rewrite
        `ENFORCED_ROOTS` in the Python lib and run the Python guard. The mechanism under test is
        unchanged; only its language moved.
      **A `$LASTEXITCODE` LOST THROUGH AN `if` EXPRESSION.** Assigning the integrity invocation to
        `if (...) { $integrityOutput = ... }` consumed the native exit code, so a failing pre-check
        reported success and the planner went on to plan from a registry it had just been told is
        invalid. The exit code is now read on the statement immediately after the call. A planner that
        ignores its own pre-check is worse than one that has no pre-check.
      **THE FIXTURE MUST CARRY THE GUARD *AND* ITS LIB.** The PowerShell pair was self-contained
      because the `.ps1` dot-sourced its lib; the Python guard IMPORTS
        `lib/verification_boundaries.py`, so 8 fixture copy sites that copied only the script produced a
        fixture whose guard could not start. The census reported "18 EXECUTE sites" and undercounted:
        it classified the copies as something other than execution. **A caller scan that prints a path is
        a question, not a conclusion.**
      Evidence: 3/3 flag combinations byte-identical on the real tree, 191/191 report lines;
      **56 contract tests + 22 subtests, 17/17 mutations caught**; **6/6 observable lib mutations caught
      with 1 classified EXPECTED-EQUIVALENT**; the two mis-resolved files now resolve to their own
      boundaries; `VerificationBoundary*` C# suite against the `.py`.

- [x] **3.5ae** `guard-test-substrate` (353 lines) — the port that is also the THIRD CONSUMER of the
      shared comment scanner, and the one where the differential could not see the worst bug.
      **28 fixtures: 21 identical in exit code and every emitted line, 7 declared divergences ALL of
      which are cases where the ORIGINAL is the defect, 0 unexplained.**
      **THE ORIGINAL'S RATCHET IS COMPLETELY BROKEN OUTSIDE THE REAL REPO ROOT, from one `Substring`.**
      It computes the repository-relative path as `$full.Substring($Root.Length)`, and for a temp
      directory `$Root` resolves to the LONG path while `$_.FullName` is the 8.3 SHORT one — so the
      slice removes the wrong number of characters and `$found` is keyed by `0a_/tests/A.cs` while
      `$baseline` is keyed by `tests/A.cs`. **Three consequences from that one line:** the path text in
      every finding is chopped; the ratchet does nothing, so every entry is reported as both new and
      stale (with one correct exemption in place the original exits 1 and the port exits 0); and the
      SELF-EXEMPTION is defeated, so the guard reports a violation in the very file that exists to prove
      the guard fires. Invisible in production, where the repository root has no short-name alias. The
      port uses `Path.relative_to`, which cannot chop. **THE DIFFERENTIAL COULD NOT HAVE FOUND THIS** —
      it needs a temp tree to exist, and every case the differential plants that does not involve the
      ratchet or the exemption is unaffected. It surfaced because the port's own contract test runs
      against a temp tree and disagrees.
      **THE WORST BUG WAS ONE THE DIFFERENTIAL REPORTED AS A MATCH.** The catch body was sliced as
      `after[open+1 : end-open]` — the PowerShell is `Substring($open + 1, $end - $open - 1)`, a start
      and a LENGTH, and I read that length as an end index. Every real catch body therefore read as
      EMPTY, so `catch (Exception e) { throw; }` — a cleanup that RETHROWS, the opposite of the defect —
      was reported as swallowed. **The differential planted three swallowed-delete fixtures and all three
      still produced the same ANSWER**, because the truncated slice was empty or whitespace: the same
      verdict, reached for the wrong reason. A differential compares answers, so a bug that preserves
      every answer is invisible to it. Only a test that varies ONE thing found it — and it is the
      false-positive direction on a guard about leaked temp dirs, which is what trains people to add
      baseline lines until the gate is decorative.
      **THE STRIPPER IS NOT REIMPLEMENTED.** This is the second consumer of `gk-core/scripts/cscan.py` and the
      reason the program asked for a shared one: the original's first version stripped block comments
      before line comments with a regex, so a `/**` in prose — the path literal
      `gk-data/packs/fusion/data/seed/items/charms/**` in a doc comment — opened a phantom block comment that ran to the next
      real `*/`, deleted the `Dispose` from the scanned text and made a real swallowed delete INVISIBLE.
      Fifteen files contain such prose and two really were violating. The case
      `a_doc_comment_naming_a_glob_path_does_not_eat_the_next_real_comment` is in the contract test rather
      than only in the differential, because the differential stops existing once the `.ps1` does.
      **A REPORTED LINE NUMBER THAT WAS COMPUTED AND NEVER USED.** The original computed a `line` for
      every swallowed delete, never printed it, and computed it unsoundly — the index came from the
      stripped text and the slice from the raw one, and the strip replaces a whole literal with `""`, so
      every index after the first literal is short. Dropped rather than ported wrong.
      **FALSIFICATION: 18/18 observable mutations caught, 1 EXPECTED-EQUIVALENT and MEASURED rather
      than argued.** The survivor is the brace match stopping at the first closer. It cannot be caught,
      and the measurement says why: truncating a body to a prefix can only REMOVE characters, the rule
      flags a body iff it holds nothing but `;` and whitespace, and a brute force over every
      brace-BALANCED body up to five characters — 5374 of them — found 0 disagreements. (The UNBALANCED
      version reports 820, which is exactly why "balanced" is the whole difference and not a detail.)
      **THE FIRST FALSIFICATION PASS FOUND THREE REAL HOLES IN MY OWN SUITE**: no negative twin for the
      corpus-copy rule, so dropping its `"data","seed"` requirement changed no fixture and survived; and
      no fixture near the `CATCH_WINDOW`, which turned out to measure the distance from `catch` to its
      OWN opening brace — the exception specification — and not the distance from the delete, so the
      first attempt put the catch in another method, which the rule reaches anyway.
      **FIVE C# ASSERTIONS WERE READING THE WRONG STREAM.** The guard reports findings on stderr, per
      the port standard, and the original printed everything through `Write-Host`, which is stdout. So
      five planted-violation assertions read an empty string and went red saying so; they now read
      `stdout + stderr`, with the reason recorded at the helper. **The verdict strings are byte-
      preserved including their em-dashes** — 22 `Assert.Contains` across the suite depend on them, and
      an ASCII-fied em-dash is exactly what a future substring assertion on the tail would catch as a
      mystery. Two mutations exist solely to keep that honest.
      **THE SWEEP'S OWN GATE LEARNED THIS STEM.** `guard-test-substrate` was not in
      `ps1-rename-sweep.py`'s `FLAG_SPELLINGS`, so the argument gate skipped it and 3 files kept
      `-Root`/`-UpdateBaseline` after the `.py` path. Added, and the sweep re-run fixed them — the gate
      is now the mechanism rather than an ad-hoc script per port, which is the third time it has been
      needed.
      Evidence: 28 fixtures (21 identical / 7 declared / 0 unexplained); 50 contract tests + 10 subtests,
      18/18 observable mutations caught and 1 measured equivalent; 11/11 `TestSubstrateGuardTests`
      against the `.py`; 86/86 across the two touched suites; three reachability proofs, and the owner
      row now carries `guards: [test-substrate]` so the guard is selected for its OWN source;
      `audit-doc-citations --strict` 0 HIGH over 26,037 citations.

- [x] **3.5af** `guard-test-content-root` (323 lines) — the lightest coupling of the program, and the
      fourth consumer of `gk-core/scripts/cscan.py`. **27 fixtures: 26 correct against their own stated
      expectation AND byte-identical in exit code and every emitted line, 1 declared divergence (a
      refusal the original had no name for), 0 unexplained.**
      **THE CENSUS SAID 0 EXECUTE SITES AND WAS WRONG BY ONE.** The census found 2 prose citations and
      no execute sites; `gk-core/tests/FusionRpg.Guard.Tests/TestContentRootGuardTests.cs` runs the guard as a
      subprocess, and the census missed it because the path is spelled
      `Path.Combine(RepoRoot(), "scripts", "guard-test-content-root.ps1")` — SPLIT ACROSS TWO STRING
      LITERALS, so no grep for the filename can match. That is the half-rename shape
      `ps1-rename-sweep.py`'s `HalfRename` gate was built for, in the place a rename sweep does not
      reach: a call site, not a citation. Six `Assert.Contains` read the wrong stream after the port
      (findings moved to stderr; the original printed everything through `Write-Host`) and now read
      `stdout + stderr`. **A COMPILE ERROR CAUGHT BEFORE THE COMMIT, not beside it:** the five
      planted-violation tests destructured `var (exit, stdout, _)` and then referenced `stderr`, which
      did not exist — so the structural edit had to be validated in its own step, which is the rule
      this program has been bitten by.
      **THE OPACITY RULE IS ASYMMETRIC, AND MY FIRST PORT DOCUMENTED IT WRONG.** I wrote that an
      unstable anchor (a local assigned more than once — a walk-up loop's cursor) is "never flagged".
      The source says otherwise: the `walk-escapes-root` branch never reads `$pure`, and only
      `walk-misses-root` is gated on it. That is the right design and a wrong comment — "it did not
      reach depth 0" is a claim about a STABLE anchor, while a walk below the root is below it whatever
      the cursor did. Both the port's docstring and the suite's twin case were corrected in this change,
      and the asymmetry is now pinned by two tests that differ by exactly one line of reassignment.
      **THE ORIGINAL'S COMMENT OVERREACHES, AND THE PORT SAYS SO.** It claims a walk written inside a
      string literal "is therefore scanned" because its stripper keeps literals. Keeping literals is
      what makes a real walk visible, but C# escapes a `".."` written in a literal as `\"..\"` and the
      escaped form never matches the `".."` argument token, so such code is unreachable to the guard —
      which is why the original's own C# test assembles its planted walk at RUN TIME. Measured, not
      inferred, and stated as a bound rather than inherited.
      **THE DEPTH ARITHMETIC IS THE WHOLE RULE, AND THE FIRST DIFFERENTIAL GOT IT WRONG.** `depth` is
      the segment count of the file's DIRECTORY, so a file at `tests/P/A.cs` is at depth 2 and a
      two-step walk from it lands ON the root. The first differential named that case
      `walk-escapes-root`; BOTH implementations agreed with each other and both were answering a
      mislabelled question, which is the ninth time a differential has proved agreement where the
      fixture was the defect. **Every case now carries its own expectation**, read from the tool's
      `--json` verdict rather than from a line of prose, and a run of the port happens twice: prose for
      the byte comparison, JSON for the claim.
      **FALSIFICATION: 14/14 mutations caught by a real assertion, 3 MEASURED-EQUIVALENT, 0 survivors,
      0 could-not-apply, 0 collection-only kills. THE FIRST TWO FALSIFICATION PASSES REPORTED 17
      KILLS THAT WERE ZERO KILLS.** Both were harness defects, and both are the kind that make a
      falsification look better than it is: (1) the mutant was written to a temp directory, so it could
      not `import cscan` and every "kill" was a collection error — a suite that never ran pins nothing;
      (2) every mutation was ALSO killed by `test_the_default_root_is_the_repository_the_tool_ships_in`,
      which fails for a relocated script because its default root is the temp directory's parent. That
      test is now excluded from the kill accounting with the exclusion reported, and excluding it
      exposed **two real holes in my own suite**: the `build_output_is_not_scanned` fixture planted a
      three-step walk at depth 3, where it lands ON the root and is not a violation at all, so dropping
      the `obj/` skip changed nothing; and the sort fixture used three files in `A`/`M`/`Z`, which the
      scanner already reads in sorted order, so removing `sorted()` changed nothing. The sort is only
      observable for two findings in ONE file on lines 4 and 10 — `":10:" < ":4:"` — and the first
      attempt used line 9, where `":4:" < ":9:"` and the two orders coincide.
      **`MAX_PASSES` NEEDS A SHAPE THAT DOES NOT OCCUR NATURALLY, AND THAT TOOK THREE ATTEMPTS.** C#
      forbids using a local before declaring it inside one method, so every in-order chain resolves in
      one pass; and the REPORTING loop is a separate full pass over every call, so even a one-hop
      out-of-order chain is already resolved by the time findings are computed. Only a TWO-HOP
      out-of-order chain needs three passes, and that is the shape now pinned, with the reason stated.
      **THE THREE EQUIVALENTS ARE MEASURED, NOT ARGUED**, because "equivalent today for an unexamined
      reason" is a classification this program has been fooled by: Python's one-element slice is
      already empty, so `rest_args`' length guard is redundant; all four Keepverse root names are
      already lowercase, so folding the vocabulary changes no answer (and stops being equivalent the
      moment a capitalised name is added); and the pattern is used with `search` not `match`, so
      narrowing it to the bare `Path` still finds the trailing `Path` in `System.IO.Path.Combine` —
      namespace tolerance is real, but it comes free from substring search.
      Evidence: 27 fixtures (26 identical / 1 declared / 0 unexplained); 43 contract tests;
      14/14 observable mutations caught and 3 measured equivalents; 6/6 `TestContentRootGuardTests`
      against the `.py`; three reachability proofs including `--deleted-paths` mapping the retired
      `.ps1` through the owner row's GLOB; `audit-doc-citations --strict` 0 HIGH over 26,037
      citations; 53 tracked `.ps1`/`.bat`/`.cmd` remain and 1 of 29 registry guards is still on
      PowerShell (`sim-fabrication`).

- [x] **3.5aj** `mutate` (205 lines) — the second caller of the resolver `coverage` duplicated, so this
      port CLOSES that duplication rather than adding a third copy. Its census was wrong the same way
      `coverage`'s was: it reported one EXECUTE site and zero registry rows, while `git grep` shows the
      site is the word "mutate" in prose and the registry row is a `verificationExemptions` entry.
      **THE BOUNDARY OWNER ROW WAS MISSING**, as it was for `coverage` — nothing selected a verification
      boundary for this tool. Added, with both spellings so the deleted `.ps1` stays mappable.
      **THE ORIGINAL DISCARDED EVERY LINE OF TEST OUTPUT, IN THE ONE TOOL WHOSE JOB IS ATTRIBUTING
      FAILURES.** Both suite invocations ended in `*> $null`, commented "a mutant run is all noise". So its
      red-baseline throw named the project and not one failing test, and every "caught" verdict carried zero
      evidence. The port keeps the output and puts the failure tail on the refusal.
      **THERE WAS NO TIMEOUT ON ANY INVOCATION, AND THIS TOOL INVOKES SUITES N+1 TIMES** — a baseline plus
      one full run per mutant. A wedged `dotnet test` held the pass open forever.
      **THE FIRST VERSION OF THE SPLICE WAS WRONG FOR EVERY LF FILE, AND ONLY A BYTE COMPARISON SAW IT.**
      It mapped the normalised match offset back with `len(prefix) + prefix.count("\n")`, which is right
      only when the source is CRLF; on an LF file the prefix length already equals the normalised index, so
      every newline counted twice and the replacement landed one character early — `keep = 1;` became
      `kekeep = 2;`. A string-level assertion does not see that, because the result still contains the
      replacement text. The offset map is now a single walk of the original, and the cases assert exact
      bytes.
      **A MUTANT THAT WAS NEVER LOADED WAS REPORTED AS A NO-OP.** `mutate.py` runs
      `sys.path.insert(0, <its own gk-core/scripts/lib>)` at import, so pointing the suite's lib override at a
      mutant copy is OVERRIDDEN by the tool and the real module loads instead. The probe could not see the
      mutation and the harness classified it "no observable behaviour" — which reads as diligence and is
      worth nothing. This is the program-wide "a mutant that cannot import its shared dependency" trap in
      a subtler form. Fixed with a `scripts/`-shaped layout so the tool's own path-relative insert resolves
      to the mutant, plus a probe field naming the file actually imported, so a silent mis-load can never be
      classified again. The guard needed three corrections of its own to become trustworthy: it compared a
      raw string against a resolved path, then a short (8.3) temp path against a resolved long one, then a
      DIRECTORY against a FILE — each reporting a false alarm on a mutant that had demonstrably loaded.
      **THE PROBE ITSELY INVENTED 21 NO-OPS.** The first probe answered two questions, so every mutation
      touching outcomes, precedence, the baseline, the restore, the loaders or the envelope looked inert.
      It is now an end-to-end run over a throwaway repository, and a mutation the probe cannot distinguish
      is reported **PROBE-BLIND** — an explicit admission — never as a no-op.
      **THE RESTORE IS NOW MEASURED, AND A `.py` TARGET IS RESTORED TIMESTAMP-INCLUSIVE.** The original
      moved a `.bak` over the file and never checked the bytes came back, in the one tool that corrupts
      tracked source on purpose. The port compares the restored bytes and REFUSES on a mismatch rather than
      reporting a clean run over a tree it damaged. A `.py` target also gets its mtime back, so the tool
      leaves no trace at all — which the original never achieved either, since moving the backup restamps
      the file whatever the rule says.
      Contract suite: **50 tests**. Falsification: **28/28 mutations killed, 0 survivors, 0 no-op, 0
      collection-only, 0 anchor-miss**, with 7 kills where the probe is blind and the suite is the sole
      evidence. Differential: the port's resolution agrees with the transcribed `Resolve-MutantProject` on
      **every real mutant set on disk** — 8 sets, 0 differences, reaching 2 distinct projects, and the
      harness refuses to report success when every set resolves to one project.
      **`source_path_token` NOW ACCEPTS THE `src/` PREFIX**, which is the shape a mutant set's `file`
      field actually stores. Without it the token was the whole `gk-core/src/FusionRpg.Core/World` string and matched
      nothing in the manifest, so a mutation score would have been measured against the residual.
      Scoped verification: **95 passed** across this suite and `coverage`'s; the guard project 64 passed with
      the one pre-existing failure, re-proved after this port's registry edit by reverting the file to the
      **HEAD bytes with the SHA checked** and asserting `mutate-tool` absent.

- [x] **3.5ai** `coverage` (106 lines) — the first port whose subject is a NUMBER a reader trusts, and
      the census was wrong about it twice over, so both corrections are recorded. It reported **15
      EXECUTE sites** across 5 test files; `git grep` shows **none of them execute it** — every one is
      the *word* "coverage" in prose or a test name. It also reported **0 registry rows**, and there is
      one: `scripts/coverage.ps1` sat in a `verificationExemptions` row, which the census's guard-shaped
      query does not see. A census is a briefing; `git grep` is the check.
      **THE BOUNDARY OWNER ROW WAS GENUINELY MISSING**, which is the defect census did report and the
      one thing here that was a real gap: nothing selected a verification boundary for this tool, so
      editing it selected nothing. Added, carrying both spellings so a deleted `.ps1` stays mappable.
      **THE RESOLVER WAS DUPLICATED, AND THE PORT COLLAPSED IT.** `coverage.ps1` and `mutate.ps1` each
      carried their own copy of the folder-token -> project lookup against
      `gk-core/tests/core-test-projects.v1.json`, already diverging on the first line: one read the token from a
      NAMESPACE, the other from a FILE PATH. Two copies of the rule that decides WHICH TESTS RUN is how a
      namespace's coverage ends up measured against a different project than the same folder's mutation
      score. It now lives once in `gk-core/scripts/lib/core_test_project.py` and `mutate` imports it when ported.
      **A DIFFERENTIAL THAT PASSED BECAUSE ITS INPUTS WERE DEGENERATE.** The first resolver comparison
      derived its token set from `project["name"].split(".")[1]`, which for
      `FusionRpg.Core.ActorHub.Tests` yields `Core` — so every case asked the same meaningless question
      and it reported ten agreements that tested almost nothing. Re-derived from the `include` entries the
      matcher actually compares against: **280 generated cases, 0 differences, 63 distinct projects**, and
      the harness now **refuses to report success when every case resolved to the residual**, because a
      comparison that never leaves the fallback proves nothing.
      **THE PORT FIXES A LATENT WILDCARD BUG, DECLARED.** `-notlike "$Namespace*"` treated the namespace
      as a wildcard while the sibling `-replace` on the next line correctly escaped it — the same concept
      escaped two ways, so `-Namespace 'FusionRpg.Core.*'` matched every class in the project and reported
      a total as if it were one namespace's. The port compares prefixes, as the original's own SYNOPSIS
      says it does, and the divergence is pinned in both directions.
      **THE POWERSHELL ORIGIN'S REAL DIAGNOSTIC DEFECT, REPRODUCED LIVE.** The original piped the run
      through `Where-Object { $_ -match "^(Passed!|Failed!)" }`, so anything else was invisible. A real run
      during this port failed with `error MSB3021: Access to the path ... is denied` — an MSBuild error,
      no `Failed!` line — and the original would have shown **nothing** and thrown only "tests failed". The
      port reported `TESTS-FAILED` and quoted the whole MSBuild error. That is not a hypothetical: a
      mistyped `dotnet test` switch produces exactly this shape, and this repository hit it during the
      `test-sharded` port, where `--no-incremental` is not a `dotnet test` switch and the run silently
      produced no test output at all.
      **THE RECURSIVE-DELETE GUARD WAS FIRST WRITTEN WHERE IT COULD NOT FIRE, AND THE TEST IS WHAT
      CAUGHT IT.** `Remove-Item -Recurse -Force` on a path assembled from a caller-supplied project had no
      check. The first guard tested `results_dir.name != "TestResults"`, which is **unreachable**: the
      path is built as `repo / project / "TestResults"`, so its last segment is that literal by
      construction. A guard that cannot fire reads as protection in review. The reachable hazard is a
      `project` that is absolute or contains `..`, so that is what is checked — and **both sides are
      `.resolve()`d**, because `is_relative_to` compares LEXICALLY and `repo/../elsewhere/TestResults`
      still "starts with" `repo`. The test failed with `NO-RESULTS-DIR` instead of `RESULTS-DIR-UNSAFE`,
      which is how the escape was noticed: it sailed through the guard and the delete then found nothing.
      **A REAL END-TO-END RUN, GREEN.** `python gk-core/scripts/coverage.py --project
      gk-core/tests/FusionRpg.Core.ActorHub.Tests --namespace FusionRpg.Core --json`: **exit 0, 2598 classes,
      67462 lines, 2673 covered, 76s wall**, worst-first, with `n/a` in the branch column exactly where a
      class has no branch sites. A second real run `--namespace FusionRpg.Core.ActorHub` REFUSED with
      `NO-MATCHING-CLASSES` and named the project it had actually run — and it was right to: the manifest
      maps a TEST FOLDER to a test project, and `FusionRpg.Core.ActorHub` is not a production namespace,
      so there was genuinely no such class. The refusal's detail is the useful part, and it is there.
      Contract suite: **45 tests**. Falsification: **28 of 29 mutations killed, 0 survivors, 0
      collection-only, 0 anchor-miss, 1 MEASURED EQUIVALENT.**
      **FOUR SURVIVORS ON THE FIRST PASS, AND TWO OF THEM WERE NOT HOLES.** `residual-fallback-dropped` is
      equivalent on this tree because the manifest's `residual` is currently `FusionRpg.Core.Tests`, the
      same string as the built-in fallback; it is made observable by planting a manifest with a
      DIFFERENT residual name, which is why an equivalent is recorded rather than chased.
      `empty-remainder-token-accepted` is equivalent because the explicit `if not remainder` above it
      already returns None. The other two were real: **first-match-wins in manifest order** was unpinned
      (so a "most specific wins" tie-break could silently re-point a folder's tests), and **the Core
      prefix test being Ordinal** was unpinned. Both now have planted-manifest cases where the two rules
      disagree, so neither can pass vacuously — the first attempt at the first-match case gave the second
      project an `include` that matched NEITHER shape, so only one candidate existed and first and last
      agreed.
      **A MUTANT THAT CHANGED NOTHING WAS REPORTED AS A SURVIVOR.** The last-match mutant declared
      `last = None` INSIDE the loop it was converting, so the variable was reset every iteration and the
      `if last: return` beneath it still returned on the first match. The suite correctly said SURVIVED
      and that reading was about the mutant, not the suite. The falsifier now **probes the mutant's own
      behaviour before asking the suite about it and refuses to classify a mutant whose probe output is
      identical to the reference's** — the harness is a tool and its defects are found the same way.
      **THE `core`-PROJECT PORTION OF THE SCOPED VERIFICATION COULD NOT RUN, AND THE REASON IS NOT
      MINE.** Repointing one prose citation in
      `gk-core/tests/FusionRpg.Core.Tests/World/Topology/ReconnectionCostBench.cs` selects that directory's
      declared owner, `core-tests-fallback`, at `module` level — 80-odd test projects. It failed on
      `ResidualFitLoopTests` and on `error MSB3021: Unable to copy file ... Access to the path ... is
      denied`, and the build itself fails the same way: the target DLL is **absent from disk** while 12
      `dotnet` processes started at the same minute are running. Another session is building concurrently.
      Killing them is not this session's call, so the block is reported rather than worked around. The
      remainder of the scoped verification is green: **45/45** on the port's own suite, and on the guard
      project 64 passed with the single failure below.
      **PRE-EXISTING FAILURE, RE-PROVED AFTER THE REGISTRY EDIT.** `SplitCoreVerificationMappingTests.
      Planner_resolves_representative_split_core_files_to_area_owners_not_residual` fails in the guard
      project. Its subject IS `verification-boundaries.v1.json`, so the earlier control — taken before
      this port added a row — did not cover it, and the registry was reverted to the **HEAD bytes with
      the SHA checked** and the row's absence asserted. It fails identically with the row and without it.

- [x] **3.5al** `verify-change.ps1` (493 lines) + `lib/VerificationBoundaries.ps1` (366 lines) — the
      program's KEYSTONE, and the one remaining item where the Python twin ALREADY EXISTS for both files.
      Deleting these is not a fresh port; it is a **deletion with the proof already committed**.
      - `gk-core/scripts/verify-change.py` and `gk-core/scripts/lib/verification_boundaries.py` are both live. The
        differential in `gk-core/tests/tools/test_verify_change.py` already runs the two implementations against
        each other, so equivalence is established evidence rather than a claim this change has to make.
      - `verify-change.ps1:14` dot-sources `lib/VerificationBoundaries.ps1`, so the two retire TOGETHER --
        which is why they are one block and not two.
      - The consumers are **C# tests, not scripts**: 52 references in
        `VerificationBoundaryWorkflowTests.cs`, 6 in `VerificationBoundaryMappingRepairTests.cs`, 3 each
        in `DocBoundaryTests.cs` / `SplitCoreVerificationMappingTests.cs` /
        `VerificationTopologyTests.cs`, 1 each in `DocCitationAuditTests.cs` /
        `ClassSystemPhase9ReadinessGateTests.cs`. Plus `scripts/run-guards.ps1`, `scripts/test-fast.ps1`
        and ~100 `AGENTS.md` / `.claude/**` / `.agents/**` prose citations.
      - **The spawn surface is small even though the reference count is large.** Each test file funnels
        through ONE helper that takes a raw argument string -- `RunPowerShell(string arguments)` in
        `VerificationBoundaryWorkflowTests.cs:28-39` and `Plan(string path)` in `DocBoundaryTests.cs:30-40`
        -- so the change is a helper rewrite plus a dialect swap, not 70 edits.
      - **The flag mapping is 1:1 and was read from `--help`, not assumed**: `-Paths a,b` -> `--paths a b`;
        `-DeletedPaths x,y` -> `--deleted-paths x y`; `-PlanOnly` -> `--plan-only`;
        `-AllowUnscoped` -> `--allow-unscoped`; `-Format json` -> `--format json`; `-Session` / `-Root`
        unchanged apart from the double dash. The Python adds `--timeout` and `--diff-base-ref` /
        `--diff-head-ref`, which the PowerShell never had.
      - Three fixtures COPY the `.ps1` into a planted root (`VerificationBoundaryWorkflowTests.cs` at
        654/769/1019/1235/1518/1562/1623/1729, `VerificationBoundaryMappingRepairTests.cs:234-241`).
        Those copies become `.py`, and the `// BOTH libs` comments at 774/1024/1523/1567/1628/1734 are
        WRONG TODAY -- the comments say the PowerShell lib `is still live`, and this block is what makes
        that sentence false, so they are edited in the same commit.
      - `RepoRoot()` in four test files walks up looking for `scripts/verify-change.ps1` and throws
        `DirectoryNotFoundException` naming it; the marker becomes the `.py` or the walk finds nothing.
      - `VerificationTopologyTests.cs:142,276,302` READS the planner as text and asserts on it, so that
        test is amended to the Python's shape the way `Native_packaging_commands_are_each_failure_checked`
        was in 3.5ak.
      - **Ordering constraint found this session, and it is the reason the three remaining `lib/*.ps1`
        are LAST and not first.** A PowerShell lib is consumed by DOT-SOURCING, which has no Python
        equivalent; a consumer only stops needing the `.ps1` when it is itself ported. So porting
        `KeepverseRoots.ps1` / `DebugStatusApply.ps1` / `LiveLawnSetup.ps1` before their ~20 live-probe
        consumers would leave the library deleted and every consumer still dot-sourcing it. The libraries
        retire with their LAST consumer, not before it.
      - **Prerequisite to check first:** `gk-core/tests/tools/test_verify_change.py:40,46` hold `PS_PLANNER` and
        `PS_LIB` as the differential's oracle. Deleting the files means deleting one half of that
        differential, and the surviving half must still be shown to pin something -- otherwise the change
        trades a cross-implementation check for a self-consistent one, which is a real loss and belongs
        in the commit message, not in a footnote.
      - No live run is required: neither file touches the game, the pool or a port. This is the largest
        remaining item that needs **no** Tier-3 live proof.

- [x] **3.5an** `test-fast.ps1` (194 lines) — and the finding it produced is worth more than the port.
      Population **47 -> 44**. Two scrapers read this file's SOURCE for the default filter
      (`verify-change.py:83` and `test_sharded.py:85`), so the constant's SHAPE is a contract with two
      readers, and the port had to keep the spelling they look for. The first repair made
      `verify-change.py`'s pattern `\$?[Ff]ilter`, which matches `Filter` and `filter` and NOT `FILTER` --
      so a pattern that LOOKED tolerant was not, and every plan in the tree would have answered
      `DEFAULT-FILTER-UNREADABLE`. `re.IGNORECASE` is the honest spelling of tolerant; a two-character class
      is a partial one.
      **THERE WAS NO TIMEOUT ON ANY OF ITS 71 `dotnet test` INVOCATIONS.** `--blame-hang` is a hang
      DETECTOR, not a kill switch: it dumps and kills a hung test HOST and says nothing about an MSBuild
      node waiting on a locked feed. Every call is now bounded, and a timeout names the project.
      **A FAILING PROJECT DID NOT STOP THE LOOP AND THE EXIT CODE NAMED ONLY THE FIRST.** The original ran
      all 71 and kept the first failure's code, so a run with 40 reds exited with one project's code and
      printed 40 lines. The port collects every failing project, names all of them, and still exits with
      the first non-zero so the code stays comparable.
      **THE LIST'S OWN COMMENT WAS FALSE, AND NOBODY HAD MEASURED IT.** It claimed `core-split-wiring`
      "keeps this list in full ... a Core split increment that forgot this list would silently drop the
      moved tests". Measured: 0 of 71 entries are stale, but **11 of the 84 test projects on disk are
      absent, and 11 of those 11 are wired into `ci.yml`** -- including `FusionRpg.Guard.Tests`, 117 test
      files. The local profile is not a proxy for CI, and none of the 11 is in `nightly.yml` either.
      **THE PORT DOES NOT QUIETLY ADD THEM.** That changes what every ordinary agent run costs, which is
      the owner's call and not a porting detail -- so the asymmetry is recorded in the module docstring,
      in `DECLARED_EXCLUSIONS`, in the report and in the commit, and left to be ruled on.
      **WHAT IT DOES IS MAKE THE SET CLOSED.** `DECLARED_EXCLUSIONS` names every project deliberately not
      in the default profile, each with a reason, and a project on disk in NEITHER list is an
      `UNDECIDED-PROJECT` refusal. That is what makes the comment true: a new test project can no longer
      arrive without someone deciding whether the default profile runs it.
      **I HAND-TRANSCRIBED 71 PROJECT PATHS AND GOT ONE WRONG.** `FusionRpg.Core.EffectGrantTests.Tests`
      does not exist, and `test_EVERY_listed_project_EXISTS_in_this_repository` failed on it -- a list
      check that asserted a LENGTH would have passed. The constant is now EXTRACTED from the original by
      script, in order, with every entry verified to exist, so the next reader can diff the two.
      **THE GUARD WAS REPOINTED, AND THE SPELLING BESIDE IT WAS NOT.** `test_sharded.py`'s table names
      `test-fast.py` -- KEBAB -- while the ported file is `test_fast.py`, snake, because a Python module's
      stem has to be a valid identifier. I repointed the `.ps1` entry and left the neighbouring `.py`
      entry, so the reader looked for a file that does not exist and answered `NO-DEFAULT-PROFILE-FILTER`,
      failing **7 guard tests**. The only signal was that refusal NAME; message prose would have sent the
      next reader to the wrong file. Same class as the `verify-change` name in 3.5ak.
      **A PRE-EXISTING GAP, CLOSED BECAUSE THIS CHANGE TOUCHED THE PATH.**
      `gk-core/scripts/test_deploy_play.py` had no owner row and no exemption -- the tool it tests is exempted and
      the test was not -- and `--plan-only` refused it outright. Naming the test beside its tool in the
      same exemption is one decision in one file, rather than one that can be half-moved later.
      **THE POWER-SHELL SPAWN HELPER IS GONE FROM ONE FILE.** `test-fast` and `run-guards` were its only
      two reasons to exist; with the first ported it had no callers, and a private method with no callers
      is the reason a reader believes a file still spawns a shell.
      Contract suite **37 tests**, 6/6 clean over six runs. Falsification **26 mutations killed, 0
      survived**, in two runs: 21 in the main falsifier and 5 in a second written to cover the six whose
      in-place repairs I could not land. **Two survivors in the first run were real holes** -- no
      `--json` envelope-key case at all, and no coverage of the `.ps1` fallback the tool promises -- and
      both now have cases; the second falsifier found 0. Two further mutants are killed but through an
      `AttributeError` (a renamed constant breaks every case that reads `tf.FILTER`), which the harness
      classifies BROKE; the suite went red, which is the kill, so the classification is the harness's
      imprecision and not a hole.
      Scoped verification: **108 passed** across `test_test_fast`, `test_verify_change`, `test_test_sharded`
      and the other tools suites; the guard project **712 passed / 4 failed**, and all four are
      pre-existing -- re-proved with a control that reverts BOTH registries to HEAD bytes and restores in
      a `finally`.
      Next: `scripts/run-guards.ps1` (252) is the LAST file holding a PowerShell spawn alive in the guard
      project, and it is wired into `ci.yml`, `nightly.yml`, `release.yml`, `deploy-play.py:435` and four
      C# test files.

- [x] **3.5am** `verify-change.ps1` (493 lines) + `lib/VerificationBoundaries.ps1` (366 lines) — the
      KEYSTONE, and the first deletion rather than a port: both Python twins already existed, both were
      live, and `gk-core/tests/tools/test_verify_change.py` already ran the two implementations against each
      other. Population **47 -> 45**.
      **THE CONSUMERS WERE C# TESTS, AND THE REFERENCE COUNT WAS A LIE ABOUT THE WORK.** 52 references
      in `VerificationBoundaryWorkflowTests.cs`, but each file funnels through ONE spawn helper, so the
      change is a helper rewrite plus a dialect swap -- not 70 edits. `RunPowerShell` is KEPT for
      `scripts/test-fast.ps1` and `scripts/run-guards.ps1`, which are unported; two dialects side by side
      is the honest state of the tree mid-migration.
      **THE ARGUMENT DIALECT CHANGED, AND A MECHANICAL FLAG RENAME WOULD HAVE PRODUCED AN EMPTY PLAN.**
      `-Paths a,b` took a PowerShell ARRAY; argparse takes space-separated values, so leaving the commas
      hands it ONE path named "a,b", which resolves to nothing -- and an empty plan reads as a scope
      refusal rather than as a bug. `PowershellPathArray` became `PathArguments`.
      **SEVEN C# TESTS WERE NOT C# TESTS.** Each built a PowerShell script, dot-sourced the library, and
      asserted on what `Write-Host` printed -- so deleting the library would have deleted six real rules
      (exact-beats-wildcard, grammar confinement, three knownRed outcomes) with no replacement. They now
      run a Python probe that IMPORTS the library by path and prints the SAME tokens, so the assertions
      are unchanged -- a port that also rewrote the expected strings could not tell a correct port from
      one that changed the ANSWER.
      **THE DIFFERENTIAL'S EVIDENCE SURVIVES ITS ORACLE; ITS ABILITY TO DISCOVER DOES NOT.**
      `gk-core/tests/tools/fixtures/verification_boundaries_parity.json` holds the PowerShell library's ACTUAL
      answers -- 84 pattern matches, 7 grammar verdicts, 7 specificities, 12 owner resolutions -- captured
      by running the real `.ps1` immediately before deleting it, and the harness refuses to write a
      golden whose answers are all one value. A Python regression on any of the 110 still fails.
      **What died is named, not buried.** The two PLANNER comparisons ran both tools over the REAL
      registry and asserted identical text and identical JSON. Nothing replaces that: a differential
      discovers bugs by asking questions nobody thought to ask, and a golden only answers questions
      already recorded. Two of three parity tests are gone, and the class docstring says so.
      **32 TESTS STOPPED BEING CONDITIONALLY SKIPPED.** `PlannedFixtureTests` carried
      `@unittest.skipIf(powershell() is None)`, but nothing in it ever spawned PowerShell -- the fixture
      copies the Python guard and the Python lib, and `_plan` goes through `run_tool`. On any machine
      without pwsh on PATH, 32 tests were skipped while the run still reported green.
      **THE FIXTURE COPIED THE SAME FILE TWICE, AND NOBODY NOTICED FOR MONTHS.** Lines 592-593 were the
      identical `shutil.copy2(PS_LIB, ...)` under a comment justifying "BOTH libs". Harmless while the two
      sources differed; a hard `IOException` the moment the same mechanical mapping pointed both copies
      at one file. Six C# planted-root fixtures had the same latent collision.
      **A BLANKET REPLACE INVERTED A HAND-WRITTEN ASSERTION.** The token sweep that repointed the file
      also rewrote the strengthened guard from forbidding `verify-change.ps1` to forbidding
      `verify-change.py` -- so it failed on every legitimate mention and would have PASSED on exactly the
      defect it exists to catch. Found by reading the failure's line and then reading the file, because
      the line provably did not contain the string the message named. A hand-written assertion and a
      mechanical rewrite must not share a file unchecked.
      **THE MULTI-LINE STRING TRAP, HIT THREE TIMES.** A C# call splits its flags across two literals,
      so a transform keyed on "this line names the tool" rewrites the first and skips the second; the
      call then reaches argparse with PowerShell spellings and dies at parse time with exit 2 and EMPTY
      stderr. The final sweep walks from each `RunPlanner(` to its closing `);` and rewrites only inside
      that span -- necessary because `-Root`/`-Session`/`-Tier` are also run-guards and test-fast flags.
      **ONE STALE-STRING CLASS A LINE-KEYED SWEEP CANNOT REACH, BY CONSTRUCTION.** A test's ASSERTIONS
      name nothing, so six assertions kept the PowerShell text (`VERIFICATION BOUNDARY MISSING`,
      `outside session scope`, `verification registry integrity guard failed`). All now assert refusal
      NAMES from the tool's own closed vocabulary -- `BOUNDARY-MISSING`, `PATH-OUTSIDE-SESSION`,
      `INTEGRITY-GUARD-FAILED` -- which is strictly better: a name is what a caller branches on and
      prose is not.
      **A PRE-EXISTING GAP, PROVEN NOT INTRODUCED.** `--deleted-paths scripts/lib/VerificationBoundaries.ps1`
      refused with `BOUNDARY-MISSING` BEFORE this change touched the boundary registry. The four candidate
      registry shapes were each run against the real planner: the owner-row shape naming the path is
      refused by the guard's stale-exact-path rule, and `gk-core/scripts/lib/*.ps1` resolves but would also claim
      `KeepverseRoots.ps1` and `LiveLawnSetup.ps1`. The exact-path EXEMPTION resolves without over-claiming,
      and its required `reason` carries the measurement.
      **`Filtered_verification_requires_a_non_empty_test_result_document` ASSERTED A FUNCTION THAT NEVER
      EXISTED in the Python.** It required `Get-JUnitTestCases` -- PowerShell only -- so the port could
      only ever fail it. Replaced with the closed set of ways a run yields no evidence
      (`ZERO-TESTS`, `TEST-EVIDENCE-AMBIGUOUS`, `ZERO-PYTESTS`, `DIFF-FENCE-INCOMPLETE`), all of which the
      tool really declares, and the behavioural half was already covered by the planted-root test below it.
      Verification: **71 passed** (`test_verify_change.py`), **56** (`test_guard_verification_boundaries`),
      **8** (`test_lib_verification_boundaries`); the guard project **78 passed / 1 failed**, the failure
      being the pre-existing `SplitCoreVerificationMappingTests`, re-proved against HEAD bytes with a
      control that restores in a `finally`. **BLOCKED, reported as blocked:** `guard.generated-seed` flags
      `gk-data/packs/fusion/data/seed/items/materials/materials.json`, dirty work owned by ACTIVE record
      `mega-merge-program-manager-20260925-f78e` -- proved by INTERSECTION again, since this change
      touches no `gk-data/packs/fusion/data/seed/**` path.
      Next in this lane: `scripts/test-fast.ps1` (183) and `scripts/run-guards.ps1` (252) are the two files
      still holding the `RunPowerShell` helper alive, and `test-substrate-leak-alarm.ps1` (105) needs its
      `[scriptblock]$Run` argument redesigned to argv before it can be ported at all.

- [x] **3.5ak** `publish-player` (244 lines) AND its only PowerShell caller `sync-ci-drop-into-game`
      (43 lines), ported in ONE change because deleting the first would have left the second calling a
      file that does not exist — a break discovered only while cutting a release. The census was wrong in
      a new way: it reported **1 registry row and 2 EXECUTE sites**, and `git grep` shows the registry
      row is a **boundary** row (`player-pack-packaging`) rather than an exemption, the exemption entry
      was for the **caller** instead, and the 2 EXECUTE sites are a C# test that reads the file as TEXT
      and `.github/workflows/release.yml` which **runs it**.
      **THE SAFETY OF THE WHOLE PACKAGE DEPENDED ON AN INVARIANT NO TEST COULD SEE.** `$LASTEXITCODE` is
      a side effect, not a return value, and the original read it after each of `npm ci`, `npm run
      build`, two self-contained `dotnet publish`es and two `dotnet build`s — so whether a failure was
      noticed depended on nothing ELSE native having run in between. One `run()` now invokes every
      external command and raises on a non-zero exit, and the property is **STRUCTURAL**:
      `every_external_command_goes_through_run` asserts by AST that `subprocess.run` is called from
      exactly one place, and the amended `Native_packaging_commands_are_each_failure_checked` counts the
      same call sites repository-side. Substring-near-a-command cannot prove the property; counting the
      call sites can.
      **`sync-ci-drop-into-game` DISCARDED ITS PUBLISHER'S EXIT CODE AND THEN CHECKED THE ARTEACT.** `&
      publish-player.ps1` ignores the exit, and the very next statement verifies `DropIntoGame` exists —
      which a PREVIOUS run's drop also satisfies. So a publish that produced nothing would refresh the
      cache from old files and report success. The port checks the exit AND the mtime against a stamp
      taken before the publish, which is the check that distinguishes "this publish produced it".
      **AND THAT STAMP IS A REAL BUG I SHIPPED, CAUGHT BY RUNNING THE SUITE EIGHT TIMES.** The first
      version took it from `time.time()` and compared it to `st_mtime` — two different clocks, and the
      write timestamp can land behind the sample. On a fast machine a drop published microseconds after
      the stamp was judged STALE: **6 of 8 runs and 3 of 8 failed, on two different cases**, which is the
      shape of a race rather than a bad assertion. The stamp now comes from a planted file's own mtime, so
      both sides of the comparison are one clock, with a documented 2s tolerance for filesystem
      timestamp rounding. **8/8 clean after the fix.**
      **THE PORT SURFACED A DEFECT THE FILE'S OWN COMMENT DOCUMENTS AT LENGTH**: `Server\data` was deleted
      here until 2026-09-23, and with the tree gone a player install answers `SeedTreeNotFound` forever
      and `/health` reports `contentSource: "codeFallback"` — the whole content layer on the fallback.
      The port makes it a **REFUSAL**, so a pack without it exits non-zero instead of shipping.
      **THE CALLER'S TWO CITATIONS ARE BOTH NOW TRUE AND BOTH WOULD HAVE BEEN FALSE.** It names
      `scripts/fetch-bepinex-refs.ps1`, which is **still a `.ps1` on disk** — naming a `.py` would be the
      rot citation introduced by the very commit that removes rot citations, and a contract case now
      **resolves the named path and fails if it does not exist**. And the Melon stage names
      `guard-game-profile.py`, which is **kebab** because that guard was ported without a stem change, so
      a second case asserts the spelling against the filesystem.
      **FOUR OF MY OWN CASES TESTED A MOCK INSTEAD OF THE CODE.** The fixture faked the pipeline stages,
      and the CI-drop, lockfile, `Server/data` and melon cases each reached the FAKE and asserted
      nothing. The fake is now keyed by stage with an `unfake()`, because a case that silently tests a
      mock always passes, which is worse than a red because it stops looking.
      **TWO UNSATISFIABLE ASSERTIONS IN THE AMENDED C# TEST, BOTH THE SAME CLASS.** The port's docstring is
      **REQUIRED** to name `$LASTEXITCODE`, `Assert-NativeExit` and `Write-Warning` while explaining what
      it replaced, so `Assert.DoesNotContain` over the whole file can never pass for a correct port — and
      leaving it in invites the next author to delete the provenance instead of the assertion. The
      dialect check is stronger where it lives: the contract suite strips docstrings and comments **by
      AST** and scans the CODE.
      **TWO LOCAL CHECKS I WROTE REFUSED A VALID CHANGE, AND THE LESSON IS THE POINT.** First a
      "no recursive delete without a containment check" hole in the suite (the original ran
      `Remove-Item -Recurse -Force` on a configuration-derived path with no containment test at all).
      Then an overlap check on the boundary registry: it refused on **30+ rows** whose `**` globs
      legitimately cover the same tree, and refused AGAIN on duplicate pattern strings. Both refusals
      **wrote nothing**, so a check stricter than the rule it verifies does not merely fail — it silently
      blocks the real change while reporting a problem the guard does not have. The guard is the judge.
      Contract suite: **46 tests**. Falsification: **32/33 mutations killed, 0 survivors, 0 broke, 0
      anchor-miss, 1 measured-equivalent** (a `.ps1` added to a **docstring**, which the dialect guard
      deliberately excludes, because a docstring naming what it replaced is documentation). Of the four
      mutations the probe could not distinguish, **all four were real suite holes** and all four now have
      cases: the generic `OSError` branch, a RUN of leading `v`s (the input that separates
      `.TrimStart("v","V")` from a single strip), the three Bep drop destinations inside `publish()` (both
      probe and suite had been calling `copy_with_suffixes` **directly**), and the Melon missing-DLL
      refusal (both had only ever built a drop that produced the DLL).
      Couplings: the exemption entry for the caller repointed to `scripts/sync-ci-drop-into-game.*`; a new
      **`player-pack-tool`** owner row carries both globs, both `.py`, the suite, `tools-audit-tests` and
      `focused`; and `player-pack-packaging` gives up `publish-player.*` and keeps only
      `scripts/smoke-player-pack.ps1`, because the guard forbids two rows matching one pattern and
      `testFiles` is legal only on a pytest project.
      17 repointings: `release.yml`, the C# test, six player-facing **strings** (a stale command in an
      error message is a support ticket), two csproj comments, `Directory.Build.props`/`.targets`,
      `smoke-player-pack.ps1`'s refusal text, two test comments and `README.md`.
      Scoped verification: **46 passed** for the tool paths, `enforcement-registry` and `release.yml`
      green. **BLOCKED, reported as blocked and not green:** `guard.generated-seed` flags
      `gk-data/packs/fusion/data/seed/items/materials/materials.json`, which is dirty work owned by ACTIVE record
      `mega-merge-program-manager-20260925-f78e` — proved by **intersection** (this change touches no
      `gk-data/packs/fusion/data/seed/**` path) rather than by a revert, because reverting another session's uncommitted work
      is forbidden. And the pre-existing `SplitCoreVerificationMappingTests` failure was re-proved after
      this port's registry edits with a control that **restores in a `finally`** — the earlier control did
      not, and it silently took the couplings with it.
      Population: 49 -> **47** tracked `.ps1`/`.bat`/`.cmd` (40 `scripts/`, 4 `gk-core/scripts/lib/`,
      1 `gk-core/scripts/checks/`, 1 `.claude/cmdc-agents/scripts/`, 1 `tasks/reports/`).

- [x] **3.5ao** `run-guards.ps1` (252 lines) — the LAST file holding a PowerShell spawn alive in the guard
      project, and the port that found two **vacuous** guard assertions and a **dead** planner call.
      **A DIFFERENTIAL, TAKEN WHILE THE `.ps1` STILL EXISTED.** This tool had no Python twin and no
      pre-existing differential, so one was built HERE — 11 cases over the real catalog, 8 of them
      reaching the guard loop, compared on the selected guard set and every exit code. It agrees with the
      original **0 disagreements**, including on the four guards that are genuinely red in the local tier
      (`doc-citations`, `game-profile`, `population-pin`, `session-boundary`) — which is where the evidence
      is, because a port that dropped a failure would agree on the green ones. **Deleting the oracle
      without taking this reading first would have spent the evidence.**
      **THE DIFFERENTIAL FOUND A REAL DEFECT IN MY OWN FIRST VERSION.** On every tier with a red guard the
      original reported 29 guards with their exit codes and my port reported **ZERO**, because it raised on
      the red verdict and threw the whole report away. The original prints its table BEFORE it throws. The
      deeper fault was **CONFLATION**: REFUSED (could not proceed — no registry, no range, empty
      selection, unknown guard) and FAILED (completed, red, results attached) were arriving at one exit
      path. They are separate now, which is what lets `GuardRunnerTests` assert the results survive a red
      run at all.
      **THE HARNESS WAS WRONG THREE TIMES BEFORE THE PORT WAS.** It never passed `--json`, so the port
      printed a table, `json.loads` failed, and every case read "0 guards, no refusal" — the exact shape of
      a vacuous pass. It passed `--ci-range` to the PowerShell side, which does not speak that flag. And
      it compared the original's ANSI-rendered PROSE against the port's refusal NAME, which no
      implementation could agree on. Then it inferred "refused" from a non-zero exit — and the ORIGINAL
      also exits 1 on a red run, so a red run read as a refusal on one side and a failure on the other.
      **WHY THE POWERSHELL FORM WAS RETIRED**, all measured on the original: no timeout on any guard
      invocation, in the longest thing CI runs; the per-guard temp log deleted with
      `-ErrorAction SilentlyContinue` (a swallowed temp delete — the shape behind this repo's 65.5 GB
      incident); the missing-interpreter probe checked `powershell` while dispatch preferred `pwsh`, so a
      PowerShell-7-only machine got a **PHANTOM** warning on the platform it is most likely read on; a
      `Format-Table`-into-a-string summary, so nothing could assert on a run; and a `default` dispatch
      branch that wrote its explanation to a file it then deleted unconditionally.
      Contract suite: **50 tests**. Two of MY OWN cases asserted a rule the tool deliberately does not
      have — the tier filter is **one-directional** (it applies to a `ci` run only; `local` is the widest
      tier by design), and my fixture asserted the opposite. That is the worse direction for a test to be
      wrong in: it reads as a specification, so an edit made to satisfy it would REMOVE guards from the
      local profile.
      **TWO COUPLINGS, BOTH MEASURED.** `guard-runner` keeps `scripts/run-guards.*` as a **GLOB** so the
      DELETED file stays mappable through `--deleted-paths`, and gains `gk-core/scripts/run_guards.py`. A second
      row `run-guards-contract` owns the pytest suite in `tools-audit-tests`, because `testFiles` is
      REFUSED on a non-pytest project — **asked, not assumed**: the guard's own verdict is
      `testFiles only allowed on a pytest project: guard-runner`, and a pytest row carrying a
      `verificationId` is refused too (`verificationId not allowed on a pytest project`). Acceptance was
      not the deciding question, **reachability** was: under the one-row shape both the tool and its
      contract suite selected the `guard` dotnet target and the pytest suite never ran. All four of the
      new path, the contract suite, the C# class and the deleted `.ps1` now select the right runner.
      **TWO VACUOUS GUARD ASSERTIONS, BOTH FIXED, BOTH IN A FILE THIS PORT ALREADY TOUCHED.**
      `EnforcementRegistryGuardTests` matched the runner name with FORWARD slashes while `ci.yml` spells
      paths with BACKslashes, so "ci.yml invokes the runner" **could never fire**; and its hand-wired-guard
      scan `scripts/guard-[a-z-]+\.ps1` matched **ZERO lines** for the same reason. Both normalise the
      separator now, and the scan accepts `.py` too — which is what the ported guards are. Verified against
      real data: both pass, and both can fail.
      **A PROBE-BLIND ASSERTION THAT FAILED TWICE ON A CORRECT DEPLOY.** `GuardWiring`'s deploy scan needed
      to see `--tier local` beside the runner's name. First version scanned for the FILE name
      `run_guards`, but `tool_argv` is called **BY STEM**, so the call site contains `run-guards` and the
      file name appears only in the rename map's value. Second version scanned the stem and still failed,
      because the dialect sits ~**313** characters downstream and the window was 300. It is **per-line**
      now, because the flags are separate argv ELEMENTS — the source spells `"--tier", "local"` — so a
      search for `--tier local` can never match however correct the deploy is. A fixed width over a
      formatted call site is a bet on formatting, and it loses in the direction that LOOKS like a defect.
      **`SplitCoreVerificationMappingTests` WAS DEAD AND REPORTING A WRONG REASON.** It spawned `pwsh` with
      PowerShell array syntax (`@('a','b')`) and a stray quote in argv, so pwsh printed its usage banner
      and exited **64** on every run — the test read "the planner said something I do not understand"
      without ever reaching the planner. Its repo-root probe already looked for `verify-change.py`; only
      the invocation was left behind. **The half-landed replace the ordering rule exists to prevent.**
      With it reaching the planner, the REAL failure surfaced: its Vfx representative `VfxCatalog.cs` is
      claimed outright by `elemental-action-vfx-earth-pilot`, and an exact path outranks `Vfx/**`. That is
      specificity ranking working as documented, so the representative was repointed to a file that is
      still representative (19 of 22 Vfx files do resolve to `core-area-vfx`; the other 3 are legitimately
      claimed) **and a new test pins the override and the area row it overrides** — repointing alone would
      have hidden the fact. `Directory.Build.targets` had **no owner boundary at all** and
      `verify-change.py` refused with `BOUNDARY-MISSING`; it is mapped into `keepverse-roots` beside
      `Directory.Build.props`, the other half of the same MSBuild root wiring.
      Repointings: `ci.yml`, `nightly.yml`, `release.yml` (the `$LASTEXITCODE` idiom **stays** — those
      steps are still `shell: pwsh` and under pwsh a native `python` is a native command), `deploy-play.py`
      (the `-LocalArgs` hashtable that forced `pwsh -Command` is `--local-arg ID:KEY=VALUE`, so the
      `-Command` wrapper, the `@{}` escaping and a pwsh spawn are gone), four C# test files, and six
      prose mentions including `Directory.Build.targets` and `audit-doc-citations.py`.
      **AND THE PRECEDING COMMIT FOUND TWO DEAD DEPLOY PATHS.** `deploy-play.py --full-suite` refused
      `TOOL-MISSING` because `test-fast.ps1` had become `test_fast.py` and the dispatcher resolved BOTH
      old spellings; `--verify --paths` resolved the right file and then handed argparse `-Paths`, so it
      exited 2 on `unrecognized arguments`. Root cause: resolving the FILE is not resolving the ARGUMENTS,
      and resolving by STEM breaks when a port renames the file — `verify-change.py` documents the first
      and already had a `py_args` parameter for it. **The port's dispatcher got the same parameter, and
      `TestToolDispatcher` closes the gap that let both through**, reading the call sites out of the AST.
      Falsified 3/3 with 0 survivors, and independently all six new cases fail against a byte-exact HEAD
      copy of the tool and pass against the new one.
      Scoped verification: **50 pytest passed**, the Core and Guard focused checks ran, Guard module check
      **717 passed / 3 failed** — and all three are PRE-EXISTING, proven by a byte-exact HEAD control that
      restored `gk-core/scripts/verification-boundaries.v1.json` and reproduced them: `LawnCoordsGuardTests` x1 and
      `ClassSystemBaselineRegenTests` x2. A fourth, `SplitCoreVerificationMappingTests`, failed at HEAD
      too and is **fixed** here. **BLOCKED, reported as blocked and not green:** including the session
      record selects the `session-boundary` guard, which fails on DRIFT(3) belonging to another ACTIVE
      record (`resume-34-cai2-2-20260925` names a branch that no longer exists, and it and this record both
      claim two `src/` paths this session legitimately touched in `b7f3a3ed2`). A byte-exact HEAD control
      shows the identical DRIFT(3) without this change.
      Population: 44 -> **43** tracked `.ps1`/`.bat`/`.cmd`, re-measured with
      `git ls-files | Select-String '\.(ps1|bat|cmd)$'` after the deletion (41 `scripts/` including 3
      `gk-core/scripts/lib/`, 1 `.claude/cmdc-agents/scripts/`, 1 `tasks/reports/`).

- [x] **3.5ap** `game-lock.ps1` (116 lines) — a file lock, so NOT a live/probe tool and no live run is
      required; its one PowerShell consumer (`restart-game.ps1`) is repointed here and that script's own
      live run belongs to its own port.
      **A DIFFERENTIAL, TAKEN WHILE THE `.ps1` STILL EXISTED**: 15 cases, 12 reaching a real state, **0
      disagreements** on the verdict and on the lock file's presence afterwards. Three cells diverge ON
      PURPOSE and are labelled: the original returns exit **1** for BOTH "another live session holds this"
      and "you passed the wrong arguments", so requiring agreement there would require reproducing a
      defect.
      **WHY IT WAS RETIRED, all measured on the original.** An unparseable lock file **CRASHED** the tool:
      `ConvertFrom-Json` on a partially-written file throws and `$ErrorActionPreference = 'Stop'` made it
      an unhandled error with no verdict. The window is real, not theoretical — `--acquire` creates the
      file with `CreateNew` and writes the body afterwards, so a concurrent reader between the two reads an
      EMPTY file. The port refuses with `LOCK-EMPTY` and exits 3, **FAILING CLOSED**, because treating an
      unreadable lock as FREE is how two sessions end up sharing one game install. The same crash existed
      one level down for the session record, with no diagnostic naming which file had failed to parse.
      The record path was built with a **HARDCODED BACKSLASH**, `tasks\sessions\`: on any non-Windows
      checkout that is a path with a literal backslash, the record never resolves, EVERY lock reads STALE,
      and `--acquire` steals a live install. And two exit codes where four are needed — a deploy reporting
      "someone else is probing this install" for a typo sends the operator after a lock that does not exist.
      Contract suite: **35 tests**, including `--acquire` atomicity asserted by racing **FOUR processes** at
      one install and requiring exactly one winner. The differential found a real gap in the port: a stale
      takeover reported **nothing**, so a takeover and a fresh acquire were indistinguishable in the log
      and in `--json`; it now carries a `notes` entry naming whose lock it took.
      **THE DIFFERENTIAL REPORTED FOUR DISAGREEMENTS THAT WERE MY HARNESS'S.** The classifier read the
      FIRST match in the whole output while both tools print the outcome **LAST** — so "taking over a stale
      lock: ..." followed by "me holds <dir>" classified as STALE — "is free" was missing from a priority
      list I had rewritten, and the port's own verdict token bypassed the canonicalisation the prose went
      through. Fixed by scanning per line and taking the last classified one. **The sixth probe-blindness
      of this program, and the same rule every time: a probe that cannot distinguish two states must say
      PROBE-BLIND rather than report a difference.**
      **THE EXEMPTION HAD TO BE CORRECTED, NOT EXTENDED.** It carried `scripts/game-lock.ps1` on the stated
      ground that this tooling has "no deterministic repository test target" — a ground that stopped being
      true the moment this port landed 35 tests, and an exemption whose REASON is false is worse than none
      because it reads as a considered decision and is neither. So `scripts/game-lock.*` stays exempt as a
      GLOB (the deleted file stays mappable through `--deleted-paths`, **measured**) and the ported tool
      gets a real `game-lock-tool` owner row in `tools-audit-tests`, so editing it RUNS its suite.
      **AND THAT EDIT DESTROYED 19 EXEMPTIONS BEFORE I CAUGHT IT.** My first coupling script wrote
      `row["paths"] = [<two items>]`, which REPLACES the list rather than editing it, silently dropping
      `gk-fusion/scripts/deploy-play.py`, `scripts/restart-game.ps1` and 17 others. **Nothing objected**: the registry
      guard still answered OK, because fewer exemptions is not a violation it checks. The only thing that
      caught it was `verify-change.py` refusing with `BOUNDARY-MISSING` on a path I had just edited.
      Restored byte-exact from HEAD with the intended change expressed as a set difference, and the row
      re-read afterwards to prove the count went 19 -> 19 and not 19 -> 1. **An assignment that shrinks a
      20-entry list to 2 is not a typo, it is a destruction with a green light.**
      Scoped verification: **35 pytest passed** and two Guard focused checks (20 and 66 tests), exit 0.
      Population: 43 -> **42** tracked `.ps1`/`.bat`/`.cmd`, re-measured with
      `git ls-files | Select-String '\.(ps1|bat|cmd)$'` after the deletion.

- [x] **3.5aq** `scripts/checks/web-fusion-rpg-web.ps1` (30 lines) — the LAST `.ps1` among the
      seventeen `gk-core/scripts/checks/*` wrappers. Sixteen already carried the `common.py` shape, so this
      COMPLETED a migration rather than starting one, and the shared runner grew to meet it.
      **IT IS A SEQUENCE, AND THAT IS WHY `common.py` GREW.** The original ran `npm test` then
      `npm run build` and said why: "the order that fails fastest". The build is the slower half and its
      `tsc --noEmit` is the half a bare vitest run does NOT do, because vitest transpiles without
      type-checking. `spec_from` gained an ordered `CHECKS` alongside `CHECK`, and a wrapper must declare
      **EXACTLY ONE** of the two — a wrapper declaring both is ambiguous, and resolving that silently
      would pick one at random. All sixteen existing wrappers declare `CHECK`, and a case now loads
      EVERY wrapper in the directory, so the extension cannot quietly break one.
      **THE PORT EXPOSED A REAL LATENT BUG IN THE SHARED RUNNER, LIVE ON THIS PLATFORM:**
      `shutil.which("npm")` returns `npm.CMD` (so the preflight PASSES) and
      `subprocess.run(["npm", "--version"])` then raises `FileNotFoundError` (so the RUN cannot start).
      `npm`, `npx`, `yarn` and `pnpm` are all `.cmd` batch shims on Windows and `CreateProcess` will not
      execute one without its extension in argv[0]. Sixteen wrappers never hit it because none uses npm;
      this one would have refused with `COMMAND-NOT-FOUND` on a tool that is demonstrably installed —
      **the worst kind of red, one that looks like a broken check and is really a broken launcher.**
      `resolve_executable` now resolves the declared token ONCE and the RUN uses the resolved path, while
      the REPORT still says the declared token, because `npm test` is what a reader retype and what the
      CI parity test compares.
      Also: a missing `node_modules` was a bare `throw` with no exit code of its own, now the named
      `REQUIRED-PATH-MISSING` refusal; and a failing command's own code is carried as `command_exit`
      rather than propagated, because **64 is this module's REFUSED** and a command exiting 64 would
      otherwise masquerade as a refusal the wrapper never made.
      **THE DIFFERENTIAL IS WEAKER THAN THE game-lock ONE, FOR A MECHANICAL REASON.** The retired script
      computes its own root from `$PSScriptRoot` and builds its command inline, so it cannot be pointed
      elsewhere or have its command substituted; driving the oracle for real costs minutes per case and
      its own result is the subject. So the harness asserts the ORDER against the original's own source
      text, drives for real only what it can, and **LISTS what it cannot reach** rather than implying it
      did (a non-zero exit from either npm, the vitest output text, whether `Push-Location`/`Pop-Location`
      were balanced, the wall-clock duration).
      **AND THAT HARNESS MISLED ME ONCE — THE SEVENTH PROBE-BLINDNESS OF THIS PROGRAM.** Its "real tree"
      case planted a temp directory holding only `web/fusion-rpg-web/node_modules`, and I read the port's
      `exit=1` as the port being red, when `npm test` in a directory with no `package.json`, no vite
      config and no sources is SUPPOSED to fail. Fixed by pointing the case at the real repo root, where
      the port runs `npm test` (0) then `npm run build` (0) and the original had also exited 0.
      **A fixture whose name contradicts what it sets up teaches the wrong lesson in both directions.**
      Contract suite: **36 tests**. Falsification: first run **11 killed / 3 SURVIVED**, all three real
      suite holes, now closed. (a) The shared-timeout case asserted `all(budget <= 60)`, which a mutant
      handing the FULL budget to every step also satisfies — it now asserts the RELATIONSHIP (each budget
      falls by exactly the elapsed clock) with the clock mocked, plus a case that the timeout reason
      names the budget the step actually got rather than the caller's total. (b) The shim case asserted
      the RESOLVER but not the RUN, so dropping the resolution inside `run` was invisible — it now
      captures the spawned argv and asserts both that argv[0] carries an extension and that the arguments
      are forwarded unchanged, alongside the report still naming `npm test`. (c) The missing-toolchain
      case did not exist, so a `toolchain` returning the token unchecked was unkillable — it now refuses
      BY NAME and spawns nothing, with a **counterweight** case so it cannot be satisfied by refusing
      everything. Second run: **14/14 killed, 0 survived, 0 could not be applied.**
      Couplings: `projects["web-fusion-rpg-web"]["script"]` — the dispatch the verification plane uses to
      RUN this check — now names the `.py`, and a new `web-check-wrapper-tool` owner row carries the
      wrapper and its suite. Reachability measured: both select that row and its pytest target, and the
      DELETED `.ps1` still maps. **The coupling script asserts the boundary COUNT before and after**,
      because the game-lock port's coupling destroyed 19 exemptions with a whole-list replacement that
      nothing objected to.
      Scoped verification: **36 pytest passed**, Guard module **717 passed / 3 failed**, and a byte-exact
      HEAD control reverting both changed files reproduces all three (`LawnCoordsGuardTests` x1,
      `ClassSystemBaselineRegenTests` x2). PRE-EXISTING, proven by the control.
      Population: 42 -> **41** tracked `.ps1`/`.bat`/`.cmd`.

- [x] **3.5ar** `scripts/first-session-progression-harness.ps1` (retired 2026-09-29) ->
      `gk-core/scripts/first_session_progression_harness.py`
      — committed as `1163b5ff4`. This entry was MISSING: the port landed and was verified, but nothing
      recorded its evidence, which is the failure mode the ledger exists to prevent.
      **THE DIFFERENTIAL WAS DRIVEN FOR REAL, AND THE TRICK IS WORTH RECORDING ON ITS OWN.** To make the
      retired script's own behaviour observable, a `.cmd` recorder was placed **on `PATH` shadowing
      `dotnet`**. That works because the original resolves its commands through `PATH`, so it invoked the
      recorder exactly as a caller would — not because the harness inspected the script's text. The
      same recorder then observed the port. Contrast with the web wrapper (3.5aq), which could not be
      substituted because it resolves its own root from `$PSScriptRoot` and builds its command inline;
      there the harness asserts ORDER against the source and **lists what it cannot reach** instead of
      implying it did.
      Contract suite: **31 tests**. Falsification: **15/15 killed, 0 survived.** M7 was **WITHDRAWN as an
      equivalent alternative** rather than counted as a kill — a different spelling that computes the
      same result is not evidence the suite is strong, and counting it would inflate the number.
      Couplings: a `first-session-harness-tool` owner row, and the retired `.ps1` converted to a glob in
      the operational exemption so the deletion stays mappable through `--deleted-paths`.
      Population: 41 -> **40** tracked `.ps1`/`.bat`/`.cmd`, measured from `git ls-tree` at `1163b5ff4`
      and its parent — **not** carried forward from the previous entry's figure.
- [x] **3.5as** `scripts/dump-melon-p0.ps1` (72 lines, retired 2026-09-29) +
      `scripts/dump-game-profile.ps1` (14 lines, retired 2026-09-29) ->
      `gk-core/scripts/dump_melon_p0.py` + `gk-core/scripts/dump_game_profile.py` — committed as `c3da6ffc0`. Two files
      retire as ONE change, because the second was a pure alias: it resolved the same two directories,
      called the other script, and printed a hint naming a different documentation surface.
      **THE HEADLINE DEFECT IS A SILENT GREEN.** The original ran `dotnet build -v q | Out-Null` and two
      `dotnet run`s, read `$LASTEXITCODE` for **none** of them, and ended with `Pop-Location` plus a
      `Write-Host` — so a failed build and a failed reflection both exited **0**. The tool whose entire
      job is to say whether two assemblies agree had no way to say they did not. Also: the build's
      output was discarded for the step most likely to fail; the scratch directory had a FIXED name
      (`$env:TEMP/fusionrpg-p0-dump`) that every caller shared and overwrote with `Set-Content`, so two
      overlapping runs could reflect over each other's payload; neither `dotnet` call was bounded; and
      the payload computed its parameter-type list and never printed it.
      **THE PROOF IS A REAL RUN, NOT A MOCK.** A purpose-built `Assembly-CSharp.dll` declaring `Plant`,
      `Zombie`, `Board` and `CreateZombie` with `TakeDamage`/`SetZombie*` methods was planted at both
      real install paths, and the tool was run end to end through BOTH entry points: **23 assertions, 0
      failed** — a genuine `dotnet build`, real reflection, the per-run scratch removed, the Melon-only
      case reported as a RESULT rather than a refusal, and the profile hint pointing at the profile docs
      and NOT at the P0 memo. Differential against the original, both driven for real over ONE shared
      fixture assembly: **0 disagreements** across every type header and census line. The exit code is
      deliberately **not** required to match: the original's `0` is not evidence that anything ran, so
      requiring agreement would require the port to reproduce a silent green.
      Contract suite: **43 tests**. Falsification: **30 mutants — 27 killed, 3 classified equivalent, 0
      could-not-apply, 0 collection errors.** Four mutants target the SUITE, not the tool.
      **THE SUITE HAD TWO REAL DEFECTS, BOTH FOUND BY MEASURING THE PROJECT INSTEAD OF THE SUITE.** Its
      first version patched `dm.subprocess` / `dm.shutil` / `dm.tempfile` — and those ARE the
      process-wide modules — so **506 unrelated failures** appeared in `test_ps1_port_census.py`, whose
      sandbox calls `subprocess.run(["git","init"], check=True)` and so silently never created its
      throwaway repo. The first symptom visible from INSIDE the suite was a case of mine reading the
      stub's literal `'stdout'` and reporting that `--ml-game-dir` was "not found in it". Separately, the
      stub context manager was not re-entrant, and the common shape `with dotnet_stub() as stub:
      self.run_tool(stub)` entered it twice, so a second patch pair was started whose "original" was
      already a mock — **35 cases failed and the tool was innocent.** Both are now impossible by
      construction: every global is bound to a module-private seam (`_RUN`, `_WHICH`, `_RMTREE`,
      `_MKTEMPT`) and the stub is depth-counted. Each has a regression mutant aimed at the suite.
      **THE FALSIFICATION HARNESS MUST RUN UNDER PYTEST, NOT UNITTEST, AND THAT WAS MEASURED.** pytest
      runs methods in DEFINITION order and `unittest` runs them ALPHABETICALLY, so the non-reentrant-stub
      mutant **survived every `unittest` run and was KILLED under pytest** — which is the runner
      `verification-boundaries.v1.json` names for this project. A harness that runs the other runner
      reports a suite as adequate for an ordering it will never see.
      **A MUTANT THAT REWRITES AN ASSERTION INTO A TAUTOLOGY IS `REDUNDANT-ASSERTION`, NOT A HOLE.** It
      cannot be killed by the case it edits — that case still passes, and it should. What it would break
      is detecting a seam that was never bound to the real function, and the sibling provenance
      assertion (`__module__ == "shutil"`) still proves that, so the mutant removes a safety net rather
      than a capability. Claiming it as a hole would overstate the suite; counting it as a kill would
      overstate the result.
      Couplings: a `dump-melon-p0-tool` owner row with **FOUR** path entries, because a `.ps1` -> `.py`
      rename is a HYPHEN becoming an UNDERSCORE and a registry wildcard is confined to the final segment
      — `scripts/dump-melon-p0.*` matches the retired file and **not** the new one. Writing the glob's
      stem with the new file's underscore produced a stale exact path and the integrity guard named it,
      which is exactly what it is for. The retired exemption paths became globs.
      **THE FIRST COUPLING INVARIANT WAS WRONG AND THE TOOL CAUGHT IT.** It asserted the exemption row's
      LENGTH was unchanged, which is false: two exact paths become two globs and two `.py` paths are
      added, so the length legitimately GROWS. The gate fired and blocked the write. Replaced with the
      invariant that would actually have caught the 19-exemption loss: the ONLY removals are the two the
      port replaced, every other row is byte-identical, and the row's stated reason is unchanged.
      **`session-boundary` DRIFT(3) is PRE-EXISTING, proven by a byte-exact HEAD control** that restores
      the record, reproduces the identical three complaints, and restores the edited record in a
      `finally` — none of the three mentions a path this port added.
      Scoped verification: **43 pytest passed, both guard focused checks pass, exit 0**, and the plan
      maps all seven paths — including BOTH deleted `.ps1` — to the new owner row.
      Population: 40 -> **38** tracked `.ps1`/`.bat`/`.cmd`, re-measured from `git ls-files` immediately
      before the deletion and again after it.

- [x] **3.5at** `scripts/probe-sim-shield.ps1` (26 lines, retired 2026-09-29) ->
      `gk-core/scripts/probe_sim_shield.py` —
      committed as `8e2858f9b`. **THE PROBE COULD NOT FAIL.** Its own comment says "expect
      shieldAbsorbed 50, hp 300 -> 270" and nothing anywhere checked it; both event pipelines were
      `(...).events | Where-Object kind -eq "shield.granted" | Select-Object -Expand payload |
      Format-List`, so an ABSENT event produced NO output and the script continued to exit 0. A probe
      whose whole purpose is to show a shield absorbing what it should, reporting success when it
      absorbed nothing, is worse than no probe -- it is a green light on the bug it exists to catch.
      The port makes the expectations CODE: seven are named, reported pass or fail, and one failure is a
      non-zero exit naming which. Three traps in the real contract are handled explicitly, each found by
      reading `SimEngine` rather than by guessing: `GrantShield` reports the shield as `hp`/`maxHp`
      totals and **not** as an `amount` key; `shieldAbsorbed` is added only
      `if (applied.AbsorbedAmount > 0)`, so an ABSENT key means the pipeline did not run and must not be
      read as zero; and `DamagePlant` emits `plant.damage` only `if (stats.LogDamage)`, so the whole
      step can vanish without error.
      Also: no timeout on any of the four requests, and a hardcoded `http://127.0.0.1:5088` -- the
      OWNER's server. The port is read from `--base-url`, then `FUSIONRPG_SIM_PROBE_URL`, then
      `FUSIONRPG_URLS` (what the SERVER itself reads, so a pooled slot points here correctly), then the
      owner's default, which is labelled as a fallback and not as the server.
      **A REAL RUN OVER A REAL SOCKET, because this tier needs a SERVER and not a game:** a real
      `http.server` speaking the payloads `SimEngine` really produces, one server per scenario, **9
      assertions, 0 failures**. Differential against the original, both driven for real over the SAME
      server: **0 unexpected disagreements** -- on all five misbehaving scenarios the original exits 0 and
      the port exits 1 naming the failed expectations, and that divergence is the point of the port
      rather than something required to disappear.
      Contract suite: **33 cases**. Falsification: **22 mutants -- 20 killed, 2 classified equivalent, 0
      could-not-apply, 0 collection errors.** Falsification found **FOUR REAL HOLES in the suite**: a
      partial absorb, an empty shield table, an HTTP error and a non-JSON body were each undriven, so a
      check rewritten to `True` satisfied the whole suite. All four are cases now. The partial-absorb hole
      is the instructive one -- the case for an ABSENT key existed and passed, so a check rewritten as
      `bool(payload.get(...))`, which accepts any non-zero amount, was invisible.
      Couplings: a `probe-sim-shield-tool` owner row, and the retired path converted to a glob in
      `live-diagnostic-scripts` -- **located by CONTENT, not by a remembered id**, because the first
      attempt hardcoded `local-operational-scripts`, the script refused, and the path turned out to live
      in `live-diagnostic-scripts`. Population: 38 -> **37**.
- [x] **3.5au** `scripts/gate-class-system-phase9.ps1` (62 lines, retired 2026-09-29) ->
      `gk-core/scripts/gate_class_system_phase9.py` — committed as `7efe8bbf1`. **THE GATE THAT STOPS A HUMAN
      EYEBALLING READINESS COULD PASS ON A FILE THAT NEVER ANSWERED.** The verdict was
      `$census.families_without_reader -gt 0`; in PowerShell a missing property is `$null`, `$null -gt 0`
      is `$false`, and the negation of `$false` is `$true` — so a census JSON that was truncated, that
      renamed the field, or that was a **different tool's** output entirely printed
      `PHASE 9 READINESS GATE: READY` and exited 0. The port makes a census that does not answer every
      question a named refusal: six fields required and type-checked, `bool` rejected where a count
      belongs, and a count that disagrees with the list of names it claims refused as a different run's
      data, which is what a stale file looks like. Six cases drive the malformed shapes, each built by
      REMOVING or REPLACING one field of a well-formed census, so a fixture cannot agree with a broken
      tool.
      Also: a missing fixture and a real gap shared exit code 1, so a caller could not tell a typo from
      an honest NOT-READY — they are **64 and 1** now. Neither `python` invocation was bounded.
      `$Root` defaulted to a `Resolve-Path` evaluated at PARSE time, so a bad default failed before the
      body ran and named nothing.
      **A TEST DEFECT OF EXACTLY THE SHAPE THIS PROGRAM KEEPS MEETING, AND IT PASSED FOR THE WRONG
      REASON.** The suite's fixture writer signalled "raw text" with `isinstance(census, str)`, which
      conflates a raw string with a string VALUE. So the case for the JSON value `"a string"` wrote the
      file `a string` — invalid JSON — and the tool refused with `CENSUS-NOT-JSON` instead of
      `CENSUS-NOT-AN-OBJECT`. The case passed, and **would have kept passing if the tool stopped
      type-checking entirely.** It now uses a `Raw` wrapper.
      `ClassSystemPhase9ReadinessGateTests` now drives the `.py`: **5/5 pass**, including the real-tree
      NOT-READY case naming `resource.efficiency`. Its non-wiring assertion checks **BOTH** spellings —
      the retired hyphenated form and the ported underscored one — because a check for one leaves the
      other free to be wired in.
      Contract suite: **28 cases**. Falsification: **17 mutants — 15 killed, 1 classified equivalent, 0
      could-not-apply, 0 collection errors.** The headline mutants are all of the shape "the validation
      was removed", because that is the defect.
      Couplings: a `gate-class-system-phase9-tool` owner row naming the tool, the pytest suite **and the
      C# consumer**, and the retired path converted to a glob. Population: 37 -> **36**.

- [x] **3.5aw** `scripts/lib/KeepverseRoots.ps1` (52 lines, retired 2026-09-29) — committed as
      `a8b93fca8`. **A DELETION, NOT A PORT**: `bdb2a9a10` shipped "one content/core/workspace root
      resolver per language" and `gk-core/scripts/lib/keepverse_roots.py` landed with it as the LIVE
      implementation. Nothing consumed the PowerShell form — its only reference was its own usage
      comment.
      **THE DELETION IS PROVED, NOT ASSERTED.** A differential drives BOTH over PLANTED trees: a legacy
      repo, a workspace with the default pack, a workspace with `KEEPVERSE_PACK` set, a workspace whose
      pack is MISSING, and a tree with nothing to resolve — **15 comparisons, 0 disagreements**,
      including the three where BOTH must fail. A difference in failure text is not a disagreement; what
      must agree is WHETHER each failed, because the contract is "a root is never guessed".
      **THE GAP THE DELETION EXPOSED, AND THE REASON IT IS NOT JUST A DELETION: the live Python module
      had NO owner row and NO contract test of its own.** Its only coverage was
      `gk-core/tests/Shared/KeepverseRoots.cs`'s twin, which tests a DIFFERENT file — so "the C# twin covers the
      contract" was never the same claim as "this file is covered", and an edit to `keepverse_roots.py`
      selected no verification at all. This change adds a `keepverse-roots-tool` owner row and 21 cases.
      Falsification: **15/15 killed, 0 survived.** It found **THREE REAL HOLES**, all cases that could
      not discriminate: (a) every case started at a `deep/deeper` beneath the layout, so a walk that
      skipped the START directory itself still found the layout two levels up and ALL of them passed —
      two cases now start AT the layout root, which is the shape a checkout-root caller has, and the one
      case where a walk beginning one level too high resolves the PARENT (here the drive root);
      (b) the "nearest layout wins" case nested a WORKSPACE inside a LEGACY repo, so no walk-order mutant
      could break it — the nearest was the workspace either way — and the discriminating shape is the
      other way round; (c) nothing tested that `FusionRpg.slnx` must be a FILE, so an `.exists()` check
      was unkillable.
      **A FIXTURE DEFECT FOR THE THIRD TIME IN THIS PROGRAM, AND IT PASSED FOR THE WRONG REASON:**
      `Tree`'s own default was `pack="fusion"`, so naming a tree `workspace-no-pack` and leaving the
      default alone BUILT a tree that did have a pack. Population: 36 -> **35**.

- [x] **3.5ax** `scripts/test-substrate-leak-alarm.ps1` (118 lines, retired 2026-09-29) — committed as
      `f9b56b330`. A DETECTOR, so its contract is asymmetric: reporting OK is easy and means little,
      while reporting a leak when there is none — or reporting OK when it could not look — is the failure
      that matters. Proved by the alarm wrapped around a REAL process that really leaks: **9 assertions,
      0 failures**, the leaking command being a real program that creates and abandons a directory.
      **AN UNREADABLE SNAPSHOT ROOT READ AS "NO LEAK".** Both snapshots were
      `Get-ChildItem ... -ErrorAction SilentlyContinue`, so an inaccessible or missing temp root produced
      an EMPTY set, the set difference was empty, and the alarm reported OK having observed nothing. Both
      now REFUSE and name the path. The private temp root's own delete was likewise swallowed
      (`-ErrorAction SilentlyContinue`), which this repository's testing standard names as the cause of
      a 65.5 GB leak; it is now a refusal, and a root holding a survivor is KEPT, because deleting it
      would erase the evidence and then the evidence.
      `[scriptblock]$Run` becomes `--run` ARGV. **The obvious defect to claim — that the verdict read
      `$LASTEXITCODE`, so a scriptblock whose first command failed and whose last succeeded would report
      clean — WAS MEASURED AND DID NOT REPRODUCE.** The original exits 1 for `{ exit 3; exit 0 }`. The
      claim is WITHDRAWN rather than shipped, and on all five leak scenarios the two implementations
      AGREE, exit code for exit code.
      **TWO HARNESSES OF MINE REPORTED CONTRADICTORY THINGS BEFORE THIS SETTLED, AND BOTH ARE WORTH
      NAMING.** The first differential passed `-Run { ... }` through `pwsh -File` as an argv element; the
      original answered "Cannot process argument transformation on parameter 'Run'", never ran the
      wrapped command, leaked nothing, and printed OK on every scenario — an artifact of a driver that
      reads exactly like a finding about the tool. The harness now writes a real `.ps1` driver and
      ASSERTS the child actually ran before comparing anything. The second differential cleaned only the
      temp root between the two halves, so the PS half's sqlite survivor was in the PORT's
      before-snapshot and the port reported OK while the original correctly reported FAILED — my harness
      leaking state, reading as a defect in the port.
      **BOTH CI CALLERS MOVE IN THIS CHANGE, the first port with external callers**:
      `.github/workflows/ci.yml:383` and `nightly.yml:69`. A workflow still calling the retired file
      parses, runs, and fails only where PowerShell is absent — which is not this machine, so it would
      read SILENTLY GREEN here. The `$LASTEXITCODE` guards are kept; replacing them would be a behaviour
      change dressed as a port.
      Falsification: **21 mutants, 20 killed, 0 survived.** It found **THREE REAL HOLES**, all cases
      that could not discriminate: an unlistable root (driven by making `iterdir` raise, since a real
      unlistable directory is not portable to arrange); a pre-existing dir ALONGSIDE a new one (alone,
      before == after, so a count check also passes); and the TEMP/TMP restore case, which read
      `os.environ` after `patch.dict` had already restored it — **so the case's own scaffolding supplied
      the property it claimed to test**, and a mutant that deleted the tool's restore entirely survived
      it. 33 contract cases. Population: 35 -> **34**.

- [x] **3.5ay** `tasks/reports/f13-schema-upgrade-proof.ps1` (177 lines, retired 2026-09-29) — committed
      as `d75e1e8ef`. A PROOF, and it is proved against the real thing rather than a fixture: the
      owner's actual `dist/FusionRpg.Server/data/rpg-hot.sqlite`, **521 MB**, online-backed-up with
      SQLite's BACKUP API, then handed to a real `dotnet run` of head code. **Two real runs, and the
      first is the interesting one.** (A) The live database AS-IS was MIGRATED by a server boot and
      already carries `dungeon_domain.first_clear_ref`, so the proof is meaningless: the tool reports
      FAILED, exits 1, and names the precondition — a proof that cannot tell an upgrade from a no-op
      proves nothing. (B) The same database with the one added column REMOVED, so the upgrade path is
      observable: the pre-fix failure is reproduced (`no such column: first_clear_ref`), then `Init()`
      fixes it, and `GetRpgActor(1,plant,1) -> level 3` and `GetRpgProgressionSummary(1) -> player 1`
      read real data back. Differential against the original, both driven over the same source:
      **0 problems** — both exit 1 on the already-migrated database and both prove the upgrade on one
      shared pre-fix copy.
      **The cleanup ran in a `finally` with no guard, and a throw from a `finally` REPLACES the verdict.**
      `Remove-Item -Recurse -Force` under `$ErrorActionPreference = 'Stop'` throws when the directory is
      held open — which on Windows is what a just-exited `dotnet` child does — so a proof that had
      already printed `PROOF OK` could exit non-zero because a temp directory would not delete. The
      verdict is now computed BEFORE the cleanup and a failed delete is REPORTED, not raised. Also: no
      timeout on `dotnet run` over 521 MB; a plain-file-copy fallback on ANY backup error, including one a
      plain copy would also hit, so a corrupt source produced a probe running against a torn file;
      `Resolve-Path -ErrorAction SilentlyContinue` on the source; and no machine-readable verdict.
      **TWO DEFECTS IN MY OWN PORT, both found rather than shipped.** The after-check searched the WHOLE
      probe output for `first_clear_ref present=True`, so when the probe bailed at the precondition it
      matched the BEFORE line and reported OK for a state never observed — now read per line. And a
      non-zero probe exit was reported as a REFUSAL, which says "I could not run" when the proof ran and
      returned its verdict; it is now FAILED with the checks read from the probe's own output.
      Falsification then found a **DEAD clause** — `not probe_timed_out` inside `ok`, unreachable
      because a timeout is already a refusal — which is removed, and a case that had asserted on a guard
      that guard could never append is rewritten to assert the property that actually holds it. Four more
      real holes: a substring line-reader that would match the probe's own `FAIL: first_clear_ref still
      absent after Init`; `ok` ignoring the named checks (every failing fixture also failed on the exit
      code, so nothing distinguished them); the probe never asserted to receive the COPY rather than the
      source; and the cleanup path unasserted. **19/19 mutants killed, 0 survived**, 30 cases.
      **THE FILE WAS IN NO EXEMPTION ROW AT ALL.** A pre-existing mapping gap: it existed and neither
      registry named it, so the guard suite had no opinion about it in either direction and its removal
      could not have been caught by anything. A dedicated row is created rather than folded into an
      unrelated one, and its reason says the gap was CLOSED rather than inherited — a row whose reason
      implies coverage it never had is a second version of the same silence. Population: 34 -> **33**.

- [x] **3.5az** `scripts/smoke-player-pack.ps1` (161 lines, retired 2026-09-29) — committed as
      `1597271ad`. Proved by a REAL run against the real unpacked pack at `dist/FusionRpg`, with the
      PACKAGED SERVER BOOTED ON EACH SIDE: the differential reports **0 disagreements** across the
      verdict, the probe exit code, the server step, all six probe step names with their ok-ness, and the
      exact `contentSource` value. Both sides leave 0 stray processes. **The pack is currently missing its
      content tree, so both tools report FAILED and name the same reason** — a real finding ABOUT the
      pack, not a defect in the port: a smoke test that cannot fail proves nothing.
      **A MALFORMED PROBE OUTPUT READ AS A PASS:** `$probeJson | ConvertFrom-Json` sat in
      `try { } catch { $probeObj = @{ ok = ($probeExit -eq 0) } }`, so a build banner on stdout made a
      probe that proved nothing and exited 0 a recorded PASS with an empty step list. **BOTH DELETES WERE
      SWALLOWED** — the `finally` wrapped the process-tree kill and the data-directory removal in nested
      `try { } catch { }`, the shape this repository's testing standard names as the cause of a 65.5 GB
      temp leak. Neither `dotnet` call was bounded, and `Get-Random` picked the port, so a collision
      surfaced as a health timeout against somebody else's server.
      **THE FILE WAS IN NO EXEMPTION ROW AT ALL** — the second such tool this session — and the registry
      guard then caught a coupling the first attempt missed: the pre-existing `player-pack-packaging`
      BOUNDARY row also named the exact `.ps1`, so deleting the file left a stale path and
      `verify-change` refused to plan. That row owned exactly the one retired file, is subsumed, and its
      glob moved to the new row, which carries the real suite; two owner rows may not share a pattern.
      Falsification: **17 mutants, 16 killed, 0 survived.** It found **THREE REAL GAPS** — the probe's own
      `ok: false` was never driven separately from the exit code, `/api/test/snapshot` was only ever HTML
      so the third property's check was unkillable, and `_stop_tree` was never driven. 35 cases. Four of
      my own suite defects are named in the commit: a suite that read scratch files after their
      `TemporaryDirectory` had deleted them, `"DominanceBaseline" in cmd` where `cmd` is a list of
      arguments (so `in` is EXACT MEMBERSHIP, not substring), and a helper with two jobs that did neither.
      Population: 34 -> **33**.

- [x] **3.5ba** `scripts/regen-class-system-baselines.ps1` (203 lines, retired 2026-09-29) — committed as
      `7dbbd0eb3`, with the last two server-only files. Proved by a real run of BOTH tools against this
      repository, each invoking the same three simulators on the live `aptitudes.v10.json` with the same
      fixed seeds: **all three emitted baselines are BYTE-IDENTICAL** after normalising line endings and
      `_meta.measuredAt`, key order included. 0 disagreements.
      **THE SCRATCH DIRECTORY LEAKED INTO A TRACKED TREE.** The element-scratch copies were written under
      `$OutDir` — by default the TRACKED `docs/research/class-system` — and removed by a bare
      `Remove-Item` placed AFTER the simulator call, not in a `finally`, so a non-zero exit left scratch
      in a committed directory. The scratch is now a private temp directory.
      **THE PROSE IS CONTENT, AND THE FIRST TRANSCRIPTION "CLEANED UP" THREE QUIRKS THAT THE
      DIFFERENTIAL CAUGHT ALL THREE OF.** `chains` NOT `` `chains` ``, because PowerShell drops the
      backtick from an UNRECOGNISED escape and a note written to read as markdown code was committed with
      no code marks at all; `dominanceMatrix/ dominantCorners` WITH A SPACE, a line-wrap artifact; and
      `"neutral"` IN DOUBLE QUOTES, where the escaped quotes ARE recognised and survived while the bare
      backticks did not. All three are reproduced byte-for-byte, because these strings are content a
      committed baseline diffs against. The float spelling is matched too (`E-06` not `e-06`), applied to
      the encoder's OWN float chunks: there are three chunk shapes and an anchored pattern rewrote dict
      floats while silently skipping every list float.
      **THE ORIGINAL COULD NOT RUN AT ALL HERE.** `gk-forge/tools/DominanceBaseline` — which the regen invokes —
      threw "could not locate repo root" on every invocation, because four tools and one guard test walked
      up from their bin directory looking for `scripts/guard-class-system.ps1`, which no longer exists, as their
      repo-root marker.
      `Directory.Build.props`, the tracked MSBuild root file, which no tool migration can delete — the
      convention the two `FusionRpg.Core.ClassSystem.Tests` files beside them already used. The fifth
      site, `gk-core/tools/SquadHarness/TuningBootstrap.cs`, was found only because a search scoped to
      `tools/*/Program.cs` would have missed it. **Measured with a byte-exact HEAD control:
      `FusionRpg.SquadHarness.Tests` goes from 193 of 193 failing at HEAD to 60 of 193.** The remaining
      60 are an independent unconfigured-hub defect (`RungPolicy.Configure(...) has not run`) that the
      repo-root throw was MASKING; not fixed here, and reported rather than absorbed.
      Falsification: **32 mutants, 31 killed, 0 survived.** It found **TWO REAL SUITE GAPS** — the element
      mapping was compared against the module's own dict, so a mutant editing it satisfied the comparison;
      and nothing asserted the scratch was actually GONE, only that the flag was not False, so a mutant
      that skipped the delete left it None. It also found **THREE BROKEN MUTANTS OF MY OWN** that were
      no-ops, and **five wrong decoy fixtures** for the regex anchors, each of which was excluded by the
      GLOB before the pattern was consulted — the one shape that exercises the anchors is a double
      extension, which the glob admits. 48 cases. Population: 33 -> **31**.

- [x] **3.5bb** **THREE LIVE BREAKAGES FOUND AND REPAIRED, none of them mine and all of them the same
      defect** — a port that renamed a tool and left its callers behind. Found by a sweep for
      EXECUTABLE references to a `.ps1`/`.bat`/`.cmd` whose target is not a tracked file.
      **THE "NONE OF THEM MINE" CLAIM WAS OVERSTATED, and the correction is 3.5be.** This sweep found
      three and called all three other lanes' work. It was INCOMPLETE: a fourth caller of the same
      retired runner existed, `TestShardManifestTests.HT5_ci_runs_data_tests_through_the_sharded_runner`,
      and it was **mine** — I ported `test-sharded.ps1` and repaired two of its three callers and missed
      the third, so a guard sat red against a `ci.yml` that had been correct since my own port. It was
      found in 3.5be, by the path-owned verification of an unrelated port, not by this sweep. The lesson
      is not "be more careful": it is that **a sweep for dangling executable references has a recall
      that a prose claim about it silently overstates**, and the count three was a reading of what the
      sweep found, not of what existed.
      (1) `.github/workflows/ci.yml:329` ran `.\scripts\test-sharded.ps1`, ported to
      `gk-core/scripts/test_sharded.py`: **CI was invoking a file that does not exist.**
      (2) `WorkflowExitCheckTests.cs:21` still held that old prefix in its list of "lines that run tests",
      so the guard meant to catch exactly this **could no longer match a real workflow line**.
      (3) `gk-core/scripts/verify-change.py:989` launched the same deleted `.ps1` for EVERY sharded-project check,
      so the verification tool this program depends on could not run the checks it selects. That is the
      defect `verify-change.py` already documents at line 321 — "resolving the FILE by dialect is not
      resolving the ARGUMENTS by dialect" — and the file had three more `.ps1` invocations of which only
      this one was breakage: the generic suffix branches at 225/870/909 prefer the `.py` and fall back, so
      they are dispatch.
      Committed as `1d21e7a12` and `477da5bd8`. Measured: the old prefix matches **0** of ci.yml's
      test-running lines and the new one matches the sharded step, whose `if ($LASTEXITCODE -ne 0) { throw }`
      still follows it. The repaired sharded branch was then run FOR REAL on
      `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs`: **4 shards, 1893 tests, no overlap, exit 0.**
      **TWO CASES ADDED FOR IT, AND BOTH ARE KILLED BY THE OLD CODE** — the existing sharded case
      asserted only the PLAN line, and a plan is printed before any process starts, so it stayed green
      while the branch could not run at all. A test that checks only the plan cannot see whether the plan
      works. A missing runner is now a named `TOOL-MISSING` refusal. **The first falsification attempt
      was WORTHLESS AND IS RECORDED AS SUCH**: it put the mutant in a temp file, but `run_tool` invokes
      the module-level TOOL constant — the real script — so the mutant never ran and reported "0 fail" for
      the wrong reason. A falsification that does not substitute the mutant reads as evidence.

- [x] **3.5bd** **THE LIVE-SLOT BLOCKER IS LIFTED. IT WAS NEVER EXTERNAL.**
      This entry exists because the program's own record carried a wrong conclusion, and a wrong
      conclusion left in the ledger is the same defect as a stale citation left in a doc.
      **MEASURED:** the pool is at `H:\Games\.fusionrpg-pool`; `slots.json` records `maxSlots: 3` with
      slots 1, 2 and 3 all `state: "ready"`, `session: null`, cloned and verified on 2026-09-26, on ports
      5101/5102/5103. With `FUSIONRPG_GAME_POOL` set, `scripts/live-slot.ps1 -Status` prints
      "free 3" and exits 0. A legal BepInEx install exists at `H:\Games\PVZ-Fusion-3.9_BepInEx` for
      `FUSIONRPG_GAME_SOURCE`.
      **WHAT WENT WRONG, precisely:** the previous check read `FUSIONRPG_GAME_POOL` and
      `FUSIONRPG_GAME_SOURCE` from the tool shell, found both empty, and concluded the tier was
      unreachable — without ever LOOKING for the pool on disk. The two variables were unset in the shell;
      the pool was there the whole time. A check that confirms a condition nobody was waiting on is not
      evidence, and I treated it as one for a full turn. **Note the operational consequence: the
      variables do not survive between tool calls, so every live command must set them inline.**
      **TWO CLASSIFIERS ALSO LIED, IN OPPOSITE DIRECTIONS, AND NEITHER IS USED FOR THE SPLIT.** A keyword
      classifier put `prove-hub-combat.ps1` in the live tier because its text contains "hub", "lawn" and
      "combat" — its own header says "No live game, no live server -- drives gk-forge/tools/ProveHubCombat, a small
      console tool over RpgStore.InMemory()". A header classifier then put the SAME file in the live tier
      because the phrase it matched WAS "No live game": the negation matched and the negation was not
      checked. Tier is now read per file and used only for sequencing, because with the pool available
      both tiers are workable.
      **THE SPLIT, RE-MEASURED:** population **31**. Nothing is blocked for want of a slot any more.
      All 31 still need their own proof — a real live run for the live tier — and none of them is counted
      as done until it has one.



- [x] **3.5be** `scripts/prove-aptitude.ps1` -> `gk-core/scripts/prove_aptitude.py` (50 lines retired).
      **THE RETRY MASKED A REAL FAILURE, and this is the port's whole point.** The original ran
      `dotnet run --no-build` and, on ANY nonzero exit, ran `dotnet run` again WITH a build, then
      reported the SECOND attempt's exit code. Measured on this repository: the first attempt ran a
      STALE Debug binary and died with `could not locate repo root`, and the script reported SUCCESS
      because the rebuilt second attempt worked. A first run that fails for a real reason is therefore
      invisible and its diagnosis is lost. The port keys the build on the build OUTPUT being ABSENT --
      decided BEFORE the recipe runs -- so the recipe runs exactly once and its exit code is the run's
      exit code. Also retired: two unbounded `dotnet` calls, `Push-Location`/`Pop-Location` mutating
      the caller's process working directory, a missing tool surfacing as a bare `dotnet` message, and
      no machine-readable verdict of its own.
      **THE DIFFERENTIAL IS TAKEN OVER TWO CASES BECAUSE ONE PROVES NOTHING.** A. the default scope,
      `Might -> combat.power.omni`, which PASSES with a zero delta. B. `--channels ""`, every touched
      channel, which GENUINELY FAILS with a large non-zero delta -- the documented P3.1 gap (the battle
      composer's `ChannelMods` loop applies no cap). Measured against the real `gk-core/tools/ProveAptitude`:
      **0 disagreements**, both cases' result files BYTE-IDENTICAL modulo line endings, same process
      exit codes (0 and 1), same `Pass`, same whole `Deltas` map, and **the two cases DISAGREE with each
      other** (A `Pass: true`, B `Pass: false`) -- so this differential can tell a port that preserves a
      proof from one that always succeeds.
      **`--channels ""` IS PASSED BY OMISSION and that is the mechanism, not a detail.** An empty value
      means "every touched channel"; forwarding it as an empty string would mean "no channels", and the
      tool would compare nothing and report a pass -- a proof that cannot fail. Pinned both ways, and
      with a case that walks the forwarded argv so a flag cannot be handed the next FLAG as its value.
      **AN ABSENT RESULT IS NOT A PASS.** The tool's own machine-readable surface is read back: exit 0
      with no result file, or with one that is not JSON, is a named refusal.
      **THE SUITE CAUGHT A REAL BUG IN THE PORT.** The first version placed the result read-back AFTER
      the `try` that converts refusals, so `UNREADABLE-RESULT` escaped `main` as an uncaught exception
      and a caller got a traceback instead of the machine-readable refusal the tool promises. A refusal
      a caller cannot catch is not a refusal. Fixed, and a mutant re-opening the hole is killed.
      **CONTRACT: 36 cases, green. FALSIFICATION: 25 mutants -- 25 KILLED, 0 SURVIVED, 0 BROKE-TOOL**,
      tool mutated in place and restored byte-for-byte in a `finally`. The three that survived the first
      pass (a build timeout nothing drove, a build timeout nothing pinned, a hardcoded TFM) are the SAME
      three that survived the sibling forwarder's first pass: a contract suite is NOT inherited by
      proximity to a sibling one. Closed with a build-timeout case, a case making BOTH the build and the
      run, and a case planting a non-default TFM. The insert script that added them expected `+4` and
      aborted on a correct `+3` -- an arithmetic error in the gate, named rather than silently fixed.
      **A SECOND REAL DEFECT FOUND, IN A CALLER I HAD ALREADY REPAINTED FOR A DIFFERENT PORT.**
      `TestShardManifestTests.HT5_ci_runs_data_tests_through_the_sharded_runner` still named the
      RETIRED `.\scripts\test-sharded.ps1` spelling, so the guard failed against a `ci.yml` that has been
      correct since that runner's port: it asked for a line that no longer exists anywhere. Repointed, and
      a falsifier that plants the retired PowerShell invocation was ADDED, so a reintroduced
      `pwsh`/`.\` call is now a failure rather than an invisible pass. Module reading: **4 -> 3
      failures, 716 -> 718 passed, 720 -> 721 total** (the new falsifier). A caller test that pins a
      tool's FILENAME goes red the moment the filename changes; that is a general failure mode, not a
      one-off.
      **THE THREE SURVIVING FAILURES ARE PROVEN NOT MINE, BY MEASUREMENT.** Two of them read exactly the
      two registries this port edits, so "not mine" was a claim until it was measured: a byte-exact HEAD
      control wrote HEAD's blob for each registry over my version, re-ran, and restored my bytes in a
      `finally` (verified by hash). All three fail IDENTICALLY with HEAD's registries --
      **introduced by my edit: none**. Nothing was stashed, reset or checked-out, and only my own paths
      were ever written.
      **COUPLINGS, both in the same commit.** The exemption row naming it was `live-diagnostic-scripts`
      (located by CONTENT, not by assumption): 22 -> 23 entries, the only removal being the retired path
      it replaced, the stated reason unchanged, every other row byte-identical. New owner row
      `prove-aptitude-tool` (glob `scripts/prove-aptitude.*` + the `.py` + the suite), 524 boundaries.
      **REACHABILITY, both directions:** `guard-verification-boundaries` walks it (`verdict: OK`, 491
      owners, 524 boundaries) and `verify-change.py --plan-only` maps BOTH `scripts/prove-aptitude.ps1`
      and `gk-core/scripts/prove_aptitude.py` to `prove-aptitude-tool (focused)`.
      **A DEGENERATE ARTIFACT WAS RESTORED, not committed.** The tool's DEFAULT output path
      `docs/research/class-system/_prove-aptitude.json` was dirty at `Theta: 0`, one channel,
      `Pass: true` -- against HEAD's committed 40-channel record with `Pass: false`, which is the
      deliberate P3.1 evidence. `gk-core/tools/ProveAptitude/Program.cs:54` does
      `ArgInt(args, "--theta", 1000)` with NO validation, so the tool itself will happily compose at
      Theta 0 and write a meaningless result; the refusal therefore belongs at the wrapper, which now
      refuses before invoking it. HEAD's committed evidence restored, and the path ADDED to this
      session's fence (a GAP: no active record claimed it, and the port now writes it by default, so a
      future real run cannot collide silently).
      **POPULATION 30 -> 29** (`git ls-files '*.ps1' '*.bat' '*.cmd'`), of which 28 are under
      `scripts/` and 1 under `.claude/`.


- [x] **3.5bf** `scripts/fetch-bepinex-refs.ps1` -> `gk-core/scripts/fetch_bepinex_refs.py` (44 lines retired).
      **THE PORT'S REAL SUBJECT IS WHAT THE ORIGINAL DID BEFORE IT PROVED ANYTHING.** Its third statement
      was `Remove-Item $OutDir -Recurse -Force`, BEFORE the API call. So a rate-limited API, a typo'd tag
      or a dropped connection left the machine with NO reference assemblies -- the exact state the tool
      exists to prevent. The fetch now happens into a staging directory and is swapped in only after
      `BepInEx/core` is verified. **MEASURED, not asserted:** a good tree is published, the server is
      broken, and the previously published tree is still there afterwards with every entry and file count
      unchanged. A case covers the failure AT extraction too, not only a failure before the download,
      because falsification showed the before-download case let a mutant that deletes the tree early
      survive.
      **NEITHER NETWORK CALL WAS BOUNDED, and here is the number for it.** A real run of the ORIGINAL
      took **1443 seconds** to fetch a 34 MB asset. A real run of the port took **1486 seconds** for the
      same asset -- so the network on this machine genuinely is that slow, and the defect was never
      slowness: it was that nothing could tell "slow" from "hung" except killing the shell. Both calls
      now carry an explicit timeout with a distinct refusal per call.
      **THE REAL NETWORK RUN, AND THE DIFFERENTIAL AGAINST THE ORIGINAL'S OWN OUTPUT.** The port ran for
      real against `api.github.com`: `verdict OK`, `downloadedBytes 34146254` equal to `assetSize
      34146254` (so the download was complete, not truncated), `files 226`, `flatten already flat`,
      `zipRemoved true`. The original's real run produced **226 files** too, and its whole tree was
      snapshotted (231 entries with per-file content hashes) BEFORE the port was run. Comparison:
      **231 of 231 entries identical, 0 present only in the original, 0 only in the port, 0 differing in
      content -- BYTE-IDENTICAL TREES.**
      **SILENT FIRST-MATCH, TWICE.** `$release.assets | Where-Object {...} | Select-Object -First 1` took
      the first matching asset without saying others matched, and in the REAL release six assets differ
      only by platform. The same shape at the archive level: `Get-ChildItem $OutDir -Directory |
      Select-Object -First 1` picked an arbitrary directory. Both are now named refusals that list the
      candidates they actually saw.
      **A RATE-LIMIT PAGE SAVED AS A `.zip`.** With no content or magic-byte check, GitHub's 403 body
      landed in the zip path and failed later inside `Expand-Archive` as a compression-method error. The
      bytes are now checked for the ZIP magic first, so the refusal names the download.
      **AN EMPTY `BEPINEX_REF_TAG` SILENTLY FETCHED A DIFFERENT TAG.** `if $env:BEPINEX_REF_TAG` treats
      an empty string as absent, so a typo'd export fetched the default instead of what the caller asked
      for. It is now a named refusal, `TAG-ENV-EMPTY`. This one was found by the fixture, not by
      reading: the first version of the differential set the variable to empty on purpose to isolate the
      tag from the machine, and the tool refused -- correctly.
      **TWO REAL BUGS IN THE PORT, both found by the loopback fixture rather than by reading.**
      (1) A successful run reported `published: false` in its own machine-readable verdict, because the
      field was seeded optimistically and never re-asserted -- the one field a caller reads to decide
      whether the tree is there. (2) `require_marker()` was DEAD CODE: `flatten_if_nested` returns only
      on paths that already guarantee `BepInEx/core`, so the post-condition could not fire. Falsification
      proved it by deleting it and watching two mutants survive, and the standing rule is that an
      equivalent mutant means the dead code is DELETED rather than defended.
      **A MASKED MUTANT, WHICH IS WORSE THAN A SURVIVOR.** `_refuse` held `published` in BOTH its base
      payload and the envelope, and the envelope's update overwrote it -- so the base literal was dead
      and flipping it was MASKED, not killed. One source of truth now.
      **SIX TEST CASES WERE SILENTLY LOST, AND THE SUITE STILL READ GREEN.** A scripted edit located by
      `str.index` and sliced to a sentinel that had MOVED cut out six cases; the suite then reported
      "35 passed", which looks perfectly healthy. It was caught only because three mutants that the
      fuller suite killed stopped being killed. A lost test that leaves a green suite is the most
      dangerous shape this program has produced, and the lesson is that a mutant count is a reading about
      the SUITE as much as about the tool.
      **A FALSE KILL, IN THE OTHER DIRECTION.** The substrate case asserted on a module-level list
      populated by the OTHER cases, so under any partial selection the list was empty and the case failed
      -- five "kills" that were not kills. It now publishes its own tree and measures that. A case whose
      correctness depends on which other cases ran is a false kill waiting to hide a real hole.
      **CONTRACT: 41 cases green (44 defs), and green under the fast static selection too, which is
      what makes that selection safe to use. FALSIFICATION: 26 mutants -- 26 KILLED, 0 SURVIVED, 0
      BROKE-TOOL**, each kill naming its own case. The `--api-base` seam exists precisely so the suite
      can drive a real HTTP server over loopback instead of the internet, and the property that it is
      WIRED is asserted STATICALLY: with the flag unwired every case escapes to the real GitHub and one
      downloads 34 MB, so the harness runs the static selection first and that mutant dies in
      milliseconds.
      **COUPLINGS, both in the same commit.** The exemption row naming it was `local-operational-scripts`
      (located by CONTENT): 24 -> 25 entries, the only removal being the retired path, the stated reason
      unchanged, every other row byte-identical. New owner row `fetch-bepinex-refs-tool`, 525 boundaries.
      **REACHABILITY, both directions:** `guard-verification-boundaries` walks it (`verdict: OK`, 492
      owners) and `verify-change.py --plan-only` maps BOTH `scripts/fetch-bepinex-refs.ps1` and
      `gk-core/scripts/fetch_bepinex_refs.py` to `fetch-bepinex-refs-tool (focused)`.
      **THE TWO REMAINING GUARD FAILURES ARE PROVEN NOT MINE, ON THIS COMMIT'S REGISTRIES.** A byte-exact
      HEAD control wrote HEAD's blob for each edited registry over mine, re-ran, and restored my bytes in
      a `finally` (verified by hash): both fail IDENTICALLY with HEAD's registries, **introduced by this
      port: none**. The `session-boundary` DRIFT(3) is the same pre-existing one recorded at 3.5bb.
      **POPULATION 29 -> 28.**


- [x] **3.5bg** `scripts/prepare-injector-refs.ps1` -> `gk-core/scripts/prepare_injector_refs.py` (63 lines
      retired). **THIS ENTRY IS THE BILL FOR 3.5bf: THE PREVIOUS PORT BROKE THIS TOOL.** Its line 6 ran
      `fetch-bepinex-refs.ps1`, which that commit deleted, so a live run exits 1 with "term not
      recognised". A port that renames a tool and leaves its callers behind is the defect class 3.5bb is
      about, and the third port of it was mine. It is recorded here rather than as a one-line name fix,
      because this tool's own defects needed the same treatment.
      **THE DEFECTS THIS PORT RETIRES, each measured or read.**
      * **THE FETCHER'S EXIT CODE WAS IGNORED.** `& (Join-Path $PSScriptRoot "fetch-bepinex-refs.ps1")`
        with no `$LASTEXITCODE` check, under `$ErrorActionPreference = "Stop"`. A child process exiting
        nonzero is NOT a PowerShell exception, so a FAILED fetch fell through to the interop logic and
        could still succeed -- on a STALE tree, reporting green. Now a named `FETCHER-FAILED` refusal, and
        a missing fetcher is `FETCHER-MISSING` rather than a half-prepared tree.
      * **THE INTEROP ZIP DOWNLOAD WAS UNBOUNDED**, on a network where a real sibling fetch measured
        1486s for 34 MB, so "slow" is the norm and an unbounded call cannot be told from "hung".
      * **IT REMOVED ITS STAGING DIRECTORY BEFORE EXTRACTING**, so a bad zip destroyed what was there.
      * **AN ARBITRARY FIRST HIT FOR THE INTEROP ROOT.** `Get-ChildItem -Recurse -Filter
        "Assembly-CSharp.dll" | Select-Object -First 1`. More than one is now `INTEROP-AMBIGUOUS`, naming
        every place it found one.
      * **A SET-BUT-WRONG `FUSIONRPG_GAME_DIR` FELL THROUGH SILENTLY** -- `if ($env:X -and (Test-Path
        $env:X))` treats a path that does not exist as unset, so a typo looked honoured. Now
        `GAME-DIR-MISSING`, with `--ignore-missing-game-dir` for the old fall-through.
      * **`Copy-Item (Join-Path $src "*")` COPIED NOTHING, SILENTLY**, if the glob matched nothing; the
        failure then surfaced later naming the wrong thing. Now `INTEROP-EMPTY-SOURCE`.
      * **THE CLOSING `$env:FUSIONRPG_GAME_DIR = $Refs` WAS INERT** -- it set the variable in a process
        that exited immediately, so no caller ever inherited it. The value is now REPORTED, in `--json`
        and on STDOUT as a line a caller can use, and the docstring says plainly it is not exported. This
        is the one behaviour that could not be preserved, because it never worked.
      **A BRANCH THAT LOOKS LIKE A BUG IS KEPT AND DISCLOSED, NOT "FIXED".** Step (d) looks for a game
      install in the directory ABOVE the repository root, which on this machine is `D:\Works\source` and
      very unlikely to hold one. That is what the original did; it is the last branch and the final check
      still refuses, so it is harmless rather than useful. Changing it would be an unrequested behaviour
      change, so the docstring says it was kept deliberately and the verdict reports which branch fired.
      **THE DIFFERENTIAL, AND AN ORACLE THAT IS ITSELF BROKEN.** The original cannot be run at all (see
      above), so the oracle is a throwaway copy OUTSIDE the repository with exactly ONE line changed --
      the broken fetch call, asserted to be line 6 and nothing else -- over the reference tree the
      original would have fetched. Measured against a REAL install,
      `H:\Games\PVZ-Fusion-3.9_BepInEx_Full_Tools`, whose interop is 99 real assemblies: branch (a)
      **tree-identical**, 99 files, same content hashes. Branch (b) built a REAL 61 MB zip from 64 of
      that install's assemblies and served it over REAL loopback HTTP: **tree-identical**, and the
      interop root inside the zip resolved to `BepInEx/interop` on both sides. Branch (c), interop
      already present: **tree-identical**, and both sides exit 0. **0 disagreements.**
      **BRANCH (c) WAS FIRST NOT DIFFERENCED AT ALL.** The harness removed the interop from the oracle's
      tree while seeding the port's, so the original exercised "no interop anywhere" (exit 1) and the
      port exercised branch (c) (exit 0) -- two different scenarios compared as one. Both sides are now
      seeded the same way, and the case asserts both exit codes agree.
      **TWO REAL BUGS IN THE PORT, both found by the contract suite.** (1) `--ignore-missing-game-dir`
      did not fall through: it skipped branches (b), (c) and (d) and went straight to the final refusal,
      the exact opposite of what its name promises. A flag whose name is a promise about control flow
        has to match the control flow. (2) `interopFrom` reported NATIVE separators on Windows while the
        refusal text did too -- and when the envelope field was switched to POSIX the refusal text was
        left behind, so the same field read differently in two places in the same file.
      **AN ARGPARSE CONSTRAINT, MEASURED NOT GUESSED.** `--fetch-arg` as a paired flag/value cannot carry
      a value beginning with `-`: `--fetch-arg --api-base --fetch-arg URL` dies with SystemExit 2 before
      the body runs, and the arguments worth forwarding are exactly the ones beginning with `-`. The
      flag therefore takes ONE shell-quoted string and splits it itself.
      **A FIXTURE THAT WAS BLIND TO A REAL DEFECT, TWICE.** The separator case used ambiguous hit
      directories named `a` and `b`; the relative path to a hit DIRECTORY is one segment even when the
      file is nested, and for one segment a native rendering and a POSIX rendering are the SAME TEXT, so
      a mutant that reverted the refusal to native separators survived through it. Two levels of nesting
      (`pkg/first`) is the minimum that makes them differ. And `assertIn("a", detail)` /
      `assertIn("b", detail)` passed against a refusal that listed nothing, because both letters occur in
      ordinary words ("places", "Repack"); the case now asserts the candidates as an exact list.
      **THE SAME MASKED-DUPLICATE DEFECT AS 3.5BF, IN A DIFFERENT FIELD.** `_refuse` held `prepared` in
      both its base payload and the envelope, and the envelope overwrote it, so flipping the base literal
      was MASKED rather than killed. One source of truth, and the mutant re-anchored onto it.
      **CONTRACT: 39 cases green, and green under the fast static selection too. FALSIFICATION: 28
      mutants -- 28 KILLED, 0 SURVIVED, 0 BROKE-TOOL**, each kill naming its own case. Three mutants
      were DROPPED or re-anchored rather than left to report a meaningless result: one targeted an
      assertion whose subject is the SUITE's own source, which the harness never mutates, so it could
      never be killed; two were re-anchored after the tool changed underneath them, and a harness that
      silently keeps a stale anchor is reporting a kill of nothing.
      **COUPLINGS, both in the same commit.** The exemption row naming it was `local-operational-scripts`
      (located by CONTENT): 25 -> 26 entries, the only removal being the retired path, the stated reason
      unchanged, every other row byte-identical. New owner row `prepare-injector-refs-tool`, 526
      boundaries. **REACHABILITY, both directions:** `guard-verification-boundaries` walks it (`verdict:
      OK`, 493 owners) and `verify-change.py --plan-only` maps BOTH `scripts/prepare-injector-refs.ps1`
      and `gk-core/scripts/prepare_injector_refs.py` to `prepare-injector-refs-tool (focused)`.
      **THE REMAINING GUARD FAILURE IS PROVEN NOT MINE, ON THIS COMMIT'S REGISTRIES**, by a byte-exact
      HEAD control that restored my bytes in a `finally`: identical failures with HEAD's registries,
      **introduced by this port: none**. The `session-boundary` DRIFT(3) is the pre-existing one recorded
      at 3.5bb.
      **POPULATION 28 -> 27.**


- [x] **3.5bh** `scripts/wait-for-deploy.ps1` -> `gk-core/scripts/wait_for_deploy.py` (46 lines retired). **THE
      FIRST LIVE-TIER PORT PROVEN AGAINST THIS REPOSITORY'S OWN SERVER, ON A SLOT'S OWN PORT.**
      **THE DEFAULT BASE URL WAS THE OWNER'S PORT, HARDCODED.** `[string]$BaseUrl =
      "http://127.0.0.1:5088"`, on a machine with a three-slot pool on 5101/5102/5103 where `5088` is the
      OWNER's server and not "the" port. A probe pointed at the owner's server measures the wrong server
      and reports it as ground truth. The URL is now read ONCE from `FUSIONRPG_SERVER_URL` -- the variable
      the Injector itself reads, so both sides agree -- falling back to `127.0.0.1:5088` only when nothing
      is configured. **The default is KEPT, because a single-slot install still needs it, and the rule is
      "never 5088 SILENTLY" rather than "never 5088": where the value came from is REPORTED**, so a reader
      can see the probe had no better information.
      **THE GAME CHECK COULD SEE ANOTHER SLOT'S GAME.** `Get-Process -Name PlantsVsZombiesRH` matches by
      NAME, so with three slots running a probe for slot 2 would see slot 1's game and report a confirmed
      deploy it never observed. When an install is known -- `--game-install`, `FUSIONRPG_GAME_DIR`, or the
      pool root -- the process is matched by EXECUTABLE PATH under it. Without one it still matches by
      name, and **the verdict says which kind of match happened**, because a name-only match is a weaker
      claim and should not read like a strong one.
      **THE HEALTH CALL'S ERROR WAS SWALLOWED BY AN EMPTY `catch { }`.** Connection refused, a timeout, a
      body that is not JSON -- all became `$health = $null` and the loop continued with no record of why.
      The last error is now carried, so a timeout saying "server not answering" also says what the server
      said about it.
      **A TIMEOUT AND A CRASH SHARED EXIT CODE 1**, and a caller could not tell a deploy that genuinely
      did not arrive from a script that broke. Now `0` ready, `1` the budget expired with the reason
      ladder, `64` a refusal.
      **THE DIFFERENTIAL IS THREE CASES, AND THE THREE MUST DISAGREE WITH EACH OTHER.** A. READY, over a
      real loopback HTTP server answering `{"ok": true, "injectorConnected": true}` with `--no-game` --
      the green path, which this repository's own server cannot reach on its own, since it reports
      `injectorConnected: false` with no game running. B. the REAL slot-1 server on **:5101**, healthy but
      not injector-connected: the state this tool exists to report, on the slot's own port and never
      :5088. C. a port with nothing on it. **0 disagreements**: same exit code, same reason, same readiness
      on all three, and the three reasons are MUTUALLY DISTINGUISHABLE on BOTH sides
      (`ready`, `injector-connected-false`, `server-not-answering`). The original had no broken
      dependency, so unlike 3.5bg the oracle ran as-is -- no repaired copy was needed.
      **ONE REAL BUG IN THE PORT, FOUND BY THE SUITE.** `game_running` called `_TASKLIST`, a name that does
      not exist; the game check would have raised `NameError` on every call. A function called only
      through a real subprocess run on this machine would not have surfaced it, because there is no game
      running in any slot.
      **A META-CASE THAT CRIED WOLF, FIXED RATHER THAN IGNORED.** The "no case starts a server it cannot
      stop" case read only `body` from a `with`/`try` node, so every `finally: server.shutdown()` was
      reported as unowned -- a false positive in the case that exists to catch false positives. A meta-case
      that reports a defect where there is none trains a reader to ignore it, so it now reads `finalbody`
      too.
      **AN EQUIVALENT MUTANT THAT NAMED DEAD CODE.** `a_trailing_SLASH_is_NOT_trimmed` survived because
      `probe_health` builds its URL as `f"{base_url.rstrip('/')}/health"` and already trims, so the second
      `rstrip` in `main` can never change the request. The strip in `main` is DELETED rather than defended,
      and the mutant is removed rather than re-anchored: its target is gone, which is the resolution for an
      equivalent mutant.
      **TWO MORE REAL GAPS, BOTH IN THE SUITE.** (1) `not health.get("injectorConnected")` and
      `... is False` differ for exactly one input -- the field ABSENT -- and only `ok` had a case for that,
      so a server that has not finished booting was the realistic shape nothing covered. (2) Every timeout
      case asserted the exit code and the reason but never the `verdict` STRING, so a tool that labelled
      every single run READY passed all of them; `verdict` is the field a dashboard reads. And the
      docstring case checked the WORDS but not the HEADING, so renaming the heading passed -- the identical
      defect 3.5bf hit, fixed the identical way.
      **CONTRACT: 39 cases green (10 subtests), and green under the fast static selection too.
      FALSIFICATION: 28 mutants -- 28 KILLED, 0 SURVIVED, 0 BROKE-TOOL**, each kill naming its own case.
      Three anchors were read FROM THE TOOL rather than typed, after two rounds were lost to backslash
      escaping: an anchor typed into a shell heredoc comes out subtly different from the one in the tool,
      so the harness now extracts it by a marker and verifies every anchor occurs exactly once before any
      result is read.
      **COUPLINGS, both in the same commit.** The exemption row naming it was `local-operational-scripts`
      (located by CONTENT): 26 -> 27 entries, the only removal being the retired path, the stated reason
      unchanged, every other row byte-identical. New owner row `wait-for-deploy-tool`, 527 boundaries.
      **REACHABILITY, both directions:** `guard-verification-boundaries` walks it (`verdict: OK`, 494
      owners) and `verify-change.py --plan-only` maps BOTH `scripts/wait-for-deploy.ps1` and
      `gk-core/scripts/wait_for_deploy.py` to `wait-for-deploy-tool (focused)`.
      **THE REMAINING GUARD FAILURE IS PROVEN NOT MINE, ON THIS COMMIT'S REGISTRIES**, by a byte-exact HEAD
      control that restored my bytes in a `finally`: identical failures with HEAD's registries,
      **introduced by this port: none**. The `session-boundary` DRIFT(3) is the pre-existing one recorded
      at 3.5bb.
      **POPULATION 27 -> 26.**


- [x] **3.5bi** `scripts/lawn-combat-observer.ps1` -> `gk-core/scripts/lawn_combat_observer.py` (45 lines
      retired). **A REAL PROOF ON A REAL SERVER, AND A SCOPE OF FINDINGS LARGER THAN THE SCRIPT.**
      **THE DIFFERENTIAL IS TWO CASES OVER THE REAL TOOL AND THE REAL SLOT-1 SERVER ON :5101**, never
      :5088. A. a live server with NO INJECTOR -- the real slot-1 server, which is `ok` but has never had
      an /api/perf window posted because no game is running. The tool answers `NoData: true` with a
      reason and exits NON-ZERO, and that is the load-bearing case: a "success" that means nothing is
      available, and both sides must keep the difference between **no data** and **zero hits**. B. no
      server at all, where the tool's health pre-check fails, it STILL writes a run file, and it exits 1
      with a DIFFERENT `NoDataReason`. **0 disagreements**: same exit code both cases, the run file
      `NoData` / `TotalHits` / `WindowsObserved` / `RequestedDurationSec` /
      `InjectorSessionActiveEverTrue` all equal, the run file landing in the SAME PLACE on both sides, and
      the two cases **distinguishable by their reason** so the differential is not agreeing vacuously.
      **THE HARNESS ITSELF REPORTED AGREEMENT WITHOUT HAVING MEASURED ANYTHING, TWICE.** It passed
      `--baseurl=<url>` and both sides answered exit 2 "unknown flag" -- because `Options.Parse` switches
      on the WHOLE token after trimming dashes, so `baseurl=...` matches nothing. Both agreed, so the
      differential was green, and it had compared two argument errors. Separately it compared the child's
      STDOUT against the original's stdout **+ stderr**, which reports a difference that is an artefact of
      the comparison. A differential that agrees for the wrong reason is worse than one that fails,
      because it buys false confidence; both are now stated in the harness itself.
      **THE FORWARDING SEAM IS THE REAL WORK, AND IT IS A SHAPE THIS PROGRAM HAS NOW HIT FOUR TIMES.**
      The original used `[Parameter(ValueFromRemainingArguments)] $RestArgs`. In Python, a bare `--` is
      rejected by argparse before the body runs, and a paired flag cannot carry a value beginning with `-`
      -- which are exactly the arguments worth forwarding. So the wrapper takes the flags it OWNS
      (`parse_known_args`) and hands the rest on **verbatim and in order**, and then **ASSERTS AT RUN TIME
      that the two flag sets are disjoint**, because a collision would silently steal a flag from the tool
      and the tool would answer "unknown flag" for an argument the caller plainly supplied. **The tool's
      flags are READ FROM ITS OWN SOURCE at run time** (`Options.Parse`'s `case` labels), not transcribed:
      a transcribed list agrees with itself forever and can never notice that the tool changed, which is
      the only reason to read it.
      **THE RUN FILE IS THE TOOL'S REAL OUTPUT AND IS READ BACK.** A wrapper printing only its child's
      stdout reports its own opinion of a result. `NoData` and `TotalHits` come from the file, and an
      absent run file is a refusal -- "no data" and "zero hits" are different findings and the run file is
      where the difference is recorded.
      **THE SAME BUG THIS PROGRAM HAS NOW PRODUCED TWICE: A REFUSAL THAT ESCAPES AS AN EXCEPTION.** The
      run-file read-back sat AFTER the `try` that converts refusals, so `UNREADABLE-RESULT` escaped `main`
      as an uncaught traceback. The sibling `prove_aptitude` port's suite caught the identical shape, and
      it was repeated here because the shape was COPIED rather than learned. A refusal a caller cannot
      catch is not a refusal. The read-back is inside the `try` now, and a mutant re-opening the hole is
      killed.
      **A STUB CASE THAT OCCUPIED THE SLOT OF A REAL ONE.** `test_exit_0_with_NO_run_file_...` ran the
      tool WITHOUT patching `_RUN` -- so it drove the real tool -- and then asserted only that stdout was
      not None. It exercised nothing, and falsification duly reported a mutant that makes an absent run
      file a pass straight through it. A case that cannot fail is worse than a missing case.
      **A CASE WRITTEN AGAINST A SHAPE THE SUBJECT DOES NOT HAVE.** The assembly-name case asserted an
      `<AssemblyName>` element the csproj does not contain, so it could only ever fail; the csproj declares
      the name WITHOUT the extension, so the wrapper's file name is that plus `.dll`. And `assertIs` was
      used on a STRING, which is identity and not equality -- the same class of mistake as comparing a
      path's short and long spellings, which also bit this port (`os.path.normcase` lowercases but does
      not expand an 8.3 name; `os.path.realpath` expands but does not case-fold; both are needed).
      **AN EQUIVALENT MUTANT THAT NAMED A REDUNDANT BRANCH.** `pathlib`'s `/` already returns the
      right-hand side when it is absolute, so the explicit `is_absolute()` test in the `--out` resolution
      could never change the result. The branch is DELETED rather than defended and the mutant removed.
      **A REAL GAP IN THE REPOSITORY, FOUND WHILE PROVING THE PORT: THE TOOL'S RUN FILE WAS UNTRACKED
      AND UNIGNORED.** `Options`' own docstring says the run file is "never a repo path a caller did not
      explicitly choose", but its DEFAULT is a bare relative filename and the wrapper runs the child IN the
      tool directory -- so the default DOES land inside the repository, and every real run left an
      untracked file behind. `.gitignore` now carries it, with the reasoning in the file, and a case
      asserts it is ignored so the gap cannot reopen.
      **THREE INVALID ESCAPE SEQUENCES, MEASURED BY THE COMPILER AND NOT BY A REGEX.** A regex sweep
      reported 35 affected files, most of them valid escapes inside raw strings; compiling every file with
      warnings recorded reported **three** real ones. One was this port's suite (`"C:\dotnet.exe"`, `\d`);
      the other two -- `gk-core/tests/tools/test_ps1_rename_sweep.py` and `gk-core/scripts/cscan.py` -- turned out to be
      IN this session's fence, so they were fixed here rather than disclosed. Escaping the backslash
      leaves the RENDERED docstring byte-identical and removes the warning.
      **CONTRACT: 38 cases green (3 subtests), and green under the fast static selection too.
      FALSIFICATION: 32 mutants -- 32 KILLED, 0 SURVIVED, 0 BROKE-TOOL**, each kill naming its own case.
      Two anchors were re-anchored after the tool changed underneath them; a harness that silently keeps a
      stale anchor reports a kill of nothing.
      **COUPLINGS, both in the same commit.** The exemption row naming it was `live-diagnostic-scripts`
      (located by CONTENT): 23 -> 24 entries, the only removal being the retired path, the stated reason
      unchanged, every other row byte-identical. New owner row `lawn-combat-observer-tool`, 528 boundaries.
      **REACHABILITY, both directions:** `guard-verification-boundaries` walks it (`verdict: OK`, 495
      owners) and `verify-change.py --plan-only` maps BOTH `scripts/lawn-combat-observer.ps1` and
      `gk-core/scripts/lawn_combat_observer.py` to `lawn-combat-observer-tool (focused)`.
      **THE REMAINING GUARD FAILURE IS PROVEN NOT MINE, ON THIS COMMIT'S REGISTRIES**, by a byte-exact HEAD
      control that restored my bytes in a `finally`: identical failures with HEAD's registries,
      **introduced by this port: none**. The `session-boundary` DRIFT(3) is the pre-existing one recorded
      at 3.5bb.
      **POPULATION 26 -> 25.**


- [x] **3.5bj** `scripts/lib/LiveLawnSetup.ps1` -> `gk-core/scripts/lib/live_lawn_setup.py`, **and the population
      does NOT drop in this change.** That is a DEPENDENCY ORDER, not a deferral, and the difference is
      worth stating precisely because "a port that does not reduce the count" is exactly the shape of
      self-exemption. **CORRECTED 2026-09-29 — this entry said "four callers still dot-source the `.ps1`"
      and named `prove-status-l2-one.ps1` and `prove-vfx.ps1` among them. MEASURED repo-wide by grepping
      every tracked `.ps1` for the dot-source operator, there are exactly THREE dot-sources left, all of
      them inside the population:**
      `audit-status-vfx-identity.ps1:171`, `audit-status-vfx-identity.ps1:172` and
      `lib/DebugStatusApply.ps1:5`. `prove-status-l2-one.ps1` was ported on 2026-09-29 and is gone.
      **`prove-vfx.ps1` never dot-sourced the library at all** -- its only occurrence of the string
      `LiveLawnSetup` is a stale header COMMENT at its line 7, and it makes zero calls to any of the
      library's seven functions. It is a free-standing script with its own private reimplementations of
      four of them, so porting it neither consumes nor blocks the library. **So `audit-status-vfx-identity.ps1`
      is the only remaining external consumer, and one port retires all three files.** The dependency
      order below was sound; the COUNT and the membership were not, and the count is what a reader would
      have relied on. All remaining callers are THEMSELVES in the population, so each is ported onto the
      Python module in turn and the exemption's glob stops matching a live file when the LAST one lands.
      **Porting a
      consumer first would mean reimplementing the library's seven functions** -- the two-implementations
      defect this program exists to prevent -- and deleting the `.ps1` now would break working
      scripts. The exemption row's exact path became the GLOB `scripts/lib/LiveLawnSetup.*`, which still
      matches the live `.ps1` and separately names `live_lawn_setup.py`: a glob covering only a deleted
      file would be a mapping that quietly stops resolving to anything. **Population stays 25.**
      **IT IS A MODULE, AND THAT IS THE POINT.** The PowerShell form was DOT-SOURCED; a file that cannot be
      imported cannot be a library, so a "module" that only runs as a script would be a wrapper wearing a
      module's name. All seven functions are importable, `preflight` exposes the module's own
      machine-readable surface so the file is also probeable by hand, and the docstring publishes the
      PowerShell-to-Python rename map -- which a case checks, because a rename that misses one of four
      callers is a stale citation in the file whose whole job is to stop people guessing.
      **THE HARDEST FUNCTION, WITH A REAL MEASURED VALUE.** `Get-DebugMaxEventId` is an exponential probe
      then a bisect. Against this repository's OWN servers, on each slot's own port, the retired PowerShell
      returned **928853** and the port returns **928853** -- on :5101, :5102 and :5103 alike. **0
      disagreements** across four case groups: that search on all three slot ports; the error scan over a
      real stream; the two PURE functions on eight planted shapes; and `Ensure-LiveLabBoard` against a real
      server whose injector is not connected -- which on this machine is not a simulated state, since all
      three slot servers answer `ok` with `injectorConnected: false`, which IS the refusal path. Both sides
      refuse, and the port's refusal carries the original's MESSAGE, skill pointer and URL included:
      those texts are the accumulated knowledge of several live-debug incidents and they are the reason the
      file exists.
      **THE SEARCH RETURNS N-1, AND THAT IS NOT A BUG.** It asks "are there events with id > X", so over a
      contiguous `1..N` space it returns N-1. Both implementations return the same value, so the semantics
      are preserved -- only my first EXPECTATION was wrong, and a reader who assumes the true maximum here
      will build a caller that skips the newest event. Pinned as a value, with its reason.
      **THE HARNESS MEASURED TWO DIFFERENT SERVERS, AND THE RAW DUMP IS WHY I KNOW.** Case D never passed
      the port to the Python side, so `$URL` became empty and the port fell back to the built-in default --
      **:5088, the OWNER's server** -- while the PowerShell side got :5101. The harness reported that as a
      disagreement about refusal text. Three fixes, all now permanent: a `$URL` with no port is a LOUD
      refusal, both sides run with `FUSIONRPG_SERVER_URL` **unset** so a stale value cannot redirect one
      side, and every "absent" value prints both sides' RAW output. Before the raw dump this looked like a
      measurement; it was the wrong server.
      **AND THE SAME HARNESS HAD BEEN MEASURING NOTHING AT ALL.** Its Python preamble was built by
      interpolating a nested path expression into an f-string delimited by the same quote character -- a
      SyntaxError before 3.12 -- so every generated script died on line 1, the port side produced no
      output, and the harness printed "absent" as though that were a result. **A differential that silently
      measures nothing is worse than one that fails, because it reads as evidence.** It now SELF-CHECKS:
      every generated script shape is compiled, through the same `$URL` substitution the comparisons use,
      before a single comparison is read.
      **A REAL REGRESSION THIS PORT INTRODUCED, CAUGHT BY ITS OWN SUITE.** Making `get_debug_payload`
      refuse on a string that is not JSON -- correct, and the fix for the original's swallowed `catch` --
      BROKE the error scan, whose last resort IS that raw unparsed text. One malformed event in a thousand
      aborted the scan that exists to report malformed events. The scan now catches the refusal and falls
      back to the raw payload, and both halves have a case.
      **THE ORIGINAL'S DEFECTS, each with a case.** The event reads had NO timeout and the search no total
      budget, so a hung read hung the search with no output and no way to tell it from a slow one -- the port
      bounds both, and the budget is a SEPARATE bound because a per-request timeout bounds one call and not
      the cost of dozens. `Get-DebugPayload`'s `catch { return $null }` made "no payload" and "a payload
      that would not parse" the same value, so a scenario that produced no evidence looked exactly like one
      that produced unreadable evidence. `Ensure-LiveLabBoard`'s parameter default was **:5088**, the
      OWNER's port, so a setup script entered somebody else's board; the URL is read once from
      `FUSIONRPG_SERVER_URL` and **its source is returned**, because a caller that cannot see which server
      it measured cannot tell a wrong board from a right one.
      **ONE SURVIVOR CLASSIFIED, NOT KILLED, WITH ITS MEASUREMENT.** The `high > 2**62` overflow guard
      needs 4.6e18 HTTP requests to reach, and the 30s total budget the port added fires long before it, so
      the mutant is NOT-APPLICABLE rather than a hole. The guard is KEPT: a caller who passes an enormous
      budget should still not overflow, and a second boundary behind the first is not a duplicate.
      **FIVE MORE REAL SUITE GAPS, ALL NOW CLOSED**: a health document with NO `ok` field (where
      `not get(...)` and `... is False` differ, and a server part-way through boot is the realistic shape);
      the NO-LIVING-ZOMBIE refusal losing its recent-error lines; the `-SkipSetup` hint, which is what tells
      a caller the flag moved the burden onto them; a failed quick-start naming no endpoint; and `simEnabled`
      being only warned about rather than REPORTED, so it was visible to a person and invisible to a
      caller. One of those five failed twice for a FIXTURE reason -- its error events sat at the id the
      search's own cursor excludes, so the case filtered out its own evidence, which is a broken case and
      not a finding.
      **CONTRACT: 48 cases green (8 subtests), and green under the fast offline selection too.
      FALSIFICATION: 42 mutants -- 42 KILLED, 0 SURVIVED, 0 BROKE-TOOL**, each kill naming its own case.
      **COUPLINGS, in the same commit, following the `keepverse_roots.py` precedent exactly.** Exemption row
      `shared-script-libraries` 4 -> 5 entries, the only change being the exact path becoming the glob, the
      stated reason unchanged, every other row byte-identical. New owner row `live-lawn-setup-tool`, 529
      boundaries. **REACHABILITY, both directions:** `guard-verification-boundaries` walks it (`verdict:
      OK`, 496 owners) and `verify-change.py --plan-only` maps BOTH `gk-core/scripts/lib/live_lawn_setup.py` AND
      the still-live `scripts/lib/LiveLawnSetup.ps1` to `live-lawn-setup-tool (focused)`.
      **THE REMAINING GUARD FAILURE IS PROVEN NOT MINE, ON THIS COMMIT'S REGISTRIES**, by a byte-exact HEAD
      control that restored my bytes in a `finally`: identical failures with HEAD's registries,
      **introduced by this port: none**. The `session-boundary` DRIFT(3) is the pre-existing one recorded
      at 3.5bb.
      **ALL THREE LIVE SLOTS ARE NOW HELD BY THIS SESSION** -- 1 on :5101, and 2 and 3 on :5102 and :5103
      under DERIVED session ids, because the pool permits one slot per session id. That is recorded in the
      session record's own `liveSlots` block, with the reason, so `slots.json` is explainable rather than
      puzzling. Every live proof names the port it ran on, and **:5088 is never probed by this session.**


- [x] **3.5bk** `scripts/prove-status-l2-one.ps1` -> `gk-core/scripts/prove_status_l2_one.py`.
      **POPULATION 25 -> 24, and this is a LEAF, unlike 3.5bj.** Nothing dot-sources it, so the `.ps1` is
      DELETED and its exemption entry is REMOVED rather than widened to a glob -- a glob covering only a
      deleted file is a mapping that quietly stops resolving to anything. **0 disagreements** over three case
      groups: the real refusal path on all three slot ports (both sides refuse, with the original's message
      and skill pointer); the three counts and the acceptance rule on the SAME planted pages fed to both
      sides; and the scenario name in a URL path, for five hostile names. The harness now ASSERTS that three
      planted pages give three DISTINCT verdicts, because a differential whose pages collapse into one
      answer is not measuring the rule.
      **IT IMPORTS THE LIBRARY 3.5bj LANDED IN THE SAME PROGRAM, AND A CASE PROVES IT.** Four library
      functions come from `live_lawn_setup`; a case scans the CODE -- with docstrings STRIPPED, because
      `ast.unparse` re-emits the module docstring, and that docstring quotes the retired `Invoke-RestMethod`
      while describing the very defect, so a case grepping the whole file could only ever fail -- and asserts
      none of them is reimplemented here. Reimplementing them is the two-implementations defect, and the
      `.ps1` library still exists precisely so it can be deleted last.
      **FOUR SURVIVORS SHARED ONE ROOT CAUSE: NO CASE REACHED THE END OF `main()`.** The final re-read, the
      verdict and the exit code were never executed by any test, because the library's injector refusal
      always stopped the run first. An END-TO-END case now drives `main()` to a verdict with a scripted
      event stream, substituting ONLY the library's board step -- the library stays real, the substitution is
      named, and reaching the real one needs a running game. **A RUN THAT PRODUCED NO EVIDENCE NOW EXITS 1
      AND SAYS `FAILED`**, which is the entire point of the tool and was previously unproven.
      **THREE MORE REAL GAPS, each found by a mutant that survived.** The MIXED page has
      `started == applied == 2`, so an implementation reporting the started number for `applied` is
      INDISTINGUISHABLE on it -- a fixture that cannot fail; the fx-only page is what separates them, and it
      is pinned there. The name refusal names the path in its HEAD, so an assertion on the path cannot see
      the tail being lost; the ACCEPTED PATTERN is pinned instead, because that is the part a person acts
      on. And the budget check looked redundant -- the library enforces the same invariant one layer down --
      but is NOT, because the library resolves the base URL FIRST, so with a hostile URL it would answer
      BASE-URL-INVALID and the caller would never learn its own budget was the problem. The ORDER is the
      only part that differs, so the ORDER is what a case pins.
      **THE ORIGINAL'S DEFECTS, each with a case.** The three `/api/events` polls had NO timeout, inside a
      loop bounded only by `-TimeoutSec`, so a hung poll meant the budget was not a bound at all; the port
      bounds every read AND checks the deadline BEFORE the sleep, clamping the sleep to what is left, where
      the original's `do/while` checked it only after an unbounded poll. The scenario name was interpolated
      into `/scenario/$Scenario` unchecked, so `../../admin` became a different REQUEST than intended and
      the counts belonged to that other request -- the differential RECORDS which paths the original would
      have asked for, for five hostile names. And the default base URL was **:5088**, the OWNER's port.
      **`debug.status` ALONE IS STILL NOT ENOUGH**, deliberately: a status event with no apply behind it is
      the signature of the bug this scenario exists to catch. Widening the rule to accept it is in the
      mutant set and dies on four cases.
      **TWO REAL HARDENING GAPS, both found by the suite against inputs the tool must survive.** A page that
      is not a list, or holds a non-object, now counts as zero instead of raising. And an UNHASHABLE `kind`
      -- a list, which a server can send as easily as a string -- no longer raises `TypeError` from `kind in
      counts`. The events come from a SERVER, and a report that crashes on an unexpected page is a tool that
      cannot be pointed at a server it has not met.
      **TWO REPAIRS THIS PROGRAM OWED, FOUND BY A CHECK I WROTE FOR THIS CHANGE.** A retirement check that
      asks "does anything still point at the PowerShell" found TWO RUNBOOKS that told a person to run the
      deleted file, and both are repointed in this same change: the debug-pipeline link now names the Python,
      and the live-test-ssot parity table row is struck through and names the port as the only form. That
      check also **found 13 DEAD MAPPINGS in the registry** -- globs that a ps1-ban port had already made
      match nothing, residue of this same program across its sessions -- and all 13 are removed. **The one
      dead mapping KEPT is `retired-verification-boundaries-lib: scripts/lib/VerificationBoundaries.ps1`,
      because that row is NAMED for a retired path and a path that no longer exists is its content**; the
      rule is residue-vs-intentional, not convenient-vs-inconvenient.
      **AND MY OWN DEAD-MAPPING CHECK WAS WRONG TWICE, IN THE DIRECTION THAT FLATTERS.** `partition("*")`
      cannot match a `**` glob, so seventeen recursive globs were reported dead when they are live; globs
      are matched with `fnmatch` against the measured set, which is what "this pattern selects this file"
      means. And `git ls-files` does not list UNTRACKED files, so the run reported the owner row's own
      just-added glob as matching nothing. The measured set is `git ls-files --cached` plus the index, so a
      path about to be committed counts as live.
      **CONTRACT: 44 cases green (32 subtests). FALSIFICATION: 40 mutants -- 40 KILLED, 0 SURVIVED, 0
      BROKE-TOOL.** A hang is now reported as a labelled KILL rather than a third category, because a
      category that is neither kill nor survivor is one every reading has to interpret; BROKE-TOOL now means
      the suite could not be COLLECTED, which is what it should have meant, and counting any
      `AttributeError` as a harness failure had been reporting two real kills as harness faults.
      **COUPLINGS, in the same commit.** Exemption row `live-diagnostic-scripts` 24 -> 23 entries (the
      retired file, gone) and 13 residue globs removed from across five rows; new owner row
      `prove-status-l2-one-tool`, 530 boundaries, carrying the glob `scripts/prove-status-l2-one.*` so that
      a later deletion of the old name still selects this owner -- **without that glob
      `--deleted-paths` refused with `BOUNDARY-MISSING`**, because the exemption that used to map the file
      is gone, so the deletion had no boundary at all. **REACHABILITY, both directions:**
      `guard-verification-boundaries` walks it (`verdict: OK`, 497 owners) and `verify-change.py --plan-only`
      maps the new script, its suite, both runbooks, AND the deleted path to their owners.
      **FENCE: the two runbooks were a GAP, not a CROSSING** -- no ACTIVE record claimed either -- and a
      retirement that repoints a runbook cannot be done without touching it, so both join this session's
      fence (1060 paths) and the gap is disclosed here rather than left for a reader to find.
      **THE REMAINING GUARD FAILURE IS PROVEN NOT MINE, ON THIS COMMIT'S REGISTRIES**, by a byte-exact HEAD
      control that restored my bytes in a `finally`: identical failures with HEAD's registries,
      **introduced by this port: none**. `guard.doc-boundary` passes on the two runbooks (4/4). The
      `session-boundary` DRIFT(3) is the pre-existing one recorded at 3.5bb.


- [x] **3.5bl** **PROOF UPGRADE, not a port: the live tier is OPEN, and both 3.5bj and 3.5bk stop being
      refusal-only.** There was no blocker. `injectorConnected: false` on all three slots was not a wall --
      it was **a game that nobody had started**. Slot 2 was fully deployable the whole time: the game exe
      present, `MelonLoader` 414 files / 160.6 MB, `FusionRpg.Injector.MelonLoader*.dll` in `Mods/`, and
      `Mods\fusionrpg.cfg` already pointing at **`ServerUrl=http://127.0.0.1:5102`** -- the slot's OWN port.
      **Launched it and the injector connected in 20 seconds** (pid 49820, 975 MB working set), with the
      game's own log confirming `SignalR connected`, `Overlay view host ready`, and the SignalR reconnect
      + re-join + grant-rehydrate handshake. **I presented this as a blocker instead of investigating it,
      and presenting a repair as a block is the same error as presenting a measurement I had not taken.**
      **THE REAL RUN, WHICH IS THE PROOF 3.5bk DID NOT HAVE.** `ensure_live_lab_board` on :5102 returned
      `entered=True levelType=Advanture targetPtr=1AAF7C06320 plantPtr=1AAF7D0C480`, and
      `prove_status_l2_one.py --scenario status-l2-wither` completed a REAL scenario in **2.018 s**:
      `verdict: OK`, `cursor: 929154`, `attempts: 2`, `collectedEvents: 102`, counts
      `fx.state.started=1 debug.status.apply=0 debug.status=1`. **That is the fx-ONLY page -- the exact
      third planted page the contract suite pins, produced by the live path rather than by my fixture.**
      So the rule "`debug.status` alone is not enough, but started-OR-applied is" is now confirmed against
      the game, not only against a loopback server.
      **SIX SELF-SKIPPING LIVE CASES, so the proof lives in the suite and not only in this entry.** Three in
      each suite: the board returns a pointer that LOOKS like the injector's hex pointer (a stub cannot
      produce one, which is why this was unprovable before); a real scenario run yields a real verdict
      from a real stream; and -- for the library -- the search finds a real max id in a stream being
      written *as the search runs*, which a fixture cannot reproduce, plus a live-payload check that every
      payload is either parsed or NAMED unparseable, never silently null. **They SKIP, with a stated
      reason, when no injector is reachable** -- verified by running with the variable unset: 4 skip
      messages naming the reason, 0 failures. CI has no game, and a test that fails there is a test that
      gets deleted rather than fixed; a test that silently passes because it did nothing is worse.
      **AND THEY REFUSE TO FALL BACK.** The skip message reads "will not fall back to
      `http://127.0.0.1:5088`, which is the owner's own server". **:5088 does not answer on this machine
      at all**, so the 3.5bj incident -- the differential measuring the port against a default that
      resolved to a server nobody was running -- could only ever have produced SERVER-UNREACHABLE, and the
      live cases make that class of mistake impossible by construction rather than by a harness check.
      **MEASURED WITH THE GAME LIVE: 98 passed, 40 subtests**, across both suites, every pre-existing case
      still green alongside the six new ones.
      **WHAT IS NOW UNBLOCKED, BY COUNT, NOT BY FEELING: 18 of the 24 remaining files are live-tier**, and
      every one of them can now be proven on its real path instead of on a refusal. The six offline-tier
      files needed nothing. `prove-live-setup-skip.ps1` (25 lines, the smallest in the population) is now
      portable with a real run rather than a refusal-path proof.


- [x] **3.5bm** `scripts/prove-live-setup-skip.ps1` -> `gk-core/scripts/prove_live_setup_skip.py`.
      **POPULATION 24 -> 23.** A leaf, so the `.ps1` is DELETED and its exemption entry removed rather
      than widened to a glob that would match nothing. **0 disagreements** over four case groups, all
      against the **REAL game in slot 2 on :5102**: the acknowledgement compared FIELD BY FIELD for both
      methods (18 comparisons, `scenarioId` excluded because it changes per board and the exclusion is
      stated rather than applied silently); the refusal path on :5101, a real server with no injector; the
      method vocabulary, refused before any request by both sides; and the budget, as a declared
      difference. The two methods are asserted DISTINGUISHABLE, because a differential whose cases collapse
      into one answer is not measuring anything.
      **A REAL RUN FOUND A REAL BUG IN MY OWN TOOL, AND IT IS THE FOURTH OF ITS FAMILY.** The tool declared
      its OWN `Refusal` class, raised it from `check_health` and `skip_setup`, and `main` caught only the
      LIBRARY's class -- so INJECTOR-NOT-CONNECTED, the single most common condition this program meets,
      escaped `main` as a traceback and exited 1. **A refusal a caller cannot catch is not a refusal; it is
      a crash wearing the reason as a costume.** Both classes are caught now, and a case reads the SOURCE
      to assert it, because an omission compiles perfectly and only the text shows it. The same trap sits
      one scope out, in `acknowledge`, which has its own handler for the same reason.
      **MY CLAIM ABOUT THE BUDGET WAS WRONG, AND MEASUREMENT IS WHAT CAUGHT IT.** I asserted that
      `-TimeoutSec 0` produced an infinite read. It does not: the original's POST timeout is
      `$TimeoutSec + 5`, so the value is SHIFTED before it reaches .NET. Measured against the game:
      `0 -> 5s`, **`-5 -> 0s, which .NET defines as INFINITE`**, `-6 -> refused by PowerShell itself**. The
      infinite read is at **-5**, and `-6` is caught while `-5` is not -- so the dangerous argument sat
      exactly one step INSIDE the validation. Both the docstring and the refusal text state the measured
      arithmetic, and a case pins the three table lines AND the conclusion sentence, because the table is
      the evidence and the sentence is the finding.
      **SIX SURVIVORS NAMED TWO SUITE GAPS, and one of them was a REAL TOOL DEFECT.**
      *(i)* **The `ok: false` PATH WAS NEVER DRIVEN**, because the fixture answered 409 and
      `invoke_debug_post` RAISES on a non-2xx before the body is read -- so three surviving mutants lived
      in a branch no test reached, and an unproven branch is not a safe branch. The new case drives a 200
      with `ok: false`, and it found that **the refusal did not name the endpoint** while the 409 path did:
      two failures of the same endpoint, one naming it and one not. Fixed.
      *(ii)* **NO CASE CAPTURED THE TIMEOUT PASSED TO THE TRANSPORT.** The suite pinned the CONSTANT and
      the request BODY, but not the argument handed to `invoke_debug_post`, so removing `+ POST_SLACK` was
      invisible. Pinning a constant and pinning its USE are different claims; only the second was the
      defect the mutant represents.
      **ONE MUTANT WAS EQUIVALENT, AND THE DEAD CODE IT TARGETED IS DELETED RATHER THAN DEFENDED.** A
      branch re-worded a 4xx as "was refused by the server" while passing the rest through -- but the
      library's own refusal already carries the endpoint, the status and the server's FULL body, so the
      branch made the message strictly LESS informative. Deleted, and the mutant removed with it, because
      an equivalent mutant is a fact about dead code rather than about coverage.
      **MY OWN META-CASES WERE WRONG TWICE, IN THE DIRECTION THAT COSTS REAL COVERAGE.** The
      both-Refusal-classes case read `part.attr`, which for `lib.Refusal` is `Refusal` -- the bare class's
      name too -- so the tuple collapsed to one string and a correct implementation read as broken;
      `ast.unparse` keeps them apart. And the no-global-patch case correctly flagged a pointless
      `mock.patch.object(sys, ...)` of my own, which was removed rather than worked around, because a
      meta-case that is right about the code and gets bypassed is worse than none.
      **THE RETIREMENT CHECK EARNED ITS KEEP AGAIN, ON MY OWN EDIT.** It found a runbook telling a person
      to run `.\scripts\prove-live-setup-skip.ps1` -- a real invocation -- plus a plan doc naming the file.
      Both repointed in this change. **And it then flagged MY OWN corrected sentence**, because its rule
      matched the path SEPARATOR inside prose: `[\\/]prove-live-setup-skip\.ps1` fires on `/`, so
      "`scripts/prove-live-setup-skip.ps1`, retired 2026-09-29" scored as a dangling instruction. The rule
      is now POSITIONAL -- `pwsh -File`, a bare command at the start of a line, or a backticked path
      followed by a flag -- because a check that flags a correctly-updated sentence is one whose output
      cannot be acted on.
      **CONTRACT: 39 cases green (11 subtests), and green with the game live and green without it.**
      **FALSIFICATION: 37 mutants -- 37 KILLED, 0 SURVIVED, 0 BROKE-TOOL.**
      **COUPLINGS, in the same commit.** Exemption `live-diagnostic-scripts` 19 -> 18 entries; new owner row
      `prove-live-setup-skip-tool`, 531 boundaries, carrying the GLOB `scripts/prove-live-setup-skip.*`.
      **REACHABILITY, both directions**, including that `--deleted-paths` resolves the retired file to the
      same owner THROUGH the glob -- without it the deletion has no boundary at all, because the exemption
      that used to map it is gone. `guard-verification-boundaries` walks it (`verdict: OK`, 498 owners) and
      `guard.doc-boundary` passes on the runbook (4/4).
      **FENCE: `tasks/live-setup-skip-plan.md` was a GAP** -- no ACTIVE record claimed it -- and a
      retirement that repoints a plan doc cannot be done without touching it, so it joins the fence (1064
      paths) and the gap is disclosed.
      **THE REMAINING GUARD FAILURE IS PROVEN NOT MINE, ON THIS COMMIT'S REGISTRIES**, by a byte-exact HEAD
      control restoring my bytes in a `finally`: identical failures with HEAD's registries,
      **introduced by this port: none**. The `session-boundary` DRIFT(3) is the pre-existing one.


- [x] **3.5bn** `scripts/lib/DebugStatusApply.ps1` -> `gk-core/scripts/lib/debug_status_apply.py`. **POPULATION
      STAYS 23, and the one consumer says why.** `scripts/audit-status-vfx-identity.ps1` (240 lines) still
      dot-sources the `.ps1`, and it is ITSELF in the population, so this is a dependency order and not a
      deferral: porting a consumer first would mean reimplementing this module's four functions, which is
      the two-implementations defect. The exemption's exact path became the GLOB
      `scripts/lib/DebugStatusApply.*`, which still matches the LIVE `.ps1` and separately names the `.py`.
      **A REAL RUN FOUND A REAL FINDING, AND IT IS THE ONE THIS MODULE EXISTS TO SURFACE.** The apply
      endpoint ACCEPTS `statusId: "status-l2-wither"` (`{"ok": true, "queued": 1}`), and the resulting
      `debug.fx.state.started` payload carries **`statusId: "wither"`**. **Measured over 31 fx events on
      one run, zero matched.** So `Wait-StatusFxStarted`'s `$p.statusId -eq $StatusId` **cannot match for
      any `status-l2-*` id**, and its `$false` return is identical in three situations: the apply was
      refused, the fx never started, or the fx started under a different name. **The two namespaces are
      not the same vocabulary**, and the runbook already said "matching `payload.statusId`" -- so the
      instruction was wrong for every `status-l2-*` case and said nothing about it. The port reports
      `seenStatusIds`, so "no fx" is a diagnosis; the runbook now carries the warning.
      **AND THE DIFFERENTIAL MEASURES THE FINDING INSTEAD OF QUOTING IT.** An earlier version asserted the
      mismatch from a previous session, and its own output showed `seenStatusIds=[]` -- so the case had
      measured nothing. Case E now applies and waits and **FAILS if a run does not reproduce the
      mismatch**, which is the only thing that makes it evidence. And the fx is **intermittent** -- 31
      events on one run, 0 on the next, because it only fires while the target is alive -- so case E
      RETRIES four times. A case that fires once and fails when the game is quiet is a flaky case, and a
      flaky differential is worse than none, because its result depends on the board's mood.
      **0 disagreements** over five case groups, all against the REAL game in slot 2 on :5102: the
      pointer (compared as a real hex pointer, not for equality, because the two sides enter DIFFERENT
      boards), the original's OWN verdict on the live stream, the retry loop's boolean and try count, the
      clear, and the namespace mismatch.
      **A REAL BUG IN MY OWN TOOL, TWICE, AND BOTH FROM THE SAME CLASS.** The record's fields are
      camelCase because they are wire-shaped, and the CLI referenced `outcome.status_id` -- so the FIRST
      real CLI run raised `AttributeError`. And when I added `seenStatusIds` I made the four counters
      PROPERTIES while leaving them declared as `int` FIELDS, which the dataclass puts in `__init__`, so
      every construction raised `property has no setter`. A derived value must not also be a field. A case
      now reads the source and fails on a snake_case twin of a wire field, and the suite's own
      camelCase meta-case had to be SCOPED twice: it first flagged the library's legitimately snake_case
      `LabBoard.target_ptr`, then this module's own private sets, then a method name. **A meta-case that
      is wrong in the direction of noise is still noise.**
      **THE COUNTERS COUNTED OBSERVATIONS, NOT DISTINCT EVENTS, AND MY OWN SUITE CAUGHT IT.** One fx
      event inside the poll window was re-read on every poll and reported `fxEvents: 4` -- a counter that
      reports four when there was one is worse than no counter, because it looks like evidence. The
      original returned a boolean and never counted, so **this is a defect the port introduced with its
      own instrumentation.** The four counts are now properties over sets of event ids.
      **THE TWO-BUDGET MISMATCH IS NOW VISIBLE.** `$DurationMs = 6000` is applied and `$TimeoutMs = 2500`
      is waited, and in the original those numbers sit in DIFFERENT FUNCTIONS, so a reader could not see
      the relationship. Both are recorded on every result and a case asserts the values -- through
      `to_json()`, not the attribute, because a value present on the object and absent from the report is
      not reported at all. A first version asserted the attribute, and two mutants survived.
      **SEVEN SURVIVORS NAMED SIX REAL GAPS, and one was a BROKEN MUTANT OF MINE.** Never driving a
      **non-dict payload** (`payload.get` on a list raises, so the `isinstance` skip is load-bearing);
      never observing the counters **across two polls** (every case either matched on the first poll or had
      no events); never driving a payload with **no statusId**, so nothing pinned that an absent id is not
      invented as `"unknown"`; asserting the budgets as **attributes** rather than through `to_json()`; and
      the finding's **HEADING** -- deleting it left the body, both ids and the sample size, so a case
      pinning only the content could not see the removal. The seventh was mine: the "never polls again"
      mutant incremented `polls` twice and returned, so `polls >= 2` passed -- it removed nothing, it
      misreported the count, and a harness defect was being read as tool coverage.
      **THE RETIREMENT CHECK FOUND THREE DOCS TO REPOINT** -- a captures README, the debug-pipeline
      runbook (twice, once as a link and once as a PowerShell block a person would run) and a plan doc's
      file table -- and then had to be taught THREE things. It flagged my own correctly-updated note
      because the sentence **wraps** and the word "retired" is on the NEXT line, so a record must be
      judged by its PARAGRAPH while a COMMAND stays line-scoped. It had to be taught to tell a **LIVE
      CONSUMER** (a tracked `.ps1` that dot-sources the library, disclosed above) from a **DANGLING DOC**,
      because flagging the consumer would force this port to also port a 240-line script, which is the
      scope-shrinking the programme forbids. And the earlier path-separator rule, from 3.5bm, applies here
      too. **A check that flags a correctly-updated sentence is one whose output cannot be acted on.**
      **CONTRACT: 46 cases green (9 subtests), plus one live case that SKIPS with a stated reason when no
      injector is reachable and REFUSES to fall back to the owner's port. FALSIFICATION: 46 mutants --
      46 KILLED, 0 SURVIVED, 0 BROKE-TOOL.**
      **COUPLINGS, in the same commit.** Exemption `shared-script-libraries` 4 -> 5 entries, the exact path
      becoming the glob and the stated reason unchanged; new owner row `debug-status-apply-tool`, 532
      boundaries. **REACHABILITY, both directions**, including that the still-live `.ps1` maps to the SAME
      owner as the module, so the port order has one boundary rather than two. `guard-verification-
      boundaries` walks it (`verdict: OK`, 499 owners) and `guard.doc-boundary` passes on the runbook
      (4/4).
      **THE REMAINING GUARD FAILURE IS PROVEN NOT MINE, ON THIS COMMIT'S REGISTRIES**, by a byte-exact HEAD
      control restoring my bytes in a `finally`: identical failures with HEAD's registries,
      **introduced by this port: none**.


- [x] **3.5bo** `scripts/prove-actor-hud-live.ps1` -> `gk-core/scripts/prove_actor_hud_live.py`.
      **POPULATION 23 -> 22.** A leaf, so the `.ps1` is DELETED and its exemption entry removed rather than
      widened to a glob that would match nothing. This is the ONLY script in the population that does not
      talk to the game directly -- it drives the web project's live Playwright project -- so the
      differential ran **both sides really launching Playwright** against the real server and game in slot
      2 on :5102. A differential that stubbed the E2E would have compared two things that never touched
      the thing under test. **0 disagreements.**
      **THE E2E IS FAILING ON THIS MACHINE, AND THE ORIGINAL CANNOT SAY WHY. THE PORT NAMES THE CAUSE, AND
      THE CAUSE IS MEASURED.** The web helper `pollBoardActorHud` inspects **only** `debug.board-stats`
      events -- it `continue`s past every other kind -- and waits **45 seconds** for one. **MEASURED:
      after a shield demo and two status applies (all three accepted, `{"ok": true, "queued": 1..3}`) the
      board emitted `shield.granted` x3, `debug.status` x2, `debug.status.resisted` x2, `debug.actor-hud`
      x1 and `debug.effect.board-snapshot` x2 -- and ZERO `debug.board-stats`.** So the poll cannot
      succeed, it spends its 45 seconds, and **Playwright's default `beforeAll` hook timeout is 30
      seconds**, so the hook dies first. The original's ENTIRE diagnostic output is
      `"beforeAll" hook timeout of 30000ms exceeded.` -- a symptom that reads like a hang and says nothing
      about the event stream. The port reports the polled kind, whether it was seen, which kinds the board
      DID emit, whether the board is alive, both budget numbers, and **that the fix belongs to the web E2E
      helper and not to this script**. The differential MEASURES this and **fails if a run does not
      reproduce it**, so the claim cannot outlive its refutation -- and it corrects one of my own
      overstatements: the original's output DOES contain the string `pollBoardActorHud`, inside
      Playwright's source excerpt for the failed hook. So "it mentions none of this" would have been false.
      The accurate claim is that it reports **no diagnosis**, and that is what is tested.
      **A REFUSAL THAT LIES, AND THE RUN THAT CAUGHT IT.** `npm` is a `.cmd` BATCH SHIM on Windows;
      `subprocess.run(["npm", ...])` raises FileNotFoundError while PowerShell resolves it fine -- so the
      ORIGINAL RAN and the first version of this port refused with `E2E-SPAWN-FAILED` claiming npm was not
      on PATH, on a machine where npm demonstrably works. Resolved through `shutil.which`, which
      understands PATHEXT, and the RESOLVED PATH is reported (`C:\nvm4w\nodejs\npm.CMD`) so a reader can see
      which npm ran.
      **THE OTHER TWO DEFECTS ARE THE ORIGINAL'S AND BOTH ARE FIXED WITH THE E2E STILL RUNNING ONCE.**
      `npm run test:e2e:live` ran with **no timeout and no capture** -- and a Vite dev server plus a
      project that polls for an event the board does not emit is exactly the shape that hangs forever while
      looking like progress. Now `subprocess.run(capture_output=True, timeout=...)` with a reported bound.
      And the `lawn.worldHud` setting was set inside a `catch` that only `Write-Warning`ed, so a failed
      setting produced an E2E whose HUD assertions could not hold -- **a SETUP failure reported as a HUD
      failure**. The setting is now REQUIRED with its own named refusal, and a case proves the E2E never
      runs after it failed.
      **`Set-Location` WAS CALLED TWICE, INCLUDING ONTO THE WEB TREE, AND NEVER RESTORED.** The subprocess
      gets an explicit `cwd` and a case asserts this process's own directory is unchanged after `main()`.
      **THE `catch` ALSO CONFLATED "SERVER UNREACHABLE" WITH EVERY OTHER FAILURE** -- a timeout, a 500 and a
      malformed body all printed "Server not reachable" and exited 1. Each is named separately now.
      **A REAL API DEFECT MY OWN SUITE CAUGHT:** `check_server(base_url, skip)` gave `skip` no default, so
      the obvious call raised `TypeError`. A flag with an obvious default is a flag with the wrong
      signature.
      **SIX SURVIVORS NAMED FIVE REAL GAPS, and the sixth CANNOT APPLY ON THIS HOST.** The injector refusal
      was asserted for the SKILL POINTER but not for the URL, so a mutant that removed the URL from the
      first message fragment survived -- the skill lives in the second fragment, so the check could not see
      it, and the refusal named a condition without saying which server refused. The diagnosis TEXT was
      unpinned in three places -- the kinds the board emitted, the two budget numbers, and the note about
      who owns the fix -- because every existing case checked the structured `diagnosis` and never the
      prose. And the docstring CLAIM was unpinned: changing "does not emit that kind at all" to "sometimes
      does not emit it" left the kind, both budgets and all three measured kinds intact, so a case pinning
      the CONTENT could not see the CLAIM soften. The sixth was `shutil.which("npm")` SUCCEEDING here, so
      the `npm.cmd` fallback is unreachable on this host: NOT-APPLICABLE, the fallback KEPT because a host
      with only the `.cmd` on PATH is real, and the measurement recorded.
      **FIVE FILES REPOINTED, AND ONE DELIBERATELY NOT.** The retirement check found eight references
      across six files. Five were repointed in this change. **The sixth,
      `tasks/backlog-clean-up-todo.md`, carries another stream's UNCOMMITTED work** -- it is dirty in the
      working tree -- so it is **DISCLOSED as out-of-scope and NOT edited**, because editing it would
      DESTROY that work (which has happened in this program) and blocking the port over a citation would
      leave the population in place, which is the worse trade. The owning stream repoints it. The check
      learned to make that distinction itself, from a rule rather than an allowlist.
      **CONTRACT: 39 cases green (5 subtests), plus live cases that SKIP with a stated reason when no
      injector is reachable and REFUSE to fall back to the owner's port. FALSIFICATION: 45 mutants --
      45 KILLED, 0 SURVIVED, 0 BROKE-TOOL.**
      **COUPLINGS, in the same commit.** Exemption `live-diagnostic-scripts` 18 -> 17 entries; new owner row
      `prove-actor-hud-live-tool`, 533 boundaries, carrying the GLOB `scripts/prove-actor-hud-live.*`.
      **REACHABILITY, both directions**, including that `--deleted-paths` resolves the retired file to the
      same owner THROUGH the glob. `guard-verification-boundaries` walks it (`verdict: OK`, 500 owners) and
      `guard.doc-boundary` passes on the runbook (4/4).
      **FENCE: four GAP files added and disclosed** (1073 paths) -- the retirement cannot repoint a
      reference without touching the file it lives in, and no ACTIVE record claimed any of them.
      **THE REMAINING GUARD FAILURE IS PROVEN NOT MINE, ON THIS COMMIT'S REGISTRIES**, by a byte-exact HEAD
      control restoring my bytes in a `finally`: identical failures with HEAD's registries,
      **introduced by this port: none**.

- [x] **3.5av** The population is now split by what each file needs in order to be PROVEN.
      **SUPERSEDED 2026-09-29 by 3.5bd — the split below was measured against a blocker that did not
      exist, and the "31 blocked" figure is WITHDRAWN.** The original reading was: **36 measured,
      5 provable on this machine, 31 blocked on a live slot**:
        * **PROVABLE HERE (server-only):** `scripts/lib/KeepverseRoots.ps1` (52),
          `scripts/regen-class-system-baselines.ps1` (203), `scripts/smoke-player-pack.ps1` (161),
          `scripts/test-substrate-leak-alarm.ps1` (118),
          `tasks/reports/f13-schema-upgrade-proof.ps1` (177).
        * **BLOCKED (needs the running game):** the other 31, which reference an injector, a game
          install, or both.
      **THE BLOCKER AS ORIGINALLY STATED WAS A CHECK THAT COULD NOT FAIL, READ AS ONE THAT HAD RUN.**
      The original text here said: `FUSIONRPG_GAME_POOL` and `FUSIONRPG_GAME_SOURCE` are both empty and
      `scripts/live-slot.ps1` refuses with "no pool root" — and concluded the live tier was unreachable.
      **Both facts were true and the conclusion was wrong.** The pool exists at
      `H:\Games\.fusionrpg-pool`; all three slots are `ready` and were verified on 2026-09-26, on ports
      5101/5102/5103; and with `FUSIONRPG_GAME_POOL` set, `live-slot.ps1 -Status` reports "free 3" and
      exits 0. The two variables were unset in the tool shell and the check READ THE VARIABLES instead of
      LOOKING FOR THE POOL, so it confirmed a condition nobody was waiting on. Corrected in 3.5bd.
      **THE CLASSIFIER WAS WRONG TWICE BEFORE IT AGREED WITH ANYTHING, AND BOTH ERRORS MADE THE
      ACTIONABLE COUNT TOO HIGH.** First it read only each file's own text, so
      `prove-status-l2-one.ps1` landed in the server-only group — but that file dot-sources
      `lib/LiveLawnSetup.ps1`, whose `Ensure-LiveLabBoard` needs an injector-connected server. A
      requirement a script INHERITS through a dot-source is a requirement it has. Second, the dot-source
      pattern was `\.s\s+` when the text is `. (Join-Path` — a pattern that never fired reported the
      population UNCHANGED, which is indistinguishable from agreeing with the previous run. The
      corrected split is 5 / 31, down from a first reading of 8 / 29.

- [x] **3.5ah** `test-sharded` (192 lines) — the first INFRASTRUCTURE tool of the program rather than a
      registry guard, so it carries no `enforcement-registry` row by design; what it needed was the
      boundary owner row, and census found that `mutate` and `coverage` have **no owner row at all**,
      a mapping gap recorded against Wave 2 rather than papered over here. Differential: on the real
      repository in replay mode both implementations exit 1, report the same shards with the same
      zero-test counts, and emit the same findings with the verdict strings byte-preserved **including
      the em-dash** — which the first draft ASCII-fied, so a substring assertion on the tail would
      have reported the change as passing. Declared divergence: findings moved to stderr while the
      per-shard readings stay on stdout, so each stream is in manifest order and a `2>&1` merge shows
      them in two groups. Contract suite: 36 tests. Falsification: **20/22 mutations killed, 1
      MEASURED EQUIVALENT, 0 survivors, 1 anchor-miss corrected** — see below.
      **THE DIFFERENTIAL AND THE C# SUITE CAUGHT A REAL BUG, AND IT SURFACED AS A FALSE PASS.**
      `analyse()` scanned `<temp>/**/*.trx` instead of `<temp>/<shard id>/**`, so every shard read every
      other shard's ids. The overlap case still found one id claimed twice, so its assertion was
      satisfied **for the wrong reason**, while the two cases asserting a shard's OWN count went red.
      A test that passes because the tool over-reports is worse than one that fails, because it stops
      looking; `shards_read_ONLY_their_own_results` exists so it cannot pass that way again.
      **THE EMPTY-FILTER REFUSAL CHECKED THE WRONG STRING, AND WAS VACUOUS WHILE LOOKING CORRECT.**
      `main` refused a filter it had already had the extra filter ANDed onto, so a prefix-less named
      shard produced `()&(Category!=Heavy)` — non-empty — and the run proceeded to hand VSTest a filter
      that means "no filter", running the whole suite once per shard and reporting success. The refusal
      moved INTO `shard_filter`, which checks the shard's OWN filter, so a caller that builds a filter
      by hand gets the same guard `main` does. Two mutants — removing the refusal, and patching the
      join so an empty prefix list yields a match-everything glob — both SURVIVED the first pass and
      were killed only by the new end-to-end case.
      **THE SUITE'S OWN ANTI-POWERSHELL GUARD COULD NOT SEE A POWERSHELL INVOCATION.** It stripped all
      string literals, and the three tokens that make `subprocess.run(["powershell", ...])` a shell-out
      ARE the string contents. The same claimed-vs-implemented shape `guard-sim-fabrication` had. The
      fix is not a better exemption list but the right distinction, which `ast` makes exactly: a bare
      `Expr` whose value is a string is a **docstring**, and a string nested in a call, list, assignment
      or f-string is **code**. So `.ps1` is no longer banned outright — it is a **DECLARED** set with a
      reason per entry, because this tool legitimately reads the unported `test-fast.ps1` and names its
      own predecessor in the CLI description. A fourth unexplained `.ps1` fails the guard.
      **THE SCRATCH DIRECTORY WAS UNTESTABLE AS WRITTEN, AND THAT IS WHY A SWALLOWED DELETE SURVIVED.**
      The deletion sat inline in `main`, reachable only through a real `dotnet build` plus four shard
      processes, so the suite could not produce a failed delete and could not tell a propagating
      failure from a swallowed one. `scratch_root()` is a context manager with the base directory as a
      parameter, and the new case produces a genuinely failing delete by holding a file handle open.
      That is the shape the repo's 65.5 GB temp leak was made of, so it is pinned rather than assumed.
      **A FENCE GAP, NOT A CROSSING.** The boundary checker refused `scripts/test-sharded.ps1` as
      outside the session fence. A path no active record claims is a GAP and is added; one another
      ACTIVE record claims would be a crossing, disclosed and never taken. The claim scan is re-run
      inside the edit that adds the paths, so the distinction is verified at the moment it is acted on
      rather than remembered from an earlier scan.
      **`--no-incremental` IS NOT A `dotnet test` SWITCH, AND IT SILENTLY SKIPPED TWO VERIFICATIONS.**
      `MSBuild : error MSB1001: Unknown switch` goes to the log and the run produces no test output, so
      it reads as "no failures" rather than "no tests ran". The correct incantation is
      `dotnet build --no-incremental` followed by `dotnet test --no-build`, and the shard suite's
      **14/14** is the first figure produced by a run that actually executed.
      **PRE-EXISTING FAILURE, PROVEN NOT MINE BY A BYTE-EXACT CONTROL.**
      `SplitCoreVerificationMappingTests.Planner_resolves_representative_split_core_files_to_area_owners_not_residual`
      fails inside the scoped run, and it is in the file this port edits, so the earlier reproduction was
      not good enough. The registry was reverted to the **HEAD blob as raw bytes** with its SHA checked
      before and after — the first attempt piped `git show` through `Out-File -Encoding utf8`, which can
      add a BOM and rewrite line endings, so the file under test was not necessarily HEAD. Result: the
      test fails identically with the edit and without it. The working copy is 6629 bytes larger than
      the blob purely as CRLF; the **content** diff is the four registry lines and nothing else.
      **A REAL END-TO-END RUN, NOT ONLY REPLAY.** Replay skips the build and the N concurrent
      processes, so it proves resolution, filter construction and the analysis but not the part the
      tool exists for. Run against `FusionRpg.Data.Tests` with no replay: **4 shards, every shard exit
      0, 1893 tests, zero overlaps, no empty named shard, 144s wall.** The per-shard walls are the
      evidence that the process boundary is real rather than decorative -- the three named shards
      finished at ~52s each while `rest` ran to 133s, which is the whole point of splitting on a
      project whose stores serialise on a process-global mutex. The `xUnit.MaxParallelThreads=N`
      runsettings argument the original passed after `--` is accepted, so it is preserved rather than
      re-derived. Wall and test counts are READINGS, re-measured each run, not constants.

- [x] **3.5ag** `guard-sim-fabrication` (569 lines) — the LAST registry guard on PowerShell, and
      the one whose private scanner was named after a policy it did not implement. **58 fixtures:
      56 correct against their own stated expectation, 54 byte-identical in exit code, report and
      finding SET, 2 declared divergences (the two refusals the original had no name for), 0
      unexplained.** Contract suite: 41 tests. Falsification: **21/21 mutations killed by a real
      assertion, 1 MEASURED EQUIVALENT, 0 survivors, 0 collection-only kills, 0 could-not-apply.**
      **THE PRIVATE STRIPPER'S NAME AND COMMENT BOTH OVERSTATE IT, AND THE PORT USES WHAT THE CODE
      DOES.** The helper is called `Strip-CommentsPreservingLayout` and its comment says it blanks
      string/char literal INTERIORS in place. It does not: the literal branch only ADVANCES the
      index past the closing quote and writes nothing. Measured, not inferred — on
      `ScenarioVocabulary.cs` the blanking policy parses **0** `ScenarioOp` rows, because it deletes
      the quotes the table's own regex needs, and the comment-only policy parses **5**, the table's
      real size. So the port uses `cscan.strip_comments_preserving_layout`. Carrying the name forward
      would have imported a scanner one policy STRONGER than the guard ever was — the exact failure
      `cscan.py` warns about in its own header, a scanner that quietly gets stronger and turns a
      passing guard red for reasons nobody can point at. The port refused `VOCABULARY-EMPTY` on its
      first real run, which is what surfaced it.
      **TWO BRANCHES CANNOT FIRE, AND BOTH ARE PINNED AS DEAD RATHER THAN DELETED.** (1) The
      `declared route's surface is not the op's surface` check is an `elif` behind
      `route == the op's own method+route`, and a route built from the op's own method and path cannot
      have a different surface. (2) The registration regex ends at the COMMA after the path, so the
      span anchor is the comma and not the opening parenthesis; scanning from a comma for a balanced
      pair returns at the first closer — the end of `(RpgStore store)` — so
      `guard defect: unbalanced handler span` is unreachable. It is also LUCKY: the span it returns
      happens to contain the parameter list, which is why `TakesStore` works at all. Deleting either
      would make a later fix look like a regression, so a test asserts each stays dead.
      **`RpgStore` INSIDE A STRING LITERAL STILL SETS THE STORE FLAG, and that is pinned in BOTH
      directions.** The scan runs on the literal-PRESERVING view, so a route whose handler only
      mentions the type in a log message is reported. Tightening it to the blanking view would fix
      the false positive and would also stop matching the real parameter, whose type annotation IS a
      literal. Neither view is a clean answer; the original's choice is kept and pinned, and a
      separate test pins that a `RpgStoreFactory` parameter is NOT the store, which is the word
      boundary's own rule.
      **THE 8.3 DEFECT, AND `relative_to` IS NOT THE FIX.** The original builds each path as
      `$file.FullName.Substring($Root.Length)` behind a `StartsWith($Root, OrdinalIgnoreCase)` test.
      Under an 8.3 short-name root the enumerator returns the LONG spelling and the slice removes the
      SHORT form's character count, so the reported path is CHOPPED — measured in the differential,
      where the original prints a root-prefixed path and the port prints the clean relative one.
      Porting to `Path.relative_to` turns that silent corruption into a loud `PATH-OUTSIDE-ROOT`
      refusal, which is strictly better and STILL WRONG, because a guard that refuses an ordinary temp
      tree cannot be tested. So the two spellings are reconciled twice and independently:
      `GetLongPathNameW`, and an `os.path.samefile` walk. **Disabling the first changes no answer —
      MEASURED, and classified EQUIVALENT rather than rounded away** — and both are kept because they
      fail differently: one needs the path to exist, the other needs an ancestor that does.
      **A `--scenario-dir` OUTSIDE `--root` IS LEGITIMATE, and the first version of the port REFUSED
      IT.** The C# bite-proof test plants its violation in a temp directory and passes the REAL
      repository as the root, so the planted file is genuinely not under it. The original permitted
      that (its `StartsWith` test failed and it reported an absolute path); the port raised
      `PATH-OUTSIDE-ROOT` and failed its own C# suite. A second base is now tried before refusing.
      **THE DIFFERENTIAL NEEDS THE PORT RUN TWICE, and getting that wrong reported ZERO agreement.**
      An early revision compared the original's PROSE against the port's `--json` envelope and
      reported `0 byte-identical` on all 58 cases — a number that reads like total failure and was
      really a harness defect. The same lesson as the previous port, written in its docstring and then
      walked into here. Prose for the comparison, JSON for each case's own expectation.
      **A PowerShell `[regex]::Replace` DELETED SIX `Assert.Contains` LINES INSTEAD OF REWRITING
      THEM.** The script-block overload resolved to the STRING-replacement overload and every match was
      replaced with nothing. Caught by reading the file back rather than by the diff, restored from
      HEAD, and redone as exact full-line replacements that assert each line occurs exactly once.
      Then the same class of error as the previous port: the five planted-violation assertions moved
      to `stdout + stderr` while three tests still destructured with a discard, so the file did not
      COMPILE — caught by a build run in its own step before the commit.
      **THE ALLOWLISTS ARE PINNED WHILE THE COUNTS ARE NOT.** The two allowlists are closed
      registries a human changes by review, and rule 6 makes a stale entry a violation, so their
      MEMBERSHIP is the contract and is pinned exactly — including `test.expedition.due`, which is
      RETIRED and stays only so the RS4 planted-violation test can still reach the notes rule. The
      readings are the opposite and are range-checked only.
      Couplings: registry row repointed; owner row carries `scripts/guard-sim-fabrication.*` as a
      GLOB and — unlike its predecessor — now carries `guards: [sim-fabrication]`, which had been an
      empty list, so the guard is selected for its OWN source. Three reachability proofs, including
      `--deleted-paths` mapping the retired `.ps1`. The sweep rewrote 8 lines across 3 documents; one
      of them was a fence GAP, checked against every active record before being added.
      `audit-doc-citations --strict` 0 HIGH over 26,037 citations. **0 of 29 registry guards are now
      on PowerShell.**

- [ ] **3.6** Every ported guard's verdict string is byte-preserved — 22 `Assert.Contains` on guard
      stdout depend on it, and `FunnelDeltaGuardTests` asserts the offending **symbol** name
- [ ] **3.7** `guard-actor-hub`'s six allowlist arrays are transcribed literally, per-entry provenance
      included; a tidy-up silently changes what the guard permits

## Task 4: Coupled guard groups

- [x] **4.1** `lib/SourceText.ps1` (retired) + `guard-battle-responsibility` together — the lib has exactly one
      consumer, so a split strands it
- [ ] **4.2** Collapse the three PowerShell copies of the comment-stripping routine
      (`guard-single-writer:76`, `guard-test-substrate`, and the existing
      `guard-vocabulary-mirror.py:55`) into one Python module
- [ ] **4.3** `guard-generated-seed` + `guard-tuning-immutability` + `guard-repo-boundary` together —
      they share the `-BaseRef`/`-Range` convention by documented agreement, and
      `guard-generated-seed` alone owns the registry `args` / `{ciRange}` mechanism and the
      `release.yml:97` direct call
- [ ] **4.4** `guard-bench-compile` + `guard-injector-compile` together — one copies the other's shape
      by its own header
- [ ] **4.5** The high-fan-out four: `guard-dal` (16 probes), `guard-class-system` (13 tests + 5
      `tools/*` programs, **not in CI** so breakage there is invisible), `guard-secondary-no-unity`
      (9), `guard-power` (6)
        **LANDED as 3.5ag.** Its private scanner was named after a policy it did not
        implement, so the port had to MEASURE which policy it was before choosing a shared
        one; and its `declared route's surface` and `unbalanced handler span` branches both
        proved unreachable and are pinned as dead rather than deleted.
- [x] **4.6** `guard-sim-fabrication` (446 code lines, 28 `param()` switches) as the **reference
      implementation** of the shared scanner, not as a solo lane
- [ ] **4.7** `guard-debug-scope` with `guard-single-writer` — its own header states the flat-regex
      technique cannot isolate a multi-line handler and leans on the other guard's scanner
- [ ] **4.8** `guard-test-substrate`'s ratchet baseline **file format** is preserved: `path : reason`,
      split on `\s*:\s*` with `maxsplit=2`, and a path containing `:` breaks it.
      `DataTestStoreTests.cs:136` reads it.
- [ ] **4.9** `guard-narrative` — rewrite `CommittedMap()` to read a data file it owns, and widen the
      `guard-narrative*.ps1` glob in `verification-boundaries.v1.json`, which is already going vacuous
- [x] **4.10** `guard-test-content-root` — six helpers implement a real C# argument parser; this is a
      parser port, not a regex port, and the parser is load-bearing for two Python tools' docstrings
      **LANDED as 3.5af.** The parser is a top-level-comma split with paren/bracket depth tracking,
      so `Path.Combine(Path.Combine(a, b), c)` is ONE call and not three - pinned by
      `a_nested_Combine_is_one_call`, because a flat comma split turns the inner call into a
      top-level argument and invents a walk out of an ordinary combine. The load-bearing claim turned
      out to be about the guards that cite this one's findings rather than about its own prose, and
      the C# execute site the census missed is why a 'lightest coupling' is never zero work.

## Task 5: Keystone tools (last)

- [ ] **5.1** `lib/VerificationBoundaries.ps1` → Python, with **all three** consumers in the same
      change: `verify-change` (dot-sources it), `guard-verification-boundaries` (dot-sources it), and
      the tests that read `$Script:EnforcedRoots` **textually and rewrite it**
- [ ] **5.2** `VerificationBoundaryWorkflowTests.cs`'s **9** `File.Copy` sites repointed, or the
      temp-root tests throw `FileNotFoundException` before the guard is ever exercised
- [ ] **5.3** `guard-verification-boundaries`'s literal PowerShell expression
      (`"@('focused', 'module', 'seam', 'full') -notcontains $boundary.level"`) replaced by something
      machine-readable, and the test that pins it updated
- [ ] **5.4** `session-boundary-check` — per the Task 0.8 ruling; its `$validModes`/`$validStatus`/
      `$required` arrays are read by `gk-core/tests/tools/test_program_status.py:311-327`
- [ ] **5.5** `verify-change.ps1:43-50` stops regexing `$Filter = "…"` out of `test-fast.ps1`'s source;
      the "default profile filter lives in exactly one place" contract survives as a real API
- [ ] **5.6** `gk-core/tests/tools/test_program_status.py` repointed at the ported files — it also reads
      `accept_lane.py`'s `ACCEPTANCE_VERDICTS` tuple (it was the retired `accept-lane.ps1`'s `$AcceptanceVerdicts`; note the ported tool is spelled `accept_lane.py`, underscore, not `accept-lane.py`) by name today
- [ ] **5.7** `test-fast`, `test-sharded`, `publish-player`, `mutate`, `coverage`, `run-guards`
- [ ] **5.8** `test-substrate-leak-alarm`'s `[scriptblock]$Run` → argv, with **both** CI call sites
      updated in the same commit. **Owner confirmation of this assumption is still outstanding.**
- [ ] **5.9** The five `gk-core/scripts/lib/*.ps1` → Python, with all six dot-source sites restructured (a
      `.ps1` cannot dot-source a `.py`)

## Task 6: Live tier (owner's bar: a real live run)

- [ ] **6.1** Fix the pool env contract: `FUSIONRPG_GAME_POOL`/`FUSIONRPG_GAME_SOURCE` are unset and
      the deploy falls back to the owner's install, so the pool guard **cannot fire** — the exact
      incident class it was written for
- [ ] **6.2** Remove the hardcoded install path from the ported deploy and from `restart-game.ps1`;
      a committed default install path is forbidden
- [ ] **6.3** Reconcile `live-slot`'s `-PoolRoot` flag with the deploy's env-only reading — the two
      halves of one protocol currently disagree on how the pool is named
- [ ] **6.4** Port `live-slot`, `lane-server`, `game-lock` — and update the slot-connection proof
      harness **in the same change**, since it invokes them by filename
- [ ] **6.5** One real end-to-end slot-connection run as the gate (~4 min at the measured 58 s deploy)
- [ ] **6.6** For the nine scripts with an existing Python equivalent in
      `gk-fusion/tools/live_test/live_test/scenarios/`, make the Python pack hard-assert parity, then delete the
      `.ps1` — the rule `docs/runbook/live-test-ssot.md:530` already states
- [ ] **6.7** Port the remaining live scripts, grouped into shared slot sessions
- [ ] **6.8** Run every live port against the real game. **Merge is gated on the run, not the port.**
- [ ] **6.9** Record as **partially provable**, not proven: visual claims that need a human eye;
      perf/soak verdicts that need a machine with no other game running; negative lock branches that
      need a second live session; anything needing a legal-game interop read outside the pool
- [ ] **6.10** Fix `wait-for-deploy.ps1`'s unscoped process check — it passes if **any** game runs on
      the machine, including another lane's
- [ ] **6.11** Move the eight live scripts that overwrite a **tracked** repo file on every run to
      gitignored session output, with the tracked path behind an explicit flag. Under a
      never-`git add -A` rule with parallel lanes this is a live collision source.

## Task 7: CI shell `pwsh` → `bash`

- [ ] **7.1** Decide the exit-check question with the owner: the ~207 `$LASTEXITCODE` lines are pinned
      by five C# guard tests and deleting them is **160 violations**. Keeping each line verbatim as an
      inert comment satisfies the ruling with zero guard churn; amending the guards is a
      larger owner-sign-off change.
- [ ] **7.2** Flip all 54 steps, or gate the 19 that invoke a `.ps1` on that tool's port landing
- [ ] **7.3** One Python tool with three labels for the three `resolve range` algorithms — they are the
      same algorithm with three message texts, and the nightly variant has **no** pull-request branch,
      so a shared mode-guess would be wrong
- [ ] **7.4** The self-referential `Select-String` filter: `|| true` is mandatory (a bare pipeline
      whose last `grep` finds nothing aborts the step under `-e -o pipefail` and turns a passing CI
      red), and the third filter is required or the step fails on its own grep line
- [ ] **7.5** The `try`/`catch` ref-prep step → `if`/`elif`/`else`; a command in an `if` condition is
      exempt from `set -e`, which is what keeps the catch path reachable
- [ ] **7.6** The zip/hash step: `Compress-Archive` puts contents at the archive root and writes
      backslash entry names. A replacement must reproduce both or every extraction path changes — and
      this touches a **shipped download**, so it needs an owner decision, not a silent swap
- [ ] **7.7** `Set-Content -NoNewline` must become `printf`, not `echo`, or the published `.sha256`
      bytes change
- [ ] **7.8** Every step that throws on a **condition** rather than an exit code is ported by hand:
      the superset contract, the profile filter, the i18n diff, the web lockfile, the release-gate
      early exit, and the two range validators
- [ ] **7.9** `ci.yml:440`'s comment is **rewritten**, not just the shell: its stated reason ("guard
      scripts use `exit`, so a shared pwsh block could make one unreachable") is a `pwsh` fact that is
      false under `set -e`
- [ ] **7.10** Confirm `shell: bash` actually exists on the `runs-on:` image before relying on it

## Task 8: The citation sweep

- [ ] **8.1** **Do not validate this sweep with `audit-doc-citations.py` at its default scope.** It
      reads only tracked `.md`, only backticked paths, blanks fenced code blocks (where most real
      invocations live), and exempts `AGENTS.md`/`CLAUDE.md`. `--scope ./` sees every markdown file and
      still sees **zero** contract scans
- [ ] **8.2** Sequence by blast radius, not count: the `Directory.Build.targets` path, the 29 registry
      rows, the 51 boundary rows, the 27 contract scans, the ~40 repo-root probes, then prose
- [ ] **8.3** Rename a registry row and its file in the **same commit**, for all 29, plus the 16
      `gen-*` boundary rows. A partial change is worse than none: the runner throws
      `guard script missing`, the boundary guard throws `script file missing`, and the two globs go
      *vacuously green*
- [ ] **8.4** Never rewrite `.claude/cmdc-agents/acceptance/*.json` — they are SHA-keyed verdict
      records and editing a recorded `command` falsifies the evidence
- [ ] **8.5** Never hand-edit the generated `tasks/ip-censor/plan.json` corpus; fix the generator and
      regenerate
- [ ] **8.6** Review the **planned-but-nonexistent** `.ps1` files individually — a blind sweep would
      silently mint `.py` proposals for guards that do not exist yet
- [x] **8.7** `docs/guide/mechanisms/_gen-stubs.ps1` — deleted 2026-09-26. The earlier reason recorded
      here was **wrong**: its path is in `gk-core/scripts/vocab-rename/identity-rename.v1.json`'s exclude
      list, but the `VocabRenameTests` assertions are a **pure glob predicate over path strings**
      (`gk-core/scripts/vocab-rename.py:100-103`), not an existence check, so the delete breaks nothing.
      The file was superseded dead data: its own header forbids re-running it and `_render.py`
      (already Python) renders all 66 mechanisms from `_content/*.json`
- [ ] **8.8** Leave the machine-local, untracked `.kilo/setup-script.ps1` alone
- [ ] **8.9** The sweep validator is `dotnet test gk-core/tests/FusionRpg.Guard.Tests` **plus** an MSBuild parse
      of the three injector host projects — not the citation audit
- [ ] **8.10** Fix prose that names a deleted tool, or replace the citation with a note; a doc pointing
      at a missing file is a real defect

## Task 9: Close

- [ ] **9.1** `git ls-files '*.ps1' '*.bat' '*.cmd'` returns **nothing**
- [ ] **9.2** Every new tool has a docstring saying **why** the PowerShell form was retired, so the
      rationale survives the deletion
- [ ] **9.3** Every new tool is importable and unit-tested with `python -m unittest`
- [ ] **9.4** No new `.ps1` was written at any point
- [ ] **9.5** A fresh clone passes: the guard suite, the boundary guard, and the injector build with
      no PowerShell on the path
