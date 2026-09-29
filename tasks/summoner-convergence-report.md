# Summoner-Convergence — manager report

**State as of `ba077932` on `features/mega-merge` (manager, 2026-09-20).** This is the checkpoint report the
delegation-first goal owes the owner: what each program's queue actually contains, which lane is carrying
it, what has merged, what is ruled, and what is blocked on whom. Row counts are read from the todos at
this head; lane state is the last recorded snapshot, not a live probe.

## 1. Programs and their queues

| Program | Anchor | Open / done rows | Carrying lane |
|---|---|---|---|
| species-gear-chain | `tasks/species-gear-chain-anchor.md` | 288 / 183 | `sgc-1` (wave 1) |
| strain-splice-host | `tasks/strain-splice-host-anchor.md` | 55 / 32 | none — spec phase awaits the owner |
| empire-progression | `tasks/empire-progression-anchor.md` | 59 / 25 | `ep2-1` (wave 2) |
| combat-ai | `tasks/combat-ai-anchor.md` | 43 / 12 | none — slice 2 merged, next wave queued |
| notification-ssot | `tasks/notification-ssot-anchor.md` | 12 / 73 (updated 2026-09-21 by the `ns-1` lane) | `ns-1` — waves 0–6 landed; G2 blocked on `WS-live-1`, centre gated on the gui-lego row |
| test-verification-boundary | `tasks/test-verification-boundary-anchor.md` | 22 / 58 | `tvb58` |
| backlog-clean-up | `tasks/backlog-clean-up-anchor.md` | 6 / 69 | corpus runs (detached) |
| seed-corpus | `tasks/seed-corpus-anchor.md` → 4 runbook todos | 53 / 409 | `item-seed-gen` (merge-back) |
| **total** | | **552 / 843** | 6 lanes at the ceiling |

## 2. Convergence checkpoints (`tasks/summoner-convergence-todo.md`, 4 done / 7 open)

Open: `CV.1` (keep the shared tuning ledger true) · `CV.3` (stale `decisions.md` line citations — analysis
done, fix not written) · the `SE4` save-identity checkpoint · `EP` CP1–CP6 · species-gear-chain + SSH
checkpoints · TVB + NS checkpoints · and **CC8** itself (full suite green + a live probe on a real save).

`CV.2` (the golden re-bless register) is closed at `88571a11` with the H1 cause order recorded.

## 3. Landed this session

| Merge | Lane | Scope |
|---|---|---|
| `21984ce9` | scope-side-wide | SSW1–SSW3, side-wide `StatApplyScope` key |
| `91b68fef` | live-qa | CC2 probes at `da117305` |
| `c70761a8` | bcu8 | BCU8.2/3/5/6/7/9/10 at `355d1d3a` |
| `fb3aa570` | live-qa | 14 evidence fragments |
| `c9ce309c` | ssh27 | 16 rows, 17 fragments |
| `d936830d` | combat-ai | slice 2 (allocation-free `TopThreeInto`, `TryPay` scratch) |
| `741f5b01` | ep-autoassign | EP1.20/EP1.21 + CP2, the auto-assign catalog published and its readers switched |

**Not merged:** `cai-sink` — accepted as far as the Injector build (`Build succeeded, 0 Error(s)` at
profile `pvzrh-3.9`) and Core `~Effects|~Execution` 57/57, but `FusionRpg.Guard.Tests` came back
`Failed: 4, Passed: 576`, so the acceptance script refused its own merge and the tree was left clean.
The four reds are being enumerated so each is attributed rather than assumed pre-existing.
`item-seed-gen` is resolving an append-only merge conflict and is not merged either.

## 4. Rulings in force

- **D23 — rarity gates price, not possibility** (`187fe3b1`). No rarity arm may be added to
  `HostAdmits` (`gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs:46-58`).
- **A green exit code is not acceptance evidence until TVB-F3 is fixed** (`b1e1cbfd`): `verify-change.ps1`
  was seen printing failing runs while exiting 0.
- **Corpus sequencing** (`4ae359fb`): the propose stage costs ~42 s per brief, so the round is
  MODEL-bound. BCU2.11 does not run beside BCU2.10; BCU2.12 follows BCU2.11; BCU2.13 (no model time)
  starts the moment `ep2-1` retires, because its `species-build doublecherry attackTempo` half touches
  `CreatureBuildPlanGen`, which `EP2.3` owns.
- **Socket-word residue ships as its own lane** (`36264fb5`), never inside `ISG7` — `ISG7` is a
  generator/registry re-key and mixing a test cleanup into it would put two causes in one commit (H1).
- **BCU8.4's block was a fence problem** (`571b49af`), so its fence is assigned: `gk-core/src/FusionRpg.Data/**`
  and `gk-core/tests/FusionRpg.Data.Tests/**` in `--allow`, last in this program's queue.
- **`SE4.30` closed** on the migration probe (`8aba2900`) with both unmet clauses kept on the row.

## 5. Detached jobs the manager owns

