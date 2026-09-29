# Plan — `ps1-ban`

Port every PowerShell tool to reliable Python, prove each port, merge to `features/mega-merge`.

Index: [`docs/architecture/ps1-ban-map.md`](../docs/architecture/ps1-ban-map.md).
Tasks: [`tasks/ps1-ban-todo.md`](ps1-ban-todo.md).
Session records: `tasks/sessions/ps1-ban-*.json`. Manager record:
`tasks/sessions/ps1-ban-manager-20260926.json`.

## Owner charter

Runtime OpenCode CLI · model `opencode/space-bunny-free` · 8 concurrent lanes · uncapped token budget
per lane · one git worktree per lane · **stop rule:** a credit or quota error stops that lane and is
reported, with **no model fallback**; a stalled lane is stopped and reported rather than silently
retried on another model.

## Owner rulings

1. **Sequence behind the active session.** `mega-merge-program-manager-20260925-f78e` fences the
   dispatchers, the registry, all 29 guards, `gk-core/tests/FusionRpg.Guard.Tests/**` and the runbook docs.
2. **`scripts/pi-web-windows-service.ps1` is deleted permanently** — it serves a pi-agent workflow the
   owner no longer uses, and it calls `Register-ScheduledTask`/`New-Service`, which need admin, so
   neither CI nor any agent can ever prove a port of it.
3. **The live tier requires a real live run.** Unit tests do not satisfy that bar.
4. **`shell: pwsh` → `shell: bash` is in scope** for the three workflows. Use `bash`, not `cmd` — `cmd`
   has no `-e` and no `pipefail`.
5. **The `AGENTS.md` line "Existing `.ps1` files are not to be rewritten wholesale" is superseded** and
   is part of the deliverable. It is fenced by two other live sessions, so it lands late.

## Unresolved, carried as an explicit assumption

`scripts/test-substrate-leak-alarm.ps1` takes a `[scriptblock]$Run` that `.github/workflows/ci.yml:383`
and `nightly.yml:69` invoke as `-Run { dotnet test … }`. A PowerShell scriptblock cannot cross into
Python. The working assumption is an **argv** redesign —
`python gk-core/scripts/test_substrate_leak_alarm.py -- dotnet test …` — with **both** call sites updated in the
same commit. This needs owner confirmation before that task merges.

---

## Section 1 — Why the order is what it is

The program is **not** a mechanical sweep. Two measured facts set the sequence:

**A guard cannot shed its `.ps1` until the dispatchers can run a `.py`.** Ten dispatch sites
(map §1) reach the outside world through `pwsh -File` or the PowerShell call operator. Port a guard
first and `run-guards.ps1:191` invokes `pwsh -File guard_x.py`, which does not execute the Python.

⚠️ **Corrected 2026-09-26 by measurement.** This paragraph originally said the suite would read
**green**. It does not. Measured on this machine with a throwaway probe: `pwsh -NoProfile -File
probe.py` exits **64** with "the file does not have a '.ps1' extension", and the call-operator path
raises `CommandNotFoundException` under `Stop`. Both are **loud**. The gate is real — the guard
cannot execute — but it fails **red**, and the sequence below is unchanged. What makes a rename
genuinely dangerous is the *other* paragraph.

`Directory.Build.targets:53` remains the severe case, and for a different reason than "it is
invisible": it runs before every `Build;CoreCompile` of the three injector host projects, and a
missing script surfaces as `FUSIONRPG0002` "was pointed at a pack that is not this cell's" — a
correct action reported as a different, wrong one. It is loud but **misleading**, which is its own
failure mode.

**Renaming is more dangerous than porting.** Three shapes break *silently* rather than loudly: a glob
that matches zero files and passes vacuously, a `File.Copy` that throws in a test temp root, and
`~40` repo-root `File.Exists` probes that walk to the filesystem root instead of failing. The map's
`contract-scan-repair` and `repo-root-probes` sections enumerate them.

So: **fix the dispatchers, then repoint the registry, then port bodies, then sweep citations.** Each
step is separately provable, and a failure at any step is attributable to that step.

## Section 2 — Waves

Every wave is gated on the previous one and on the active session releasing its fence.

### W0 — Program instrument *(manager, no port)*
The capability map, this plan, the task list, and the session records. **Without these a lane's
acceptance has nothing to be measured against** — the status reader reports a program with no declared
shape as `unmeasured`, never "0 open".

### W1 — `dispatcher-interpreter` *(the wave with no port in it)*
Make the ten sites interpreter-aware. **Zero behaviour change; every guard is still `.ps1` when it
lands.** Proof is "nothing changed": the same guard suite, green, before and after. This is the only
wave that can be proven by absence of difference, and it is what makes every later wave safe.

### W2 — `shim-guards` + `retirements` *(cheapest first)*
Five registry rows move to Python tools that already exist (215–548 lines each), two of which already
have pytest coverage. Plus the proven-unreferenced one-off deletions. **This is the first proof that
W1 works** — if a shim guard runs and gates after its row moves, the dispatcher fix is real.

