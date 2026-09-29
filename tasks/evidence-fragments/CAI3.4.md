# CAI3.4 — `delve-automated-wiring` A: the downed read (VIEW-HALF)

Lane `combat-ai-2`. The row's deps (CAI1.9, CAI1.10) are done and the read is in-fence, so it was
reopened from `blocked` and its view half landed. The role policy (bullets 2-3) is NOT built and is named
below.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `IBattleView.DownedAllyKeysOf` exists — without it `ally-downed` is inert | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/IBattleView.cs','gk-core/src/FusionRpg.Core/Actions/FoggedBattleView.cs','gk-core/src/FusionRpg.Core/Actions/TraitAwareBattleView.cs','gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs','gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs','gk-core/tests/FusionRpg.Core.Tests/Delve/Battle/DelveRolePolicyTests.cs') -Session combat-ai-20260920"` | **14953 passed, 4 failed** (the four pre-existing corpus facts). The member is declared with a DEFAULT implementation; `BattleRunState` overrides it with the real read; `FoggedBattleView`, `TraitAwareBattleView` and the nested `BloodthirstyView` forward it | `IBattleView.cs`, `BattleRunState.cs` |
| `DownedAllyKeysOf_is_empty_under_every_profile_without_DownedOnDeplete` — the byte-identity claim | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DelveRolePolicyTests"` | **3 passed, 0 failed** — a view that does not override the read reports NOBODY down, asserted through the interface (a default implementation is not reachable from a concrete reference, which is part of the contract) | `tests/.../Delve/Battle/DelveRolePolicyTests.cs` |
| The wrappers FORWARD rather than hide it — where a real defect would live | same run | passes — `A_trait_aware_view_forwards_the_downed_roster` and `A_fogged_view_forwards_the_downed_roster_ungated`. This matters because `BattleRunState.TraitView` WRAPS the run state: a non-forwarding wrapper would answer "nobody is down" for every delve | — |
| Golden: byte-identical | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|~ExpeditionResolver\|~Siege\|~Delve\|~Stance\|Category=BalanceGuard"` | **2249 passed, 0 failed** — nothing moved, and the default implementation is why | — |
| Doc citations | `guard-doc-citations.ps1 -Strict` | exit 0, **0 HIGH** | — |

## A stated deviation, with its reason

The spec expected the member added to every implementor ("three existing implementors move ... plus the
test fakes"). It is a **default interface implementation** instead, returning empty. Two reasons, and the
second is the load-bearing one: (a) empty IS the byte-identity answer the row asks for — every profile but
`delve` has no downed state — so nine `=> Array.Empty<string>()` copies would assert nothing; (b) it keeps
the twelve implementors compiling in one step, where an abstract member would have needed a 12-file edit
to land atomically or not at all. The one view that HAS the state, `BattleRunState`, overrides it, and the
three wrapping views forward it, which is the part that would otherwise be silently wrong.

## NOT done — the row's role policy, and the battle-integration assertion

1. **The role policy (bullets 2-3) is not built.** `Role_is_derived_from_held_action_tags_and_ties_break_in_the_stated_order`,
   `An_actor_with_no_loadout_is_a_striker` and `A_wave_actor_is_the_enemy_row_before_any_tally` need the
   derivation in `Delve/Battle/DelveBattle.cs` (the row's own second file) plus the tie-break order from
   §2-3 of the spec, and `DelveBattle.Resolve`'s new trailing optional parameter. In-fence; it is the
   row's next step and needs the spec read in the same session it is implemented.
2. **`Downed_party_members_are_absent_from_LiveActorKeys_and_present_in_DownedAllyKeysOf` cannot be
   written here.** It needs a live `BattleRunState` — a private nested class inside `BattleEngine` that the
   file's own lines 20-31 record was nested *to avoid* a visibility change, and which no test constructs.
   This is the SAME accessibility decision CAI3.1 is waiting on, so one ruling unblocks both rows'
   remaining behavioural tests.
3. **`Ally_downed_falls_through_when_no_held_action_can_revive`** is the honest state of the consumer gap
   (a revive is a supply today, not an action) and needs the same battle fixture.

## Second slice — the role policy (bullets 2-3), and the row's remaining blocker narrows to one decision

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `Role_is_derived_from_held_action_tags_and_ties_break_in_the_stated_order` | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DelveRolePolicyTests"` | **6 passed, 0 failed** — one case per branch (Heal→support, Defensive→frontliner, Construct→frontliner, Offensive→striker, Movement→striker), plus the STATED tie order both ways (support beats an equal frontliner bucket; frontliner beats striker) and a case proving the tie order is not a blanket precedence (a larger frontliner bucket wins outright). Every action id in the test is synthetic, because the rule must never read a corpus action id | `DelveBattle.RoleOf` |
| `An_actor_with_no_loadout_is_a_striker` | same run | passes — one basic attack and two basic attacks both derive `striker`, because the exclusion is by `ContainerId`, not by count. That is today's behaviour expressed as a role | `DelveBattle.cs` |
| `A_wave_actor_is_the_enemy_row_before_any_tally` | same run | passes — asserted with a loadout that would otherwise derive `frontliner`, so a tally running first would be visible. The `isWaveActor` check is the method's first statement | — |
| Golden: byte-identical, and the §4 rules verbatim | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|~ExpeditionResolver\|~Siege\|~Delve\|~Stance\|Category=BalanceGuard"` | **2252 passed, 0 failed** | — |
| The row's files are untouched elsewhere | `StanceRuntime`/`PoiseLedger`/`Riposte` not in the diff; `DelveBattle.Run` unchanged | `RoleOf` is ADDITIVE — the role is not wired into any caller yet, because the caller is `RpgHub.Resume`'s composition root (CAI3.5, `gk-core/src/FusionRpg.Server/**`, outside this lane) | — |
| Boundary + overflow + citations | `verify-change`; `audit-overflow --targets A3`; `guard-doc-citations -Strict` | **14956 passed, 4 failed** (pre-existing); audit-overflow **exit 0**; doc-citations **0 HIGH** | — |

### The row's remaining blocker is now ONE decision, shared with CAI3.1

Everything the row asks for is landed except its two battle-integration assertions,
`Downed_party_members_are_absent_from_LiveActorKeys_and_present_in_DownedAllyKeysOf` and
`Ally_downed_falls_through_when_no_held_action_can_revive`. Both need to observe a live `BattleRunState`,
which is a private nested class inside `BattleEngine`; `BattleRunState.cs`'s own lines 20-31 record that
the nesting was chosen *to avoid* a visibility change. So this row and CAI3.1's two behavioural tests are
gated on the SAME ruling — make the run state internal, or add a fixture seam — and one decision buys four
acceptance tests across two rows.

**Second, smaller note for the manager:** `RoleOf` has no production caller yet, because its caller is
`RpgHub.Resume`'s composition root — CAI3.5, whose files are all under `gk-core/src/FusionRpg.Server/**` and
therefore outside this lane. A `bool isWaveActor` parameter is how the pure rule is testable without a run
state; the run state is what will supply it (`PartyIndex is null`), and that wiring is CAI3.5's.
