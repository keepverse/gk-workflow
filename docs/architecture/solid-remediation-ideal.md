# SOLID remediation — the ideal

> ### ⚠️ Status line vs. what shipped (checked 2026-09-18)
>
> **This document's status line is not current, and it is the kind of wrong that costs a whole
> session.** Measured today: **map approved 2026-09-17**, **18 module specs** under `docs/architecture/solid-remediation/`, and a task list at **96 done / 1 open**.
>
> A status line reading *"no build authorized"* over a program that has already shipped invites
> the next session to re-derive work that exists — and its inventory of gaps is stale in the same
> direction, because a gap named before the build is usually closed by it. **Read this document
> for its reasoning and its decisions; never for its status, its gap list, or its counts.**
> Verify anything load-bearing against the capability map, the task list, and the code.

**Status:** idea phase, 2026-09-16. **Not a spec. No build authorized.**

**This is phase 2 of the SOLID program.** Phase 1 shipped as
`actor-hub-and-combat-power-solid-fixing` (T1–T23, five waves, build complete, awaiting close); its
ideal, map, plan, todo, runbook and evidence map stay as the trail. Phase 1 fixed one subsystem's dual
compose. Phase 2 is the owner's wider instruction: *"clean everything and make our repo follow SOLID
correctly."*

**Program id: `solid-remediation`** (owner, 2026-09-16). Plan and todo land at
`tasks/solid-remediation-{plan,todo}.md`, map at `docs/architecture/solid-remediation-map.md`. Phase 1's
artifacts stay closed and readable as the trail; the old name no longer describes the scope.

**All four open questions were ruled on 2026-09-16 — see §Rulings at the foot of this doc.** The
build-state answer changed the program's operating model, so read that first.

---

## Step 0 — the principles, in my own words, before anything else

Restated inline, because a downstream session reads this doc, not its links.

1. **Every RPG feature lives in the RPG layer. It is never built by changing what PvZ is.** We observe
   PvZ's events and contribute signed deltas; we never read its current state or rewrite it. As of
   2026-09-16 no term of the damage equation is written into PvZ at all, and the lawn transport is a delta
   over `hp` / `armor1` / `armor2`.
2. **One ActorHub compose, one read.** Actor combat derived numbers compose exactly once. A layer is a
   *source* of `DerivedModifier`s into that fold — never a stacking tier, never a second composer.
3. **One battle engine.** It is deterministic, it solves every battle logic, and a mode is a **driver,
   never an owner**: a mode may own its *loop*, never a *mechanism*. The engine **resolves**; it never
   **decides** — player control and AI are a separate system feeding it through `IIntentSource`.
4. **Two async systems, deltas not absolutes, record-then-drain.** Delay is the designed degradation mode.
5. **One power ladder.** Contests read `Θ`; magnitudes read `P(Θ)`. A private `f(level)` is the defect
   that let three incompatible curves ship at once.
6. **The balance surface is data**, in `gk-core/data/tuning/<domain>.v{n}.json`, never a `const`.
7. **No hard progression ceilings.** A cap on a magnitude is a progression ceiling until proven otherwise.
8. **Gameless-first is a capability**, not the pitch: every feature stays playable with Fusion closed.
9. **Seed → concrete.** The seed is shared, deterministic generator input; the concrete is per-player and
   produced by a real in-game event.
10. **SOLID is binding, and a decision that locks a violation is itself a defect** — including this repo's
    own prior decisions. That is the rule this whole program exists to apply.

**And the one that governs the method here:** SOLID is *"not a license to refactor everything for purity.
It is a ban on locking or extending SOLID-breaking shapes."* This program must not become a purity pass.

---

## Which loop this extends

None, and that is deliberate. `the-loops.md` asks a feature to name a loop; this is not a feature. It is
**maintenance of the machinery every loop already runs on**. Its player-visible payoff is entirely
second-order: reflect starting to work in a delve, a zombie reading its own empire's progression, an
effect-driven hit in battle actually rolling to hit. Each of those belongs to a loop; the remediation
itself belongs to none.

---

## What this is

**A wiring and ownership pass over shipped code, not a rewrite.**

The owner's scope, in their words:

> *"Scope is clean everything and make our repo follow SOLID correctly. Scope only apply for ship feature
> include haft build. Stub feature this need to find it own plan to update (not complete), a own file to
> track debt and remove stub."*

> *"You need to check the real scope, maybe a lot of feature already build well but wire wrong or wrong
> place that we can move file (build tool to move) and re-wire instead of delete and code new, that will
> be waste of effort."*

That instinct is correct, and the measurements below say it is **more** correct than it sounds.

---

## What already exists

Measured 2026-09-16 against the working tree. Counts are readings, not constants.

### The headline: the rot is not where it feels like it is

**1,246 C# files, ~95,000 lines.** I looked for structural rot mechanically — a file whose declared
namespace disagrees with the folder it sits in, which is the cheapest available signal for "this code is
in the wrong place."

| Finding | Count |
|---|---|
| Files scanned | 1,246 |
| Namespace ≠ folder | 85 |
| …of which are `FusionRpg.Data` using a flat root namespace **by convention** | 73 |
| …of which are `Injector.Bridges` / `Injector` host shims | 9 |
| **Genuinely filed under the wrong subsystem** | **3** |

The three:

```
src/FusionRpg.Core/Actions/BasicAttack.cs        declares FusionRpg.Core.Battle
src/FusionRpg.Core/Actions/TimelineDispatch.cs   declares FusionRpg.Core.Battle
src/FusionRpg.Core/Actions/TurnOrderRecord.cs    declares FusionRpg.Core.Battle.Timeline
```

All three are `partial class BattleEngine` bodies living under `Actions/`. **That is the entire
file-placement problem in the repo.** A "tool to move files" would have three files to move, and moving
them is a `git mv` plus nothing — the namespace is already correct, so no call site changes at all.

**So the remedy the owner hoped for — move and re-wire instead of delete and rewrite — is right, but the
"move" half is nearly empty. The work is almost all *wire*.**

### Built

| What | Evidence |
|---|---|
| **The hard boundaries hold** | `guard-dal.py` bans nine SQL-shaped regexes outside `FusionRpg.Data` with an **empty allowlist** — the injector genuinely cannot reach the database. `guard-power.py` empty allowlists. `guard-single-writer`, `guard-funnel-delta`, `guard-secondary-no-unity` all green |
| **The assembly DAG is clean** | `Contracts` depends on nothing; `Core → Contracts`; `Data → Contracts, Core, CheatCore`; `Server` is the only assembly that sees `Data`; the three injector hosts never do; `Launcher` stands alone |
| **One damage resolver** | `OverlayCombatCalculator`, two `Compute` call sites repo-wide. `BattleStatComposer` was the second and is deleted |
| **Mitigation primitives are already extracted** | `PierceFactor`, `AmpFactor`, `DivisiveMitigation`, `CapAvoidanceBand`, `ResolveBand`, `CombatProbability.Sigmoid` — each declared **once**. Every estimator calls them. **Nobody re-derives a curve** |
| **Targeting, resource pools, shields** | `TargetResolver` shared by five callers; `BattleRunState` uses `LawnActorResourcePools` *verbatim*, with a comment saying it deliberately chose that over a near-duplicate type |
| **Phase 1's own fix held** | `guard-actor-hub.py` refuses a new composer, and the dual-compose defect it was written for has not returned |

### Wiring gap

**This is where the whole program lives.** The 27 defects catalogued on 2026-09-16 across four audits,
sorted by the remedy they actually need:

| Remedy | Count | What it means | Examples |
|---|---|---|---|
| **Wire** — set a property, restore a caller, add a dimension to a key | **11** | The code is correct and unreached | D1 battle's bag never sets `CombatMath`; S5 `MaterialisePlayerSpecies` lost its only caller; S1 the species cache key has no empire dimension |
| **Share** — route a second implementation at the first, or alias it | **7** | Two owners for one mechanism | X1 status categories declared twice; X2 two element switches disagreeing on failure; D8 the reflect assembly written twice |
| **Extend** — reach a mechanism into modes that lack it | **5** | A mode-local mechanism that the law says is shared | D2 reflect lawn-only; D10 permadeath delve-local; D3 nine triggers dead in battle |
| **Move** — relocate a file, keep the code | **1** | Wrong place | D12 capture under `Delve/Wild` rather than as a battle-engine extension |
| **Build** — genuinely absent | **1** | No implementation anywhere | R4 the species level-to-magnitude rule. *(D11 equipment damage left this program on 2026-09-16 — owned by `species-gear-chain`.)* |
| **Delete** — dead vocabulary or dead code | **1** | Registered and unread | D14 72 per-element parry/block/reflect channels with no reader |