### W3 — `checks-ports` + solo mechanical guards
The 16 `gk-core/scripts/checks` wrappers, then the guards with no cross-tool coupling and no high probe
fan-out. Each lands with its registry row, its `verification-boundaries.v1.json` rows, and the
`GeneratorCheckCiParityTests` repoint **in the same commit**.

### W4 — coupled guard groups
Port by group, because a split produces a red tree rather than a half-ported tree:

| Group | Members | Forced by |
|---|---|---|
| `SourceText` | `lib/SourceText.ps1` + `guard-battle-responsibility` | the lib has one consumer |
| `stripper` | the three PowerShell copies of the comment-stripping routine | porting independently yields a fourth divergent copy |
| `diff-guards` | `guard-generated-seed`, `guard-tuning-immutability`, `guard-repo-boundary` | a shared `-BaseRef`/`-Range` convention by documented agreement |
| `compile-guards` | `guard-bench-compile`, `guard-injector-compile` | one copies the other's shape by its own header |
| `high-fanout` | `guard-dal`, `guard-class-system`, `guard-secondary-no-unity`, `guard-power` | 6–18 repo-root probes each; wrap-don't-rename or budget the edit |

### W5 — `tool-ports`, the keystone last
`session-boundary-check` and `guard-verification-boundaries` are last: both are read as **source text**
by other code, both own or share a `gk-core/scripts/lib` module, and `verify-change` dot-sources the same lib
the boundary guard does. Porting either without the other strands the lib.

### W6 — `live-probe-ports` *(owner's bar: a real live run)*
For the nine scripts that already have a Python equivalent in `gk-fusion/tools/live_test/live_test/scenarios/`,
the sanctioned migration is the one `docs/runbook/live-test-ssot.md:530` already states: make the
Python pack hard-assert parity, then delete the `.ps1`. The rest are ported and live-proved.
**Merge is gated on the run, not on the port.** Scripts whose verdict needs a human eye, or a machine
with no other game running, are listed as **partially provable** rather than claimed as proven.

### W7 — `ci-shell-bash`
54 steps. The exit-check lines are **pinned by five C# guard tests**; deleting them is 160 violations.
The zero-guard-churn path is to keep each line verbatim as an inert comment under `shell: bash`, which
satisfies the owner's ruling without touching a test. Only the genuinely PowerShell steps — the three
`resolve range` algorithms (one Python tool with three labels, not three translations), the
self-referential `Select-String` filter, the `try`/`catch` ref-prep step, and the zip/hash step — are
real rewrites.

### W8 — `citation-sweep`
One tool-driven pass, executed **by** the ported `guard-doc-citations` in the same commit as its own
port. Ordered by blast radius, not by count: the `Directory.Build.targets` path, the 29 registry rows,
the 51 boundary rows, the 27 contract scans, then prose. Acceptance artefacts under
`.claude/cmdc-agents/acceptance/` are **never** rewritten — they are SHA-keyed verdict records and
editing one falsifies the evidence.

---

## Section 3 — The merge gate

A lane merges to `features/mega-merge` only when all of these hold:

1. Its own scoped verification is **green**, and the report pastes the real output.
2. Its registry / boundary / test repoints are **in the same commit** as the port.
3. An acceptance exists at an **exact pinned SHA**, produced by the ported harness.
4. The main worktree is **clean enough to merge into** — which, right now, it is not.

**The active session is still committing to `features/mega-merge`.** Merging a lane branch into a tree
another session is actively writing is the collision the whole boundary system exists to prevent, so
**lane branches are held, verified, and merged after that session closes.** Holding is not stalling: the
branches are real, the evidence is real, and nothing is lost by waiting.

## Section 4 — Verification discipline

Run the **path-owned scoped** command for the paths you touched. Do **not** run the unfiltered full
suite to "be safe" — that is a defect in this repository, not caution. A missing verification boundary
for a path you touched is a **registry defect to report**, never a reason to substitute a broad run.

Two standing facts for this program:

- A newly ported `.py` is **unmapped** in `verification-boundaries.v1.json` until W2 adds it, so
  `verify-change` refuses it with `VERIFICATION BOUNDARY MISSING`. That refusal is correct and is
  reported, not worked around.
- `.github/workflows` invocations are **not** this program's to edit until W7.

## Section 5 — Known environment facts that constrain the live tier

Recorded because they are machine state, not code, and they change the plan's feasibility:

- `FUSIONRPG_GAME_POOL` and `FUSIONRPG_GAME_SOURCE` are **unset**, and the deploy tool falls back to
  the owner's own install. The pool guard therefore **cannot fire**, which is the incident class that
  guard was written for. Both the env contract and a hardcoded install path in the ported deploy are
  defects to fix in the pool port's wave, not later.
- Only **one** of the three live slots exists, and an abandoned second pool root also claims a slot.
- `live-slot.ps1` and `deploy-play.py` **disagree on how the pool is named** (flag vs env-only), so an
  honest pooled run cannot currently be expressed.
- The ported slot-connection proof harness **invokes the unported `.ps1` pool tools by name**; porting
  either half without the other removes the repository's only pooled-path proof.
