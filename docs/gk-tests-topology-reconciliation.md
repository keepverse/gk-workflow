# gk-tests — topology reconciliation

Lane 3 of the Keepverse migration, implementing `[ADDED 5]` of
[`migration-goal-prompt.md`](migration-goal-prompt.md) as **one change set**: the plan, the
ownership rules, the transform path, the templates, the task criteria and the principles had
to agree, and `stage` and `check` had to be shown enforcing the result. A doc-only change is
not a topology change.

Date 2026-09-30. Source SHA unchanged by this work: `effc51d9b55f78aa7a5c47e14eef0e61b690e5eb`.

---

## 1. The defect, in one paragraph

`tools/kvsplit/rules/ownership.v1.json` contained **zero** occurrences of `gk-tests`. The rules
therefore already assigned it nothing, and nothing could land there. But nothing *said* so, and
the authoritative plan said the opposite in three places — §1.6's topology tree, the fourth
boundary bullet in §1.6, and §6.4. The plan claimed gk-tests held "gate definitions and
cross-repo suites" and that it *needed* the per-repo verification boundary declarations, a
cross-repo suite and a `ContentIntegration` category. Two documents named two different
topologies, and the one a reader believes is the prose. `ownership.v1.json` was right by
accident; `keepverse-migration-plan.md` was wrong on purpose.

The owner's workspace ownership principle settles it: **gk-workflow owns the development process
and its single source of truth** — shared guards, verification and migration harnesses,
orchestration tools, path rules, CI policy, contributor standards, architecture decisions,
principles, plans, task records and development documentation. Shared gate definitions, shared
harness logic and workspace policy are therefore gk-workflow's. A second copy of one inside a
sub-repository is the competing copy the principle forbids, and gk-tests must not hold them.

## 2. The reconciled role, stated once

**gk-tests is the repository that holds cross-repo test _suites_ that genuinely span
repositories, and nothing else.** It is 4 tracked files — `.gitignore`, `AGENTS.md`, `LICENSE`,
`README.md` — at `0b3672a`, with no import commit, and it stays that way.

No file was moved into gk-tests, and none was invented for it. An empty repository with a
written rationale is a better outcome than a populated one with invented content, and there is
nothing to invent: **before the split there were no repositories, so no path in the legacy
monorepo is a cross-repo suite.** A suite that spans repositories cannot exist in a repository
that is not yet several repositories. gk-tests was empty for a reason nobody had written down,
and now it is empty by decision.

## 3. What changed, file by file

| File | Change |
|---|---|
| `tools/kvsplit/rules/layout.v1.json` | `gk-tests` gains `seal.reason` — the decision, attached to the rule that can drift from it |
| `tools/kvsplit/kvsplit/rules.py` | `Repo.seal`, `Layout.sealed`, `OwnershipRule.entrypoint`; four refusals at rules-load time |
| `tools/kvsplit/kvsplit/check.py` | new residue kind `sealed-repo-received-file`, asserted on every row shape |
| `tools/kvsplit/tests/test_topology_seal.py` | 14 tests, all failing against the pre-change tool |
| `docs/keepverse-migration-plan.md` | §1.6 tree and boundary bullet, §6.4, the authority paragraph, A1, A4, and the stale-figure warnings on §1.1 and §1.5 |
| this file | the record |

**Not changed, deliberately:** no ownership rule was added, removed or retargeted, and no
template was added or removed. The seal changes what the rules *permit*; it moves nothing. So
the import-SHA `placedPerRepo` figures in A4 are unchanged by this work, and the only thing that
moved is `rulesDigest`:

```
before (at import)  0fe37c774d299b735312c684fac46e6e782f5824ad67715984bd2309dde9638d
after  (shipped)    05e46df60c016c0d09ff6613562a8b5ec293366b207ba70e7fcda3137f1495d4
```

Both read with `load_rules(Path("rules"), set(REGISTRY)).digest`. The import commits in the nine
repositories were made under the first digest and are unaffected; nothing re-runs `apply`.

## 4. The four refusals — `stage` enforces

A declaration nobody checks is a comment, so the seal is enforced at the point where rules are
loaded, and every message names the decision it is refusing against.

**A rule that places a file in a sealed repo.** This is the competing copy itself:

