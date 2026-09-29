# Mega-merge program handoff — 2026-09-25

**Status:** **RESUMED / HANDOFF — fanout active, not a completion claim.**

- Evidence snapshot collected at `2026-09-25T10:45:21+07:00`.
- Integration branch at collection: `features/mega-merge`.
- Integration HEAD at collection: `cd4104c05582b4de04c538c2df0f9850728c4605`.
- The checkout was clean and 58 commits ahead of `origin/features/mega-merge` at collection.
- Work is local only. No push or pull request was made.
- The program goal was explicitly resumed by the owner after this snapshot. A bounded fanout is now active.
- BCU2.12 PassiveTree recovery remains paused; the resumed fanout does not authorize another generation run.

The detailed program goal is not restated here. This file is the resume contract: exact current state,
what is accepted, what is not accepted, which evidence is stale or partial, and the order in which to
finish without laundering an unproven claim into a green one.

## Manager charter retained for resume

- Manager session: `mega-merge-program-resume-20260925`
- Runtime: repository OpenCode CLI runner
- Allowed model: `opencode/space-bunny-free`
- Effort: `max`
- Input/output budget: uncapped
- Configured total lane ceiling: none
- Fallback: none
- Error rule: stop the affected lane on quota/context/provider failure; do not switch models
- Acceptance capacity remains the limiting factor: no lane is merged without exact-SHA review
- The owner charter remains `.claude/opencode-agents/allowed-models.json`; do not broaden it silently

## Executive truth

1. **Fourteen per-lane schema-v2 artifacts are GREEN and their merge commits are ancestors of the
   collection HEAD.** A fifteenth exact-SHA artifact, RS-F27 follow-up `4f78ed6c`, is GREEN and
   clean but is not yet merged. This proves the enumerated lane acceptances, not whole-program
   acceptance, and does not turn the partial `resume-15` browser report into feature acceptance.
2. **There is no terminal current-head merged-head verdict at `cd4104c05582b4de04c538c2df0f9850728c4605`.**
   The only merged-head report, `tasks/reports/mega-merge-post-merge-phase0-20260925.md`, is stale
   **BLOCKED** evidence for its own older SHA. It is not current-head evidence.
3. **Legal BepInEx and MelonLoader interop builds passed in the preflight.** That proves the two host
   projects can compile against the owner-supplied legal sources; it is not the merged-head gate and
   not live-game proof. Evidence: `tasks/reports/legal-interop-preflight-20260925.md`.
4. **Browser QA is partial; its sanitized report is integrated on the manager branch, not the dirty
   integration branch.** A real no-live-game recovery state was captured, but active-match recovery,
   HUD/occupant behavior, and cross-match isolation were not proved.
5. **The late RS-F27 tightening is independently accepted at exact SHA
   `4f78ed6c9ebe744c2b69232d325a67348161326f`, but is not merged yet.** The earlier RS-F27
   measurement remains accepted at `912e041d27774ac804ba8f418e9644dfd22b8c97`; this is a separate
   follow-up artifact.
6. **BCU2.12 remains incomplete at 361/904.** Its fail-closed launcher/report hardening is included in
   the accepted composite, but the corpus run is not complete, the generic `wither` tree gap remains,
   and no terminal Seedsmith verdict authorizes a resume.
7. **Release/topology, current-head legal live proof, and final ledger reconciliation have not run.**
   No current-head report matching release, topology, live, or current was present at collection.

## Current task-block reading

The reproducible TVB-F20 reading at the collection HEAD was:

```text
118 todo files
open=671
done=2885
unticked boxes=1884
shaded boxes=843
unmeasured=2
```

This is a task-block census, not an effort estimate and not proof that a tick is true. Checkbox counts
are explicitly not work units. The command was:

```powershell
python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks
```

## Current schema-v2 acceptance set

All rows below were re-read from `.claude/cmdc-agents/acceptance/`, had
`schemaVersion == 2`, had verdict `GREEN`, recorded `before: CLEAN` and `after: CLEAN`, and had their
recorded merge commit verified as an ancestor of the collection HEAD.

| Scope | Reviewed SHA | Merge commit |
|---|---|---|
| Fail-closed composite, verification mappings, Seedsmith hardening | `fc144f2cc4a67464d763051c428deed2937692ef` | `86911a360d14f25929ac88c6ef325331d3527ad8` |
| Release/verification topology | `011cd122b384a71417a082f2882074cabc435ffb` | `9bc8598ca2885485603636f659b5f0301d9f3c8f` |
| Split-Core verification mappings | `ff934d08baeaa9d8832e6fcbab00c1a4b50c0db1` | `06ea826d629d5862ad3926232f8682761e12d3c1` |
| Delve server-owned outcome | `03d8cee8d6943777e9333db106926f9295f8fe41` | `9a24e56c88e62f1e846889e8c98c77cbe4044b96` |
| Battle ActorHub/observer/HP range | `7b4e8ef582a0744e20f501562a4b28167e402c89` | `dd573e05b75bdacadcb1676a2b5c7ea61497bd1f` |
| Web authoritative recovery/isolation | `4ff99673b14dc919d654789b30c254f0d13efa77` | `c7d2cc93798f27189483d29e93591b3712f014eb` |
| Expedition durability | `ec4773b9c2b4a90d9dae9c69834d78ae8493c87e` | `244e8fb9fac0f6c00f9ca34dcf99582b59ed8359` |
| FamilyExpand vocabulary recovery | `85d2c096f829edf2560ee1f67a80aef97c40cb13` | `83febfacdc7dd205dcadd9030f7b996c74223d58` |
| PassiveTree binder/report parity | `1984dfcd185a26b7d2127c871b712e4f0f985e5f` | `3aa8d7656a70e159892f9ab17dec397a00f9d39f` |
| BattleEffects H1 re-pin | `78f4db6fd4d80dfd25feaad4b070bb2b955418bc` | `3036350b65316412bb6d54b49062996c8142293c` |
| TVB-F36 checked-heading classifier | `a3660c664d99c36cc33944df192ad6a2db8534ee` | `7ca9ee8b4ade30309117525e17f3c609d4ea33ff` |
| Persisted Delve steering | `41dd8af4fe6056e940ff5776ba7db81b38827c87` | `17cf1ef56abe7f5cd7946118d84c9105a4757cf6` |
| Build-preset BP1.11/BP1.12 | `005239e4b38dfe389a365b0c62e94fdca159238a` | `094ebc3aeb6882ce88b0c36d63a10edf448f4723` |
| RS-F27 legal-empty measurement | `912e041d27774ac804ba8f418e9644dfd22b8c97` | `ef009d9a154090a6affa31acb5b9f18a33baef54` |

