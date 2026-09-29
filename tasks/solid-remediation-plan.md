# Implementation plan — `solid-remediation`

**Program:** `solid-remediation` · **Branch:** `features/mega-merge` · **Written:** 2026-09-17
**Map:** [docs/architecture/solid-remediation-map.md](../docs/architecture/solid-remediation-map.md) ·
**Specs:** `docs/architecture/solid-remediation/spec-<module-id>.md` (18) ·
**Tasks:** [solid-remediation-todo.md](solid-remediation-todo.md)

## Overview

A wiring and ownership pass over shipped code, not a rewrite. The measured remedy mix is **11 wire,
7 share, 5 extend, 1 move, 1 build, 1 delete** — the structure is sound, the boundaries hold, and what is
broken is wiring.

Ultimate purpose, in one line: **make the layers actually connect, so a lawn run reflects the RPG.** One
battle engine resolves every mode; one ActorHub composes actor numbers once; a feature extends by
contributing to a gate rather than forking one.

## Operating model — decided, not assumed

| | |
|---|---|
| **Writers** | **One.** Owner ruling 2026-09-17: *"you do this one by one, only consider to deploy agents if they understand context, reason is this refactor task need comprehend this architecture."* |
| **Build-break permission** | **Granted**, and it holds because there is exactly one writer. `src` may be red **inside** a module |
| **Unit of green** | The **module**, not the task. A module ends green — builds, guards pass, scoped `verify-change.ps1` passes |
| **Live probes** | At module boundaries only. A live probe needs a build |
| **Recovery** | A module that cannot get green is `git reset` to its start commit and re-planned. Never left half-applied |
| **Session** | `solid-remediation-20260917`, created by **T0.1**. Every verification runs `-Session solid-remediation-20260917` |

**Agents:** the default is none. A subagent is considered only for a task whose brief is self-contained
and verifiable without architectural judgement — realistically the per-failure diagnoses in T0.3/T0.4/T0.5,
and T5.6's tool tests. Every refactor task stays with the single writer, which is the whole point of the
owner's ruling: this work needs someone who comprehends the architecture.

## No pre-work gates — and why that is deliberate

Checked against `planning-and-task-breakdown`'s *"Gates vs. checkpoints"*: a hard gate is reserved for a
genuinely **irreversible** action. This program has none.

Every decision that could have been a gate was **already ruled** on 2026-09-17 and verified against the
source of truth rather than assumed:

| Would-be gate | Status |
|---|---|
| Module gate = all-green vs known-red baseline | Ruled: all-green (module 1 exists to make it true) |
| Build-break permission / exclusivity | Ruled: granted, single writer |
| D14 disposition | Ruled: fix via `elemental-resolver`, not delete |
| D10 disposition | Ruled: promote to engine, ladder per mode |
| `file-move-tool` kept despite void justification | Ruled: kept, scoped to move **and** rewire |
| Lawn ladder starting numbers | Ruled: ship working values, *"default now, re-tune later"* |

**Nothing blocks starting.** The checkpoints below review work already done; they are not gates.

## Dependency graph

```
green-baseline
  ├─ battle-responsibility-guard ─────────────┐
  ├─ verification-boundaries-extend ──────┐   │
  ├─ stub-register / fe-debt-register     │   │   (created early, appended by every module)
  │                                       │   │
  ├─ elemental-resolver ◄─────────────────────┘
  │       └─ battle-effect-math
  │              └─ retaliation-shared
  │                     └─ battle-mode-parity
  │                            ├─ species-empire-scope ─ species-carrier
  │                            ├─ estimator-parity ◄────┘ (also needs verification-boundaries)
  │                            ├─ capture-as-extension
  │                            ├─ death-and-injury
  │                            └─ unified-clock
  ├─ vocabulary-single-declaration
  ├─ numeric-single-source
  └─ file-move-tool
```

`battle-mode-parity` is the fan-out point: five modules depend on it and none of them on each other.