- **BCU2.10 T4.6 round 1** — `generate_action_pipeline --round 1 --batch-size 25 --max-passes 8`,
  ~23–28 h, resume-safe, in `.claude/worktrees/corpus-bcu210` (branch `corpus/bcu210`). Its B0 preflight
  is GREEN at `6651c1b4` (`tasks/reports/BCU2.10-preflight.json`): the vocab, the v3/`full` tuning and
  the fresh coverage report all pass, the 1-brief propose proved transport in 42 s, and D: has ~191 GB
  free. The follow-up is checkpoint N (shortfall delta, `quotaDrift`, the O3 rows).
- **BCU2.11–2.13** are queued behind it by the sequencing ruling above; BCU2.11's full item-seedgen run
  is the largest remaining piece.

## 6. Pipeline tooling added (manager plane)

`accept_lane.py` (fixed the two bespoke-script defects: it proves the review checkout and its SHA before
running anything, and it keeps the FULL log so failing test names survive; it splits registered debt from
an unregistered failure and merges only on all-green) · `resolve-append-only.ps1` +
`union_append_only.py` (the union resolution for the append-only conflicts every lane merge produces) ·
`tasks/reports/BCU2.10-preflight.json`.

## 7. Open blockers, with owners

| Blocker | Owner |
|---|---|
| The 4 `FusionRpg.Guard.Tests` reds at the cai-sink checkout are unattributed | manager, enumeration job running |
| `TVB-F3` (verify-change exit 0 despite failures), `TVB-F1`, `TVB-F2` | `test-verification-boundary` (queued on `tvb58`) |
| The four pre-existing red Core facts | registered as `knownRed` by `tvb58`; each already has an owning row (`tasks/item-seedgen-todo.md:522`, `tasks/atom-family-expansion-todo.md:624`) |
| The aura-disable withdraw wire (`UniqueActorService.PushAtomUnionAsync` is additive-only) | `tasks/backlog-clear-todo.md:99-106`, `tasks/backlog-clean-up-todo.md:370-374` |
| `strain-splice-host` spec phase | **owner** — 55 rows cannot start without approval |

## 8. What needs the owner

1. **`strain-splice-host` R13 — the still-blocked cells, once the re-run prints them.** The program is
   **not** idle: `ssh27` is working it (SSH2.7 onward, seg 11). R13 asks you to rule each still-blocked
   grid cell by id, and it becomes answerable only when `SSH5.11`'s re-run re-prints the report
   (`tasks/strain-splice-host-todo.md:301`), so there is nothing to answer yet. *(Corrects this
   report's earlier "spec-phase approval" line, which named a gate the program does not have.)*
2. **CC8's live half** — the full-suite gate plus a live probe on a real save needs the game and server
   up; both are outside the manager's hands (BP4's live run left the game and server closed).

## 9. Checkpoint 2 — 2026-09-21 (supersedes the rows it names)

**Owner rulings landed** (commit `d12dcb90`):

| Gate | Ruling | Released |
|---|---|---|
| A1 (NS0.1) | the rail moves to `shell/notify/rail/` | NS5.7–NS5.11 |
| A2 (NS0.2) | the fog rule moves into Core `WorldReportVisibility` | NS5.2, NS5.3, and NS5.12, NS5.13, NS6.5 with them |
| NS6.8 | owner named a resolver instead of reviewing in person: the gui-lego program accepts the queue row | NS6.11/NS6.12 stay gated on that row being accepted and dated |
| T37/T38 | author a per-base-type `successorOf` edge; never derive it from the class ladder | T38 released, T37 unblocked; the ~800 non-armour values stay the content pass at `tasks/species-gear-chain-todo.md:1941` |

**Still owed by the owner:** T27 (`setClass` topology classes), the `strain-splice-host` spec phase (55 rows),
and CC8's live half.

**Lanes this checkpoint:** `ns-1` continued with A1/A2 (its 15 released rows); `sgc-1` continued with
T37/T38; `docs-citations-1` spawned (`docs/**` + `tasks/**`, worktree) carrying `CV.3`; `ssh27`, `tvb58`
and `ep2-1` running. Fleet 6/6.

**Program bookkeeping:** the species-gear-chain ledger queue was re-seeded to its 8 open tasks
(`3da77ab4`); 12 finished session records were retired and 4 invalid statuses fixed (`182fc1fc`), leaving
7 active records.

**Manager-plane tooling:** `accept_lane.py` gained the contention preflight (exit 9 + `-AllowContended`),
flake labelling, and a `contendedTree` field in the JSON artefact (`a062b019`).

**Detached jobs:** `BCU2.10` round-1 (`b4d86b632`, worktree `corpus-bcu210`) and `item-seed-gen`
acceptance (`bd277c482`).

