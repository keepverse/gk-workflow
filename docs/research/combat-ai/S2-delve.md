# Lane S2 — delve (party dungeon) combat decisions

## Summary (≤12 lines)
Delve reuses the exact same battle intent core as battle/siege — `IIntentSource` /
`BattleEngine.Resolve(profile:, intentSource:)` — with zero delve-specific engine fork. The
delve-specific piece is a thin **dispatch wrapper**, `RaidIntentSource`, that routes each actor key to
either an interactive (`InteractiveIntentSource`, shared with web battle) or an "automated" source by
precomputed `PartyIndex` key set — this is the raid/party-steering concept battle and siege don't have.
The delve profile (`hybrid-atb`-shaped, `PerSide`, `RequiresLiveInput`, `DownedOnDeplete`) is a Core
data row, built. The critical hole: **there is no real automated `IIntentSource` in production for
un-steered parties or wave enemies** — `RpgHub.Resume` throws `NotImplementedException` by design,
citing the spec's own "Never: `StubIntentSource` as the raid policy" boundary. This is D2.16/D5.11's
long-standing wiring gap, still open. A second, less-discussed gap: `DelveBattleSessionManager.StartSession`
has **zero production callers** anywhere in `src/` — nothing yet triggers "a party arrived at a fight
room." Formations are 1-D rank only (`RankSpan`, board deferred); there are no combo skills anywhere
in the delve tree (real gap, not even named).

