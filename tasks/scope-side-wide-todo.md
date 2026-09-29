# Tasks: scope-side-wide program

Brief: the patron aura buffs the enemy side (live defect, creature-standalone **PT7**). Decision
source: [multi-lane-handoff-20260920.md](multi-lane-handoff-20260920.md) §6 — **extend the owner-key
grammar with a side-wide key**; do **not** re-platform the aura onto `BattlefieldOwnSideReactor`,
which would answer "which side does this apply to" in a second place.

**3 tasks · S each.** Writable paths for this lane: `gk-core/src/FusionRpg.Core/Stats/StatApplyScope.cs`,
`gk-core/src/FusionRpg.Core/Effects/**`, `gk-core/src/FusionRpg.Core/**/Patron*`, `gk-core/tests/FusionRpg.Core.Tests/**`,
`tasks/**`.

> ## ⛔ Rules binding on every slice below
>
> **1. No golden moves.** A moved hash is a stop-and-report, never a re-bless.
> **2. Out of scope, untouched:** the `instance:` Hot guard (`StatApplyScope.IsInstanceOwnerKey`) and
> the `player:` stub (match-wide on purpose).
> **3. Tests pin the CONTRACT** — the grammar, its closed vocabulary, its side arithmetic. Never a
> population count, never generated text.
> **4. The key must actually reach a production host.** The aura's live delivery is the grant store +
> `GrantedDerivedAtomReader`, not `StatApplyScope.Matches` alone; a grammar change with no reader-side
> lookup widening would leave the aura inert, which is worse than the defect.

---

- [x] **SSW1: the grammar — a side-wide owner key** · S
  - Add `plant:*` / `zombie:*` (constants: `EffectOwnerKey.PlantSide` / `ZombieSide`) and make
    `Normalize`, `Matches`, `IsKnownOwnerKey`, `IsMatchWide` agree about it. Chose the prefix spelling
    over `side:plant` because the family already spells the side as the prefix; the key is deliberately
    **not** match-wide (match-wide = both sides). `OwnerKeyCovers` is the one store-lookup widening the
    key needs to be reachable at all.
  - Acceptance: a side-wide plant key matches every plant regardless of type id; never a zombie;
    `match` still matches both sides; the type-keyed arms are not widened; `IsMatchWide` is false for
    the new key.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StatApplyScope|FullyQualifiedName~Patron"`
  - Files: `gk-core/src/FusionRpg.Core/Stats/StatApplyScope.cs`, `gk-core/src/FusionRpg.Core/Effects/EffectProcAndOwner.cs`,
    `gk-core/tests/FusionRpg.Core.Tests/Scope/StatApplyScopeSideWideTests.cs`
  - **Done.** `EffectOwnerKeys` (Contracts) was outside this lane's paths, so the constants live in
    Core's own owner-key class `EffectOwnerKey`; the Contracts mirror is a follow-up row, not a
    disagreement with the brief.
- [x] **SSW2: the fix — the aura asks for the plant side, and the grant store answers it** · S
  - `PatronSecondaryPlugin` grants `OwnerKey = EffectOwnerKey.PlantSide` with `OwnerKind = "plant"`;
    `InMemoryEffectGrantStore.ForOwner` answers a side-wide grant for the per-type lookup every reader
    makes; `EffectFunnel.WithdrawByPluginId` treats an omitted owner key as "every scope this plugin
    granted at" (it silently meant the literal `match` scope, so a `plant:*` grant could not be
    withdrawn and would outlive its match).
  - Acceptance: a patron-shaped grant read through `GrantedDerivedAtomReader` + the real grant store
    reaches plants of any type and **nothing** on the zombie side; a match-scoped grant still reaches
    both sides; the plugin stamps the side-wide key; board.end still withdraws it.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StatApplyScope|FullyQualifiedName~Patron"` and `pwsh -NoProfile -File scripts/guard-actor-hub.ps1`
  - Files: `gk-core/src/FusionRpg.Core/Effects/Plugins/PatronSecondaryPlugin.cs`,
    `gk-core/src/FusionRpg.Core/Effects/EffectBag.cs`, `gk-core/src/FusionRpg.Core/Effects/EffectFunnel.cs`,
    `tests/FusionRpg.Core.Tests/Effects/PatronAuraScopeTests.cs`,
    `tasks/creature-standalone-todo.md` (PT7b — the second producer, outside this lane's paths),
    `tasks/aura-skill-todo.md` (stale citation this change causes)
  - **Done.** Falsified before claiming it: reverting the store widening fails 3 of the new tests;
    reverting the funnel withdraw fails the board.end test — which itself had to be rewritten, because
    `SimEffectHost.EndMatch` calls `ClearAll` and the first version passed against a withdrawal that
    never ran. The out-of-scope second producer is filed as **PT7b** (rule 2), the stale citation as
    **T25**, and the `core-fallback` planning reading as **TVB6.5**.
  - ⚠️ **The live half is NOT closed by this commit.** `PatronEndpoints.TryBuildPatronSessionGrant`
    still stamps `match` for the same grant id, so PT7 criterion 2 needs PT7b first.
- [x] **SSW3: pin the boundary the key deliberately does not cross** · S
  - `EffectOwnerKey.MatchesEvent` (the trigger gate) keeps its type-keyed arms only, so a side-wide key
    never fires as a triggered grant — documented in `StatApplyScope`'s own header, pinned here so a
    future producer gets a red test rather than silence.
  - Acceptance: a `plant:*`-keyed grant matches no event, while the same event is matched by its
    `match` and `plant:{typeId}` forms (non-vacuous).
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StatApplyScope|FullyQualifiedName~Patron"`
  - Files: `gk-core/tests/FusionRpg.Core.Tests/Scope/StatApplyScopeSideWideTests.cs`
  - **Done.** Not in the brief; added because the header now states the boundary as a decision, and a
    stated decision with no test is a comment. The non-vacuity control is inside the same test: the same
    event object IS matched by `match` and `plant:5`, so the refusal is about the key, not the event.

### Checkpoint S

- [x] SSW1–SSW3 closed; the two named brief filters + `guard-actor-hub.ps1` green; **no golden moved**
  (36/36 identical to the pre-change baseline).
- [ ] **Live half stays open (owner/live-qa lane).** PT7b: `PatronEndpoints.TryBuildPatronSessionGrant`
  is the second producer of grant id `patron:aura` and still stamps `OwnerKey = "match"`, so whichever
  of the two writes the injector's bag last decides the scope. This lane cannot touch
  `gk-core/src/FusionRpg.Server/**`; PT7 criterion 2 needs PT7b fixed first.
