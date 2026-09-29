# `scripts/live-slot.ps1` → `gk-core/scripts/live_slot.py` — 2026-09-26

Session `live-slot-python-20260926` · program `ps1-ban` · branch `features/mega-merge` · the agent does
NOT merge; the manager reviews these SHAs:

| SHA | What it carries |
|---|---|
| `f4ba08460` | the port, its 77 tests, the `live-slot-tool` verification-boundary row |
| `f672503e7` | the three documentation callers, this report, the session record |

| Path | What it is |
|---|---|
| `gk-core/scripts/live_slot.py` | The port. Same CLI contract (both flag spellings), two defects fixed by construction. |
| `gk-core/tests/tools/test_live_slot.py` | 77 tests: the contract, both defects, the falsification against the `.ps1`, and parity. |
| `gk-core/scripts/verification-boundaries.v1.json` | `live-slot-tool` row, so the two new files are mapped (guard green). |
| `.agents/skills/live-probe-mcp/SKILL.md`, `.claude/cmdc-agents/briefs/cc8-live.md`, `.claude/cmdc-agents/briefs/ssh29.md` | Name the Python tool as the entry point. |

`scripts/live-slot.ps1` is **NOT deleted.** §7 has the exact caller list and the retirement order.

---

## 0. Two things the brief got wrong, found by reading the code

Both change the shape of the work, so they come first.

**The brief says `git grep live-slot.ps1` finds "only documentation callers — no code or CI caller".**
It finds a **live code caller**: `gk-fusion/scripts/prove-slot-connection.py:456` shells
`live-slot.ps1 -Acquire -Session …` and `:488` shells `-Release`. It is the pool's own end-to-end
connection prover, it reads the pool registry at `:398` and `:458`; `slots.json` does not exist in git
(it is a runtime file in the pool root) — and it depends on two `.ps1` behaviours by
name in its comments: that `-Acquire` ignores `-Slot` and takes the lowest ready slot (`:452`), and
that the port is `BasePort + slot` (`:453`). That file is in the active manager session's fence and
outside mine, so the re-point is routed, not done (§7). The good news stands and is now sharper than
the brief assumed: because the port accepts the **PowerShell flag spelling**, re-pointing that caller
is a one-token change (the program name).

**The brief says the registry is UTF-8 **BOM**, so a plain `utf-8` read raises `JSONDecodeError`.
Host-dependent, and the mechanism matters.** `live-slot.ps1:95` writes with
`Set-Content -Encoding utf8`, which emits a BOM under **Windows PowerShell 5.1** and **not** under
PowerShell 7. Measured on this machine: `slots.json` in the pool root, a path that does not exist in git,
under `pwsh`, the first four bytes of that file are `b'{\r\n '`.
`utf-8` decode. Resolution: the port **reads `utf-8-sig`** (tolerant of both, which is the load-bearing
half) and **writes plain `utf-8`, no BOM** — because `prove-slot-connection.py:212` reads this file
with `json.loads(path.read_text(encoding="utf-8"))`, and a BOM would break it during the window where
both implementations coexist. No reader objects to the absence of a BOM; a plain-`utf-8` reader objects
to its presence. Pinned by `RegistryEncodingTests`.

---

## 1. The CLI contract, preserved

Verbs `-Status`, `-Clone`, `-Acquire`, `-Release`, `-Reclaim`; parameters `-Session`, `-Slot`,
`-PoolRoot`, `-SourceInstall`, `-MaxSlots` (3), `-BasePort` (5100), `-LockTimeoutSeconds` (60),
`-StaleLockMinutes` (15), `-StaleClaimMinutes` (240), `-Force`.

**Every flag answers to both spellings.** `--session` is canonical; `-Session` is the compatibility
alias, and it is load-bearing rather than cosmetic: it is what makes the one live code caller a
one-token re-point. `CliShapeTests.test_every_flag_answers_to_both_spellings` and
`test_the_help_names_the_powershell_spelling_as_the_compatibility_alias` hold it.

