# Handoff: `combat-ai`

**Written for:** the next agent session that builds this program. Not a spec, not a plan — the
orientation the plan pair assumes you already have.

**Date:** 2026-09-20 · **Branch:** `features/mega-merge` · **From:** session
`backlog-clean-up-20260920` (documents only; now closed).

---

## 1. What state the program is in

| Phase | State |
|---|---|
| Idea | **Done.** [docs/architecture/combat-ai-ideal.md](../docs/architecture/combat-ai-ideal.md), revision 3. Owner rulings **D1–D6** in §10 are binding and are not reopened. |
| Capability map | **APPROVED** 2026-09-20 by independent agent review. [combat-ai-map.md](../docs/architecture/combat-ai-map.md), 20 modules in 4 waves. |
| Specs | **Done.** 20 module specs in [docs/architecture/combat-ai/](../docs/architecture/combat-ai/), ~9,750 lines, plus 3 cross-program specs. Two independent reviews (`REVIEW-A`, `REVIEW-B`) and a fixer pass are in [docs/research/combat-ai/](../docs/research/combat-ai/). |
| Owner questions | **None open.** D7 (orders: uniques only in v1) and D8 (accept the idle-reward drift) are recorded in [backlog-clean-up/rulings-2026-09-20.md](../docs/architecture/backlog-clean-up/rulings-2026-09-20.md) and applied in the two specs. |
| Plan | **Done, unstarted.** [combat-ai-plan.md](combat-ai-plan.md) / [combat-ai-todo.md](combat-ai-todo.md), 38 tasks in 5 waves, prefix `CAI`. |
| Build | **Not started. Nothing exists.** `gk-core/src/FusionRpg.Core/Actions/Ai/` does not exist; `gk-core/data/tuning/combat-ai.v1.json` does not exist; `publish.py` has no `--remove-key`; `PerfProbe.cs` still reads `SectionCount = 25`. Verified 2026-09-20. |

Your first task is **CAI1.1**. Nothing blocks it.

## 2. Read these, in this order, before your first edit

1. `CLAUDE.md` and `AGENTS.md` — the hard rules. They are stated in full on purpose; do not skim them.
2. [tasks/combat-ai-plan.md](combat-ai-plan.md) — **especially "Corrections carried into this plan"
   and "Decisions inherited from the specs' open questions."** Those two sections exist so you do not
   rediscover a contradiction or re-litigate a default that is already settled.
3. [docs/architecture/combat-ai-map.md](../docs/architecture/combat-ai-map.md) — module boundaries and
   dependencies are binding.
4. Your task's own spec, in full. Then `docs/DESIGN-GATE.md` §1 rows it touches, and
   `docs/architecture/battle-engine-ssot.md` §2, §3c, §5.
5. The code each spec cites. **Code beats docs; docs beat comments.** Every spec cites `file:line`;
   open them.

## 3. The five things most likely to go wrong

1. **Re-blessing a golden that moved when it should not have.** Only `CAI3.6` re-blesses, and only four
   hashes, exactly once. `CAI1.5` and `CAI1.11` may move **siege** behaviour with a predicted-delta
   note. Everywhere else, a moved hash is a **defect in your change** — stop and report, never
   re-bless. Several tasks say "if a golden moves, this task is wrong"; that is literal.
2. **Claiming byte-identity without running the suite.** Most tasks' acceptance is that nothing moved.
   Run `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` and **state
   what it printed** in the commit body. An unrun claim is an opinion (DESIGN-GATE §3 rule 4).
3. **Putting a balance number in code, or a structural one in tuning.** The test is in the plan and in
   `tunables-ssot.md`: *would a balance pass ever want to change this?* → tuning. *Does changing it
   break whether the system works rather than how it feels?* → a code `const` **with a comment saying
   why**. `CAI4.7` is where this was already got wrong once in the spec round and corrected.
4. **Hand-editing `gk-core/data/tuning/**`.** Never. A change publishes `v{n+1}` through
   `gk-core/tools/tuning/publish.py`. Creating `combat-ai.v1.json` (new; does not exist yet) is the one authoring act (`CAI1.8`);
   everything after it goes through the tool, and `--remove-key` is built in `CAI1.7` for exactly
   that reason.
5. **A second scorer, a second composer, or a second rank walk.** One `AiScoring` under
   `Core/Actions/Ai/`. One `AiRowSelector`. One `ActorHub` compose. SOLID is binding, and an owner or
   ADR confirmation does not convert a violation into design.

