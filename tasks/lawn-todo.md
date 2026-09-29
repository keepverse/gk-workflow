# Todo: `lawn`

**Plan:** [lawn-plan.md](lawn-plan.md) · **Maps:** [../docs/architecture/lawn-playable-map.md](../docs/architecture/lawn-playable-map.md),
[../docs/architecture/lawn-tuning-profile-map.md](../docs/architecture/lawn-tuning-profile-map.md) ·
**Status:** plan approved 2026-09-20 (`backlog-clean-up` BCU2.4). Prefix `LW`. A cross-program
reference is written `<prefix><id>` (e.g. `SP6.6`).

Verification everywhere is `.\scripts\verify-change.ps1 -Paths <changed> -Session <id>` unless a task
names a live check. No task exceeds 5 files or L scope — split further at build time if a real file
touches more.

---

## Wave 1 — freshness and the two silent failures

- [x] **LW1.1 — `lawn-perf-budget.v1.json` + wire every perf-ceiling reader** · S · deps: — · *(spec: rider-default-on)*
  - Acceptance: the ceiling (currently a number in a commit message, `≤6%`) is a tunable; every gate
    that checks it reads the file, not a constant.
  - Verify: `.\scripts\verify-change.ps1 -Paths <changed> -Session <id>`; `guard-tuning-immutability.py`.
  - Files: `gk-core/data/tuning/lawn-perf-budget.v1.json` (new), its loader, the perf-gate reader(s).

- [ ] **LW1.2 — `summon-pool-integrity`: generator fix + `fail-deploy` wiring** · M · deps: — · *(spec: summon-pool-integrity)*
  - **Landed 2026-09-23 (lane `lawn-1`), and this row stays OPEN for the generator half.** Half (b)
    shipped 2026-09-20 (`8e56f9e9e`). Half (a) landed **at the serve point**: Task 22's own three ids
    (`261`/`264`/`265`) are `speciesKind: "excluded"` rows that `CreatureAdmission` refuses, and the
    summon roller was the fourth context that re-derived the raw `Summonable` flag instead of asking
    admission — it now asks `CreatureAdmission.ForWave`, the `/api/creatures/catalog` payload reports the
    admitted answer, and `SummonPoolPlantabilityTests` closes the join over the real scoped corpus.
  - **What is still open, and why:** whether every `gameTypeId` in the 200–299 band is plantable at all
    (fusion results are not) needs the authored plantability registry plus a generator that cannot flag an
    unplantable species `Summonable`. Both are `gk-forge/tools/CreatureSpeciesGen/**` + `gk-data/packs/fusion/data/generated/creatures/**`,
    outside this lane's allowed paths — the same fence ruling the Wave-2 note below asks for.
  - Acceptance: a summonable species is one this build can actually plant; an injector-side spawn
    failure answers the deploy correlation instead of timing out. Closes live-probe Task 22.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter Summon` + live re-check of Task 22's 5 pulls.
  - Files: the summon registry/generator, `SummonRoller.cs`, `fail-deploy` wiring, focused tests.

- [x] **LW1.3 — `exhaustion-event`: edge-triggered status + per-actor transitions** · M · deps: — · *(spec: exhaustion-event)*
  - Acceptance: one `actor.exhausted`/`actor.recovered` per window (not per refused swing); the
    existing `ExhaustionPolicy` status lifecycle gets a real lawn caller with an empty payload.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter Exhaustion`.
  - Files: the lawn cost charger, `ExhaustionPolicy` caller, focused tests.

- [x] **LW1.4 — `actor-liveness-refresh`: Core revision type + closed invalidation vocabulary** · S · deps: — · *(spec: actor-liveness-refresh)*
  - Acceptance: `ActorLivenessRevision` (long counter per `(playerId, entityKey)`); the closed kind
    enum (`Ladder`, `CommanderAllocation`, `UniqueAllocation`, `Equip`, `Tree`) is pinned in a test that
    says why it is closed.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter ActorLivenessRevision`.
  - Files: `gk-core/src/FusionRpg.Core/Stats/Derived/ActorLivenessRevision.cs` (new), its test.

- [x] **LW1.5 — `actor-liveness-refresh`: server-side send, extends `SP6.6`** · S · deps: LW1.4 · *(spec: actor-liveness-refresh)*
  - Acceptance: each server verb that changes a tracked input (allocate, equip, tree spend) sends
    exactly one invalidation naming the right kind/scope, riding `SP6.6`'s existing transport — never a
    second `Player`-kind channel (hard edge E2).
  - Verify: `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter Invalidat`.
  - Files: the existing `AptitudesUpdated`/`CreaturesUpdated`-style broadcast sites, its test.

- [x] **LW1.6 — `actor-liveness-refresh`: injector receive + bounded recompose** · M · deps: LW1.5 · *(spec: actor-liveness-refresh)*
  - Acceptance: an unknown kind is refused, never silently skipped; a revision bump recomposes lazily
    (mark dirty, recompose on next read) — asserted bound, not assumed; `Player` re-hydrates Θ in one line.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter Liveness`; live check per
    `spec-actor-liveness-refresh.md`'s Commands section (allocate mid-match, switch player, level up).
  - Files: `gk-fusion/src/FusionRpg.Injector/RpgClient.cs`, `CheatState.ApplyPowerSnapshot`, its test.

