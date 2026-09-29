# Handoff: the multi-lane run of 2026-09-20

**Written for:** the next manager session that picks up Summoner-Convergence and Backlog-Clean-up.
Not a plan and not a spec — the state the plans assume you already know.

**Date:** 2026-09-20 · **Branch:** `features/mega-merge` · **Head at handoff:** `dfcd52f9`

**Why this file exists:** the owner ran out of plan quota mid-run. Every lane was stopped on that
signal, which is the charter's stop rule, not a failure of the work. Nothing is half-merged; the
unfinished work is uncommitted in the lane worktrees and is listed below file by file.

---

## 1. Where the branch is

`features/mega-merge` is at `dfcd52f9`, and it is green:

- `scripts/run-guards.ps1 -Tier ci` → **GUARDS OK - 21 guard(s) run, 0 red**
- The CI test projects build with **0 errors**
- `BattleGolden` / `Dominance` / `Category=BalanceGuard` → **36/36**

**206 commits** merged this session across nine lanes, in four review rounds. Every round was
verified in a detached worktree at the exact reviewed sha before anything touched the branch — the
procedure is in the `project-manager` skill and it is worth keeping, because it caught two real
blockers that would otherwise have landed red (§4).

## 2. Before you start anything

**Collect the charter.** The owner approves runtimes, models, budget and the stop rule *in the
current conversation* before any worker starts — that is a hard rule (`CLAUDE.md`, "Multi-agent runs
start with the owner's charter"). The charter this session ran under does not carry over, and this
run ended on a quota stop, so the budget question is live rather than routine. Do not read
`allowed-models.json` and treat it as approval.

The last charter, for context only: Claude Code native subagents, `sonnet` at `xhigh` for
implementation lanes, `google/gemma-4-26b-a4b-qat` on LM Studio for seedsmith generation,
unlimited parallelism until quota.

## 3. The lanes, and exactly what each one left

All lane worktrees are under `.claude/worktrees/`. Everything committed is merged; what is listed
under "uncommitted" is real work that was mid-task when the lane stopped.

| Lane | Worktree / branch | Last landed | Next task |
|---|---|---|---|
| save-share-hierarchy (C) | `cmdc-lane-c` / `cmdc/lane-c` | SSH2.6 — socket-words retired | SSH2.7 |
| build-preset + TVB wave 5 (D) | `cmdc-lane-d` / `cmdc/lane-d` | TVB5.6 + SplitPlanner MSBuild fix | TVB5.7 apply, then TVB5.8 |
| test-verification-boundary | `agent-a7caaafc906532c18` | registry conflict fixes | planner latency (§5) |
| empire-progression | `agent-a62e66aeb29dc472c` | EP1.19 | EP1.20 |
| backlog-clean-up | `agent-acff69ce4dcbf4b73` | BCU8.1 — `nerve.*` VFX apply cue drift (D17) | BCU8.2, Injector write-path honesty |
| combat-ai | `agent-a9fc4fb25a529a317` | CAI1.10 | CAI1.11 (unblocked, see §6) or CAI1.12 |
| item-seed corpus | `agent-a4b1f7b41c6d11881` | `_meta` provenance backfill | the 27 `TagAxisExclusive` findings (§5) |
| live-qa | `agent-a133b88741cadeb4f` | all 13 live checks closed | idle — no live item is currently blocked |
| scope-side-wide | worktree removed | nothing committed | the whole task (§6) |

### Uncommitted work, by lane

**empire-progression** — 12 modified, 2 new. An auto-assign pass spanning server, core and FE:

```
gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeAutoAssign.cs
gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs
tests/FusionRpg.Core.Tests/ClassSystem/AptitudeAutoAssignTests.cs
gk-core/tests/FusionRpg.Server.Tests/AptitudePresetEndpointsTests.cs
gk-web/web/fusion-rpg-web/src/features/aptitudes/autoAssign.ts + autoAssign.test.ts
gk-web/web/fusion-rpg-web/src/features/gui-lego/foldAptitudesSurfaceVm.ts
gk-web/web/fusion-rpg-web/src/lib/bus/aptitudePresets.ts, keys.ts
gk-web/web/fusion-rpg-web/src/ui/actor/AptitudesTab.tsx
gk-web/web/fusion-rpg-web/src/ui/gui-lego/pieces/aptitude.tsx
gk-web/web/fusion-rpg-web/src/ui/gui-lego/recipes/aptitudes-console.json
gk-core/data/tuning/aptitude-auto-assign-catalog.v1.json   (new)
docs/research/class-system/real-runs/              (new)
```

This is the largest uncommitted set and the one most worth resuming deliberately: it crosses
Core/Server/FE, so it is one of the three cases where the whole suite is the right call rather than
a scoped boundary. The new `gk-core/data/tuning/aptitude-auto-assign-catalog.v1.json` is an authoring act —
check whether it is a first publish (allowed) or should have gone through `gk-core/tools/tuning/publish.py`.

**test-verification-boundary** — `scripts/lib/VerificationBoundaries.ps1`,
`gk-core/scripts/verification-boundaries.v1.json`. Mid-edit on the registry. Every lane edits that file
additively, so if it conflicts, resolve by structural union by id and run
`gk-core/scripts/guard-verification-boundaries.py` **before** committing (§7).

**save-share-hierarchy** — `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json`. A registry, so
hand-authoring is allowed here; confirm the edit was finished before trusting it.

## 4. What the review rounds caught

Both of these landed as holds, not as merged red, and both were fixed by the lane that caused them:

1. **`doc-citations` went red on 22 citations**, and each lane had broken its own docs. CAI1.1
   moved the siege scorer into `Core/Actions/Ai/CandidateScorer`, shrinking `SiegeAi.cs` from 219 to
   115 lines under 20 live citations; EP1.5 deleted the TypeScript fill mirror, taking
   `autoAssign.ts` from 125 to 48 under two more. The guard's rule is that citations re-anchor in
   the **same commit** as the code move — worth enforcing on every lane, because a cross-lane
   citation break only surfaces at merge otherwise.
2. **A modify/delete conflict on `data/seed/items/socket-words/sockwords.json`**, resolved as the
   deletion: lane C's SSH2.6 retires the file through `combogen-migrate --write` (95 combination
   entries replacing 25 legacy ones) while the item-seed lane had only bumped its registry stamp.