The separate RS-F27 exact defeat-floor follow-up is accepted at
`4f78ed6c9ebe744c2b69232d325a67348161326f`; its merge commit is intentionally pending until the
cleanup boundary closes.

Older pre-schema acceptance JSON remains historical. It was not reclassified or counted as a current
schema-v2 record.

## Work that is not merged

### 1. RS-F27 real defeat-award floor — accepted, merge deferred

- Worker lane: `resume-20-rpg-sim-defeat-floor-20260925`; its no-commit rule was honored.
- Fresh manager review worktree: `.claude/worktrees/review-resume-20-rpg-sim-defeat-floor-20260925`.
- Reviewed SHA: `4f78ed6c9ebe744c2b69232d325a67348161326f`.
- Base SHA: `6d77888cca860805e5a11e617e201847e01c16b7`.
- Changed paths are exactly the test, the worker report, and the review session record.
- Manager verification: focused 20-sample test `1/1` passed; scoped verifier `281` E2E and `689` Guard
  tests passed; fabrication guard and citation audit passed; detached clean checkout was exact and
  clean.
- Acceptance artifact: `.claude/cmdc-agents/acceptance/resume-20-rpg-sim-defeat-floor-review-20260925-4f78ed6c.json`.
- The older dirty `resume-19` review draft was not adopted and remains untouched.
- The exact SHA is ready to merge only after the unrelated dirty integration session closes; the
  merged-head gate must then be rerun. The earlier `912e041d27774ac804ba8f418e9644dfd22b8c97`
  acceptance remains historical and was not amended.

### 2. Browser QA — integrated partial report, active proof still open

- Sanitized report: `tasks/reports/resume-15-web-browser-qa-20260925.md`.
- Source report SHA-256: `0EA1C2C079F4D4BB6971479FD57151E66BFAABF88524E57F96FC306C72B80483`.
- Integrated report SHA-256: `5CDDA3AF5CD5011D94DB831A324E3B96C92AA93CB4661C9A44AA45BE4DA7F527`.
- Result: **PARTIAL**. The no-live-game recovery state is proven; active-match recovery,
  HUD/occupant behavior, persistence read-back, and cross-match isolation remain open.
- Raw `.playwright-cli` evidence remains external to the tracked report; the report does not claim
  that a hash preserves those raw files.
- The QA worker is no longer alive. Its `partial` report is the evidence; the status label alone is not.

### 3. Manager worktree residue

The manager worktree `.claude/worktrees/program-resume-manager-20260925` was at `ac3bec1ce` with no
tracked modifications and these untracked files:

- `.claude/opencode-agents/briefs/resume-16-delve-persisted-steering-acceptance-20260925.md`
- `.claude/opencode-agents/briefs/resume-17-build-preset-acceptance-20260925.md`
- `.claude/opencode-agents/briefs/resume-18-rpg-simulator-rsf27-acceptance-20260925.md`
- `.claude/opencode-agents/briefs/resume-19-rpg-simulator-defeat-floor-20260925.md`
- the `resume-19` session record is not tracked on the integration branch

Do not discard or stash these files. Reconcile them explicitly after this report lands. The accepted
feature SHAs do not depend on the briefs being retroactively committed, but the session/topology
records must tell the truth when the program resumes.

## BCU2.12 paused state

The Seedsmith launcher/report hardening, serial worker, checkpoint/resume, collision-ledger,
hard-gate propagation, and report-completeness changes are included in accepted composite
`fc144f2cc4a67464d763051c428deed2937692ef`. The abandoned source worktree remains dirty because it is
the provenance checkout; its code/test files match the accepted main-tree versions. Do not merge that
source worktree again. The manager reconciliation record
`tasks/reports/seedsmith-p1-audit-final-review-reconciliation-20260925.md` explains why the
worker's `abandoned` session status and the accepted composite artifact are consistent.

The captured run is still incomplete:

- progress reading: `361/904`;
- current generic `wither` tree is one node short of its 40-node plan and lacks
  `skill.wither-def-t9-n1`;
- disk reconciliation for the current 352 node/species files remains `NOT_MEASURED` in the captured
  evidence bundle;
- the run must stop non-zero on the first reproduced hard-gate failure and must never be described as
  a completed corpus from the partial evidence.

Tracked evidence hashes recorded by `tasks/reports/seedsmith-p1-audit-final-20260925.md`:

```text
BCU2.12-run.log=8D92344AD00DE386EDABC571366D224E94BFE0C746CBB68D8902AAA9DBC3096F
BCU2.12-run.err=E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855
tree-language.ledger.json=4F1D40CE071905AE10E855FD53EAFFB958AC17B1CEEBF0123FE787D918A2F13E
```

