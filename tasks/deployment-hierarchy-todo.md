# Todo: `deployment-hierarchy`

**Plan:** [deployment-hierarchy-plan.md](deployment-hierarchy-plan.md) · **Map:**
[../docs/architecture/deployment-hierarchy-map.md](../docs/architecture/deployment-hierarchy-map.md) ·
**Status:** plan approved 2026-09-20 (`backlog-clean-up` BCU2.5). Prefix `DH`.

Verification: `.\scripts\verify-change.ps1 -Paths <changed> -Session <id>` unless a task names
otherwise. No task exceeds 5 files or L scope.

---

## Wave 1 — `deploy-carry` (module 1: wire the inert inherit side)

- [ ] **DH1.1 — Populate `CarryInPools` at every setup call site** · M · deps: — · *(spec: deploy-carry)*
  - Acceptance: every battle/delve/lawn/siege setup builder passes a real `CarryInPools` value
    (today null everywhere, confirmed live via `grep CarryInPools\s*=` returning zero hits); a setup
    with no parent state is still explicitly empty, never silently null.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter DeployCarry`.
  - Files: the shared setup builder(s), `BattleModels.cs`, focused tests.

- [ ] **DH1.2 — `DelveCarryIn.Apply` carries pools into the next room's setup** · S · deps: DH1.1 · *(spec: deploy-carry)*
  - Acceptance: a party moving room-to-room in a delve starts the next room from its `CarryOut` pool
    values, not rest-max.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter DelveCarry`.
  - Files: `src/FusionRpg.Core/Delve/DelveCarry.cs`, focused tests.

- [ ] **DH1.3 — Map `DelveMemberState.Statuses` into the next setup's initial status specs** · S · deps: DH1.2 · *(spec: deploy-carry)*
  - Acceptance: `EventOutcomeDispatch.cs`'s appended statuses actually reach the next room's setup
    (today appended but never consumed); troop `Hp/Wounds` headcount representation stays unchanged.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "DelveCarry|StatusCarry"`.
  - Files: `src/FusionRpg.Core/Delve/EventOutcomeDispatch.cs`, `DelveCarry.cs`, focused tests.

### Checkpoint CD1 (G1 — the tree carries)
- [ ] A delve party redeployed into a second room starts from its `CarryOut` pools and status specs;
  a battle actor's `CarryInPools` is non-null end to end; replay is byte-identical.
- [ ] `.\scripts\guard-dal.ps1` green.

## Wave 2 — `injury-tiers` (module 2, in full)

- [ ] **DH2.1 — The `wound.*` status family** · M · deps: DH1.* · *(spec: injury-tiers)*
  - Acceptance: `wound.*` joins the closed status vocabulary (decisions.md row P1, already approved);
    timeless, attacker-less, exhaustion-shaped; its own opt-in constructor check mirroring
    `ExhaustionPolicy.cs:59-66`/`NervePolicy.cs:68-74` — the anti-spiral guarantee is tested, not assumed.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter Wound`.
  - Files: the new `wound.*` status container, `StatusCatalogBootstrap.cs`, focused tests.

- [ ] **DH2.2 — Tier thresholds + durable worsening counter** · M · deps: DH2.1 · *(spec: injury-tiers)*
  - Acceptance: tier thresholds read `%HP lost` past a relative bound, bound to an existing
    potency/power read (owed: the exact `base + %lost × scale` formula and its `ssot-power-scale.md`
    §10 row); the worsening counter lives in durable per-specimen state
    (`rpg_unique_actor_pools`/`rpg_unique_actor_recovery`), never on `StatusInstance`.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter InjuryTier`.
  - Files: the tier resolver, `data/tuning/deployment-hierarchy.v{n+1}.json` (thresholds), focused tests.

- [ ] **DH2.3 — Per-deployment-kind recovery clocks** · M · deps: DH2.2 · *(spec: injury-tiers)*
  - Acceptance: delve-counted `Recovering`, world-turn legion rest, and priced ritual each advance on
    their own clock — never wall time; a specimen graded into a tier fights measurably weaker on its
    **next** deployment, not the current one.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter Recovery`.
  - Files: the recovery-clock resolver(s), focused tests.

### Checkpoint CD2 (G2 — a wound is real)
- [ ] A graded specimen fights measurably weaker on its next deployment; an untreated serious wound
  advances and can kill on its own settlement clock; the anti-spiral check refuses a runaway stack.

## Wave 3 — `item-durability-repair` remainder (module 7)

