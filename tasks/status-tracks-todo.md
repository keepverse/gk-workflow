# Todo: `status-tracks`

**Plan:** [status-tracks-plan.md](status-tracks-plan.md) ·
**Map:** [../docs/architecture/status-tracks-map.md](../docs/architecture/status-tracks-map.md) ·
**Ideal:** [../docs/architecture/status-tracks-ideal.md](../docs/architecture/status-tracks-ideal.md) ·
**Ledger:** [status-tracks-ledger.jsonl](status-tracks-ledger.jsonl) ·
**Packet:** [../docs/research/status-tracks/owner-decision-packet.md](../docs/research/status-tracks/owner-decision-packet.md)

**Status:** **All waves built and verified 2026-10-02.** Wave 2 was unblocked by the packet's
stated `K1` defaults, not by a human answer. Tasks prefix `ST`. A cross-program reference is written
`<prefix><id>`. Verification:
`python gk-core/scripts/verify-change.py --paths <paths> --session <id>`.

**Completion criteria + the reviewer's falsification list:**
[../docs/architecture/status-tracks-completion.md](../docs/architecture/status-tracks-completion.md).
Read §E before closing this program: a green suite that cannot be made to fail is the failure mode
these tests exist to catch, and one of them was nearly shipped that way.

---

## Wave 0 — the contract

- [x] **ST0.1 — `status-pulse-vs-project`: pin the two track shapes in one test** — assert a combat
  status pulses on the battle clock (apply → `Tick(now + period)` → exactly one `PulseHp`, instance
  gone after `ExpiresAt`) and a projection writes on transition only (apply → repeat `Sync` at an
  unchanged value → exactly one apply, no re-write; a changed stage → `ClearGrant` then `Apply`).
  Copy the shape from `StatusRuntimeTests.cs:9-39`; a projection `Sync` fixture from
  `ExhaustionPolicyTests.cs:112`.
  - Files: `gk-core/tests/FusionRpg.Core.Status.Tests/Status/StatusTrackShapeTests.cs` (new).
- [x] **ST0.2 — `projection-never-counts`: assert the negative rules** — no count or stack field on
  `StatusInstance`; `Refresh`/`Replace`/`Coexist` are re-apply policies (two `Coexist` applies of one
  id produce two independent instances, **not** an accumulated count); a projection applies
  attacker-less and with `BaseDuration 0` so it never expires on a clock.
  - Files: `gk-core/tests/FusionRpg.Core.Status.Tests/Status/StatusTrackShapeTests.cs` (new).
- [x] **ST0.3 — `one-tick-owner`: pin the tick's caller set** — assert `StatusRuntime.Tick` is driven
  from the battle's virtual `now` and that no new clock-bearing call site appears in `Core/`. A
  regression here is the exact defect this program exists to prevent, so it is a test, not a review
  note.
  - Files: `gk-core/tests/FusionRpg.Core.Status.Tests/Status/StatusTickOwnershipTests.cs` (new).
- [x] **ST0.4 — `no-wall-clock`: assert the clock ban holds** — no `DateTime.UtcNow`,
  `DateTimeOffset.UtcNow`, `.Now`, `Environment.TickCount`, `ElapsedDays` or `System.Random` under
  the track code; `BaseDuration 0` projections carry no `*_utc` persistence. Extends the existing
  `guard-clock-seam.py` allowlist with a reasoned entry if a seam is genuinely needed — never a
  silent pass.
  - Verify: `python gk-core/scripts/guard-clock-seam.py` plus the Core suite.

## Wave 1 — the two paths (parallel-safe)

- [x] **ST1.1 — `catalog-registration-points`: document and test the three that must agree** — a new
  id lands in `StatusCategoryRegistry.Map`, `StatusCatalogBootstrap.RegisterAll` **and**
  `status-catalog.v{n}.json`, or `StatusCatalogParityTests` (`Json_entry_ids_equal_Bootstrap_ids`,
  `Injected_catalog_matches_Bootstrap_kinds_and_payloads`) fails. Note the two counts most authors
  miss: `SingleDeclarationTests.AllStatusIds_is_the_locked_twenty_four_member_set` and
  `ResistanceEvaluatorTests.Bootstrap_registers_24_ids`. **Ships no new id.**
  - Files: `gk-core/tests/FusionRpg.Core.Status.Tests/Status/StatusAuthoringContractTests.cs`
    (new — the parity-drift and closed-vocabulary assertions live here, **not** in
    `StatusCatalogParityTests.cs`, which this row originally named and which is untouched and clean at
    `f41559a`; the existing guards it cites are asserted as *set pins* by reflection in the new file
    rather than re-implemented), `docs/architecture/status-tracks/` (one authoring page).
- [x] **ST1.2 — `grant-overlay-keys`: pin the authored overlay contract** — the keys
  `StatusEffectBridge.BuildApplyInput` actually reads (`periodMs`, `durationMs`, `amount`, `chance`,
  `status_icd_ms`, `tickBudget`, `spread`, `immunityTags`, `stat`) and the closed allowlist that
  throws on anything else at `EffectBag.Grant`. An example row that is not allowlisted fails at load,
  which is the trap that shipped once.
  - Files: `gk-core/tests/FusionRpg.Core.Status.Tests/Status/StatusAuthoringContractTests.cs`
    (new — every overlay-key assertion for this task is here: each documented key reaching
    `BuildApplyInput`, the no-timing-key defaults, the two `status_icd` spellings as one gate, and
    the unknown key refused at grant **and** the allowlist that refused it carrying every documented
    key. `StatusEffectBridgeTests.cs`, which this row originally named, is untouched and clean at
    `f41559a`).
