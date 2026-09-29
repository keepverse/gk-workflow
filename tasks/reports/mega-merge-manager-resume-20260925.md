# Manager resume report — 2026-09-25

**Session:** `mega-merge-program-manager-20260925-f78e` (direct, `features/mega-merge`)
**Owner charter (re-stated this session):** OpenCode CLI lanes, `opencode/space-bunny-free` max effort,
uncapped per lane, no fallback model; a credit/quota error stops the lane and is reported; no configured
lane ceiling — the manager still sizes each wave to what it can accept.
**Owner answers applied:** the `.commandcode` recommended set (track the taste files, keep
`settings.json` local-only behind a narrow ignore, record the policy in `decisions.md`), and one repair
lane for the worktree-cleanup tool before committing it.

## What this session changed, as commits

| # | Commit | What |
|---|---|---|
| 1 | `a313713e3` | **Gate unblock**: preserved the orphaned cleanup-tool work on `adopt/worktree-cleanup-20260925@6d2c48460`, removed it from the main tree, retired its session record; applied the owner's `.commandcode` routing; harvested four briefs + a record the paused manager left uncommitted. |
| 2 | `c8887089f` | Merged the paused manager's evidence plane (50 commits) at its tip. |
| 3 | `78c6b3a99` | **EPL1.1** closed power-class registry + C# mirror, exact SHA `8334a1d61`. |
| 4 | `78d07423c` | **SSH7.1/SSH8.4** tuning-revision reader guard, exact SHA `a120ce2d8`. |
| 5 | `d7fbf7d1d` | **RS-F27** defeat ledger floor, exact SHA `4f78ed6c9`. |
| 6 | `6b0397849` | Routed **TVB-F39** (found by the gate, below). |
| 7 | `c059aab4e` | Session boundary: 39 crossings → 0. |
| 8-9 | `1c4d2a6d3`… | resume-31 boundary + **TVB-F37** repair accepted (see below). |
| 10-14 | `071098ddc`… | **CAI2.2** salvaged from a failed lane + PT-F39 routed + closure. |
| 15-18 | `1419a2351`… | resume-32's salvaged test contribution; **BP1.11/BP1.12 ticked** (they shipped at `005239e4b`). |
| 19-21 | `d6b3b3dd9`… | resume-33's blocked-with-evidence half accepted; P11.1r left open by design. |
| 22-23 | `57a1224d3`, `f91a5b138` | **TVB-F39 fix**: an injector cell owns its pack; all three hosts build in one environment. |

22 non-merge commits + 7 merges. Every merge names the exact reviewed SHA; every routed finding has an
open row in the owning program's todo.

## The five lanes this session ran

| Lane | Outcome | Manager verdict |
|---|---|---|
| `resume-31-cleanup-repair` | done — 19 tests (10 + 9 new), fail-open reproduced | **accepted** `6b36c52cd`; TVB-F37 closed |
| `resume-32-bp1112` | failed at turn 41 — BP1.11/12 already shipped; one test contribution | **salvaged + accepted** `1419a2351` |
| `resume-33-p11-1r` | blocked with evidence — three measured bars, in-fence half landed | **accepted** `d6b3b3dd9`; P11.1r open for owner design |
| `resume-34-cai2-2` | failed mid-`verify-change` — 317 lines + a test file | **salvaged + accepted** `071098ddc` |
| `resume-35-slnx-topology` | partial — cell-owns-its-pack, honest gaps | **accepted** `57a1224d3` |

The repair lane's defect and fix, reproduced by the manager independently:

```
scenario: linked worktree whose tracked session record is stale (status merged) but whose path is
          owned by a LIVE OpenCode lane (meta.json cwd + status.json state=running)

OLD core -> should-clean, blockers=[]                     <- a live lane's worktree was removable
NEW core -> manual-review, blockers=[managed-runner-session, runner-lane-not-finished]
```

## Findings routed to their owning programs

- **TVB-F37** — cleanup-tool runner discovery blind to OpenCode/cmdc owners. **Fixed** `6b36c52cd`.
- **TVB-F38** — the pre-existing `.commandcode/skills/**` citation red (11 HIGH). Open, XS.
- **TVB-F39** — the solution could not build in any single environment. **Fixed** `57a1224d3`.
- **PT-F39** — `PassiveTreeEndpointsTests.Post_anOwnedTierOneNodeAfterOpeningTierOne_contributes` is
  red at HEAD. Open. Its root cause is the same one `P11.1r` blocked on: that fixture's node atom is
  deliberately `stat.modify`, an ignored kind on this projection.
- **P11.1r** — remains open **by design**: delivering a `stat.modify` tree atom needs a primary carrier
  (`StatSystem`'s session bag or an `IStatModifierPlugin` on the lawn) plus a reviewed `decisions.md`
  row. That is an owner design decision, not a lane's to invent.

## The merged-head gate — the program's terminal gate

The gate found TVB-F39 on its first honest run: `post_merge_check.py` builds `FusionRpg.slnx`, and the
solution's three injector hosts could not compile in one environment. The fix landed and the gate's own
build phase now reads:

```
=== build FusionRpg.slnx (legal-game/interop limitations are reported as BLOCKED) ===
build_exit=0  error_lines=0  projects_with_errors=0
```

The first run of that build aborted only because this session committed the closure while the gate held
a head assertion — the manager's own mistake, corrected by re-running at the frozen head. The final
verdict is recorded in `tasks/reports/mega-merge-post-merge-phase0-20260925.md`'s successor, written
when this run returns.

## Honest gaps

1. **Live proof remains owner-blocked.** `live-slot.ps1` reports no pool root and neither
   `FUSIONRPG_GAME_POOL` nor `FUSIONRPG_GAME_SOURCE` is set on this machine, so the active-match
   browser proof and the legal live proof cannot be produced here. No lane was briefed to fake one.
2. **Three of five lanes failed rather than finished.** Their work was salvaged and accepted on
   manager-run evidence, and each record says so; but a lane that dies mid-`verify-change` produced no
   final report, so for those the acceptance rests on the manager's own commands, which are listed in
   each acceptance artifact.
3. **Lane 35's limitation is real and carried forward**: the whole-solution `Build succeeded` string
   was never observed on this machine because an external process held an `obj/bin` sharing lock on one
   test project (reproduced with the new targets renamed away, so independent of the change). The gate
   run above is the observation that closes it.
4. **The gate's own env contract is still the loader-wide pair** (`Get-LegalGameEvidenceError`
   validates only `FUSIONRPG_GAME_DIR` + `FUSIONRPG_ML_GAMEDIR`); a full three-host run needs the
   per-cell variables exported. That file is pipeline-plane and outside every lane's fence — the
   manager's to fix, and it is not yet fixed.
5. **The deploy script was not run end-to-end** (it writes into a game install and launches the
   game); its exact build invocations were reproduced with a temp `OutputPath`. Named
   `deploy-play.ps1` when this was first written — that file is **superseded** at this head by the
   in-flight PowerShell→Python port, so read the port's own record for its current name.

---

# Manager addendum — 2026-09-26

Owner priority this day: *finish leftover work, merge to `features/mega-merge` and then to main before
the Keepverse migration, and clear the worktrees — including ones holding Seedsmith corpus that was
never validated or merged.* This addendum records what was merged, a **correction** to gap 1 above,
and the measured cleanup inventory.

## A. Correction: live proof was never blocked by configuration

Gap 1 above says the live pool has no root because `FUSIONRPG_GAME_POOL` and `FUSIONRPG_GAME_SOURCE`
are unset. **That check was wrong, and so is the conclusion.** It read the *process* environment; this
project keeps its local configuration in **`.env`**, which the machine-local setup script copies into
each worktree. `.env` on this machine carries `FUSIONRPG_ML_GAMEDIR` (plus `FUSIONRPG_ML_GAMEDIR_DEFAULT`
and `FUSIONRPG_GAME_PROFILE`), the path exists, and it contains `BepInEx`, `MelonLoader`, `Mods`,
`UserData` — a legal MelonLoader install. `AGENTS.md` also states the default game needs no flag or
env var, because the deploy script already points at it. That sentence was written against
`deploy-play.ps1`, now **superseded** by the Python port, so confirm the current entry point before
a probe.