```
> python -m kvsplit stage --source <fixture> --rev HEAD --rules <rules+tests-gate-definitions> --out <dir>
kvsplit stage: ownership.rules[84]: rule tests-gate-definitions targets sealed repo 'gk-tests' -
gk-tests holds cross-repo test suites and nothing else. ... A rule that places a file there must
set 'entrypoint': true and say why.
exit=2
```

**A `copies` row naming a sealed repo.** A copy is the same bytes in a second repository, which
is the competing copy the seal exists to prevent — so it can never be the thin-entrypoint
exception either:

```
kvsplit stage: ownership.rules[84].copies: gk-tests is sealed. A copy is the same bytes in a
second repository - the competing copy a seal exists to prevent - so it can never be a thin
entrypoint.
exit=2
```

**A template emitted into a sealed repo.** kvsplit writes templates *verbatim*. This is the
route that produced H2's `template` rows, the ones a count-keyed guard did not see:

```
kvsplit stage: templates/gk-tests/AGENTS.md: repo 'gk-tests' is sealed - ... kvsplit emits
templates verbatim, so a template here is the split writing into a repository it may not write
into, and it is never a thin entrypoint.
exit=2
```

**An `entrypoint` claim on a repository that is not sealed.** The exception exists for one case.
A rule may not claim it for an ordinary repository, or it becomes an unreviewed hole in every
seal:

```
kvsplit stage: ownership.rules[N]: rule R claims the thin-entrypoint exception but its target
'gk-core' is not sealed. The exception exists only for a sealed repository, so claiming it
elsewhere is an unreviewed hole in the seal.
exit=2
```

## 5. `check` enforces the same thing on the tree

`stage` refuses the rules, so a tree cannot contain a breach through them. `check` is the
assertion on an **already-built** tree, and it is deliberately not the same mechanism: it reads
`files`, not the rules that produced them, because a tree can outlive the rules that built it.

It is asserted on **every row shape** — primary placement, `copies` row and `template` row
alike. That is the H2 lesson applied to the new rule: gk-assets held 228 art files behind two
*non-primary* rows, so a check that only counted placements would have read that repository as
untouched.

```
staged with the seal lifted : [('gk-tests', 'scripts/verification-boundaries.v1.json', 'source')]
sealed repos in the shipped layout : ['gk-tests']
check  sealed-repo-received-file  gk-tests/scripts/verification-boundaries.v1.json
       anchor=scripts/verification-boundaries.v1.json  fix=rule
       gk-tests is sealed (gk-tests holds cross-repo test suites and nothing else. ...) and
       received a source file anyway
```

The one row `check` accepts inside a sealed repo is one a rule **declared** as an entrypoint, and
it is resolved from the same ownership the parser enforced — so `check` cannot be stricter than
the rules, and cannot be talked round by a rule's `target` field alone.

## 6. The transform path

A transform runs per `(source path, target repo)`, and the target repo comes from
classification — which the seal has already refused. So no transform can reach gk-tests, and
that is asserted rather than assumed:

```python
paths = ["scripts/verification-boundaries.v1.json", ".github/workflows/gk-tests.yml"]
cls, _ = classify([Entry(p, "100644", "blob", oid) for p in paths], rules.ownership, lay)
# {'scripts/verification-boundaries.v1.json': 'gk-core', '.github/workflows/gk-tests.yml': 'root'}
```

The entrypoint rule is the one placement a transform *could* run against, which is exactly why
the `check` assertion above is on every row shape: it is the backstop if that stops being true.

**A thin CI entrypoint, when a platform requires one.** gk-tests is a public repository and a
platform will want a CI file inside it. That file stays a **thin entrypoint** to workflow-owned
policy and tooling — never a copy of it — and it must arrive as a rule that sets
`"entrypoint": true` and carries its own reason, so the exception is reviewed rather than
inherited. No such rule exists yet and none is invented here; `KS1.5`'s CI-split transform
(§6.5 of the plan) is its first candidate, and it is the unbuilt half of that block.

**A product generator belongs with the repository that owns its output.** gk-forge keeps
generator code; unchanged by this work and already expressed in the rules
(`forge-seedsmith`, `forge-*`).

## 7. Verification

```
$ cd tools/kvsplit
$ python -m pytest tests/ -q
94 passed in 85.70s (0:01:25)
```

80 before this change, 14 added in `tests/test_topology_seal.py`. No existing test was weakened,
disabled or edited, and no acceptance criterion was changed in the same change that satisfied it.