- [ ] **DH3.1 — §3 real per-battle wear decrement** · S · deps: DH1.1 (battle settlement hook) · *(spec: item-durability-repair)*
  - Acceptance: an item's `current` decrements once per battle settlement, never per delve room; goes
    unusable at zero, never destroyed by wear alone.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter DurabilityWear`.
  - Files: the battle-settlement wear hook, `data/tuning/deployment-hierarchy.v{n+1}.json`
    (`wearPerBattleMilli`), focused tests.

- [ ] **DH3.2 — D4 field touch-up** · M · deps: — · *(spec: item-durability-repair)*
  - **Corrected 2026-09-20** (`backlog-clean-up` BCU2.8 independent review): `party-dungeon`'s
    `PackGrid` already shipped (`party-dungeon-todo.md` D3.18-D3.23, all `[x]`;
    `gk-core/src/FusionRpg.Core/Delve/Pack/PackGrid.cs` exists) — the earlier "external, unbuilt" dependency
    was stale. The real remaining gap is narrower: `ICarriedSupplyCheck` has zero C# implementations
    (grep-confirmed) and no caller threads a `PackGrid` instance through the resolver.
  - Acceptance: a real `ICarriedSupplyCheck` implementation reads a party's `PackGrid`; field
    touch-up resolves through it — substrate only, carried tool+materials required, caps at
    partial/eroding.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter FieldTouchUp`.
  - Files: `ICarriedSupplyCheck`'s implementation, the field-touch-up caller, focused tests.

- [ ] **DH3.3 — D6 commander-pouch parity** · S · deps: — · *(spec: item-durability-repair)*
  - Acceptance: commander-pouch gear wears through the same mechanism as unique gear, same table
    scope, no second wear path.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter CommanderPouchWear`.
  - Files: the commander-pouch wear caller, focused tests.

### Checkpoint CD3 (G6 remainder)
- [ ] DH3.1, DH3.2 and DH3.3 all ship — DH3.2 is buildable now (its `PackGrid` dependency shipped;
  corrected 2026-09-20), not blocked.

- [ ] **DH-B1 — `dotnet build gk-fusion/src/FusionRpg.Injector` fails with `Ambiguous project name 'FusionRpg.Injector'`
  (a host assembly-name collision).** **Filed by:** lane `cmdc-ep2-1` (`empire-progression`), 2026-09-20,
  on EP3.4's Verify line. **Cause:** `gk-fusion/src/FusionRpg.Injector.BepInEx/FusionRpg.Injector.BepInEx.csproj:8`
  sets `<AssemblyName>FusionRpg.Injector</AssemblyName>` — the same assembly name as
  `gk-fusion/src/FusionRpg.Injector/FusionRpg.Injector.csproj` — and **the reference runs injector → host, not
  host → injector**: `gk-fusion/src/FusionRpg.Injector/FusionRpg.Injector.csproj:10` references
  `..\FusionRpg.Injector.BepInEx\FusionRpg.Injector.BepInEx.csproj`, and that host compiles the
  injector's sources directly (`FusionRpg.Injector.BepInEx.csproj:33-35`,
  `<Compile Include="..\FusionRpg.Injector\**\*.cs">`) rather than referencing the project. So NuGet's
  restore graph sees two projects named `FusionRpg.Injector`:
  `NuGet.targets(198,5): error : Ambiguous project name 'FusionRpg.Injector'`. Reproduced on this
  worktree with `dotnet build gk-fusion/src/FusionRpg.Injector` **and** with the explicit
  `gk-fusion/src/FusionRpg.Injector/FusionRpg.Injector.csproj` path, with `FUSIONRPG_GAME_DIR` unset and SDK
  10.0.303 installed; nothing in this lane touched any injector file (`git log -1 --
  gk-fusion/src/FusionRpg.Injector/` is `7fc1c363`, another program's). **Not established:** whether the BepInEx
  host's `AssemblyName` is deliberate (a plugin-dll naming requirement) or a copy-paste, and whether the
  owner's own `deploy-play.ps1` run hits it (that script may pass extra properties). **Fix (owner or this
  program):** give the BepInEx host its own assembly name, or state why the collision is intentional and
  make the plain injector build addressable. Until then no lane can run an injector build — which
  EP3.4/EP3.5 and any injector-facing Verify line needs.
  - **Blast radius corrected 2026-09-22 (session `arch-d-20260922`), verified by running it — the
    paragraph above is right about the failure and too broad about the reach. What DH-B1 blocks is a
    build of `gk-fusion/src/FusionRpg.Injector/FusionRpg.Injector.csproj` itself and nothing wider.**
    `FusionRpg.slnx:7-9` lists the three **host** projects only (the plain injector project is not in
    the solution); `scripts/guard-injector-compile.ps1:29` builds
    `gk-fusion/src/FusionRpg.Injector.MelonLoader.39` whose `<AssemblyName>` is `FusionRpg.Injector.MelonLoader.39`
    (`:9`) — so `guard: injector-compile` is not blocked; `gk-fusion/tests/FusionRpg.Injector.Tests/*.csproj:33`
    references the **BepInEx host**, so the injector test project is not blocked either;
    `scripts/deploy-play.ps1:215,294,297` builds the host; and CI has no injector build at all
    (`grep -n Injector .github/workflows/ci.yml` → no match). This row's own program already recorded the
    narrower truth: `empire-progression-todo.md:538` — *"the injector host builds. The row's literal
    `dotnet build src\FusionRpg.Injector` is red on DH-B1."* **"no lane can run an injector build" is
    therefore false**; the literal command in EP3.4/EP3.5's Verify lines is what is red. Register and
    sequencing: [reports/deployment-scope-status-20260922.md](reports/deployment-scope-status-20260922.md)
    §2(c).