### Checkpoint CL1
- [ ] `summon-pool-integrity` and `exhaustion-event` ship; `actor-liveness-refresh` closes live-probe
  Tasks 23/24/25 (re-checked live).
- [ ] `.\scripts\guard-actor-hub.ps1` and `.\scripts\guard-single-writer.ps1` green.

## Wave 2 — the scale foundation and its two consumers

> ⛔ **FENCE GATE (lane `lawn-1`, 2026-09-23).** `LW2.2` needs `data/tuning/mode-profiles.v1.json`
> (new), and this lane's allowed paths carry only `data/tuning/lawn*.json`. That one file gates the
> rest of this plan: `LW2.3`–`LW2.6` depend on `LW2.2`, `LW3.1`/`LW3.2` on wave 2, `LW4.1` on wave 3
> and `LW4.2` on `LW4.1`. The spec, the plan's own H7 and `LW2.4` all name that exact filename, so a
> lawn-prefixed rename would fork the plan rather than fix the fence. Ruling requested: widen this
> lane's paths to `data/tuning/mode-profiles*.json`, or route the scale chain to a lane that owns it.
> Independently denied too: `LW1.2` (`gk-forge/tools/CreatureSpeciesGen/**` + `gk-data/packs/fusion/data/generated/creatures/**`)
> and `LW5.1` (`gk-core/src/FusionRpg.Data/**`).

- [x] **LW2.1 — `regen-unit-trace`** · S · deps: — · *(spec: regen-unit-trace)*
  - Acceptance: the resource-regen unit question is answered and tested; no shipped behaviour changes yet.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter ResourceRegenUnit`.
  - Files: the trace note/test named in the spec.

- [ ] **LW2.2 — `mode-profile`: `ModeProfile` record + `mode-profiles.v1.json`** · M · deps: — · *(spec: mode-profile)*
  - Acceptance: `ActorHubBootstrap.CreateDefault` gains a mode-row parameter; a missing row falls back
    to today's behaviour (byte-identical) — the foundational seam every later module in this plan needs.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter ModeProfile`.
  - Files: `src/FusionRpg.Core/Stats/Derived/ModeProfile.cs` (new), `data/tuning/mode-profiles.v1.json` (new), `ActorHub.cs`.
  - Ruling 2026-09-23 (owner: erratum reword): the tuning file is CREATED by this row, not a precondition — the lane's "file does not exist" denial misread a deliverable as a dependency. Fence granted to `data/tuning/mode-profiles*.json` for the lawn successor; the LW2.3+ chain proceeds once LW2.2 lands.

- [ ] **LW2.3 — `base-relative-read` (hp/armour only)** · S · deps: LW2.2 · *(spec: base-relative-read)*
  - Acceptance: `maxHp`/`defense`/`arm1`/`arm2` read relative to base on the lawn; the attack half is
    **not** reintroduced (architecture decision 3 — removed by `2b9fb2c2`).
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter BaseRelativeRead`.
  - Files: `AptitudeReadFunctions.cs`, its test.

- [ ] **LW2.4 — `lawn-combat-baseline`: `combatBaseline` arm + injector pass** · M · deps: LW2.2 · *(spec: lawn-combat-baseline)*
  - Acceptance: a lawn-shaped Hub's accuracy/crit contests equal a battle Hub's at the same Θ;
    `combat.defense.omni` unchanged; `BattleBaselineSubsystem` registered exactly once per Hub.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "ActorHub|BattleBaseline"`; `.\scripts\guard-actor-hub.ps1`.
  - Files: `ActorHub.cs` (new opt-in arm), `CheatState.cs`, `data/tuning/mode-profiles.v1.json` (one key added).

- [ ] **LW2.5 — `zombie-power-source`: per-side Θ + `ZombossCommanderAllocation` wiring** · M · deps: LW2.2 · *(spec: zombie-power-source)*
  - Acceptance: lawn zombies read `Θ_player + thetaOffset` and `ZombossCommanderAllocation`, never the
    player's own commander build (fixes M5, ruling 1). Narrowed to wiring — the mechanism
    (`ZombossCommanderAllocation.cs`) already exists.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter ZombossCommanderAllocation`.
  - Files: `CheatState.cs:186`, `WaveCatalog.cs:176-177`, its test.

- [ ] **LW2.6 — `lawn-resource-scale`** · M · deps: LW2.1, LW2.2 · *(spec: lawn-resource-scale)*
  - Acceptance: the stamina pool is sized so it is genuinely emptiable at a real, in-budget allocation
    (M2's fix) — a pool an aptitude regen edge cannot outrace at every tested allocation.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter LawnResourceScale`.
  - Files: `data/tuning/battle-resources.v{n+1}.json`, its loader, focused tests.

