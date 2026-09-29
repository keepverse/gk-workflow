# Independent review — combat-ai spec batch B

Reviewer: independent agent, read-only, standing in for owner approval (owner ruling). Repo
`D:\Works\source\plant-vs-zombie-rise-of-summoner`, branch `features/mega-merge`. Date 2026-09-20.

Scope: the 9 `docs/architecture/combat-ai/` specs named below, plus the 3 cross-program specs
(`creature-lawn-deploy/spec-unique-deploy-cap.md`, `lawn-tuning-profile/spec-lawn-combat-baseline.md`,
`lawn-tuning-profile/spec-zombie-power-source.md`), checked against `combat-ai-map.md` (approved),
`combat-ai-ideal.md` rev 3 (D1–D6 binding), `docs/research/combat-ai/AUDIT.md`,
`overlay-control-loops.md` §3/§6/§7, `battle-engine-ssot.md` §3c/§5, `lawn-playable/spec-actor-liveness-refresh.md`,
CLAUDE.md hard rules, and DESIGN-GATE §5/§2.16.

Method: grounding documents read in full by the reviewer; the four Wave-2/3 turn-mode specs and
`lawn-actor-view` were read and citation-verified directly by the reviewer against source; the four
Wave-4 lawn specs (16–19) and the three cross-program specs were read and citation-verified by two
parallel sub-investigations, whose file:line findings were independently spot-checked by the reviewer
before being folded in here. Every citation reported as PASS below was opened in this session — the
repo, not the spec's own prose, is the source of truth.

---

## 1. Verdicts

| Spec | Module | Verdict |
|---|---|---|
| `spec-replay-identity.md` | 8 | **Sound.** No changes required. |
| `spec-action-schedule-twin.md` | 9 | **Sound.** No changes required. |
| `spec-decision-inspector.md` | 10 | **Sound.** No changes required. |
| `spec-auto-policy-switch.md` | 14 | **Sound.** No changes required. |
| `spec-lawn-actor-view.md` | 15 | **Sound, one required change** (folder/guard-scope tension, §3.1). |
| `spec-lawn-held-actions.md` | 16 | **Sound.** No changes required. |
| `spec-lawn-cost-authority.md` | 17 | **Sound, one required change** (upstream doc-status mismatch, §3.5). |
| `spec-lawn-cast-activation.md` | 18 | **Sound.** No changes required. |
| `spec-lawn-cast-trigger.md` | 19 | **Sound, one required change** (tunable-vs-structural cap placement, §3.2). |
| `creature-lawn-deploy/spec-unique-deploy-cap.md` | cross-program | **Sound.** One terminology fix owed upstream (§3.4), not to this spec. |
| `lawn-tuning-profile/spec-lawn-combat-baseline.md` | cross-program | **Sound.** No changes required. |
| `lawn-tuning-profile/spec-zombie-power-source.md` | cross-program | **Sound.** Best-in-batch on §2.16 cache-trigger discipline; also self-corrects a stale claim in the map/ideal (M5), verified. |

**Headline:** this is an unusually high-quality batch. No spec invents a second scorer, a second
composer, a private fold, a fabricated debug result, or a silently-pinned population count. No two
specs claim ownership of the same number or mechanism. The defects found are three concrete,
fixable items (below) plus a handful of citation line-drifts of 1–5 lines that do not change any
claim's truth value — those are listed but not counted as required changes.

---

## 2. Citation verification (requirement: ≥4 load-bearing citations per spec, opened directly)