## Phases

| Phase | Modules | Why grouped |
|---|---|---|
| **0 — Baseline** | `green-baseline` | The gate must mean something before anything is gated |
| **1 — Enforcement + registers** | `battle-responsibility-guard`, `verification-boundaries-extend`, `stub-register`, `fe-debt-register` | Change no behaviour. Safest possible first production changes, and everything after lands protected |
| **2 — The battle chain** | `elemental-resolver`, `battle-effect-math`, `retaliation-shared` | One seam, opened once. First player-visible change |
| **3 — Mode parity** | `battle-mode-parity` | The big one. Alone in its phase because five modules depend on it |
| **4 — Fan-out** | `species-empire-scope`, `species-carrier`, `capture-as-extension`, `death-and-injury`, `estimator-parity`, `unified-clock` | All depend on parity, none on each other |
| **5 — Independents** | `vocabulary-single-declaration`, `numeric-single-source`, `file-move-tool` | Depend only on the baseline. Deliberately last: low risk, no dependants |
| **6 — Close** | — | Registers closed, definition of done, live proof |

**Why Phase 5 is last rather than first.** It could run any time after Phase 0. Putting it last keeps the
risky work early, while there is most appetite for re-planning a module that goes wrong — and it gives the
program three low-risk modules at the end rather than a cliff.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| **`battle-effect-math` is inert** — measured: wiring `CombatMath` moved 0 of 13,943 tests, because `Finalize` returns unchanged with no `ElementPayload` and battle defaults it empty | **High** — the program's headline module does nothing | T2.1 is a spike that answers it before any code. `elemental-resolver` owns the payload seam and runs first |
| **`battle-mode-parity` is the widest change** and five modules sit behind it | High | Alone in its phase, with a checkpoint before the fan-out. Its `decisions.md` question (T3.1) is answered before registration changes |
| **`unified-clock` touches the injector hot path** where the no-round-trip invariant lives | High | Last in the fan-out; perf is an acceptance criterion, not an afterthought |
| **Flaky Data tests** — two cleared between runs with no code change, under 31 concurrent `dotnet` | Medium | T0.4 re-runs in isolation *before* diagnosing. A flake fixed as a defect is a change with no reason |
| **Citation drift** — specs cite `file:line` from a pre-merge measurement; D6's writer already moved 460 → 388 | Medium | Each module re-verifies its own citations as its first act. 45 bare citations already line-checked clean |
| **Scope creep into features** — `capture-as-extension` and `death-and-injury` both sit next to half-built features | Medium | Both specs state the refusal explicitly: relocate the mechanism, do not make it reachable |

## Definition of done

1. Every one of the 27 register entries **fixed, reassigned, or struck** — the map's *Register coverage*
   table is the checklist
