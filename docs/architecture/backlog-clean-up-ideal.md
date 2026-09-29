# Backlog clean-up — the ideal

**Status:** idea phase, 2026-09-20. It feeds [backlog-clean-up-map.md](backlog-clean-up-map.md), which
the owner approved on 2026-09-20.
**Evidence:** [program-pipeline-audit-2026-09-20.md](program-pipeline-audit-2026-09-20.md) (revision 3)
and the eight lane reports under [../research/backlog-clean-up/](../research/backlog-clean-up/README.md).
Every claim below that names a file or commit is cited there.

---

## 1. The problem, measured

The repo writes an idea, then a map and specs, then a plan and todo, and then builds. Between
2026-08-21 and 2026-09-19 that chain broke in four repeatable ways. None of them is a code defect. They
are all failures of **ownership after hand-off**.

| Cause | What happens | Measured instances |
|---|---|---|
| **C1. Specified, then left out of the next round** | A program is specced days before a large round (convergence, 2026-09-18) that does not include it. Its map names plan files that are never written. | `lawn-playable`, `lawn-tuning-profile`, `effect-pipeline` (12 specs), `deployment-hierarchy` remainder, both 2026-09-16 audits' remainder |
| **C2. A human gate nobody clears** | A task waits on "owner review", and the whole sequence behind it stops. | `backlog-clear` BP1 (since 2026-08-31) blocking Phases 2 and 5, the AU and GG items, and actor-hud optionals. About 47 owner-gated rows outside convergence |
| **C3. Built in slices by other programs** | Program B builds the slice of program A it needs, then says "A's own eventual plan" owns the rest. A never gets that plan. | `deployment-hierarchy`, whose modules 3–6 were built by `empire-development` and module 7 by `species-gear-chain` |
| **C4. Absorbed without a pointer** | A later program does the work but never cites the earlier plan, so the earlier plan reads "unbuilt" forever. | `solid-remediation` ← `battle-derived-wire` / `combat-math-dedup`; the perf pass ← `lawn-playable`; `party-dungeon` ← battle-timeline B22; `species-gear-chain` ← item module 23 |

**Paperwork drift** compounds all four: completion is recorded in a header, ledger or merged session,
and the checkboxes stay empty. The lanes found ten or more fully built programs reading as 0% done.
That noise hides the real gaps. A reader cannot tell "rift-gate, 0/134" (done) from
"lawn-tuning-profile, no plan" (nothing built).

## 2. What this program is

**A one-pass reconciliation that leaves every forgotten item with exactly one of three outcomes:**

1. **Closed with a pointer.** The item is built, superseded or obsolete. Its todo or spec says so, and
   names the commit, program or ruling that closed it.
2. **Owned and scheduled.** A still-wanted item gets a home: a plan pair of its own, a task in a live
   plan, or a module of this program. It has dependencies and verification like any other task.
3. **Put to the owner once, in one packet.** Only what is genuinely the owner's goes here: a live visual
   judgement, a model-calling corpus run, a product or balance decision not already ruled, or the scope
   of R28. Each question carries a default.

It is **not** a new feature program and invents no mechanics. Every piece of build work it schedules
already has a spec or a named audit row. Where a spec is missing (for example `lawn-combat-baseline`),
the task is to *write that spec* in its owning program, not to design it here.

## 3. Principles (each learned from this audit)

1. **Code beats checkboxes.** A box is ticked only against evidence: a commit, a file, or a test name.
   A box is closed as superseded or obsolete only with a pointer. This applies the repo's "code beats
   docs" rule to the todo files themselves.
2. **One owner per remaining item.** When two todos track one defect, one row keeps it and the other
   points to that row. Duplicates found: `lawn-combat-wire` L-N26 = `live-probe` Task 17; `live-probe`
   Task 22 = `summon-pool-integrity`; `battle-derived-wire` W16 = `class-system` P9.0 readers.
3. **Absorbing work means writing the pointer.** When a program builds another program's module, it
   edits that program's todo or map in the same change. That is the C3/C4 fix going forward, and
   `pipeline-audit-v2` checks it.
4. **Respect the convergence boundary.** This program never edits a convergence program's files; those
   belong to their active lane sessions. It routes through cross-program notes and waits for their hard
   edges. The one live collision it must prevent is the `PUT /api/players/current` notice: `SP6.6` owns
   it, and `actor-liveness-refresh` extends it and never duplicates it.
5. **No hand-edited generated data.** Every content fix in scope is a generator change plus
   regeneration, for example the naming-grammar pass in `seedsmith-generated-seed-repair`.
6. **Gates must be answerable.** Every owner question in the decision packet has a named default the
   work ships behind. Nothing waits silently for months again, as BP1 has since 2026-08-31.

## 4. The shape of the remaining work

The lanes sorted everything open outside convergence into four piles.

| Pile | What it holds | Where it goes |
|---|---|---|
| **Paperwork** | Stale boxes, headers and gate lines; dead session-fence citations; duplicate rows. About 30 files. | Module `paperwork-reconcile`: pure doc edits with pointers, no code |
| **Real engineering, never planned** | The lawn pair; the `deployment-hierarchy` remainder; the battle-wire remainder; `effect-pipeline`; aura close-out; creature, world, item and UI remainders; infra leftovers | Modules that write plan pairs (orphan programs) or add tasks to this program's todo (small remainders) |
| **Owner-only** | Live visual gates; model-calling corpus runs; balance passes; product calls; the R28 scope; the `rider-default-on` scale debt | Module `owner-decision-batch`: one packet, each item with a default |
| **Superseded or obsolete** | loam L44–L50 (L47–L49 retired twice); roster-balance RB1–RB6; four trailed actor-sheet specs; item D39 `Override`; verification-boundaries follow-ons → `test-verification-boundary` | Closed in `paperwork-reconcile` with pointers |

## 5. Why a program and not a chore list

The same drift will recur unless the pipeline can see it. The first pass of this audit was itself wrong
four times: it matched spec names against code names, trusted checkboxes, missed blockquote status
headers, and matched a tool path. `gk-core/scripts/audit-program-pipeline.py` reads only the document chain. A
program keeps the lessons as **tooling**, not memory:

- header-status parsing, including blockquote banners;
- ledger and merged-session awareness;
- a check that a todo header claiming completion has no unticked boxes;
- a check that "built by program X" pulls leave a pointer in the owning map.

That is module `pipeline-audit-v2`.

## 6. Out of scope

- Anything inside the 11 convergence programs, except reading them to route or deduplicate.
- New mechanics. The six `war-feedback` proposals stay an idea backlog. They get `/idea` only if the
  owner promotes them, through the decision packet.
- `identity-rename` and `ip-censor`. Both are new (2026-09-19), awaiting their own approval, and are
  not drift.
- `keepverse-split`, which is active and blocked on `features/mega-merge` → `main`, not stalled.
- The 2026-09-19 spec round (trade-network, world-continuity, legion-build, empire-seed,
  narrative-seed, npc-story-events). Those are fresh specs waiting for their own plans. This program
  only records their plan-file naming inconsistency for the owner.