All citations below were opened against the real files in this session (not trusted from the spec
or from the sub-investigations' say-so where the reviewer re-checked directly).

| Spec | Citations opened | Result |
|---|---|---|
| replay-identity | `WebMatchService.cs:125-128`, `RpgStore.ContentHash.cs:18-56`, `DecisionTrace.cs:1-20`, `RpgStore.cs:800-822` (`profile_id` precedent), `ContentHashStamp.cs:14-66` | All exact. `RpgStore.cs` comment structure for `profile_id`/`environment_stamp` matches verbatim. |
| action-schedule-twin | `ActionSchedule.cs:1-30,95-115`, `Predictor.cs:20-45,68-90`, `DominanceGuard.cs:55-70` (line 64), `TerminationGuard.cs:95-105` (line 100) | All exact, including the decisive finding that both guards call the **two-argument** `Predictor.Predict(a,b)` overload (`economy: null`), which is the whole basis for "the dominance baseline does not move." |
| decision-inspector | `BattleTrace.cs:105-130` (incl. `_lines`/`_aiDecisions` split), `SiegeAiIntentSource.cs:265-280`, `SiegeAi.cs:145-195` (pre-CAI1.1 — that scorer no longer exists there; it is `Actions/Ai/CandidateScorer.cs`, and `SiegeAi.cs` is 75 lines today), `CombatDebugObservability.cs:1-53` | All exact, several to the exact comment wording the spec quotes. |
| auto-policy-switch | `BattleModels.cs:260-286` (`RulesetVersion=5`, v4/v5 doc history), `BasicAttack.cs:158-167`, `TimelineDispatch.cs:73-82` | Exact as reviewed, but **the two fallback-chain citations are PRE-FIX line numbers**: `CAI1.10`/`CAI1.11` replaced that chain at both sites with the one `IntentRouter.Compose` call, so `BasicAttack.cs:163-165` and `TimelineDispatch.cs:79-80` no longer hold it. |
| lawn-actor-view | `IBattleView.cs` (10-member contract), `ILawnBoardView.cs:1-70`, `BoardSnapshot.cs:1-25`, `ILawnBoardViewTests.cs` (the guard test) | Substantively correct; `ILawnUnitView`/`ILawnBoardView` interface line numbers drift by ~4-5 lines (cosmetic). One real finding: the guard test's actual class is `ILawnBoardViewTests`, not `ZombossDeployAiGuardTests` as the spec's own design-gate checklist names it — that wrong name is **inherited from a stale comment already inside the shipped `ILawnBoardView.cs` source** (not invented by the spec), but the spec repeats it uncritically. See §3.1 for the substantive issue this citation touches. |
| lawn-held-actions | `LawnBasicAttackRow.cs:31`, `BattleRunState.cs:226,540-596,873-882`, `ActionSetAssembler.cs:41-45`/`FrozenActionSet.cs:26-45`, `InjectorEntityRegistry.cs:129-157` | All match (sub-investigation, spot-checked). |
| lawn-cost-authority | `LawnBasicAttackCostCharger.cs:97-106`, `BattleRunState.cs:601-619,671-684`, `CostLedger.cs:148-156`, `gk-core/data/tuning/action-rungs.v4.json` (`cap:10`) | All match, `BattleRunState.cs:671-684` reported as a character-for-character match. |
| lawn-cast-activation | `BasicAttack.cs:193-216` (**PRE-FIX**: the `OnActivate` raise moved to `:215-232` when `CAI1.11` rebuilt the fallback chain), `EventDrain.cs:118-146`, `GameEventRec.cs:12` (`ChainSynthetic=6`), `EffectDtos.cs:226` | All match, one quoted verbatim. |
| lawn-cast-trigger | `PerfProbe.cs` (25 sections, `LawnMoveDrain=24`/`SectionCount=25`), `EventDrain.cs:110-146`, `KernelDriveHost.cs:54-56`, `LawnBasicAttackFeature.cs:9-61` | All match; `KernelDriveHost.cs:107,174-176` drifts 1-3 lines from the real `NowTicks`/pause-guard locations (cosmetic). |
| unique-deploy-cap | `RpgStore.UniqueActors.cs:150-250`, `ZombossDeployPolicy.cs:60-70`, `ContractPolicy.cs:171`, `KernelDriveHost.cs:54-56` | All match. |
| lawn-combat-baseline | `BattleBaselineSubsystem.cs:20,40-48`, `BattleHubCompose.cs:81`, `ActorHub.cs:141-182`, `BattleModels.cs:367-370`, `DerivedStatRegistry.cs:298-311` | All match. Minor: spec says "four" optional Hub delegates, code has six — cosmetic miscount. |
| zombie-power-source | `SpeciesAllocationSource.cs:22-25,36,106,114-124`, `RpgStore.Aptitudes.cs:224-233`, `ZombossCommanderAllocation.cs:9-61`, `WebMatchService.cs:488-510` | All match; `SpeciesAllocationSource.cs:36` is off by one (field is at 37). |

**No fabricated symbol, wrong file, or content mismatch was found anywhere in the batch.** Every
line-number discrepancy found was 1–5 lines and did not change whether the cited claim is true.

---

## 3. Required changes

### 3.1 `spec-lawn-actor-view.md` — folder/guard-scope conflict with `Match/Ai`'s narrow-view invariant

The spec places three new files — `LawnBattleView.cs`, `LawnRelationChain.cs`, `LawnDerivedCache.cs`
— in `gk-core/src/FusionRpg.Core/Match/Ai/`. That folder already carries a **compile-time-enforced narrowness
invariant** built for a different consumer: `ILawnBoardView`'s own doc comment says it is *"the ONLY
thing the Zomboss scorer (T3.3) may read... deliberately narrow: wave, visible units, HP — nothing
else... until a real policy build proves it needs more,"* and `ILawnBoardViewTests.Nothing_under_
Match_Ai_may_read_the_board_itself` (verified, exists, passes today) scans every `.cs` file under that
folder for the literal strings `MatchRuntime`, `MatchSnapshot`, `: Board`, `(Board `, ` Board.` and
fails the build if any appear — precisely so nothing under `Match/Ai` can read a full board census.

`LawnBattleView`'s own design (per its "Answering all ten members" table) reads `BoardSnapshot`
(`Combat/BoardSnapshot.cs`) directly for `PositionOf`/`FactsOf` (Row, Col, TypeId, MindControlled) —
a richer census type than `ILawnUnitView` (which the Zomboss folder's own interface deliberately
exposes as only `Ptr`/`Relation`/`HpCurrent`/`HpMax`, with **no** position or type). The current guard
happens not to string-match `BoardSnapshot`/`InjectorBoardSnapshot` (different literal substrings than
`MatchRuntime`/`MatchSnapshot`/`Board `), so it will not fail today — but the new code sits exactly in
the folder whose stated purpose is "board access stays narrow," reading a wider seam than the folder's
own existing interface offers, and a future hardening of that guard (a natural edit, since
`BoardSnapshot` is an obvious oversight in its pattern list) would break this module without warning.

**Fix:** either (a) move `LawnBattleView.cs`/`LawnRelationChain.cs`/`LawnDerivedCache.cs` out of
`Match/Ai` into a combat-ai-owned location (e.g. `Actions/Ai/Lawn/`, alongside `decision-inspector`'s
own `Actions/Ai/` files, which is also the more natural home since `IBattleView` itself lives under
`Actions/`), or (b) explicitly widen `Nothing_under_Match_Ai_may_read_the_board_itself`'s stated scope
in the same change, with a comment distinguishing "no full board access" (Zomboss, still enforced) from
"a combat-ai lawn adapter's own richer census read" (newly allowed). The spec's own design-gate
checklist already half-notices this ("close to the existing guard... not resolved here") — it should be
resolved before build, not left open. Not a blocker to the spec's mechanism design otherwise.

### 3.2 `spec-lawn-cast-trigger.md` — three "structural" caps placed in the balance-surface tuning file

`carryCasts` (=1), `decisionsPerFrame` (=8) and `castTokens` (=4) are labeled "Structural" in the
spec's own tunables table, but are placed in `gk-core/data/tuning/combat-ai.v1.json`, published through
`gk-core/tools/tuning/publish.py` — the same surface and the same publish path as the genuinely tunable
`swingsPerDecision`/`ticksPerDecision`/`postCastLockTicks` rows beside them. CLAUDE.md's tunables rule
is explicit: a structural value stays a `const` in code with a comment saying why it is not tunable —
the balance-surface file is for values "a balance pass would want to change." Putting a labeled-
structural value inside the same published, balance-pass-editable JSON blurs exactly the distinction
the rule protects: nothing stops a future balance pass from retuning `castTokens` alongside a real
weight change, silently turning a stated frame/pool budget into a de facto balance lever. A fourth cap,
`castTokenTimeoutTicks` (=20), is not labeled at all, inconsistent with its three neighbors even under
the spec's own scheme.

**Fix:** move `carryCasts`, `decisionsPerFrame`, and `castTokens` to code `const`s with the structural
comment CLAUDE.md requires (matching the pattern the spec itself follows for `CombatDebugObservability`'s
`Cap`), or, if there is a real reason a structural per-frame/pool budget belongs in tuning (e.g. it must
vary by device tier), say so explicitly and cite the precedent — the spec does not currently make that
case. Label `castTokenTimeoutTicks` consistently with whichever answer is chosen.

### 3.3 Propagate a verified correction back into `combat-ai-map.md` / `combat-ai-ideal.md`: the lawn clock

Both the approved map (module-15/19 rows) and the ideal (§4.1 "Lawn clock host," §6.1 "a timer on the
lawn engine clock `AdvancedEffectClock`, D15") name `AdvancedEffectClock` as the clock `lawn-cast-
trigger`'s timer and lock must read. `spec-lawn-cast-trigger.md` checked this against code and found
`AdvancedEffectClock` (`Core/Effects/AdvancedEffectClock.cs:33,37`) is constructed from a
`DateTimeOffset` — the wall-clock time source `battle-engine-ssot.md` D15 itself names as the *wrong*
half of the lawn's two-clock split (status timing). The spec instead reads `KernelDriveHost.NowTicks`
(`Injector/Effects/KernelDriveHost.cs:104`), verified in this session to be backed by `SimulationClock`
— the kernel's own scheduled-event-queue clock, which is the half D15 says is correct. This is a good,
code-verified self-correction, but it corrects the **map and the ideal**, and DESIGN-GATE's own evidence
rule 6 ("when you correct something, propagate it... a fix that lands in prose but not in the sibling
map... has not landed") applies. Neither `combat-ai-map.md` nor `combat-ai-ideal.md` has been updated
to say `KernelDriveHost.NowTicks`/`SimulationClock` in place of `AdvancedEffectClock`.

**Fix:** a one-line correction to `combat-ai-map.md` row 19 and `combat-ai-ideal.md`'s two
`AdvancedEffectClock` mentions (§4.1, §6.1), naming `KernelDriveHost.NowTicks`/`SimulationClock`
instead, with a short note citing this finding. Not a change to `spec-lawn-cast-trigger.md` itself.

### 3.4 Terminology drift owed to `combat-ai-ideal.md` / `combat-ai-map.md`: "demon-contract binding slots"

Both documents name "the demon-contract binding slots" as one of three limits
`spec-unique-deploy-cap.md` must reconcile into one admission rule (alongside the AI tier cap and
`ZombossDeployPolicy`). No such literal mechanism exists in code — the nearest real things are
`LoyaltyRank.Bound` (a loyalty tier, not a slot count) and `ContractPolicy.Capacity`/`BaseSlots` (a
roster-size cap). `spec-unique-deploy-cap.md` handles this correctly: it maps the phrase to
`ContractPolicy.Capacity`, verifies that capacity is a roster axis (not a concurrency axis), and
correctly declines to fold it into the concurrency admission rule — the right engineering call, made
explicit rather than silently skipped. The map/ideal's phrase itself, though, has no code referent and
should be corrected to name `ContractPolicy.Capacity`/`BaseSlots` so a future reader does not go looking
for a "binding slot" type that does not exist. Owed to `combat-ai-ideal.md` §6.2a and the map's
cross-program table, not to `spec-unique-deploy-cap.md`.

### 3.5 `spec-lawn-cost-authority.md`'s upstream citation chain: a stale status line one hop away

The spec depends on `action-skill-tiers/spec-holder-rung-pricing.md` for `EffectiveRungOf`. Its own
load-bearing citation (`BattleRunState.cs:672-679`) shows the mechanism is **already shipped** in
battle. `spec-holder-rung-pricing.md`'s own status line, however, still reads "proposed, no build
authorized" (per the sub-investigation's finding, confirmed plausible against the map's own convention
of status lines). A reader who follows `lawn-cost-authority`'s citation chain outward would hit a
contradiction between a spec that says "not built" and code that is visibly built. This is a doc-hygiene
defect in `spec-holder-rung-pricing.md`, not in `lawn-cost-authority`, but it should be fixed in the same
change that lands `lawn-cost-authority`, since that is the change that will next touch the file the stale
status line misleads about.

---

## 4. Cross-spec contradictions (highest-value check) — none found at the "two sources of one number"
level

Explicitly checked and cleared:

- **`PerfSection.LawnAiDecide` ownership.** `lawn-actor-view` (15) and `decision-inspector` (10) both
  explicitly disclaim adding this member and both name `lawn-cast-trigger` (19) as its sole owner;
  19 does add it. Single ownership, stated three times independently, never duplicated.
- **Dominance baseline "does not move."** `action-schedule-twin` (9) and `auto-policy-switch` (14) each
  independently derive this from the same evidence (`DominanceGuard.cs:64`/`TerminationGuard.cs:100`
  calling the two-argument `Predictor.Predict` overload) and each treats the other as authoritative
  rather than re-deriving a possibly-different answer. Verified true by the reviewer directly.
  14 explicitly states it will *stop and report* if a re-run shows it moving — the correct guard against
  the one thing that could actually diverge (a re-run finding something the citation-based argument missed).
- **`replay-identity` (8) → `auto-policy-switch` (14) ordering.** Both specs state the same reason
  (`RulesetVersion≥6` rows with a NULL profile stamp would be unrecoverable) for the same hard edge, and
  the map's own "Hard edges" section agrees. No spec tries to skip or reorder it.
- **Aggression-channel bound (`aggression-tier-map`, module 6) vs. its two readers.** `lawn-actor-view`
  (15) explicitly forwards the raw Hub-composed `AggressionOf` value and explicitly assigns the
  saturation-onto-tier-range responsibility to module 6, never doing its own fold. Single mechanism,
  single owner, stated correctly at the one place that could have been tempted to duplicate it.
- **The three cross-program specs vs. the map's ownership table.** All three specs' authorship line,
  implementation-owner line, and mechanism description match the map's cross-program table exactly (see
  §2). `spec-unique-deploy-cap.md` produces genuinely one admission rule on the concurrency axis
  (deletes `ZombossDeployPolicy`'s own `MaxConcurrentOwnUnits` field rather than leaving two live caps);
  it does not touch the roster-size axis (`ContractPolicy.Capacity`) or the engine-wide RAM axis
  (`CapPolicy`), correctly treating those as different questions rather than folding three axes into a
  number that would then mean three different things.
- **`spec-zombie-power-source.md` vs. `combat-ai-ideal.md`'s own M5 finding.** The ideal's audit-derived
  claim ("the player's Might leaks to zombies") is checked against `SpeciesAllocationSource.cs:106,114-116`
  and found **already false** — the code already gates the commander term by empire; the real defect is
  that zombies resolve `Empty`, not that they inherit the player's number. This is exactly the
  code-beats-docs discipline DESIGN-GATE demands, applied correctly and stated as a correction rather
  than silently assumed.

No spec in this batch introduces a second `ActorHub`-shaped compose, a second scorer, a second cost
ledger mechanism, a duplicated cache-trigger set copied from a differently-shaped sibling, or a debug
surface that fabricates a result. The three items in §3 are documentation-propagation and
placement/labeling defects, not architectural forks.

---

## 5. Suggestions (non-blocking)

- Fix the trivial 1–5-line citation drifts noted in §2 opportunistically when each module is built —
  none currently misleads a reader about what the code does, but they will rot further if left.
- `spec-lawn-actor-view.md`'s own design-gate checklist item about the `Match/Ai` guard ("not resolved
  here") should become a resolved line once §3.1 is answered, rather than carrying forward as an open
  item into the plan.
- Consider a single "clock sources" table somewhere in `battle-engine-ssot.md` §4 D15's row, enumerating
  `SimulationClock`/`KernelDriveHost.NowTicks` vs `AdvancedEffectClock`/wall-clock explicitly by name —
  this is the second time in this program alone (D15 itself, and now this review) that the two have been
  confused in prose, which is a sign the distinction is not yet load-bearing-obvious from the docs alone.