The full raw evidence bundle remains in
`.claude/worktrees/opencode-seedsmith-p1-audit-final-20260925/tasks/evidence-fragments/seedsmith-p1-audit-final-20260925/`.
It is not integrated at the collection HEAD. Preserve that worktree until an explicit retention or
archive decision is recorded.

BCU2.12 remains paused until all of the following are true:

1. the stable integration head has a terminal `GREEN` merged-head verdict;
2. the accepted audit hardening remains ancestry-visible at that head;
3. the separate generator-led `wither`/J13 repair is resolved through its owning program;
4. the owner/program manager explicitly authorizes a monitored resume;
5. the resumed launcher keeps `WORKERS = 1`, fail-closed checkpoints, and the data-owned unresolved gate.

Any pause, deferral, or later resume decision needs a tracked record with the owner/authority, date,
scope, receiving owner, preserved blocker, and exact re-entry condition. Handoff prose alone is not a
durable deferral.

## Open decisions and named follow-ups

| Item | Current state | Receiving owner |
|---|---|---|
| PassiveTree `P11.1r` primary `stat.modify` route | **BLOCKED** on an owner/design choice: name a primary carrier/delegate or define a lossless primary-to-derived contract. Merely widening the derived predicate is forbidden. See `tasks/reports/resume-12-passive-tree-p11-1r-20260925.md`. | PassiveTree owner |
| `BCU2-R1` onboarding-rift contradiction | Header says all boxes are closed while task headings still say `OPEN`. The authoritative declaration must be chosen before implementation resumes. See `tasks/backlog-clean-up-todo.md`. | Owner/backlog reconciliation |
| `CAI2.2` replay-profile pin | Still unimplemented and deferred. The inventory calls the Data/Server seam dependency-ready, and the current main records show no exact active overlap, but this paused manager has not re-dispatched it after the Delve steering merge. Reconfirm path ownership and keep CAI3.5/`RpgHub.Resume` outside the slice. | Combat-AI owner |
| BCU2.12 generic `wither` / J13 repair | The generic tree is one node short and the captured run is incomplete. This is generator-led work, not a hand edit and not part of the accepted launcher/report hardening. | Seedsmith/PassiveTree generator owner |
| Build-preset boot schema hook | First-use ensure is idempotent and reopen-tested; a boot-time `RpgStore.cs` registration hook remains a separate follow-up. | Build-preset/Data owner |
| Shared human-empire helper | BP1.12's local helper should be replaced when SE4.37's shared helper lands. | SE4.37 owner |
| Browser deep-link/favicon observations | A first-open `#/lawn` deep link returned to Sanctum, and the initial favicon request was 404. These are observations, not classified defects. | Web owner |
| CAI3.5 / `RpgHub.Resume` | Explicitly outside persisted steering and RS-F27. | Combat-AI owner |
| Unowned `.commandcode` dirty paths | Owner selected **review as tracked configuration** on 2026-09-25. `resume-30` is reviewing a hashed evidence bundle; the actual paths remain untouched and unmerged. See `tasks/reports/worktree-cleanup-unowned-config-paths-20260925.md`. | Tooling/configuration owner |

No unchecked-box count above is a unit of work. The TVB-F20 task-block reading remains the only
mechanical census used here.

## Runtime resources observed

- Live-slot status at collection: slot 1 `ready` and unclaimed, slots 2–3 free, no slot game process.
  This is an ephemeral reading; rerun `scripts/live-slot.ps1 -Status` before acquiring.
- Supply `FUSIONRPG_GAME_POOL` and `FUSIONRPG_GAME_SOURCE` from the runtime environment. Never put
  their values in a committed file.
- Browser QA cleaned its own server/browser processes and did not leave port `5088` occupied.
- The legal BepInEx and MelonLoader source folders remain runtime environment values only.
- `FUSIONRPG_GAME_PROFILE=pvzrh-3.9` is required for the MelonLoader 3.9 interop build.

## Resumed fanout currently running

The owner explicitly resumed the program after the collection snapshot. The manager dispatched an
initial eight-lane triage/preparation wave from integration HEAD
`6d77888cca860805e5a11e617e201847e01c16b7`, then dispatched the bounded EPL1.1 implementation lane
after its dependency report. All use `opencode/space-bunny-free#max`, uncapped budget (`--budget 0`),
and no fallback:

| Lane | Kind | Scope |
|---|---|---|
| `resume-20-rpg-sim-defeat-floor-20260925` | implementation | RS-F27 real `player:defeat` floor, exact focused test/report |
| `resume-21b-effect-pipeline-triage-20260925` | read-only triage | next bounded effect-pipeline row; worktree-local recovery |
| `resume-22-deployment-hierarchy-triage-20260925` | read-only triage | next bounded deployment-hierarchy row |
| `resume-23-notification-ssot-triage-20260925` | read-only triage | buildable vs owner/live-gated notification rows |
| `resume-24-party-dungeon-triage-20260925` | read-only triage | next party-dungeon row outside CAI3.5 |
| `resume-25-strain-splice-triage-20260925` | read-only triage | next deterministic strain-splice slice |
| `resume-26-gate-release-prep-20260925` | read-only prep | merged-head gate and player-packaging evidence contract |
| `resume-27b-browser-live-prep-20260925` | read-only prep | real connected-injector/browser proof checklist; worktree-local recovery |
| `resume-28-effect-pipeline-epl1-1-20260925` | failed setup | abandoned before implementation; no product verdict |
| `resume-28b-effect-pipeline-epl1-1-20260925` | infrastructure-failed implementation | four dirty EPL1.1 files await manager harvest; Bitdefender blocked an unrelated verifier output |
| `resume-29-strain-splice-reader-guard-20260925` | manager-owned implementation | SSH7.1 current-revision guard/readers with SSH8.4 named companion; no publish/live scope |
| `resume-30-commandcode-config-review-20260925` | read-only review | owner-selected tracked-config review of the three unowned `.commandcode` paths; no source edits |

