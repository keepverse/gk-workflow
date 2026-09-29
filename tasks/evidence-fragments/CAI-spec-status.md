# `CAI-spec-status` — twelve module specs said "Not built" while halves of them had shipped

Lane `combat-ai-3`, 2026-09-21. Each spec under `docs/architecture/combat-ai/**` opens with a `**Status:**`
line, and `DESIGN-GATE.md` sends every agent to that spec before proposing anything in its subsystem — so a
status line that contradicts the code costs the next reader the same re-derivation this program has already
paid for. The Deferred section already records the pattern for a sibling spec
(`spec-holder-rung-pricing.md` reads "not built" though its contract 4 ships).

| Criterion | Command | Result |
|---|---|---|
| The stale set, found two ways | `grep -n "^\*\*Status" …` found six; the header-status grep (`grep -n "Status:" …`) found **six more declared inline** mid-header — the first grep was not enough | **12 stale**, every one reading `**Status:** spec, 2026-09-20. Not built.` |
| Each correction is a verified claim | existence + ledger state for every task named | see the table below; all 10 named source files are present and every task is `done` in the ledger where the status says "built" |
| What must stay "Not built" | ledger | **five** specs keep it honestly — `auto-policy-switch` (CAI3.6 blocked), `commander-direct-orders` (CAI4.9), `lawn-cast-activation` (CAI4.6), `lawn-cast-trigger` (CAI4.7), `lawn-held-actions` (CAI4.2) |
| Two more already had accurate statuses | read | `resolvable-here` ("the Core half is built (CAI1.12)") and `action-schedule-twin` ("**Identity half BUILT**") were left alone; `aggression-tier-map` ("built (CAI1.13)") likewise |
| The doc scope's audit did not move | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | **`D1 7` (0 HIGH)**, `D2 0`, `D3 0`, `D4 0` — unchanged, after a fix described below |
| No new repo-wide finding | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 1 on other programs' docs, **0** lines mentioning `combat-ai/` |

## The twelve

| Spec | New status | Landed (verified) |
|---|---|---|
| `spec-intent-router.md` | **built** (CAI1.10 + CAI1.11) | `Actions/IntentRouter.cs` is the one chain; both older routers deleted; `ITraitDecorator`s reach every policy |
| `spec-core-scorer.md` | **built** (CAI1.1) | `Actions/Ai/CandidateScorer.cs` (`Score`, `ChooseTarget`, `TopThree`); `SiegeAi.cs` holds no scorer |
| `spec-profile-schema.md` | **built** (CAI1.6 + CAI1.8) | `CombatAiProfile.cs`, `AiVocabulary.cs`, `AiRowSelector.cs`, `gk-core/data/tuning/combat-ai.v1.json`, read by both hosts |
| `spec-ai-tiers-personality.md` | **built** (CAI1.9) | `AiTierResolver.cs`, `AiPersonality.cs`, `AiPersonalityApply.cs`, `CoreIntentPolicy.cs` |
| `spec-stance-wiring.md` | **part built** (CAI3.1) | the seam **and**, since 2026-09-21, its one writer; the two dead keys await `AiTuning` narrowing |
| `spec-siege-loadout-wiring.md` | **part built** (CAI3.3) | `CompositeContainerEffectResolver` + 7 tests; the Data/Server halves are `CAI3.2` |
| `spec-delve-automated-wiring.md` | **part built** (CAI3.4) | `IBattleView.DownedAllyKeysOf` + `DelveBattle.RoleOf` + 6 tests; consumer is `CAI3.5` |
| `spec-lawn-actor-view.md` | **built in Core** (CAI4.1), no host | the three `Actions/Ai/Lawn/…` files + 18 tests; `LawnActorViewHost.cs` is out of fence |
| `spec-lawn-cost-authority.md` | **part built** (CAI4.4) | `Actions/Unlock/EffectiveRungResolver.cs`; the lawn ledger half is `CAI4.5` |
| `spec-decision-perf.md` | **part built** (CAI1.14) | sites 1–4 landed with their zero-byte measurements; site 5 + `PerfProbe` are `CAI-perf-1` (filed, out of fence) |
| `spec-decision-inspector.md` | **part built** (CAI2.4) | record + sink seam in; the lawn ring's injector half is `CAI2.5`, out of fence — and this now agrees with the spec's own status further down at `:70`, which it contradicted |
| `spec-replay-identity.md` | **part built** (CAI2.1) | `CombatAiProfileIdentity` + `ICombatAiProfileSource`; the Data/Server thirds are filed — likewise now agreeing with `:69` |

## One self-inflicted finding, caught and fixed in the same change

Writing `spec-lawn-actor-view`'s new status pushed the scope's `D1` count **7 → 8**: naming a path that does
not exist (`Injector/Effects/LawnActorViewHost.cs`) is a `D1` "no tracked file with this name". The audit's
own remedy is *"Fix the citation, or say on that line that the file is gone"*, so the line now says **"does
not exist yet"** — which is also what it means — and `D1` is back to **7**. No other count moved.

## Not proved

- **The statuses were corrected, not the specs' bodies.** A spec's *tunables*, *acceptance* and *open
  questions* sections were not re-verified; only the status line each reader meets first.
- **"Part built" is a summary, not an audit** of which acceptance bullets are met — the authoritative
  per-bullet state is the todo row the status names.
- **Five specs still say "Not built"**, and I verified that by the task state rather than by reading each
  spec's own subject matter end to end; if a blocked row has a landed slice the row text does not mention,
  the status would be understated.