## Inventory
| Piece | Bucket | Evidence (file:line, verbatim quote ≤1 line) | Notes for a shared core |
|---|---|---|---|
| Shared intent seam | Built | `gk-core/src/FusionRpg.Core/Delve/Battle/DelveBattle.cs:33` `BattleEngine.Resolve(setup, seed, trace, ..., profile: BattleModeProfileCatalog.Delve, ..., intentSource, board, ...)` | Delve calls the identical `Resolve` entry point battle/siege use; no parallel resolver exists |
| Delve mode profile | Built | `gk-core/src/FusionRpg.Core/Battle/Timeline/BattleModeProfile.cs:295-300` `Delve => _delve ??= Build(DelveId, ..., WScope.PerSide, Commitment.EarlyBoundWithFallback, points: true, ..., requiresLiveInput: true, downedOnDeplete: true)` | One profile row, `BattleModeProfileCatalog` is sole holder of the id literal |
| Profile-pin guard | Built | `gk-core/tests/FusionRpg.Core.Tests/Delve/Battle/DelveBattleProfileGuardTests.cs:13,28` bans `ProfileForExpedition`/`ProfileFor(` anywhere under `Core/Delve` | Source-scan guard proves delve never falls back to `classic-round` via a wave-catalog lookup |
| Raid dispatch wrapper | Built, then superseded | `src/FusionRpg.Core/Delve/Battle/RaidIntentSource.cs:42-43` (deleted by combat-ai CAI1.10, `c284f5f6d`; the same shape is now `gk-core/src/FusionRpg.Core/Actions/IntentRouter.cs`) `TryDeclare` → `_steeredKeys.Contains(actorKey) ? _steered.TryDeclare(...) : _automated.TryDeclare(...)` | Delve-specific: precomputed `PartyIndex` key set, not a live `SideOf`/view lookup — mirrors `SiegeIntentSource`'s corrected shape exactly |
| Steered-party keys | Built, then superseded | `RaidIntentSource.cs:49-50` (deleted by combat-ai CAI1.10, `c284f5f6d`) `KeysForParty(BattleSetup setup, int partyIndex) => setup.Squad.Where(a => a.PartyIndex == partyIndex)...` | Known before `Resolve` runs, from `BattleActorSetup.PartyIndex` |
| Steered-actor safety | Built, then superseded | `tests/.../RaidIntentSourceTests.cs:103-112` (deleted with its subject by combat-ai CAI1.10, `c284f5f6d`; ported test-for-test into `Actions/IntentRouterTests.cs`) "A_steered_actor_that_declares_nothing_is_never_handed_to_the_automated_policy" | Unconditional key-set branch — no accidental autopilot takeover mid-decision |
| Automated policy for un-steered parties + all enemies | **Real gap** (named as such by the spec) | `docs/architecture/party-dungeon/spec-delve-battle-profile.md:355-356` `"Never: ... StubIntentSource as the raid policy"`; `gk-core/src/FusionRpg.Server/RpgHub.cs:253-259` `throw new NotImplementedException("RpgHub.Resume needs a real siege-ai-class automated IIntentSource ... StubIntentSource is explicitly barred from standing in for it.")` | This is the AI a delve-combat-ai profile would replace/fulfil — the exact target for a shared core's automated-policy contribution |
| siege-ai (the named dependency) | **Real gap upstream** | `RpgHub.cs:244` `"SiegeAi.PlayedSide is never set in production either"`; `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs:220` (pre-CAI1.1 — that dispatch wrapper no longer exists; the scorer is `Actions/Ai/CandidateScorer.cs`) only ships `SiegeIntentSource` (a dispatch wrapper identical in shape to `RaidIntentSource`, not a scoring/decision policy) | Base-defense's own `siege-ai` module (one `IIntentSource` dispatching on `SideOf`) is itself unbuilt as a *competent* policy — delve explicitly consumes it rather than building its own, so the gap is shared with siege, not delve-only |
| `StartSession` (the room→fight trigger) | **Wiring gap** | `gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs:191` `public DelveBattleSession? StartSession(...)`; grep confirms zero non-test callers in `src/` (`grep -rn "StartSession(" src/` → only the declaration itself and unrelated `DebugRuntime.StartSession` in the injector) | Nothing yet decides "a party arrived at a fight room" and calls this; the manager's own doc comment (`:25-35`) names this honestly as still-unbuilt content wiring, separate from the automated-policy gap |
| Steer / Declare / Resume hub surface | Built (Steer, Declare) / **Wiring gap** (Resume) | `gk-core/src/FusionRpg.Server/RpgHub.cs:214-235` (`Steer`, `Declare` real, tested); `:251-260` (`Resume` throws) | `DelveBattleSessionManager.Resume` itself (server/DelveBattleSessionManager.cs:267) is real and tested against a *supplied* automated source — only the HTTP/SignalR-reachable path is blocked on the missing upstream policy |
| Downed-not-killed (party attrition) | Built | `gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs:683-690` `if (activeProfile.DownedOnDeplete && a.Setup.PartyIndex is not null) { ...TransitionTo(TurnState.Downed)... }` | Delve-specific FSM branch gated on the profile flag + `PartyIndex`; every other profile (battle/siege) keeps the ordinary death path — a shared AI core must know an actor can be "downed" (still targetable/revivable) rather than dead under this profile |
| Formation | Built (1-D only) | `gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:183` `public int? RankSpan { get; init; }`; `docs/architecture/party-dungeon-map.md:117` `"formation as 1-D rank on SideIndex with rankSpan (R1: board adopted later)"` | No 2-D board for delve yet (siege's `board-render`/A10 to be adopted later) — an AI targeting/positioning profile can't reason about lanes/columns in delve today, only rank |
| Party roles / multi-party raid | Built, then superseded | `RaidIntentSourceTests.cs:38-61` (deleted by combat-ai CAI1.10, `c284f5f6d`; the four-party dispatch test is now `Actions/IntentRouterTests.cs`) four-party dispatch test; `BattleModels.cs:176,621` `PartyIndex` on both setup and result | `PartyIndex` is "a label on the setup, not a third side" (spec quote, `spec-delve-battle-profile.md` Locked anchors §4.8) |
| Encounter/enemy composition | Built | `gk-core/src/FusionRpg.Core/Delve/Encounter/Encounter.cs:91` `public static EncounterHalf Build(...)`; production caller `DelveBattleSessionManager.ResolveRoomEncounter` (`:144-182`) | Deterministic per room seed; admits `CreatureAdmission.ForDelve` only; refuses (throws `EncounterRefusal`) rather than silently substituting a species on an unfillable slot |
| Oaths | Built (data/unlock only, not combat-facing) | `gk-core/src/FusionRpg.Core/Delve/Difficulty/OathUnlock.cs` (file exists, opt-in-below-the-gate unlock mechanic per `party-dungeon-map.md:116` "the Oath as opt-in below the gate with a clear at `maxRungWithoutOath`") | Oaths gate *difficulty/rung access*, not a combat decision input — no evidence they feed `IIntentSource`/AI behaviour at all |
| Event deck encounters | Built (as content selection, not combat AI) | `party-dungeon-map.md:120` module `event-deck`: "the four-filter selector ... the outcome draw ... rolled through `TryInstantiate` at the room's Θ" | Event outcomes can grant/modify a room's fight setup before `Resolve`, but nothing here is itself an in-combat decision-maker |
| Combo skills (party synergy moves) | **Real gap** | grep for `combo`/`Combo` under `gk-core/src/FusionRpg.Core/Delve/` returns nothing | No mechanism anywhere ties multiple party members' actions into a shared/linked skill; would need to be designed from scratch if wanted — not merely wired |
| Retreat / extract | Built (data-level, at room-graph layer, not mid-battle AI) | `party-dungeon-map.md:119` `delve-attrition`: `Downed`, `downedOnce`, wipe rule, recovery-in-delves; extraction is raid-wide per `loot-pack` module | "Retreat" as a player action exists at the room/extraction layer (leaving the dungeon), not as a mid-fight AI-chosen tactical retreat inside `BattleEngine` |

## How decisions are made today in this mode (trigger, who decides, what inputs, what executes)
- **Trigger:** a live SignalR session (`RpgHub`) drives a `DelveBattleSession` background task per
  party-room fight. Each actor's turn opens a dwell window (`Ask`); the steered party's human player
  calls `Declare(matchKey, actorKey, actionId, targetKey)` within the window, or a timeout fires.
- **Who decides today:** for the steered party, the player, via `InteractiveIntentSource` (the same
  class web battle uses) — this path is real and tested. For every un-steered party and every wave
  enemy, `RaidIntentSource` routes to an `automated` `IIntentSource` parameter — but **no real
  implementation of that parameter exists in production**; only `DelveBattleSessionManagerTests`
  supplies a fixed/fake one. Consequently the only HTTP/SignalR-reachable path that would need it
  (`RpgHub.Resume`) is a hard `NotImplementedException`, and the path that starts a fresh session
  (`StartSession`) has no production caller to supply setup + automated source in the first place.
- **What executes:** once an intent is declared (by either source), it flows through the ordinary
  battle resolution (`BattleEngine.Resolve` under the `Delve` profile) — effect bag → Funnel →
  EntityStatWriter-equivalent Core paths, identical to battle/siege. No RPG-layer rule is bypassed;
  the gap is purely "who supplies the un-steered decision," not how a decision executes.

## Per-mode constraints a shared core must respect (timing, determinism/seeds, perf, fog, goldens)
- **Timing:** `RequiresLiveInput: true`, `PerSide` scope (all parties/wave act concurrently per round,
  not turn-by-side like `classic-round`), `AdvancePolicyKind.FixedIncrement`,
  `Commitment.EarlyBoundWithFallback`, `ActionPoints` economy (`points: true`) — closer to siege's
  shape than to lawn's basic-attack-only loop, but with a dwell window (`DefaultDwellWindowMs = 1500`)
  for the human party that a pure-AI mode wouldn't need.
- **Determinism/goldens:** delve fights are logged via `AppendWebMatchLog`/`DecisionTrace`, replay-
  and freeze/resume-safe; `DelveBattleProfileGuardTests` proves the profile pin never drifts to a
  wave-keyed lookup. Any AI added here must produce a decision that serializes into the same
  `DecisionTrace`/replay contract (same `TryDeclare(actorKey, nowTick)` shape) — no new decision
  channel. Golden safety is explicit: new `BattleActorSetup`/result fields are nullable +
  `WhenWritingDefault` so battle/expedition hashes never move.
- **Perf:** no lawn-style hot-loop budget concerns are named for delve — it's a turn-dwell live
  session, not a per-frame engine tick, so an automated policy here can afford materially more compute
  per decision than `lawn-combat-ai`'s trigger-edge budget.
- **Freeze/steer semantics:** switching a human player away from a party **freezes** that party's fight
  (cancel-and-discard, never "finish on autopilot" — a structural guarantee via uncaught
  `OperationCanceledException`, not a policy choice); Resume is always a fresh session replaying the
  persisted decision trace, never a reattachment.

## Cross-mode reuse candidates (what this mode already shares / could share)
- **`IIntentSource` contract** — identical across lawn/battle/siege/delve. A shared "combat-AI core"
  can target this one interface and be automatically consumable by all four places.
- **`InteractiveIntentSource`** is literally shared code between web battle and delve (not
  reimplemented) — proof that a shared decision seam already works across modes when the mode only
  needs a thin profile/dispatch layer on top.
- **Dispatch-by-precomputed-key-set** pattern (`RaidIntentSource` mirrors `SiegeIntentSource`
  "exactly," per its own doc comment) — the same shape could host a shared AI-core's per-side/per-party
  routing uniformly across siege and delve.
- **The missing piece delve and siege share, not delve-specific:** neither mode has a real "automated,
  competent policy" `IIntentSource` today. `StubIntentSource` (battle/lawn's basic-attack-preference
  fallback) is explicitly barred from filling this role for delve by the spec's own Boundaries table.
  A shared combat-AI core that produces one real policy usable as both siege's `siege-ai` and delve's
  `automated` parameter would close two named gaps (party-dungeon D2.16/D5.11 and base-defense's
  `siege-ai`) with one build, rather than two bespoke ones.