Added (the Python-tool standard requires them): `--json`, `--timeout` (1800 s, per external call),
`--process-timeout` (30 s). The `-Reclaim` verb's `-Session` stays optional, as in the original.

### Behaviour deliberately preserved, and where it lives

| Contract | Where | Pinned by |
|---|---|---|
| `ready` = cloned **and** verified against the five required entries; anything missing is `broken` | `REQUIRED_ENTRIES`, `test_install` | `RequiredEntriesContractTests` reads the list **out of `live-slot.ps1`**, so a change there turns this red instead of forking the rule |
| A slot's port is **stored** on acquire and otherwise **derived** as `base_port + slot` | `resolve_port`, one function | `PortRuleTests` (both branches, and asserts they are not equal); `StatusTests` asserts both halves in one report |
| `-Clone` refuses an `occupied` slot without `--force` | `cmd_clone` | `test_cloning_over_an_occupied_slot_is_refused_and_names_the_holder` |
| `-Acquire` with every slot held **refuses and names the holders** — never kills | `cmd_acquire` | `test_acquire_refuses_when_every_slot_is_held_and_names_the_holders` |
| The lock is an exclusive create held for the read-modify-write only; a stale lock is broken and the break **recorded** in `staleBreaks` | `slot_lock` | `test_the_lock_is_taken_for_the_write_and_released_afterwards`, `test_a_stale_lock_is_broken_and_the_break_is_recorded`, `test_a_fresh_lock_makes_the_caller_wait_and_then_refuse_by_name` |
| `-Status` reports the game process **actually running from that install** | `slot_processes` | exercised by every `-Status` test; a live-PID test would need a real game |
| The pool root is trimmed, and a trim is **announced** | `resolve_pool_root` | `PoolRootTests` |
| `-Acquire` ignores `-Slot` and takes the lowest ready slot, else the first uncloned | `cmd_acquire` | `test_acquire_ignores_a_slot_flag_but_says_so` |
| `-MaxSlots` is only written when the flag was **given** (`$PSBoundParameters` at `:59`) | `default_max_slots` (`default=None` carries the distinction) | — |
| Exit **4** for a clone that finished and failed verification (`:244`) | `EXIT_CLONE_BROKEN` | `RefusalContractTests.test_the_exit_codes_preserve_the_powershell_originals_four` |
| A `broken` slot on acquire is **recorded and then refused** (`:281`) | `cmd_acquire` | `test_a_broken_slot_on_acquire_is_refused_by_name` |

### Exit codes