A6, out-of-scope invariance, before and after this work:

| Repo | Tracked | HEAD | Before | After |
|---|--:|---|---|---|
| `gk-tests` | 4 | `0b3672a` | unchanged | unchanged |
| `gk-assets` | 228 | `b02db75` | unchanged | unchanged |

No `apply`, no `--confirm-migration-start`, no `reset` / `checkout` / `stash` / `clean`, no
`git add -A`, and no contact with the source repository.

## 8. The larger finding this exposed — and it is not confined to gk-tests

Correcting gk-tests surfaced the same violation **one repository over**, and it is deliberately
not fixed here.

`scripts/**` is placed in **gk-core** by the blanket `core-scripts` rule. Under that rule the
import put these in gk-core, measured from `report.json` at the import SHA:

```
gk-core/scripts/verification-boundaries.v1.json     a shared gate definition - the per-repo
                                                      verification boundary map
gk-core/scripts/enforcement-registry.v1.json        the guard enforcement registry
gk-core/scripts/guard-verification-boundaries.py    the guard that reads it
```

The plan's §6.4 used to call the first of these gk-tests' to hold. It is not gk-tests' to hold,
and it is not gk-core's either: shared guards and verification harnesses are gk-workflow's. The
engine repository holding the workspace's shared gate surface is the same competing copy, one
repository over, and it is arguably worse than the gk-tests case because gk-core is a repository
that is *supposed* to be self-contained for public CI.

**Why not fixed in this change set.** Three reasons, and the first is the important one: (1) it
is a different boundary decision. `scripts/**` is 132 primary rows at the import SHA, and
re-routing it needs an owner decision about which guards are engine-facing and which are
workspace-facing — a judgement about 132 files, not a mechanical move. (2) It is not required to
seal gk-tests, and a topology change made without being able to re-run `stage` against the real
source is exactly the unverifiable change this migration has been bitten by. (3) It would move
residue anchors that other lanes own, and `[ADDED 7]` warns that an id which moves means the fix
changed the shape of the problem.

**The obvious move is also the wrong one, and this was measured rather than assumed.** Re-routing
`scripts/**` to gk-workflow looks like a one-rule edit. It is not, because the consumers are inside
gk-core and name those scripts by relative path:

| Consumer | References |
|---|---|
| `gk-core/.github/workflows/ci.yml` | `scripts/audit-magic-numbers.py`, `audit-overflow.py`, `audit-program-pipeline.py`, `enforcement-registry.v1.json`, `fix-doc-citations.py`, `test_fast.py`, `test_sharded.py`, `test_substrate_leak_alarm.py`, `guard-verification-boundaries.py`, `run_guards.py`, `session-boundary-check.py` |
| `gk-core/.github/workflows/nightly.yml` | `test_fast.py`, `test_substrate_leak_alarm.py`, `run_guards.py`, `session-boundary-check.py` |
| `gk-core/Directory.Build.targets` | `run_guards.py`, `guard-game-profile.py`/`.ps1` |
| `tools/SquadHarness/SquadHarness.csproj` | `gk-core/scripts/guard-dal.py` |
| `tests/FusionRpg.Guard.Tests/…csproj` | `gk-core/scripts/regen_class_system_baselines.py` |
| `src/FusionRpg.Server/…csproj` | `scripts/publish_player.py` |

`Directory.Build.targets` is imported by **every** project in gk-core, so a target naming
`../scripts/run_guards.py` fails for anyone who clones gk-core alone — which is the entire point of
a public repository, and the same self-containment §8 notes gk-core is supposed to have. Moving the
tooling without rewiring its consumers does not relocate the policy; it breaks the build of the
repository the policy exists to help validate.

ADDITION 5 already names the shape of the answer — *"where a platform requires a CI file inside a
sub-repository it stays a thin entrypoint to workflow-owned policy and tooling"* — so the correct
change set is four things, not one:

1. the tooling moves to gk-workflow;
2. gk-core's `Directory.Build.targets` guard invocation becomes **conditional** on the root being
   present, so a standalone clone still builds and skips the cross-repo gate;
3. gk-core's CI gets a thin entrypoint that invokes root-owned tooling instead of holding a copy;
4. the three project-file references are resolved individually — and two of them are `.ps1`, which
   the ps1-ban program is retiring, so they must not be given a new home.

