# Deployment scope — status at the convergence head (2026-09-22)

**Session:** `arch-d-20260922` · **Head:** `15baa1454` (worktree `cmdc-arch-d`) · **Mode:** read-only survey.
**Question answered:** is *deployment* scope complete — general creature/unit, specimen, lawn, actor layer,
empire progression (the owner's five-part bar)?

**Answer: no. Four of the five parts have real work left, and two whole lanes were missing from the
register this doc supersedes.** Measured as **task blocks**, not checkbox lines (`TVB-F20`,
`tasks/reports/backlog-reconciliation-20260921.md`).

**Method.** Counted every todo's rows and classified each open row as *task block* / *gate line* /
*aggregate suite line* / *owner-only line*. Nothing was ticked. Every number below is a reading taken at
this head, reproducible with the quoted command. Two claims were tested rather than assumed — the injector
build (§3) and the boundary guard (§4) — and one scout claim is corrected.

---

## 1. Verified register

`<file>` = `tasks/<file>-todo.md`. Counts: `grep -c '^- \[x\]'` / `grep -c '^- \[ \]'`.

| Program | file | done / open lines | **open task blocks** | What the open lines actually are |
|---|---|---|---|---|
| **creature-seed** (`species-rank`) | `creature-seed` | 7 / 23 | **17** | 12 build tasks (1–12; Task 13 done) across 5 phases; 5 gate lines (Foundation, Seed side, Flow, Landing, Complete); 5 findings (GAP-4, RB-H1, TB-H1, TB-H2, CS-F1-a) + CS-F1-b owned by `keepverse-split` |
| **lawn / creature deploy** (Phase 4) | `creature-lawn-deploy` | 11 / 4 | **4** | T4.1–T4.3 `PARTIAL 2026-09-08`, T4.4 `TODO`; the 4 open lines are Checkpoint 4's acceptance. Phases 1–3 and Checkpoints 1–3 are **CLOSED 2026-09-07** |
| **lawn / playable-scale (LW)** | `lawn` | 0 / 24 | **17** | **Entirely unstarted** (plan approved 2026-09-20): LW1.1–LW1.6, LW2.1–LW2.6, LW3.1–LW3.2, LW4.1–LW4.2, LW5.1 + 5 checkpoint lines + 2 routed notes |
| **lawn / interactive chrome** | `lawn-interactive` | 19 / 1 | **0** | one deferred gate: *Checkpoint E — combat book full arm→Intent (deferred until action corpus)* |
| **action / specimen** | `action` | 144 / 12 | **3** | **T71** (M), **T72** (S), **T73** (XS doc propagation); the other 9 lines are Checkpoint M/N/O/Q/Q.1 aggregate suite lines, most marked **orchestrator-owned** |
| **deployment-hierarchy** | `deployment-hierarchy` | 0 / 14 | **10** | 9 build tasks (DH1.1–DH3.3, Wave 1 not started) + DH-B1 + 4 wave gates. The map declares **7 modules**; the todo schedules modules 1, 2 and 7 |
| **empire-progression** | `empire-progression` | 78 / 8 | **1** | **EP5.3** only (blocked as written, proof test + erratum requested, 2026-09-21); the other 7 are CP1/CP3/CP4 aggregate lines, two of them `test-fast.ps1 -AllDefault` |

**Actor layer** — the bar's fifth part, absent from the register, so measured here:

| Program | file | done / open | **real task blocks open** | Open lines |
|---|---|---|---|---|
| actor-hub + combat power SOLID fix | `actor-hub-and-combat-power-solid-fixing` | 188 / 1 | 0 | owner acceptance of program close (owner-only) |
| actor-hub enforcement | `actor-hub-enforcement` | 21 / 2 | **1** | *Lawn equip SourceIds as `equip:` without double-counting grants*; plus one presentation-only row (FE InspectSplit) |
| actor-hud | `actor-hud` | 79 / 10 | **1** (+4 optional) | **AUDIT-1** — *the host still reads `actor-hud.v1.json`, so the published v2 has no effect* (XS, a real wiring defect). The rest are owner LIVE eyeballs/sign-off, two optional content items, one perf publication |
| lawn-combat-wire | `lawn-combat-wire` | 159 / 4 | **1** | **L-N34** boot crash on HEAD (`8710d326`, not that program's code) + a proofs redo + 2 closed/deferred lines |
| combat-unification | `combat-unification` | 40 / 2 | 0 | two explicitly non-blocking content follow-ups (F2b, F2) |
| actor-sheet-derived / -shell | both | 6/0, 5/0 | 0 | closed |

**So "playable" is not gated by ~8 lines anywhere.** Counting task blocks: **creature-seed 17 ·
deployment-hierarchy 10 · creature-lawn-deploy 4 · action 3 · empire-progression 1 · actor layer 3** —
plus **lawn LW 17**, which the register did not list at all.

## 2. Two register corrections, and one omission

**(a) The lawn register missed a whole program.** `tasks/lawn-todo.md` (plan approved 2026-09-20, prefix
`LW`) is **0 of 17 tasks**, 24 open lines, waves 1–4 unstarted: `rider-default-on`, `summon-pool-integrity`,
`exhaustion-event`, `actor-liveness-refresh`, `mode-profile`, `base-relative-read`,
`lawn-combat-baseline`, `zombie-power-source`, `lawn-resource-scale`, `species-flavour-lawn`,
`basic-attack-cost-scale`, `lawn-scale-live-proof`. That is the largest unstarted lawn block and it is
*not* the same program as `creature-lawn-deploy` Phase 4 (which is the deploy/progression conformance
seam). The register's "lawn: Phases 1–3 done, Phase 4 PARTIAL" describes `creature-lawn-deploy` correctly
and the LW program not at all.

**(b) The actor layer is not clean.** The register named it as one of the five parts but gave no rows;
it has three real blocks (§1) and eight owner-only LIVE eyeball lines in `actor-hud` alone.

**(c) DH-B1's blast radius is overstated — corrected with a live repro.** The row
(`tasks/deployment-hierarchy-todo.md:97-112`) says *"Until then no lane can run an injector build — which
EP3.4/EP3.5 and any injector-facing Verify line needs"*, and the scout register repeated it as
"blocks injector-facing verification **repo-wide**". It does not:

```
dotnet build gk-fusion/src/FusionRpg.Injector/FusionRpg.Injector.csproj
  → NuGet.targets(198,5): error : Ambiguous project name 'FusionRpg.Injector'.   [reproduced, 0.59s]
```

The collision is real and its **cause direction is wrong in the row**: it says the three host projects
*"carry a `ProjectReference` to the injector"*, but the reference runs the other way —
`gk-fusion/src/FusionRpg.Injector/FusionRpg.Injector.csproj:10` references
`..\FusionRpg.Injector.BepInEx\FusionRpg.Injector.BepInEx.csproj`, whose `<AssemblyName>` is
`FusionRpg.Injector` (`FusionRpg.Injector.BepInEx.csproj:8`) — and the **host compiles the injector's
sources directly** (`:33-35`, `<Compile Include="..\FusionRpg.Injector\**\*.cs">`) rather than referencing
the project. What that means for the blast radius, each verified at this head:

- `FusionRpg.slnx` lists the three **host** projects only (`:7-9`) — it does **not** include
  `gk-fusion/src/FusionRpg.Injector/FusionRpg.Injector.csproj`, so solution builds never see two projects with one
  assembly name.
- `scripts/guard-injector-compile.ps1:29` builds `gk-fusion/src/FusionRpg.Injector.MelonLoader.39/*.csproj`, whose
  `<AssemblyName>` is `FusionRpg.Injector.MelonLoader.39` (`:9`) — no collision. `guard: injector-compile`
  is therefore **not** blocked (`injector-fallback` selects it for every `gk-fusion/src/FusionRpg.Injector*/**`
  path).
- `gk-fusion/tests/FusionRpg.Injector.Tests/*.csproj:33` references the **BepInEx host**, not the plain project; a
  graph that contains one of the two colliding projects and not the other has no ambiguity.
- CI has no injector build at all (`grep -n Injector .github/workflows/ci.yml` → no match; AGENTS.md
  records the same: *"`FusionRpg.Injector.Tests` needs interop refs and is not in CI"*).
- `scripts/deploy-play.ps1:215,294,297` builds the **BepInEx host** — the path the owner ships with.

Independent corroboration, from the row that filed it: `empire-progression-todo.md:538` records
*"the injector host builds. The row's literal `dotnet build src\FusionRpg.Injector` is red on DH-B1."*

**Corrected statement:** DH-B1 is a real defect — one project in the tree cannot be built — and it makes
**the literal command** in the verify lines of EP3.4/EP3.5 (and any DH3.x row that copies it) red. It does
**not** block `guard-injector-compile`, `injector-tests-fallback`, the solution, or `deploy-play.ps1`, and
"no lane can run an injector build" is false. The fix is one property (give the BepInEx host its own
`<AssemblyName>`, or keep the plugin-dll name and make the plain project not reference it) and needs the
owner only if the shared assembly name is deliberate.

## 3. What gates "playable" — the five-part bar

| Bar part | Gating work | State |
|---|---|---|
| **1. General creature / unit** | `creature-seed` Tasks 1–12 (the rank ladder, 5 phases) and **TB-H1** (721 of 906 anchors carry no `threatBand` → every real dungeon domain refuses on `domain.encounter:*`, so it also **blocks `party-dungeon` F1**). TB-H2 (C# readers still on `creature-threat.v1` after v2 shipped) is a second classification gap in the same axis | **Not ready** — 12 tasks + 3 findings |
| **2. Specimen** | `action` **T71/T72** (shared `ActionChoice` lookahead reaching both intent sources) + **T73** propagation; `deployment-hierarchy`'s Wave 1–2 (`deploy-carry`, `injury-tiers`) for persistent specimen condition; **EP5.3** for the AI default | **Not ready** — 3 + 10 + 1 blocks |
| **3. Lawn** | `creature-lawn-deploy` Phase 4 (T4.1–T4.4 + Checkpoint 4): exact-once unique lawn XP under replay/crash/redeploy and `EmpireGeneral` source-gating; **`lawn` (LW) 0/17** — scale, mode profile, exhaustion, liveness, rider default-on; `lawn-interactive` Checkpoint E (deferred on the action corpus → **T71/T72 unblock it**) | **Not ready** — 4 + 17 + 0 |
| **4. Actor layer** | `actor-hud` **AUDIT-1** (host reads `actor-hud.v1.json`, so published v2 is inert), `actor-hub-enforcement`'s lawn equip SourceIds row, `lawn-combat-wire` L-N34 boot crash; the rest is owner LIVE sign-off | **Nearly ready** — 3 blocks |
| **5. Empire progression** | Only **EP5.3**, which is blocked on an erratum ruling, plus 7 orchestrator-owned aggregate runs | **Ready but for one ruling** |

## 4. Sequenced recommendation

Order by "unblocks the most, costs the least, and cannot be done later". `[O]` = owner/orchestrator
decision, not a lane.

1. **`[O]` Rule on DH-B1's assembly name** (or state it is intentional). One property, then the row
   closes; it is the only thing making any verify line red for a build that is otherwise green.
2. **`[O]` Rule on EP5.3's erratum.** It is the last non-aggregate row in a program that is otherwise
   complete; a ruling closes empire progression's part of the bar.
3. **Lane A — `action` T71 → T72 → T73.** Small (M/S/XS), closes Checkpoint Q *and* `lawn-interactive`'s
   only open gate, and every `action` task is independent of the lawn/hierarchy work.
4. **Lane B — `creature-lawn-deploy` Phase 4 (T4.1→T4.2→T4.3→T4.4, then Checkpoint 4).** The
   lawn/specimen correctness seam; no new module, all four rows already scoped.
5. **Lane C — `creature-seed` TB-H1 first, then Tasks 1–12 in the plan's phase order.** TB-H1 is on the
   critical path of another program (`party-dungeon` F1) and its acceptance already names the
   before/after reading; the 12 tasks are the longest pole and should start early even though they finish
   late.
6. **Lane D — `lawn` (LW) Wave 1** (`lawn-perf-budget` + `summon-pool-integrity` +
   `exhaustion-event` + `actor-liveness-refresh`). Disjoint from A–C; run it in parallel, not after.
7. **`[O]`/owner-time batch — the `actor-hud` LIVE eyeballs** (8 lines) plus the program sign-off. They are
   owner-only; batching them in one sitting is cheaper than interleaving them.
8. **Lane E — `deployment-hierarchy` Wave 1** (`deploy-carry` → `injury-tiers`). G0's `decisions.md` half is
   already satisfied (`decisions.md:45` carried the `wound.*` amendment, `:46` the Deployment hierarchy
   SSOT row, both 2026-09-13); its two external acknowledgements (`loot-pack` sign-off, `CloseDelve`
   hook-slot) still need each owning program's confirmation before the wave opens.
9. **Lane F — `actor layer`** the three blocks (AUDIT-1, equip SourceIds, L-N34) with the owner batch.

**What this order buys:** the three smallest decisions and the two smallest lanes finish the *actor layer*
and *empire progression* parts of the bar first; `action` + `creature-lawn-deploy` close two of the
remaining gates and unblock `lawn-interactive`; `creature-seed` and `lawn` LW are the two long poles and
start in parallel rather than serially.

## 5. Open questions for the owner

1. **DH-B1:** is `FusionRpg.Injector.BepInEx`'s `<AssemblyName>FusionRpg.Injector</AssemblyName>` deliberate
   (the BepInEx plugin-dll name) or a copy-paste? Deliberate ⇒ the plain project's build stays red and its
   verify lines change; a copy-paste ⇒ rename the host's assembly and the defect closes. **Default:**
   leave both as they are and treat `dotnet build gk-fusion/src/FusionRpg.Injector` as a known-red literal.
2. **EP5.3's erratum** — accept the row's proof-test finding (the rung cannot close behaviour-preservingly
   under neutral beliefs) or ask for a different acceptance. Default: the row stays open and blocked.
3. **The `lawn` (LW) program** — it is approved and 0/17; does it run in parallel with `creature-seed` in
   this wave, or does it wait? It changes nothing about the order above except how many lanes are live.

## 6. What this doc did not verify

- No program's *evidence* was re-read: the register is a count of todo state plus the code checks named
  above. A row marked `[x]` is taken as closed.
- `deployment-hierarchy` G0's two external acknowledgements (`loot-pack` sign-off, `CloseDelve` hook-slot)
  are named, not confirmed — they belong to the wave that opens.
- The `world-map` / `party-dungeon` / `narrative` programs are outside the five-part bar and are not
  counted here, except where one blocks a bar part (TB-H1 → `party-dungeon` F1).
- The five suite/golden lines in `action` and the seven aggregate lines in `empire-progression` are
  orchestrator-owned runs; whether they are *green today* was not tested here.