### Checkpoint CL2
- [ ] `lawn-perf-budget.v1.json` exists and every perf gate reads it (LW1.1, re-confirmed here since
  the scale chain is where a regression would first show).
- [ ] `mode-profile`'s identity property holds: `CreateDefault` with no mode row composes bit-identically to today.

## Wave 3 — the two dependents

- [ ] **LW3.1 — `species-flavour-lawn`** · M · deps: LW2.3, LW2.4, LW2.5 · *(spec: species-flavour-lawn)*
  - Acceptance: layer-1a magnitude reach extends to general lawn actors, per `species-progression-map.md`
    §5's delegation — consumed by convergence, not built there.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter SpeciesFlavourLawn`.
  - Files: per the spec's own project-structure table.

- [ ] **LW3.2 — `basic-attack-cost-scale`** · M · deps: LW2.6 · *(spec: basic-attack-cost-scale)*
  - Acceptance: the basic attack's stamina cost is sized against `lawn-resource-scale`'s real pool, not
    a guessed constant.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter BasicAttackCostScale`.
  - Files: `LawnBasicAttackCostCharger.cs`, its tuning key, focused tests.

## Wave 4 — the live proof and close-out

- [ ] **LW4.1 — `lawn-scale-live-proof`** · M · deps: LW3.1, LW3.2 · *(spec: lawn-scale-live-proof)*
  - Acceptance: a real board, a clean player within allocation budget: hit/crit measured at battle
    parity, and a real exhaustion edge on an actor that also carries a live Hub bonus. Closes
    `lawn-combat-wire` proof 5 / L-N2 and confirms live-probe Task 22's fix under real play.
  - Verify: live, per `live-probe-standard.md` — real endpoints, real rows, read back through the
    normal path, never a fabricated debug response.
  - Files: none new; a research write-up under `docs/research/perf/`.

- [ ] **LW4.2 — `rider-default-on` close-out** · S · deps: LW4.1, LW1.1 · *(spec: rider-default-on)*
  - Acceptance: both halves of the module's own contract are true — cost (already shipped) and scale
    (LW4.1) — before this module is called closed. `lawn-perf-budget.v1.json` is the real ceiling every
    gate reads, replacing the commit-message figure.
  - Verify: `.\scripts\verify-change.ps1 -Paths <changed> -Session <id>`.
  - Files: doc-only pointer updates in `lawn-playable-map.md` marking the module closed.

### Checkpoint CL3/CL4
- [ ] `lawn-scale-live-proof`'s live measurement is recorded with real numbers, read back through
  overlay telemetry, not a debug fabrication.
- [ ] `rider-default-on` reads "closed, both halves" in `lawn-playable-map.md`.
- [ ] No golden moved anywhere in this plan (the lawn has none per `lawn-combat-baseline`'s own spec) —
  if one did, that is a defect report, never a re-bless.

---

## Cross-program notes (convergence files not edited here)

- `SP6.6` and `SE4.31`–`SE4.36`: see the plan's own Cross-program edges section. Neither is a file this
  todo's tasks touch.
- `combat-ai`'s wave 4 reads this plan's module list for sequencing context. **Corrected 2026-09-21 (lane
  `combat-ai-3`, measured):** only `CAI4.1`/`CAI4.2` depend on no single `LW*` task — `CAI4.7`'s own entry
  condition is that `gk-core/data/tuning/lawn-perf-budget.v1.json` **exists** (its `lawn.ai.decide` share is read
  from it), and that file is `LW1.1` and does not exist today (`ls gk-core/data/tuning/` holds only
  `combat-ai.v1.json`, `siege.v1.json`, `siege.v2.json`). `CAI5.1` waits on `lawn-combat-baseline`
  (`LW2.4`) and `CAI5.3` waits on `LW1.4`-`LW1.6` plus the cap that `LW5.1` below adds to this todo.

---

## Routed in from `combat-ai` (lane `combat-ai-3`, 2026-09-21)

- [ ] **LW5.1 — `unique-deploy-cap`: the spec exists and this plan never scheduled it** · M · deps: —
  · *(spec: [../docs/architecture/creature-lawn-deploy/spec-unique-deploy-cap.md](../docs/architecture/creature-lawn-deploy/spec-unique-deploy-cap.md))*
  - **In-fence half LANDED 2026-09-23 (lane `lawn-1`), and this row stays OPEN.** Landed: the pure rule
    (`LawnUniqueDeployCap.TryAdmit`, per-empire reason first), its tuning record + hub + loader with the
    file's own `board >= perEmpire` invariant refused loudly at load, the two constants beside
    `GateReasons` (`cap.unique_per_empire`, `cap.unique_board`), `gk-core/data/tuning/lawn-deploy.v1.json`, and
    both host loads (server composition root + injector `RpgHost`) so the file has its reader (H7).
  - **Two wires still denied, and they are the whole remainder:** (1) the count query + the gate call are
    `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:150-250`, outside this lane's allowed paths —
    without it the rule has no production caller; (2) subsuming Zomboss's forked
    `scorer.maxConcurrentOwnUnits` needs `gk-core/tools/tuning/publish.py --drop-key` plus a published
    `zomboss-deploy-ai.v2.json`, and both `tools/**` and a non-`lawn*` tuning file are outside the fence
    (leaving the key behind would be dead config, which the repo forbids).
  Cause read: that spec's own header says *"Implementation home: `creature-lawn-deploy`, scheduled once in
  the backlog-clean-up lawn plan (`tasks/backlog-clean-up-todo.md` BCU2.4)"* and its status line reads
  *"**Status:** spec, 2026-09-20. Not built."* — yet this todo schedules 16 tasks (`LW1.1`-`LW4.2`) and
  none of them is this one, and `grep -rn "unique-deploy-cap" tasks/*-todo.md` finds only `BCU2.9`'s own
  *done* row (which authors the spec, not a task that builds it) and `combat-ai`'s cross-program note.
  It is a **hard prerequisite**: combat-ai's `CAI5.3` (flip `LawnCombatAiFeature`
  default-on) has it as precondition 1, because that program's decision budget was sized assuming five
  uniques per side.
  - Acceptance: that spec's own §5 / §6 — the one admission rule, reconciled with `ZombossDeployPolicy`,
    registered at `ssot-power-scale.md` §11.3, refusing with a reason and never dropping a deploy.
  - Verify: the spec's own Verify section; `guard-actor-hub.ps1` / `guard-single-writer.ps1`.
  - Files: per that spec's §5; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:150-250` is the one
    existing unique-deploy admission gate it extends.
  - **If the implementation home is read as `creature-lawn-deploy` rather than this plan, move this row to
    `tasks/creature-lawn-deploy-todo.md`** — the id and the cause survive the move. It is filed here
    because this is the plan the spec's own header names.

---

## Routed out of `lawn` (lane `lawn-1`, 2026-09-23)

- [ ] **LW5.2 — `regen-unit-trace`: the `resource.regen.*` coefficients are a per-round fit read per tick** · M
  · deps: LW2.1 · *(trace:
  [../docs/architecture/lawn-tuning-profile/regen-unit-trace.md](../docs/architecture/lawn-tuning-profile/regen-unit-trace.md))*
  Cause read: `gk-core/tools/CombatSim/ActionEconomy.cs:123-127` accrues `_regen[id] * rounds`, called once per
  round (`gk-core/tools/CombatSim/Analytic.cs:567`; `Simulator.cs`'s own round loop), while the runtime reads the
  same channel as **units per tick** (`gk-core/src/FusionRpg.Core/Stats/Derived/ResourceChannelReader.cs`,
  `ResourcePoolState`'s per-mille carry, `gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:475` with
  `TicksPerSecond = 10` at `:482`) — and `gk-core/data/tuning/aptitudes.v10.json`'s own `_meta.status` declares
  the coefficients were ported verbatim from that POC. At a basic attack's cadence (150 + 50 ticks,
  `gk-core/data/tuning/action-timing.v1.json`) the runtime accrues the same coefficient **200×** more often:
  M3, and the shape behind M2's measured symptom.
  - Acceptance: the coefficient table carries a per-tick unit (converted or re-fitted), the mismatch is
    gone at a named cadence, the unit is stated at every seam the number crosses, and battle's own
    measured behaviour is recorded as an observed consequence.
  - **Why it is routed out rather than done here:** the repair publishes `data/tuning/aptitudes.v{n+1}.json`,
    which is **outside lane `lawn-1`'s allowed paths** (`data/tuning/lawn*.json` only) and belongs to the
    class-system program's balance surface. It also moves **battle as well as lawn**, and
    `spec-regen-unit-trace.md`'s Boundaries require landing that alone and measured — never as a lawn-only
    scaling, which would leave battle reading the wrong unit and hide the defect one layer down.
  - **Routing note:** the owning program's todo was **not** edited — this lane cannot write
    `tasks/class-system-*.md`. The manager should route it to whoever owns `class-system`'s `aptitudes`
    tuning, or widen this fence to `data/tuning/aptitudes*.json`.