These lanes are allowed to work in isolated worktrees while the main checkout is dirty in the
unrelated active `worktree-cleanup-20260925` session and three unowned `.commandcode` paths. No lane
may merge into the main checkout until the cleanup session closes, the `.commandcode` ownership
question is resolved, the exact-SHA acceptance is recorded, and the current-head gate can run. The
fanout is deliberately wide on **triage and preparation**, not blind implementation: a larger merge
backlog without acceptance capacity is not throughput. Current dispatch capacity is full: one
active implementation lane (`resume-29`), one read-only config review (`resume-30`), and the
manager harvest/acceptance slot for the dirty `resume-28b` EPL1.1 files; no additional
implementation lane may be opened until one slot is resolved.

The original `resume-21-effect-pipeline-triage-20260925` and
`resume-27-browser-live-prep-20260925` workers stopped before producing reports after
`external_directory` permission denials: they attempted reads outside their own worktrees. Their
records are explicitly `abandoned`; the `21b` and `27b` rows above are the corrected,
worktree-local replacements. These are infrastructure events, not product verdicts.

`resume-23-notification-ssot-triage-20260925` returned `done` with a read-only dependency
report. The manager independently reproduced its `5` open / `63` done task-block reading and the
missing notification surface/world-route checks, then integrated the report. No NS6.11 or NS5.13
implementation is authorized until its named gui-lego, world-continuity, authored-scenario, and
real-live gates are satisfied.

`resume-24-party-dungeon-triage-20260925` returned `done` with a read-only dependency report. The
manager preserved its D3.31 generator-owner routing and the NR2.20 → NR2.21 → NR2.24 live-path
prerequisites. D4.32/D4.14 remain behind the route-placement/live dependencies, and D4.13 remains a
later Phase-5 coverage gate. No party-dungeon implementation was opened.

`resume-22-deployment-hierarchy-triage-20260925` returned `done` with a read-only dependency report.
The manager confirmed the `10` open / `0` done deployment-hierarchy reading and the missing
production settlement, wound, field-repair, and battle-wear seams. No DH-P0 or DH1.1 lane was
opened; the shared settlement/carry contract must first be named across deployment-hierarchy,
party-dungeon, and combat-ai/CAI3.5. H1/H2/H7 handling and the DH1.1 scope conflict remain explicit.

`resume-25-strain-splice-triage-20260925` returned `done` with a read-only dependency report. The
manager confirmed the `9` open / `69` done task-block reading and retained SSH7.1 as the next
revision-literal guard slice, with SSH8.4 only as its named same-file companion. The protected
verification-boundary guard path is now explicitly manager-owned, and `resume-29` is implementing
that exact reader/guard fence. It does not publish tuning, regenerate data, or start live work.

`resume-21b-effect-pipeline-triage-20260925` returned `done` with a read-only dependency report. The
manager confirmed the `6` open / `0` done effect-pipeline reading and selected EPL1.1 as the first
fenced implementation row. Its four-file registry/mirror/test fence is ready; EPL1.3's owner charter
and EPL2.1's channel-SSOT ruling remain later gates.

`resume-28-effect-pipeline-epl1-1-20260925` failed before implementation because its worktree
lacked the manager-owned session record. It changed no files, produced no report or verification,
and is explicitly classified as an infrastructure/lane-setup failure. The corrected
`resume-28b-effect-pipeline-epl1-1-20260925` replacement ran with a worktree-local boundary and
produced four dirty EPL1.1 files, but its broad verifier was stopped by a Bitdefender deny-write
lock on an unrelated `EffectGrantSessionTests` output. The worker is therefore closed as
infrastructure-failed; the manager must review and harvest those four files independently. No
replacement lane merges until its exact SHA is independently reviewed.

`resume-29-strain-splice-reader-guard-20260925` is now the active manager-owned implementation lane
for SSH7.1 with SSH8.4 as its named companion. Its exact fence covers the protected revision-literal
Guard test, the Python literal scan, and the currently shipped strain/materials test readers. It
must stop at the reader contract; SSH7.7, H7, SSH4.9, generated data, and live proof remain out of
scope.

`resume-30-commandcode-config-review-20260925` is the owner-directed read-only review of the three
unowned `.commandcode` paths. It reads a hashed evidence bundle and writes only a report; it cannot
edit the source paths, ignore rules, cleanup tools, or integration checkout.

`resume-27b-browser-live-prep-20260925` returned `partial` with a worktree-local proof checklist.
The manager integrated it as preparation only. It starts no game/server/browser/slot process and
proves no active-match recovery, normal-path persistence, or cross-match isolation; those gates
remain blocked until a real connected-injector run.

`resume-26-gate-release-prep-20260925` returned `partial` after producing a read-only readiness
contract. The manager integrated that report and its review record; it ran no full gate and proves
no current-head `GREEN` verdict. Its session record is therefore closed as `abandoned` with the
report retained, rather than being presented as a merged implementation.

## Current blockers after resume

1. **Main checkout is dirty:** `worktree-cleanup-20260925` owns six cleanup-tool paths, while three
   `.commandcode` paths are unowned by any session fence. The ownership finding is recorded in
   `tasks/reports/worktree-cleanup-unowned-config-paths-20260925.md`. Both sets block the merged-head
   gate and every merge; neither may be reset, stashed, cleaned, or deleted by the manager.
2. **No current-head gate verdict exists.** The legal BepInEx/MelonLoader preflight passed, but it is
   not the gate.
3. **RS-F27 follow-up exact SHA `4f78ed6c9ebe744c2b69232d325a67348161326f` is accepted but not merged.**
   The dirty integration cleanup session and unowned `.commandcode` paths still block the merge and
   the post-merge gate.