- [x] **ST1.3 — `combat-coverage-reading`: record what the 24 ids actually cover** — a reading, not a
  build: which classic needs are covered today (DoT, HoT, CC-lock, stat mods, contagion), which are
  expressible-but-inert (`turn.haste` is legal but `classic-round` never reads `OrdersBySpeed`), and
  which are deliberately separate (shield). Shipped so the next author does not re-derive it.
  - Files: `docs/architecture/status-tracks/`.
- [x] **ST1.4 — `projection-host`: the reusable out-of-combat `Sync` host** — extract the apply /
  `ClearGrant` / idempotent-pre-read dance that `ExhaustionPolicy.Sync` and `NervePolicy.Sync` each
  implement, so a new track is a ladder function plus a caller rather than a third copy. **Behavior
  must be byte-identical to both**; a golden or parity test proves it, and no existing policy is
  rewritten in the same commit as the extraction.
  - Files: `gk-core/src/FusionRpg.Core/Status/StatusProjectionHost.cs` (new),
    `gk-core/tests/FusionRpg.Core.Status.Tests/Status/`.
- [x] **ST1.5 — `projection-refusals`: keep the anti-spiral guard** — a projection whose stage
  touches its own driving pool's regen channel is refused at construction, mirroring
  `ExhaustionPolicy.cs:59-66` and `NervePolicy.cs:68-74`. This is not runtime-owned; a host that
  drops it silently reintroduces the loop.
  - Files: as ST1.4.
- [x] **ST1.6 — `projection-atomicity`: assert at-most-one live instance per track per host** — the
  exclusivity `NervePolicy` gets from prefix-matching `nerve.` on the live scan. Import-time refusal
  already exists (`EventDeckPreflight.cs:287-288`); this pins the runtime read that backs it.
  - Files: `gk-core/tests/FusionRpg.Core.Status.Tests/Status/`.
- [x] **ST1.7 — `deferred-projection`: the deferral path is a supported answer** — assert the
  documented shape from `EventOutcomeDispatch.cs:66-77`: with no live `StatusRuntime`, the scalar
  still moves and the projection is deferred. A track that requires an always-correct status where
  no runtime exists is a design defect, and this test names it.
  - Files: `gk-core/tests/FusionRpg.Core.Status.Tests/Status/`.

## Wave 2 — the catalogue (blocked on `K1`)

- [x] **ST2.1 — `need-inventory`: score every candidate need under the locked rules** — thirst,
  temperature, morale, disease, sleep/fatigue, environmental poison. For each: pool vs projection,
  which `Never` clauses each violates, which HUD surface it can actually reach (a status can only be
  a token; only a pool publishes a ratio), and what it would cost. A reading with the reasoning
  shown, not a recommendation dressed as a finding.
  - ⛔ Blocked on `K1` for the needs whose carrier the answer decides.
- [x] **ST2.2 — `carrier-rule`: state the deciding question once** — *"does anything spend it?"* A
  need that becomes an action cost needs a pool; a need whose consequence is thresholded needs a
  ladder. Encode it so the next track is not re-litigated.
  - Files: as ST1.3's authoring page.
- [x] **ST2.3 — `closed-vocabulary-ledger`: record what a widen would cost** — a new status id moves
  **both** count lines (`status-ssot.md` §9 and `docs/design-gate/combat.md:14`) in the same commit,
  and a new `StatusKind`/`StatusPayloadKind` is a reviewed change. Recorded so the next widen is
  budgeted, not discovered.
  - Files: as ST1.3's authoring page.

## Cross-program notes

- **`buff-debuff-scope` is adjacent, not upstream.** It answers *which population an effect reaches*
  (WHERE × WHO); this program answers *what state an actor is in*. Its map is still
  `proposed, pending owner approval` — if it lands first, `track-catalogue` should cite its scope
  model rather than restate a population question.
- ~~**D1 in `battle-engine-ssot.md` §4 is the real combat-status gap, and it is not ours.**~~ **Struck
  2026-10-04: this was wrong, and it was wrong in the way a doc rot is always wrong — it outlived
  its own fix.** It asserted that a status pulse applies its authored number with no hit roll, crit,
  matchup, penetration or block, so DoTs bypass the combat resolver in battle. That was true of
  `battle-engine-ssot.md` as it stood and false of the code: **D1 was already fixed by
  solid-remediation T2.5** — `BattleRunState.cs:497` wires
  `Host.Bag.CombatMath = OverlayCombatMath.Create(resolveActor, rng: effectCombatRng)`, with
  `ActorResolve` at `:495` and the battle-seeded `effect-combat` stream at `:496`. A status pulse now
  resolves through the same math as a swing, which is the *point* of the track design in
  [status-tracks/carrier-rule.md](../docs/architecture/status-tracks/carrier-rule.md). Both
  `battle-engine-ssot.md` §4 and this note were corrected in the same change; the ADR row records the
  same correction. `ST1.3` does not claim the gap closed because it closed — it was never open.
- **`turn.haste` is legal and inert.** Writing it on a status today changes nothing under
  `classic-round`, which takes the non-`OrdersBySpeed` branch. If a haste status is ever wanted, the
  prerequisite is a battle **profile** decision, not a status decision.
- **No need may reintroduce a wall clock.** Anything shaped like elapsed-real-time decay has no legal
  home and is a product decision before it is a coding one.