## 4. Hard edges, restated

- **H1** — one golden cause per commit. See §3.1.
- **H7** — a publish switches its readers in the **same commit**: `CAI1.8`, `CAI3.1`.
- **`RulesetVersion` 5 → 6 happens once**, in `CAI3.6`, and nowhere else.
- **E1** — no wave-4 task starts before `BCU0.1` (`lawn-signal-ownership`) lands in the documents.
- **E2** — `CAI5.3` (default-on) waits on **two** lawn-plan preconditions: the unique deploy cap, and
  `actor-liveness-refresh`.

## 5. Things this program depends on that it does not own

| Needed by | What | Who owns it |
|---|---|---|
| Wave 4 entry | `BCU0.1` `lawn-signal-ownership` (documents) | `backlog-clean-up` |
| `CAI4.7` | `gk-core/data/tuning/lawn-perf-budget.v1.json` (new; does not exist yet) — `lawn.ai.decide`'s **share of the frame** | lawn plan (`BCU2.4`) |
| `CAI5.1` | `lawn-combat-baseline` — without it the A/B measures a 0.5 hit coin-flip | lawn plan |
| `CAI5.3` | the unique deploy cap (5 per side) **and** `actor-liveness-refresh` | lawn plan |

The lawn plan does not exist yet (`BCU2.4` is unstarted). **Waves 1–3 are entirely unblocked by it** —
that is why they come first. If you reach wave 4 and the lawn plan still does not exist, say so rather
than authoring `lawn-perf-budget.v1` here; two owners for one tunable is the fork this program exists
to prevent.

## 6. Process you must follow

- **Session boundary.** `backlog-clean-up-20260920` was documents-only and is closed; it does not
  cover any build task. **Open your own record** at `tasks/sessions/combat-ai-<date>.json` with a
  `paths` fence for your lane, and run `python scripts/session-boundary-check.py` before the first edit.
  Other sessions edit this tree concurrently — never `git stash`/`checkout`/`reset` around their work.
- **Git.** Plain git, explicit paths, never `-A`. One task = one commit (code + tests + evidence).
  Commit as part of finishing a task; push only if asked. No attribution trailers.
- **Verification.** `.\scripts\verify-change.ps1 -Paths <every changed path> -Session <your id>` per
  task, plus the guards each spec names. The **full** suite runs at exactly three points: `CAI3.6`,
  `CAI4.9`, and immediately before the `CAI5.1` live probe. Do not reach for it out of caution.
- **Multi-agent work needs a charter first.** If you fan out to subagents, the owner names runtimes,
  models, budget and the stop rule **in that conversation** before any worker starts. A quota error
  stops the lane and is reported; it is never a reason to switch models.
- **The live probe (`CAI5.1`) obeys `live-probe-standard.md`.** Real endpoints, real rows, read back
  through the normal path. The injector's own telemetry is never proof of the injector.

## 7. What was decided while planning, so you do not redo it

Three spec-level contradictions were found and resolved; the plan's **Corrections** section has the
reasoning and the evidence:

1. `PerfSection` index collision — `decision-perf` takes 25/26, `lawn-cast-trigger` takes 26/27.
2. `AiTriggerBlock` is declared with **three** fields from the start, never five-then-dropped.
3. `lawn-held-actions` has **no** dependency on `profile-schema` — its spec header is stale, the map
   is right.

Plus one sequencing hazard: four tasks edit `InjectorEntityRegistry.Remove`/`Clear`. Each one's
acceptance names the drops that must already be there, so a later task cannot delete an earlier one's.

Twenty-one further defaults — taken from the specs' own "Open questions" and adopted rather than
re-decided — are in the plan's **Decisions inherited** table. If you disagree with one, that is a
change with a reason, not a fresh choice.

## 8. What is deliberately not in this program

Difficulty (its own future sub-program, D2). Vanilla PvZ unit control (D6). Player-editable AI (D4 is
inspect-only). Combo-skill content. Strategic and world AI. Balance values — every seed in this plan is
identity or `UNMEASURED`. Orders for general creatures (D7).

The todo's **Cross-program notes** section lists seven items this program found and does not own
(`base-defense`'s `spec-siege-ai.md`, the `action` program's `StanceReleaseActionId`,
`battle-engine-ssot` §4 D15's clock-sources row, `event-pipeline`'s `ChainSynthetic`, the delve's
revive action, `party-dungeon`'s `StartSession` caller, and siege's missing durable battle record).
Leave those files alone; the notes are the handoff.