4. **Active-match browser/live proof needs a real connected injector.** No debug-created match will be
   accepted as a substitute.
5. **P11.1r needs an owner/design decision** on a primary carrier/delegate or a lossless
   primary-to-derived contract.
6. **BCU2.12 remains paused** at 361/904 pending a terminal GREEN head, the generator-led
   `wither`/J13 repair, and explicit resume authorization.
7. **CAI3.5/`RpgHub.Resume` and CAI2.2 remain deferred** until their named Data/Server ownership and
   Delve path dependencies are reconciled.

## Exact resume order

### 0. Preserve the resumed boundary

The owner has explicitly resumed the program and the eight-lane triage/preparation fanout above is
already running. Do not start BCU2.12, run a live game, or merge any lane into the dirty integration
checkout merely because the fanout exists. The cleanup session and the current-head gate remain the
merge boundary. The three unowned `.commandcode` paths are a separate owner-routing blocker; the
manager will not clean them to make the gate pass.

### 1. Reconcile manager topology first

From both the integration checkout and manager worktree:

```powershell
git status --short --branch
git worktree list --porcelain
python scripts/session-boundary-check.py --session mega-merge-program-resume-20260925
```

Preserve the untracked manager files listed above. Land this report as one manager commit, merge that
exact commit into `features/mega-merge`, then fast-forward the manager branch to the resulting
integration head. Confirm the handoff commit is an ancestor before editing the manager worktree; do
not use a stash/reset cycle to reconcile it.

### 2. Merge the accepted RS-F27 follow-up after cleanup

The worker was harvested into the fresh review branch and the exact SHA is accepted:

```text
4f78ed6c9ebe744c2b69232d325a67348161326f
```

The old `resume-19` dirty review draft is not the acceptance source. Once the main checkout is clean,
merge this exact reviewed SHA, then verify:

```powershell
git merge --no-ff 4f78ed6c9ebe744c2b69232d325a67348161326f
git status --porcelain=v1 --untracked-files=all
git diff --check
```

The merge must preserve the accepted `resume-13` report and its historical artifact. The manager
acceptance report and schema-v2 artifact are evidence-only descendants and must not change the
reviewed code SHA. After the merge, rerun the current-head post-merge gate; this lane acceptance
does not substitute for it.

### 3. Keep the integrated browser report partial

The sanitized browser report and its hash-chain record are already integrated on the manager branch.
Do not upgrade its claims. A real connected-injector run must still prove active-match recovery,
normal-path persistence, and cross-match isolation before the browser/live gate can be called green.

### 4. Reconcile records and ledgers

- Re-run the session-boundary check scoped to the manager and each edited session.
- Confirm every schema-v2 artifact named in this handoff remains GREEN, clean, exact-SHA, and merged.
- Confirm the manager worktree has no unexplained untracked evidence.
- Re-run the TVB-F20 census and compare it with this report; do not reuse the collection numbers if
  the head changed.
- Update `tasks/reports/mega-merge-program-resume-20260925.md` with the new exact integration head.

### 5. Run the terminal current-head merged-head gate

The gate requires a clean checkout on `features/mega-merge`. Supply the legal sources only through the
process environment:

```powershell
$env:FUSIONRPG_GAME_DIR = '<owner-supplied BepInEx source with BepInEx/core and BepInEx/interop>'
$env:FUSIONRPG_ML_GAMEDIR = '<owner-supplied MelonLoader 3.9 source>'
$env:FUSIONRPG_GAME_PROFILE = 'pvzrh-3.9'

.\.claude\cmdc-agents\scripts\post_merge_check.py
```

Do not use `-SkipBuild` or `-SkipGuards`; either makes the terminal verdict BLOCKED. Record:

- `$gatedHead = git rev-parse HEAD` and the branch before the run;
- the post-run HEAD, which must equal `$gatedHead`; the script also asserts this before and after
  every phase;
- exact command and environment-variable names, but not machine values;
- complete build/Guard/declared-test results;
- terminal verdict exactly as `GREEN`, `RED`, or `BLOCKED`;
- external log path/hash and a tracked report.

A tracked gate report is necessarily written after the run. Commit every gate/browser/live/topology
report on the manager branch, merge those evidence commits into `features/mega-merge`, and capture
`finalHead` only from that clean integration branch. The final handoff bundle is the tracked report
plus the terminal/merge transcript: the report holds `gatedHead` and the pre-merge evidence commit
list, while the transcript holds the self-referential final integration SHA. The handoff file cannot
honestly embed the SHA of the commit that contains itself.

Before the evidence merges, write an external JSON commit-to-path manifest with one object per
planned commit (`{"commit":"<sha>","paths":[...]}`) and hash that manifest. After the final merge,
generate the actual manifest from `git rev-list`/`git diff-tree`, compare commit IDs and each
commit's exact path set, and retain both manifest hashes. Prove the evidence-only descendant
mechanically:

```powershell
$expectedEvidenceManifest = '<external JSON commit-to-path manifest>'
$finalHead = (git rev-parse HEAD).Trim()
git merge-base --is-ancestor $gatedHead $finalHead
if ($LASTEXITCODE -ne 0) { throw 'gatedHead is not an ancestor of finalHead' }

function Test-EvidencePath([string]$Path) {
  return $Path.StartsWith('tasks/reports/') -or
         $Path.StartsWith('tasks/sessions/') -or
         $Path.StartsWith('.claude/opencode-agents/briefs/') -or
         $Path.StartsWith('.claude/cmdc-agents/acceptance/')
}
$changed = @(git diff --name-only "$gatedHead..$finalHead")
$violations = @($changed | Where-Object { -not (Test-EvidencePath $_) })
if ($violations.Count -gt 0) { throw ('non-evidence paths changed after gate: ' + ($violations -join ', ')) }

$expectedManifest = Get-Content -LiteralPath $expectedEvidenceManifest -Raw | ConvertFrom-Json
$actualManifest = @()
$commits = @(git rev-list --reverse "$gatedHead..$finalHead")
foreach ($commit in $commits) {
  $paths = @(git diff-tree --no-commit-id --name-only -r -m --first-parent $commit)
  $bad = @($paths | Where-Object { -not (Test-EvidencePath $_) })
  if ($bad.Count -gt 0) { throw ("non-evidence path in $commit`: " + ($bad -join ', ')) }
  $actualManifest += [pscustomobject]@{ commit = $commit; paths = @($paths | Sort-Object -Unique) }
}
$expectedByCommit = @{}
foreach ($entry in @($expectedManifest.commits)) { $expectedByCommit[[string]$entry.commit] = @($entry.paths | Sort-Object -Unique) }
$actualByCommit = @{}
foreach ($entry in $actualManifest) { $actualByCommit[[string]$entry.commit] = @($entry.paths | Sort-Object -Unique) }
$commitDelta = @(Compare-Object -ReferenceObject @($expectedByCommit.Keys | Sort-Object) -DifferenceObject @($actualByCommit.Keys | Sort-Object))
if ($commitDelta.Count -gt 0) { throw ('evidence commit set differs from expected manifest: ' + ($commitDelta | Out-String)) }
foreach ($commit in $actualByCommit.Keys) {
  $pathDelta = @(Compare-Object -ReferenceObject $expectedByCommit[$commit] -DifferenceObject $actualByCommit[$commit])
  if ($pathDelta.Count -gt 0) { throw ("evidence paths differ for $commit`: " + ($pathDelta | Out-String)) }
}
if ((git branch --show-current).Trim() -ne 'features/mega-merge') { throw 'final evidence proof is not on features/mega-merge' }
if (@(git status --porcelain=v1 --untracked-files=all).Count -gt 0) { throw 'final integration checkout is dirty' }
```

Hash and retain the gate report plus every external log. If any product, infrastructure, workflow,
registry, generated-data, or other non-evidence path changed, rerun the gate on the new
product/infrastructure head.

`RED` and `BLOCKED` are both failure for program progression. Neither authorizes a broad retry,
BCU2.12 resume, or a live claim.

### 6. Only after a current-head GREEN

Before executing this section, load the repository `live-qa`, `live-lawn-quick-start`,
`live-probe-mcp`, and `playwright-cli` skills. They own the detailed real-game and browser command
sequence; this handoff owns the slot, server, evidence, and cleanup boundaries.

1. Re-run the full local aggregate immediately before the live boundary and retain its output:

   ```powershell
   $testedHead = (git rev-parse HEAD).Trim()
   if ((git branch --show-current).Trim() -ne 'features/mega-merge') { throw 'full test ran off features/mega-merge' }
   if (@(git status --porcelain=v1 --untracked-files=all).Count -gt 0) { throw 'full test started from a dirty checkout' }
   $fullLog = Join-Path $env:TEMP ('fusionrpg-full-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.log')
   pwsh -NoProfile -File .\scripts\test-fast.ps1 -AllDefault 2>&1 | Tee-Object -FilePath $fullLog
   if ($LASTEXITCODE -ne 0) { throw "full aggregate exited $LASTEXITCODE" }
   if ((git rev-parse HEAD).Trim() -ne $testedHead) { throw 'full test changed HEAD' }
   Get-FileHash -Algorithm SHA256 -LiteralPath $fullLog
   ```

2. Claim and validate a slot explicitly; all slots held means wait. Keep acquisition inside the
   cleanup boundary so a post-acquire setup failure cannot leak the slot:

   ```powershell
   $session = 'mega-merge-program-resume-20260925'
   $slotAcquired = $false
   $slot = $null
   $slotPort = $null
   $slotInstall = $null
   $probeError = $null
   $cleanupErrors = @()
   try {
     .\scripts\live-slot.ps1 -Status
     .\scripts\live-slot.ps1 -Acquire -Session $session
     $slotAcquired = $true
     .\scripts\live-slot.ps1 -Status
     $slot = <slot-number-from-the-acquired-status>
     $slotPort = <registry-port-from-the-acquired-status>
     $slotInstall = (Resolve-Path '<runtime install from acquired status>').Path
     $serverUrl = "http://127.0.0.1:$slotPort"
     if ($slotPort -eq 5088) { throw 'slot resolved to the owner port' }

     $env:FUSIONRPG_ML_GAMEDIR = $slotInstall
     $env:FUSIONRPG_GAME_PROFILE = 'pvzrh-3.9'
     $deployedHead = (git rev-parse HEAD).Trim()
     if ($deployedHead -ne $testedHead) { throw 'live deploy HEAD differs from testedHead' }
     if ((git branch --show-current).Trim() -ne 'features/mega-merge') { throw 'live deploy is off features/mega-merge' }
     if (@(git status --porcelain=v1 --untracked-files=all).Count -gt 0) { throw 'live deploy started from a dirty checkout' }

     .\scripts\lane-server.ps1 -Start -Slot $slot
     .\scripts\lane-server.ps1 -Status
     .\scripts\deploy-play.ps1 -LoaderHost MelonLoader -NoServer -ServerUrl $serverUrl -Session $session
     if ((git rev-parse HEAD).Trim() -ne $deployedHead) { throw 'live deploy changed HEAD' }

     $health = $null
     $deadline = (Get-Date).AddSeconds(120)
     do {
       try { $health = Invoke-RestMethod -Uri "$serverUrl/health" -TimeoutSec 3 } catch { $health = $null }
       if ($health -and $health.ok -and $health.injectorConnected) { break }
       Start-Sleep -Seconds 2
     } while ((Get-Date) -lt $deadline)
     if (-not ($health -and $health.ok -and $health.injectorConnected)) { throw 'slot injector did not become healthy' }

     playwright-cli open "$serverUrl/#/sanctum"
     playwright-cli goto "$serverUrl/#/lawn"
     playwright-cli snapshot
     playwright-cli screenshot
   }
   catch { $probeError = $_ }
   finally {
     if ($slotInstall) {
       try { playwright-cli close } catch { $cleanupErrors += "browser close: $($_.Exception.Message)" }
       try {
         $prefix = [IO.Path]::GetFullPath($slotInstall).TrimEnd('\', '/') + '\'
         Get-Process -Name 'PlantsVsZombiesRH' -ErrorAction SilentlyContinue |
           Where-Object { $_.Path -and $_.Path.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) } |
           Stop-Process -Force
       } catch { $cleanupErrors += "game cleanup: $($_.Exception.Message)" }
     }
     if ($slot) { try { .\scripts\lane-server.ps1 -Stop -Slot $slot } catch { $cleanupErrors += "server stop: $($_.Exception.Message)" } }
     if ($slotAcquired) { try { .\scripts\live-slot.ps1 -Release -Session $session } catch { $cleanupErrors += "slot release: $($_.Exception.Message)" } }
     try { .\scripts\live-slot.ps1 -Status } catch { $cleanupErrors += "slot status: $($_.Exception.Message)" }
   }
   if ($slotPort) {
     if (@(Get-NetTCPConnection -LocalPort $slotPort -State Listen -ErrorAction SilentlyContinue).Count -gt 0) { $cleanupErrors += "slot port $slotPort still has a listener" }
   }
   if ($probeError) { throw $probeError }
   if ($cleanupErrors.Count -gt 0) { throw ($cleanupErrors -join '; ') }
   ```

   Use the loaded skills to enter a real match through the real game flow, query the actual lawn
   state, and record server persistence read-back separately from engine observation. Then start a
   second real match and prove the first match remains the browser scope. Do not use a debug-created
   active match, `window.__fusionRpgAppendLogEvent`, or an injector-only response as this proof.
   Record `testedHead`, `deployedHead`, slot number/port/install, full-test log hash, live engine
   read-back, browser snapshots/screenshots, and cleanup results in
   `tasks/reports/mega-merge-live-browser-current-20260925.md` after adding that path to the manager
   session fence.

### 7. Release, topology, and final reconciliation

After deterministic, browser, and live evidence are green, add the exact report paths below to the
manager session fence before writing them.

**Player packaging:**

```powershell
$packagedHead = (git rev-parse HEAD).Trim()
if ((git branch --show-current).Trim() -ne 'features/mega-merge') { throw 'packaging ran off features/mega-merge' }
if (@(git status --porcelain=v1 --untracked-files=all).Count -gt 0) { throw 'packaging started from a dirty checkout' }
$env:FUSIONRPG_GAME_DIR = '<owner-supplied BepInEx source>'
$env:FUSIONRPG_ML_GAMEDIR = '<owner-supplied MelonLoader 3.9 source>'
$env:FUSIONRPG_GAME_PROFILE = 'pvzrh-3.9'
$env:FUSIONRPG_VERSION = '<candidate-version>'

