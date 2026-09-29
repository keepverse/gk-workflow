# Lane `arch-d` — architect: verify and reconcile the D-row plans, clear their open questions

**Session:** `arch-d-20260922` · **Program:** cross-program architect · **Mode:** worktree
**Fence:** `tasks/**`, `docs/architecture/**` — **documents only. No product code, no test edits.**

## Role

You are the ARCHITECT at max effort. The owner's ruling 2026-09-22: the plans below were already
approved for implementation; your job is to **verify and reconcile them against the current tree**
(`features/mega-merge` head, post the 2026-09-22 convergence merges) and **clear remaining open
questions**, NOT to rewrite approved plans. Where a plan is stale, write a dated addendum naming the
drift; where a question is answerable from code or an existing owner ruling, answer it and cite the
source; where it genuinely needs the owner, list it as an Open Question for the manager to relay.

## The three programs

1. **identity-rename** — `tasks/identity-rename-plan.md` + `identity-rename-todo.md` (19 tasks,
   5 checkpoints; G1 answered 2026-09-19: no save-name migration). Status line says "awaiting owner
   approval" — the owner has now approved deployment. Verify the plan's premises still hold (the
   2026-09-19 audit fixed B1; check nothing else rotted), then update the status line to
   "approved 2026-09-22, ready for lanes" if clean.
2. **ip-censor** — `tasks/ip-censor-plan.md` + `ip-censor-todo.md` (25 tasks, 7 checkpoints; G1
   answered yes 2026-09-19). Same treatment: verify premises, update status.
3. **npc-story-events** — `tasks/npc-story-events-plan.md` + `npc-story-events-todo.md` (94 tasks,
   6 checkpoints, PG1–PG3 irreversible-action gates). Phase 7 (`storylet-card`, `quest-log-layer`)
   is blocked on `/idea-ui` with no task. Your added deliverable: **write the idea-ui task** — an
   idea/spec entry point for the Phase 7 UI surfaces following the repo's idea conventions
   (read `.claude/skills/idea-phase/SKILL.md` and an existing idea doc for the shape), so Phase 7
   has its entry task. Do NOT design the UI itself; produce the idea entry point with Open Questions
   for the owner.

## Also reconcile (secondary, time-boxed)

4. **Backlog-clear §3.3/§10.1** (`tasks/backlog-clear-todo.md`): the spec's open owner question —
   do bindings become the SSOT for aura activation (recommended), or does activation get its own
   table? The owner asked: "did they contradict? if not why don't we follow the original spec?"
   Read the spec (`docs/architecture/aura-skill/spec-aura-binding-producer.md` §3.3, §10.1) and
   BP2/BP3's landed evidence. Determine: does the landed code contradict the spec's recommendation?
   If not, the answer is "follow the original spec (bindings as SSOT)" — record that as a
   recommendation with evidence, flagged for owner confirmation, and do not implement.
5. **Live-probe freeze** (lawn-playable program): the owner asked whether deployment scope is
   complete (general creature/unit, specimen, lawn, actor layer, empire progression). A scope scout
   has already produced this register (2026-09-22, read-only):
   - creature-seed species-rank: 1/13 done, GAP-4 open, RB-H1/TB-H1/TB-H2 open (TB-H1 blocks
     party-dungeon F1)
   - lawn: Phases 1–3 done (deploy/events/zomboss-ai, checkpoints closed 2026-09-07); Phase 4
     progression conformance PARTIAL (T4.1–T4.3), T4.4 TODO, Checkpoint 4 open
   - action/specimen: Phases 0–13 done, Phase 14 mostly done (T62–T70); 12 unchecked lines
     (Checkpoints M/N/O/Q, T71–T73, final gates); Checkpoint Q blocked on T71/T72
   - deployment-hierarchy: 0/13 tasks, Wave 1 not started; DH-B1 (injector build collision) blocks
     injector-facing verification repo-wide
   - empire-progression: Waves A/B/D substantially closed; ~8 unchecked lines (CP1 suite line,
     CP3, CP4, EP5.3 deferred, one denied-path row)
   Fold this register into a short **deployment-scope status doc** at
   `tasks/reports/deployment-scope-status-20260922.md` with your own verification of the counts and
   a sequenced recommendation: what order the remaining lanes should close these gaps in, and which
   gaps gate "playable" (the owner's bar: creature/unit + specimen + lawn + actor layer + empire
   progression all complete). Do not tick any todo row.

## Definition of done

- Per program 1–3: a dated addendum (or a clean bill) recording premise verification and the
  updated status line; npc-story-events gets its Phase 7 idea-ui entry task.
- Item 4: the §3.3/§10.1 answer with evidence, flagged for owner confirmation.
- Item 5: `tasks/reports/deployment-scope-status-20260922.md` written.
- All open questions that need the owner, collected in ONE list at the end of your report for the
  manager to relay.

## Verification

- `.\scripts\verify-change.ps1 -Paths <every file you changed> -Session arch-d-20260922` — expected: exit 0

## Rules that bite here

- Documents only — no product code, no test edits, no scripts.
- Never tick a todo row on the architect's own authority; recommendations only.
- Cite file:line for every claim; a comment is not evidence.
- Explicit `git add <paths>`, never `-A`; never push.

## Hand-back

- If a plan's premise is badly rotted (not just stale), stop and report it as a finding instead of
  writing an addendum that papers over it.