**Eleven wires, seven shares, five extends, one move, one build, one delete** — plus **D15**, the
lawn's two time bases, found after the owner's clock ruling and classed as a *share*. Nothing in that
table is a rewrite.

**And one defect left the program entirely.** D11, equipment damage in battle, is owned by
`species-gear-chain` (owner, 2026-09-16): *"species gear chain program own it, we don't need to touch,
but that program is haft build — after we merge them and refactor completely, they will continue they
program."* That is the correct shape for a half-built program under this operating model: **merge it into
the remediation branch, refactor it with everything else, hand it back.** It is in scope as *code to be
cleaned*, and out of scope as *a feature to be finished*.

### Real gap

**G1 — no stub register exists.** The owner asked for *"a own file to track debt and remove stub"* and
there is no such file. The closest things are per-program todo entries and inline refusal messages.

**G2 — the enforcement is presence-shaped, not ownership-shaped.** `guard-actor-hub.py` refuses a
second *composer*; nothing refuses a second *owner* of a battle mechanism. `guard-class-system.py:129-150`
is a **positive-presence** check — one symbol reference anywhere satisfies it — which is why a hand-copied
reflect formula passes it today, and it scans two filenames and never `tools/`.

**G3 — three trees have no verification boundary at all**: `gk-core/tools/CombatSim/**`,
`gk-core/tools/ProvePredictor/**` and `web/**`. Per `AGENTS.md` an unmapped production path is itself a
verification-boundary defect.

### The stubs — smaller and more honest than feared

`NotImplementedException` appears **14 times** in `src` and the web app. **Ten are in one file**,
`gk-core/src/FusionRpg.Server/DelveEndpoints.cs`, and every one of them names *why* it refuses and which finding
owns it:

```
"DomainStaleness needs validated_json parsed from a real dungeon_domain row -- none exists yet (D4.16)."
"No rung display-name registry exists anywhere in this codebase (D4.19's own finding)."
"ParentWorldTerms has never been built from live state anywhere (D4.21's own finding)."
```

**That is the correct stub pattern, not the rotten one** — refuse loudly with the reason and the owning
finding, rather than invent a value. The 355 textual matches for "stub" are overwhelmingly doc comments
describing something else (`progression.realm` stub); they cluster nowhere, at most 8 files in any
directory. **The stub problem is one endpoint file and the delve-stage Phase 5 it waits on.**

---

## Prior art, with numbers

Three anchors, and they point the same way.

### Netscape 6 — what "delete and code new" costs

Netscape rewrote its browser from scratch between 4.0 and 6.0. The result was a **three-year gap between
releases**, during which the competition took the market. Spolsky's two reasons are the ones that apply
here exactly:

1. **The crufty-looking parts embed hard-won knowledge** about corner cases and weird bugs.
2. **The rewrite blocks improvement** for its whole duration.

This repo's own code is full of the first: `BattleRunState` explaining why it reused
`LawnActorResourcePools` verbatim, `EntityStatWriter` explaining why `MakeChild` uses `CreatePrimitive`
(Il2Cpp generic `AddComponent` blows a type initializer), `ActorHudPool` explaining a LIVE regression from
2026-09-06. Deleting those files deletes the reasons.

