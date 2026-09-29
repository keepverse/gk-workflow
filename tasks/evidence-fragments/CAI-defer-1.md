# CAI-defer-1 — the Deferred list's conditions, measured

Lane `cai4` (session `combat-ai-4`), 2026-09-22. Filed and closed in the same session.

## Why

`tasks/combat-ai-todo.md`'s **Deferred / named follow-ups** section is where a future session looks for
known-owed work. Most of its entries carry a **condition** rather than a date — *"once a second non-table
consumer exists"*, *"if it reaches eight members"*, *"next lane: decide whether … or …"* — and a condition
is exactly the kind of claim that goes stale while the heading still reads as owed. Four entries were
therefore **measured rather than re-read**, and each now carries a dated verdict.

| Entry | Condition | Measured 2026-09-22 |
|---|---|---|
| Rename `ContentHashStamp.TableDigests` to `PartDigests` | *once a second non-table consumer exists* | **MET, and filed elsewhere.** `CombatAiProfileIdentity` (`CAI2.1`) is that consumer: `StampOf` builds `new ContentHashStamp(…, digests)` where the map is keyed by **profile id** (`"siege/default"`), at `gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiProfileIdentity.cs:67`. `effect-atom` owns the rename and has it open with three options (`tasks/effect-atom-todo.md:642`). Nothing for a combat-ai session to do — recorded so the next one neither re-derives the condition nor reaches into another program's file |
| `CAI2.4`'s missing `AiCandidateVerdict.Gate`, "next lane: … **or** the sink is threaded through the router as its own task" | is the router carrying a sink still a task? | **the second option is already carried out** — `IntentRouter.Compose` takes `IAiDecisionSink? sink` and wraps the policy in `AiDecisionRecordingSource` (`gk-core/src/FusionRpg.Core/Actions/IntentRouter.cs:77,86-88`). What the entry is actually about still stands: there is no honest per-candidate `UsabilityResult` in the **siege** path, and the spec forbids obtaining one by re-running the gates a tick later — so the open item is the **erratum**, not the wire |
| The doc-citation re-anchoring entry (`CAI1.11`/`CAI1.12` code moves) | is any of this program's own half still owed? | **the combat-ai half is DONE.** `CAI-cite-1` re-anchored 39 citations across 12 specs; `CAI-cite-2`/`CAI-cite-3` closed this program's two doc trees, so both scopes audit at `D1 0, D2 0, D3 0, D4 0` and the survey tree's content sites carry dated pre-fix notes. What remains of the entry is the **other programs'** documents it lists, which are theirs |
| Fold `AiRowCondition`'s fact half into `ICompiledPredicate` | *if it reaches eight members* | **NOT met — it is 6.** Pinned by its own test, which states the same trigger on its own line (`AiRowCondition_has_six`). No action |

Every other entry in the section was read and **remains owed** as written (the `gk-forge/tools/DominanceBaseline`
run; `CAI2.1`'s Data/Server thirds; `CAI1.14`'s `PerfProbe` residue; D7's general-creature orders; the
difficulty lever; the economy-carrying dominance variant; the real divergent-loadout golden fixture; the
lawn "now" accessor; `RendezvousLane`; and `CAI-guard-1`, whose executor note is its own record).

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| Each measured verdict is dated and evidence-bearing | `grep -n "MEASURED 2026-09-22" tasks/combat-ai-todo.md` | **4** annotations, each naming the file, line or task it rests on |
| The two verify-able conditions were checked in code, not recalled | `grep -rn "TableDigests" gk-core/src/FusionRpg.Core/Actions/Ai/`; `grep -n "sink" gk-core/src/FusionRpg.Core/Actions/IntentRouter.cs` | `CombatAiProfileIdentity.cs:67`; `IntentRouter.cs:77,86-88` |
| The non-membership claim uses the pinned contract, not a hand count | `grep -n "AiRowCondition_has_six" -A 3 tests/…/CombatAiTuningTests.cs` | `Assert.Equal(6, Enum.GetValues(typeof(AiRowCondition)).Length)` — the count is pinned by the closed vocabulary's own test |
| No code, test or tuning file touched | `git diff` | docs only |

One cross-program item is named rather than filed: the `ContentHashStamp` rename belongs to `effect-atom`,
whose todo is not in this lane's fence — so it is routed here by reference, with its own row number.
