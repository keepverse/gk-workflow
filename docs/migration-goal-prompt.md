# Keepverse migration — extended goal prompt

Extends the owner's 2026-09-30 prompt. Every addition below is marked **[ADDED]** with the
reason it exists. Nothing marked ADDED narrows the owner's original text.

---

## [ADDED 1] What has already happened — read this before anything else

**The migration has already been applied.** This is not a fresh start, and a reader who
assumes it is will either re-run `apply` or misread the state it finds.

Measured at the time of writing, and to be re-verified rather than trusted:

| Repo | State |
|---|---|
| `gk-workflow` (root) | import commit applied, 5,155 files |
| `gk-core` | import commit applied, 3,863 files |
| `gk-forge` | import commit applied, 800 files |
| `gk-web` | import commit applied, 1,112 files |
| `gk-fusion` | import commit applied, 447 files |
| `gk-content` | import commit applied, 5 files |
| `gk-data` | import commit applied, 3,237 files |
| `gk-tests` | **untouched by design** — the split places no primary content here |
| `gk-assets` | **untouched by owner decision** — the art was migrated by hand |

- Source SHA imported: `effc51d9b55f78aa7a5c47e14eef0e61b690e5eb`
- Rules digest at import: `0fe37c774d29`
- Output digest at import: `b464968fa8e6`
- Import commits are **local and unpushed** in 7 repos. The owner's authorization 7 covers
  the pushes.

**Consequences for the agent picking this up:**

1. **Do not re-run `apply` against these repos.** It is not idempotent in the sense that
   matters: it is gated, it deletes what it does not place, and the repos now hold the
   imported tree rather than the pre-migration 4-file state. Re-verify with `stage` and
   `hash`/`lossy-check` instead.
2. **Authorizations 1 and 4 are already consumed.** Gate GM was exercised. The three
   `.gitignore` overwrites were applied under it. Do not treat either as pending.
3. **Authorizations 2, 3, 5, 6 and 7 remain open.** Phase A is the owner's separate
   stream; the reconcile charter has not been recorded; G3 and G2 have not been exercised;
   the pushes have not happened.
4. The reconciliation and residue figures in the authoritative plan predate the merge of
   `features/mega-merge` into `main`. **They are stale and must be remeasured.**

---

## [ADDED 2] Three hazards, each of which caused real data loss in this migration

These are not warnings. Each one fired.

### H1 — `apply` writes outside the staging directory, and it deletes

`apply` is the only verb that writes into the Keepverse repositories. It is **not** a dry
run, it has no preview mode, and `--confirm-migration-start` is the owner's gate — not a
"be careful" flag to be passed while testing.

- `--confirm-migration-start` was passed twice on what was intended as a dry run. Both
  times `apply` committed to three real repositories (gk-web 1,108 files, gk-data 3,173,
  gk-content 1). Both were caught in the same command and reverted with
  `git reset --hard HEAD~1` while the commits were still local and unpushed.
- **The delete loop runs regardless of what a repo receives.** A repo that receives zero
  staged files still has every unpreserved tracked file removed. "This repo gets nothing
  anyway" was false, and cost 209 of gk-assets' 228 files — the whole art tree.

**Rule: never pass `--confirm-migration-start` to learn what apply would do.** Compute the
answer from the `kvsplit` `report.json` — a run artefact that does not exist in any repository, so
re-derive it with `stage --plan-only` rather than looking for a committed copy — and from the target
repo, as this prompt's audit section requires.

### H2 — a report row is not content

The `report.json` does not exist in any repository (it is a `kvsplit` run artefact), and its
`reconciliation.placedPerRepo` counts only **primary** placements. The
`files` array also holds `copies` rows (the same file staged into a second repo) and
`template` rows (kvsplit emitting an `AGENTS.md` to seed a repo that lacks one).

gk-assets held 228 art files and **zero** primary placements, yet had two rows. A guard
keyed on "does this repo have rows" therefore did not fire, and the delete loop ran.

**Rule: a repo is out of scope when it has no row with `origin == "source"` and
`primary == true`.** That is now the implemented predicate and it is tested with the exact
failing row shape. Two repos are out of scope and must stay byte-identical:
**gk-assets** (owner decision) and **gk-tests** (by design).

### H3 — `preserve` means "the repo's", for deletion *and* for writing

`preserve` originally stopped `apply` deleting a file but not writing over it, so a
25-line template `AGENTS.md` would have replaced seven hand-authored 40-line guides.
`AGENTS.md` is now preserved in all nine repos and the root `.gitignore` is preserved too
(234 lines, versus a 23-line template that would have destroyed it).

**Rule: anything a repository already owns is `preserve`d, and `preserve` beats the split
in both directions.**

---

## [ADDED 3] Do not inherit a verification claim, including mine

The owner's original prompt already says to remeasure rather than reuse. Concretely, the
failure mode is arithmetic presented as a count:

- A summary reported "unplaced 0" from `placedPerRepo` while 209 files were being deleted
  from one repository. The aggregate was true and the migration was still wrong.
- A summary reported gk-assets as "receives 0 files" while the tool was about to remove
  209 of its files. That sentence was the direct cause.

**Rule: assert the per-repository post-condition, not only the aggregate.** For every
repository, before and after, record tracked file count and HEAD, and require them
byte-identical when the split places nothing primary into it. An aggregate that balances
is compatible with one repository being emptied.

---

## [ADDED 4] Two audit rows the original list is missing

Add to the proof set:

- **A6 — out-of-scope invariance.** For gk-assets and gk-tests, tracked file count and
  HEAD are identical before and after, and `git status` is clean. This is the check that
  would have caught H1's art loss.
- **A7 — private-content absence from public repository *history*, not just its working
  tree.** The original prompt says "and their history"; make it an explicit row, because
  the check is `git rev-list --objects --all` over the public repo, not a file listing.

---

## [ADDED 5] gk-tests — reconcile, do not populate

The owner's workspace ownership principle supersedes the plan's assignment of cross-repo
gate definitions and suites to gk-tests. The principle says gk-workflow owns the
development process and its single source of truth: shared guards, verification and
migration harnesses, orchestration tools, path rules, CI policy, contributor standards,
architecture decisions, principles, plans, task records and development documentation.

Therefore:

- **`gk-tests` must not hold shared gate definitions, shared harness logic, or workspace
  policy.** Those are gk-workflow's, and a second copy in a sub-repository is a competing
  copy — the thing the principle forbids.
- Where a platform requires a CI file inside a sub-repository, it stays a **thin
  entrypoint** to workflow-owned policy and tooling.
- A product generator belongs with the repository that owns its output; gk-forge keeps
  generator code.

**Required, together in one change set — not piecemeal:** update the authoritative plan,
the topology decision, the ownership rules, the transforms, the templates, the task
criteria, and the relevant principles. Then **verify that `stage` and `check` enforce the
resulting ownership**, and show that verification. A doc-only change is not a topology
change.

**Do not invent work to populate gk-tests.** If its honest role after this reconciliation
is "the repository that holds the cross-repo test *suites* that genuinely span
repositories, and nothing else", then say so and leave it at 4 files. An empty repository
with a written rationale is a better outcome than a populated one with invented content.

---

## [ADDED 6] The reconciliation charter is recorded here

The owner's authorization 3 names the charter. Recording it, as required, before any
worker starts:

| Field | Value |
|---|---|
| Runtimes | local Windows; Python; .NET; Node |
| Models | **only** `opencode/space-bunny-free`, per `.claude/opencode-agents/allowed-models.json` |
| Thinking | `max` for reconciliation and audit work; `high` for mechanical edits |
| Token budget per lane | none configured (`tokensPerLane: null`) |
| Concurrency ceiling | none configured (`maxConcurrentLanes: null`) |
| Model fallback | **none.** A credit or quota error stops that lane and is reported |
| Stop rule | continue until the objective is proven, or a specific irreducible blocker remains |
| Evidence | disk-backed, exact-SHA |

**No worker may use a model outside that list.** There are 204 models visible to the
harness and exactly one is chartered. Do not substitute a profile's model — the two
configured agent profiles use `pi` with `opencode-go/muse-spark-1.3-contributor` and
`anthropic/claude-opus-5`, and **neither is chartered for this run**.

---

## [ADDED 7] Agent topology

Context collection and reconciliation are separate lanes with separate fences, because a
worker holding both will reconcile against its own assumptions.

1. **Context collector (read-only).** Establishes and writes down the measured current
   state: reconciliation at the current SHA, residue composition, per-repo tracked counts
   and HEADs, the todo's open blocks, the import commits' presence and push state, and the
   gk-assets/gk-tests invariance baseline. Its output is the input every other lane uses.
   It edits **no** repository.
2. **Reconciliation workers.** One per residue kind, each closing **only its own residue
   ids**, each re-running `stage` after its own change, each proving the ids it claims are
   gone **and that no replacement id appeared**. Residue ids are stable, so an id that
   moves means the fix changed the shape of the problem.
3. **Topology worker (gk-tests reconciliation).** Owns [ADDED 5] as a single change set.
   Sequenced after the context collector, because it rewrites rules and must not race the
   residue workers.
4. **Audit worker.** Owns the proof set, including A6 and A7. Runs after reconciliation;
   an audit against a moving tree proves nothing.

Do not deploy a worker whose fence overlaps another's. Overlapping fences in this repo
have repeatedly cost whole days.

---

## [ADDED 8] What "done" means here, stated so it cannot be argued later

The migration is complete when **all** of these hold, each with recorded evidence:

1. Phase A's five exit checks pass, verified by the owner's stream and recorded.
2. The reconciliation charter in [ADDED 6] is on disk.
3. `stage` at the pinned SHA reports `tracked = placed + dropped + unplaced` with
   `unplaced 0`, `balanced True`, and the same SHA plus the same rules reproduces the same
   output digest.
4. `lossy-check` reports **zero** findings.
5. Every residue id is either closed with no replacement, or named in a report as an open
   item with its owner and its reason. **A carried residue is an open item, not a pass.**
6. A6: gk-assets and gk-tests tracked counts and HEADs unchanged; every other repo's
   tracked count matches its `report.json` count — that file does not exist in any repository, it is
   a `stage` run artefact, so this clause is checkable only against a fresh `stage` run).
7. A7: no derived content in any public repository's working tree **or history**.
8. gk-core builds and tests with every private sibling absent.
9. Per-repository build and test results at the lock SHAs.
10. Generators `--check` byte-identical to the import SHA; goldens unchanged.
11. Web served from the server; the real live lawn entered from the Keepverse layout; a
    real allocation read back through the normal path.
12. The gk-tests topology reconciliation in [ADDED 5] is complete **as one change set**
    and `stage`/`check` demonstrably enforce it.
13. The import commits and the cutover commits are pushed, without force.
14. Every authorized todo block carries evidence matching its original criterion.

If any of these is unmet, the migration is **not complete**, and the report says which one
and why. A blocked or partly verified migration is never called complete.
