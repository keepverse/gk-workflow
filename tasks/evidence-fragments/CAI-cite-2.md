# `CAI-cite-2` — `docs/research/combat-ai/**` cites two files this repo deleted, and no lane holds the path

Found while attributing the CI tier's `doc-citations` red: the repo-wide `D1` list has 15 entries whose path
contains `combat-ai`, seven in `docs/architecture/combat-ai/**` (already classified LOW "proposed file" and
in fence) and **eight in `docs/research/combat-ai/**`**, which no combat-ai lane's fence includes.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The eight, with refs and severity | python `audit('docs/')` filtered to `research/combat-ai` | `AUDIT.md:41` `RaidIntentSource.cs:42-43` · `S1-battle-core.md:24` `RaidIntentSource.cs:29-51` · `S1-battle-core.md:101` `src/FusionRpg.Core/Delve/Battle/RaidIntentSource.cs` · `S2-delve.md:25` `RaidIntentSource.cs:49-50` · `S2-delve.md:26` `tests/…/RaidIntentSourceTests.cs:103-112` · `S2-delve.md:33` `RaidIntentSourceTests.cs:38-61` · `S3-siege.md:33` `BattleStatComposerTests.cs` · `S1-battle-core.md:93` `lawn-combat-ai.v1.json`. **All LOW**, because `docs/research/` is a prior-art scope in the audit's severity rule | — |
| Six of them name a file **this program deleted** | `git log --oneline --diff-filter=D -1 -- src/FusionRpg.Core/Delve/Battle/RaidIntentSource.cs` (and the tests path) | both deleted by **`c284f5f6d`** — *"combat-ai CAI1.10: the router, cause A -- one chain, two routers deleted"*. `git ls-files \| grep -i RaidIntentSource` → **NONE tracked** | — |
| One names a file another program deleted | `git log --oneline --diff-filter=D -1 -- tests/FusionRpg.Core.Tests/Battle/BattleStatComposerTests.cs` | deleted by **`3689f35b1`** (actor-hub Wave 1a + T5). `git ls-files \| grep -i BattleStatComposer` → **NONE tracked** — and `BattleStatComposer` is the closed incident the repo's own rules say never to copy | — |
| One names something never created | `git ls-files \| grep lawn-combat-ai.v1.json` | absent; the Deferred/plan record it as the **rejected** alternative to putting the lawn keys in `combat-ai.v1.json` | — |
| Why they have stayed invisible | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | the repo-wide guard reports the notify-rail findings in **other** programs' docs and **0** lines mentioning `combat-ai/` — the audit routes `docs/research/**` to LOW, and the CI gate keys on HIGH | — |

## What is actually wrong, and what is not

These are **historical survey documents** (`S1`–`S3`, `AUDIT.md` — the pre-implementation inputs to BCU2.9),
so citing `RaidIntentSource.cs` was correct *when written*: the type existed then and this program deleted it
in `CAI1.10`. That is the same shape as the four self-labelled past-state sites `CAI-cite-1` refused —
**except** that these lines do not say the file is gone, and the audit's own remedy is exactly *"Fix the
citation, or say on that line that the file is gone"*. So the honest options are:

1. **Add the exemption note on the line** — `deleted by CAI1.10 (c284f5f6d)` for the six raid refs and
   `deleted by 3689f35b1` for `BattleStatComposerTests.cs`. That is the audit's sanctioned fix, and it costs
   seven short edits.
2. **Re-point the raid refs** to what replaced them (`Actions/IntentRouter.cs`, and the ported tests
   `Actions/IntentRouterTests.cs`) — truer for a reader, but it edits the survey's *findings* rather than its
   citations, which is a content decision for whoever owns the document.

Either way the path is **out of every combat-ai lane's fence** (`docs/research/combat-ai/**` is not in the
allowed set), which is why this is filed rather than executed — and why the Deferred paragraph has said for
two days that it "needs a routing decision, not a guard fix". This row is that decision, sized.

## Not proved

- **The other `S1`–`S5`/`REVIEW-*`/`AUDIT.md` citations were not swept.** Only the eight the audit reports
  were read; a symbol-level check of those documents is not attempted here, and they are a plausible home for
  more of the same.
- **Nothing in `docs/research/combat-ai/**` was changed** — out of fence.
- **The audit's LOW severity is not disputed.** Whether the repo *wants* these fixed is a judgement: a survey
  that cites the state it surveyed is arguably correct as-is, and the cheap fix is the exemption note.

---

## Completion — the scope is 14 findings, not 8 (measured before this row shipped, added after)

The first commit reported only the `D1` class. Re-running the summary for the same scope gives
**`D1` 8 · `D2` 5 · `D3` 1 · `D4` 0**, all LOW, and the extra twelve are the same "cannot be opened or
resolved" class:

| Class | Refs | Why |
|---|---|---|
| `D2` × 5 | `SiegeAi.cs:135` (`AUDIT.md:33`), `:220-239` (`AUDIT.md:41`), `:96-103` (`AUDIT.md:74`), `:145-195` (`REVIEW-B.md:56`), `:220-239` (`S1-battle-core.md:25`) | `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs` is now **75 lines** — `CAI1.1` moved the scorer out of it into `Actions/Ai/CandidateScorer.cs`. Every one of those line ranges is **past the end of the file it names**, so the `AiScoring` members they point at no longer live there at all |
| `D3` × 1 | `Program.cs:217-219` (`REVIEW-A.md:21`) | **42 files** share the basename `Program.cs`, so the line number cannot be checked. The audit's own wording: *"cite a path, not a bare basename, so the line number can be checked"* |

**Sized total for `CAI-cite-2`: 14 LOW findings (8 D1 + 5 D2 + 1 D3) across 5 documents, from three causes** —
a type this program deleted (`RaidIntentSource`, `CAI1.10`), a type another program deleted
(`BattleStatComposerTests`, `3689f35b1`), and one file this program **shrank** (`SiegeAi.cs`, `CAI1.1`).
None of the causes is a defect in the docs; each is a doc that was right when written. What is missing is the
one-line note the audit exempts, on a path no combat-ai lane holds.