**Known and reported, not fixed:** `scripts/session-boundary-check.py` still exits 1 repo-wide with 39
broad-glob overlaps among long-lived records (`tasks/sessions/**`, `tasks/evidence-fragments/**`,
`gk-core/tests/FusionRpg.Core.Tests/Battle/**`, `docs/architecture/decisions.md`). No lane is affected —
`scripts/verify-change.ps1:242` runs the check scoped by `-Session`, where drift belonging only to other
sessions does not fail — but `keepverse-split` (a different program, parked before its gate GM) does
overlap `combat-ai-build-20260920` on Battle tests and `docs/architecture/decisions.md`. **Owner ruling
2026-09-21: Keepverse is deferred until summoner-convergence and backlog-clean-up are complete**, so the
record stays active and those two overlaps remain reported rather than resolved.

### 9.1 Coverage measurement (2026-09-21) — the end state's real bar

"Every sub-program todo at 0 open rows" needs a stated definition, because the anchors' numbers were
line counts while one program is task-shaped. Measured per file (unchecked `- [ ]` lines; task-heading
counts only apply where the todo is written as `#### Task T<n>:` headings):

| Todo | Open rows | Done rows | Open tasks |
|---|---|---|---|
| `species-gear-chain` | 288 | 183 | **4** (T27, T31, T37, T38; 21 of those rows) |
| `strain-splice-host` | 55 | 32 | — |
| `empire-progression` | 59 | 25 | — |
| `combat-ai` | 44 | 12 | — |
| `passive-tree` | 33 | 325 | — |
| `test-verification-boundary` | 23 | 58 | — |
| `notification-ssot` | 12 | 73 | — |
| `action-distribution-gaps` | 13 | 25 | — |
| `backlog-clean-up` | 6 | 69 | — |
| `item-seedgen` | 4 | 38 | — |
| `seedsmith-generated-seed-repair` | 3 | 21 | — |
| **total** | **550** | **847** | |

A row is an unchecked checklist line, and the bar is 0 in every file. Two consequences worth stating:
species-gear-chain's `287`-style figure is not 287 tasks — it is 288 rows of which only 21 sit under the
four open task headings; and **five programs hold 59 rows with no lane**: `combat-ai` (44, its lane is
terminal), plus the seed-corpus runbooks `passive-tree` (33), `action-distribution-gaps` (13),
`backlog-clean-up` (6), `item-seedgen` (4) and `seedsmith-generated-seed-repair` (3). Slot order when a
lane retires is therefore: a fresh `combat-ai` lane, then `sgc-2` (brief ready), then the seed-corpus
lanes.

## 10. Checkpoint 3 — 2026-09-21 (the owner's FIRST MOVE is complete)

**Five unaccepted lanes cleared, in the owner's order** (`cai-sink`, `item-seed-gen`, `live-qa`, `ssh27`,
`combat-ai`), each accepted at a named SHA and merged `--no-ff`:

| lane | reviewed SHA | merge | what decided it |
|---|---|---|---|
| `cai-sink` | `e37a9f58` | `04da1747` | the lane's four reds are a subset of the seven measured on the Guard baseline `b6712875b` (7 failed / 573 passed at `48fd754e`), so it introduced none |
| `live-qa` | — | already merged | 0 commits ahead of the integration head, ancestry checked |
| `combat-ai` | — | already merged | CAI1.11 `b19c9460`, CAI1.12 Core `c3bb0ba2`, CAI1.13 `98e20e10`, CAI1.14 slice 2 `d936830d` |
| `item-seed-gen` | `cb0eff76` | `068906eb` | validator 0, CI guards 21/0, and a base run that made the pytest reds attributable: base `e0f1375d` 22 failed vs tip 20, **empty set difference**, two fixed by the lane |
| `ssh27` | `4e94fd92` | `e78f4a12` | boundary 0, actor-hub OK, python combogen+strain-splice 0; the two Core socket reds are pre-existing `ISG-F1` members. Merged the **reviewed** SHA, not the branch tip |

**Pipeline defects found by clearing those lanes, and fixed on the manager plane:**

1. **Every lane's `verify-change` was reporting foreign drift** (`733ef458`). Cause, measured not guessed:
   `session-boundary-check.py` skips a collision only when *both* records are `mode: worktree`, and two
   `mode: direct` records were not skipped against any lane. `-Session combat-ai-build-20260920` reported
   **29 blocking problems, every one naming the manager's own record**. `keepverse-split` (parked at the
   owner's gate GM, all artefacts at HEAD) was retired and the manager and `docs-citations-1` records were
   narrowed to what they actually write.
