# CAI3.5 — blocked, with two MEASURED blockers rather than a reading

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The row was named three times; this segment established
exactly why it cannot be finished, by attempting the half that looked purely mechanical.

## Blocker 1 — the tuning half cannot be satisfied: `delve/enemy` is not in the closed vocabulary

The acceptance asks for *"Four `delve/*` rows published as `combat-ai.v2.json`"* and the spec names them
`delve/frontliner`, `delve/support`, `delve/striker`, `delve/enemy`
(`spec-delve-automated-wiring.md:36-37,249-256`; `:281` *"`PartyIndex is null` is `delve/enemy`"*).

I built all four rows against the parser's requirements — copying `*/default` and overriding `rows`,
`scoring` (`objective` = **0**, spec `:355`), `reserves` (150/300/100/100 `UNMEASURED`, `:356-357`), and a
`_note` carrying the `UNMEASURED` marker — and **validated every `selector`/`condition`/`census`/`tag` name
against the enum declarations before publishing**. The build aborted on exactly one name:

```
AiRole: ['Default', 'Frontliner', 'Support', 'Striker', ...]   (no Enemy)
ABORT - names not declared: [('role', 'Enemy')]
```

`CombatAiTuningLoader.ParseProfile` splits the profile key on `/` and parses both halves against the closed
vocabularies (`AiPlace` and `AiRole`), so `delve/enemy` cannot be written today. **Three of the four keys ARE
expressible** (`AiPlace.Delve` plus `Frontliner`/`Support`/`Striker`); the fourth needs either a fifth
`AiRole` member — a reviewed vocabulary change that breaks its own pinned count
(`CombatAiTuningTests.AiRole_has_four`, `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/CombatAiTuningTests.cs:89`) —
or an erratum naming a different key. That is an owner decision, and the erratum is the cheaper of the two.

Everything else the publish needs is prepared and spec-complete, so once the key is ruled the publish is one
`publish.py --add-key` invocation plus the H7 reader switch (this lane holds `gk-core/data/tuning/**` AND both
readers, so that half is not blocked).

## Blocker 2 — the headline half needs a view a private nested class holds

`RpgHub.Resume` throws because it has no *"real siege-ai-class automated `IIntentSource` for the raid's
un-steered actors and every wave enemy"*. `DelveBattleSessionManager.Resume(string matchKey, long playerId,
IIntentSource automated)` is real, tested, and takes one — so the fix is to BUILD that policy
(`DelveAutomatedPolicy`, the row's own new file).

What that needs, measured:

| Fact | Where |
|---|---|
| A public composition factory exists | `CoreIntentPolicy.Create` — `gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs:104` |
| The only battle `IBattleView` is a PRIVATE NESTED class | `BattleRunState` — `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:41` |
| …and the nesting is documented as deliberate | `BattleRunState.cs:20-31` — the nesting exists *to avoid* a visibility change |

So `DelveAutomatedPolicy` cannot obtain a view without reaching into `BattleEngine` — the same **owner
decision** the todo's `R-OWNER` bullet already records for CAI3.1's and CAI3.4's last two tests ("making it
`internal` is a recorded-position reversal, so it is an owner decision, not a lane's").

## Also owed, unchanged

- Dependency row **CAI2.2** (→ `gk-core/src/FusionRpg.Data/**`, the delve replay pin).
- The acceptance's `NoCatchInLiveBattleCallStackTests` edit is a **protected pipeline path**; the todo
  records `tvb58` being refused by the hook on it twice.

## Not attempted, and why that is the honest outcome

Landing `DelveAutomatedPolicy` without a view would be a mechanism that can never declare an intent, and
publishing three of four rows would leave `combat-ai.v2.json` contradicting the spec's own success criterion
4 while its fourth key is still undecided. Both are worse than naming the two decisions.
