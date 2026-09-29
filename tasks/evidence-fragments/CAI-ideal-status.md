# `CAI-ideal-status` — the ideal's "Built" table claimed things this program has since moved or deleted

Lane `combat-ai-3`, 2026-09-21. `docs/architecture/combat-ai-ideal.md` is the document `DESIGN-GATE.md` §1
sends every agent to before proposing anything in this subsystem, and it is in this lane's fence. Section 4.1
is titled **"What already exists: built"** — present tense — while §4.2/§4.3 are gap lists. Nine waves later,
several rows are false.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| §4.1's scorer row named a class that no longer exists | `grep -rn "class AiScoring" --include=*.cs src/ tests/ tools/`; `wc -l gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs` | **no such class**; `SiegeAi.cs` is **75 lines**, while the row cited `maxCandidatesScored` at `:135`. The scorer is `Actions/Ai/CandidateScorer.cs` (**CAI1.1**) and the ten weights are at `gk-core/data/tuning/combat-ai.v1.json` `profiles["siege/default"].scoring` (**CAI1.8**, H7) — verified to be the **same ten values** (70/50/15/10/10/1/120), so only the address was stale | — |
| §4.1's retarget row named a file region that no longer holds it | `find src -name RetargetLedger.cs`; `sed -n '316p;351p' …/SiegeAiIntentSource.cs` | the type is at **`Actions/Ai/RetargetLedger.cs`** (**CAI1.4**); the cited `SiegeAiIntentSource.cs:316-351` is now a decision-record comment | — |
| §4.1's selection-chain row cited a superseded expression and an open gap that is closed | `sed -n '175,177p' gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs` | the chain is `IntentRouter.Compose(policy: …, fallback: …)` at **`:175-177`** (**CAI1.10**), not the inline `intentSource ?? … ?? new StubIntentSource(…)` it quoted from `:163-165`, and the reselect gap it pointed at is closed | — |
| §4.2 claimed traits reach only the stub | `sed -n '79,86p' gk-core/src/FusionRpg.Core/Battle/TimelineDispatch.cs`; `grep -n "ITraitDecorator" gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs` | both sites compose the router with `decorators: new ITraitDecorator[] { new LoyalTargetRedirect(state, now) }` — **CLOSED by CAI1.11**, and the reselect site's own comment records CAI1.10's fix textually | — |
| §4.2 claimed aggression is siege-only | `grep -n "AggressionOf" gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs` | **`:416`** reads `_view.AggressionOf(candidateKey)` — **CLOSED by CAI1.9** (CAI1.13 made the map saturating) | — |
| §4.3 said no per-place resolvable filter exists | `grep -rn "interface IDeclaresExecution" --include=*.cs src/` | **`Effects/EffectModels.cs:139`** — **CLOSED by CAI1.12** | — |
| §4.3 said nothing expresses a policy as data | `ls gk-core/data/tuning/combat-ai.v1.json`; `grep -c "record CombatAiProfile" …/CombatAiProfile.cs` | present, one record — **CLOSED by CAI1.6 + CAI1.8** | — |
| §4.3 said no lawn `IBattleView` exists | `ls gk-core/src/FusionRpg.Core/Actions/Ai/Lawn/` | `LawnBattleView.cs`, `LawnDerivedCache.cs`, `LawnRelationChain.cs` — **CORE HALF CLOSED by CAI4.1**; its injector host is out of every combat-ai lane's fence | — |
| Every new anchor holds what the text claims | python slice of six ranges | **6 of 6 OK**: `BasicAttack.cs:175`, `TimelineDispatch.cs:81`, `CoreIntentPolicy.cs:416`, `EffectModels.cs:139`, `CandidateScorer.cs:132`, `RetargetLedger.cs:21` | — |
| The doc guards stayed clean | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary`; `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | scope unchanged (`D1 7 (0 HIGH)`, `D2 0`, `D3 0`, `D4 0`); repo-wide strict guard still exits 1 on **other** programs' docs with **0** lines mentioning `combat-ai/` | — |