**A classification by content-reference was tried and rejected as evidence.** It files
`guard-dal.py` and `verification-boundaries.v1.json` as engine-facing, because they mention
`SqliteConnection` and `data/seed` — as *strings they grep for*. A guard's subject matter is the
product; its job is the process. The discriminator that holds is ADDITION 5's own enumeration plus
the shape of the file, not which words appear inside it. Recorded because the wrong discriminator
produces a confident 132-file answer, and a confident wrong answer here would have been shipped into
a re-apply.

**Owner:** the `scripts/**` boundary in `tools/kvsplit/rules/ownership.v1.json`, together with the
four consumers above. Recorded here so it is an open item with an owner and a reason, which is what
`[ADDED 8]` condition 5 asks for, and not a silent pass.

## 9. Also in scope, also a stale authority

- **Fixed here.** `docs/keepverse-migration-plan.md` named `tasks/keepverse-split-plan.md` in
  its opening paragraph. The paragraph said "this document replaces", which was already
  correct — but it never said what this document's own standing *was*, so a reader searching for
  the plan's authority found only a reference to a superseded one. It now states the
  supersession explicitly and says which document wins a disagreement.
- **Reported, not fixed.** `gk-core/Directory.Build.props:27` cites
  `tasks/keepverse-split-plan.md` as the authority for the resolver contract. That is a stale
  authority and should name this plan. **Not fixed:** `gk-core` is a different repository, its
  source of truth is the legacy repository, and it is outside this lane's fence. One-line fix,
  owner is whoever holds that file.
- **Remeasured.** Audit rows A1 and A4 carried pre-merge figures that `[ADDED 1]` already
  declares stale. Both now read the import-SHA numbers and say so in the row. §1.1's
  reproduction block and §1.5's "Receives" column are left unedited with a warning above each,
  because they are reproductions at a named SHA and rewriting a measurement to match a later one
  falsifies it.

## 10. What ADDITION 5 asked for, and where each part landed

| ADDITION 5 requires | Where it is |
|---|---|
| authoritative plan updated | §1.6 tree, §1.6 boundary bullet, §6.4, opening paragraph, A1, A4, §1.1/§1.5 warnings |
| the topology decision updated | **outside this lane's fence** — see below |
| ownership rules updated | `layout.v1.json` `seal`; `ownership.v1.json` unchanged, which is the point |
| the transforms updated | no transform may reach a sealed repo; asserted in `rules.py`/`check.py` and tested. A new transform was **not** invented |
| the templates updated | no template exists for a sealed repo, and `load_rules` now refuses one |
| the task criteria updated | `gk-tests` at 4 files is the criterion's endpoint; the open CI-entrypoint criterion is recorded for `KS1.5` |
| the relevant principles updated | **outside this lane's fence** — see below |
| `stage` and `check` verified to enforce it | §4 and §5 above, with commands and output |

**Two of those are outside this lane's fence and are therefore reported, not done.** The
workspace ownership principle lives in `AGENTS.md` and `docs/PRINCIPLES.md`; the topology
decision lives in `docs/architecture/decisions/`. Both are real, and both are in the root
repository, but neither is in the file list this lane was given. The change they need is small
and specific:

- `AGENTS.md` and `docs/PRINCIPLES.md` already state that gk-workflow owns the development
  process and its single source of truth. What is missing is the corollary: **gk-tests is sealed,
  and no second copy of a shared gate belongs in any sub-repository.** That corollary is what
  makes the principle checkable rather than advisory.
- `docs/architecture/decisions/` needs a row stating gk-tests' reconciled role and pointing at
  this document, so a reader of the decision index reaches the seal rather than §6.4 of a plan.

Whoever holds those files should treat this file as the specification for that half.

## 11. Not done, on purpose

- **No file was moved into gk-tests.** Its honest role is a reserved one, and populating it
  would be inventing work.
- **No cross-repo suite was named or created.** None of the legacy monorepo's tests span
  repositories, so there is no specific suite to point at. Any suite proposed later must be
  justified by what it spans, not by the existence of an empty repository.
- **`scripts/**` was not re-routed.** §8, with the owner and the reason.
- **`ownership.v1.json` was not touched.** A topology change that adds a rule nobody needed
  would change the residue queue for no reason. The seal lives in `layout.v1.json`, which is
  where the statement "this repository is not a placement target" belongs.