So: **a live probe is available; only the three-slot *pool* is unconfigured** (that needs
`FUSIONRPG_GAME_POOL` / `FUSIONRPG_GAME_SOURCE`). No lane will be told that live proof is impossible,
and none will fake one. (Also corrected: `live-slot.ps1` is at `scripts/live-slot.ps1`, not the
`.claude/cmdc-agents/scripts/` path this report's tooling list implied.)

## B. Merged today

| Merge | Row | Reviewed SHA | Evidence |
|---|---|---|---|
| `08eec6b38` | the program status reader + the AGENTS.md status gate | `15a346f79` | 60/60 tools tests; identical reading in a detached clean checkout; guard 693/693; AGENTS.md citations 0 HIGH |
| `10efdd090` | close the stale worktree-cleanup gap report | — | five closure legs re-verified on this head, not taken from the lane's report |
| `062860c22` | doc-citation guard: a dot-directory was invisible | `fc209a8e3` | 13/13 doc-citation tests (6 before), guard 700/700 (693 before), repo-wide `--strict` exit 0 with 25 925 citations (25 860 before) |

`08eec6b38` and `062860c22` were merged into a main worktree that another stream was using for a
PowerShell→Python deploy port; the second merge therefore also carries that stream's staged deletion of
`scripts/deploy-play.ps1` — a file **superseded** by that port at this head. It was not reviewed by the
manager and is not evidence for either row.

## C. Cleanup inventory (measured, `git worktree list` + per-worktree porcelain)

190 worktrees besides the main checkout. **10 branches carry commits not in `features/mega-merge`**;
74 worktrees have local changes; **8 hold untracked generated content**.

The two that matter, and the answer to "those seeds were never validated":

**`corpus/bcu212` — 706 untracked files under `gk-data/packs/fusion/data/seed/passive-tree`, 1 unmerged commit.** This is
the interrupted BCU2.12 run. The binder's read-only check settles it:

```
dotnet run --project gk-forge/tools/TreeBinder -c Release -- --check     # in the corpus worktree
exit 0        <- the COMMITTED gk-data/packs/fusion/data/generated/passive-tree is not stale
REFUSED  1120 distinct node ids
         612  affix does not exist in the shipped seed content
         507  affix is a pool reference where a node is required
           1  a node's affixIds must be 1..3, got 0 (R6)
```

`--check` exiting 0 while refusing 1120 node ids is the decisive combination: the committed generated
tree is fine, and **the 706 untracked files have never been bound.** They cannot be merged — doing so
would push refusals into `gk-data/packs/fusion/data/generated`. This matches the accepted audit's own verdict that the run
is incomplete at 361/904 and must not be described as a finished corpus
(`tasks/reports/seedsmith-p1-audit-final-20260925.md`; accepted at `fc144f2c`, GREEN, an ancestor of this
head). **Recommendation: do not merge this corpus; archive or discard it, and regenerate only after
the missing atoms exist and a model run is authorized.** No file was deleted and no cleanup command
was run.

**`codex/actor-hud-bottom-anchor-20260916` — 39 unmerged commits, 8348 changed paths, 6932 untracked
generated files** (its untracked sample is `tmp/bep-verify/data/generated/creatures/*.json`, i.e. output
under `tmp/`, not a corpus at all). This is the largest single item in the cleanup and needs its own
decision: recover the 39 commits, or confirm the branch is superseded.

The other six untracked-generated worktrees are single files each (`gk-data/packs/fusion/data/seed/atoms/generated/
_family-expand.manifest.json` ×4, `gk-core/data/tuning/aptitude-auto-assign-catalog.v1.json`,
`gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json`) — the last of which is EPL1.1's registry, already
merged and accepted at `8334a1d61`, so that worktree's copy is a leftover, not pending work.

## D. Every unmerged branch, triaged (not just counted)

Ten branches carry commits not in `features/mega-merge`. `git cherry` separates the two cases that look
identical in a count: a commit that is **patch-equivalent** to something already integrated (nothing to
finish) from a **unique** one (real leftover). Per branch, what it actually contains and what should
happen:

| Branch | Unique | What it is | Verdict |
|---|--:|---|---|
| `codex/actor-hud-bottom-anchor-20260916` | 35 | injector vfx + actor-hud fixes, a 3.9 zombie-HP interop width fix, a `data/tuning/actor-hud.v3→v7` chain, a "v7 live proof" doc — 146 files | **Review lane dispatched** (`actor-hud-merge-20260926`). Biggest leftover; the tuning chain must be proven published, not hand-written. |
| `corpus/bcu212` | 1 | the **J9 driver fix** — `_j9_batch_run.py`, `generate_codex.py`, `generate_tree.py`, `test_j9_batch_run.py` | **Merge the code, never the corpus.** The 1 commit is real tool work; the 706 untracked files beside it are the unbindable corpus of §C. |
| `corpus/bcu211` | 1 | item-seedgen full run, "56 files, gaps 931 → 770" | **Validate before any merge.** Generated item data whose validity is unproven on this head. |
| `opencode/ipc-3e` | 1 | `briefkit/avoid_list.py` + 139 lines of tests + a fixture, marked `WIP … brief half still open` | **Do not merge as-is.** Measured: 11/14 tests pass, 3 fail with `render_brief() got an unexpected keyword argument 'avoid_terms'`, and nothing imports the helper. The helper is done and tested; the one-parameter wiring into `render_brief` is missing. A small follow-up lane, not a merge. |
| `adopt/worktree-cleanup-20260925` | 1 | the pre-repair snapshot of the cleanup tooling | **Superseded** by the merged repair `6b36c52cd`; keep as provenance, do not merge. |
| `opencode/resume-30-commandcode-config-review` | 1 | evidence bundle + its session record | **Land the evidence** — the owner already applied its recommendations at `a313713e3`. |
| `review/resume-28b-effect-pipeline-epl1-1-20260925` | 2 | one report file | **Land** (doc). |
| `review/resume-29-strain-reader-guard-20260925` | 1 | one report file | **Land** (doc). |
| `review/seedsmith-p1-audit-20260925` | 0 | — | **Already integrated by another route.** Nothing to finish. |
| `review/resume-00a-final-20260925` | 0 | — | **Already integrated by another route.** Nothing to finish. |

So the "10 unmerged branches" figure is really **three items of real work** (actor-hud, the BCU2.12
driver fix, the bcu211 corpus), **one half-finished helper**, **four doc/evidence landings**, **one
superseded snapshot**, and **two already done**. Nothing here needs a decision I cannot make from
evidence except deleting a corpus, which is the owner's.

## E. What is now measurable that was not


`python gk-core/scripts/program_status.py` answers done/left in **task blocks** (AGENTS.md's rule made
runnable): **118 programs, 670 open, 2 889 done, 2 unmeasured** — `player-guide` and
`world-map-gaps-followup` have no declared shape and are reported unmeasured, never as zero. The
largest remainders have no lane on them: `trade-network` 162 (a docs-only umbrella specced 2026-09-20,
never scheduled), `npc-story-events` 93 (approved 2026-09-22, "ready for lanes", its one build attempt
abandoned), `narrative-seed` 50 (stalled on owner gates CP1/NSG1/NSG4), `combat-ai` 27,
`onboarding-rift` 26.

Two findings that tool surfaced and that are **routed, not fixed**:
`tasks/combat-ai-todo.md:9` states "46 done, 25 open" where the file measures 47/27, on a line that
says "counted as TASK BLOCKS" and then cites `grep -c` — and its ledger has no event after 2026-09-23
although six commits edited the todo. `tasks/onboarding-rift-todo.md`'s header claims a story ledger
and media provenance registry are implemented while its own Tasks 6–7 (the story ledger) are `OPEN`
and no implementation exists in the tree.

## E. Next steps, in the owner's order

1. **Cleanup decisions** (§C): the BCU2.12 corpus, then the 39-commit `actor-hud` branch, then the
   10 unmerged branches. Nothing is deleted before the owner rules on each.
2. **Finish leftovers, then merge to main** — the owner wants `features/mega-merge` → main settled
   before the Keepverse migration.
3. **A verification-plane row**: `verify-change.ps1`'s guard step leaves a `testhost` holding
   `FusionRpg.Guard.Tests.dll`, so the next build of that project collides (`MSB3027` / `exit -1`).
   It blocked this session's own gate twice. Precise reproduction, measured on this head:

   ```
   verify-change.ps1 -Paths <a path mapping to the guard project> -Session <id>
     -> dotnet test spawns tests/FusionRpg.Guard.Tests/bin/Release/net8.0/testhost.exe
     -> that testhost OUTLIVES the dotnet test call (observed still running after the script exited)
     -> the next build of the same project: MSB3027 "Could not copy ... FusionRpg.Guard.Tests.dll …
        The file is locked by: testhost (NNNN)"
   ```

   The same command run as two explicit steps — `dotnet build` once, then
   `dotnet test --no-build` — never collides, which is the discipline session
   `cold-process-test-build-20260912-e5b1` established for tool tests. **Every change whose paths map
   to the guard project is affected**, so this is not a one-session annoyance.

   **Decision needed, because it interacts with the ps1-ban program** (which is retiring this very
   script): either (a) the surgical fix now — make the guard step build once and test with
   `--no-build`, which removes a race without adding PowerShell, or (b) fold it into the port, since
   the owner's 2026-09-25 ruling says a `.ps1` touched for a fix is a port candidate and the capability
   should move to Python rather than grow in PowerShell. I did not start either without that call,
   because the ps1-ban stream is mid-flight on the same tooling.
4. **BCU2.12 resume** still needs explicit owner authorization for a model run; the audit gate is
   satisfied, the authorization is not on record.

---

# Manager addendum F — 2026-09-26 (the cleanup phase, the verification plane, and one incident I caused)

Everything below is measured on this tree. Reproduce before quoting.

## F.1 The cleanup phase is merged, and the tool was wrong twice before it worked

`gk-core/scripts/retire_worktrees.py` merged at `1c45b5944`, with two defect fixes after it (`d1f716d7a`,
`8097f5eaf`). Three defects, each found by *running* the tool rather than reading it:

1. **Ownership resolved against the cwd, not the main checkout.** The lane registries under
   `.claude/{opencode,cmdc}-agents/agents/` are **untracked**, so they exist in the main checkout and
   are absent from a linked worktree; and `tasks/sessions/` in a worktree is a fork-time snapshot, so
   a session created after the fork is missing there too. Both errors push worktrees toward
   *retirable* — the direction that deletes somebody's work. Measured: **108 retirable read from a
   worktree, 39 from main.** The 108 figure I reported earlier in this session was 69 too permissive.
2. **`--why <group> --apply` removed nothing and exited 0.** `--why` returned before the apply block,
   so the filter and the action were mutually exclusive. A removal tool that looks like it worked is
   worse than one that fails loudly.
3. **The apply loop called git with no `cwd`**, so `git worktree remove` ran in whichever repository
   the module was imported from. Same class as the `git cherry` cwd bug, in the one code path where a
   wrong cwd deletes nothing while claiming to. `git_diag` now keeps stderr, because the real reason
   (`failed to delete ...: Filename too long`) is the thing an operator needs.

**Applied:** 29 worktrees retired (9 `review/`, 2 `prep/`, 1 `codex/`, 17 under `Temp/opencode`),
2 failed with a Windows `Filename too long` on nested build output, 6 still retirable. Both live lanes
KEPT throughout, for the right reasons.

**Deliberately not retired:** `ps1ban/l4-artifacts`. The ps1-ban program is running, and its active
session record does not name the worktree its lane is using — so the tool cannot see it. That is a
finding for that program, not something to override.

**Two of my own records were stale `active` after their merges** (`worktree-retire-20260926`,
`citation-dotpath-guard-20260926`), closed at `869b0cfee`. A stale `active` record is not cosmetic: it
is ownership proof. The tool caught this class in its own plan; the manager's ledger was the instance.

## F.2 The verification plane: the Python planner, and the guard that was reading my live session list

`gk-core/scripts/verify-change.py` + `gk-core/scripts/lib/verification_boundaries.py` merged at `f5ed749de`. The
testhost race is gone **by construction** — each project is built once, memoized on its absolute path,
and every test for it runs `--no-build` — and the *discipline* is pinned rather than the race, because
a bad thing to pin is one that reproduces by luck.

The port is pinned by parity, not trusted: text output byte-equal to the `.ps1`, json an equal object,
the unmapped-path refusal carrying the same exit code, and the library answering 84 planted questions
against the real `VerificationBoundaries.ps1`. That comparison found three real port bugs.

**Then the merged head was red, and the first cause was mine.** I merged the port without its three
doc edits, because the ps1-ban stream held `AGENTS.md`, `CLAUDE.md` and `testing-standard.md`
uncommitted. But the port's own guard test pins that documentation, so the port and those documents
are **one indivisible change** — the split produced a red gate, which is worse than not landing.
Lesson recorded: *a guard test that pins a document makes that file part of the change's atom.*

Both conflicts were then resolved as the **union** of the two sides, by a resolver that refuses unless
the union is exact. That refusal earned its keep: the first attempt took `theirs` and would have
silently dropped the `deploy-play.py` rename. Each region had two independent renames in play, not one.

`34ba133a6` fixed the second red honestly. `Planner_rejects_a_path_outside_the_active_session_scope`
hardcoded `README.md` and asserted the active session did not claim it — so it was a reading of
whoever's session records were active, not of the planner. It passed where it was written and failed
on the integration branch, because `ActiveSession()` returns the first `active` record alphabetically
and that is a manager session that legitimately claims `README.md`. **A guard that passes by luck of
machine state is a false green.** The path is now chosen at runtime from the session's own fence.

## F.3 Incident: I reverted another stream's commit

While reverting the port merge I ran `git revert -m 1 --no-edit HEAD` on a HEAD I had read seconds
earlier. The ps1-ban stream had committed in between, so I reverted **their** merge commit
`506a5802b`, which had legitimately widened *my* manager session record to 56 paths and recorded the
crossing. Restored by `020c1caec` (a revert of the revert) — forward, no history rewriting, no
`reset`, nothing of theirs touched. The record reads 56 paths with the crossing note intact.

The real defect was mine: I treated a HEAD I had observed as if it were still HEAD. The correct
sequence is to re-read HEAD in the same command that acts on it, or to name the SHA explicitly.

## F.4 actor-hud: three blockers, three lanes, and a route that had never existed

`merge/actor-hud-bottom-anchor-20260926` is a 40-commit branch. Its review (`9157c1811`, then
`648b07d1a`) said "do not merge" for two reasons; both are now closed and one more was found.

1. **"The Injector has no compile evidence" was a false blocker the lane caused.** It read
   `AGENTS.md`'s `FUSIONRPG_GAME_DIR` line and reported an unset variable as a property of the branch.
   It is a property of a shell: `Directory.Build.props` deliberately does **not** let the loader-wide
   `FUSIONRPG_ML_GAMEDIR` reach a MelonLoader host (two cells), so the sanctioned call is an explicit
   `-p:MlGameDir`. With that, `INJECTOR COMPILE GUARD OK` — 57 changed injector files, including the
   lane's own `SpriteSpan` edit, now compiler-verified.
2. **The import-guard red needed no ADR.** The lane believed the fix changed the FE→game contract
   across `foldActorHud` / `hudSnapshotsEqual` / 4 call sites. It did not: the game plane needed one
   pure value, so a React-free extraction (`gk-web/web/fusion-rpg-web/src/lib/actorSurfaceCatalog.ts`) served
   it, `git diff --stat` over the fold contract is **empty**, and `importGuard.test.ts` was not edited.
   The lane also found the guard's blind spot: it only sees *direct* specifiers, so a second React path
   via `actorHudElementArt.ts` would have passed it. A transitive walk showed 6 reachable modules
   after the fix, identical to the merge base.
3. **The route the client has always called did not exist.** `GET /api/catalogs/actor-surface` —
   requested by `gk-web/web/fusion-rpg-web/src/lib/bus/actorSurface.ts:165` since before this branch, and
   **never mapped in any branch** (`git log -S ... --all -- gk-core/src/FusionRpg.Server` is empty). It was
   pre-existing debt; this branch made it fatal by depending on `hudPresentation`. Added at
   `748929af2`, and the lane found a second bug on the way: `BuildDto()` dropped
   `ActorSheetCatalog.DefaultOpen`, so mapping the route alone would have traded dead glyphs for a
   broken ActorSheet.
4. **The server read the catalog version without the glyphs.** Server read `element-catalog.v1.json`
   (0 `hudGlyph`), Injector read `v2` (6). Fixed at `4b7041615`. Falsified by reverting: 3 new
   assertions fail, and **7 pre-existing ones stay green with the bug present** — direct evidence the
   old suite was blind. Live A/B on two real servers: non-null `hudGlyph` **0 of 7 → 6 of 7**, with the
   SPA fallback still answering a no-such-route on the same process as the control.

**Still unproven: no frame was ever rendered.** No pool slot was free, and the default install is held
by a live server on another session's port. The lane correctly declined to deploy over a shared
install, and correctly declined to call a static trace a render.

## F.5 Ruled out, with the check that ruled it out

- **"the nine pick-refusal codes are stale" is not a finding.** `fda33f0ed` is an ancestor of the
  integration head and `PlayerSpeciesMaterialiseCallerGuardTests` is **5/5 green here**. It is red only
  on branches forked before that commit. Two lanes reported it as a pre-existing red; it is a
  stale-branch artifact.
- **`gk-core/data/tuning/**` was never hand-edited on the actor-hud branch.**
  `git log --diff-filter=M features/mega-merge..<branch> -- gk-core/data/tuning/` is **empty**; all five tuning
  commits are `--diff-filter=A`, and the first review replayed `actor-hud.v3..v7` plus
  `element-catalog.v2` through `gk-core/tools/tuning/publish.py` byte-for-byte.
- **The 108/39 worktree swing was not a real difference in the tree** — it was the tool reading
  ownership from a worktree that structurally cannot see the evidence (F.1).

## F.6 New finding, highest value per line: the guard that exists for this bug class, not covering it

`gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs` exists precisely for "two readers
disagree about a tuning version, so a retune reaches one path and not another". Its real-tree rows
covered `action-base` and `action-rungs` — **not `element-catalog`**, the domain that had just
demonstrated the bug. One row makes it green today (`[1, 1]` on the integration head) and red for any
future publish that leaves a reader behind. This is the "unmapped path is a verification-boundary
defect" rule applied to a guard rather than to a test.

## F.7 Ruled out of the cleanup scope, on purpose

`ps1ban/*` and every branch named by a **live** lane registry were left alone: 127 of the 160 kept
worktrees are kept for that reason. 151 branches are claimed by lane registries, and most of those
lanes finished long ago — so the *registry* is the stale thing, and pruning it is a separate,
owner-visible decision, not something a cleanup pass should guess at.


---

# Manager addendum G — 2026-09-26 (the actor-hud merge, and a corpus claim that inverted)

## G.1 `merge/actor-hud-bottom-anchor-20260926` is merged — `679501f7f`, 157 files

The review said "do not merge" for two reasons. Both closed, and closing them found two more.

| # | Blocker | Closed by | Evidence |
|---|---|---|---|
| 1 | "no injector compile evidence" | a false blocker the review caused | `Directory.Build.props` will not let the loader-wide `FUSIONRPG_ML_GAMEDIR` reach a MelonLoader host (two cells); the sanctioned call is `-p:MlGameDir`. With it: **INJECTOR COMPILE GUARD OK**, 57 files compiler-verified |
| 2 | import-guard red "needs an ADR" | a React-free extraction | the game plane needed one pure value; `git diff --stat` over `foldActorHud`/`lawnViewModel`/`lawnProjectorFold` is **empty**; `importGuard.test.ts` unedited |
| 3 | the route the client always called | `748929af2` | `GET /api/catalogs/actor-surface` unmapped in **every** branch; mapping it exposed `BuildDto()` dropping `ActorSheetCatalog.DefaultOpen` |
| 4 | server read the catalog without glyphs | `4b7041615` | v1 has 0 `hudGlyph`, v2 has 6. Falsified: 3 new assertions fail with the reader reverted and **7 pre-existing ones stay green with the bug present** |

Also found: the import guard reads **direct** specifiers only, so a second React path via
`actorHudElementArt.ts` passed it. A transitive walk (39 roots, 86 modules) now matches the merge base.

**Rendered, not assumed** (browser-proof lane, `f207e0337`): control first — unmapped paths answer
`200 text/html`, so the route's `200 application/json` means something. Then the page's own fetch
path: `200 image/png` on `flame.png` and `crystal.png`. Then pixels: flame and crystal visible
server-fed, **neither** visible when only the route answers the fallback.

## G.2 The merged-head gate: two thirds green, and the authoritative one could not run

| Check | Result |
|---|---|
| Guard suite | **exit 0** |
| Declared core surface (`gk-core/tests/core-test-projects.v1.json`) | **67 projects, 0 red, 0 missing** |
| Solution build | exit 1 — **my** env var |
| `post_merge_check.py` (authoritative) | **did not run** |

The build failure is mine and the repo caught it: I set `FUSIONRPG_GAME_DIR_PVZRH_3_8_1` to the
**3.9** MelonLoader pack, and `Directory.Build.targets:59` refused by name —
`error FUSIONRPG0002: Cell pvzrh-3.8.1 x BepInEx was pointed at a pack that belongs to another cell`.
That is the cell fingerprinting working exactly as designed, and it is the strongest evidence in this
addendum that the pack/loader matrix is safe.

The authoritative gate was **not** worked around. It requires a CLEAN checkout **and** the literal
branch `features/mega-merge`; the main worktree carries two uncommitted files belonging to the
ps1-ban stream, and only the main worktree may hold that branch. A clean detached worktree at the
merged SHA satisfies the SHA half, not the branch half, so the phases were run there and the result
is labelled substitute evidence. **The authoritative verdict is still owed and is blocked on another
stream committing two files.**

## G.3 `corpus/bcu211` was aborted, and its headline number is a regression

Its commit subject claims `gaps 931 -> 770`. Measured, same command both sides:

```
before the attempt    931 gap /   612 note / 153 not_measured
resolved merge       1672 gap / 10533 note / 153 not_measured
```

**+741 gaps, not −161.** The merge was aborted, the tree restored to 931/612/153 exactly, and
nothing landed. I had written the revert condition into the merge message before measuring.

The resolution was not the cause, and establishing that mattered more than the merge would have:

- 52 add/add files. 19 verified strict supersets. 4 are run ledgers / a blocked-combination record.
- **29 carry the same item ids with different content.** The only difference is one field: this side
  has `successorOf`, the run does not — a missing post-pass, not a merge decision.
  `successor_edges.py:10` says the field is applied additively from the authored registry, so the
  sanctioned tool was re-run: `--dry-run` planned **398** restamps, `--write` applied them,
  `_meta.amendments` records it. The metric still went to 1672.
- **Provenance cannot adjudicate the 29:** every `_meta` key is byte-identical on both sides —
  `promptVersion`, `contractVersion`, `model`, `registryVersions`, even `authoredUtc`. Not two
  generations of the file. "The newer run wins" has no evidence behind it.

This **confirms and quantifies** the 2026-09-23 reading already in BCU2.11 (stale base 1 ahead /
1160 behind; regenerate, never hand-merge). I re-derived the whole thing before finding that the
ledger had already answered it — the cost of not reading the owning program's block first.

**The regeneration is not progress:** worktree `corpus-bcu211b` is based on `f0661fc13` (~1160
commits behind), holds **73 uncommitted** entries, has **0** commits not on head, and its run log
`D:\tmp\cu211b-run.log` is **absent**.

## G.4 `corpus/bcu212` closed out as a content no-op

Its one commit touched four seedsmith files; all four resolve to this side, decided by comparison
rather than by picking:

- `_j9_batch_run.py` (add/add): ours defines 8 top-level names to the branch's 7 and introduces no
  `UPPER_SNAKE` token the branch lacks — checked explicitly, because a driver that loses a refusal
  fails open.
- `generate_tree.py`: ours 330 lines to 235, with two names the branch lacks. Signatures identical
  apart from main's deliberate `config: ... | None = None`. The branch's `accepted_records`
  construction and the full `codex_unresolved_reason` plumbing are both present in ours.
- `test_j9_batch_run.py`: compared **by test name**, because taking one side of a test conflict
  silently deletes a test. All 18 of the branch's tests are in main's 22 — one named
  `test_four_workers_overlap_but_the_bcu212_driver_is_serialized`.

So the J9 driver fix landed by another route and the branch was sitting in triage as if it still owed
work. **22 J9 tests pass.** Its 706 untracked `gk-data/packs/fusion/data/seed/passive-tree/**` files are an interrupted
run's disposable output and are deliberately not merged.

## G.5 Registry conflict, and a resolver that destroys data while reporting success

Merging actor-hud conflicted in `gk-core/scripts/verification-boundaries.v1.json` on **one** hunk — 484 vs
481 boundaries, 6 ids only on the branch, 475 shared, and **9 shared-with-different-content**, so a
plain union would have silently dropped a side's paths. Resolved to 490, **+119/−0**, no deletions:
every id from either side survives; shared ids take this side because in all 9 ours dominates (main
split the seven `core-area-*` boundaries out of `core-residual`; the branch is pre-split).

**`.claude/cmdc-agents/scripts/union_append_only.py` is not usable on this file.** It is line-based;
handed this registry it emitted **96 KB from two 182 KB sides as invalid JSON and exited 0**. Used on
markdown ledgers it is fine, but a resolver that reports success while destroying a verification
registry is worse than none. Recorded as AUDIT-5.

## G.6 Bookkeeping and a tool defect of my own

Four stale `active` session records closed (`869b0cfee`, `f794968d2`, and the two ps1-ban-adjacent
ones). A stale `active` record is not cosmetic — `retire_worktrees.py` reads these as ownership
proof, so it keeps merged worktrees looking owned.

**My own tooling defect:** the falsification harness that proved the new `element-catalog` guard row
goes red restored its file with `write_text`, which normalises newlines — so the file did **not** come
back byte-identical on a CRLF checkout. Caught by hashing before and after, repaired with
`git checkout --`, and the warning is now in the browser-proof lane's brief. A "revert" that is not
byte-identical is a second change wearing a first change's clothes.


---

# Manager addendum H — 2026-09-26 (the three-slot live pool, and two defects it exposed)

## H.1 The pool is configured and all three slots are clean

Owner ruling applied: configure the three-slot pool. `FUSIONRPG_GAME_POOL` and
`FUSIONRPG_GAME_SOURCE` written to the gitignored `.env` (never a committed file), pool root
`H:\Games\.fusionrpg-pool`, source `H:\Games\PVZ-Fusion-3.9_MelonLoader` (0.88 GB; 620 GB free on H:,
so three slots cost ~2.6 GB).

| slot | state | port | process | strays | Mods files |
|---|---|---|---|---|---|
| 1 | ready | 5101 | none | 0 | 1944 |
| 2 | ready | 5102 | none | 0 | 1944 |
| 3 | ready | 5103 | none | 0 | 1944 |

This unblocks actor-hud **AUDIT-4**, which was the last open evidence item for that program and was
recorded as *owed and blocked* rather than optional. Note the ps1-ban stream's own measured finding
that a **cold seed import fails** against an empty data dir (`LeadNamesHub.Configure(...) has not
run`), which is exactly what a first-time slot has — so the pool makes that deploy defect reachable
and it should be fixed before a slot's first deploy is treated as a green path.

## H.2 Defect 1 — the owner's game install was polluted, and my first measurement of it was wrong

Six display entries named `Mods <build flags>` sat in the source install, created 08:55–08:57 today,
each a **1157-file copy of the whole Mods tree**. The signature is a path built by concatenating a
build-flag list onto `Mods`. Not `deploy-play.py` (it contains neither `WebView2` nor
`--no-incremental`), and not the Launcher (it does not write `WebView2Loader.dll` into the install);
most consistent with an ad-hoc command from today's deploy measurements. Owner-authorised, removed.

**My first report of this was wrong in a way that mattered.** I reported "each containing exactly one
`WebView2Loader.dll`". That reading was an artefact of the same defect described below: Windows
normalises trailing spaces out of ordinary path APIs, so `Mods --nologo -v q` and
`Mods --nologo -v q  ` are the same directory to `iterdir()` and `rglob()`. What I counted as six
directories was three, and the one-file count was taken against the wrong entries. The cleanup script
compounded it by reporting `remaining stray dirs: none` while three were still on disk.

The real `Mods` is proven untouched: **1944 files, 29,649,205 bytes, fingerprint `23a1c1f0667184d9`
identical before and after.**

## H.3 Defect 2 — `live-slot.ps1` cannot re-clone a slot polluted this way, and fails unhandled

A clone of the polluted source produced the same trailing-space names, after which:

- `shutil.rmtree` failed with `WinError 145: directory is not empty`, five times over;
- the tool's own remedy, `-Clone -Slot 1 -Force`, failed inside
  `Remove-Item -LiteralPath $install -Recurse -Force` (`Win32Exception`, "cannot find the file"), exit
  1, with no guidance — because `Remove-Item` cannot address those names either.

`Remove-Item` on a tree containing trailing-space directory names is a **hard** failure, not a slow
one, and the slot then sits permanently `broken`. The working remedy, found by measurement:
**mirror an empty directory over the target with `robocopy /MIR`** — robocopy itself enumerated the
three offending names — after which `Remove-Item` succeeds immediately.

Routed to the ps1-ban program (it owns `scripts/*.ps1`). Acceptance: the clone's cleanup step uses the
empty-mirror (or the `\\?\` prefix) and a slot polluted with trailing-space names re-clones without a
manual step.

## H.4 Two measurement rules this earned

1. **A directory listing is not evidence about names Windows normalises.** If a tool's own output
   contains something that looks like a CLI flag, address it through `\\?\` before counting it, and
   reconcile the count against a second API before reporting a number.
2. **My own cleanup printed a false negative** (`remaining stray dirs: none` while three existed)
   because the verification reused the API that had already hidden them. A verification step that
   shares a failure mode with the step it verifies is not a verification. The pool registry also
   turned out to be UTF-8 **BOM**-encoded by PowerShell, so a `utf-8` read raises — recorded because
   it will bite the next tool that touches `slots.json`.


---

# Manager addendum I — 2026-09-26 (a cold deploy, a broken deploy, and two hazards found by using them)

## I.1 A cold deploy was broken: the seed importer never configured the lead-names hub

Found because the live pool was configured and the first thing a slot needs is a deploy. Reproduced
against a genuinely empty data dir:

```
$ dotnet run --project gk-forge/tools/AtomImporter -- --db <empty dir>
EXIT 1
the import failed and was rolled back: LeadNamesHub.Configure(...) has not run
```

After `47c9d1f60`: **EXIT 0, 503 rows changed, catalog revision 1, `rpg-hot.sqlite` written.**

A warm dir re-imports clean, so this only ever appeared on a *first* deploy — which is every
first-time pool slot. `RealColdProcessTests` was **already red for exactly this**, and attribution was
measured rather than assumed: in a clean detached worktree at HEAD that project has **4** failures,
one of them the cold-process test; with the fix, **2** remain and both are the pre-existing
`ValidateGateCiTests` pair, which fail with and without the change and are routed, not fixed here.

The read/parse/configure step is now **one** implementation (`LeadNamesHub.ConfigureFromFile`), with
the server's `LeadNamesBoot` delegating rather than carrying a second copy — a second copy is how the
hole opened. The path stays each host's own business.

## I.2 Every deploy was broken: `npm` is not launchable by `subprocess`

The live-proof lane could not deploy to its own slot at all. Measured, not assumed:

| invocation | result |
|---|---|
| `subprocess.run(["npm", ...], shell=False)` | **`FileNotFoundError: [WinError 2]`** |
| `shutil.which("npm")` | `C:\nvm4w\nodejs\npm.CMD` |
| the resolved `.cmd` path | **works** — `11.12.1` |
| `cmd.exe /c npm.cmd` | works |
| `node + npm-cli.js` | works |

`CreateProcess` does not apply `PATHEXT`; it only tries `.exe`, and nvm4w ships none. So the FE build
died at **stage 3 of 12** — every deploy, and with three slots configured, every pooled deploy. Fixed
at `f71c31788` by resolving through `shutil.which` in one place, the way `_mirror` already resolves
`robocopy`. Proven **in situ** by calling the deploy's own `run([npm, "run", "build"], cwd=web)`:
`✓ built in 12.38s`, exit 0.

## I.3 The cfg hazard was live on two of three slots

A pool slot is cloned from the owner's install, and the owner's `Mods\fusionrpg.cfg` names the
owner's server. Measured immediately after configuring the pool: **slots 2 and 3 both carried
`ServerUrl=http://127.0.0.1:5088`.** The Injector reads `FUSIONRPG_SERVER_URL`, then the cfg, then
falls back to 5088 with a warning — so a game launched in one of those slots outside a successful
deploy would have dialled the owner's server. That is the SSH4.9 incident class, and the cfg write in
`deploy-play.py` exists to prevent it, but it is **stage 10 of 12**: any failure in publish or seed
import leaves the inherited value in place. With I.1 unfixed, that was not hypothetical — every
pooled deploy failed at stage 3, i.e. always before the cfg write.

All three slots are now stamped with their own port (5101/5102/5103). Stamping used the tool's own
rule rather than a guess: a slot's `port` is only *stored* on its registry entry when acquired
(`Add-Member port`, `live-slot.ps1:286`) and otherwise *derived* as `5100 + slot` (`:189`). Reading
only the stored field silently skipped two slots — the same shape of bug this session produced twice
already, so the derivation was mirrored instead of reinvented.

**Durable fix, routed to the ps1-ban program (it owns `scripts/*.ps1`):** `live-slot.ps1 -Clone`
should stamp the new slot's own `ServerUrl` at clone time, and the deploy should assert the resolved
server URL is its own before launching the game rather than relying on stage ordering.

## I.4 actor-hud AUDIT-4 is largely closed — with one half that cannot close here

The Unity live-proof lane ran on pool slot 1 and **proved the Unity→Server HUD ingest**, which is
exactly what the browser proof had stubbed out: 21 real `debug.actor-hud` events from the running
game (`ActorHudCache.DeltaEmit` → `ActorHudInvalidator.cs:49-60`), read back through the Server's own
`/api/debug/events`. No FE hook, no fixture. The subject is a real record — real Hub stats applied
(270→411 HP, 0→177 defense), `sourceKind: creature.progression.v1` — and element resolution holds end
to end: `elements:{primary:"earth"}` → `hudGlyph: stone` → `stone.png` deployed and served `200
image/png`. `INJECTOR COMPILE GUARD OK` against the slot's own install, and it connected to *its* own
server (`catalogRevision: 1`, its cold import, against the owner's `15`).

**What it did not claim, correctly:** the HUD canvas is `ScreenSpaceOverlay`
(`ActorHudPool.cs:395`), so it cannot appear in a camera capture — the repo's own comment already
says that primitive *"Misses UI overlays"* — and `repaintsSeen=0` across seven captures including
four foregrounded. So its screenshots showing no HUD are **uninformative, not evidence of absence**,
and the lane said that instead of reporting a red.

**AUDIT-2's mechanism is confirmed and sharper than the todo's wording:** telemetry cannot detect it
at all, which is why it survived the merge. Its *measurement* is not re-taken — a browser lane can
now, because the input exists for real. One caution recorded: the Peashooter's first two events had
`elements=null`, so a window starting at board entry can contain no glyph at all, and reading that as
"still broken" would be a third false red.

## I.5 A structural error I made, and what it cost

I wrote a script to close every active session record whose branch is an ancestor of HEAD. It closed
**13** — and two of those were wrong, structurally rather than by slip: a session working in **direct
mode on `features/mega-merge` is live, and ancestry cannot tell**, because its commits are by
construction already ancestors of HEAD. So it closed the manager's own record **and the ps1-ban
program manager's live one**. Both were restored immediately, and the criterion now skips any record
whose branch *is* the integration branch.

The cost was two restored files and a lesson worth more than the 11 correct closures: **a merge test
that is trivially true for the thing you are testing is not a merge test.** The boundary checker is
now clean (exit 0) where it previously reported three overlaps.


---

# Manager addendum J — 2026-09-26 (two lanes reviewed, and a ledger row I deleted)

## J.1 The live pool is now a Python tool, and I verified the refusal myself

`gk-core/scripts/live_slot.py` (1080 lines, 77 tests, registry row `live-slot-tool`) ports `live-slot.ps1`
and carries two fixes the original lacked. Per the owner's ruling — a `.ps1` touched for a fix moves to
Python rather than growing — the port is the deliverable and the `.ps1` stays as the pre-fix
reference the port's tests read.

**Verified independently, not accepted on the lane's word:** on a 7-boundary registry pair cut from
the real registry, the fixed tool prints
`REFUSED [classify-input] INPUT-SHAPE-UNSUPPORTED`, names the file, states
`shape=structured (declared suffix '.json' is block-structured, not append-only text)`, points at
`union-registry-sides.py`, **exits 2**, and **creates no output file**. Pre-fix, the same pair gave
`ours=101 theirs=100 theirs_only=2 result=62`, exit 0, and an output that does not parse.

The lane corrected my brief twice, both times against code: `prove-slot-connection.py` is a **live
code caller** of the `.ps1`, not a documentation reference as I stated; and the registry is **not**
unconditionally BOM (PowerShell 5.1 writes one, PowerShell 7 does not). I re-pointed the probe at
`d06ebbd95`, which also removed the last code dependency on the `.ps1` — the tool is now referenced
only by the port's own tests.

**Deferred deliberately:** `--structured` was not built. The manager plane already carries two
*conflicting* boundary-union rules, and choosing between them is a product decision; a second JSON
merge implementation is a drift risk. The refusal is a pointer, not an implementation.

## J.2 AUDIT-2 fixed, and the fix is deferral rather than patience

`730f92614` defers the Band B element glyph to load-complete. Both cheaper shapes were rejected **on
evidence**: `syncFromModel` early-returns unless the model revision moves
(`SyncFromModelSystem.ts:398`), so `setHudDisplay` is not per-frame and a patient assertion would make
the gate green while the canvas stays wrong; and an awaitable loader has no caller able to await it
because `syncFromModel` is synchronous. The deferral seam already existed one function away, built for
type icons, so the fix extends it rather than forking it. `decisions.md:39` ships with the code.

Measured over **5 distinct elements** so caching cannot masquerade as a fix: fixed each
`false→true`; reverted **and rebuilt** all five `false→false`. The reverted build also measured
`draws=1, glyph=false` across 20 polls / 6.5 s / 4 poll cycles, which shows `false,false,true,true` is
only the *busy*-board form and a **quiet board never got the glyph at all** — a sharper defect than the
row recorded.

The lane caught three of its own errors, each of which would have produced a false green: its first
falsification was **invalid** (the mocked e2e serves the *built* bundle, so reverting source without
rebuilding tested the fixed build — caught by a throwaway counter reading `draws=0`); its masking
theory was wrong (`epochs=0`, not force-resyncing); and its change would have introduced an infinite
404 retry loop and an epoch bust stranding in-flight loads.

## J.3 I deleted a ledger row and my own assertion hid it

`e21f3fb0f` shipped a deletion I did not notice. Two scripts computed a row's end by scanning forward
for "the next line starting with `- [`"; that scan ran past the following headings, so **AUDIT-5 was
destroyed** and AUDIT-4's heading line was lost, orphaning its body under no checkbox.

What made it invisible is the part worth keeping: the script asserted that AUDIT-2 and AUDIT-6 were
intact — **the two rows that happened to survive** — printed `sibling rows intact: True`, and I read
that as verification. The rebuild does not scan: it starts from `5ab1bfe81` (the last commit with all
six rows), splits on the six exact headings, and **refuses to write** unless all six are present with
their bodies. The assertion counts headings, not survivors, because counting survivors is what let the
deletion through. Restored at `edd26acee`.

## J.4 Merged-head evidence at `a588a8fab`

| Check | Result |
|---|---|
| Guard suite | **exit 0** |
| Declared core surface (`gk-core/tests/core-test-projects.v1.json`) | **67 projects, 0 red, 0 missing** |
| `guard-verification-boundaries.py` | **exit 0**, 492 boundaries, none pointing at a missing file |
| `session-boundary-check.py` | **clean, exit 0** |
| Solution build | exit 1 — **the repo correctly refusing** |

The build failure is `error FUSIONRPG0002: Cell pvzrh-3.8.1 x BepInEx was pointed at a pack that
belongs to another cell`. This machine has only a 3.9 MelonLoader install and no 3.8.1 pack, so the
cell fingerprint declines to fake one. That is the pack/loader matrix working, and it is the same
refusal I caused earlier by mis-setting the variable. **The 3.8.1 BepInEx host is not compilable on
this machine**, which AGENTS.md already acknowledges.

The **authoritative** `post_merge_check.py` still has not run: it requires a CLEAN main worktree and
the literal `features/mega-merge` branch, and the ps1-ban stream holds uncommitted files. Two separate
attempts to satisfy it were the wrong lesson twice — I measured the substitution rather than inventing
one.

## J.5 Fence narrowed, and a wrong tool of my own corrected

The boundary checker reported DRIFT on `AGENTS.md` / `CLAUDE.md`, claimed by this record and by
`numeric-types-dedup-20260926`. The direction matters: this record has claimed those two since the
manager's documentation work, which is finished and merged, while the other is a live lane that needs
them. So the fence was narrowed **here** — 40 paths to 38 — and the script refuses to drop a path that
has uncommitted modifications, because that would declare a file unowned while someone's work sits in
it. Boundary check is clean.

I also used my own glob search to conclude that `gk-fusion/scripts/prove-slot-connection.py` was **unmapped** in
the verification registry, and nearly reported it as a defect. Asking the **planner** — the component
that actually decides — showed it is covered by an **explicit exemption** (`exemption-live-diagnostic-scripts`,
"live/game-install diagnostics require a legal local game"). A substring search cannot see exemptions.
That is the second time today a hand-rolled check contradicted the real tool, and both times the tool
was right.


---

# Manager addendum K — 2026-09-26 (closing leftovers, and a pattern in stale claims)

## K.1 Two acceptance records landed — and both carried a claim that had gone stale

`review/resume-28b-effect-pipeline-epl1-1-20260925` (reviewed SHA `8334a1d61`) and
`review/resume-29-strain-reader-guard-20260925` (reviewed SHA `a120ce2d8`) are **evidence for
implementations already in this head** — verified by ancestry, not by the report's own word. Each is a
single report file, so neither merge can regress behaviour.

Both were **add/add conflicts**: the integration head already had a copy of each report, from the
original implementation merges. That is the interesting part, because the copies on the head annotated
their reviewed paths `(**new**; reviewed path; not yet integrated on this manager branch)` — a claim
that was true when written and became **false the moment the implementation landed**.

Resolution was on evidence, in both cases taking the branch's revision:

- EPL1.1: the branch's copy drops four stale qualifiers. Taking ours would have kept a false
  statement in an acceptance record.
- SSH7.1: I first took `--ours` **wrongly**, on the assumption that main's copy was canonical because
  it was already there. Comparing the two showed the branch's copy was the corrected one — and then
  that the branch's copy *also* still carried 14 stale `not yet integrated` annotations.

So I checked all 14 against the tree: **14 claims, 14 false, 0 still true** (every named path exists in
HEAD). Struck at `0ac9db730`, and the script refuses if even one claim is still true, because a
uniformly-stale annotation is a different thing from a mixed one. The diff is 14 insertions against 14
deletions, each pair differing only by the qualifier — the path list, which is the evidence, survives
intact.

## K.2 `adopt/worktree-cleanup-20260925`: unique, and still not landable

`git cherry` reports its one commit as **unique**. Merging it would have reverted **298 accepted
insertions**: three of the six files it changes are the same three `6b36c52cd` already evolved.

That is the second time today that "unique" and "landable" came apart, and it is a limit of the
measure rather than of the branch — `git cherry` counts **commits**, and a commit can be unique while
its content is a regression. The branch triage table should be read as "worth reviewing", never as
"mergeable".

What the branch still carried and the head lacked was **one file**: the session record of a lane
retired on 2026-09-25 whose active state had been blocking the integration gate. That file alone was
taken (`0eba7190a`); nothing else.

## K.3 …and that record's warning was stale too

It read: *"A confirmed fail-open defect remains: `worktree_cleanup_core._runner_evidence` reads only
`.kilo/agent-manager.json`, so it cannot see opencode/cmdc lane owners"* and *"the tool must not be run
against live worktrees until that row is done"*. Both false now:

- `gk-core/scripts/worktree_cleanup_core.py:29-30` define both lane-registry roots, and `_runner_evidence`
  (line 280) documents reading all three sources; `gk-core/scripts/test_worktree_cleanup.py:70` plants each
  runner's record via `write_lane`.
- `tasks/test-verification-boundary-todo.md:1678` reads `- [x] **TVB-F37` with exactly that remedy.

A **dated correction was appended**, not a rewrite: the record said what was true when the session was
retired, and its `status` stays `abandoned` — the session genuinely was abandoned, only the warning it
left behind was stale.

## K.4 The pattern, stated

Four stale-claim corrections in one stretch: two acceptance records, the retired session record, and my
own AUDIT-2 ledger row. The common shape is that **a record is accurate when written and goes stale
silently as the tree moves under it, and nothing in the repo re-checks a record's claims against the
tree.**

That is a candidate defect in its own right, and it is cheap to guard: a check that walks acceptance
records and session-record notes for claims of the form "not yet integrated" / "not in the head" and
verifies each named path. It would have caught all four. Not started here — it belongs to whichever
program owns acceptance hygiene (`test-verification-boundary` or the verification-boundaries program),
and the manager will route it rather than add it to a fence that is already 38 paths wide.

## Addendum L — 2026-09-26: the verification plane was fully blocked, and it is now green

Three commits. The first is the one that mattered: **no agent in this repository could scope-verify
anything**, and that was not visible from any status reading.

### L1 — `7494c0f13` — a false registry claim blocked every scoped verification

`verify-change.py` runs the verification-boundary integrity guard as its integrity precheck. That
guard refused the whole registry at clean HEAD `67747a336`, reproduced in a detached clean worktree:

```
ambiguous owner pattern: gk-core/scripts/cscan.py (dal-guard, secondary-no-unity-guard)
```

So every scoped gate in the repo exited 1 at the plan stage, for every path, regardless of the change
under test. The two candidate repairs were not equivalent. Dropping the path from `dal-guard` would
stop the secondary guard running whenever the shared scanner changes — a real hole, and exactly the
"narrow the fence to make the gate pass" move this repo forbids. Dropping it from
`secondary-no-unity-guard` costs nothing, and reading the two guards decides it: `guard-dal.py:52`
genuinely does `from cscan import line_of, strip_comments`, while `guard-secondary-no-unity.py` names
cscan exactly once — line 25, inside a comment stating it scans RAW TEXT and deliberately does *not*
strip comments, recording that as an owner finding rather than widening what the guard permits. The
secondary entry's claim was false. Registry still 494 boundaries, `dal-guard` keeps the scanner, and
the guard goes `exit 1` → `VERIFICATION BOUNDARY GUARD OK` `exit 0`. Re-verified end to end:
`verify-change.py --plan-only` now returns 0 and a real plan.

**This crossed `ps1BanSplit`** — `scripts/**` belongs to `ps1-ban-manager-20260926`, which is active
with an unmerged registry edit (`ps1ban/l3-checks`, 88 diff lines, touching neither entry and adding
no id there, so the two merge additively). Recorded deliberately in the session record rather than
silently taken. **Owner decision: any further `scripts/**` registry work routes to that stream.**

### L2 — `c1236555a` — the cleanup tool could delete a lane's acceptance evidence

`retire_worktrees.py` had **no awareness of acceptance artefacts at all**. An artefact's `logDir` is a
relative path resolving inside whichever review worktree the harness ran in; deleting that worktree
destroys the command output a verdict rests on while leaving the tracked artefact — and its
resolvable `sha` — looking intact. Across the 78 tracked artefacts, **17 name a `logDir` that
resolves nowhere**; `external-evidence/` exists in no surviving worktree and is not gitignored at the
repo root. Whether this session's own earlier retirement of 29 worktrees removed them is **not
determinable from the tree** — the paths are relative — so it is recorded as unproven, not asserted.
What is determinable is that nothing prevented it. The new blocker resolves each `logDir` against the
candidate worktree and names the lanes. `contendedTree` is a **boolean** in the current schema; reading
it as a path is what made an earlier audit of mine report "0 missing" for a check that had not run, so
the type is checked and asserted. 23 tests (was 21), falsified against the pre-fix tool: both new
tests fail there and the evidence worktree is *retirable* without the guard, so it is load-bearing.

### L3 — `90bbe73fb` — SR-25 is closed, and nothing was checking

The five `knownRed` entries registered as debt `SR-25` **pass** (`5 passed in 159.67s`; whole file
`12 passed in 296.55s`). Not vacuous: the test's own loader returns **33,073 entries** with
`findings == []`. It closed by *correcting a stale assertion* (lane sgc-6, 2026-09-23), not by filling
a corpus. But the integrity guard checks each entry for shape, project, file existence and debt
resolution and **never that it is still red** — so a green test stays exempted and the closure is
invisible. Bounded blast radius (the match derives classname from the file part, so a stale entry
cannot exempt a different file), but the report lies. Landed in the owning ledger
(`tasks/seedsmith-generated-seed-repair-todo.md`, unclaimed, appended not rewritten), with remediation
routed rather than taken across a fence.

### L4 — the ipc WIP was superseded, and my brief was wrong about it

`opencode/ipc-3d-staged` and `opencode/ipc-3e` were **the same commit** (`f4769a660`) under two names.
I measured 3-of-14 tests failing on it and briefed a lane to wire `render_brief(avoid_terms=...)` into
`briefkit/render.py:82`. The lane disproved my premise: the wiring already landed in `93a2e16d9` at
`adapters/trees/nodegen/brief.py:120` — a different function the 14 tests never touch — so the WIP was
superseded, not unfinished, and my named target was wrong. The lane still delivered: two tests for a
fail-closed registry read that had **zero** coverage, each falsified by one-line mutation with
byte-exact restore (`186248a26`), plus the record closed (`ef80025d9`).

Both refs and their worktree are now removed. Justified by evidence rather than ancestry: all three
added files are **byte-identical at HEAD** (3/3 blob-hash comparison), the worktree was clean, and no
session record claimed it. Ancestry-based tools would have kept it forever — `f4769a660` is 1059
commits behind and unreachable from any integration branch, yet carries nothing.

### Open, routed, not taken

- **`PowerShellParityTests::test_the_real_registry_plans_identically_in_both_implementations`** is red
  in the port stream's plane. At HEAD it failed on the L1 ambiguity; with the guard green it reaches
  the real defect — the test hardcodes `scripts/guard-dal.ps1`, which commit `17d884e09` deleted when
  it ported the guard body. Both trees red, so L1 did not cause it; L1 *revealed* it. Until it is
  fixed, the Python planner has no parity proof against the PowerShell one.
- **Remove the five stale `SR-25` entries** — the seedsmith programme's call.
- **Add a "still red" check for `knownRed`** — the registry/guard plane.
- **The stale-claim guard** (addendum K) is still unstarted and still unowned.



## Addendum M — 2026-09-26: items 8–10, and a commit gate that was not mine

### Verdicts

| item | branch | verdict | evidence |
|---|---|---|---|
| 8 | `opencode/resume-31-cleanup-repair-20260925` | **STALE** | 3/3 files stale, 0 own commits, merged at reviewed SHA `6b36c52cd` with artefact `resume-31-cleanup-repair-20260925-6b36c52c.json` |
| 9 | `adopt/worktree-cleanup-20260925` + worktree `cleanup-tool-adopt-20260925` | **SUPERSEDED** | 1 own commit `6d2c48460`, not an ancestor of integration; all 6 of its files are at integration; its 11 unique lines are the **v2** form of capability integration carries as **v3** |
| 10 | `prep/resume-31-cleanup-repair-20260925` + worktree `prep-resume-31` | **UNLANDED EVIDENCE → rescued** | its single dirty file was the lane brief, the owner directive for `TVB-F37`; `.claude/opencode-agents/briefs/` is tracked, the path was not ignored, and no equivalent brief existed at integration |

**Item 9 was preserved before removal.** Git refused `git branch -d` ("not fully merged"), which is the guard working: `6d2c48460` is not an ancestor of integration, so deleting the branch without a ref would have made it unreachable and eventually garbage-collected. It now lives on `rescue/adopt-worktree-cleanup-20260925`, matching the existing `rescue/review-tvb3` precedent. The v2→v3 supersession is the reason it is safe to keep as a rescue ref rather than a live branch: `TOOL_VERSION` is `worktree-cleanup-v3` at `worktree_cleanup_core.py:37`, `RUNNER_BLOCKER` is extracted to a constant at line 37, `_runner_evidence` returns `tuple[records, errors]` rather than records alone, `global_blockers.append(...)` replaces a reassignment, and `test_worktree_cleanup.py` carries 6 tests over the `runnerEvidence` states.

**Item 10's brief was rescued because clearing the worktree would have deleted the only record of why the repair was ordered.** Its acceptance is verified rather than assumed: `worktree_cleanup_core.py:29-30,283` reads all three sources the brief names (legacy `.kilo/agent-manager.json`, `.claude/opencode-agents/agents/*/meta.json`, `.claude/cmdc-agents/agents/*/meta.json`), and `test_worktree_cleanup.py` carries `test_legacy_manager_evidence_still_holds_its_worktree` plus the cmdc / terminal / malformed cases.

### Two tools of mine were wrong, and both were caught by a falsification

**A per-file line comparison reported `actorSurface.ts` as +199 unlanded. It was false.** Integration had *split* the 374-line module into a 63-line re-export shim plus a new `actorSurfaceCatalog.ts`; 280 of 288 "worktree-only" lines had moved there. A file-to-file line test cannot see a split — the same blindness the file-level test has for a rename, one level down. Fixed with a whole-tree line index, falsified in both directions: 209/217 moved lines found, and 0 synthetic probe lines matched. On `review-b3`, **419 of 429** "missing" files were likewise the Core test split, not losses.

**`adjudicate_leftover.py` failed open on an unmeasurable reading.** Handed a directory name instead of a branch name, it reported `ancestor False` / `own commits None` and fell through to *"FINISHED — merged ancestor, 0 own commits, clean. Safe to clear."* An unreadable commit count must never reach a "safe to clear" line. It now refuses with **UNMEASURED** and prints the commands to read by hand.

### A name test could not see two of the items

`cleanup-tool-adopt-20260925` and `prep-resume-31` are worktree *directories* whose branch names do not appear in their paths. A `Select-String` for `worktree-cleanup` and a branch-suffix-in-path match both missed them. Third occurrence of a name-shaped test hiding a real item, after the Core test split and the `deploy-play.ps1` → `.py` rename. **A leftover is identified by its branch, not by its directory name.**

### The commit gate I was relying on was another lane's script

`C:\Users\NeneScarlet\AppData\Local\Temp\opencode\commit_fence.py` had been **overwritten** by the `ps1-ban` stream with their own version, whose docstring is their commit message verbatim and which *stages from the fence and commits*. Running it published the whole index — my rescued brief plus their already-staged deletion of `scripts/guard-injector-compile.ps1` — as `e00390900`, under their message. My own `git commit -F` then found nothing to do.

That directory holds ~300 scripts from many concurrent sessions, and several carry `-MINE` suffixes (`ah-MINE.py`, `cscan-MINE.py`, `sw-MINE.py`), so this collision has already bitten other agents here and been worked around by renaming. Session tools now live in a session-private directory.

**Provenance correction for `e00390900`:** that commit carries
`.claude/opencode-agents/briefs/resume-31-cleanup-repair-20260925.md` (92 lines, the `TVB-F37`
owner directive) under a message that describes only the `ps1-ban` fence change. Nothing is lost and
nothing is rewritten; this paragraph is the record. The `.ps1` deletion in the same commit is
`ps1-ban`'s intended port step and is coherent — `gk-core/scripts/enforcement-registry.v1.json` already
names `gk-fusion/scripts/guard-injector-compile.py`, and `EnforcementRegistryGuardTests` passes 20/20.

### Live risk, not fixed here

`gk-core/scripts/enforcement-registry.v1.json` at HEAD names `gk-fusion/scripts/guard-injector-compile.py`, which is
**untracked**. A committed registry naming an uncommitted file is the same shape as the false
`cscan.py` ownership claim that blocked every scoped verification in this repository, and it is the
`ps1-ban` stream's in-flight state to close. Flagged, not touched: their fence owns it.

### Still open for the owner

`3307f0597` is still in history carrying 88 files, 1 mine and 87 the `ps1-ban` stream's, under a
message describing one file. Recovery is `git reset --soft HEAD~1` and a commit of only my file,
which restores their staging area exactly. Not run unasked, because it rewrites shared history.


## Addendum N — 2026-09-27: the append-only ledger census, and the six cases that must not be touched

Seven ledgers were rescued one at a time by walking leftover worktrees. That is an accident of which
worktrees got visited, and the rule added to the manager skill in `bd8d68acf` says the loss is
invisible in a diff — so a worktree nobody walked can hold it too. So the question was asked
directly, for **all 37 tracked `tasks/*.jsonl` ledgers** against **every copy on disk**, including
copies in directories git no longer registers as worktrees.

**Result: 1 rescue candidate · 6 contention · 302 older copies.** The one candidate was
`tasks/narrative-seed-ledger.jsonl` and it is landed (`49174e692`). The 302 hold nothing integration
lacks, so there is nothing in them to rescue.

### The seven rescues

| ledger | rows | shape |
|---|---|---|
| `npc-story-events` | 55 | split across two worktrees of one lane, disjoint |
| `lawn` | 16 | integration 29 seconds behind |
| `ip-censor` | 8 | task T23, disjoint from integration's T12/T16 |
| `empire-progression` | 2 | a named unlanded code site with an owner |
| `combat-ai` | 1 | a CAI3.1 slice-4 verification record |
| `keepverse-split` | 1 | a **negative** result: "no edit was made" |
| `narrative-seed` | 2 | *"NS25 LOST, recorded rather than glossed"* — and the rebuild landed |

### The six that must not be touched, with the reason each is not a rescue

- **`test-verification-boundary-ledger.jsonl` in `corpus-bcu213` (+1/-180).** The one row the copy
  holds is `kind: "finding"` for `TVB-F24`. Integration's own note says it *"sat in the ledger as kind
  `finding`, **a schema violation, so every later ledger write was refused**"*, and it was refiled as a
  note. **Landing it would re-introduce the schema violation that blocked the ledger.** This is the
  sharpest case in the set: the row looks like an unlanded finding and is in fact the defect.
- **`combat-ai-ledger.jsonl` in five worktrees (+9/-407 … +15/-390).** The added rows are `CAI1.1`–
  `CAI1.14` task rows that integration already carries in a **richer** form, plus **5 note rows**.
  Three of those notes name findings absent from the ledger, and each is already recorded elsewhere:
  `ActionStage.TryPick` 1× in `tasks/combat-ai-todo.md` and 2× in evidence fragments, `BasicAttack.cs`
  14× and 34×, `DerivedStatChannels` 5× and 14×. So they are **duplicate records of tracked
  findings**, not unlanded ones.

### The census tool's own first run was wrong

It reported **303** rescue candidates, every one of them `+0`. A copy that adds nothing cannot be
rescued; the classifier sent `adds=0, lacks>0` down the divergent branch instead of recognising an
older copy. Fixed before any of it was reported. Recorded here because the corrected figure is the
one worth citing, and because a census that inflates by 300× is worse than no census.


## Addendum O — 2026-09-27: the evidence census, and the three verdicts it produced

The ledger census (Addendum N) closed the `.jsonl` class. The same blind spot applies to every record
class, so it was asked directly for the whole other class: **all 1083 tracked `tasks/reports/**` and
`tasks/evidence-fragments/**` files** against **every copy on disk**, across 67 worktree directories.

The first run reported 39 unlanded files. The corrected answer is **5**, and the difference is worth
recording because both errors were mine:

- A line set built on raw `str` equality cannot see that two trailing spaces are a markdown hard
  break. Whitespace normalisation then re-inflated the count to 166 "forks", because the ps1-ban
  stream renamed every guard and rewrote its invocation line.
- Grouping by `(file, worktree)` rather than by the **content** of the difference reported 104 pairs
  for what is 5 files, because worktrees forked at the same moment all carry the same stale revision.

**60 of the 65 dirty files differ from integration only in how a guard is invoked.** That is the
symmetric one-for-one rename the adjudication rules require discounting — the same rule that stopped
a 7-file build-infrastructure change from being discarded as "unlanded" — so there is nothing in them.

### The five, and what each is

| file | copies | verdict |
|---|---|---|
| `evidence-fragments/CAI1.12.md` | 29 | PARTIALLY LANDED — 28 rename-only, 2 carry a real revision |
| `reports/resume-13-rpg-simulator-rsf27-20260925.md` | 2 | SUPERSEDED (see the correction below) |
| `reports/resume-08-passive-tree-binder-20260925.md` | 1 | STALE — rename plus trailing whitespace, nothing else |
| `reports/BCU2.11-full-run.json` | 1 | blocked on the BCU2.11 authorization |
| `reports/BCU2.12-full-run.json` | 1 | blocked on the BCU2.12 authorization |

`CAI1.12.md` is the interesting one. It exists in 29 worktrees in two shapes: 28 differ by a single
renamed guard, and 2 (`cmdc-item-seed-gen`, `corpus-bcu210`) carry a much larger earlier draft. Most
of that draft is genuinely superseded — integration's copy is a **later** `cai-sink` session that
closed erratum 1 by opening `gk-core/src/FusionRpg.Core/Effects/**` and `gk-fusion/src/FusionRpg.Injector/**` (so the
lawn half now reads "13 passed, 0 failed") and answered erratum 2 with "manager ruled erratum
granted". Erratum 3 is landed in the artifact itself: `spec-resolvable-here.md:117` carries the
correction by name.

**Erratum 4 survived nowhere**, and it was the only real loss in the census: the draft recorded that
the battle half is golden-neutral because no production host reads the footprint map, the later
session did not restate it, and `EffectFootprints` appears in **zero** todo rows. Re-measured rather
than transcribed — `BattleRunState.cs` holds exactly three occurrences, at 281 (declaration), 729
(setup assignment) and 840 (the builder), and nothing reads it. The claim still holds a week on, so
the negative result is landed in the fragment and cross-referenced onto `CAI3.6`, which already exists
as the first consumer and already depends on CAI1.12. A cross-reference rather than a new row is also
the truthful placement: the map stays inert until CAI3.6 ships.

### A published claim was wrong, and is corrected rather than deleted

`resume-13`'s addendum was first justified by claiming its two result strings "appear nowhere in
`tasks/`". That was false, and mechanically so: `Select-String -Path tasks/*.md` matches the **top
level** of `tasks/` and does not recurse, so it never opened `tasks/reports/**` or
`tasks/evidence-fragments/**`, which is where every one of those records lives. Measured with
`git grep` at the parent commit, `SIM FABRICATION GUARD OK` was already in **7** files, `36 steps` in
2, `7 reads` in 3, `8 resolvable citations` in 4. The results were tracked; they were never lost, and
by the standard applied to the `combat-ai` contention cases the correct verdict is **SUPERSEDED**. The
addendum keeps its place for two narrower reasons — it makes the report self-contained, and it carries
the one phrase that existed nowhere before it, that *the golden subtree was skipped as designed* (0
occurrences before, 1 after). The claim is withdrawn in the document in `5b6ef97a0`, not quietly
edited, so the next reader sees both the finding and why it was wrong.

### Three lessons added to the skill

11. Group a census by content, not by `(file, worktree)`. 12. A non-recursive glob reads as an
absence. 13. A lesson written is not a lesson applied — lesson 10 already named the
`if (git cat-file -e ...)` exit-code trap in those words, and it fired again inside a loop, printing
"55 of 55 `.ps1` files are not at HEAD" for files that were all at HEAD. The durable form is
structural, not editorial: a checker that **returns** an exit code, and a reporting step that cannot
render a verdict it did not compute.


## Addendum P — 2026-09-27: `cmdc/ip-censor-2` closed as STALE, and a prior claim corrected

An earlier note in this report described this worktree as "clearable after its ledger rescue". That
was wrong, and wrong for a reason worth recording: it was based on the ledger being rescued and
nothing else. The worktree holds **28 dirty paths**, and a verdict cannot be reached from a file count.
Every one is now adjudicated by the line-set test.

| group | n | verdict |
|---|---|---|
| evidence fragments (`CP1`, `CAI1.10`–`CAI1.14`, `CAI2.3/4/6`, `CAI3.1/3`, `CAI4.4`) | 13 | STALE — differ only in how a guard is invoked |
| lane briefs (`cai-sink.md`, `combat-ai-cai111.md`) | 2 | STALE — same |
| `docs/**` specs and `software-architecture.md` | 6 | STALE — same, plus anchor drift |
| `tasks/combat-ai-todo.md` (+44/-216) | 1 | SUPERSEDED |
| `tasks/ip-censor-todo.md` (+41/-101) | 1 | SUPERSEDED |
| `tasks/ip-censor/release-readiness.md` (untracked) | 1 | STALE — byte-equivalent to integration's copy |

**The two large todos are superseded, and this needed proving rather than assuming.** The worktree's
revisions are older than integration's, so "holds 40 lines integration lacks" is a description of a
rewrite, not of a loss. Every decision-bearing line in the residue was checked against integration:

- `CAI2.6` "needs a ruling" → integration: **CLOSED**. `CAI3.1` "owner decision" → **CLOSED**.
  `CAI4.7` "core half landed, remaining…" → **CLOSED**. `CAI-tests-1` "**BLOCKED on this lane's
  fence**" → integration: `- [x]` **DONE 2026-09-23** (lane `cai2`, session `combat-ai-2b`). Filed
  blocked, then completed.
- `T16` in the ip-censor todo "blocked" → integration: `- [x]` **closed**. `T12` → open, its `Files:`
  line already names `.github/workflows/release.yml` and `gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs`,
  the same outside-fence pair. `T18` → open, carrying **"PART 2 OUTSIDE THIS LANE'S FENCE"**, which is
  more detail than the draft had.
- The worktree's external-dependency table (CAI2.2, CAI2.3, CAI2.5, CAI2.6, CAI3.1, CAI3.2, CAI3.3) is
  **not** landed, deliberately: four of the seven rows it names are now closed, so the table is stale
  by construction and landing it would mislead. All seven rows are open-or-closed at integration with
  their own dependency recorded.

**It is not a ninth holder of the `CAI-spec-fork` drafts.** That row names 8 worktrees across three
holder groups and this is not one of them, and the reason is that its spec residue is not a competing
body. Of `spec-resolvable-here.md`'s 7 unlanded lines, 4 are the guard rename, 2 are context around a
`BattleEffects.cs:238-250` anchor, and the seventh is a single test row differing by one line number:
`AtomKindRegistry.cs:701` at integration against `:699` in the worktree. The fork row already
distinguishes this from a fork — *"This is not the stale-citation problem tracked at the
`BattleRunState.cs` rows above; that is about line anchors resolving, this is about incompatible bodies
of the documents."* This is the former.

**The tool's `retirable: false` is a blanket blocker, not a finding.** It reports
`"28 local path(s) incl. 1 untracked"` — the *existence* of dirty paths, which it cannot adjudicate by
content. That is the manager's job and it is now done.

**Stale lane-registry claim surfaced, not dropped.** The tool reports `staleClaims: ["cmdc:ip-censor-2"]`.
Uncorroborated, so it does not block: `state: stopped`, `pid: null`, and 0 live processes touching the
repo. Recorded here rather than silently ignored, per the rule that a stale claim must be surfaced and
only a corroborated one blocks.

Pre-removal checks, all negative: 0 commits unique to the branch (so no rescue ref was needed), 0
session records naming the lane, 0 acceptance artefacts, and the single untracked path verified
byte-equivalent to integration's copy. Removed, then the branch deleted. The four rescue refs
(`rescue/adopt-worktree-cleanup-20260925`, `rescue/resume-30-commandcode-config-review`,
`rescue/review-resume-00a-final`, `rescue/review-tvb3`) are untouched — they live under
`refs/heads/rescue/`, not `refs/rescue/`, which is worth knowing before a count of them comes back 0.


## Addendum Q — 2026-09-27: the empty-leftover blind spot, closed in the tool rather than carried

The leftover walk had one gap it could see but not close, and it was the gap the walk's own success
criterion named: *"the blind spot where a failed long-path or permission delete leaves an empty
de-registered directory that the cleanup tool cannot enumerate or reclaim, which must itself be fixed
in the tool rather than left as a known gap."*

Enumeration had been fixed in `afed89f92`. **Reclamation had not**, and the reason given was sound:
the tool enumerates leftovers and refuses to remove any of them, because deciding that an unregistered
directory is disposable needs a content adjudication rather than a path test. One such directory held
451 lines across 9 files that exist nowhere else in this repository, so "remove them all" was
correctly refused.

What the tool was missing is that **empty is a proof, not a judgement**. A directory with nothing in
it cannot hold unlanded work, so it never needed that adjudication — and the refusal was applied to
the one class where it was not needed. Measured on this tree: **28 empty** de-registered directories
sat beside the worktrees, 24 removable and 4 held open by a live handle.

`--reclaim-only` now removes the provably-empty ones and does three things it will not compromise on:

- **A capped scan is refused outright.** The entry cap exists so a huge directory cannot stall the
  walk, so a capped count of zero is evidence that the walk *stopped counting* — not evidence of
  emptiness. Reading it as empty would delete on the strength of a number that was never finished
  being produced, which is the exact shape of the bug the tool exists to report.
- **Content is never removed.** A leftover holding entries is still only reported, and `Path.rmdir`
  is the second independent proof: it succeeds only on a directory the OS also considers empty, so a
  directory that filled up between the scan and the attempt fails there instead of deleting real work.
  That race is a test, not a hope.
- **A refusal is named, not bucketed.** `LOCKED`, `PATH-TOO-LONG`, `PERMISSION`, `NOT-EMPTY`, taken
  from the OS's own code and not from the message text, with a retry under the `\\?\` extended-length
  prefix so the long-path case is actually fixed rather than merely labelled. Three refusals with three
  different fixes reported as one "could not remove" is how a known gap stays a gap. The run exits
  **non-zero** while one stands, because a tool that exits 0 with the gap open is the
  checker-that-cannot-fail shape.

`--reclaim-only` exists because reclaiming litter and retiring a merged worktree are independent
decisions, and coupling them through `--apply` would have been destructive here: the only retirable
worktree on this machine is `materialistic-spear`, held back deliberately because `.kilo` was written
minutes ago and holds two other worktrees. Asking the tool a question about *directories* must not
remove a *worktree*.

**Result: 24 reclaimed, 37 registered worktrees untouched, `materialistic-spear` untouched.** Four husks
remain and are now named rather than silent — `opencode-resume-32/33/34/20260925` come back `[LOCKED]`
and the run exits 1. A rename probe fails the same way, and `SearchIndexer` was running; the Windows
Search indexer holds a directory handle while indexing and releases it. That is an external holder with
its own release, not a tool limitation, and killing a system service to reclaim four empty husks is not
a trade this repo should make.

One bug was caught by the tests rather than by the run, and is worth naming because it is the same
family as a lesson already in this file: `winerror` and `errno` genuinely disagree on Windows, which
raises `errno` 13 for a sharing violation — the same number as a POSIX `EACCES`. The first
implementation read `errno` first and classified a real `ERROR_ACCESS_DENIED` as `LOCKED`, telling the
owner to go and find a process when the fix is an ACL. `winerror` is now read first and exclusively
when set. Tests 39 → 53; `verify-change` green at 900 tests and 376 subtests.


## Addendum R — 2026-09-27: the 23-worktree group is not blocked by the fork, and one holds live unlanded code

The holder-census correction in `CAI-spec-fork` freed 23 worktrees from a blocker they were never
subject to. Taking them one at a time:

**`opencode-findings-2c` — STALE, cleared** (35 → 34 worktrees, 40 → 39 branches). Its three specs are
the +2 / +9 / +6 rename group; every worktree-only line in `spec-intent-router.md` was read and all ten
are integration being newer — four `guard-*.ps1` → `.py` renames, two code samples with the stale
`BattleRunState.cs:687-699` anchor against integration's `:743-757`, the **three**-parameter sink
construction against integration's six-parameter form, and the `Reselect` row. Its todo's six
decision-bearing lines all name rows that are open-or-closed at integration. Pre-removal: 0 unmerged
commits, 0 session records, 0 acceptance artefacts, no lane registry.

**The next four are NOT homogeneous, which is why they are not batched.** Each carries 29–36 dirty
paths against `findings-2c`'s 26, and three of them carry an `ABSENT-AT-INTEGRATION` or
`UNLANDED-COMMITTED` entry. The 23-worktree group is homogeneous *in its spec residue only*; the rest of
each worktree is its own business.

**`opencode-resume-00b` and `opencode-resume-00c` — LIVE STREAM, not touched.** Both edit
`gk-core/tests/FusionRpg.Guard.Tests/**` and hold `scripts/guard-generated-seed.ps1` untracked, and **all of
those paths are inside the active `ps1-ban-manager-20260926` fence** (449 paths, status `active`),
which claims `gk-core/tests/FusionRpg.Guard.Tests/**`, both `guard-generated-seed.ps1` and `.py`, and
`gk-core/scripts/verification-boundaries.v1.json`. Their Guard.Tests residues are the port itself
(`FileName = "powershell"`, `-ExecutionPolicy Bypass` → `pwsh`). Work stopped in flight is not a
leftover.

**`opencode-resume-00a` — DRAINED, with UNLANDED CODE that is verifiable.** Its session record is
`abandoned`, no commit was made, and its own 207-line report ends *"manager review/harvest is still
required"*. The unlanded code is the **fail-closed merge/acceptance plane**: `accept-lane.ps1`,
`merge-lanes.py` and `post_merge_check.py` at **1,412 insertions / 327 deletions**, plus a new
`test_fail_closed_pipeline.py`. It is **verifiable now**: run unchanged in its own worktree, **53 tests
green, exit 0, 119s** — and the test names are this repository's own fail-closed properties
(`test_zero_exit_test_run_failed_summary_is_red`, `test_zero_test_count_guard_is_red`,
`test_zero_test_count_test_is_red`), which is precisely the "a green process exit without evidence of
executed tests is not green" rule turned into assertions.

**The report is landed; the code is not, deliberately.** The report existed nowhere else, so it is
rescued to `tasks/reports/resume-00a-fail-closed-recovery-20260925.md` with exactly one change: its
`**Worktree:**` header's `D:/Works/source/...` became repo-relative, because AGENTS.md requires
portable committed paths and **0 of the 255 reports already at integration carry a drive letter**. The
script proved the rest byte-identical before writing.

The 1,412 lines are not landed by this session because they *are* the acceptance plane — the scripts
that decide whether a lane is accepted — and the ps1-ban stream is porting every `.ps1` in this
repository and has not yet claimed these three. No active fence owns them today (the ps1-ban session
claims only `.claude/cmdc-agents/briefs/*` from that directory), so this is not a fence collision; it
is a sequencing judgement, and the right one to record rather than to take silently. The worktree stays
in the plan: it holds real unlanded code, so clearing it would clear half of a change whose other half
is landed.


## Addendum S — 2026-09-27: the rpg-simulator pair, and a stale record that reads `active`

`opencode-resume-13-rpg-simulator-rsf27-20260925` and `review-rpg-simulator-defeat-floor-20260925` are a
lane and its review. Both are **STALE** and both are cleared (34 → 32 worktrees, 39 → 37 branches).
Their shapes are identical, and neither is the rename group the 23 worktrees belong to — these two hold
**real, superseded content** in three artifacts, which is why they are worth writing down.

**The report.** The worktree copy is the original draft; integration holds the later body plus the
addendum and the correction. Sixteen of its worktree-only lines include the two results already
rescued, so nothing is lost a second time. The body at integration is the later and more precise
revision on the point that matters: it tightens the non-vacuity floor from *"must contain at least one
row"* to *"must contain a `player` row whose reason is `defeat`"*, and it corrects the sample
enumeration from *"Sample 13 contained `player:defeat,player:kill`"* to *"Samples 3 and 13"* — the
committed count line carries two `2`s where the draft carried one.

**The test.** `gk-core/tests/FusionRpg.E2E.Tests/RpgSimInProcHostTests.cs` is 9 lines each way, and integration
is later: `hasPlayerDefeatAward` against the draft's `hasDefeatAward` — matching the report's wording —
commented *"must contain the **exact** player/defeat award"*, and a failure message that names the run
(`read a defeat from {runs...result} but read no player/defeat progression-ledger row from {ledger...}`)
where the draft's said only *"read a defeat but no player/defeat row"*.

**The fixture.** `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` differs by one sentence, and
the direction is integration again: the draft restates the rule inline (*"the normal GET read-back must
contain a player row with reason defeat"*) while the committed version drops the restatement and points
at the test (*"checked from the normal GET read-backs by the focused RS-F27 in-process test"*), so the
rule lives in one place instead of three. **All three artifacts are coherent at integration and all
three are a coherent earlier draft here** — which is the strongest form of "superseded" available: not
one file that moved on, but a set that moved together.

**A stale record that reads `active` — and a filter that nearly believed it.** The review worktree's
copy of `tasks/sessions/resume-19-rpg-simulator-defeat-floor-acceptance-20260925.json` says
`"status": "active"`, where both the main checkout and integration say `merged`. The **main checkout is
the authority** the cleanup tool reads, so `merged` governs and the worktree is simply behind on its own
record. A first pass over the active records reported "2 active records naming it" — both false
positives from a substring filter matching *my own* fence, which contains `rpg-sim` paths, and the
template record. Re-ran asking whether each active record's `worktree`/`branch` actually names the
worktree: **none does**. A loose substring over a JSON blob is a name test, and this walk has now been
 bitten by that shape three times.

**The acceptance artefacts are not this worktree's evidence.** Two artefacts match `rpg-sim`: one is for
lane `resume-18`, the other for `resume-20-rpg-sim-defeat-floor-review-20260925` — the review lane
itself, verdict **GREEN**, `sha 4f78ed6c…` **merged into integration**. My first attempt to read their
SHAs took `($_.Name -split '-')[1]`, which yields `18` and `20` — the lane's own number — and so reported
both as "NOT on integration". The convention is `<lane>-<8-char-sha>.json`, so the SHA is the **last**
field. Both are historical entries in the shared `acceptance/` directory, not artefacts sitting in a
worktree, and the rule about not removing a worktree that holds acceptance evidence does not bite.


## Addendum T — 2026-09-27: `resume-08` closed as STALE, and a tool that was inflating every number

`opencode-resume-08-passive-tree-binder-20260925` — **STALE, cleared** (33 → 32 worktrees, 38 → 37
branches). Its 30 dirty paths: 14 are the guard rename, `software-architecture.md` is the
`deploy-play.ps1` → `.py` port, and 14 are STALE at zero residue.

**A C# file that is superseded, not unlanded.** `gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs`
is 7 lines each way, and integration's 53 are a rewrite of the worktree's 7 prose comments into
**measured XML documentation** — `<para>`, `<see cref="TryReadOp"/>`, *"Why `stat.modify` is refused
here, measured rather than asserted (P11.1r)"*, and *"Three independent bars, each verified against
the code that would have to carry it"* opening a numbered list. The `P11.1r` citation is the tell: that
work landed, and its documentation pass is the later revision. The worktree's *"// P4.2: `More` is a
real op for `stat.modify`"* is the earlier phrasing of the same fact.

**A finding that looked unlanded and is tracked as `PT-F39`.** The report's extra content is a
fence-external red: `PassiveTreeEndpointsTests.Post_anOwnedTierOneNodeAfterOpeningTierOne_contributes`
failing in the **Server** suite because *"its fixture's comment already identifies the node atom as
ignored `stat.modify`, but its old expectation still requires that node in the report's derived
`ContributingNodeIds`"*, which the lane deliberately did not edit and named for the
Server/primary-route owner. That is exactly the shape of a rescue — and it is already
`tasks/passive-tree-repair-todo.md:800`, **open**, `PT-F39`, *"found by the resumed manager,
2026-09-25"*, with the root cause documented at `tasks/passive-tree-todo.md:1154`
(`skill.might-off-t1-n0` → `{kindId: "stat.modify", …}`). The test still exists at integration
(`PassiveTreeEndpointsTests.cs:271`, `Assert.Contains("skill.might-off-t1-n0", might.ContributingNodeIds)`),
so the row is live and correct. **Duplicate record of a tracked finding, not an unlanded one** — the same
verdict the `combat-ai` contention cases got, reached the same way: read it, then look for the row.

Nothing blocked removal. The one active record naming this lane is `ps1-ban-manager-20260926`, which
carries the paths in its fence but has `worktree: None` and `branch: features/mega-merge`, so it does
not own this worktree. The one acceptance artefact, `resume-08-passive-tree-20260925-1984dfcd.json`, is
for a SHA **merged** into integration, and the worktree has **0** unmerged commits — so no artefact can
be its pending acceptance. Its own record is `abandoned`.

### The tool was wrong, and every number it printed with it

`dirty_diff.py` built its two line sets by filtering blanks but keeping each line **verbatim**. A
markdown hard break — two trailing spaces — therefore read as content integration lacked. On this
report it reported **9 unlanded lines** where **6** are real, and three of the nine were pure
whitespace. Every residue count this session quoted from that tool was inflated by the same mechanism.

The cause is the same one that produced the `+0` census bug and the "104 pairs for 5 files" grouping: a
measurement that over-reports is worse than no measurement, because its numbers get quoted onward — and
I quoted them. Fixed by stripping both sides, with the reason recorded at the comparison rather than in
a commit message, and re-measured: **6 / 5**, of which four are guard renames, one is the `PT-F39`
paragraph and one its test-result line. **The verdicts do not change** — every file was read, not
counted — but the numbers attached to them were wrong, and the residue column is what a later pass
reuses to decide what to look at.


## Addendum U — the six-investigator pass, and what it corrected in me (2026-09-27)

Six read-only investigators, one report each, stop rule enforced. No lane was resumed, merged, or
closed on a guess. Two independent reports **corrected the manager's own earlier readings**, which is
recorded here rather than replaced, because the corrections are the evidence that the earlier readings
were wrong.

### Where I was wrong

| I had said | measured | how it was found |
|---|---|---|
| the 11 spec-floor files are ones integration lacks | **all exist at integration** | `git ls-tree` per path |
| 11 of 25 worktrees hold nothing of their own | that set **does not exist**: 1 strict, 4 widest | per-worktree floor-only census |
| the spec-fork count of 7 was wrong, it is 25 | **7 is right; holders are 28** | hashed every holder's copy, grouped by content |
| the floor is 11 paths | it is **26** | counted tracked-modified paths across every worktree |
| the `bin/` gap is only in a stale worktree | `.gitignore` has **no `bin/` rule at HEAD either** | `git show HEAD:.gitignore` |

The first three were one error repeated: I measured *unlanded* content with a **reachability** test and
read the result as a fork, when the residue is a **time gradient** — 28 worktrees holding snapshots taken
at different points in one document's life, with integration the newest. Of 883 residue lines, **810 are
neutral, 50 are stale markers, and all 23 "fresh" ones already exist at integration in later form**. The
15 largest holders differ by **two lines**: a `.ps1` filename since ported. Had that been "resolved" by
merging, it would have rewritten `**Status:** part built (CAI1.14, 2026-09-20): sites 1-4` back to
`Not built` across 28 worktrees.

### Verdicts, by group

| group | verdict | the fact that decides it |
|---|---|---|
| 28 spec-residue holders (T1) | **STALE, close (3b)** | time gradient; integration canonical; merging reverts landed status |
| `scope-side-wide`, `resume-04`, `agent-a62e66` (T2) | **STALE** | integration is a strict superset; different mechanism, not newer capability |
| `cmdc-bp-1` (T2) | **STALE** + one mapping gap | BP1.4/1.5/1.9-1.12 all `- [x]`; a `core.loadout-set` group is unmapped |
| `resume-05-vocabulary-*`, `review-vocabulary-*` (T2, T6) | **STALE** | a pre-repair draft; `FamilyExpandManifest.cs:57` already carries the fix |
| `seedsmith-p1-audit-{final,recovery}`, `review/seedsmith-p1-audit` (T6) | **STALE** | byte-identical or strict-subset; the review is a copy, not an independent pass |
| `resume-01-delve-owner-recovery` (T6) | **SUPERSEDED** | same `isPartySteered` design; the replacement is `resume-10`, merged at `17cf1ef5` |
| `corpus-bcu210` (T3) | **STALE, close (3b)** | zero `gk-data/packs/fusion/data/seed` files; `BCU2.10` already `- [x]` |
| `corpus-bcu211` (T3) | **UNLANDED EVIDENCE + branch work** | a 58,830-line uncommitted ledger is not at integration (12,667 vs 386,586) |
| `corpus-bcu211b` (T3) | **UNLANDED GENERATED DATA** | 71/72 uncommitted; the generator moved, so regenerate — never land the diff |
| `corpus-bcu212` (T3) | **UNLANDED GENERATED DATA** | 9 unlanded + 699 untracked, now characterised: 0 of 699 ignored |
| `corpus-bcu213` (T3) | **UNLANDED GENERATED DATA** | 6 unlanded and regressive; `CreatureCorpusDump` has not moved |
| `3307f0597` (T6) | **CHANGE NOTHING** | the proposed `reset --soft HEAD~1` targets the wrong commit (69 back), and 87 of 88 files are an attributed port |
| 3 of 4 LOCKED husks (T6) | **STALE, close (3b)** | landed; `1419a235`, `d6b3b3dd`, `57a1224d` all verified ancestors |

### Two refusals that were the tool working

`resume-34`'s husk is **not clearable**: its record is `active` (never touched by rule), its branch is
**gone**, and the Data half plus the five-step pin resolution are still owed. An active record pointing at
nothing is a decision, not a cleanup item.

`materialistic-spear` looked like an emergency — 4 unmerged commits, no branch, no reflog — but its HEAD
`52fec0bee` survives in the worktree admin record, and **all four are merge commits whose second parents
are already in integration**. A merge introduces no content of its own, so nothing was lost. Note the
trap: `git diff-tree` on a merge reports **zero files** unless `-m` is passed, which would have made this
look empty rather than safe.

### Landed in the owning ledgers

`CAI-spec-fork` closed as RESOLVED-INTEGRATION-CANONICAL with the counts corrected and the merge hazard
spelled out (`tasks/combat-ai-todo.md`); the `BCU2.11` second-pass correction, the per-lane corpus
disposition, the 699-file characterisation and the `.gitignore` `bin/` gap
(`tasks/backlog-clean-up-todo.md`); `SGC-F-dump-args` reattributed from `CreatureCorpusDump` to
`CreatureCatalogGen:13` / `CreatureCorpusEmit:18`, which have no flag guard at all
(`tasks/species-gear-chain-todo.md`); and the Keepverse readiness reading — gate G1 **met**, the tool
**exists**, `apply` **never run**, and `KS5.1`'s "zero findings" satisfiable while 4,197 pieces /
231.98 MB are silently lost (`tasks/keepverse-split-todo.md`).

### The cleanup tool's own blind spot, closed

`git worktree remove` de-registers first and deletes second, so a Windows long-path failure leaves a
directory full of files git can never reclaim. The tool written for that then **refused the real orphan
and named the wrong reason** — `WALK-CAPPED` while `hash-object` had failed. Root cause: git-ignored
build output was never excluded, and 14,912 of 14,912 files on that orphan were ignored.

The obvious fix was a **fail-open trap set by this repo's own `.gitignore:91`**, which ignores
`.claude/worktrees/`: `check-ignore` then answers IGNORED for *every* path under a worktree, including
`gk-core/src/FusionRpg.Server/Program.cs`. Excluding on that answer would have skipped the whole proof and
reported a clean reclaim over **2,171.7 MB** it never looked at. `FailOpenTrapTests` fails if that
regresses. A second defect was ours: `subprocess.run(text=True)` translates newlines in **both**
directions on Windows, so every path sent to git carried a trailing CR and the ignore set matched
nothing.

Applied to the orphan: **3,935 files hashed, every one proven present in integration's history, 10,977
build artifacts cleared across 120 gated subtrees, `unlandedCount: 0`, 2,171.7 MB reclaimed.** The single
non-build file it surfaced was the superseded Delve steering test already adjudicated by hand — the
division of labour working exactly as designed. 73 tests green.

## Addendum V — two clears, and a false alarm withdrawn (2026-09-27)

### `corpus-bcu210` — STALE, closed (option 3b)

- **12 tracked-modified files, every one the spec-floor residue**: the three `combat-ai` specs,
  `software-architecture.md`, two `solid-remediation` specs, two `trade-network` specs,
  `tasks/combat-ai-todo.md`, `CAI1.11`/`CAI1.12`, and the two `cai-*` briefs. Time gradient, not a fork.
- **2 untracked files, `docs/research/action-corpus/_usage-2026-09-21.json` and `-09-23.json`** — these
  needed a content read rather than a name, because the name says "usage" and says nothing about
  whether work is owed. They are **dated population readings** of a series integration already carries
  (`_usage-2026-09-05`, `-09-06`, `-09-09`, plus `_budget-2026-09-19`): `acceptedCount` 1967 and 1968.
  This repo's validation rule is explicit that population counts are readings, never pinned facts, and
  never a contract — so nothing is owed by them and none were rescued.
- **A real observation, recorded rather than discarded**: integration's newest snapshot is
  `_usage-2026-09-09` while the worktree holds `-09-21` and `-09-23`, so **the measurement cadence lapsed
  at integration for 12 days**. That belongs to `action-corpus-todo.md` alongside `AC-F2`; it is not a
  reason to keep a worktree.
- 0 unmerged commits; HEAD `000bb2fc0` is an ancestor of integration; no session record, no active
  record, no acceptance artefact. Cleared: worktree and branch `corpus/bcu210` both gone.

**A lane that left no record at all.** No `tasks/sessions/*.json` mentions `bcu210` — it produced 20
changed files and recorded nothing. The boundary checker cannot see a lane that never wrote a record,
which is a gap in the fence rather than in this cleanup: a lane with no record has no `paths`, so nothing
can detect a crossing with it.

### `baseline-item-seed-base` — STALE, closed (option 3b)

- 9 tracked-modified files: the same spec-floor cluster.
- 13 untracked, because this worktree's HEAD predates the files. The decisive one was the only non-spec
  item: **`gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json`**, a 500 KB generated registry with
  `schemaVersion: 1`, `registryVersion: 2` and **904 themes**. Compared by content rather than trusted:
  **904 themes at integration too, 0 only-in-worktree, 0 only-at-integration, and the whole file is
  byte-identical** (`d1c6c3e02` both sides). So the generated-data rule never engages — there is nothing
  to regenerate because nothing differs.
- The other three untracked (`spec-capture-as-extension.md`, `CAI1.10.md`, `solid-remediation-todo.md`)
  differ from integration, and are the same older-revision cluster.
- **Detached HEAD** at `e0f1375db` with no branch — normally the "unique commit with no ref" emergency.
  **The rule correctly does not fire**: the commit is an ancestor of integration, so nothing is unique.
  The test that matters is reachability, not the absence of a ref. No rescue taken, none needed.

### `materialistic-spear` — the false alarm, withdrawn

The manager reported this worktree as *"there 40 minutes ago and is now gone — along with its branch"*
and began a recoverability check on the strength of 4 unmerged commits read from an earlier census. **That
was wrong.** The manager tested `.claude/worktrees/materialistic-spear`; the worktree lives in
**`.kilo/worktrees/`**. It was never removed, its branch was never deleted, and the reflog and
dangling-commit hunt that followed was chasing a deletion that did not happen.

The check still produced a durable result, so it was not wasted: HEAD `52fec0bee` is **4 merge commits
whose four second parents are all already in integration**, and a merge introduces no content of its own,
so the worktree holds nothing unique. The trap worth keeping: **`git diff-tree` on a merge commit reports
zero files unless `-m` is passed** — the first check said "0 files" and would have made this look empty
rather than safe.

`.kilo/worktrees/` is the Agent Manager's pool and holds exactly two worktrees:
`actor-hud-bottom-anchor-20260916` (214 dirty, 32 unmerged — live, and out of scope by owner ruling) and
`materialistic-spear` (0 dirty, nothing unique). **Deleting from another tool's pool is not this
cleanup's surface**, so `materialistic-spear` is reported clearable and left in place. All 26 other
worktrees are under `.claude/worktrees/`.

## Addendum W — group A: five are clearable, and eight were mis-verdicted (2026-09-27)

The owner directed: adjudicated-STALE items to be investigated and cleaned, the corpus lanes to be merged
if that breaks nothing, and the live/`codex` streams left to other agents. Group A was therefore walked with
a pre-removal check. **It changed the answer on more than half the batch**, and the reason it could is
worth more than the verdicts.

### The check was wrong before the worktrees were

The inherited STALE verdicts came from comparing **tracked** files by line set. The decisive test says
untracked files "must be inspected by content, not by name", and **nobody had**. The pre-removal check
inherited the same gap and then made it worse:

- **it counted untracked ENTRIES.** `git status --porcelain` collapses an untracked directory to a single
  `?? dir/` line, so a worktree holding **33 untracked files read as 6**. The 27-file difference was
  invisible precisely where it mattered.
- **it classified by directory prefix** and moved on. A category like `other` tells a reader nothing about
  whether integration has the file.
- **it never asked the only question that matters**: does integration have this path *at all*?

With that added, **7 of 12 verdicts flipped**. Of the group-A candidates, **5 are clearable, not ~19.**

### Unlanded CODE — real, and it exists nowhere in integration

| file | lines | the decisive measurement |
|---|---:|---|
| `src/FusionRpg.Contracts/ExpeditionDtos.cs` | 53 | **six DTO records, and `git grep` finds NONE of them at integration** |
| `src/FusionRpg.Core/BuildPresets/ValidatedPiece.cs` | 37 | `ValidatedPiece` in 0 files; its enum `BuildPresetPieceState` is at integration, so the record is new or renamed |
| `tools/FamilyExpandGen/FamilyExpandPoolClosure.cs` | 156 | `FamilyExpandPoolClosure` in 0 files at integration |
| `tools/FamilyExpandGen/LatestVersionFile.cs` | 64 | `LatestVersionFile` in 0 files at integration |
| `tests/…PassiveTreeRosterGen.Tests/FamilyExpandGeneratorTests.cs` | 227 | absent at integration, plus a `Fixtures/` file |

`opencode-resume-04-expedition-durability-20260925` was recorded as **"STALE — integration a strict superset
on all 4 contract items."** Its `ExpeditionDtos.cs` was never in that comparison, because it is untracked.
**53 lines of Contracts code that integration does not have.**

The FamilyExpand case is a **fork, not litter**, and it is the one place where a merge would be wrong:
integration's `gk-forge/tools/FamilyExpandGen/` carries `FamilyExpandPoolCatalog.cs` + `VersionedInputFile.cs`, while
the worktree carries `FamilyExpandPoolClosure.cs` + `LatestVersionFile.cs` instead, with new public types
(`FamilyExpandPoolClosureResult`, `VersionedFileSelection`) and a 227-line test written against them.
Integration **did** take the lane's manifest repair — the manifest at HEAD reads `"kind": "affix"`, matching
`FamilyExpandManifest.cs:57` — but not the API rename. So this lane is **PARTIALLY LANDED**: the manifest
half shipped, the code half did not, and the report that says so is unlanded too.

### Unlanded EVIDENCE — and one copy, not three

`BCU2.12`'s run record exists **only inside worktrees**: `BCU2.12-full-run.json`, `BCU2.12-run.log`,
`BCU2.12-run.err`, `tree-language.ledger.json` and a `README.txt`, under
`tasks/evidence-fragments/seedsmith-p1-audit-{final,recovery}/` and again in the review worktree. Plus three
unlanded reports (`seedsmith-p1-audit-recovery-20260925.md`, `seedsmith-p1-audit-acceptance-20260925.md`,
`resume-00b-acceptance-20260925.md`) and a `real-runs/test-9a7035f1….jsonl` in `agent-a62e66`.

This is the class the standing rules protect: **a finding that lives only in a temp worktree is not tracked
work, and a routine cleanup deletes the only record that the work was owed.** The three copies are one
piece of evidence, so they are unioned once rather than rescued three times.

### A rescue taken, then shown to be unnecessary

`review-seedsmith-p1-audit-20260925` held **one commit on no other branch** — the standing rule's emergency
case, so `rescue/review-seedsmith-p1-audit-20260925 -> 6208be7b4` was created **before** anything else. Only
then was the content checked: 8 of its 13 files are identical at integration, 5 differ, **and all 5 blobs
are reachable from integration's history** — they are older revisions of session records and the
verification registry that integration has since updated. So the rescue is insurance that turned out not to
be needed, and the commit is STALE. The worktree still stays blocked, on its 6 untracked evidence files.

The trap: `diff-tree -m` on a merge reports per-parent deltas, so "both parents are in integration" does
**not** settle what the merge's resolution contains. Asking about the blobs directly does.

### Cleared (5)

`cmdc-item-seed-gen`, `cmdc-lane-c`, `agent-a7caaafc906532c18`, `scope-side-wide-20260920` — each with
**0 untracked files**, a HEAD that is an ancestor of integration, a merged or absent record, no active
claim, no acceptance artefact, and 162-164h since last touched. Plus
`opencode-resume-01-delve-owner-recovery-20260925`, whose single untracked file is **identical** to
integration, so nothing is unlanded. That one hit the long-path delete failure again and was reclaimed
through `reclaim_worktree_dir.py` with `unlandedCount: 0` over 3,937 files — the tool doing the job it was
written for, on the second real orphan.

23 worktrees, 29 branches, 6 rescue refs.

## Addendum X — the three unlanded-source items, re-read (2026-09-27)

Addendum W listed five files as UNLANDED CODE. **Two of the five were wrong**, and the error is the same
one this session has now made three times: asking whether a **name** exists at integration rather than
whether integration delivers the **capability**.

### `ExpeditionDtos.cs` — SUPERSEDED, not unlanded. 53 lines, six DTOs, all delivered

Every one of the six concepts exists at integration, under a different name, in a **different layer**:

| the worktree's `FusionRpg.Contracts` record | integration's `FusionRpg.Data` type |
|---|---|
| `ExpeditionCollectResultDto` | `ExpeditionCollectResult` — `RpgStore.Expeditions.cs:47` |
| `ExpeditionTickDto` | `ExpeditionTickOutcome` |
| `ExpeditionCollectBattleDto` | `ExpeditionBattleResult` |
| `ExpeditionMaterialDto` | `MaterialDrop` |
| `ExpeditionSpecimenXpDto` | `ExpeditionSpecimenXp` |
| `ExpeditionTurnOrderEntryDto` | **dropped entirely** — no counterpart at any name |

The single `ExpeditionTickDto` hit at integration is **TypeScript**, not C#:
`gk-web/web/fusion-rpg-web/src/lib/bus/expeditions.ts:36` declares its own type of that name. That is a
parallel client-side projection, not the server contract, and reading it as a reference is what made the
file look load-bearing. **Landing `ExpeditionDtos.cs` would add six orphaned public records to the wrong
layer**, one of which has no integration counterpart in any form. `opencode-resume-04-expedition-
durability-20260925` is therefore **STALE** — and this is the third time a verdict on that lane has moved,
each time toward "already delivered".

### `ValidatedPiece.cs` — UNLANDED CODE, but not verifiable as *needed*. Park it, do not land it

This one is **not** a rename, and the difference matters. Integration splits the idea in two:

- `BuildPresetPieceRow` in `gk-core/src/FusionRpg.Core/BuildPresets/BuildPresetShape.cs:8` carries **4 members**
  (`Kind, TargetRef, Ordinal, RefId`) and its doc comment says the validity question is *"deliberately"*
  not answered there - *"whether a reference still resolves, whether capacity allows the field, whether a
  skill is held: those are the gates' questions."*
- `BuildPresetPieceState` is declared in **`FusionRpg.Data`**, `RpgStore.BuildPresets.cs`.

The worktree **fuses** them into one Core record with `State`, `Reason` and a `Present` projection, and
**moves the enum from Data into Core**. That relocation is the point: `FusionRpg.Core.csproj` references
only `FusionRpg.Contracts` and **not** `FusionRpg.Data`, so integration's placement makes the enum
unreachable from Core - which is presumably why the lane moved it. So the worktree holds a coherent
**layering refactor**, not a broken artifact.

But its owning tasks are closed: `cmdc-bp-1`'s record is `build-preset-bp1`, status `abandoned`, and
BP1.4 / 1.5 / 1.9-1.12 are all `- [x]`. So the fusion refactors a closed task set, and integration
carries a deliberate two-type alternative. **Whether to take it is a build-preset program decision, so
this is PARKED (option 4) with the decision named** - not landed, and not silently dropped.

### The FamilyExpand pair — a genuine fork, and the one place merging is wrong

`FamilyExpandPoolClosure.cs` and `LatestVersionFile.cs` are **0 files at integration**, while the names
they replace - `FamilyExpandPoolCatalog` and `VersionedInputFile` - are at integration in 2 files each.
So this is a **rename the lane performed that integration never took**, together with new public types
(`FamilyExpandPoolClosureResult`, `VersionedFileSelection`) and a 227-line test written against them.

Integration **did** take the lane's other half: the manifest at HEAD reads `"kind": "affix"`, matching
`FamilyExpandManifest.cs:57`'s `SeedReaderKind = "affix"`, where the empty `entries` array is documented as
load-bearing. So the lane is **PARTIALLY LANDED** - the manifest repair shipped, the API rename did not, and
the report saying so was unlanded until this session rescued it.

Merging this one would be the single most damaging action available in the whole leftover set: it replaces
integration's pool-catalog and versioned-input types with a different public API, on a lane whose own
tests target the new names, for a task set that is closed. **It needs an owner ruling.**

### Net effect on the census

Group A's unlanded-CODE count falls from five files to three, and those three are **one** decision:

    ExpeditionDtos.cs          SUPERSEDED   (all six concepts delivered in Data)
    ValidatedPiece.cs          PARKED       (a layering refactor for closed tasks)
    FamilyExpand pair + test   FORK         (integration took the manifest half, not the API half)

`opencode-resume-04-expedition-durability-20260925` and `cmdc-bp-1` return to STALE. Only the FamilyExpand
fork is live, and it is a program decision rather than a cleanup.

## Addendum Y — the 12.5 MB I nearly called residue held the run's only finding (2026-09-27)

Clearing the `seedsmith-p1-audit` trio needed a decision on three unlanded files shared by all three
holders: `BCU2.12-run.err` (0 b), `BCU2.12-run.log` (10,033,057 b) and `tree-language.ledger.json`
(12,467,133 b). My earlier reasoning on this pair was that both are regenerable residue of a run
interrupted at 1 of 904 species, that the 3.5 KB census already landed carries the population, and
that 22.5 MB of interrupted-run output is not owed work. **That reasoning was right about the log and
wrong about the ledger**, and the way it was wrong is worth recording.

### What the check actually found

Read by shape rather than sampled — the log is 114,203 lines, so a sampled read would have missed the
point and a verbatim read floods a session with 10 MB of generated node ids:

| artefact | shape | error/verdict lines | distinct shapes |
|---|---|---|---|
| `BCU2.12-run.log` | 114,203 lines, longest 593 chars | 52 | **3** |
| `tree-language.ledger.json` | 386,586 lines, JSON, one `done` map of 15,597 keys | 3,680 | **984** |

The log's 52 are three transport/model-transient signatures (`HTTP 500`, `HTTP 400 Bad Request`,
`DegenerateGenerationError: repetition loop`), all retried. The ledger's 3,680 across 984 "shapes"
differ only in a quoted generated name, so it is **one** defect wearing 984 masks. Grouping by
`(file, worktree)` or by line would have reported 3,711 problems; grouping by content found two.

The landed census mentions `error`, `fail` and `reject` **zero** times. So the finding was recorded
nowhere at integration, and calling the ledger residue would have destroyed the only copy of it.

### The finding

> Corpus-wide node-name uniqueness has no deterministic fallback. Of **15,597** attempted node subjects
> the run committed **10,164** and failed **5,433 (34.8%)**, and **3,633 of those 5,433 failures
> (66.9%)** are the same defect: a name-collision gate the model-only repair loop cannot satisfy.
> All 3,633 carry `outcome=escalated`, so the gate is **99.2% of the entire escalation population**
> (3,633 of 3,661). 957 distinct names were rejected; `Primal Ferocity` alone was rejected **74** times.

Both code sites are still present at `features/mega-merge`, so this is **open** work, not a closed
incident. The asymmetry that makes it a finding rather than a shrug: the items pipeline solves the
identical corpus-wide problem **deterministically** (`adapters/items/setgen/name_repair.py` —
`NameRepair` keeps the lexically first id of each collision group and renames every other row). The
node path has no equivalent, so a third of the run is lost to a condition the sibling pipeline
already handles without a model call.

A second, smaller defect is recorded in the same fragment: `name_collision`
(`workflow/validators/field_echo.py:92`) hardcodes *"already used by another **commander effect**"*,
but its `nodegen` call site (`adapters/trees/nodegen/run.py:249`) checks **passive-tree node** names —
`taken_names` is seeded corpus-wide from the ledger's own node `record.name` values (`run.py:1084`). So
every one of the 3,633 failures logged a message naming the wrong subject kind, which is precisely why
the ledger reads as 984 distinct shapes until the quoted name is masked out. The wording is the reason
this finding was nearly missed.

Landed as `tasks/evidence-fragments/seedsmith-p1-audit-final-20260925/BCU2.12-failure-census.json`
(7,874 b) — computed from the sources rather than transcribed, carrying the parse rule and a
re-derivation command, and stating that its 22.5 MB sources are deliberately **not** landed. A number
in it is a dated reading of one interrupted run and must never be pinned in a guardrail.

### A correction inside the correction

My first pass reported the collision rate as **23.3%** — failures over all 15,597 rows. That is wrong
by a third, and wrong in the direction that flatters: a row carrying a non-null `record` is a
**committed** node and belongs in neither numerator. The ledger holds two structurally distinct
populations, told apart by `record`:

    10,164 rows   record is a non-null dict, no detail   -> committed a node
     5,433 rows   record is null, has detail+outcome+attempts -> failed
                  outcomes: escalated 3,661 | unresolved 1,739 | blocked 33
                  attempts: 1 x 5,081 | 2 x 352

This is the same family as the three corrections already made this session — tracked-only line sets
reading a gradient as a fork, a substring search missing `[Bb]in/`, "does this type name exist" as the
test. Each time the cheap measure was available, plausible, and wrong. The shape of the trap is
constant: **a population that is not homogeneous gets measured as if it were.**

### The owed edit, and why it is not landed

The owning ledger for this finding is `tasks/passive-tree-todo.md`. It is **not** written, because
`tasks/sessions/ps1-ban-manager-20260926.json` is `status: active` and claims that path. Writing there
is a crossing with a live session, so the finding is landed as a new evidence fragment and the owed
edit is recorded here for whoever holds that fence:

> **`passive-tree-todo.md` — add a row for the corpus-wide node-name-collision failure (Addendum Y).**
> No existing row covers it: `passive-tree-todo.md:3336` and `:6214` both reference `name_collision`,
> and `seedsmith-todo.md:2193-2197` is the row that added the gate — but all three are *shipped
> metrics* reusing the validator (`NameCollisionMetric`, the U1 corpus-wide `(name, flavor)` index),
> i.e. post-hoc measurement. None records what the gate did to a real run. Evidence:
> `tasks/evidence-fragments/seedsmith-p1-audit-final-20260925/BCU2.12-failure-census.json`. The
> candidate fix is a deterministic name-repair fallback on the node path mirroring
> `items/setgen/name_repair.py`, plus correcting the validator's subject-kind wording. The 10 MB log
> and 12.5 MB ledger are NOT to be landed.

This session's own fence was widened by exactly one path for the new fragment, and the amendment
refuses if any `active` record already claims the path. The fence also deliberately does **not** gain
`tasks/passive-tree-todo.md` — which is why that row is an owed edit here rather than a silent loss.
## Addendum Z — the trio cleared, and six defects in the tools that were supposed to prevent this (2026-09-27)

`opencode-seedsmith-p1-audit-{final,recovery}` and `review-seedsmith-p1-audit-20260925` are gone
(**19 → 16 worktrees, 27 → 23 branches**), and `rescue/review-seedsmith-p1-audit-20260925` is deleted
as spent insurance. Every file in all three was STALE, SUPERSEDED or STALE-RENAME — the only unlanded
content was the 22.5 MB pair Addendum Y distilled, and the rescue ref's 3,222 blobs were all already in
integration's history.

The interesting part is how nearly they were cleared **wrong**, six times, by tooling of my own. Every
one of these produced a confident, wrong, actionable claim, which is the definition of the failure mode
the procedure exists to stop. None was caught by reading the output harder; each was caught by a
measurement that contradicted the first one.

### 1. `preclear.py` only ever compared untracked files

The three worktrees held 13–16 unlanded files each. `preclear.py` had reported 3–5, because it reads
`git status`, and git collapses an untracked **directory** to one `?? dir/` entry. Its own expansion
under-reported by roughly 3x. The fix is not a patch to preclear: `audit_registered.py` calls the
reclaim tool's `audit_unlanded`, which hashes every file including tracked-modified ones, and does so
**before** removal rather than after. `audit_unlanded` does not care whether a directory is still
registered — only `reclaim_worktree_dir` refuses that, because only it deletes — which is exactly what
makes it safe to run as a pre-removal check.

### 2. The line-set test's `only_head` was inverted

`only_head = [l for l in hvis if hset_counts[l] < mvis.count(l)]` measures worktree *surplus*, which is
already `only_mine`. It was therefore structurally pinned at **0** for every file — the field that
carries integration's side of a comparison can never be non-zero if it measures the wrong direction.
Every file reported "integration has nothing the worktree lacks", which is the signature of a tool that
has been quietly agreeing with you. Fixed to `>`, and the only reason 11 files were then testable at
all.

### 3. The rename mask could not match the rename it was written for

`re.sub(r'\.[A-Za-z]{1,5}\b', ...)` cannot match `.ps1`: `1` is not a letter, and `\b` never falls
between `s` and `1` because both are word characters. The mask existed to see the ps1-ban
`.ps1` → `.py` port, and was blind to precisely that — the one rename the standing rule names by
example. Needs `[A-Za-z][A-Za-z0-9]{0,4}`.

### 4. …and then the invocation form, and the separator

Erasing the extension is not enough, and finding that out took two more passes:

    worktree:    .\scripts\guard-tuning-immutability.ps1
    integration: python  gk-core/scripts/guard-tuning-immutability.py

Erasing the extension leaves `python ` on one side and `.\` on the other. Erasing the invocation word
then leaves a **backslash** against a forward slash. Both are the same guard, on the same line, in the
same sentence, in `tasks/combat-ai-todo.md` — which integration holds verbatim nine lines further down.
The ordering matters too: stripping `./` *before* converting `\` → `/` leaves `.\scripts\x.ps1`
becoming `./scripts/x.ps1` with a leading `./` its ported twin never had, so the pair still fails on a
character nobody would read as a difference. Normalise separator first, then prefixes.

With all three, **12 of 12** files resolve to STALE-RENAME and genuinely unlanded content drops to
**zero**. Before the fix, 11 files / ~460 KB of already-landed substance read as unlanded work — which
is the documented `deploy-play.ps1` incident, reproduced, on a different lane.

### 5. A non-homogeneous population measured as if it were one

The first census said the collision gate failed **23.3%** of the run. The ledger holds two
structurally distinct populations: 10,164 rows carrying a non-null `record` (**committed** a node) and
5,433 carrying `record: null` + `detail`/`outcome`/`attempts` (**failed**). Dividing by all 15,597
counts committed nodes in the denominator and is wrong by a third — **34.8%** is the failure rate, and
3,633/5,433 = **66.9%** of failures are the one gate. Same shape as the three earlier corrections this
session: the cheap measure was available, plausible, and wrong. The constant lesson is that a
population which is not homogeneous gets measured as if it were, and the tell is always a rate that
looks tidy.

### 6. A wrong flag and a wrong parser, both reporting "nothing differs"

Checking the rescue ref took two false negatives in a row:

- `git diff -m A B` returned **0 paths**. `-m` is a `diff-tree`/`log` flag; `git diff` compares two trees
  and wants none. The repo's standing warning is that `diff-tree` reports zero files *without* `-m` —
  the mirror trap is passing `-m` to a command that never wanted it.
- Then `git diff --raw` returned 2,274 lines and the parser kept **none**. In non-`-z` raw format the
  status is the last *space*-separated token of the first tab field, not a tab field of its own, so
  `len(parts) < 3` skipped everything. The field indices were wrong too (`:oldmode newmode oldsha
  newsha status`, and I had read `status` from the old-SHA slot).

Both read as "nothing differs", and either would have deleted a ref that was the last holder of an
unmerged merge commit. The parser now counts rows and **refuses on any unparsed line**, because a diff
this loop cannot account for is a measurement failure, not a finding.

### The standing rule all six share

Every one of these produced *silence* where a difference should have been reported, and silence reads as
permission. A measurement that cannot fail is not a measurement. The concrete form this takes: a
derived field that is structurally constant, a mask that cannot match its own target, a parser that
skips what it does not understand, and a denominator that mixes two populations. Each is cheap to check
and none was checked by re-reading the output — only by asking a *second, independent* measurement and
believing the disagreement.

## Addendum AA — a green gate on a run where nothing ran, and the only fix was uncommitted (2026-09-27)

`opencode-resume-00a-fail-closed-recovery-20260925` was audited next. Its 17 unlanded files split into
the 11 ps1-ban renames already resolved in Addendum Z, `.git`, one report line, and **four files
carrying a live fail-closed fix that exists nowhere in git**.

### The defect

`post_merge_check.py` decides whether a check ran by `Test-PositiveTestCount`:

    integration   [regex]::Matches($line, '(?i)\b(?:Total|Passed):\s*(\d+)')   -> Total: 1   => TRUE
    worktree      foreach ($field in @('Passed', 'Failed')) { ... }            -> 0 and 0    => FALSE

`Total` counts **skipped** tests. So a run reporting

    Passed!  - Failed: 0, Passed: 0, Skipped: 1, Total: 1

has a positive test count at integration, produces no red, and the merged-head gate returns **GREEN** —
for a run in which no test executed. This is the standing trap in its purest form, and it sits in the
harness that decides whether a lane is accepted, so it is fail-open at the point of acceptance rather
than in a leaf test. The worktree's version excludes `Total` deliberately and pins it with
`test_skipped_only_test_count_is_red`.

A second, smaller change rides along: integration's `Test-FailedSummary` matches only `Failed!` and
`Build FAILED`, while the worktree also matches `Test Run Failed\.` — the summary `dotnet test` prints
on a failed run, which a zero process exit can otherwise carry unflagged.

Both are **live at integration**. `accept-lane.ps1`'s verdict validation is *not* part of this finding:
integration's `$AcceptanceVerdicts` array with `-cnotin` (L141-143) is a better form than the
worktree's inline `-notmatch`, and integration is 36 lines ahead on the reporter's tests (57 methods to
53) — so the worktree is the older snapshot there, not the newer one. Reading "the worktree has lines
integration lacks" as "integration is behind" would have been wrong for two of the four files.

### Why it nearly died, and why a rescue ref was no help

The fix was **uncommitted**. It existed only as working-tree files, so:

* the branch ref captured none of it — a rescue ref, the standing answer for a unique commit with no
  ref, is *worthless* against uncommitted work and would have looked like due diligence;
* `git worktree remove` would have deleted the only copy;
* the audit's own reachability test calls these files "unlanded", which is true and is the reason not
  to clear, but does not by itself preserve them.

So the diff was extracted first, with `difflib` against integration's copy, and verified to **apply and
reverse** in a scratch worktree before committing — a rescue artefact that does not apply is not a
rescue. Landed as
`tasks/evidence-fragments/resume-00a-fail-closed-recovery-20260925/post-merge-check-positive-test-count.patch`
(22,651 b, 4 file diffs).

The path rewriting in that tool went wrong first, and recognisably: `git diff --no-index` printed the
scratch path through the **8.3 short-name alias** (`NENESC~1`) while the rewrite used the long path, so
no replacement matched and the patch did not apply. That is the same alias trap the standing rules name,
hit a third time in this cleanup — `os.path.samefile` and `difflib` over string rewriting are the two
answers, and only the first was reached for by hand.

### The owed edit, and where it is not going

The fix belongs in `.claude/cmdc-agents/scripts/post_merge_check.py`, which
`ps1-ban-manager-20260926.json` (`status: active`) claims via `.claude/**`. It is not applied here.
Named for whoever holds that fence:

> **`post_merge_check.py::Test-PositiveTestCount` — drop `Total` from the positive-count regex.**
> `Total` counts skipped tests, so a run that executed nothing is GREEN. Replace
> `'\b(?:Total|Passed):\s*(\d+)'` with a check on `Passed` and `Failed` only, and add
> `Test Run Failed\.` to `Test-FailedSummary`. Apply
> `tasks/evidence-fragments/resume-00a-fail-closed-recovery-20260925/post-merge-check-positive-test-count.patch`,
> which carries both changes plus the two tests that pin them
> (`test_zero_exit_test_run_failed_summary_is_red`, `test_skipped_only_test_count_is_red`).
> Prove with the fail-closed pipeline suite, not by reading the diff.

This session's fence gained that one evidence path and deliberately did **not** gain the script.

## Addendum AB — the resume-00x trio, a downgrade caught by reading the diff, and four spent rescue refs (2026-09-27)

`opencode-resume-00a-fail-closed-recovery-20260925`, `opencode-resume-00b-verification-topology` and
`opencode-resume-00c-split-core-mapping-20260925` are cleared (**16 → 13 worktrees, 23 → 17 branches**).
Addendum AA already covers 00a's rescued fix; what is new here is 00b, and a lesson about the test
itself.

### 00b: the "unlanded" line was a downgrade

`publish-player.ps1` produced a genuinely-new line that read like a missing fail-closed guard:

    + if (-not (Test-Path "node_modules")) {
    +     npm ci
    +     Assert-NativeExit "npm ci"
    + }

Rescuing it and reading the actual hunks inverted the verdict. Integration is the **newer** file on both
counts: the worktree re-duplicates a `package-lock.json` precondition that integration had already
removed, and it calls `guard-game-profile.**ps1**` where integration calls the `.py` — beside
integration's own comment, which says it exactly:

> The guard is Python now, so the invocation and its arguments are the .py spellings. A stale
> `& path.ps1` here fails only when a player pack is BUILT, which is the worst place to discover it.

So the "unlanded guard" was a repair, and adopting it would have reinstated a **build-time-only
failure in the player pack**. The patch was generated, verified to apply, read, and discarded unlanded.

The same holds for `release.yml` and `VerificationTopologyTests.cs`: the worktree's `release.yml` has
**13** raw `VERIFICATION_GATE:` markers and integration has **0**, while integration's shipped
`VerificationTopologyTests.cs:90` asserts `DoesNotContain("VERIFICATION_GATE:", release)`. Merging that
lane's work would turn a green test red. SUPERSEDED, and regressing.

**00c** is a plain gradient: the same 7 split areas, the same paths, the same `core-area-*` ids — and
integration's mapping records carry a sixth argument the worktree's do not.

The lesson is about the tool, not the lane. "Genuinely new" is a *line-level* signal and says nothing
about direction; a file can gain lines by being repaired and lose lines by being improved. Only the
diff says which, and the diff is one command away. A line-set verdict that stops at "these lines are
not at integration" is the same class of defect as the inverted `only_head` in Addendum Z: a partial
measurement that reads as a complete one.

### The rescue sweep: five refs, one load-bearing

Every rescue ref was re-checked with the corrected blob proof rather than assumed:

| ref | unlanded blobs | verdict |
|---|---|---|
| `adopt-worktree-cleanup-20260925` | 1 of 3038 | spent — a **strict prefix**, see below |
| `corpus-bcu211-itemseedgen-run` | **56 of 11100** | **REQUIRED** |
| `resume-30-commandcode-config-review` | 0 of 3033 | spent |
| `review-resume-00a-final` | 0 of 3224 | spent |
| `review-tvb3` | 0 of 11805 | spent |

Four deleted; one kept. The keeper is the whole group-B question in a single ref: 50
`gk-data/packs/fusion/data/seed/items/base-types/**` rows, three `drop-tables/*.json`, `materials.json`, three
`_runs/*.ledger.json`, `combination-still-blocked.json`, and `tasks/reports/BCU2.11-full-run.json` —
its subject line reads *"the item-seedgen full run -- 56 files, gaps 931 -> 770"*. It is a real
population delta against a corpus that has since been regenerated, so "merge it if it won't break
anything" has to be answered per file, not per ref.

### A blob that is not in history is not always a loss

`adopt-worktree-cleanup-20260925` was flagged for exactly one path —
`tasks/sessions/worktree-cleanup-20260925.json` — whose blob `4525630c` appears nowhere in history. The
file exists at integration, in a *different* blob. Reading the two:

    rescue      notes:  924 chars
    integration notes: 1981 chars
    the diff is ONE line, and the integration side is the longer one

Integration holds a strict **superset** of the same note. So the blob test was right — that exact
content was never committed — and substantively wrong: it reported a superseding edit of a file as an
unlanded one. **Blob identity is not loss any more than reachability is not landing.** The two known
false positives now have a shared shape, and both are cured by the same question: does integration hold
*this content or more of it*, asked per file and not per blob.

This is the third distinct lesson in this cleanup pointing the same way — a residue spread across
worktrees is a **time gradient** far more often than it is a fork. Every one of them was a measurement
that could not tell "newer" from "older", and every one produced an actionable, wrong answer.

### Correction to Addendum AA, same day

The owed edit above names `.claude/cmdc-agents/scripts/post_merge_check.py` as its target. While
committing this addendum the commit gate refused, because the index already held that file and
`accept-lane.ps1` as **staged deletions** — 603 and 479 lines removed, both gone from disk, and
**neither has a `.py` replacement on disk or in the index**, with
`test_fail_closed_pipeline.py` modified in the working tree beside them.

That is an in-flight port by `ps1-ban-manager-20260926.json` (`status: active`, which claims
`accept-lane.ps1` directly), not a change from this session. It was left exactly as found: staged
deletions are another lane's work, and unstaging them would destroy their staging the same way a broad
`git stash` would.

Two consequences, both of which make the earlier wording wrong in a way worth recording:

1. **The rescued patch is a reference, not an applicable change.** It is written against the `.ps1`
   form, which is mid-deletion. Whoever applies the `Total` → `Passed`/`Failed` fix must apply it to
   whichever form of `post-merge-check` survives the port, and the patch's own header claim — that it
   applies to `features/mega-merge` — was true when written and will stop being true the moment the
   port lands. A rescue artefact that names a moving target is a rescue with a shelf life, and the
   honest thing is to say so rather than let the "verified to apply" line imply permanence.
2. **A gate script deleted with no replacement is a live risk, and it is not this session's to
   resolve.** `post_merge_check.py` is the merged-head gate; `accept-lane.ps1` decides lane
   acceptance. If the port commits the deletions before the `.py` replacements, the gate is simply
   gone — and `test_fail_closed_pipeline.py` is already modified in a way that suggests the port is
   part-way through. Surfaced here rather than acted on: the owning session is active, and an
   interrupted session's staged work is not a cleanup target.

### Retraction of one clause in the correction above, and the finding survives the port

The correction states that neither script has "a `.py` replacement on disk or in the index". **That is
false and is retracted here.** The replacements exist, tracked at HEAD, on disk and in the index:

    .claude/cmdc-agents/scripts/post_merge_check.py        (plus test_post_merge_check.py)
    .claude/cmdc-agents/scripts/accept_lane.py             (plus test_accept_lane.py)

The error was mine and it is the same blind spot the rest of this cleanup keeps hitting: I searched for
`post-merge-check.py` — extension-only — when the port renamed the **stem** to snake_case
(`post_merge_check.py`), not merely the extension. Checking one axis of a two-axis rename finds nothing,
and "nothing" then reads as "no replacement exists", which is a stronger and wrong claim than "not at
the path I guessed". The hyphen/underscore difference is a fourth instance of the same shape: a
measurement that cannot see a rename reports absence.

`6f479d091` ("Retires two Tier-5 .ps1") is also **not** the commit that touched these two — it retired
`resolve-append-only.ps1` and `verify-no-disk-write.ps1`. The two gate scripts are still present at HEAD
and still staged for deletion, so the port remains in flight for them.

**The finding itself survives the port, which is the part that matters.** `post_merge_check.py:123`
carries the defect across verbatim:

    POSITIVE_COUNT_RE = re.compile(r"\b(?:Total|Passed):\s*(\d+)", re.IGNORECASE)

`Total` counts skipped tests, so `Passed! - Failed: 0, Passed: 0, Skipped: 1, Total: 1` still satisfies
the positive-count check and the gate still returns GREEN for a run in which nothing executed. The port
translated the bug faithfully; translating a bug is what a port does. `Test Run Failed.` is likewise
absent from the `.py` (0 occurrences), so that half of the finding is unlanded in the new form too.

The corrected owed edit, for whoever holds the ps1-ban fence:

> **`post_merge_check.py:123` — drop `Total` from `POSITIVE_COUNT_RE`, and add a `Test Run Failed.`
> branch beside the `Failed!`/`Build FAILED` summary match.** The rescue patch
> (`tasks/evidence-fragments/resume-00a-fail-closed-recovery-20260925/post-merge-check-positive-test-count.patch`)
> is the reference implementation of both changes and of the two tests that pin them
> (`test_zero_exit_test_run_failed_summary_is_red`, `test_skipped_only_test_count_is_red`); it is
> written against the `.ps1` form, which is staged for deletion, so port the change rather than apply
> the patch. The replacement suite already has
> `test_a_positive_test_count_is_required` and `test_a_zero_exit_with_a_failed_summary_is_red` — the
> gap is that neither pins the **skipped-only** case, which is the one `Total` lets through.

Nothing about the live risk has changed: the gate scripts exist in both forms, and the defect is in
whichever one runs.

## Addendum AC — group B: the corpus lanes must NOT be merged, and the "regenerate later" already happened (2026-09-27)

The owner ruled: *"merge the 4 corpus lanes if it won't break anything, regenerate later."* The
conditional fails, and not narrowly. **All four `corpus-*` worktrees and their branches are cleared**
(**13 → 9 worktrees, 17 → 13 branches**), and the one branch that had anything to merge is **retained
under a rescue ref rather than merged**, because the finding behind that decision is the owner's to
overturn, not mine to execute by deleting the evidence.

### What the four actually were

Three of the four had nothing to merge at all — `corpus/bcu211b`, `bcu212` and `bcu213` are already
ancestors of integration, 0 unmerged commits. Their only content was uncommitted working-tree residue:
84, 719 and 18 unlanded files respectively, **every one of them under `gk-data/packs/fusion/data/seed/**`**. That is
generated data from interrupted or partial runs, and the standing rule is categorical — regenerate on
current head, never land an old diff. `corpus-bcu212`'s 719 are the BCU2.12 residue already adjudicated
in Addendum Y (an interrupted run that completed 1 of 904 species). Nothing to rescue, so all three
cleared on the sanctioned route; none needed the reclaim tool, and the prefix gate was never asked to
wave away tracked generated content.

### The fourth: why merging it would have broken things

`corpus/bcu211` is the only lane with an unmerged commit — `6fc3d2b21`, *"the item-seedgen full run --
56 files, gaps 931 -> 770"*, the target of `rescue/corpus-bcu211-itemseedgen-run`. It is **not** a
fast-forward. It is divergent from a merge-base, one commit each way, and merging it would touch
**6,973 files with 173,231 insertions and 449,213 deletions**:

    gk-data/packs/fusion/data/seed/items/materials/materials.json     integration 426 lines   corpus/bcu211 59,130 lines

Those 449k deletions are not corpus changes; they are every document, skill, test and web file that
landed on integration after the branch point. The single commit itself is narrow — 55
`gk-data/packs/fusion/data/seed/items/**` paths plus `tasks/reports/BCU2.11-full-run.json` — which is why the surgical
alternative is a cherry-pick. And the cherry-pick is the one the hard rule forbids:

* every generator and corpus commit since the divergence is in integration and **not** in bcu211 —
  `f671cc5ad` (*"author the per-base-type armour successor edges and regenerate the corpus"*),
  `808b727d8` (*"corpus re-emit, pricing floors, materials constant"*), `3ff951918` (*"item emitters
  stamp the resolved model"*);
* the regeneration demonstrably **covered bcu211's own paths** — `f671cc5ad` touched 35 base-types
  files, **29 of which overlap** bcu211's 55 data paths;
* and the content proves it. Integration's `base-types/footing/plant/a.json` carries **20** occurrences
  of `successor`; bcu211's carries **0**.

So integration already holds a **later** regeneration of exactly these files, containing rows bcu211
never produced. The owner's "regenerate later" is not a future step — it happened, twice, on current
head. Landing the old diff would replace newer generated output with older generated output, which is
the exact failure the rule exists to prevent.

`tasks/reports/BCU2.11-full-run.json` is a **census**, and integration's copy is the newer one: the same
14 keys, differing only in `head` (`ac0fd77c` vs `784555a1b`), `gitStatusPorcelainCount` (70 vs 55) and
`diffStatTail`. A dated population reading is a reading, never owed work.

### Why the rescue ref is kept

`rescue/corpus-bcu211-itemseedgen-run` is the **only** ref holding those 56 file versions. Its content
is adjudicated SUPERSEDED and must not be landed, so it is spent insurance by the letter of the rule —
and it is kept anyway, deliberately. A ref costs 41 bytes, and deleting it would foreclose a decision
that belongs to the owner: the ruling was conditional on safety, my finding is that it is unsafe, and
the owner may reasonably want to inspect the 56 files before accepting that. One classified ref is a
legitimate terminal state; a deleted ref is not reversible.

### The answer to the ruling, stated plainly

**Do not merge the corpus lanes.** Three had nothing to merge; the fourth's merge is a 449k-line
deletion and its cherry-pick is forbidden stale output whose regeneration already exists. If the
`gaps 931 -> 770` improvement is still wanted, the sanctioned route is to re-run the generator on
current head and commit the fresh diff — not to recover the September snapshot.

## Addendum AD — the closing census, and a claim about the main worktree that measurement retracts (2026-09-27)

### The main worktree is not an unlanded holder

The standing claim about this cleanup was that *"the main worktree on the integration branch is itself
the largest single unlanded holder and no migration mechanism can catch it."* Measured, it is not. Its
entire working state is **10 tracked changes, every one of them claimed by an active session**:

| change | active owner |
|---|---|
| `accept-lane.ps1`, `post_merge_check.py` staged deleted; `test_fail_closed_pipeline.py` modified | `ps1-ban-manager-20260926` |
| `scripts/lane-server.ps1`, `gk-core/scripts/verification-boundaries.v1.json` | `ps1-ban-manager-20260926` |
| 3 `blender/**` files + `tasks/sessions/ice-shield-sprite-export-20260927-41bc.json` | `ice-shield-sprite-export-20260927-41bc` |
| `tasks/sessions/ps1-ban-manager-20260926.json` | `ps1-ban-manager-20260926` |

plus 3 untracked `blender/` paths (5 files). So the main worktree holds **no unlanded work of its own** —
it holds two live sessions' in-flight work, which is precisely what a shared main checkout is for and
exactly what must not be cleaned. The claim was right that no migration mechanism can see it and wrong
about what is in it. (`mega-merge-program-manager-20260925-f78e` also matches several of those paths,
but only through this session's own broad `.claude/**` and `verification-boundaries.v1.json` fence
entries — none of them is a change this session made.)

### `main` is a merge record, not a leftover

`main` is 4 commits divergent from integration, every one titled
`Merge pull request #NN from letuhao/features/mega-merge` — and its tree is **byte-identical to its
merge-base** (`7cb9a330c` on both). So those four merges were no-ops: main was already current when
each was made. All 2,102 differing blobs are in integration's history, so nothing is unlanded. It is
the published branch of record (PRs #18–#21), not parallel-program residue, and it is **retained**.

### Where the set actually stands

Worktrees **9 → 8 by the status reader's count** (it excludes the main checkout), branches 11, rescue
refs 1. Every remaining item is classified, and only four need an owner:

| item | verdict | why it is not actioned |
|---|---|---|
| main checkout | live shared work | two active sessions in flight |
| `ps1ban-l3-checks`, `ps1ban-l4-artifacts` | out of scope | owner-ruled: another agent's live work |
| `actor-hud-bottom-anchor-20260916`, `materialistic-spear` | out of scope | owner-ruled: group C |
| `cmdc-bp-1` | **PARKED** | `ValidatedPiece.cs` layering refactor — a program decision |
| 3 vocabulary worktrees | **PARKED** | the FamilyExpand API fork — a program decision |
| `main` | merge record, no-op | retained; nothing unlanded |
| `rescue/corpus-bcu211-itemseedgen-run` | SUPERSEDED, retained | 56 stale generated blobs; owner's to inspect |

Read against the objective's success criterion, the cleanup is **complete except for the two owner
rulings**: no registered worktree or branch is unclassified, every classification above is backed by a
command that can be re-run, and the one place a failed delete could have left an un-reclaimable
directory — the long-path orphans — is fixed in the tool rather than left as a known gap (Addendum V,
with the second orphan reclaimed at **2,171.7 MB**).

Two numbers are deliberately *not* quoted: a count of zero, because no program was measured to zero
open blocks by me, and the corpus population, because a dated population reading is a reading.
`program_status.py` reports `passive-tree` at **2 open task blocks (J10, J13), 2 done, 2/2 verified,
fenced by `ps1-ban-manager-20260926`** — which is also the independent confirmation that the
`passive-tree-todo.md` finding from Addendum Y is correctly parked rather than applied.

## Addendum AE — the drift question, answered by measurement rather than by a label (2026-09-27)

The owner asked, of "superseded them": *"then what next? drift forever?"* That is the right question to
ask of a verdict that is only a label, and the answer is that the drift was real, was **named in the
tool's own output**, and is now closed. Both parked decisions are cleared as superseded
(**9 → 5 worktrees, 11 → 7 branches**), and here is why that is not the end of the story.

### The loop was in the tool's own words

`retire_worktrees.py` reported:

> **37** director(ies) sit beside the worktrees that `git worktree list` does not report — **33 still
> hold content** … **This tool does not remove these.** Deciding that one is disposable requires
> adjudicating its content … Adjudicate first, then delete by hand.

That is the drift loop, written down: the survey can name a leftover but cannot decide one, so every
run regenerates a human queue. A verdict that only labels a directory does nothing about that.

### The queue was wrong twice, and both errors flattered the tool

Running the reclaim tool's own proof over the same directories:

| | count |
|---|---:|
| leftovers reported | 37 |
| told to adjudicate | **33** |
| actually provably stale or empty | **14** |
| genuinely holding unlanded content | **23** |

And of those 37, **30 are not repository content at all**. They sit under
`C:\Users\NeneScarlet\AppData\Local\Temp\opencode`, and they enter the count only because two
owner-ruled ps1-ban worktrees (`ps1ban-l3-checks`, `ps1ban-l4-artifacts`) are themselves registered
there — the scan derives its candidate parents from registered worktrees, so a worktree living in a
temp directory drags every sibling scratch directory in with it. My own session scratch,
`sess-f78e`, is one of the 23.

So "adjudicate 33" was really **"adjudicate 23, of which 0 are the repository's"**. The repository's
own leftover debt across both pools is **one** directory, and `--prove-stale` proves it stale.

### The fix, in `gk-core/scripts/retire_worktrees.py`

`--prove-stale` (committed `588909b4b`, 62 tests green) classifies every leftover by **content** using
`reclaim_worktree_dir.audit_unlanded` — the proof that already existed — into `PROVABLY-STALE`,
`NEEDS-ADJUDICATION` (with the unlanded count), `CAPPED-NOT-PROVEN`, `HAS-GIT`, `UNREADABLE` and
`PROOF-UNAVAILABLE`. It is read-only, off by default, refused when combined with `--apply`, and every
verdict states what it means. Three properties are pinned by tests: the two verdicts that need no
instrument (empty, `.git`-bearing) are decided *before* the tool is consulted; a missing or broken
instrument makes every content-holding leftover `PROOF-UNAVAILABLE` with **no content claim**, because
a missing instrument must never read as a clean result; and asking what is disposable cannot remove
anything.

The durable part is not the flag. It is that the human queue is now only the items a machine cannot
settle — **23 now, and every one of them another tool's scratch under Temp, none of them repository
work.** The next survey of this repository will not regenerate a pile, because there is no pile.

### What "superseded" rests on, for the four just cleared

* **The three vocabulary worktrees.** `FamilyExpandGen --check` is **clean** at integration —
  *"11 generated file(s), 70 recorded refusal(s), and provenance manifest match"* — and
  `85d2c096f fix(seedsmith): close FamilyExpand manifest schema` moved the generator after they were
  cut. Their `FamilyExpandManifest.cs` is not a fork: it **lacks 15 significant lines** integration has,
  including the whole `SeedReaderKind = "affix"` mechanism, the `entries: []` empty-envelope fix, and the
  schema validation. Adopting it would undo the fix that makes `--check` green, and their generated
  manifest is output from a generator that no longer exists in that form.
* **`cmdc-bp-1`.** `ValidatedPiece.cs` is a layering refactor for BP1.11/BP1.12, which are landed and
  accepted; integration's `BuildPresetPieceRow` is the contract. The branch was an ancestor with 0
  unmerged commits, so nothing was lost.
* One of them hit the long path again and was reclaimed through the tool: **2,356 files proved landed**,
  14 adjudicated, 23 build-output subtrees, and the refusal first caught
  `gk-forge/tools/FamilyExpandGen/FamilyExpandManifest.cs` — which is why the manifest claim above is measured
  rather than assumed.

### One tool verdict the owner overrides

`retire_worktrees.py` reports `materialistic-spear` as **RETIRABLE** — no active owner, integrated,
clean. It is not retired, because the owner ruled the group C lanes theirs to handle. A tool verdict is
evidence, not authority: where a standing scope boundary and a clean bill of health disagree, the
boundary wins and the disagreement is written down rather than silently resolved.

### Where the set stands

**5 worktrees** (4 per the tool, excluding the main checkout), **7 branches**, **1 rescue ref**:

    main checkout            live shared work - two active sessions in flight
    ps1ban-l3 / l4           out of scope - owner-ruled, another agent's live work
    actor-hud, materialistic-spear   out of scope - owner-ruled group C
    main                     published merge record; 4 no-op merges, tree == its merge-base
    rescue/corpus-bcu211      SUPERSEDED and retained; the owner's to inspect
    codex/*                  never touched, owner-ruled

Every registered worktree and branch carries a named verdict backed by a re-runnable command. The one
recurrence risk — a cleanup phase that depends on someone remembering to run it and then hand-adjudicating
what the tools can prove — is now a flag that runs in seconds and reports only genuine items.

## Addendum AF — the tool's coverage shrank as the cleanup succeeded (2026-09-27)

The last item was the four empty directories left in `.claude/worktrees`, and getting to them exposed a
worse defect than the directories: **the tool had stopped looking.**

### What happened

`retire_worktrees.py` derives its candidate pool set from the parents of the **registered** worktrees.
That derivation is deliberate and correct — deriving it any other way once swept in 92 unrelated
directories including 28 whole sibling repositories (`lore-weave-*`, `Keepverse`, `wabbajack`,
`ComfyUI-GGUF`), which would have been listed as disposable litter. The tool's own comment says so.

But it means **coverage shrinks as the cleanup succeeds**. Once I cleared the last worktree out of
`.claude/worktrees`, that pool was no longer any registered worktree's parent, it dropped out of the
candidate set, and **the four husks it still held became invisible** to the tool whose entire job is to
find them. Measured both ways:

    31 leftovers  reported without the pool declared
    35 leftovers  reported with `--pool .claude/worktrees`

A cleanup tool that loses sight of a pool the moment the pool empties is not a tool that reports a
clean tree — it is a tool that reports a **clean tree**, and the objective's standing rule is that
"a count of zero is never reported unless it was measured." Here the count was neither zero nor
wrong-by-policy; it was a *silently narrowed scope* presented exactly like a full one.

**Fixed** with `--pool DIR` (`a8fd3a446`): a caller may declare a pool, a declared pool that does not
exist is refused by name (`POOL-NOT-A-DIRECTORY`) rather than skipped — skipping it would restore the
very blind spot the flag closes, since the caller would believe a pool was covered — and declaring the
repository root is refused (`POOL-IS-THE-ROOT`) for the over-scan reason. 67 tests green, and one of the
five new ones asserts **the blind spot itself**: the same husk is absent from the report without the
declaration and present with it, because a fix for "the tool cannot see this" is only proved by a test
that watches the tool fail to see it.

The rule, added to the manager SSOT as a sixth binding blind spot: **pass the repository's own pools on
every run; never rely on the derived set to still contain them.**

### The husks are HELD, and that is their terminal state

All four refuse with `HELD` — a live process holds a handle. Their plan is `WOULD-REMOVE` (0 files
walked, 0 unlanded) and the apply is refused, which is the correct pair of facts: the **content** is
provably disposable and the **delete** is blocked by the OS. A locked de-registered husk is reported,
never forced, so they stay. What the fix bought is that they are *visible* rather than absent.

### Two defects of my own on the way, both the recorded shape

1. An edit left four lines of docstring prose at module level plus a stray `"""`. Python reported the
   error **100 lines later**, inside a perfectly valid docstring — because that docstring's apostrophe
   in `` `porcelain`'s `` became a string opener once the real string had closed early. A `compile()`
   gate caught it before anything was committed, which is the discipline earning its keep; chasing the
   reported line would have meant chasing a symptom.
2. The wiring script ran twice and registered `--pool` **twice**. `compile()` accepts that — the file is
   valid — and only `argparse` sees it, at runtime, as `conflicting option string`. So the idempotence
   check now asserts the **count** of a registration rather than its presence. A check that passes is
   not a check that ran, and a count is the only thing that distinguishes "registered" from
   "registered twice".

### Where the set stands

**5 worktrees · 7 branches · 1 rescue ref**, every one classified, and **35 leftover directories** with
**12 machine-decidable** and **23** holding unlanded content — of which all 23 are other tools' scratch
under Temp, none of them repository work. The repository's own debt is the four HELD husks above, which
cannot be deleted by anything short of releasing the handle, and the six out-of-surface Temp
directories whose content is proven already integrated.

## Addendum AG — retracting "none of them is repository work", and the six that are not mine to delete (2026-09-27)

Addendum AF closed with: *"all 23 are other tools' scratch under Temp, **none repository work**."* **That
is false, and it was false in the exact way the standing rules name — location is not ownership.** The
claim rested on *where* the 23 directories sit, never on what is in them. Re-examined by content,
**16 of the 23 hold repository-shaped material**, and the conclusion I drew from it happened to survive
while the reason did not. A conclusion that is right for the wrong reason is the failure mode this
whole cleanup exists to catch, so the correction is recorded here rather than quietly replaced.

### What the content test actually finds

| kind | n | directories | verdict |
|---|--:|---|---|
| build output / game binaries | 2 | `actor-hud-unity-live-server-20260926` (2,568 repo-shaped paths, `FusionRpg.*.dll`/`.pdb`), `epl11-obj` (NuGet intermediates) | **disposable** — and "unlanded" is the *desired* state, since binaries are never committed |
| test fixtures at production paths | 2 | `openid-fixture` (9 one-to-seven-line C# stubs under `gk-core/src/FusionRpg.Core/**`), `statpairs-fixture` (a 19-line `gk-data/packs/fusion/data/seed/derived-stats/catalog.json` against integration's 773) | **disposable, and must never be landed** |
| tool / session scratch | 5 | `msbuild-probe`, `union-append-only-20260926`, `debug-mcp-backup-20260915`, `uareg`, `sess-f78e` (this session's own) | **disposable** |
| acceptance evidence | 1 | `resume-20-rsf27-acceptance-20260925` | **disposable — proven a duplicate** (below) |
| **runtime copies of the owner's live save** | 4 | `asroute-before`, `asroute-after`, `glyphs-data`, `glyphs-data-base` — each holds `rpg-hot.sqlite.<timestamp>.bak` | **OWNER DECISION** |
| **live-probe artefacts of a group-C lane** | 2 | `actor-hud-unity-live-20260926` (lawn PNGs with the HUD on), `actor-hud-proof-data-20260926` (browser proofs) | **OWNER DECISION** |
| unremarkable scratch | 7 | `deep-audit-notes`, `__pycache__`, `wt-probe`, `coldseed`, `ipc`, `probe1`, `probe-exit` | disposable |

So: **10 disposable, 6 for the owner, 7 unremarkable scratch.** The content proof decides none of the
middle column, because it answers "is this landed", not "is this mine to destroy".

### The acceptance artefact, which is the most protected category here

`resume-20-rsf27-acceptance-20260925/evidence.json` is an acceptance artefact, and the standing rule is
that acceptance evidence is not removed and an artefact naming an **unmerged** sha blocks even when the
branch is merged. Checked properly rather than assumed:

    lane        resume-20-rpg-sim-defeat-floor-review-20260925
    reviewedSha 4f78ed6c9ebe744c2b69232d325a67348161326f   -> ANCESTOR of integration
    baseSha     6d77888cca860805e5a11e617e201847e01c16b7   -> ANCESTOR of integration

Both merged, so it does not block. And it is **not the only copy**:
`.claude/cmdc-agents/acceptance/resume-20-rpg-sim-defeat-floor-review-20260925-4f78ed6c.json` is
tracked at integration and names the same `reviewedSha`, the same `baseSha`, and the same `command`. So
the temp copy is a duplicate of evidence that is already landed — the one category where being wrong
would have destroyed the only record, checked and found wanting.

### The six that need the owner, and why a content proof cannot decide them

Four directories hold **`rpg-hot.sqlite.<timestamp>.bak`** — copies of the running game database. That
is the owner's live save: not evidence owed to this repository, not regenerable by any generator, and
destroyed by deleting the only copy. A `NEEDS-ADJUDICATION` verdict on it is technically correct and
practically wrong, which is the clearest argument in this cleanup for why "unlanded" and "disposable" are
different questions. The other two are `actor-hud`'s live-probe artefacts — lawn screenshots and
browser proofs — and that lane is owner-ruled out of scope, so their being unlanded is the *purpose* of a
probe rather than a gap in it.

Nothing in either group is deleted or landed here. All six are outside the repository's own worktree
pools, so they are not this cleanup's surface in the first place; they are surfaced because
"12 leftover directories nobody claims" is not a true statement about this machine, and a manager
reading a count would act on it.

### The correction, stated as a rule

*Location is not ownership, and a filename is not a verdict.* A directory under a temp path holding a
tracked file's path, a `.sqlite` backup, or a lane's screenshots is repository work or owner property
**regardless of where it sits** — and the previous addendum's confidence came entirely from a `path`
field. The corrected form of the claim is: **none of the 23 is owed work for this repository, and six of
them are not this cleanup's to touch.** Both halves are content-derived, and the first half is now
supported by reading what each one holds rather than by where it lives.

## Addendum AH — the cleanup's own fence was 69% fiction, and the fix is a rule about fences (2026-09-27)

The last unmet clause of this walk's success criterion — *every finding is landed in the owning
program's ledger* — turns out to be blocked by a defect in **my own** session record, so it was
diagnosed from the inside rather than argued from outside.

### What the drift was actually made of

`session-boundary-check.py` reported `DRIFT (52)`. About **34** of those were this session against
`ps1-ban-manager-20260926`, and the reason was mine: **55 of 80 fenced paths had never been touched by
this session**, and five entries were globs swallowing whole trees. The narrow test I had been applying
all walk — *does this session hold `README.md`?* — was answered "yes", and the honest answer was "no,
it was never edited and never will be".

That is not tidiness. `git commit` publishes the whole index, another lane's **68 staged paths** sat in
the index for this entire session, and a fence claiming `README.md`, `Directory.Build.props` and
`gk-core/src/FusionRpg.Server/Program.cs` would have **sanctioned** publishing that lane's staged copies of
them under my commit message. The over-broad fence was the mechanism that turns "check the staged set
against your own paths" from a guard into a no-op.

Narrowed **80 → 11**: the two cleanup tools, their two test files, the walk record, the owning ledger,
the two rescued-evidence subtrees, this record, and the manager SKILL. `DRIFT (52) → 18`; this session
now accounts for **1**, the other 17 being `ice-shield-sprite-export` against ps1-ban.

### The evidence-fragments glob was wrong in a way worth keeping

`tasks/evidence-fragments/**` collides with **35 individual fragments** ps1-ban claims. The honest entry
is two named subtrees — `seedsmith-p1-audit-final-20260925/` and `resume-00a-fail-closed-recovery-20260925/`
— and neither is among them. A glob over a shared evidence directory is a claim on a directory that
belongs to whoever rescued something into it.

### Four ways to derive a fence from history, all of which lie

1. **Recency on the shared branch.** Every session commits to `features/mega-merge`, so `git log -40`
   attributes all of them to this one: 430 "owned" paths, **399** other lanes'.
2. **"A commit touched a fenced path."** Coincidence. `gk-core/scripts/verify-change.py` is mine;
   `scripts/session-boundary-check.py` is not; recency cannot tell them apart.
3. **A hand-listed SHA set.** Undercounted — it missed `BCU2.12-full-run.json` and `README.txt`, both
   rescued evidence, both committed in an earlier commit.
4. **Every SHA named in a document is not an authorship claim.** The walk report is a *catalogue* of
   the commits it describes; 80 of its 85 hex tokens resolve to real commits, and most are other
   lanes' — `f671cc5ad`, `AGENTS.md`, `.commandcode/**`.

A fence is a **forward** permission set: it answers what may be edited *next*, checked at commit time
against what is staged. History can only understate it, and the shortfall is exactly the rescued
evidence a later rescue must gate. The honest derivation is from the program's surface, validated by
the one check that can only over-collect — the commits touching **only** fenced paths (58 of 361), each
read before it counts. A pre-write assertion built on trap 4 **failed closed and printed all 347 gaps**
instead of a pass, and that failure is what identified the trap.

### The mutual claim, and which side I am on

`gk-core/scripts/verification-boundaries.v1.json` is claimed by both sessions. From the ps1-ban record's own
30-version history:

    this session's claim first appears   2026-09-26 16:18
    ps1-ban's claim first appears        2026-09-26 19:08   (at path-count 118, after a step from 39)
    this session first committed to it   2026-09-26 03:13   cca2200c6

**I did not cross.** The 538-path widening swept a file this session had been editing for sixteen hours
and had committed four times. The boundary checker reports DRIFT without ranking, so it cannot
distinguish an innocent session from one that widened over another's file — the **older claim is the
better claim**, and the correct response is to surface the junior side, not to drop the older one.

### CB8, second instance, with the mechanism

ps1-ban's fence is a growth curve rather than a fence:

    5 → 25 → 27 → 32 → 35 → 39 → 118 → 211 → 251 → 254 → … → 502 → 533   (committed)
    538                                                                  (uncommitted)

A whole-tree `.ps1` → `.py` port needs every file it ports, so its blast radius **is** the tree. The
step that mattered was 39 → 118, and it is what put two program ledgers (CB8) and a live registry file
out of reach. The owner decision is to cap it, or to require per-file claims renewed as the port
advances. The binding rule is now in `.agents/skills/project-manager/SKILL.md`.

## Addendum AI — one phantom item removed: a worktree that only pointed at a branch (2026-09-27)

Re-deriving the final tables rather than trusting them found a double-count in this walk's own
classification, in exactly the form the procedure warns about — a census grouped by
(file, worktree) instead of by content.

`main` was checked against its merge-base to settle why it reads as unintegrated: tree `7cb9a330c`
identical to its merge-base tree, 4 commits not in integration, **0 non-merge** commits. Four no-op
merges, zero content contribution. Correct, and worth stating precisely because "not an ancestor" is
the only fact `git branch` shows.

That prompted the obvious question about `.kilo/worktrees/materialistic-spear`, which this walk had
classified as group-C live work holding 4 unintegrated commits. It holds **none**:

    HEAD            52fec0bee  == main's tip
    branch          (detached - no branch of its own)
    status entries  0
    rev-list ... --not main   0 commits

So the four commits were `main`'s, seen through a worktree that happens to be checked out at `main`'s
tip. One piece of work, counted twice. The group-C ruling is untouched — the worktree is still
owner-ruled and still not touched — but the belief that it holds four commits in flight is not true,
and it matters: "group C still has work in flight" is a reason to keep a worktree, and there is
nothing in this one to keep.

The name of a worktree is not a verdict, and neither is a commit count inherited from a branch the
worktree merely points at. That is CB10's rule stated from the other side.

## Addendum AJ — the item that appeared mid-walk, and the verdict the prefix cannot give (2026-09-27)

The criterion is *"no registered worktree or branch remains unclassified"*, and a lane merging while
this walk is in progress breaks that condition the moment it happens. Between the two audits the
registered set went **5 worktrees / 7 branches -> 6 / 8**, and by the time it was measured properly it
was back to **5 / 8**. Two things in that churn are worth recording, because both are ways a cleanup
reports a wrong number.

**A worktree list read at two instants is not a list.** The first audit caught
`codex/actor-hud-merge-20260927` checked out; by the next command that lane had **merged its own branch
and removed its own worktree**, which is correct behaviour and not residue. A tool that sampled once and
reported 6 would have reported a phantom. A PowerShell extraction of `git worktree list --porcelain`
then returned **4** and dropped the main checkout entirely, which is the same failure one level
removed: the raw command answers 5, and the reader is what was wrong. **Re-derive a count from the
stated command before quoting it, and treat an extractor as a claim to check, not a reading to trust.**

**The new branch, classified by the same four questions and not by its prefix:**

    codex/actor-hud-merge-20260927   d4fc6887e   MERGED into integration   no worktree

- **Decisive.** `d4fc6887e` is an ancestor of `features/mega-merge`, so integration holds it; it is the
  very commit that carried the concurrent `update documents` merge that took 4 of this session's paths
  (CB15).
- **Reachability, not absence of a ref.** The branch is a real ref to a real merged commit, so it needs
  no rescue and no evidence.
- **Owner.** `codex/*` is owner-ruled ACTIVE, never touched. That ruling is unchanged by the branch
  having merged — it is a *disposition* rule about what I may do, not a prediction about the lane's
  state.

**Verdict: MERGED, owner-ruled, retained — not cleared, not merged by me, not deleted.** The owner ruling
outranks the cleanup, exactly as it did for `materialistic-spear`.

The set is therefore back to the same shape, honestly re-measured: **5 worktrees** (main checkout — live
shared work; `ps1ban/l3` and `l4` — owner-ruled live; `codex/actor-hud-bottom-anchor` — owner-ruled,
now merged; `materialistic-spear` — **EMPTY**, a clean detached checkout of `main`'s tip per CB12) and
**8 branches** (3 `codex/*` owner-ruled, the integration branch, `main` = one merge record, 2 `ps1ban/*`
owner-ruled, 1 rescue ref kept deliberately).

## Addendum AK — the set shrank because other lanes closed out, and one verdict genuinely changed (2026-09-27)

Between Addendum AJ and this one the registered set went **6 worktrees / 8 branches -> 4 / 5**. **This
cleanup removed nothing.** All three `codex/*` branches and the `actor-hud-bottom-anchor` worktree are
gone, and `ice-shield-sprite-export-20260927-41bc` is no longer an active record — other lanes closed
their own work out, which is the correct behaviour and is not residue. A cleanup that reported its own
count falling without asking why would be claiming credit for another lane's work, so the delta is
attributed here rather than absorbed into a total.

**One verdict genuinely changed, and it was the standing claim about the main checkout.** It was
classified all session as *"the largest single unlanded holder — 10 tracked changes, all claimed by an
active session."* It is now **clean (`dirty=0`)**: those changes were committed by the lanes that owned
them. The standing scope note said the main worktree "is itself the largest single unlanded holder and no
migration mechanism can catch it" — that is no longer true of the current tree, and it is worth recording
because a scope note that outlives its measurement is the same rot as a remembered number.

**The two gates that were blocking, re-measured rather than assumed:**

    ps1-ban-manager-20260926   status=active  paths=538  working-tree edit: none
    tasks/ps1-ban-todo.md        last written 2.4h ago
    tasks/passive-tree-todo.md   last written 18.0h ago

So the fence is still live and correctly blocks. What changed is that **both findings' code is now
fixed anyway** — the `Total|Passed` gate, the validator's wrong noun, and (this session) the tree-plan
vocabulary — because in all three cases the block was on the *ledger* while the *code* was free. What
remains genuinely owed to a fenced ledger is now only: the `NameRepair`-on-the-node-path design
decision, and the ledger rows recording the three fixes. That is a much smaller, and much more honest,
residue than "two unlanded findings".

**Re-derived, each from its stated command:**

    git worktree list                      4 worktrees, every one carrying a verdict
    git branch --format=...                5 branches,  every one carrying a verdict
    retire_worktrees.py --prove-stale      35 leftovers, 35 classified, 0 unclassified
                                            (23 NEEDS-ADJUDICATION, 12 PROVABLY-STALE)
    session-boundary-check.py              DRIFT 3, of which 0 name this session
                                            (52 at the start; this session's share 34 -> 0)

The three remaining DRIFT rows are all `ps1-ban-manager-20260926` against `resume-34-cai2-2-20260925`,
one of them being that record's branch not existing at all — the known zombie. Not mine to retire, and
not mine to fix.