## What was changed, and the convention it follows

Three §4.1 rows now name the **new home** and credit the task that moved it. That is not a new convention
invented here: §4.2's *Two identical routers* row already reads *"Both deleted 2026-09-20 (combat-ai
`intent-router`, CAI1.10) … One shared router — done"*, and §4.1's own *Delve profile and routing* row already
records `RaidIntentSource.cs`'s deletion by CAI1.10. So the document was already the kind that says where a
thing went; three rows simply had not been updated.

§4.2 and §4.3 each gained a **dated status block** ahead of their table, listing which gaps are closed (four in
§4.2, two in §4.3) and which are **half** closed (*Stance gate 0* by CAI3.1; *A lawn `IBattleView`* by CAI4.1),
with the still-open ones pointed at `tasks/combat-ai-todo.md`. The original finding rows are **left as written**
— they were correct when the spec was authored and they are this program's own brief; rewriting them would
destroy the record of what the design phase found.

## Not proved

- **Not every §4.1 row was re-verified** — only the three that name a moved or deleted thing were read against
  code. Rows still citing `IntentSource.cs:29-37`, `ActionTagPreference.cs:16-60`, `FrozenActionSet.cs:18-46`,
  `CooldownLedger.cs:29-106`, `StubIntentSource.cs:27-97`, `InteractiveIntentSource.cs:30-154`,
  `RendezvousLane.cs:1-44` and `EventDrain.cs:631` are **bounds-clean** (the audit reports no D2), but a
  bounds-clean citation can still name the wrong symbol, which is the class `CAI-cite-1` spent 39 fixes on.
- **The §4.2/§4.3 status blocks assert closures, not the reverse.** I checked that each closed gap's mechanism
  exists in code; I did **not** re-audit the rows I left as "open" to confirm they are still open beyond what
  the todo's own rows say (e.g. *Combo skills* and *Exhaustion has no producer* were not re-measured).
- **No behaviour changed.** This is documentation only; no test or guard was run against a production path.

---

## Follow-up: the rows I left as "open" were checked too (they were the fragment's weakest claim)

The first commit said the rows I left as *open* "were not re-measured beyond what the todo's own rows say".
That was the weakest part of the claim, so four of them were measured directly:

| Row left open | Command | Result |
|---|---|---|
| *Exhaustion has no producer* | `grep -rn "new ExhaustionPolicy" --include=*.cs src/` | **NONE** — claim holds |
| *The lawn never calls the decision stack* (the row claims **zero** injector hits for `IIntentSource \| ActionIntent \| FrozenActionSet \| IBattleView`) | `grep -rlE "IIntentSource\|ActionIntent\|FrozenActionSet\|IBattleView" --include=*.cs gk-fusion/src/FusionRpg.Injector/ \| wc -l` | **0 files** — claim holds, and this is the one most likely to have moved in wave 4 |
| *Combo skills* (no decision-side proposer) | `grep -rln "RendezvousLane" --include=*.cs gk-core/src/FusionRpg.Core/Actions/ gk-fusion/src/FusionRpg.Injector/` | **no hit** outside `Battle/Timeline` — claim holds |
| *Lawn swing counter* (only the per-swing dedupe exists, not a per-actor count) | `grep -rn "SwingBump" --include=*.cs src/ \| wc -l`; per-actor-counter grep in the injector | `SwingBump` still **3** sites (a consumed-and-released dedupe) and **no** per-actor counter in the injector — claim holds |

So the status blocks' "open" column is measured for four of the six §4.2 rows I left open and two of the
four §4.3 rows; the remainder are the ones whose closure would require an out-of-fence file and which the
todo's own blocked rows already track. The original "Not proved" note above is narrowed, not withdrawn:
*Combo skills*'s *decision-side* absence is confirmed, but the four remaining open §4.2/§4.3 rows were still
not each re-derived.
