# CAI-cite-2 — `docs/research/combat-ai/**` cites files this repo deleted

Lane `cai4` (session `combat-ai-4`), 2026-09-22. Row: `tasks/combat-ai-todo.md` CAI-cite-2.
This lane's fence **does** include `docs/research/combat-ai/**`, which is what the row was waiting on
("BLOCKED on a fence decision or an exemption note"). **Remedy (a) executed** — the audit's own
sanctioned fix: every flagged line now says the file is gone, or the citation is qualified.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| D1 (file does not exist) cleared | `python scripts/audit-doc-citations.py --scope docs/research/combat-ai --summary` | **8 → 0** (0 HIGH) | 8 sites: `AUDIT.md:41`, `S1-battle-core.md:24,93,101`, `S2-delve.md:25,26,33`, `S3-siege.md:33` |
| D2 (line past end of file) cleared | same | **5 → 0** (0 HIGH) | 5 sites: `AUDIT.md:33,41,74`, `REVIEW-B.md:56`, `S1-battle-core.md:25` — all `SiegeAi.cs` ranges, which is 75 lines since CAI1.1 moved the scorer to `Actions/Ai/CandidateScorer.cs` |
| D3 (ambiguous basename) cleared | same | **1 → 0** (0 HIGH) | `REVIEW-A.md:21` — the bare `Program.cs:217-219` is now `gk-core/src/FusionRpg.Server/Program.cs:240` (re-read: `SiegeTuningPolicy.Configure` is called there) |
| Whole scope clean | same | `D1 0  D2 0  D3 0  D4 0`, 9 documents, 253 resolvable citations | — |
| Nothing else moved | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | unchanged (`D1 4 (0 HIGH)`, the `(new; does not exist yet)` specs) | — |
| Guard | `pwsh -NoProfile -File ./scripts/guard-doc-citations.ps1 -Strict` | **exit 1** — red on **7 other programs' documents** (`legion-build`, `npc-story-events`, `strain-splice-host`, `trade-network` ×3, `world-stage`) and **0 `combat-ai/` lines**. *Corrected 2026-09-22: this fragment first recorded "exit 0", which was measuring the exit of the `tail` in the pipeline rather than the guard's. The guard has been red on those other programs' docs since before this lane.* | — |

**Causes, each read rather than assumed:** `RaidIntentSource.cs` / `RaidIntentSourceTests.cs` were
deleted by combat-ai `CAI1.10` (`c284f5f6d`); `BattleStatComposerTests.cs`'s subject was fused into
`ActorHub` on 2026-09-13 (`69ba6a7b3`); `lawn-combat-ai.v1.json` was **never created** (the program took
the sibling-rejection branch and the lawn keys belong in `combat-ai.v*.json`); `SiegeAi.cs` is 75 lines
since `CAI1.1` moved the scorer and its top-three to `Actions/Ai/CandidateScorer.cs`.

**Two extra sites were annotated for consistency, not because the audit flagged them** —
`S2-delve.md:24` and `:28` name the same two deleted/shrunk files and were equally unopenable.

**Named as still owed, and deliberately NOT swept here — a distinct finding, already filed in the
Deferred section.** The *content*-level half of that Deferred bullet is now in this lane's fence and
remains open: `docs/research/combat-ai/**` cites `BasicAttack.cs:163-165`, `:152`, `:189-191`,
`:193-216`, `:489` and `TimelineDispatch.cs:79-80` at line numbers that moved in CAI1.10/CAI1.11
(`BasicAttack.cs` is 654 lines today; the fallback chain is now an `IntentRouter.Compose` call). **The
remedy there is a pre-fix note, not a re-anchor**: those lines describe the defect the program has since
closed, so bumping the numbers would claim current behaviour for a historical audit — the same refusal
`CAI-cite-1` recorded for its four self-labelled past-state sites.
