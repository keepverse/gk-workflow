# spec — `battle-mode-parity`

**Module 8 of `solid-remediation`.** Register entries: **D3, D4, D5, D6**. Depends on `retaliation-shared`.

**The big one.** Sequenced after the math and the bag are correct — otherwise parity is proven against a
broken resolver, which is worse than not proving it.

## Objective

One subsystem set, one trigger set, one `HubInputs` shape across every mode, and the dead recompose
retired. After this module, "the same specimen fights with different numbers depending on the mode" is
false.

## The defects

**D3 — 9 of 13 atom triggers never fire in battle.** `OnDamageTaken`, `OnDeath`, `OnSpawn`, `OnTimer` and
the five match/board-economy triggers. The lawn raises all 13. Battle raises `OnActivate`,
`OnDamageDealt` (`BasicAttack.cs`), `OnGranted`/`OnRemoved` (`EffectBag.cs:277-301`). Rule 2 — the same
authored content behaves differently by mode.

**D4 — delve and siege compose with no `HubInputs` at all.** `Encounter.cs:206-212`,
`DistrictAssaultResolver.cs:360-385`; only `WebMatchService.cs:600-609` populates them. Rule 4.

**D5 — the compose paths do not share registration.** `BattleHubCompose` bypasses
`ActorHubBootstrap.CreateDefault` and registers neither `RpgProgressionSubsystem` nor
`StatusDerivedSubsystem`; the lawn registers no `StarLoyaltySubsystem`.
`BattleHubCompose.cs:15-17,41-64` vs `CheatState.cs:49-81` vs `UniqueActorHubCompose.cs:70-76`. Rule 4 —
per-mode stat vocabulary.

**D6 — the mid-battle derived recompose is a permanent no-op.** It runs every round against an input with
zero production writers. `BattleEngine.cs:481`; `BattleDerivedModifierLedger` has one construction-time
writer (`BattleRunState.cs:460`), `ActiveAuras` has none, `Host.AddDerivedContribution` is test-only.
Rule 2.

D6 is grouped here because it is the same seam: it is dead **because** the compose paths never populate
what it reads. Fixing D4/D5 either gives it real inputs or proves it should be deleted — and that is a
decision this module must make explicitly rather than leave running.

## The open question this module must settle

The ideal doc records it and the first draft of the map lost it in renumbering:

> **Whether `BattleHubCompose`'s omissions were ratified.** `BattleHubCompose.cs:15-17` asserts the bypass
> was deliberate, but that was a **byte-identity argument during the phase-1 fusion**, which is not the
> same claim as "battle should have no progression subsystem."

**Settle it against `decisions.md` before changing the registration.** If it was ratified, D5 is struck
with a reason. If it was not — and the comment's argument does not support the broader claim — D5 is
fixed. Either outcome is complete; leaving it unexamined is not.

## Shape

- **D5 is a share:** route the compose paths at one registration instead of three hand-rolled sets.
- **D4 is a wire:** the shape exists and two modes do not populate it.
- **D3 is an extend:** battle raises a subset; the trigger vocabulary is closed and already declared.
- **D6 is a delete or a wire**, decided by what D4/D5 leave behind.

## ActorHub — the load-bearing gate

This module touches the compose paths directly, so it is where a parallel composer is most tempting.

**Every mode composes through `ActorHub`.** Contribute via `IActorStatSubsystem` or a registered atom
reader with a non-empty GG-49 `ContributionSourceIds` grammar id, or consume Hub output. Never a private
fold, never a second composer.

`BattleStatComposer` was **fused and deleted 2026-09-13** (`69ba6a7b3`). It is a closed incident. Citing
it as precedent for a new mode-local composer fails the DESIGN-GATE checklist outright.

## Numeric

Derived magnitudes are `long`; widen before multiplying; overflow throws. Where a mode currently composes
without `HubInputs` and starts composing with them, magnitudes change — that is the fix landing.

## Tests to rewrite

Any test asserting a mode-specific stat vocabulary, trigger subset, or compose result is pinning D3/D4/D5.
Restate each to the contract.

The module owes a **mode-conformance test**: every registered mode drives the same mechanism set, so D4
and D3 cannot recur silently. Assert the **closed vocabularies** — 13 triggers, the registered subsystem
set — and say why each literal is pinned. Never assert how many actors, effects or rows a mode produced;
those are populations.

## Boundaries

