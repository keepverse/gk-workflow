# Keepverse migration plan — extension, 2026-09-27

Extends `tasks/keepverse-split-plan.md` in the source monorepo (written 2026-09-19). That
file stays where it is: the source repo is archived at G3, and a plan that describes moving
*out* of a repo belongs to the repo being left, not to the workspace being built. This file
is the authoritative version for the split and is versioned with the tool that performs it.

**The 2026-09-19 plan is superseded where it disagrees with this file.** Its topology section
is not merely incomplete — it is wrong in a way that would cause damage, because it says
"Web stays in gk-core" and lists six repositories. An agent following it would undo the split.

## Current state, verified

Measured by `kvsplit stage` against source `0923dfe03`, rules digest `5a1de009e5c3`:

```
tracked 14900   dropped 224   unplaced 0   balanced True
  root        5105    gk-data     3172
  gk-core     3784    gk-web      1108
  gk-forge     785    gk-tests       0   (receives nothing, by design)
  gk-fusion    463    gk-content     1
                     gk-assets    258
residue 2515:  path-literal-moves 2120 · content-root-consumer 388 · dead-rule 6 ·
              content-in-public-repo 1
```

`unplaced` is 0: every tracked path has an owner. `residue` is the work, not a gap in the
rules. kvsplit's own suite is 74 tests, green; two runs from the same SHA and rules produce
the same output digest, so a residue id is stable across unrelated changes.

The source tree is clean at `0923dfe03`. The 16 commits since the previous staging
(`421cac07b`) **added and deleted zero files**, so no ownership rule needed changing and every
number above is identical to the previous run. That is the useful property to preserve: staging
tracks file *paths*, so a content-only change cannot invalidate the rules.

## What changed since 2026-09-19, and why

| Plan said | Now | Why |
|---|---|---|
| 6 repositories | 9 (root + 8) | three added, see below |
| "Web stays in gk-core" | `web/**` → **gk-web** (1,108 files) | separate toolchain, bundle and failure mode from the C# server. It still ships as one release from the Server's `wwwroot` and binds the same `Contracts` DTOs — that is a cross-repo note, not a reason to merge the trees |
| `gk-data` holds `content/**` | **gk-content** (private) | authored names and flavour are ours; the derived corpus is not. One repo may not carry both and stay honestly private |
| (absent) | **gk-tests**, public | gate definitions and cross-repo suites, hand-written. It deliberately receives **zero** migrated files: path-owned verification co-locates a test with the code it tests, and a cross-repo lookup rots |
| `gk-assets` is MIT | **CC BY 4.0** art + **MIT** `tools/**` | the 2026-09-19 note flagged this itself: "MIT on art lets anyone reuse Keepverse art commercially". Splitting code from art is deliberate — CC BY on source code is an anti-pattern |
| `scripts/bootstrap.ps1` clones | Python | new tooling is Python by owner ruling; the old plan predates it |
| root `CLAUDE.md` loads for sub-repos | root **`AGENTS.md`** primary, `CLAUDE.md` a 23-line pointer | one instruction file, not two that can drift |
| (absent) | `blender/**` → **gk-assets** (258 files) | the tree had no owner at all; gk-assets staged zero files until this. Each subtree relocates onto the layout already hand-migrated there |

Two boundaries the 2026-09-19 plan left open, now decided: **`gk-content` vs `gk-data`**
(authored vs derived) and **`gk-tests`** (gate definitions only).

## Tool contracts added since — none are in the old plan

Each of these is a rule change with a refusal behind it, discovered by measuring the real
workspace rather than by design:

- **`layout.testProjectGlobs` waives `compileDeps` for a test project.** `compileDeps` governs
  what *ships*. A test that invokes a generator to assert on its output is verifying the forge,
  not depending on it. Opt-in, applies only to the referencing project, and the graph edge is
  still recorded — the waiver hides a residue row, never a dependency. Absent the field nothing
  changes.
- **A `drop` ownership rule also authorises dropping a non-blob entry.** A symlink cannot be
  migrated (git checks it out as plain text without `core.symlinks`) and never reached ordinary
  classification, so all 222 were unresolvable. They are two alias sets of the same 111 skills;
  `tools/bootstrap_skills.py` recreates the aliases as a mirror that creates, repairs and prunes.
- **`apply` refuses to overwrite a committed file that differs**, naming each one, unless
  `--accept-overwrites`. `preserve` stops apply *deleting*; it never stopped the write loop
  overwriting. Measured: 77 staged paths are already committed somewhere, **38 with different
  content** — 28 of them in gk-assets, including 7 `.blend` scenes and 8 rendered sheets.
- **`apply` reports a repo that receives nothing** as `unchanged` instead of dying on
  `git commit` against an empty index. gk-tests is that case.
- **`preserve` must list every live file the split does not itself produce.** Measured, not
  guessed: with the lists as first written, `apply` would have deleted 96 hand-authored files,
  84 in gk-assets, including the CC BY / MIT licence split.
- **Refusals are messages, not tracebacks.** `main()` had no error handling, so gate GM,
  residue-not-empty, not-clean and the overwrite guard all printed a stack trace.

## New work class between Phase 2 and Phase 4

**Overwrite reconciliation — 38 files.** The owner has already hand-migrated art into gk-assets
and then improved it; the split now produces the same paths from `blender/`. For each of the 38,
one of two is canonical: the newer gk-assets file, or the legacy `blender/` one. This is a
decision, not a mechanical transform, so it is not an agent brief. `vfx/index.json` and the 7
`.blend` files first. `apply` refuses until it is settled.

## What did not change

- **Ownership rules are complete.** 0 unplaced, and 16 content-only commits did not move that.
- **The direction contract holds** apart from the test-project waiver: no Unity reference below
  the injector, and gk-core never references gk-fusion.
- **Phase ordering.** kvsplit still reads a pinned SHA, never the working tree, so Phase 3
  ("decouple in place") still runs beside normal development.

## Where this stands

Phases 0–2 are done: the tool exists, the rules cover every path, and dry runs are
deterministic. **Phase 3 has not started** — all 2,515 residue items are open. Phase 4 is held
behind GM; `apply` currently refuses for two independent reasons (residue non-empty, and the
overwrite clashes).

Before the freeze, three session records still read `active` and hold path fences:
`ps1-ban-manager-20260926` (451 paths), `mega-merge-program-manager-20260925-f78e`, and
`resume-34-cai2-2-20260925`. Phase 4 requires them closed.

**Still unanswered by the owner: whether the trademark/IP risk is time-sensitive.** It is the
one open item with a clock on it — `gk-content` and `gk-data` are private for that reason, and
G2/G3 both wait on it. Everything else on this page is sequencing.