`0` ok · `1` a named refusal (the original's unhandled-throw code) · `2` the pool could not be
read/written/locked, or an external call failed or timed out · `4` a clone verified `broken`
(preserved). Every refusal prints `live_slot REFUSED [<stage>]: <NAME>: <instance> -- <remedy>` to
stderr and prints nothing on stdout.

### Deliberate changes, each with its reason

1. **The log prefix is `live_slot`, not `live-slot`.** The prefix names the emitter; the emitter
   changed. Pinned in the parity normaliser so the difference cannot hide a third one.
2. **A refusal carries its remedy.** The original folded the guidance into the message it threw
   (`"-- wait for one to release; do not kill another session's game"`, `:259`). My first cut printed
   only name + instance and my own test caught the regression — so `Refusal.render()` now appends
   the registry row's meaning. `RefusalContractTests.test_a_refusal_renders_its_stage_its_instance_and_its_remedy`.
3. **The registry is written atomically** (sibling temp file + `os.replace`) and **without a BOM**.
   The original's direct `Set-Content` could leave a truncated registry if it died mid-write. See §0.
4. **`updatedAt` is printed as stored (ISO-8601), not locale-formatted.** `ConvertFrom-Json` turns the
   original's own `(Get-Date).ToString('o')` back into a `[datetime]`, so `:181` interpolating it
   prints `09/26/2026 12:37:32` — locale-dependent, ambiguous across a DST boundary, and 38
   characters wide in a column the table declares as 22 (`:194`), so **the original's date column
   overflows its own layout**. Pinned by `test_the_timestamp_rendering_is_the_ports_to_improve`.
5. **A failed process enumeration refuses instead of reporting "no game running."** The original
   wraps `Get-Process` in `try { } catch { return @() }` (`:129-133`) — and an empty answer is the
   *wrong* answer for a liveness check: `-Status` uses it to raise `STALE CLAIM` and `-Reclaim` uses
   it to permit a force-release. `PROCESS-ENUM-FAILED`, fail-closed, with a sentinel line proving the
   enumeration ran.
6. **The pool root is canonicalised** with `Path.resolve()` (long path) where PowerShell's
   `Resolve-Path` kept the 8.3 short name. Both sides of the process-path comparison then agree;
   `deploy-play.py:314-316` already resolves before comparing, so it agrees too.
7. **`--slot` on `--acquire` is announced as ignored.** The pick rule is preserved exactly (a
   `prove-slot-connection.py:452` dependency); silently swallowing the flag is not.
8. **The `deploy into THAT path` line says `python gk-fusion/scripts/deploy-play.py`.** The original says
   `pwsh -File gk-fusion/scripts/deploy-play.py` — a `.py` file run with `pwsh`. Pinned, not filtered (§3).
9. **A stamp refusal on `--clone` records the slot as `broken` with the reason, then refuses.** A
   clone claims nothing, so persisting the diagnosis costs no slot and leaves the evidence in the one
   place the next agent looks — the same persist-then-refuse shape the original already uses at
   `:281`. A stamp refusal on `--acquire` happens **before** the claim is written, so it costs no
   slot (`prove-slot-connection.py:389`).
10. **Dropped: the original's unused `$slug` scriptblock** (`:173`), dead in the original and
    referenced nowhere.
11. **The lock's stale-break still writes the registry without holding the lock**, exactly as
    `:108-111` does. That is this shape's one inherited weakness; changing it would be a silent
    behaviour change, so it is left visible and named here instead.

---

## 2. The two defects, measured before and after

### Defect 1 — a clone inherits the owner's server URL

A slot is cloned from the owner's install and the owner's `Mods/fusionrpg.cfg` names the owner's
server. The Injector reads `FUSIONRPG_SERVER_URL`, else `ServerUrl=` in the cfg, else `:5088` **with
a warning**; `deploy-play.py` only rewrites that cfg at **stage 9 of 12** (`:500-514`), so any earlier
failure leaves the inherited value.

**Before**, on a temp pool whose source cfg named `http://127.0.0.1:5088` (observed output):

```
clone slot 1  ->  cfg ServerUrl = http://127.0.0.1:5088     state ready
clone slot 2  ->  cfg ServerUrl = http://127.0.0.1:5088     state ready
acquire       ->  registry port = 5101, transcript "YOUR SERVER PORT: 5101"
                  cfg ServerUrl = http://127.0.0.1:5088      <-- the game dials the owner
```

That is the worst shape a bug can take here: the registry, the transcript and `-Status` all agree
with each other and all disagree with the game.

**After**, same source, same sequence:

```
clone slot 1  ->  stamped ServerUrl=http://127.0.0.1:5088 -> http://127.0.0.1:5101
clone slot 2  ->  stamped ServerUrl=http://127.0.0.1:5088 -> http://127.0.0.1:5102
clone slot 3  ->  http://127.0.0.1:5103
acquire       ->  cfg ServerUrl = http://127.0.0.1:5101  (re-stamped; "already correct" is idempotent)
```

`stamp_server_url` stamps on `--clone`, on a `--force` re-clone and on `--acquire`, using
`resolve_port` — the same stored-or-derived rule `-Status` uses — and prints the value it replaced.

The key is **read, not guessed**: `SERVER_URL_PATTERN` is the exact pattern `deploy-play.py:508`
verifies its own write with, and `test_the_cfg_key_this_tool_stamps_is_the_key_deploy_play_writes`
reads `deploy-play.py` back and fails if the two ever diverge. So if the deploy ever writes a
different key, this test goes red instead of the stamp silently editing a dead key.

Three cases, distinguished on purpose: a cfg **with** the key → rewritten, old value reported; a cfg
**without** the key → `CFG-NO-SERVERURL`, refusing rather than inventing one, and the file is
asserted unchanged; **no** cfg → reported loudly, nothing created (the BepInEx host has none by
design, `deploy-play.py:277`, and a staged deploy writes it). An absent cfg inherits nothing, so the
precondition "this slot will not dial the owner's server" already holds — inventing a file there
would be the guess the brief forbids.

### Defect 2 — `--force` re-clone cannot delete a tree with trailing-space directory names

Cause: a polluted **source** carried directories named `Mods --no-incremental --nologo -v n ` whose
trailing space the Windows path APIs normalise away, so the name can be neither addressed nor deleted
through them. Measured, per host:

| Attempt | Result |
|---|---|
| `shutil.rmtree` (what the port would naively do) | **`WinError 145: The directory is not empty`** — every host, every time |
| `Remove-Item -LiteralPath <dir> -Recurse -Force` — what `live-slot.ps1:225` calls — under **Windows PowerShell 5.1** (`Desktop 5.1.26100.9444`) | **`FAILED: Win32Exception: The system cannot find the file specified`, rc 1**, tree left in place |
| the same under **PowerShell 7** | **rc 0 — it happens to work** for a single trailing-space directory |
| `robocopy <empty> <target> /MIR` then `shutil.rmtree` | **rc 2 (success; 0–7 is the success range) then the tree deletes immediately.** robocopy reports `*EXTRA Dir -1 …\Mods --no-incremental --nologo -v n \` — it enumerates the offending name itself |

A second, quieter failure measured alongside: under 5.1 the throw happens **before** `Write-Registry`,
so after a failed `--force` re-clone the registry is stale. `slots.json` in the pool root does not exist in
in git, so it still reads **ready** while the install is still the old polluted tree that was never
the old polluted tree that was never replaced. `test_the_originals_own_force_reclone_fails_and_claims_success_in_the_registry`
pins that fail-open.

**The remedy chosen, and why this one.** `remove_tree` tries `shutil.rmtree` first — it succeeds for
every normal tree and is far faster than a robocopy pass, and `ForceRecloneTests` asserts the fast
path is still taken (`deleteRemedy == "rmtree"`). Only on `OSError` does it mirror an **empty**
directory over the target and retry, reporting which remedy ran. The `\\?\`-prefixed walk is the other
known-good path and is deliberately **not** used: it needs its own long-path plumbing through every
step, whereas the mirror is one already-measured call with a documented exit range.

The `\\?\` prefix is still needed — to *reproduce* the defect. And the reproduction has a trap worth
recording: `os.path.abspath` runs `ntpath.normpath`, which **strips the trailing space off the last
component**, so a `\\?\` path built that way silently creates the *trimmed* name and the test quietly
proves nothing. Measured, both ways. `extended()` in the test file prefixes an already-absolute
`str(path)` and never goes through `abspath`, with the measurement in its docstring.

---

## 3. Parity: method, and the real differences

**Method** (the `verify-change-python-20260926` approach): two temp pools under one parent with
**equal-length** names (`ps1`, `py1`) so the status table's column padding is directly comparable, the
same fake source install in each, the same six-verb sequence driven through each implementation
(`clone 1`, `clone 2`, `acquire`, `status`, `release`, `status 2`), then compare **exit codes**,
**stderr**, the **stdout transcript** and the **resulting registry**. The runtime `slots.json` does not exist in git — it
is written into the pool root by whichever tool touched the pool last.

Normalised away, each for a stated reason: the pool root and the per-implementation label (two
absolute temp paths, and the two hosts disagree even on 8.3-vs-long); every timestamp; the port's
extra `registry written` line. What survives is compared for **equality**, not similarity.

**Result.** The registry is **identical** after the whole sequence, and the transcript matches line
for line — same states, same ports, same free/ready counts, same `ready-to-claim` footer, same
column layout — on every verb except the two differences below, which are **pinned by explicit
assertions** rather than filtered, so a third difference cannot hide behind them:

1. the port's `stamped …` / `already names …` line, which the original cannot produce (defect 1);
2. the `deploy into THAT path` line, `pwsh -File gk-fusion/scripts/deploy-play.py` vs `python
   gk-fusion/scripts/deploy-play.py` (deliberate change 8);
3. plus the timestamp rendering, pinned by its own test.

`test_the_states_and_ports_a_probe_depends_on_are_identical` pins the shape a probe reads directly:
`[(1, "occupied", 5101, "probe-1"), (2, "ready", None, None)]` from both.

---

## 4. Falsification: which tests failed against the pre-fix code

The pre-fix code **is** `scripts/live-slot.ps1`, so the falsification is a swap, not a re-statement.
Two shared helpers — `assert_clone_names_its_own_port` and
`assert_force_reclone_survives_a_trailing_space_directory` — are the bare invariants, and the only
thing that differs between the two implementations is the `runner` passed in.

Observed, running the port's own invariants against the pre-fix tool:

```
########## live-slot.ps1  (PRE-FIX)
  -- defect 1 invariant: a clone must not inherit the owner's :5088
     FAIL   the clone INHERITED the owner's server URL (http://127.0.0.1:5088); the Injector reads
             FUSIONRPG_SERVER_URL, else ServerUrl= in this cfg, else :5088 with a warning, and
             deploy-play.py only rewrites the cfg at stage 9 of 12
  -- defect 2 invariant: --force must delete a tree with a trailing-space dir name
     PASS   the undeletable name was removed and the slot is usable again
########## live_slot.py  (this port)
  -- defect 1 invariant: a clone must not inherit the owner's :5088
     PASS   slot 1 cfg ServerUrl = http://127.0.0.1:5101
  -- defect 2 invariant: --force must delete a tree with a trailing-space dir name
     PASS   the undeletable name was removed and the slot is usable again
```

**Defect 1 is falsified directly.** `PowerShellDefectTests.test_the_original_fails_the_no_inherited_owner_url_invariant`
is green *only* because the old tool violates the invariant, and the passing half is
`DefectOneCloneTests.test_the_invariant_holds_for_this_implementation` — the identical helper.

**Defect 2 is falsified, but not the way the brief assumed, and I am not going to overstate it.**
Against **PowerShell 7** — this machine's default and the one `deploy-play.py` prefers — the
*original* passes the delete invariant: `Remove-Item -Recurse -Force` happens to handle a single
trailing-space directory there. So the honest falsification is split:

- `PlainRmtreeTests.test_shutil_rmtree_alone_cannot_delete_a_trailing_space_directory` — the
  **host-independent** half. The naive Python delete fails `WinError 145` on every host; the
  test also asserts the plain-path view cannot see the name and that the mirror is what clears it.
  This is the assertion that would have caught a naive Python port on any machine.
- `PowerShellDefectTests.test_the_originals_own_force_reclone_fails_and_claims_success_in_the_registry`
  — runs the **real `.ps1`** under `powershell` 5.1 and asserts `rc != 0`, a `Win32Exception`, the
  name surviving, and the registry still claiming `ready`. Skips if 5.1 is absent (it is present here).

Both halves fail against *fixed* code, which is what makes them falsifiers. Both are in the file.

The other 74 tests are contract tests: they would pass against the old tool, and they are not claimed
as evidence of anything beyond the contract they state.

---

## 5. Test results

```
python -m pytest gk-core/tests/tools/test_live_slot.py -q -p no:cacheprovider
77 passed in 33.31s
```

Scoped verification through the port itself, at the boundary the registry selects
(`python gk-core/scripts/verify-change.py --paths <the 6 changed paths> --session live-slot-python-20260926`):

| Stage | Result |
|---|---|
| plan | `live-slot-tool` (focused) for both new files, `guard.verification-boundaries` for the registry row, `guard.doc-boundary` for the three docs, their three doc-citation checks, and `pytest tools-audit-tests` |
| `pytest tools-audit-tests` | **green — 77 passed in 33.31 s** |
| `doc-citations` × 3 | **green** (no refusal) |
| guard focused check | **exit 1 — `Failed: 2, Passed: 63, Total: 65`** |

**The two guard failures are pre-existing and are not mine.** Measured, not assumed: I re-ran both
failing tests **with my registry row and with it removed** (491 entries vs 490, everything else
byte-identical) and they fail **identically both ways**.

| Failing test | Why it is not this change |
|---|---|
| `SplitCoreVerificationMappingTests.Planner_resolves_representative_split_core_files_to_area_owners_not_residual` | `Assert.Single()` found no selection matching one of the Core **area** mappings. The planner returns an area boundary *and* a seam boundary for each path (`unique-allocation-reader-seam`), so the test's single-selection expectation no longer holds. Pure `gk-core/src/FusionRpg.Core/**` mapping; my row names `gk-core/scripts/live_slot.py` and `gk-core/tests/tools/test_live_slot.py` only. |
| `VerificationBoundaryWorkflowTests.The_real_magic_number_audit_boundary_is_guard_only` | `FullyQualifiedErrorId: path does not exist: scripts/guard-magic-numbers.ps1`. That shim was **deleted by `90a367afc` "feat(guards): run five guards as Python, and retire their shims"**, while the verification registry row and this test still name the `.ps1`. A `ps1-ban`-program break, not a mapping break. |

Both are routed, not fixed: `gk-core/tests/FusionRpg.Guard.Tests/**` is in the active manager session's
fence and outside mine (§9).

Two operational notes, reported rather than smoothed over:

1. **One intermediate run died on the documented testhost race.** `MSB3027 "…FusionRpg.Guard.Tests.dll
   … is locked by: testhost (23828)"` → `VERIFY-CHANGE REFUSED [build]: BUILD-FAILED`. I caused it by
   launching a second `verify-change.py` while the first was still running: the first run's
   `testhost.exe` outlived its `dotnet test` (the incident in
   `tasks/reports/verify-change-python-20260926.md` §2). I killed my own orphan — identified by path
   (`tests/FusionRpg.Guard.Tests/bin/Release/net8.0/testhost.exe`) and start time — and the next
   build succeeded. The port classified it correctly as `BUILD-FAILED` at the `[build]` stage, i.e.
   before any test ran, which is the right stage for that failure.
2. **The first background run also reported a test-host crash** ("The active test run was aborted.
   Reason: Test host process crashed", while running
   `VerificationBoundaryWorkflowTests.An_unmapped_tool_tree_still_refuses_rather_than_selecting_nothing`).
   Same machine contention class; it did not reproduce in the standalone and isolated re-runs above.

Green, observed, and worth naming separately: `python gk-core/scripts/guard-verification-boundaries.py`
→ `VERIFICATION BOUNDARY GUARD OK` on the full walk with coverage, which is what proves the two new
files are **mapped** rather than silently unmapped. And the doc-citation audit on each of the three
edited docs and on this report: `0 HIGH` in every bucket.


---

## 6. What I could NOT verify

1. **A live game was never launched.** Both defects are about what a cloned install *contains* and
   what the Injector would read, and both are proven by reading the slot's own `Mods/fusionrpg.cfg`
   back off disk — not by a game dialling a port. A live probe would be the final confirmation and
   needs the pool, the game lock and an owner-free slot; it is not this lane's to take.
2. **No process-liveness test against a running game.** `slot_processes` is exercised on every
   `-Status`/`-Release`/`-Reclaim` test, but always with the answer "no game is running from this
   install". The positive branch (a real PID from a real install) is unexercised.
3. **`--force` re-clone was never run against a real 546 MB game tree.** The remedy is the same
   robocopy mirror the clone already uses, on a small tree; the timing and the long-path behaviour of
   a full game tree are unproven here.
4. **The `SLOT-STILL-RUNNING` and "still running, releasing anyway" paths** need a live process, so
   their refusal and warning branches are unexercised.
5. **The stale-lock break writes the registry without holding the lock** (preserved from `:108-111`).
   The single-threaded test passes; the concurrent case is untested, in both implementations.
6. **Concurrency is untested.** Two simultaneous `live_slot.py` processes contending for the lock
   are not exercised; only a held lock and a stale lock are.
7. **The full unfiltered suite was not run.** Every number above comes from a scoped boundary or
   from `gk-core/tests/tools`.
8. **The scoped boundary is not fully green**, and I am not claiming otherwise. The pytest step and
   all three doc-citation checks pass; the grouped guard check exits 1 on **two pre-existing
   failures** that reproduce identically with my registry row removed (§5). Nothing in this change's
   evidence is green that I did not observe green.

---

## 7. Retirement order for `scripts/live-slot.ps1`

The `.ps1` is still live. Nothing breaks if the two diverge today (a pool's registry is read by both),
but the duplication is real. Ordered, with each step's owner:

| # | Step | Owner | Why it must come first |
|---|---|---|---|
| 1 | **Re-point the one live code caller.** `gk-fusion/scripts/prove-slot-connection.py:456` (`-Acquire`) and `:488` (`-Release`), plus the `powershell("live-slot.ps1", …)` helper. Because the port accepts the PowerShell spelling, this is **the program name only**. Update the three comments that name `.ps1` line numbers (`:383`, `:411`, `:452-453`, `:716`). | the session holding `scripts/**` (currently `mega-merge-program-manager-20260925-f78e`; `ps1-ban-manager-20260926` is retiring PowerShell) | **Without this the deletion breaks the pool's own connection prover.** This is the step the brief's "no code caller" reading would have skipped. |
| 2 | **The two callers of `lane-server.ps1`'s registry read** need no change: `lane-server.ps1:53-60` reads that registry directly — `slots.json` in the pool root, a path that does not exist in git — and the port
writes the same shape (`port` present after acquire, absent before). Verified, not assumed — the parity test asserts the registry is identical. | — | — |
| 3 | **Delete `PowerShellParityTests` and `PowerShellDefectTests` from `gk-core/tests/tools/test_live_slot.py`** in the same commit. They read `scripts/live-slot.ps1`; leaving them behind would fail the moment the file goes. Their content becomes the historical falsification in this report. | the lane that deletes the `.ps1` | A half-retired tool is worse than a broken one; a test that reads a deleted file is worse still. |
| 4 | **Delete `scripts/live-slot.ps1`** and drop it from `gk-core/scripts/verification-boundaries.v1.json`'s `guard-verification-boundaries-tests` path list (`:3744-3747` region) in the same commit. | same | `gk-core/scripts/enforcement-registry.v1.json:241` also names it — that row goes too, in the same commit. |
| 5 | **`AGENTS.md:135` and `:337`, `docs/contributing/live-probe-standard.md:209,212`, `.agents/skills/project-leader/SKILL.md:117`, `scripts/audit-doc-citations.py:66-67`, `scripts/lane-server.ps1:9,192`, `gk-fusion/scripts/prove-slot-connection.py`'s comments** — comment- and prose-only references; a rename for tidiness, no behaviour. `AGENTS.md`, `CLAUDE.md` and `docs/contributing/**` are all in the active manager's fence, which is why they are not in this lane. | the manager / `ps1-ban` | They are documentation, so they can move in the same commit or the one after; none of them executes. |
| 6 | **`tasks/**` reports and ledgers** name it historically. Leave them: they are dated evidence, and rewriting a dated report is how a report stops being evidence. | — | Deliberately **not** done. |

Comment-only references found by `git grep` (a rename for tidiness, no behaviour):
`AGENTS.md:135,337`, `.agents/skills/project-leader/SKILL.md:117`,
`docs/contributing/live-probe-standard.md:209,212`, `gk-core/scripts/enforcement-registry.v1.json:241`,
`scripts/lane-server.ps1:9,192`, `gk-fusion/scripts/prove-slot-connection.py:233,250,383,411,425,452,456,488,716`,
`scripts/audit-doc-citations.py:66-67`, `tasks/reports/mega-merge-manager-resume-20260925.md:81,124,557,645,649`,
`tasks/ps1-ban-plan.md:169`, and the `tasks/**` reports/ledgers/session records listed above.

---

## 8. Open questions

1. **Process enumeration still shells out to PowerShell** (`pwsh`, falling back to `powershell`) —
   the one place this port did not become pure Python. It is a single implementation with a hard
   timeout and a fail-closed sentinel, and it is what the brief's "hard timeout on process
   enumeration" asks for. But a tool whose purpose is retiring PowerShell still requiring it is worth
   naming. The alternative is ~70 lines of `ctypes` (`CreateToolhelp32Snapshot` +
   `QueryFullProcessImageNameW`) with no external dependency and no ~1 s per call; it was not written
   here because a second implementation of one thing is the defect this repo treats as non-negotiable
   (§2.15 SOLID), and picking it properly is a design decision, not a port detail. **Owner call.**
2. **`lane-server.ps1` is still PowerShell and still reads the pool registry.** It is the other half
   of the live-probe story and the natural next port. Its `SlotPort` is the reader half of the
   stored-or-derived rule this port made explicit; the port does not change its behaviour, so the
   retirement order does not block on it.
3. **A slot whose `BasePort + slot` equals 5088.** The port stamps whatever it resolves and prints a
   `WARNING` when the result is the owner's port, but `lane-server.ps1:68` is what refuses. Should the
   pool *refuse* such an acquire instead of warning? Measured reachable: `--base-port 5087 --slot 1`
   resolves to 5088. I kept the original's behaviour and added the warning rather than change the
   contract in a port.
4. **The `-Slot` flag on `--acquire` is accepted and ignored** (preserved, announced). A future
   deprecation could refuse it outright; that is a contract change, not a port decision.

---

## 9. Three findings for the manager, all out of this lane's fence

1. **`gk-fusion/scripts/prove-slot-connection.py` is a live caller of `live-slot.ps1`** (§0, §7 step 1). The
   brief's "documentation callers only" is wrong, and acting on it would have deleted a file with a
   live caller.
2. **`gk-core/scripts/verification-boundaries.v1.json` had no active owner**, so the `live-slot-tool` row was
   added without a crossing. If the manager disagrees, the row is one `id` block to move.
3. **Two pre-existing guard failures sit inside `guard.verification-boundaries`, which my registry
   edit selects** (§5): the `SplitCore` area/seam single-selection mismatch, and
   `The_real_magic_number_audit_boundary_is_guard_only` naming `scripts/guard-magic-numbers.ps1`,
   deleted by `90a367afc` while the registry row and the test still point at it. Both reproduce with my
   row removed. The second is a one-line registry/test fix that belongs to the `ps1-ban` program, and
   it will keep reddening every boundary that touches the registry until it lands.