## 5. Open work that is assigned but unstarted

**The verification planner is slow enough to time out its own tests.** Six
`VerificationBoundaryWorkflowTests` fail with `verification-boundary script timed out` in
`ExternalProcess.Run` — not assertions. Measured directly: `verify-change.ps1 -PlanOnly` took
**415 seconds for two paths** with 22 `dotnet.exe` hosts on the machine, and returned a correct
plan. A scoped planner that takes minutes defeats the point of scoping, so the fix is the latency
(likely per-path repo scanning or a repeated git call that should be hoisted), **not** raising the
timeout. If the timeout is raised anyway, it carries a comment saying why that number, and it never
becomes an asserted reading. Owner: the test-verification-boundary lane.

**Item-seed is at 62 validator errors, down from 3581.** The remaining findings were triaged as
generator defects rather than owner questions, because the repo's rule already decides them — a
failing seed test is a stale test or a generator defect, never a prompt to edit emitted JSON:

- **27 `TagAxisExclusive`**, 26 of them `combat-posture` carrying both `defensive` and `utility`.
  The axis is declared exclusive and the generator emitted two values on it. A blanket
  "defensive wins" was explicitly rejected: it hand-picks an identity for 26 items from outside
  their own evidence and the next run reverts it. Enforce exclusivity at emit time, regenerate.
- **8 content bugs** — `UniqueFrameImpossible` (4), `UniqueSetMembership` (3),
  `GemAffinityNotConcrete` (1). Each means a generator never constrained its draw.
- **6 kind/id findings** — `item-category` and `rare-name-words` ship but were never onboarded into
  `KindCatalog.cs` / `naming.v1.json`; `rare-name.head`/`tail` and `atom.chill-punisher`/
  `atom.rot-punisher` need the actual `naming.v1.json` rule read, then either renaming or a widened
  exemption — not four special cases.
- **19 `MetaIncomplete`** — largely done in `c896da35`. For anything left, do not stamp a model name
  that was never used; an admitted unknown provenance beats a fabricated `_meta.model`.

## 6. Two decisions already made — do not re-litigate them

