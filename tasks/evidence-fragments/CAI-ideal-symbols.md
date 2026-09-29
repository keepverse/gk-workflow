# `CAI-ideal-symbols` — the ideal's §4 tables symbol-checked, and four stale citations fixed

Lane `combat-ai-3`, 2026-09-21. Follows `CAI-ideal-status`, whose own "Not proved" section flagged that the
ideal's remaining §4.1 rows were **bounds-checked, not symbol-checked** — a bounds-clean citation can still
name the wrong symbol, which is the class `CAI-cite-1` spent 39 fixes on. This closes that caveat.

Method: for every `` `X.cs:N[-M]` `` citation from §4.1 onward, require each identifier the row names to
appear inside the cited range, then **read every flag by hand** — because rows legitimately name things that
belong in their neighbour column, so most flags are artifacts.

| Check | Command | Result |
|---|---|---|
| §4.1 is symbol-clean | the range check over §4.1's 14 citations | **all hold**, including the two that flagged and were then read: `SiegeAi.cs:25-30` is exactly the doc comment that names `BattleTrace.AiDecision` (and it already records CAI1.1's move), and `BattleModeProfile.cs:295-300` is the `Delve` profile with `downedOnDeplete: true` — which is CAI3.4's byte-identity claim |
| The flags elsewhere are artifacts, checked one by one | read of each | `KernelDriveHost.cs:54-56` names the *budget* while `SimulationClock`/`AdvancedEffectClock` are the row's other subjects; `LawnBasicAttackFeature.cs:56`/`EffectRuntime.cs:359` are the start of a chain whose end is `EntityStatWriter`; `ILawnBoardView.cs:36-66` is cited for the lawn seam while `IBattleView` is the type it feeds; `RpgHub.cs:251-260` is cited for `Resume` while the `Siege…IntentSource` names sit in the second column |
| **Four citations were genuinely stale, and are fixed** | see below | each verified to hold its named member at the new anchor (6/6 anchor checks OK) |
| The guard scope stayed clean | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary`; `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | `D1 7 (0 HIGH)`, `D2 0`, `D3 0`, `D4 0` unchanged; repo-wide strict guard exit 1 on **other** programs' docs with **0** lines mentioning `combat-ai/` |

## The four fixes

| Ideal row | Was | Now | Member actually found at the new anchor |
|---|---|---|---|
| §4.2 *Aggression is read only by siege* | `SiegeAiIntentSource.cs:258` | **`:501`** | `Aggression: _view.AggressionOf(candidateKey),` — `:258` is inside a `RetargetLedger` doc comment |
| §4.3 *A per-place "resolvable here" filter* | `BattleEffects.cs:206-225` | **`:243-251`**, and the text now says "the dispatch table" | `[EffectActions.ApplyStatus] = ExecApplyStatus,` at 243 … `[EffectActions.PlaceStructure] = ExecPlaceStructure,` at 249 — `:206-225` is a `pluginId: "battle"` construction region (the file grew 384 → 447 in CAI1.12) |
| §6.1 *Aggression bound* | `DerivedStatRegistry.cs:292` | **`:296-298`** | `Register(new(DerivedStatChannels.AiAggression, DerivedComposeKind.FlatSum, 0, …))` — `:292` is blank |
| §7 *the replay stamp* | `WebMatchService.cs:125-127` | **`:125-128`** | `RngAlgoVersion` is at 127 and `BattleEnvironment.Stamp` / `ComputeContentHash().ToCompact()` at **128**, so the range was one line short |

Each is a **location** fix; no claim in any of those rows was reworded, and the numbers they assert
(`FlatSum`, the four opcodes, the `AggressionOf` read) all still hold.

## One site deliberately NOT touched, consistent with the tabulated refusals

`§6.1`'s sentence *"fixes siege's `IsKillingBlow` call, which omits `baseOverlayDamage`
(`SiegeAiIntentSource.cs:214`)"* is plan-era prose describing a defect that **CAI1.5 has since fixed**, and
`SiegeAiIntentSource.cs:214` is now blank. Re-anchoring the citation alone would make a landed fix read as
still pending, and rewriting the sentence would erase the plan's record of what it set out to fix — the same
reason the §4.4 baseline, the `CAI1.11` pre-fix quotes and the §4.2 stance row were left as written. It joins
that tabulated list.

## Not proved

- **§4.4 and the historical rows were not swept**, by design: their citations point into the *pre-CAI1.14*
  state that the tables exist to record. Fixing them would make a baseline look current. The fragment for
  `CAI-ideal-status` tabulates the reason.
- **§5 and §8–§10 were not symbol-swept** — only §4 and the three later rows that the range check flagged.
  The rest of the document's citations are bounds-clean (`D2 0`) but not symbol-verified.
- **The four fixes are location-only**, so nothing here changes a claim; the guard counts before and after
  are identical, which is the evidence that no citation was removed or invented.