2. **The anchors pointed at a script that does not exist.** A stray `0x0B` (a JSON `\v` escape) had eaten
   `\` and `v` from `.\scripts\verify-change.ps1`; the first repair wrote the replacement text wrong
   (`.\scriptserify-change.ps1`). Eleven occurrences across 8 anchors and 3 briefs are now correct, and an
   `0x0B` scan over every tracked text file is 0 (`e26fc765`).
3. **`TVB-F8`**: `gk-core/data/tuning/aptitude-auto-assign-catalog.v1.json` arrived with a merge and no
   `boundaries[]` owner row, which failed `guard-verification-boundaries.py` and two Guard tests in
   `tvb58`'s verification — one root cause, not two lane defects. Row added, guard re-run OK (`0f77d670`).
4. **A retired record was being asked for a live branch**, which no merged session can satisfy once its
   worktree is removed. The rule now applies to `status: active` records only (`63e3b858`), and the
   repo-wide `session-boundary-check.py` exits **0** for the first time in this convergence.

**Verification of an H7 surface (the trigger rule, used once):** the `ssh27` merge carried a tuning
publish (`sockets.v2.json`, commit `611d9c23`), so it was not merged on the lane's word. The manager ran
its cheap check (both revision constants name v2; v1 on disk as the revert path; every remaining revision
literal is comment prose; `maxCombosPerActor` gone with only the `SOCKETS_OWNED_KEYS` deny-list naming it;
the literal guard filter 2/2) **and** commissioned an independent read-only reviewer, which returned
**merge-OK, Q1–Q5 PASS, no reader defect** (`tasks/evidence-fragments/SSH5.10-independent-review.md`). Its
four P2 notes are routed as `SSH5.10-P2`. Two other verifier paths failed first (`bg_delegate` could not
project this conversation; `fusion_validate` died on `pi_executable_resolution_failed`) — recorded rather
than silently retried.

**One union artifact the merge exposed, repaired by the merger** (`06a7c452`): item-seed-gen's `--overwrite`
guard and ssh27's R11 `--retry-blocked` pre-flight both live in `_cmd_items_combination`, and the merged
file ran the tuning-state refusal first, so `--overwrite all --retry-blocked` returned `EXIT_REFUSED` (3)
where the test expects `EXIT_CANNOT_RUN` (2). `test_strain_splice_gen.py` 68 passed / 1 failed → 69 passed.

**Routed this round** (every finding has an owning row): `TVB-F9` (the four Core reds behind `ISG-F1` are
unregistered, so three acceptances had to be explained in prose — fix or register them before CC8), the
15 unregistered seedsmith reds (`tasks/seedsmith-generated-seed-repair-todo.md`), `DM-F1`,
`SSH5.10-P2`, and the correction that `TVB-F8`'s "missing per-path check" already exists at
`scripts/verify-change.ps1:114`.

**CC8's red inventory (the closing gate), each line with its owner:**

| suite | state | owner |
|---|---|---|
| Core | 4 failed / 73 passed at the post-merge head (`SocketOperations`, `UniqueCorpus`, `FamilyExpansion` filters) | `ISG-F1` + `TVB-F9` (unregistered) |
| Guard | 7 failed / 573 passed at `48fd754e` | `TVB-F2`, `TVB-F4`, `CAI-guard-1` |
| seedsmith (pytest) | 20 failed / 4142 passed at `item-seed-gen`'s tip — 5 registered `SR-25`, 15 pre-existing | routed to the seed-corpus runbooks |
| live half | not started | needs a game + server window |

**Burn-down, re-measured 2026-09-21:** 555 open rows / 855 done across 11 todos (species-gear-chain 289,
strain-splice-host 55, empire-progression 59, combat-ai 43, passive-tree 33, test-verification-boundary 28,
notification-ssot 22, action-distribution-gaps 13, backlog-clean-up 6, item-seedgen 4,
seedsmith-generated-seed-repair 2).

**Fleet 6/6** (`ns-1`, `ep2-1`, `sgc-1`, `sgc-2`, `ssh27`, `combat-ai-2`). Per the owner's ruling the freed
lanes re-point at the anchors one at a time: the next free slot goes to **`seed-corpus-1`** (brief ready;
it covers item-seedgen's 4 rows, passive-tree's 33, action-distribution-gaps' executable 13 and the
seedsmith-repair rows). `tvb58` stays parked until a slot frees. BCU2.10 round 1 is running as a detached
job (`D:\tmp\bcu210\round1.latest.log`), with BCU2.11 held back because it is model-bound to the same
endpoint.

**Still owed by the owner:** CC8's live half (a game + server window), `SSH5.12` (`resocket --write`, the
ask-first corpus rewrite) and `SSH5.13` (the R11 re-run) — R13's still-blocked cells become answerable
only after `SSH5.13` re-prints the report.

## 11. Checkpoint 4 — 2026-09-21 (after the pause; five more lanes integrated)

**Lanes merged since checkpoint 3** — each accepted at a frozen SHA with cheap checks, then merged
`--no-ff`, then re-checked at the merged head:

| lane | reviewed SHA | merge | decisive evidence |
|---|---|---|---|
| `ep2-1` | `48576b91` | `50a8e5e3` | Core aptitudes/species-build/lean/respec 414 passed / 0 failed; `CreatureBuildPlanGen` exit 0; ledger OK (258 events) |
| `combat-ai-2` | `eaafeaaa` | `87112284` | guard-actor-hub OK; ledger OK; its only product red was the pre-existing `ISG-F1` socket test, pulled in by my own `~Ai` filter matching "aw-**ai**-ts" |
| `ns-1` | `483bb678` | `4bce1fe5` | Core fog/intel 88 passed; Server notification/WorldReport 57 passed; ledger OK |
| `sgc-2` (S1) | `be608027` | `cc2b01a9` | ledger OK; `guard-doc-citations -Strict` exit 0 |
| `sgc-1` | `791aacad` | `12806367` | **GREEN** — boundary 0, Core item/upgrade/successor 45/45, focused seedsmith 0, ledger OK |

**The merged head builds and its generated trees do not drift.** `dotnet build
gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj -c Debug` → 0 errors, 6 warnings, 9.9 s;
`CreatureBuildPlanGen -- --check` exit 0 and `CreatureSpeciesGen -- --check` → "clean, 904 species match".
No lane had made either claim about that head.

**Guard reds: 7 → 4 at the post-merge head, fully attributed** (run `b11c9249e`). Every one of the four is
a member of the recorded seven, so no merge introduced one; `TuningRevisionLiteral` was already cleared by
`e99242c4`, and the two load-flaky `VerificationBoundary` tests did not reproduce. Two of the remaining
four were not about their subjects at all — `CiWiringGuardTests` and `CoreTestProjectPolicyTests` threw
`UnauthorizedAccessException` on the stale gitignored `tools/seedsmith/.tmp-seedsmith-pytest-audit` from
`Directory.GetFiles(..., AllDirectories)`, i.e. they never evaluated their rule. Fixed on the guards plane
with a shared `GuardWiring.SafeFiles` walk (`6bdd696c`, 11/11 green on the affected classes). The other two
are routed, not fixed here: `CAI-guard-1`'s deliberate re-pin (`tvb58`) and a live pipe-drain offender the
guard names itself, `gk-core/tests/FusionRpg.FileMove.Tests/SplitExecutorTests.cs` (into `TVB-F2`).

**Process lesson that cost real time.** I capped `maxAutonomousRuns` to `0` to stop empty-run churn. A
capped goal is a **paused** goal, and a paused goal cannot act on notifications either — so the heartbeat's
turn could only report. Five lanes then sat `partial` for ~90–100 minutes and `sgc-2` sat `failed`, while
BCU2.10 kept working (detached process, unaffected). The allowance stays uncapped; the manager's turns stay
cheap instead. Also learned the hard way: an acceptance launcher must take `-ExpectSha` as a **parameter** —
mine hardcoded a literal and silently ignored the pin, aborting two `sgc-1` attempts on SHA drift.

**Fleet now:** six lanes on fresh segments (`ns-1`, `sgc-1`, `sgc-2` after its exit-3 retry, `ep2-1`,
`ssh27`, `combat-ai-2`); `tvb58` and `seed-corpus-1` queued behind the 6-lane ceiling with exact commands
on the run board. BCU2.10 round 1 is still producing (5500+ model calls, no report artefact yet); BCU2.11
stays held back because it is model-bound to the same endpoint.

**Still owed by the owner:** CC8's live half (a game + server window), `SSH5.12` (`resocket --write`, the
ask-first corpus rewrite) and `SSH5.13` (the R11 re-run), after which R13's still-blocked cells become
answerable. Open rows are **538 open / 912 done** across the eleven todos (re-measured 2026-09-21
09:30; the pre-batch reading was 555/855), so the end state is not close and nothing
here is claimed as convergence.

## 12. BCU2.10 round 1 — the action-corpus run reached its first milestone (2026-09-21)

The owner-assigned corpus run (manager plane (d), detached job, report artefact) finished its first round
against the current plan: commit `710390b5` on `corpus/bcu210`, merged here. Readings, taken from
`gk-data/packs/fusion/data/seed/actions/_reports/coverage-round-1.json`'s `_meta` rather than from prose:

| reading | value |
|---|---|
| acceptedCorpusSize | **181** |
| mode / partition / tuningVersion | `full` / `round-1` / `3` |
| roster | families **227**, familyAssigned **1183**, species **904** |
| reviewQueueCount | 0 |
| corpusHash | `9c8ff5b7c981ede955cd47eaffe7143d935b6a6a678ddff947e11d18b200bbeb` |
| coverage entries | 5435 |

What it unblocks: **BCU2.11** (the item-seedgen full run, ~904 species / 36 sets / ~904 charms) is
model-bound to the same LM Studio endpoint and was deliberately held back so it could not contend with this
round — it is now released. **BCU2.12** (passive-tree J9/J10/J13) follows it, and **BCU2.13** (the small
re-classifies) waits on the species-build surface, whose `CreatureBuildPlanGen` overlap (lane `ep2-1`) is
now merged. The top-up rounds of BCU2.10 itself (`action-distribution-gaps` T3.2/T3.3) stay owner-gated.

Nothing here is asserted as convergence: these are the run's own printed readings, and the corpus still has
open rows in all four runbooks.

## 13. BCU2.11 — the item-seedgen full run reached its milestone, with one real content defect

Owner-assigned corpus run (manager plane (d), detached job, report artefact), branch `corpus/bcu211`:

| reading | value |
|---|---|
| fill passes | smoke exit **0**, `items fill --full --continue-on-error` exit **0**, second (overnight-rule) pass exit **0** |
| items health check |  exit **1** — `[GAP] Linkage/SetCompletability` |
| corpus size | **1048** item json files (sets 885, base-types 62, uniques 18, affix-families 16, …) |
| diff | 68 files changed, **129,299 insertions**, 330 deletions |

The red is content, not tooling: hybrid sets name member roles outside the hybrid role core (`head-guard`,
`sense`), so *a hybrid frame could never complete those sets* — exactly what that check exists to catch. It
is routed as **`ISG-gap-1`** in `tasks/item-seedgen-todo.md` with the hard rule attached: fix the
**generator** and regenerate; never hand-edit `gk-data/packs/fusion/data/seed/items/**`. The run's output is committed on its own
branch so the work is preserved while the generator fix is made; it is **not merged** until that check
passes, because merging it would land a corpus its own checker rejects.

**BCU2.12 (passive-tree J9/J10/J13) is released** by this run finishing — it was held back only because the
fill is model-bound to the same local endpoint. BCU2.13 stays on the species-build surface (`ep2-1`'s merge
unblocked it).

## §14 Checkpoint (2026-09-22 00:30) — the number was wrong, the gate was broken, and both are now fixed

**Owner-facing summary of this batch.** Five lane batches are merged, each accepted at a frozen SHA with an
artefact under `.claude/cmdc-agents/acceptance/`: `combat-ai-3` (12 commits, `c9250d229`, GREEN), `seed-corpus-1`
(`39029506f`, carrying the **J9-B1 fix** — the codex vote resolves and a duplicate `nameKey` no longer loses a
whole tree), `ep-3` (`90e170d82`), `tvb58` (`f2d2d8e61`), `tvb59` (`2b1ef9977`, GREEN 4/4).

### The headline correction: the burn-down number overstated the work, and the owner was right to ask

The published burn-down counted unchecked `- [ ]` **lines**. A line is normally an acceptance-condition box
*inside* a task, and `tasks/species-gear-chain-todo.md`'s own header says its shipped tasks' boxes are "the
original contract" and "were not re-run one by one". So a shipped task contributes 6–10 permanently-unchecked
lines, and the program I had called "too huge" in fact holds **25 task headings, 24 shipped by name, 7 open**.
Lane `recon-1` is measuring every program the same way and reporting how far that clause spreads; its report
lands at `tasks/reports/backlog-reconciliation-20260921.md`. Until then, no lane-count or split decision should
rest on a line count — including the ones I already made this session.

### Guard state at the merged head: 3 reds, each with an owning row

Measured on a quiet machine, 3 failed / 580 passed (14 m):
1. **`EP-F1`** (empire-progression) — `ZombossCommanderLevelSingleReaderGuardTests`: `RpgStore.EmpireSpecies.cs`,
   new in the EP4 batch, reads the narrow `SELECT level FROM rpg_actor_progression` shape where the guard admits
   one seam, `RpgStore.CommanderLevelOf`. Lane `ep-3` steered to fix it. **The lane's own acceptance could not
   see it** — it ran aptitude/species/plan-gen/ledger filters, not the Guard suite.
2. **`TVB-F19`** (test-verification-boundary) — the boundary planner demands a `.cs` path from every active
   session, so a documentation-only lane (`recon-1`, fence `tasks/reports/**`) throws instead of passing or
   skipping. Not fixed by widening the record (that would grant a report-only lane write access to code).
3. **`CAI-guard-1`** (pre-existing row) — the `BattleEffects.cs` byte baseline: pin `52F843B0…`, actual
   `02B04A25…`, moved by `c3bb0ba2` (CAI1.12, per-place executor allowlist; `combat-ai-todo.md:830` records
   384 → 447 lines). An H1 surface, so the fix is a re-pin in its own commit naming that cause — assigned to
   `tvb58`, which holds `tests/**`.

### A reading that nearly cost a day: 178 "defects" that were one contended machine

The first run of the new post-merge gate reported **178 Guard failures in 6 seconds**. That was 30+ orphaned
MSBuild nodes from a killed job holding CPU; after clearing them the same suite read **3 failed / 580 passed in
14 minutes**. Nothing but the duration separated the two readings. My own gate produced it, so the gate now
refuses to be read that way: it resolves `dotnet` explicitly and **aborts** rather than opining, treats a
missing `Passed!`/`Failed!` summary as failure, prints **UNKNOWN** when nothing ran ("no check ran is never a
pass"), keeps its transcript so failing test names survive, and labels a sub-120-second mass failure **SUSPECT**.

### Corpus and CC8

- `corpus/bcu211` (BCU2.11's item run) is committed and **unmerged**, gated on lane `isg-gen-fix`, which has
  located the cause — 18 defective set entries, all in five legacy `sets-1c` files (promptVersion 1, pre-D30)
  whose hybrid sets claim roles outside the hybrid role core.
- **J9's 840-species run is held** on the measured `J9-B2`: the codex vote resolves about one attempt in two, so
  one invocation does not converge (pass 1 wrote one species, the resume pass inverted exactly that). Lane
  `j9-vote` owns the bounded-retry fix. `J13` follows J9 on the same local model.
- **CC8's live half now has a mechanism.** The owner's game-pool policy is in force: three slots claimed by file
  lock with no human sequencing (`docs/contributing/live-probe-standard.md` §9). Smoke-testing the implementer
  found a real defect — an explicit `-MaxSlots` was ignored, so the cap silently widened — now fixed and
  re-measured, including that no stale lock is left behind. Per the objective, a QA lane *produces live
  evidence* and is "not a re-runner of unit boundaries"; unit re-running after a merge is the gate above.

### Manager plane changes worth recording

The acceptance harness no longer races a fed lane's tip (it pins the reviewed SHA — `27728f9e7`); three
false-green paths are closed in the post-merge gate; and this batch's own merge slips (a dropped brace, a
smashed import line, an invalid session record) are recorded as one rule: **a structural edit validates in a
step that gates the commit, never beside it.**

**Outstanding owner items:** nothing blocking. The objective still says "at most 6 running lanes" while the
charter (owner, 2026-09-21) says 8 — the owner takes that to `/goal-tweak`. The `project-leader` skill is
written and in reserve, to be deployed on the measured trigger now being reported by `recon-1`.

## §15 Checkpoint (2026-09-22 02:30) — three lanes merged, one corpus run honestly refused, and J9 released

**Merged, each accepted at a frozen SHA with its artefact:** `isg-gen-fix` (`687709650`) — the items generator's
hybrid-set role defect, measured **30 → 0** `Linkage/SetCompletability` readings; `tvb58` (`156a8b5a9`) — the
`TVB-F19` guard-rule fix, whose reds were re-measured **at the integration head** and shown pre-existing;
`j9-vote` (`0e812c098`) — `J9-B2` closed: one driver invocation converges (bounded codex re-vote, measured 8/8
species over 13 draws, 0 named failures), plus the positional-count bug that would have stopped the 840-species
run from starting at all.

### BCU2.11 — the generator fix is in; the corpus it produced is a regression and was NOT merged

This is the checkpoint's most important line. The BCU2.11 run's corpus (`corpus/bcu211`, 955 files) was believed
to fill the base corpus's 911 `Coverage/EmptyPartition` gaps. Measured in the same tree with the same command,
taking each items corpus **wholesale**:

| items corpus | gaps | of which |
|---|---|---|
| the integration head's (isg-gen-fix's regeneration) | **931** | 911 `Coverage/EmptyPartition` |
| `corpus/bcu211` after the role repair | **1674** | 911 `Coverage/EmptyPartition` **+ 747 `SemanticDedup/NearDuplicate`** |

So it fills **nothing** it was believed to fill and **adds 747 near-duplicates**. The claim in
`tasks/reports/ISG-gap-1.md:22` is falsified; the merge was reverted to the head's corpus (re-measured 931) and
`ISG-gap-2` was corrected rather than deleted, so the 911 gaps stay open with an honest statement of what closing
them requires: **a re-run against the current generator inputs**, not this corpus.

**A shape error worth keeping:** the first attempt merged the two corpora with `-X theirs`, and the result read
**1675** gaps — worse than either side — because both descend from the generator and each regenerated its own copy.
Generated trees are taken **wholesale from one side or not at all**; a 3-way merge of them manufactures a corpus
that is neither. That reading came from running the health check after the merge, not from trusting it.

### BCU2.12 / J9 released

`J9-B2` was the gate, and `j9-vote` closed it, so the **840-species production run is now in flight** as a
detached manager job (`b53e979f0`) with its report artefact — smoke first, then the roster-length run, then a
resume pass, then the model-free census. `J13` follows it on the same local model.

### Routed this round

`ISG-gap-2` (the 911 pre-existing coverage gaps, premise corrected), `TVB-F21` (two CI-gating guards —
`magic-numbers` and `population-pin` — red **at the head** and routed nowhere; they were clean earlier the same
day, so the reddening commit is the first thing to find), plus the earlier `EP-F1`, `TVB-F19` (now fixed),
`CAI-guard-1` (fixed), `TVB-F20` (the replacement metric), `LEDGER-R1`, and `RECON-F1..F9`.

### Manager plane, for the record

The sweep is now one tool (`lane-signals.py`: runner signals **plus the lane's own pi session**), the acceptance
harness refuses to call an unattributed red "registered debt" and prints `UNATTRIBUTED` with the log, and the
project-manager skill carries the mechanism and the traps. Every one of those came from a mistake this session
made and measured — including four launcher bugs that each looked like work and did nothing.

## §16 Checkpoint (2026-09-22 17:40) — the live-test path works, two CC8 blockers closed, and two of my own diagnoses corrected

Owner directive this era: *"Fix it and make this work completely"* → *"Run it"* → *"Resolve them"* → *"Fix it"*.
All four steps landed, and the interesting part is what the work corrected.

### The four steps, and the evidence that they are done

1. **The injector's silent fallback is gone.** `FileRpgConfig` pre-filled `ServerUrl` with the owner's `:5088`,
   so the "nothing configured" branch could never fire. `ServerUrlFromFallback` now exists on the interface and
   all three implementations, and `Initialize` warns. Verified in the **deployed** assembly
   (`Mods/FusionRpg.Injector.MelonLoader.39.dll`, 648704 bytes, `ServerUrlFromFallback=True`) — not by reading
   source, which is the mistake this took twice.
2. **Two pooled servers at once**: `:5101` and `:5102` both `HTTP 200`, the owner's `:5088` untouched on PID
   30644, both stopped by recorded PID.
3. **A real connection is now provable**: a game launched from a pool slot reporting
   `server=http://127.0.0.1:5101` in the injector's own line, with the slot server's own log as the second,
   independent witness. `scripts/prove-slot-connection.ps1` reports **CONNECTION PROVEN** and
   **DATA PATH HEALTHY** as separate verdicts, because on this run the first was true and the second was not —
   one combined line would have hidden the defect.
4. Committed: injector hardening, the pool tooling, the board, the acceptance verdicts, the briefs.

### Three traps, all of which produced convincing wrong answers

- **`src/**/bin` is not where the injector lands.** The `.39` host redirects `OutputPath` into the game's
  `Mods\` once its refs resolve; the copies under `src/**/bin` are 4 KB **skip-stubs** from a ref-starved build,
  and a stub build prints `0 Error(s)`. Reading them produced a confident false negative.
- **`Ambiguous project name 'FusionRpg.Injector'` is a repo property, not worktree drift** — a compatibility
  shim referencing a project whose `AssemblyName` is the same string. Pruning 52 worktrees did not and could not
  fix it.
- **`2>&1` does not capture `Write-Host`** (it writes to the information stream), so four call sites parsed empty
  strings and failed on output that had plainly printed. All now use `*>&1`, and the port is derived rather than
  parsed from log text.

### Two of my own diagnoses were wrong, and the lanes proved it

- **F13**: I filed it as *two* missing columns. Lane `f13-schema` derived the complete list (fresh head schema ∪
  all 110 `EnsureColumn` sites, diffed against the real 546 MB file): **exactly one** genuine miss,
  `dungeon_domain.first_clear_ref`. The eight `player_id` errors were a **stale `dist/FusionRpg.Server` binary**
  (built between 2026-09-07 and 2026-09-19, pre-SE4.20 SQL) querying a database a newer server had migrated.
  Fixed and merged (`fb0deb1ad`); the proof script now deploys **before** starting the server (the publish skip
  was the cause) and fingerprints the server binary in its verdict.
- **CS-F1**: I filed it as a ledger defect. Lane `cs-f1` proved it a **fixture defect** — a private `..\..\..`
  walk from a file sitting directly in `gk-core/tests/FusionRpg.Data.Tests` resolves one level *above* the repo root, so
  the boot answered the absence sentinel correctly and the test only passed in a worktree because `FindUp` kept
  walking into the main checkout's tree. Closed by deleting the private walk in favour of the shared
  `ContentRoot.Path`, and the assertion was **strengthened** (`Assert.True(boot.Ok)`, since `NotEqual(SeedTreeNotFound)`
  also accepted `Failed`).

### A false closure caught, and a ruling made

Lane `ssh29` ticked **SSH4.9** — "a real word on the real sheet" — closing it *"on the manager's ruling"*. **No
such ruling was given**, and all three acceptance lines were unmet (nothing socketed, nothing equipped, nothing
read back; the pre-probe suite not run). The row is re-opened with the evidence kept and the claim dropped, and
the connection half is recorded as what it actually is: a prerequisite. Its word-on-sheet half is the lane's next
work, now that F13 is fixed.

### Routed

`F14` (F13's fix has no committed regression test — the lane's fence excluded `tests/**`), `KS-F1`/`KS-F2` in
`keepverse-split` (the two defects CS-F1 exposed: a boot with no Keepverse content-root awareness, and nothing
forbidding a private repo-root walk in a test).

### CC8 status

Suite half: `CS-F1` closed (fixture), `ADG-F4` in a lane (an E2E test red in the suite, green alone). Live half:
the pooled path is **proven to connect**; the data path awaits the re-proof delegated to `ssh29`. Guards green at
the head (21 run, 0 red) when last measured.

### Plane (d)

The BCU2.12 corpus run had **stalled**, not slowed: a 967-minute-old artefact, no process, census 1 complete /
12 started-incomplete / 888 untouched, five uncommitted corpus files. Relaunched detached the way its own header
requires, now at `[12/904]` with an empty `.err` — measured **~50 s/species**, so roughly 12–13 hours for the
roster rather than the ~100 hours the earlier estimate implied.