**The patron aura buffs the enemy side (live defect, unfixed).** PT7's live probe read
`combat.power.fire` back at 47 on the plant side — the correct magnitude — and got the identical
value on the **zombie** side, contradicting `spec-patron-creature.md:27`. Root cause:
`PatronSecondaryPlugin` grants `OwnerKey = EffectOwnerKeys.Match`, and
`gk-core/src/FusionRpg.Core/Stats/StatApplyScope.cs:52-53` returns `true` unconditionally for `"match"`
regardless of side. `PatronAuraOverlay`, which used to keep it plant-side, was deleted in the
2026-09-06 seed-to-concrete T6.2 migration and the property was never re-verified.

*The decision:* **add a side-wide owner key to `StatApplyScope`.** The grammar has `plant:N` and
`zombie:N` (side *and* type id) and `match` (everything), but no way to say "every plant, any type",
so the aura asks for the only thing the grammar can express. Do **not** re-platform patron onto
`BattlefieldOwnSideReactor` — that answers "which side" in a second place and leaves the gap for the
next feature. `Normalize`, `Matches`, `IsKnownOwnerKey` and `IsMatchWide` all have to agree about
the new key, and whether it counts as match-wide changes behaviour, so decide it deliberately and
write the reason down. Leave the `instance:` Hot guard and the `player:` stub alone. A moved golden
means the change is wrong. Afterwards the live-qa lane re-runs PT7 criterion 2 against the real
game.

**CAI1.11 is not blocked.** The lane recorded it blocked because `SiegeAiIntentSource` binds
`IBattleView` at construction (`SiegeAiIntentSource.cs:113`) and owns a persistent
`RetargetLedger`/`BattleTrace`, so it cannot be rebuilt per decision; it proposed widening
`IIntentSource.TryDeclare` or making the view swappable per call.

*The decision:* **decorate `IBattleView`, not `IIntentSource`.** Every `IBattleView` method already
takes an `actorKey`, and `TryDeclare` reads the world exclusively through `_view`, so a trait-aware
wrapping view gives `bloodthirsty` its pre-decision decoration with no interface change and no
per-call swap. `gk-core/src/FusionRpg.Core/Actions/FoggedBattleView.cs` is already a decorating
`IBattleView` with a per-actor predicate — same shape, same seam. `loyal`'s post-decision redirect
stays in `IntentRouter.TryDeclare`. Check it against `spec-intent-router.md` §2 first; if the spec
forbids a decorating view, that is a real spec gap and a different conversation. CAI1.11 is H1, so
it carries a predicted-delta note.

## 7. Process, and what it cost to learn

- **Lanes stall on their own background jobs.** Six did it this session, each idling until the
  manager noticed. `.claude/agents/implementer.md` now carries "Never end a turn waiting on your own
  background job" (`ba035a2a`) — foreground, scoped, read in the same turn. Enforce it; the agents
  do not self-correct without being told.
- **`user-mapped section open` is contention, not a hang.** With 20+ `dotnet` hosts across lanes,
  another lane's MSBuild holds the handle. `dotnet build-server shutdown` and retry; waiting never
  clears it.
- **Heavy machine load makes evidence unreliable, not just slow.** Timeouts get read as failures.
  When a suite goes red under load, re-run the decisive case alone before attributing it to a change.
- **Chain git steps with `&&`, and use `git -C <worktree>`.** A `;` chain once committed conflict
  markers into `verification-boundaries.v1.json`, and once ran `checkout` in the main tree.
- **A recurring conflict is worth retiring, not re-resolving.** `RpgStore.Patron.cs` conflicted on
  three consecutive empire-progression merges, comment-only every time. Telling that lane to merge
  `features/mega-merge` back into its own branch ended it; the next round had zero conflicts across
  six lanes.

## 8. Still owed

- `tasks/summoner-convergence-report.md` was never written.
- Checkpoints CC5/CC6/CC7 need re-verification now that EP, SSH and TVB have landed; CC8 (full suite
  plus a live probe) is the manager's own.
- Owner decisions still open from earlier rounds: E26 vs dropping A32 (T71/T72), the NS A1/A2 asks
  and the NS6.8 recipe review, and the species-gear-chain T27/T37/T38 content gaps.
- `gk-core/scripts/verification-boundaries.v1.json` still has no `gk-web/web/fusion-rpg-web` entries, and
  `gk-forge/tools/seedsmith/tests/**` is unmapped. An unmapped production path is a verification-boundary
  defect — repair the mapping rather than compensating with a broad suite.
