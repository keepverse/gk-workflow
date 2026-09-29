# Implementation plan: `build-preset`

**Map:** [docs/architecture/build-preset-map.md](../docs/architecture/build-preset-map.md) ·
**Specs:** [docs/architecture/build-preset/](../docs/architecture/build-preset/) (7 modules) ·
**Tasks:** [build-preset-todo.md](build-preset-todo.md) · **Task prefix:** `BP` ·
**Parent:** [summoner-convergence-plan.md](summoner-convergence-plan.md), lane B, after
[`empire-progression`](empire-progression-plan.md) (ruling R5: *"specced now, built after
`empire-progression`"*). The ruling fixes the **suggested** order. The **hard** dependencies are only the
modules the map names (table below).

## Overview

A build preset is the "save the whole lean" layer the Spine C Vision line names (`docs/guide/the-loops.md:55`).
It is a named, player-owned bundle of **references**: which creature is patron, who is fielded, which
aptitude preset sits on which scope, which item loadout sits on which actor, and which skills are
equipped. It is applied by calling each piece's **own** write gate at that gate's **own** price. It is not
a stat layer, not a second aptitude or gear library, and it adds no price of its own.

The work is seven modules in three waves, **32 tasks** and five checkpoints. **No pre-work gate.** The
one `/idea-ui` pass is a task (BP3.1). It blocks only the surface's layout, and nothing upstream of it.

**Verified against code 2026-09-18 (plan session `plan-ep-bp-20260918`):**
- No module is built. `gk-core/src/FusionRpg.Server/Gates/`, `ItemLoadoutEndpoints.cs` and
  `RpgStore.BuildPresets.cs` are absent.
- The item loadout library (`RpgStore.Items.cs:131-147`, `SaveLoadout`/`ListLoadouts`) still has zero
  production callers and no route.
- `tasks/item-todo.md` (P1.2 armoury) confirms that the loadout **apply** half is still deferred by the
  item program.
- `patron.v1.json` and `contracts.v1.json` load in the server `Program.cs`. `build-preset.v1.json` does
  not exist yet.

## Architecture decisions (from the map; not re-litigated)

- **D1. A composite of references, never a copy.** The aptitude and gear pieces point at rows in their
  own libraries. Validate-on-read shows a deleted reference as `Missing`.
- **D2. A closed piece vocabulary:** `Patron`, `Field`, `Aptitudes`, `Gear`, `Skills` (five members,
  pinned, with the reason).
- **D3. "Who you field" is the contract-bound set,** applied as an exact set. Wardens stay outside the
  diff.
- **D4. The preset adds no price and removes none.** The price equals the by-hand sum, computed by the
  same functions:
  - Species targets carry the player's spend-or-pay choice (R18).
  - Commander and unique targets pay in souls on a take-back (R18 with the owner's correction).
  - No target ever draws a free respec unless it is a species target.
- **D5. Apply is convergent, not one transaction.** Preview refuses the whole plan. Apply re-checks and
  runs a structural step order. Derived correlation ids make a retry charge nothing twice.
- **D6. Not a stat layer.** No `DerivedModifier`, `ActorHub` or `ContributionSourceIds` reference in the
  build-preset namespaces, and an architecture test enforces it.
- **Identity:** `rpg_build_preset` is born `(save_id, empire_id)` with a human-only API. This is
  `save-identity` mismatch 3 applied, so no migration is ever owed.
- **No `decisions.md` row is owed** (map §5 checklist).

## Dependency graph (modules)

```
[EP specimen-respec-price EP1.6–EP1.10] ─┐
[EP respec-free-counter  EP4.9–EP4.10] ──┼─► gate-services (the AptitudePresetActivation half only)
                                         │      patron / contract / action-loadout lifts: no external dep
item-loadout-apply  (no dep; the item program's claimed surface)
[EP commander-roster EP3.1–EP3.3] + [SE4.1–SE4.4] + [SE save-identity first slice SE4.11–SE4.14] ─► preset-store

gate-services ─┐
item-loadout-apply ─┼─► piece-appliers ─► apply-orchestrator ─┐
preset-store ──┘                                              ├─► preset-surface  (after its /idea-ui pass, BP3.1)
preset-store + item-loadout-apply ─► capture-current ─────────┘
```

## Suggested order and parallel lanes (suggested, not enforced)

R5 suggests starting after `empire-progression`. The table shows what each lane actually waits on, so a
builder may start a lane earlier where only the suggestion holds it back.

| Lane | Tasks | Hard deps (external) | Suggested start |
|---|---|---|---|
| **P1 — gate lifts** | BP1.1, BP1.2, BP1.3 (in parallel) → BP1.4 → BP1.5 | BP1.1–BP1.3: none. BP1.4 and BP1.5: EP1.10 and EP4.10 (specimen-respec-price and respec-free-counter) | after EP CP6 |
| **P2 — item loadouts** | BP1.6 → BP1.7 → BP1.8 | none. Check `tasks/item-todo.md` first: if the item program has built the armoury routes and apply, these close as consumed | any time. It fills a surface the item program claimed and never scheduled |
| **P3 — the store** | BP1.9 → BP1.10 → BP1.11 → BP1.12 | EP3.3 (commander-roster), `SE4.4`, `SE4.11`–`SE4.14` (the save-identity first slice: tables born `(save_id, empire_id)`) | after EP CP4 |
| **P4 — apply** | BP2.1, BP2.2 → BP2.3 → BP2.4, BP2.5, BP2.6 → BP2.7 → BP2.8 → BP2.9 → BP2.10 → BP2.11 | P1, P2, P3 | after CP1 |
| **P5 — capture** | BP2.12 → BP2.13 → BP2.14 → BP2.15 | P2, P3; BP2.15 also needs BP2.10 | parallel with P4 |
| **P6 — surface** | BP3.1 (can start any time) → BP3.2 → BP3.3 → BP3.4 → BP3.5 | P4, P5 | the `/idea-ui` pass runs early. Code follows CP3 |

**Parent hard edges:**
- **H7:** `build-preset.v1.json` and its server `Program.cs` load land in one commit (BP1.10).
- **H1 and H2:** none. No golden moves, and no `rpg_actor_progression` write.

**Spec-level orders:**
- BP1.4 lifts whatever the aptitude-preset activate route does **after** EP1.10 and EP4.10. Lifting it
  earlier would lift the unpriced route, and the lift would then have to be redone.
- `preset-store`'s target column stores the post-`commander-identity` actor grammar (map
  "Dependencies", hard).

## Phases

| Wave | Modules | Task ids | Sizes | Parallel-safe |
|---|---|---|---|---|
| **A** (`BP1`) | gate-services, item-loadout-apply, preset-store | BP1.1–BP1.12 | 8 S · 4 M | Yes. The three modules share only the server `Program.cs` registration lines, so rebase rather than race |
| **B** (`BP2`) | piece-appliers, apply-orchestrator, capture-current | BP2.1–BP2.15 | 8 S · 7 M | Appliers ‖ capture. The orchestrator follows the appliers |
| **C** (`BP3`) | preset-surface | BP3.1–BP3.5 | 1 XS · 2 S · 2 M | The `/idea-ui` pass runs in parallel with everything |

## Checkpoints (review points, not gates)

| # | After | Evidence |
|---|---|---|
| **CP0 — review** | before build | Satisfied by the ruled map (its one OWNER question was closed by R18) and the parent plan. It is a review point, not a gate |
| **CP1 — the gates are callable** | BP1.1–BP1.8 | 1. Patron set, aptitude activate, contract bind/release and the action loadout behave byte-identically through their services: the existing endpoint tests pass **unedited**. 2. An item loadout can be saved, listed, previewed and applied over HTTP, with a named conflict refusal and `force` reporting what it stripped |
| **CP2 — a preset applies** | BP1.9–BP2.11 | 1. A preset naming all five piece kinds previews at exactly the by-hand price. 2. A species target shows both options and applies the player's pick. 3. A commander or specimen take-back shows its soul price. 4. The preset applies, and a retry with the same correlation id charges nothing more. 5. Each layer reads back through its **own** route, never from the apply response (live-probe standard) |
| **CP3 — keep what you have** | BP2.12–BP2.15 | Capture, then apply on a changed build, restores the capture (aptitudes as a lean). The aptitude and gear parts are rows in their own libraries |
| **CP4 — the player can reach it** | BP3.1–BP3.5 | 1. Playwright: create, capture, preview (prices and refusals visible by name), apply. 2. The aptitude console is relabelled "Aptitude presets". 3. `docs/guide/mechanisms/build-presets.md` is rewritten from "Vision". 4. `.\scripts\test-fast.ps1 -AllDefault` green once. This is the end of a large feature, and the program crosses Core, Data, Server and Web |

## Cross-program edges

| Edge | Other program's task | Direction | Kind |
|---|---|---|---|
| `RespecPolicy.Quote`, `QuoteReallocation` and the priced `TryReallocateUnlocked` activation branches | EP1.6, EP1.8, EP1.10 (`specimen-respec-price`) | EP → BP1.4, BP1.5, BP2.5 | hard |
| `payWith`, `QuoteSpeciesRespecUnlocked` and the free empire respec stock | EP4.9, EP4.10 (`respec-free-counter`, after `empire-level`) | EP → BP1.4, BP1.5, BP2.5, BP2.9 | hard |
| The actor-reference grammar for commander targets, and `ForEmpire(EmpireRef)` | EP3.1–EP3.3 (`commander-roster`), `SE4.1`–`SE4.4` | EP/SE → BP1.9–BP1.12 | hard |
| `HumanEmpireOf`, `EmpireRef` | `SE4.11`–`SE4.14` (first slice) | SE → BP1.11 | hard |
| `RequireHumanEmpire` / `EmpireScopeNotWidened` (the shared Tier B refusal) | `SE4.37` (the helper), `SE4.40` (the presets and respec batch) | SE → BP1.11. Reuse the helper if it has landed; otherwise BP1.11 throws `EmpireScopeNotWidened` itself, and SE4.40 folds it in | order |
| The `active-preset` rung reads the binding that activation writes; the FE auto-assign mirror is already retired | EP1.2, EP1.5 (`assign-ladder`) | EP → BP (order) | order |
| `systemCopy` presets are referenceable like any aptitude preset | EP1.16 (`default-build`) | EP → BP (order) | order |
| The armoury loadout routes and apply (`spec-armoury.md:103-121,220`) | item program P1.2 (deferred apply half) | BP1.6–BP1.8 build it. If the item program builds it first, these close as consumed and `piece-appliers` calls that version | order |
| The one generic server-to-injector save-switch notice | `SP6.6` | BP adds no save-switch notice of its own. The surface refreshes on the existing gate events, and a save switch reuses `SP6.6` | order |
| The armoury G-C lock ("loadout membership implies lock") | item program | not built here (map X6). Once G-C lands, captured gear becomes salvage-locked | none |

## Tuning publishes this plan owns (parent §5)

| File | Version | Task | Keys | Parent §5 row |
|---|---|---|---|---|
| `build-preset` | **v1, a new domain** | BP1.10 | `softMaxBuildPresets` (32, matching `aptitude-presets` `softMaxPresets`) | not in §5 (no other publisher). The EP map's "Tuning version sequence" table lists it: *"v1, a new file · `preset-store` · no collision"* |

The first version of a new domain is authored with its module, as the spec states: `publish.py` edits an
existing domain and has no "create domain" mode. Every later change is `v{n+1}` through
`gk-core/tools/tuning/publish.py` (tunables-ssot T4). All the prices a preset charges stay in their own domains
(`patron`, `contracts`, `species-build`), which this plan never publishes.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| A "byte-identical" lift silently changes a gate | High: presets and by-hand clicks would diverge | Each lift's first acceptance is the existing route tests passing **unedited**, then a service-versus-route parity test |
| The item program builds the armoury routes concurrently | Med: two files serving one contract | Check `tasks/item-todo.md` before BP1.6. If it is built, close BP1.6–BP1.8 as consumed |
| The preset price drifts from the by-hand price | High: players would route every change through a throwaway preset | BP2.7's price-equality test (soul ledger, free-stock ledger and churn counters at one injected clock) is the program's contract. EP1.10 is its gate-level half |
| An interrupted apply leaves a half-applied build | Med | Convergence (D5): derived correlation ids and a retry test (BP2.11). Every partial result is reported piece by piece |
| Server `Program.cs` merge churn (four service registrations, two route maps, one tuning load) | Low | Rebase. `SE4.7` (the `Program.cs` split) may move these lines. Whichever lands second adapts |
| The "Build presets" label collides with the aptitude console | Low | BP3.4 relabels the aptitude console in the same release that ships this surface (X1) |

## Defaults shipped behind (no gates)

| Unknown | Default | Corrected by |
|---|---|---|
| Layout, host and pieces of the surface | Not built until BP3.1 records them. Everything upstream of the surface proceeds | BP3.1 |
| `softMaxBuildPresets` | 32, the sibling library's value | a later `publish.py` revision |
| Whether the item program lands the armoury routes first | Build them here, exactly to `spec-armoury.md` | close as consumed if theirs lands first |

## Spec content not turned into a task (and why)

- **The armoury G-C lock** (map X6) is the item program's salvage guard. It is recorded, not built.
- **A commander-seat piece** is excluded by the map, pending `commander-roster`'s final shape. Adding it
  later is a reviewed change to the closed piece enum.
- **Delve party and legion lineups** are chosen at mode start and are never a persistent set (D3), so
  there is no task for them.