2. `battle-responsibility-guard` and the verification boundaries **in CI**
3. Both registers **exist and are populated**, written as the work happened
4. **The live proof passes** — RPG Server Debug scope, an effect-driven hit on a live lawn at the
   300-zombie tier resolving through `CombatMath` rather than `PassThroughCombatMath`, read back through
   the normal path, with `vfx.tick` inside its budget

   > **⚠️ This clause has three parts, and two of them cannot be met as written. Measured 2026-09-17,
   > recorded here rather than quietly reinterpreted at the end** — the audit's own anti-cheat rule
   > forbids deciding a requirement is unnecessary, so it is restated with what was actually observed.
   >
   > | Part | State |
   > |---|---|
   > | Effect-driven hit resolves through `CombatMath`, read back through the normal path | **MET** — T6.3, 13/13, real lawn, current binary, read back via `debug.board-stats` |
   > | "at the 300-zombie tier" | **UNREACHABLE.** 300 spawn calls were accepted; the board held at **80**. That is the game's own cap, not a probe defect. The tier named here does not exist to be measured at |
   > | "`vfx.tick` inside its budget" | **NOT MET, and there is no budget to be inside.** `vfx-v2-spec.md` F8 already recorded *"`PerfSection.VfxTick` instrumented but no budget asserted anywhere"*. Measured: `vfx.tick` **2.513 ms/frame = 91.8%** of the whole injector loop, and `loop.tick` **2.737 ms/frame** against `perf-probe-plan.md` §0's locked ≤ 2 ms at 200+ entities — over budget at under half the entity count |
   >
   > **Neither shortfall is this program's to close, and both are handed off rather than absorbed.**
   > This program's entire surface in that window is the remaining **0.224 ms/frame** (~11% of the
   > budget), and `combat.dispatch` does not appear in it at all. Setting a VFX budget and attributing
   > the 2.5 ms is `vfx-v2`'s work: F8 is **reopened** in
   > [vfx-v2-spec.md](../docs/architecture/vfx-v2-spec.md) §2a with this measurement, its severity
   > corrected from Low, and the note that its acceptance criterion must be restated against a board
   > size the game will actually produce before it can be measured at all.
   >
   > The corresponding todo clause (Phase 2, *"Live proof, half 2"*) is left **unticked** for the same
   > reason — reworded into something passable is exactly what it must not become.

**How the live proof is set up** (it appears at CP2 and again at T6.3, and improvising it is how a probe
ends up proving nothing): the `live-lawn-quick-start` skill owns the cold start — server started as its
own process so it survives tool-call teardown, `deploy-play.ps1 -NoServer` for the injector, then
`POST /api/debug/lawn/quick-start`. The board setup is **Game Injector Debug** scope and is never the
proof; the proof is read back through the RPG Server path.

## Task index

**56 tasks** across 6 phases, in [solid-remediation-todo.md](solid-remediation-todo.md), numbered `T<phase>.<n>`.
(Was written as 57, which never matched this section's own phase table: 7+8+8+6+16+7+4 = **56**. Counted
against the todo 2026-09-17 — all 56 ids present, none missing, none extra, one heading covering two ids
(`T5.3/T5.4`). A task count is a closed, code-owned number, so it is pinned and reconciled, not estimated.)
Every module also runs the todo's **module-start ritual** first — start SHA, citation re-verify, exclusivity check.
Sizes: **XS** 1 file · **S** 1–2 · **M** 3–5. No task exceeds M by design.

| Phase | Tasks | Checkpoint |
|---|---|---|
| 0 | T0.1 – T0.7 | **CP0** — all twelve CI projects green |
| 1 | T1.1 – T1.8 | **CP1** — guards in CI, registers exist |
| 2 | T2.1 – T2.8 | **CP2** — effect damage resolves; live probe |
| 3 | T3.1 – T3.6 | **CP3** — mode conformance proven |
| 4 | T4.1 – T4.16 | **CP4** — fan-out complete |
| 5 | T5.1 – T5.7 | **CP5** — independents landed |
| 6 | T6.1 – T6.4 | **CP6** — program done |

## Architecture decisions carried into every task

- **ActorHub:** contribute via `IActorStatSubsystem` / a registered atom reader with a GG-49
  `ContributionSourceIds` grammar id, or consume Hub output. Never a private fold. `BattleStatComposer`
  is a closed incident, not a precedent
- **Assertions are contracts, never populations.** No test pins a derived count, an item total, generated
  text, or a per-cycle outcome. A pinned literal names a closed vocabulary and says why
- **Numerics:** `long` for integer magnitudes `P(Θ)` grows; widen before multiplying; overflow throws;
  narrowing is checked; divide by 1000 last
- **Generated seed data is never hand-edited** — fix the generator and regenerate
- **This program re-tunes nothing.** A new mechanism ships **working values** (*"default now, re-tune
  later"*) with an `_meta` note; re-tuning an existing number is out of scope
- **A test that pins a defect is rewritten to the contract**, never re-pointed at a new number