.\scripts\publish-player.ps1
.\scripts\smoke-player-pack.ps1
if ((git rev-parse HEAD).Trim() -ne $packagedHead) { throw 'packaging changed HEAD' }
Get-FileHash -Algorithm SHA256 -LiteralPath 'artifacts/player-pack-smoke.json'

$pack = (Resolve-Path 'dist/FusionRpg').Path
$packManifest = Get-ChildItem -LiteralPath $pack -File -Recurse | ForEach-Object {
  $relative = [IO.Path]::GetRelativePath($pack, $_.FullName).Replace('\', '/')
  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash
  "$relative`t$hash"
} | Sort-Object
$packManifest | Set-Content -LiteralPath 'artifacts/player-pack-manifest.txt'
Get-FileHash -Algorithm SHA256 -LiteralPath 'artifacts/player-pack-manifest.txt'
```

Record `testedHead`, `deployedHead`, and `packagedHead` (they must be the same product/infrastructure
head unless a new gate was run), the commands, version, package layout, smoke JSON hash, sorted
relative-path package-manifest hash, full-test log hash, and external logs in
`tasks/reports/mega-merge-release-current-20260925.md`. Never commit `dist/` or `artifacts/`.

**Topology and program reconciliation:**

```powershell
python scripts/session-boundary-check.py --session mega-merge-program-resume-20260925
python .claude/cmdc-agents/scripts/lane-signals.py
python gk-core/scripts/audit-program-pipeline.py
git status --short --branch
```

Record exact output in `tasks/reports/mega-merge-topology-current-20260925.md`; update owning todos
with exact SHAs and verdicts. If BCU2.12 remains paused, add `tasks/reports/BCU2.12-owner-deferral-20260925.md` to the manager
session fence and record authority/date/scope/receiving owner/blocker/re-entry condition there before
finalization. Then update the
final handoff with `gatedHead`, the pending evidence commit list, the evidence-only descendant proof,
and every still-open owner decision. Commit the release/topology/final-handoff evidence on the
manager branch, merge those exact evidence commits into `features/mega-merge`, and capture `finalHead`
only after the integration checkout is clean. If release/topology or the BCU2.12 disposition changed
a non-evidence path, rerun the merged-head gate before the final integration merge. After that final
merge, run the following once and retain the output and its SHA-256 in the external transcript:

```powershell
$finalHead = (git rev-parse HEAD).Trim()
$finalBranch = (git branch --show-current).Trim()
$finalStatus = @(git status --porcelain=v1 --untracked-files=all)
if ($finalBranch -ne 'features/mega-merge') { throw "final branch is $finalBranch" }
if ($finalStatus.Count -gt 0) { throw 'final integration checkout is dirty' }
"finalHead=$finalHead"
"finalBranch=$finalBranch"
"gatedHead=$gatedHead"
Get-FileHash -Algorithm SHA256 -LiteralPath $expectedEvidenceManifest
```

The transcript is the durable carrier for the self-referential final SHA; the tracked handoff carries
the gate head, planned evidence commits, expected manifest hash, and unresolved decisions.

## Evidence index

- Manager control/handoff: `tasks/reports/mega-merge-program-resume-20260925.md`
- Program inventory: `tasks/reports/resume-06-program-inventory-20260925.md`
- Composite acceptance: `tasks/reports/resume-00-composite-acceptance-20260925.md`
- Stale merged-head attempt: `tasks/reports/mega-merge-post-merge-phase0-20260925.md`
- Legal interop preflight: `tasks/reports/legal-interop-preflight-20260925.md`
- Persisted steering acceptance: `tasks/reports/resume-16-delve-persisted-steering-acceptance-20260925.md`
- Build-preset acceptance: `tasks/reports/resume-17-build-preset-acceptance-20260925.md`
- RS-F27 accepted measurement: `tasks/reports/resume-13-rpg-simulator-rsf27-20260925.md`
- RS-F27 acceptance: `tasks/reports/resume-18-rpg-simulator-rsf27-acceptance-20260925.md`
- P11.1r blocker: `tasks/reports/resume-12-passive-tree-p11-1r-20260925.md`
- BCU2.12 audit finalization: `tasks/reports/seedsmith-p1-audit-final-20260925.md`
- Browser partial report: currently only `.claude/worktrees/opencode-resume-15-web-browser-qa-20260925/tasks/reports/resume-15-web-browser-qa-20260925.md`
- `.commandcode` tracked-configuration review: `tasks/reports/resume-30-commandcode-config-review-20260925.md`

## Completion boundary

This program is not finished at the collection HEAD. Terminal completion requires all of the
following, with no population-count or fabricated-evidence shortcuts:

1. terminal `GREEN` from `post_merge_check.py` for the final product/infrastructure head, with only
   the prefix-allowlisted and exact-expected evidence/report descendants after `gatedHead`;
2. current-head release/player-packaging and topology evidence;
3. real connected-injector live proof with normal-path persistence read-back plus separate engine
   observation;
4. real active-match browser recovery and cross-match isolation proof;
5. reconciled session, lane, acceptance, todo, and report records;
6. explicit owner disposition for P11.1r, BCU2-R1, BCU2.12, and every other owner decision;
7. BCU2.12 completed under its fail-closed generator-first gates, **or** an owner-approved deferral
   with a named receiving owner and preserved blocker. Without that explicit disposition, the
   program remains **partial/deferred**, not terminally complete.

## Manager update — terminal lane processing

The following terminal results are now recorded separately from the collection snapshot:

- `resume-30-commandcode-config-review-20260925` completed a read-only, hash-bounded review of the
  three owner-routed `.commandcode` paths. No source path, ignore rule, cleanup tool, or integration
  checkout was changed. The report is retained at
  `tasks/reports/resume-30-commandcode-config-review-20260925.md`; its six policy questions remain
  open and no recommendation was applied.
- `resume-29-strain-splice-reader-guard-20260925` returned `partial` with a 14-file implementation
  diff. Independent manager review is running in
  `.claude/worktrees/review-resume-29-strain-reader-guard-20260925`; focused changed-path checks are
  green, while the known Data sharded-runner exit-code defect remains separately under diagnosis.
- `resume-28b-effect-pipeline-epl1-1-20260925` returned `failed` after focused Python and C# checks
  passed; a Bitdefender deny-write lock stopped the broad verifier on an unrelated output. Its four
  dirty files remain quarantined for manager harvest and are not accepted or merged.

The main integration checkout remains blocked by the cleanup-owned six paths and the three
owner-routed `.commandcode` paths. No merge, cleanup, ignore-rule change, current-head gate, browser
proof, live proof, or BCU2.12 resume is authorized by this update.

## Manager update — exact-SHA acceptances

Two independently reviewed implementation slices now have schema-v2 acceptance artifacts on the
manager branch:

- EPL1.1 exact SHA `8334a1d617cdf68edd33929262315f8502c7ea91` —
  `.claude/cmdc-agents/acceptance/resume-28b-effect-pipeline-epl1-1-review-20260925-8334a1d6.json`.
  The manager repaired the invalid-enum ordinal contract and hardened registry schema/numeric-field
  refusal. Focused Python 12/12, C# atoms 10/10, generated-seed, item validator, item gate, and
  PlanOnly checks are green. The broad verifier's unrelated AV output denial remains a documented
  limitation, not a hidden pass.
- SSH7.1/SSH8.4 exact SHA `a120ce2d8f83617228017a020c063c35e3c37dd0` —
  `.claude/cmdc-agents/acceptance/resume-29-strain-reader-guard-review-20260925-a120ce2d.json`.
  Guard 5/5, Seedsmith 39/39 plus 7 subtests, Core Items 78/78, Data Items 16/16, Server 111/111,
  worker-report citations, PlanOnly, and detached clean-checkout checks are green. The known Data
  sharded-runner/external backup-file failures remain explicit limitations.

Neither exact SHA is merged. The cleanup boundary and owner-routed `.commandcode` decision still block
integration, and the current-head gate has not run.