- **Always:** settle the `BattleHubCompose` ratification question against `decisions.md` first
- **Ask first:** widening the trigger vocabulary. It is closed on purpose — `status.apply`-class kinds
  resolve their target from the event, and a match-scoped event has no ptr
- **Never:** a mode-local composer or a per-mode subsystem set "for now"

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Battle/** gk-core/src/FusionRpg.Core/Delve/** <tests> -Session solid-remediation-<date>
```

- [ ] `decisions.md` question settled, in writing, either way
- [ ] Delve and siege populate `HubInputs`
- [ ] One registration path; `guard-actor-hub.py` green
- [ ] All 13 triggers fire in battle, or each exception is named with its reason
- [ ] D6 is wired or deleted — not left running against nothing
- [ ] Mode-conformance test present and failing on a synthetic divergent mode

## Success criteria

The same specimen fights with the same numbers in every mode. Before this module that is false, and D4 is
the proof.

---

## T3.1 — the `BattleHubCompose` ratification question, answered (2026-09-17)

**Question:** `BattleHubCompose.cs:15-21` asserts the bypass of `ActorHubBootstrap.CreateDefault` was
deliberate. Was it **ratified**, such that D5 should be struck?

**Answer: no. The compose PATH was ratified; the SUBSYSTEM SET was not. D5 stands and T3.2 fixes it.**

### What `decisions.md` actually ratifies

The **ActorHub sole Hot compose gate** row (`decisions.md:51`) locks that every module reading or
writing actor combat/derived numbers goes **through `ActorHub`**, contributing via registered
`IActorStatSubsystem` / atom readers. Its 2026-09-13 amendment records the fusion:

> **✅ Fused 2026-09-13 (`battle-hub-fuse` T6):** `BattleStatComposer` is **deleted**; `BattleEngine`
> (and every delve/siege/web/expedition caller) composes exclusively through `BattleHubCompose`
> (ActorHub). The debt named above is **retired, not merely reduced** — the dual-compose defect this
> row records no longer exists in `src/`.

That ratifies **one composer**. It says nothing about which subsystems battle registers, and the
defect it declares retired is *dual compose*, not *subsystem divergence*.

### What the code comment actually argues

> *"Deliberately NOT `ActorHubBootstrap.CreateDefault`: battle composes no progression or status
> channels, so those subsystems stay unregistered and **parity with the old composer is
> channel-exact**."*

The load-bearing clause is the last one. That is a **byte-identity argument made during the fusion** —
the reason not to register them was to keep `BattleGoldenTests` from moving while `BattleStatComposer`
was being deleted, which the same row records as "goldens re-blessed **once**". It is not a ruling that
battle *should* have no progression or status channels. T3.1 anticipated exactly this distinction and
the code confirms it.

### The measured divergence (three call sites, three sets)

`CreateDefault` registers `RpgProgressionSubsystem` **unconditionally**, plus `StatusDerivedSubsystem`,
`StarLoyaltySubsystem`, `AptitudeSubsystem`, `AtomDerivedSubsystem`, `DraughtSubsystem`,
`ExpeditionInjurySubsystem` on opt-in.

| Call site | Registers | Missing vs `CreateDefault` |
|---|---|---|
| `BattleHubCompose.cs:38-64` — battle, delve, siege, web | its own four battle subsystems + Resource, Aptitude, Atom, StarLoyalty, Draught, Injury | **`RpgProgressionSubsystem`, `StatusDerivedSubsystem`** |
| `CheatState.cs:49` — the lawn | `CreateDefault` with atoms, status mods, resource baseline | **`starLoyalty` never passed** |
| `UniqueActorHubCompose.cs:70` — server sheet | `CreateDefault` with atoms, resource baseline, starLoyalty | **`statusDerivedMods` never passed** |

So the same specimen composes from a different subsystem set depending on where it is standing. That is
D5 verbatim, and it is rule 4 of the responsibility register — a mechanism one mode has and the others
do not.

### Consequence for this module

- **D5 is not struck.** T3.2 routes the three sets through one registration.
- ⚠️ **Expect goldens to move**, and that is the correct outcome rather than a regression: registering
  `RpgProgressionSubsystem` in battle is precisely the change the 2026-09-13 comment avoided in order to
  hold them still. Each mover is named and explained as this fix, per the module's own verification.
- The ratified part is untouched: battle keeps composing through `ActorHub`, and nothing here
  reintroduces a second composer.