Source: [Things You Should Never Do, Part I](https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/) ·
[Lessons from 6 software rewrite stories](https://medium.com/@herbcaudill/lessons-from-6-software-rewrite-stories-635e4c8f7c22)

### Branch by abstraction — the technique that makes the build-break unnecessary

The technique for *"making a large-scale change to a software system in a gradual way that allows you to
release the system regularly while the change is still in progress."* An abstraction layer is introduced so
**all existing references keep working**; new code uses the new object; existing call sites migrate
gradually. **Every check-in keeps the code releasable.**

Its own literature is explicit that the alternative — a long-lived branch — *"prevents both continuous
delivery and refactoring."*

Source: [Make Large Scale Changes Incrementally with Branch By Abstraction](https://continuousdelivery.com/2011/05/make-large-scale-changes-incrementally-with-branch-by-abstraction/) ·
[Patterns for Managing Source Code Branches](https://martinfowler.com/articles/branching-patterns.html)

### Google's Rosie — how a large change is actually shipped

Rosie's whole contribution is **sharding**: it splits a large set of changes into smaller pieces *"which
can be tested, reviewed, and submitted independently"*, letting Google land thousands of changes a day
across the monorepo. The detail worth stealing is the one that sounds like a failure: in **2013 Google
introduced a formal large-scale-change review process, and the number of commits through Rosie went
down.** A gate on large changes was judged worth the throughput.

Source: [Large-Scale Changes, *Software Engineering at Google* ch. 22](https://abseil.io/resources/swe-book/html/ch22.html) ·
[Why Google Stores Billions of Lines of Code in a Single Repository](https://cacm.acm.org/research/why-google-stores-billions-of-lines-of-code-in-a-single-repository/)

**All three say the same thing in different words: shard it, keep it releasable, never big-bang it.**

---

## The shape

### The remediation ladder — cheapest remedy that closes the defect

Ordered. A defect is fixed at the **highest** rung that closes it; dropping to a lower rung needs a reason
in the module spec.

| Rung | Remedy | Cost | Build impact |
|---|---|---|---|
| 1 | **Wire** — set the property, restore the caller, widen the key | hours | none |
| 2 | **Alias** — one declaration, the other becomes a reference | hours | none |
| 3 | **Route** — the second implementation calls the first | hours–days | none |
| 4 | **Extend** — reach the mechanism into the modes that lack it | days | none |
| 5 | **Move** — `git mv`, namespace already correct | minutes | none |
| 6 | **Build** — a genuinely absent mechanism | its own feature | none |
| 7 | **Delete** — dead vocabulary, with a proof of zero readers | hours | none |

**Every rung is build-safe.** That is not a coincidence — it is what the measurement above produced.

### On the build-break permission — GRANTED, and why the objection dissolved

The owner ruled: *"the plan need to be module by module accept src code cannot build when refactor until
it wire correctly."*

I argued against it, on one ground only: this tree runs **several agent sessions at once**, one problem
each, under a written session-boundary policy with a record per session in `tasks/sessions/*.json` — ten
were active when this was measured — and `deploy-play.py` runs `guard-injector-compile.py` on every
deploy. A `src` that does not build stops every other session, every live probe and every deploy.

**The owner answered by removing the concurrency, not by working around it** (2026-09-16):

> *"We will build in new session. I will be merge other branch when we build — make me make new branch
> first. We will only one who build it, so I will ask for other session merge they code first then stop."*

That is a better answer than any of the three options I offered, because the objection was never about
broken builds in the abstract — it was about *who else is standing in the tree.* With exclusive
ownership there is nobody else, and the permission costs nothing.

**The operating model this program runs under:**

| | |
|---|---|
| **Precondition** | The owner cuts a new branch. Every other active session merges its work into it and **stops**. `scripts/session-boundary-check.py` is clean and this program's record is the only `active` one |
| **During** | `solid-remediation` is the **sole writer**. `src` may be unbuildable inside a module, and only inside a module |
| **Per module** | A module ends green — builds, guards pass, its scoped `verify-change.py` passes. "Module by module" is the unit of green, not the unit of work |
| **Live probes** | Only at a module boundary, never mid-module, because a live probe needs a build |

> ⚠️ **The permission is conditional, and the condition is the whole argument.** It holds *because* this
> program is the only builder. If another session starts on the branch — or the owner resumes a parallel
> stream — the permission lapses and the fallback is branch-by-abstraction, which every rung of the
> ladder above already supports. A module must not assume exclusivity it has not checked.

**Even with the permission granted, prefer green.** The measurement stands: eleven wires, seven shares,
five extends and one move need no broken intermediate state at all. The permission is there for the few
modules that genuinely cannot be split — it is not an invitation to stop caring.

### The merge is the first unmeasured thing, and it changes the numbers

**Every measurement in this doc was taken on the current tree. The program does not start on the current
tree.** The operating model begins with every other session merging its work into a new branch and
stopping — and that merge is large.

Measured 2026-09-16:

| Branch | Commits | `src` files | Scale |
|---|---|---|---|
| `worktree-species-gear-chain-20260915-9afc` | 28 | **51** | 1,251 files, 42,237 insertions |
| `worktree-passive-tree-repair-20260915-7a1c` | 21 | **9** | 22,683 insertions |
| `worktree-achievement-title-20260915-7f3a` | 8 | **15** | 5,172 insertions — this is **layer 5a/5b** |
| `worktree-rift-gate-20260914` | 44 | 0 | docs and content |
| `story-scene-idea` | 37 | 0 | docs and content |
| `worktree-action-dist-phaseA-20260915-9d2b` | 7 | 0 | generated data |
| `worktree-empire-development-20260915-b7e2` | 2 | 0 | docs |

**Seven unmerged branches, 75 changed `src` files, roughly 70,000 insertions.** Ten session records are
`active`. Sixteen worktrees exist, three of them unclaimed `worktree-agent-*` leftovers the boundary
check already flags.

Three consequences, and none of them is optional:

1. **Re-measure after the merge, before `/spec` closes the module list.** The 1,246-file scan, the
   three-misplaced-files result and the defect register are all pre-merge readings. Four of those
   branches are half-built programs whose code is explicitly in scope, and 51 files from one of them have
   never been looked at by any of the four audits behind this doc.
2. **The merge is a program step, not a precondition that happens offstage.** Resolving conflicts across
   1,251 files of half-built work is precisely where a SOLID violation gets introduced by accident, and
   it happens *before* the guards in modules 1 and 2 exist. It needs an owner and a checkpoint.
3. **Three branches carry work this program has already reasoned about.** `achievement-title` is layers
   5a/5b, which `actor-layer-compose-ideal.md` records as "in build elsewhere" — after the merge it is
   in build *here*. `species-gear-chain` owns D11. `passive-tree-repair` touches layer 4.

### Scope boundary — three tiers, and only one is in

| Tier | Definition | In this program? |
|---|---|---|
| **Shipped** | reachable by a player today | **Yes** |
| **Half-built** | built, reachable, incomplete — or built and **dark** | **Yes** (the owner's *"include haft build"*) |
| **Stub** | refuses by design, waiting on a named external finding | **No** — register it, plan it separately |

**"Built and dark" is the category that matters most**, and it is bigger than it looks. Fusion picks are
built, validated, nine refusal codes, reachable from the FE — and render nothing, because one upstream
writer has no caller. That is not a stub. It is a shipped feature with a wiring defect, and it is squarely
in scope.

**And one more boundary, ruled 2026-09-16: back end only.**

> *"Solve the BE first. When it solid, we will make new plan to solve FE — but I don't think we really
> need, because the FE is ugly, so I want to refactor it almost completely. So we don't really do it now,
> but track it."*

So `web/**` is **out of scope for remediation and in scope for tracking**. That includes X4, the
C#/TypeScript sigmoid divergence — it is recorded, not fixed, because fixing a formula inside a surface
the owner intends to rebuild is effort spent twice. `gk-core/tools/CombatSim` and `gk-core/tools/ProvePredictor` stay
**in** scope for G3, since they are back-end trees.

This needs a second register beside the stub one — see **The FE debt register** below.

### The stub register

`G1`'s answer, and the owner asked for it by name. One row per stub:

| Column | Why |
|---|---|
| Stub id + `file:line` | where it refuses |
| The refusal message, verbatim | it already names the reason |
| The finding that owns it | `D4.16`, `D4.19`, `D4.21` are already cited in the code |
| The condition that removes it | what must exist before this can return a value |
| Owning program | who completes it, and its plan |

**The code is already more than half of this register** — the refusal strings carry the reason and the
finding id. The register mostly transcribes what `DelveEndpoints.cs` already says, and makes it countable.

### The FE debt register

The owner's *"track it"*, given a home. One row per FE-side defect or rebuild note, so that when the FE
program starts it inherits a list instead of a fresh audit:

| Column | Why |
|---|---|
| Id + `file:line` | where it is |
| What is wrong | the defect, or the reason the surface is slated for rebuild |
| Does the BE fix change it? | a divergence like X4 may simply disappear when the FE is rebuilt against the BE's own numbers |
| Survives a rebuild? | the distinguishing question — a duplicated formula does not survive; a wrong contract does |

**X4 is its first row**, and it is the row that shows why the register is worth keeping: the browser and
the engine disagree on the same sigmoid (roughly 1.0 percentage points against 23.1 for one input). If the
FE is rebuilt to consume the BE's computed value rather than recompute it, that defect is deleted rather
than fixed — which is exactly the owner's *"waste of effort"* argument applied to the FE.

### Module decomposition — one seam per module

Module by module, as instructed, with each module closing **one seam end to end** rather than one file:

1. `battle-effect-math` — D1. Battle's bag gets `CombatMath`. The single highest-value task in the program.
2. `battle-mode-parity` — D3, D4, D5. One subsystem set and one trigger set across modes.
3. `retaliation-shared` — D2, D8. Reflect becomes a mechanism, not a lawn feature.
4. `species-empire-scope` — S1, S2, S3, S7, D9. The empire dimension, kill attribution, and Zomboss earning.
5. `species-carrier` — S4, S5, S6. Layer 1 binds; the picks feature stops being dark.
6. `vocabulary-single-declaration` — X1, X2. Status categories and element ids declared once.
7. `estimator-parity` — D7, X5. Estimators call the resolver's primitives or are pinned to them.
8. `numeric-single-source` — X3. Pool regen. *(X4 moves to the FE debt register, not fixed here.)*
9. `dead-vocabulary` — D14. Prove zero readers, then delete.
10. `battle-responsibility-guard` — G2. The guard that makes rule 3 mechanical.
11. `verification-boundaries-extend` — G3, back-end trees only: `gk-core/tools/CombatSim`, `gk-core/tools/ProvePredictor`.
12. `stub-register` — G1.
13. `fe-debt-register` — the owner's *"track it"*, and the hand-off to the later FE program.
14. `unified-clock` — D15. The engine's clock module owns when a pulse happens on every board, including
    the lawn; the wall clock may only be what feeds it. Touches the injector's hot path, so it wants the
    guards and the mode-parity work landed first.

**Module 0 — `file-move-tool`.** Built **first**, during the window while other sessions are merging into
the new branch and stopping (owner, 2026-09-16: *"when I ask for other agent merge into new branch, you
will code that tool first"*). That window is otherwise dead time, and the tool is the one piece of work
that needs no exclusivity, because it writes no production code.

> I recorded that the tool has only three inputs today and that their namespaces are already correct.
> The owner has the measurement and asked for it anyway, which is their call — and building it in the
> merge window costs the program nothing it would otherwise spend. **Scope it to earn its keep:** move a
> file *and* rewire it — namespace, `using` directives across callers, and the project file if the move
> crosses assemblies — so it is worth reaching for the next time, not only this one.

Dependency: **10 and 11 should land early**, not last. A guard that exists before the fixes is what stops
the next feature re-opening them, and Google's own lesson is that the gate is worth the throughput.

---

### Three things every module owes, beyond its fix

**1. Expect to rewrite tests that pin the defect — and rewrite them to the contract, not the value.**
This is not hypothetical; it happened three times in one day while the audits were being written:

| Test | What it pinned | What it became |
|---|---|---|
| `GetOrBuild_always_rebuilds_from_build_delegate` | that the HUD cache rebuilt on every read | serves a clean ptr from cache; rebuilds only a dirty one |
| `The_feature_default_is_off` | a default that a measured perf pass had since cleared | pins the default *and* the CheatState-is-override-only boundary |
| `EntityFields12PlusGuardTests` | twelve fields written, asserted against **raw file text** | comment-stripped, so a retired write cannot pass as a live one |

The third is the dangerous shape and the rule this program needs: **a guard that reads source as text
cannot tell code from a comment.** Retiring a write the honest way — commented out with the ruling beside
it — left `Assert.Contains` passing on the comment. The change would have committed green while the guard
asserted the opposite of the truth.

> **The rule:** when a module changes behaviour a test pins, the test is rewritten to assert the
> **contract** — never edited to expect the new number. If the old test cannot be restated as a contract,
> that is a signal the change is wrong, not that the test is in the way.

**2. A before/after measurement where a fix makes an inert number start applying.** D1 is exactly this:
battle's effect damage will begin rolling to hit. The module owes the measurement, not a re-tune — see
§Tunables.

**3. A note in the module's own spec saying which of the two registers it added rows to**, if any. The
stub and FE registers are only useful if they are written as the work happens, not reconstructed at the end.

### If a module goes wrong

The exclusive branch makes recovery simpler than usual, and it is worth stating so nobody improvises:

- **Inside a module**, the branch may be red. That is the granted permission, and the recovery is
  `git reset` to the module's start commit — no other session is affected, because there is no other session.
- **A module ends green or it does not end.** "Module by module" is the unit of green: builds, guards
  pass, scoped `verify-change.py` passes. A module that cannot get green is reverted to its start commit
  and re-planned, not left half-applied for the next one to inherit.
- **The one thing that is never acceptable** is a red branch at a point where the owner might need a live
  build. Live probes happen at module boundaries; if one is needed mid-module, the module is finished or
  reverted first.

### When this program is done

Not "all 27 fixed" — that is a task list, not a definition. The program is done when:

1. Every defect on the register is **fixed, reassigned to a named owner, or struck with a reason.**
   D11 is already the second of those, and it is a complete outcome, not a deferral.
2. The **battle responsibility guard** and the **verification boundaries** are in CI, so the fixes cannot
   silently regress and the next feature has something to fail against.
3. The **two registers exist and are populated** — stub debt and FE debt — so the next two programs
   inherit a measurement instead of an audit.
4. A **live probe passes on the lawn** with the feature on, at the 300-zombie tier, because that is the
   scenario every one of these defects was found under.

---

## Order of attack

The owner delegated this (*"you choose optimized order"*). Ordered by **value per unit of risk**, with
dependencies respected and the enforcement deliberately early.

| # | Module | Why here |
|---|---|---|
| **0** | `file-move-tool` | The merge window. Needs no exclusivity — it writes no production code — so it costs the program nothing |
| **1** | `battle-responsibility-guard` (G2) | **Enforcement before fixes.** It changes no behaviour, so it is the safest possible first production change, and every module after it lands already protected. Google's own lesson: the gate is worth the throughput |
| **2** | `verification-boundaries-extend` (G3) | Same reasoning, and it *unblocks* later modules — `gk-core/tools/CombatSim` and `gk-core/tools/ProvePredictor` have no scoped verification today, and modules 7 and 9 need it to prove anything |
| **3** | `battle-effect-math` (D1) | The highest single value in the program: one property on an already-constructed object, and twenty channel families start mattering in battle. First module that changes what a player sees |
| **4** | `retaliation-shared` (D2, D8) | Same seam as 3 — reflect needs `ActorResolve` on the battle bag, which module 3 is already inside. Doing it separately would open the same file twice |
| **5** | `battle-mode-parity` (D3, D4, D5) | The big one. After 3 and 4 so the math and the bag are correct before the subsystem sets are unified — otherwise parity is proven against a broken resolver |
| **6** | `vocabulary-single-declaration` (X1, X2) | Independent of everything above, and X2 is a **silent-wrong-answer** risk: one element switch returns `""` where the other throws, so a missed element reads as a neutral matchup with no error |
| **7** | `estimator-parity` (D7, X5) | Needs a correct resolver to bind estimators to, so it follows 3–5. Needs module 2's boundary to verify `tools/` |
| **8** | `species-empire-scope` (S1, S2, S3, S7, D9) | S2 depends on module 5 having given battle a compose worth adding a species term to |
| **9** | `species-carrier` (S4, S5, S6) | After 8 — the carrier is only worth binding once the scope it carries is right |
| **10** | `unified-clock` (D15) | Riskiest: it touches the injector's hot path, where the locked no-round-trip invariant lives. Wants the guards, the mode parity and a green battle path behind it |
| **11** | `numeric-single-source` (X3) | Small, independent, no dependants |
| **12** | `dead-vocabulary` (D14) | **Last of the fixes, deliberately.** "Prove zero readers, then delete" is only safe once the earlier modules have stopped *adding* readers — module 5 in particular could give the per-element channels their first consumer |
| **13** | `stub-register` (G1) | Hand-off |
| **14** | `fe-debt-register` | Hand-off |

**Two orderings I considered and rejected.** Guards last, which is the instinct — it front-loads visible
progress, and it is how the defects got here in the first place. And D14 early, since deleting dead code
feels like a cheap win — but it is the one module whose premise (nothing reads this) another module can
falsify while it is in flight.

**The first player-visible change is module 3.** Modules 0–2 change no behaviour at all, which is also
what makes them the right place to prove the exclusive-branch operating model works before anything is
at stake.

---

## Tunables

**This program introduces no tunables**, and that is a property worth stating: a remediation pass that
starts changing balance numbers has stopped being a remediation pass. Where a fix makes a previously-inert
number *start applying* — D1 is exactly this, since battle's effect damage will begin rolling to hit — the
module owes a **before/after measurement**, not a re-tune. Any re-tune that measurement justifies is
`lawn-tuning-profile`'s or the owning feature's, not this program's.

---

## What this deliberately does not decide

- **Whether the delve's Phase 5 gets built.** The stub register names it; completing it is its own program.
- **Balance.** See above.
- **The species-progression design questions** — what a species level gives, what drives Zomboss's clock.
  Those are `species-progression`'s, and this program only fixes the scope and wiring underneath them.
- **Whether `BattleHubCompose`'s omissions were ratified.** `BattleHubCompose.cs:15-17` asserts the bypass
  was deliberate, but that was a byte-identity argument during the phase-1 fusion, which is not the same
  claim as "battle should have no progression subsystem." Module 2 must settle it against `decisions.md`.
- **FE architecture.** `web/**` appears here only for X4 and G3. The god-TSX / page-CSS problem is
  `gui-lego`'s, and `/idea-ui` is its gate.

---

## Rulings — all four cleared 2026-09-16

| # | Question | Ruling |
|---|---|---|
| 1 | Keep the build-break permission? | **Granted, under exclusivity.** New branch; every other session merges and stops; `solid-remediation` is the sole writer. The permission is conditional on that and lapses if it stops being true. See §On the build-break permission |
| 2 | Build the file-move tool? | **Yes, and first** — in the window while other sessions merge into the new branch. Scoped to move *and* rewire, so it is reusable. Module 0 |
| 3 | Is `web/**` in scope? | **No — back end only.** FE is tracked, not fixed, because the owner intends a near-complete FE rebuild. X4 moves to the FE debt register. `tools/**` stays in scope |
| 4 | Program id? | **`solid-remediation`.** New id; phase 1's artifacts stay as the trail |

### What the rulings changed about this program

- It is no longer a shared-tree program. It is a **serialized, exclusive-ownership** program, which is a
  different operating model from every other program in this repo and is the reason the build permission
  is safe.
- It gained a **module 0** that runs before exclusivity exists.
- It **shrank**: X4 left the scope, and with it the only TypeScript work.
- It gained a **second register**. There are now two debt lists this program produces and hands on — the
  stub register (G1) and the FE debt register — and neither is a fix list. Both exist so the next program
  inherits a measurement instead of an audit.

## Hand-off

Next is `/spec` — a capability map at `docs/architecture/solid-remediation-map.md`, then one module spec
per seam under `docs/architecture/solid-remediation/`, once questions 1–4 are answered. **The ideal doc is
where this phase stops:** no spec, no plan, no code here.

**The one sentence to carry forward:** the repo's structure is sound, its boundaries hold, its primitives
are already extracted once — what is broken is wiring, and wiring is fixed without breaking a build.
