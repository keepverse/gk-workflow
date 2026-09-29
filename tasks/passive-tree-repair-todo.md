# Task list — passive tree repair

Plan: [passive-tree-repair-plan.md](passive-tree-repair-plan.md). Parent plan:
[passive-tree-plan.md](passive-tree-plan.md). Map:
[docs/architecture/passive-tree-map.md](../docs/architecture/passive-tree-map.md).
Workflow skill: [.agents/skills/seedsmith-passivetree-repair/SKILL.md](../.agents/skills/seedsmith-passivetree-repair/SKILL.md).

**Rewritten 2026-09-12** from a full distribution census, not an aggregate. Baseline:
42/42 trees `Fail`, **266/1,680 nodes bound (15.8%)**, 108 bound-but-inert, 75,697‰ budget unspent,
mechanism nodes bind at **2.1%** vs magnitude **29.5%**, tiers 8–10 are **100% mechanism and produce
nothing**, 75 of 101 chosen affixes cannot resolve, `FamilyExpandGen` refuses **94 of 125** families,
the binder **crashes**, and the corpus **drifts**.

**Owner direction (2026-09-12):** Bundle C, full — and **do not split lawn from battle**. The repo has
one battle engine for all gameplay mechanisms, so a tree contribution must reach that shared engine
and be correct on both read modes; "battle-only first pass" is not an option.

**Standing verification for every task:** the module's own tests green · `dotnet build` clean ·
`guard-single-writer`, `guard-secondary-no-unity`, `guard-funnel-delta`, `guard-dal` pass ·
`guard-power` where a magnitude or curve is touched · `python gk-core/scripts/audit-overflow.py` 0 critical ·
`python gk-core/scripts/audit-magic-numbers.py` 0 M1/M2 attributable to the task. For `gk-forge/tools/seedsmith` work,
add `python -m pytest gk-forge/tools/seedsmith/tests/adapters/trees`.

---

## ▶ RESUME HERE (state at 2026-09-15 — spec round landed, plan extended, `/build` resumes at V3-1)

**Committed and gated:** P0.1, P0.1b, P0.2, P0.3, P1.1, P1.2, P1.3, P2.2 (verb/operator separation,
`1fae4654` + follow-up `240f4e54`), P4.1, P4.2, P4.3a.

**Spec round 2026-09-15 (approved map + 5 specs, commit `ddc8ee5a`):**
`docs/architecture/passive-tree-repair-map.md`,
`docs/architecture/passive-tree-repair/spec-{pin-table-v3,status-anchor,interval-ledger,structural-rows,mechanism-carriage}.md`.
Owner inputs: both tracks; intervals are Milliseconds; status cliff fixed by rescale AND m1
floor; rate channels get per-channel v3 pins too. Key turn: anchors are authored BY this
program (no power-program session exists) as versioned data — pins, not curves.
Commits: `d352a027` `52ad4948` `bbe47eb1` `c82d6f5a` `c3ef3d9a` `bd5b651b` `38286a0d` `4e21bc2f`
(`ab1a1b56` cleanup) `1d76131f`.

**Measured gain from Phase 4:** `op 'more'` refusals 80 → 0; the binder no longer crashes; live bind
rate 15.8% → 24.2%. **But `readable = 0.0% of bound`** — every bound atom is `stat.modify` and the
resolver reads only `stat.derived`, so the tree still contributes nothing in play. That is P4.3.

**Confirmed live this session (`docs/architecture/passive-tree-ideal.md` §17):** the derived-side
consumption path is already fully built and tested end to end — lawn (`PassiveTree/Resolve/TreeAtomSource.cs`
→ `AtomDerivedSubsystem` fan-in) **and** battle (`Battle/TreeAtomSource.cs` → `BattleStatComposer`),
task B6/D6/D7. The Injector's own Hot `ActorHub` was *also* separately fixed to hydrate tree-bound
derived atoms live (`actor-hub-and-combat-power-solid-fixing` T13, concurrent session) — the derived
route was NOT the gap; the binder emitting the wrong kind was.

**Both §4 blockers are now RESOLVED by owner decision (2026-09-13):**

1. **P2.1 (mechanism-kind anchors) — ANSWERED: publish now.** The power program publishes
   `power-scale.v3.json` (R10, 20 channels) **and** a new `status.apply` chance/duration anchor. Real
   work, not yet built — Phase 2/3 are UN-DEFERRED and actionable. See P2.1 below (defer flag removed).
2. **P4.3 (kind fork) — ANSWERED: both kinds.** Derived route proceeds exactly as originally scoped
   (P5 + P3 dependency unchanged). Primary route is corrected from the original proposal — **not** a
   battle-side `FA1`/`BattleStatModifierLedger` bolt-on; it contributes through **`ActorHub`** as a
   registered `IActorStatSubsystem` (owner's own correction: *"it is actor hub, not battle engine"*),
   matching the repo's One-ActorHub-compose hard rule. Split out to **Phase 11** below because it is
   architecturally distinct work (a new Core subsystem, not a binder/resolver change) and because of
   blocker #3.
3. **NEW real blocker — `solid-run-20260912-eb53` (worktree `actor-hub-and-combat-power-solid-fixing`).**
   Actively fusing `ActorHub`/`BattleStatComposer` and relocating subsystem registration
   (`gk-core/src/FusionRpg.Core/**`, `scripts/guard-actor-hub.ps1`) — the exact surface Phase 11 needs to
   register against. Status as read this session: T1–T23 done, "program complete, owner sign-off
   pending," most recent commit enables agent-shell git merge — **close, not stuck.**
   **Named resolver:** owner merge of that worktree. **Default if this plan reaches Phase 11 before
   it merges:** skip Phase 11, ship Phases 0–10 (the derived route reaches full playability on its
   own), track Phase 11 as a standing follow-up. Phase 11 also needs its own `decisions.md` row
   (AGENTS.md: an architecture change that locks behavior) — write it only after the merge, against
   the merged subsystem contract, not before.

**L0 added — new Phase 10, not blocked, safe to build in parallel with everything above.**
`effect-pipeline` modules 11 `affix-power-class` / 12 `affix-channel-weights` — specced 2026-09-03,
still zero `src/` lines as of today. Not required for playability (P5's own vocabulary-restriction
task gets the tree readable without it), but the owner asked for it in this round: it fixes the
narrow, accidental 26-family vocabulary (Herfindahl 0.027) with a principled distribution.

---

**Standing rule:** a task that edits generated seed/generated JSON **without** a `src/` or
`gk-forge/tools/seedsmith` code change is not a repair. If the only change is data, it is class D/E and must
cite the code evidence that the pipeline is already correct.

**Standing rule:** a balance surface (`tier-bands.v{n}`, `power-scale.v{n}`, `bands.v1`) is
**published as a new version, never edited in place**. `bands.v1.json` is frozen; `power-scale` is at
v2; `tier-bands` is at v5.

**Standing rule:** cite `Battle*` files by symbol, never by line (other streams edit them).

**Standing rule (from the distribution):** do **not** fix the bind-rate metric by narrowing the
vocabulary first. The refusals are the honest signal. Expand the pipeline, then narrow to what
genuinely resolves.

---

## Phase 0 — reproduce and freeze the distribution baseline

### P0.1: Commit a distribution census command
**Spec:** repair skill §1, §2. **Description:** the plan §1 tables must be one command, not a
transcript, so every later phase reports a delta. It must report bind rate **by class, by tier, by
category, and by tree** — an aggregate hides the mechanism collapse.
**Acceptance:**
- [x] One command prints: trees, expected/bound/refused, by-class bind rate, by-tier mechanism %, by-tree bind rate, refusal buckets, unspent‰
- [x] The baseline is recorded with the exact commands and git revision
- [x] Binder crash, `FamilyExpandGen --check` drift, and the `wither` ungenerated node are captured verbatim
**Depends on:** none. **Scope:** S. **Done:** `d352a027` — `seedsmith trees census [--json]`.

### P0.2: Name the focused regression test each fix must ship
**Spec:** repair skill §8. **Description:** CI runs whole test projects and this repo has no
`Skip`-a-known-failure convention, so a committed red test breaks the build. **Each regression test
therefore lands WITH its fix, in the same commit** (repair skill §5 step 4: "add/update focused
regression tests that would fail on the old code"). This task fixes the *list* — what test proves what
— so every later fix task knows its acceptance test before it edits code:

| Defect | Test (must fail on the pre-fix code) |
|---|---|
| R1 vocabulary | `permitted_for_branch(b) ⊆ resolvable_family_ids` for all three tags |
| R2 `More` | a `more`-op atom resolves end to end; never reaches an `Enum.TryParse` failure |
| R3 pool channel | a pool-shaped `channel` resolves or refuses as a `BindRefusal`, never throws |
| R4 kind parity | a bound node's `KindId` is one the resolve path reads, for **both** kinds |
| R5 mechanism | a tier 8–10 mechanism node reaches `NodeAtom` and contributes |
| R7 mechanism kinds | a `status.apply` family expands with the `statusMagnitudeAndDuration` ladder |
| R8 `Replace`/`Flag` | the chosen semantics are named; no magnitude invented |
| R9 board/economy verb | `params.op` is read as a modifier only for kinds that own one |
| R10 curve | a Flat family on a curve-less channel refuses by name, not by crash |

**Acceptance:**
- [x] Each fix task below names its test, and the test is committed in the same commit as the fix
- [x] No test asserts a corpus count — the envelope/contract only
- [x] No test is committed in a failing state
**Depends on:** P0.1. **Scope:** S (the list; the tests ride with their fixes). **Done:** `d352a027` (census), `52ad4948` (re-counts).

### P0.3: Propagate the stale counts the specs still carry
**Spec:** DESIGN-GATE §3 evidence rule 6. **Description:** `spec-tree-language.md` §3 still says
16 kinds / 7 attach points / 98 affix families / 21 statuses; live it is 18 / 9 / 125 / 24. Correct
the citations in the specs this program touches, naming the counting command each time.
- [x] `spec-tree-language.md` §3 and `spec-tree-binder.md` §2 counted tables match a fresh count
- [x] Every corrected number names what was counted, not where it was quoted from
**Depends on:** none. **Scope:** S. **Done:** `52ad4948`.

---

## Phase 1 — corpus self-consistency (drift + not-yet-generated + provenance)

### P1.1: Resolve the three stale `family-expand` files
**Spec:** `spec-family-expand.md` §3.2 step 3. **Description:** `FamilyExpandGen --check` exits 1 on
`g-armour`, `g-precision`, `g-tempo`. Determine whether the source family file changed or the
generator did, fix the code if the generator is wrong, and regenerate through the real CLI. **Record
which of the two it was** — a stale generated file with a correct generator is class D; the reverse is
class A.
- [x] Root cause classified A or D with `file:line` evidence (two class D renames + one class B line-ending)
- [x] `dotnet run --project gk-forge/tools/FamilyExpandGen -- --check` exits **0**
- [x] The three files were regenerated by the CLI, never hand-edited
**Depends on:** P0.1. **Scope:** S. **Done:** `bbe47eb1`.

### P1.2: Classify the `wither` ungenerated plan node and add the envelope check
**Spec:** repair skill §2 (distinguish PASS/FAIL/NOT_MEASURED), §3 (class E). **Description:** measured
2026-09-12 in both directions: there are **zero** true orphans (no generated node outside a plan) and
exactly **one** ungenerated plan node — `skill.wither-def-t9-n1`, in `wither`'s plan but in no seed
document (39 of 40; zero ledger row). That is class **E**, an incomplete run, which the binder already
refuses correctly. The P0.1 census initially mislabeled it an "orphan"; this task corrects the
semantics (done in the census) and decides whether to finish the node through the real CLI now or
leave it for the Phase 8 regeneration.
**Acceptance:**
- [x] The census reports `orphanGeneratedNodeIds` (defect) and `neverGeneratedNodeIds` (class E) separately
- [x] Whole-corpus both-direction reconciliation is 0 true orphans, and a check fails if one appears
- [x] The decision on `skill.wither-def-t9-n1` is recorded: it is left for the Phase 8 regeneration (it is one node, the whole corpus is being re-rolled there anyway, and finishing it now would spend model calls on a node that regeneration replaces)
**Depends on:** P1.1. **Scope:** S. **Done:** `c82d6f5a`.

### P1.3: Establish uniform current provenance
**Spec:** `spec-tree-language.md` §5.1; PRIOR-SESSION work on `PROMPT_VERSION`. **Description:**
`PROMPT_VERSION` is `tree-language/3` but **zero** seed documents carry it: 20 `mixed`, 22 `/1`,
5 `/2`. `mixed` exists because the emit path stamps `mixed` + `promptVersionByNode`. Decide whether
the corpus must be re-generated under a uniform current version (it must, before Phase 8), and add the
guard that prevents a stale vintage from being reported as healthy.
**Acceptance:**
- [x] The intended vintage is stated, with the command that shows it (`trees census` → `tree-language/3`; 1,066 records are not current)
- [x] A check fails when a seed document's vintage is stale or `mixed` (classification + real-corpus envelope tests; `stale_vintage_trees()` is the gate input)
- [x] The regeneration scope is written down for Phase 8 (all 42 trees; the 1,066 stale records are the re-roll scope)
**Depends on:** P1.1. **Scope:** S. **Done:** `c3ef3d9a`.

---

## Phase 2 — expander: non-magnitude kinds (R7, R8)

### P2.1: Teach `FamilyExpansion` the mechanism-kind formulas — ✅ SUPERSEDED 2026-09-15 by the spec round

**Supersession note:** this task's "40 families / 40 refusals" census is stale — live
`FamilyExpandGen --check` shows **0** `no supported tier-magnitude formula` refusals (P2.2
re-bucketed the residue into curve/opWeight buckets). The real work splits three ways, each
with an approved spec: `status-anchor` (status.apply chance/duration + shares), `pin-table-v3`
(Flat GameUnits pins), `structural-rows` (19 Replace/Flag). Build those; do not rebuild this
task's shape. Original text retained below for reference.

**Owner decision (2026-09-13, /spec round):** publish the missing anchors now (Decision B, "publish
anchors now" over "rescope to magnitude-only"). This task is actionable; the anchors themselves
(`power-scale.v3.json`, the `status.apply` chance/duration anchor) are still real work — see P3.1 and
the new anchor sub-task below. **Verified 2026-09-13 during `/build full`, still accurate. This is a
data gap, not a code gap — do not implement by inventing a number.** The formulas' *shape* is locked,
but their *anchors* were authored nowhere as of this reading:

- `bands.v1.json` → `powerBand.channelFamilyGroups.statusMagnitudeAndDuration` has **no `formula` and
  no `sharePermilleOwnership`** key. It gives `twoLadderRule` (chance 1.75‰, duration 1.4‰ *mandatory*),
  a `memberFamilies` list, and a `workedExample` whose own `status` field reads
  **`"illustrative, inherited, not balanced"`**. There is no `m1` anchor for chance or duration.
- `docs/architecture/seedsmith/spec-numerics.md:210-212` states the other three groups (incl.
  `statusMagnitudeAndDuration`) **"have locked formulas and need their own shares… specced when their
  families are resolved."** The shares do not exist.
- `gk-data/packs/fusion/data/seed/items/_tuning/tier-bands.v5.json` has **no per-family chance/duration override surface**
  (keys are only `baseSharePermille`, `channelWeightPermille`, `opWeightPermille`), and
  `bands.v1.json`'s own `note` says a rider's family-specific chance ladder is *"recorded in the
  family's own tier-bands input, never this registry's default."*
- `sharePermilleOwnership` states the binding rule: *"A generator with no authored share for a channel
  must reject at import, not guess one."* The existing tool already follows it — its `BattleRuleset`
  curve lookup returns `null` for a channel it has no curve for and refuses honestly. (The bare
  this line used to carry was un-anchorable — several files share that basename and none of them at
  those lines is the tool this sentence means — so it is stated as behaviour rather than a wrong line.)

**The owner decision (plan §6 A1/A5, confirmed again 2026-09-13):** author the missing anchors as a
new published balance surface — a `power-scale.v3.json` curve for the magnitude kinds (already
R10/P3.1) **and** a chance/duration anchor for `status.apply` (new sub-task: `P3.1b`, see Phase 3).
Until the anchor is published, the honest behavior stays the status quo: refuse by name. No longer a
§4 stop — build P3.1/P3.1b, then this task.

### P2.1 (original task text, retained for reference): Teach `FamilyExpansion` the mechanism-kind formulas
**Spec:** `bands.v1.json` `statusMagnitudeAndDuration` + `familiesOutOfFourWaySplit`;
`spec-family-expand.md`; `spec-mechanism-wiring.md`. **Ask first** (owner confirms the formula
reading). **Description:** `TryReferenceBaseM1` (`FamilyExpansion.cs:253-284`) refuses everything whose
kind is not `stat.modify`/`stat.derived`. Implement the frozen registry's own formulas: `status.apply`
chance at `r = 1.75` and duration at `r = 1.4` (mandatory); `resource.delta`/`resource.economy`/
`spawn.entity`/`board.action`/`shield.grant`/`status.clear`/`grid.*`/`box.set` by
`familiesOutOfFourWaySplit`'s stated analogy. **40 families**, and every deep tier.
**Acceptance (SUPERSEDED 2026-09-15 — all four bullets below are retired, replaced by the
status-anchor spec + SA-1's DONE tick; the "40" census was stale, live was 0 tier-magnitude
refusals post-P2.2):**
- [x] SUPERSEDED: status.apply rows carry chance+duration at 1.75/1.40 — DONE as SA-1 (anchor file + data-driven branch, 14/20 expand)
- [x] SUPERSEDED: non-magnitude params intact — DONE as SA-1 (scalar duration, no op/amount keys) + P2.2 verbatim verbs
- [x] SUPERSEDED: 40 refusals → 0 — DONE (live count was already 0; residue re-bucketed honestly)
- [x] SUPERSEDED: purity/determinism — DONE (`--check` reproducible throughout; byte-compare tests green)
**Depends on:** P0.2. **Scope:** L. **Files:**
`gk-core/src/FusionRpg.Core/Effects/Atoms/Generation/FamilyExpansion.cs`, `FamilyExpansionTypes.cs`, tests.

### P2.2: Stop conflating modifier `op` with board/economy verbs (R9)
**Spec:** `bands.v1.json` `familiesOutOfFourWaySplit`; `FamilyExpansionTypes.cs`. **Description:**
`board.action` families carry `op:"cherry"|"fireline"|"freeze"|"doom"` meaning *which action*, and
`resource.economy` carries `op:"add"` meaning a verb. Reading those as modifier ops produces the
misleading `no opWeightPermille entry` refusal. Read `params.op` as a modifier **only** for kinds that
own one; carry the verb through unchanged.
**Acceptance:**
- [x] SUPERSEDED (verb families): carried verbatim + Flat-analogy wired (proven by test); the 11 real verb families still refuse — truthfully at the curve gate, and NO anchor covers board.action/economy verbs (no program owns their bases; filed as follow-up). No base invented here.
- [x] The 11 authored verb refusals vanish as `no opWeightPermille entry` refusals (live `FamilyExpandGen --check`: 0 remain); a modifier-op check still guards the kinds that have one (`stat.modify`/`stat.derived` only, `OwnsModifierOp`)
- [x] A test proves the two fields are separate (`FamilyExpansionTests`: verb-verbatim expansion, stat-kind guard, curve-refusal naming; 25/25 green)
**Depends on:** P2.1. **Scope:** M. **Files:** `gk-core/src/FusionRpg.Core/Effects/Atoms/Generation/FamilyExpansion.cs` (`OwnsModifierOp` + verb branch), `tests/.../Atoms/Generation/FamilyExpansionTests.cs` (3 new tests). **Verify:** `verify-change.ps1` core-fallback 13594/13595 (1 fail = pre-existing CRLF `DungeonLootTableSeedFileTests`, proven failing on clean tree).

### P2.3: `Replace`/`Flag` tier semantics (R8) — ✅ ANSWERED 2026-09-15, then FLIPPED to option (b)
**Verdict:** exclude by principle. Replace substitutes a constant where the ladder requires
`f(Θ)` — on contest channels it freezes one side of a parity difference (§2: level stops
cancelling), on magnitude channels it rots as `P(Θ)` climbs (PS-3, §5.1). Verified against
code: every combat channel registers `FlatSum` (`DerivedStatRegistry.cs:309`), whose composer
arm reads only Flat (`DerivedComposer.cs:42`) — Replace composes to silent zero, or D6 refuses
it at load as never-read (`AtomRowValidator.cs:343-348`). A pin *anchors the function* (§4.3);
Replace *discards* it. The unified specs (`spec-structural-rows.md`,
`spec-mechanism-carriage.md`) are marked superseded, retained as trail.
**Survivor:** Flag on `status.immune` (presence, not magnitude — needs no spec).
**Acceptance:**
- [x] EX-1 DONE 2026-09-15: `permitted_for_branch` excludes Replace/Flag ops on both branches (ladder citation in docstring; re-authoring as Flat re-admits with no code change); real-corpus test proves no permitted option carries a structural op; 10/10 vocab + 536 trees-dir green
- [x] EX-2 DONE 2026-09-15: expander refusal for Replace/Flag cites the principle (`excluded by principle … re-author as Flat`); guard test pins the wording; 32/32 expander green. Note: seedsmith pytest files have no verification-registry project (pre-existing infra gap) — verified by direct pytest runs, reported not mapped.
**Depends on:** decided (done). **Scope:** P5.1-sized + S.

---

## Phase 3 — expander: publish the missing channel curves (R10)

### P3.1: Author `power-scale.v3.json` — pins, not curves (was: request from power program)
**Spec:** `docs/architecture/passive-tree-repair/spec-pin-table-v3.md`. **Description:** no
power-program session exists, so this program authors the anchors (idea phase 2026-09-15).
One `(CMilli, PinValue)` row at Θ=20 per GameUnits channel (`arm1Max`, `arm2Max`,
`combat.shield.capacity/pen/toughness.*`), a per-second pin for `combat.shield.regen.*`, and
per-channel pins for the rate channels (owner: rates get pins too). `FlatReferenceBase`
reads the new file; §10 rows added; v2 untouched.
**Acceptance:**
- [x] V3-1 DONE 2026-09-15: v3 exists (14 pins: 8 GameUnits incl. `combat.power/defense.{variant}` + regen/s + 4 rate + 2 mult, each with reason, versioned, shared dial with v2); `FlatReferenceBase` reads merged pins (v2 curve + v3, collision refuses)
- [x] 15 previously-refused families expand (carapace/cruelty/elemental-defense/elemental-power/evasion/evd-shift/keen-edge/padding/plating/precision/shield-capacity/shield-pen/shield-regen/shield-toughness/stoicism); 0 newly refused; uncovered (`''`, intervals, zombieSpeed, Replace/Flag) still refuse naming the channel
- [x] §10 rows 35–36 added (count line 33→35); `guard-power` OK; T7 proven: regen diff 1645 insertions, 0 deletions
- [x] Evidence: hand-probe exact two tiers (evasion t1 12/24, t2 21/43 from pin 520); 16th unique anchor built (hollow-orchard-30-003 via shield-capacity.t2); 4 new PowerTuningTests + test-local v3 mirror; 108/108 affected classes green; pre-existing DungeonLootTable CRLF still fails (out of scope, tracked)
**Depends on:** spec round approved (done). **Scope:** M. **Files:** `gk-core/data/tuning/power-scale.v3.json` (new), `gk-forge/tools/FamilyExpandGen/Program.cs`, `ssot-power-scale.md` §10, tests.

### P3.1b: Author the `status.apply` chance/duration anchor — container rule 2026-09-15
**Spec:** `docs/architecture/passive-tree-repair/spec-status-anchor.md`. **Description:** balanced
chance-t1 + duration-t1 per member family (20 named in the registry), 1.75/1.40 ratios intact,
`sharePermilleOwnership` entry, TreeBinder stamps `NodeAtom.WhenJson` chance at bind (container,
NOT E43 — E43 stays untouched), m1 floor as data. The `effectiveApplyScale` rescale is
`StatusPolicy` runtime — external follow-up, not this program; `status.power/resist` families
stay excluded until it lands. New file beside frozen `bands.v1.json`, never an edit.
**Acceptance:**
- [x] SA-1 DONE 2026-09-15: anchor file exists (t1s 25‰/2000ms + all-20 SS3.4 mappings + m1-floor note; status.power/resist base deferred — bare stems unemittable, recorded); 14/20 expand (70 rows, g-affliction.json new, 0 existing files touched); 6 unauthored families mapped inertly (no entries — P1.2-class gap, not refusals); E43 status branch (data-driven) + WhenJson chance persisted via serializer when-arm (importer already read it); hand-probe exact (blighting t1 2000ms/25‰, t5 7683ms/236‰ stepwise); 81/81 lint+validator+status green; 30/30 expander green (4 new SA-1 tests)
- [x] SA-2 DONE 2026-09-15: §4.3 re-verified against shipped code — cliff gone (netFactor linear since T3.2, resistFromPowerRatio 1.0, duration/intensity split); verdict UNSUPPRESSED with corrected reading, prior text retained as trail; FE implementation noted as its own program's work
- [x] Missing anchor row refuses naming the family (T5 — proven by test); `--check` exits 0
**Depends on:** spec round approved (done). **Scope:** M (SA-1) + M (SA-2).

### P3.1c: Classify the interval channels — NEW 2026-09-15 (`interval-ledger` spec)
**Spec:** `docs/architecture/passive-tree-repair/spec-interval-ledger.md`. **Description:**
`attackInterval`/`produceInterval` are Milliseconds (owner) — write the ledger row with its
verified consumer, complete the `channel-policy/defaults.json` stub entries with reasons, and
price Flat families on both channels. Fourteenth class only with proof (default: none needed).
**Acceptance:**
- [x] IL-1 DONE 2026-09-15: ledger Milliseconds row extended (attackInterval → SpeciesTempoProjection/BattleTempoSubsystem; produceInterval → StatComposer.Interval) with inversion note; policy stub completed (attack 1500ms read from SimEngine 1.5f, produce 24000ms economy-tick order P9-checked, direction + reasons); Flat families on both price (quickening/flourishing, +10 rows, g-tempo.json modified); hand-probe exact two tiers (quickening t1 36/70 from m1 53; flourishing t1 563/1117 from m1 840); E43 synthetic test + mirror policy arm; 65/65 expander+lint green; no fourteenth class
**Depends on:** spec round approved (done). **Scope:** S.

### P3.2: Publish the missing `opWeightPermille` rows (if any remain)
**Spec:** `tier-bands` `_tuning`. **Description:** after P2.2/P2.3, re-measure the op refusals. Any
real modifier op still missing a weight gets a row in a **new** `tier-bands.v6.json`, with the value
justified by the existing ladder rather than invented. If none remain, close this task with the zero.
**Acceptance:**
- [x] P3.2 DONE 2026-09-15 as moot: opWeight keys are exactly Flat/Increased/More; Replace/Flag are excluded by principle (no rows owed, none authored); v1–v5 untouched, no v6 needed
**Depends on:** P3.1. **Scope:** S–M.

### P3.3: Add the four missing channel pools (D)
**Spec:** `spec-channel-pool.md` §6.1 (the 12-pool list and the add-one rule). **Description:**
`combat.power.pierce.{variant}` and `combat.power.overflow.{variant}` are named by 4 families with no
pool, and the spec's own §6.1 states the add rule. Note the spec also records these two stems as **not
registered channel families** — verify which is true before adding a pool.
**Acceptance:**
- [x] P3.3 DONE 2026-09-15 as answered: verified against `DerivedStatChannels` — neither `combat.power.pierce.*` nor `combat.power.overflow.*` is registered (only prose mentions); per the task's own fork, no pool is authored for an unregistered stem; the 4 families stay honestly curve-refused; registration filed to the derived-stat program as follow-up (not this program's channel to invent)
**Depends on:** P3.1. **Scope:** S.

### Checkpoint: spec-round parallel set (V3-1, SA-1/SA-2, IL-1) + exclusions (EX-1/EX-2) — DONE 2026-09-15
- [x] Each task's spec success criteria met on real data (`--check` exits 0 throughout; 305 rows, 64 refused honestly)
- [x] No pre-existing emitted row changed value (T7 — regen diffs additive: +1645/0 V3-1, status/interval rows new files or additions)
- [x] Exclusions recorded as vocabulary with the ladder citation (EX-1 in picker, EX-2 refusal wording)
- [x] Committed per task with explicit paths (1fae4654 → b084c6e series)

### Checkpoint: mechanism live (MC-2) — BLOCKED (see MC-2 line: no executor). Human review of the
blocked mapping happens with this close-out, not before P7.1 (which is blocked on the same wall).

---

## Phase 4 — binder robustness and kind parity (R2, R3, R4)

### P4.1: Make `AffixComposer` handle pool-shaped channels without crashing (R3)
**Spec:** `spec-tree-binder.md` §7.1 (refuse, never repair); `spec-channel-pool.md` §3.2. **Description:**
`AffixComposer.ParseAtom` (`AffixComposer.cs:69`) calls `GetString()` on a pool object and throws an
unhandled exception, killing the run. A pool must resolve to a concrete channel deterministically
(§3.2's roll rules) or refuse as a named `BindRefusal`.
**Acceptance:**
- [x] `gk-forge/tools/TreeBinder --check` completes on all 42 trees without an unhandled exception
- [x] A pool-shaped channel is resolved with the §3.2 rule named, or refused as a `BindRefusal`
- [x] A test proves both paths; `--check` no longer crashes
**Depends on:** P0.2. **Scope:** M. **Done:** gate PASS 2026-09-13. Chosen disposition: **refuse by
name**, not resolve — `spec-channel-pool.md` §4 makes the roll effect-pipeline module 2's, and §3.4
prices a pool as `count × weighted_mean(member)`, so a bake-time pick would store a number the roll can
contradict. Verified: `--check` exits 1 (stale corpus, separate task) with **0 unhandled exceptions**
and 289 pool channels named; AffixComposerTests 10/10; PassiveTree 405/405; 4 guards green. Gate noted
the malformed-channel assertion was only weakly discriminating (word "channel") and the boxes were
unticked at gate time — both fixed in this commit.

### P4.2: Add `More` to the tree op vocabulary (R2)
**Spec:** `spec-tree-catalog.md` §2.3; `AtomKindRegistry.cs:517`. **Owner chose: add the member**
(Bundle C). **Description:** `stat.modify` legally supports `More` and it is priced (550‰); `NodeAtomOp`
lacked it, so every `more`-op node was refused at `TreeBinderRun.ParseOp`. Add `More`, and move the
derived-side M3 rule from a *structural* property (the member's absence) to a **named, kind-aware
refusal at both the load path and the bind path** — otherwise adding the member would silently convert
a loud refusal into the silent drop `TreeAtomSource.BoundAtomsFor` performs when
`AtomDerivedSubsystem.TryParseOp` fails.
**Acceptance:**
- [x] A `more`-op atom parses to a real op end to end and is priced (`A_more_op_stat_modify_atom_parses_binds_and_is_priced` asserts `NodeAtomOp.More` and `kMicro > 0`)
- [x] The `op 'more'` refusals drop to **0** (measured 80 → 0 on the live binder; live bind rate 15.8% → 24.2%)
- [x] A source-shape test proves both read modes map every `NodeAtomOp` including `More` (`Both_read_modes_map_every_NodeAtomOp_including_More`)
- [x] `NodeAtom`'s doc comment states which kinds own which ops
- [x] M3 stays LOUD at both sites: `Derived_atom_with_a_more_op_is_refused_by_name_at_load` (loader) and the bind arm in `ChannelLegalityTests`; both proven to FAIL when the arms are mutated out
**Depends on:** P4.1. **Scope:** M. **Done:** gate PASS 2026-09-13 (round 2; round 1 was FAIL for missing
loader/pricing/source-shape tests and a stale doc comment, all fixed). Verified: focused 101/101,
full Core.Tests green (`13369/13369` as read at the gate — a reading, and it moves as other streams add
tests), `op 'more'` 80 → 0 with 0 unhandled exceptions, 6 guards green.

### P4.3a: Census counts READABLE atoms, not priced ones — DONE `4e21bc2f`

**Found while investigating P4.3, and it is the program's own instrument lying.** The P0.1 census's
"inert" metric counted atoms the binder *priced*, but the resolver reads only `stat.derived` — so 243
bound nodes reported healthy while contributing nothing. By the repair skill's own §0.1 definition
("bound nodes carrying zero READABLE atoms"), the real number is **266/266 unreadable, readable 0.0%
of bound**. Fixed: `bound_with_readable_atoms`, `bound_atoms_by_kind`, `unreadable_share_permille`,
a named `DEFECT` line when no readable kind binds, and a test asserting `READABLE_KIND_ID` against the
resolver source so the census cannot drift from the thing it measures. 37 census tests, 545 tree tests.

### P4.3: Make binder and resolver agree on kind — DERIVED ROUTE ONLY (R4) — ✅ UN-DEFERRED 2026-09-13

**Owner decision, 2026-09-13 (/spec round): both kinds, confirmed.** Split in two, because the two
routes are architecturally different work with a different blocker:

- **Derived half — BLOCKED with evidence 2026-09-15 (not deferred, not skipped).** Live census
  this session: nodes pick derived families (precision ×60, evasion ×4) but every one of the 47
  `stat.derived` families emits pool-shaped or bare-stem rows — 0 emittable-concrete — so pool
  refusal (P4.1) stands on all of them. Pools resolve at ROLL time via effect-pipeline module 2
  (spec-channel-pool.md §4 forbids any other program implementing the resolver), which is unbuilt
  with no active session. The consumption path is proven green with synthetic atoms
  (TreeFanInTests + TreeAtomSource, 32/32); real content is starved upstream. Unblocks the day
  module 2 lands — no work in this program can substitute for it.
- **Primary half — moved to Phase 11**, `P11.1`. Corrected from the original proposal (a
  `FA1`/`BattleStatModifierLedger` bolt-on): the owner named the mechanism explicitly —
  *"it is actor hub, not battle engine"* — so the primary contribution registers as an
  `IActorStatSubsystem` on `ActorHub`, the repo's single compose gate for both lawn and battle
  (`decisions.md` "ActorHub sole Hot compose gate"). Blocked on the `solid-run-20260912-eb53` merge
  (see ▶ RESUME HERE) and needs its own `decisions.md` row, written after that merge.

No longer a §4 stop for this half. Unblocking order unchanged: P2.1/P3.1/P3.1b's anchor → P3 → P5 →
this task.

**Measured detail (2026-09-13, live bind):**

```
fresh bind (gk-forge/tools/TreeBinder --out):  bound=407  onlyModify=243  onlyDerived=0  empty=164
bound atoms by kind/channel:          stat.modify/atk: 261   stat.modify/defense: 76
                                      stat.derived: 0
resolve path (Resolve/TreeAtomSource.BoundAtomsFor):  `if (atom.KindId != "stat.derived") continue;`
```

100% of bound tree atoms are dropped by the resolver. The committed census reads 266 bound (lower
than the live 407 because the committed corpus is older than the current generator), of which
`readable=0.0%` — the number P4.3a's fix made visible.

### P4.3 (current scope, derived route only — primary route is P11.1)
**Spec:** `spec-tree-binder.md` §4.1; `spec-tree-resolve.md` §2.1, §12 test 15. **Owner answered:
both kinds — this task builds the derived half; P11.1 builds the primary half.** **Description:** the
binder must emit `stat.derived` for every node whose plan-assigned `channelFamily` is a derived
channel (R1/P5's job to align the picker; this task's job to align the emission and remove the silent
skip `Resolve/TreeAtomSource.BoundAtomsFor` performs today for `stat.modify`).
**Acceptance (original bullets SUPERSEDED 2026-09-15 — replaced by the derived-proof block
below; the emission half was already true, the proof half is blocked on module 2):**
- [x] SUPERSEDED: binder emits stat.derived for derived-family nodes — TRUE (rows emit; nothing to align in emission)
- [x] SUPERSEDED: TreeFanIn synthetic proof — DONE 32/32 (consumption path green, real subsystems)
- [x] SUPERSEDED: lawn/battle totals agree — PROVEN SYNTHETIC ONLY (same 32/32); no real derived bind exists to compare
- [x] SUPERSEDED: stat.modify stored-not-dropped — TRUE (92 bound, stored in NodeAtoms for P11.1)
**Depends on:** P4.2. **Scope:** L. **Files:**
`Binding/TreeBinderRun.cs`, `Resolve/TreeAtomSource.cs`, tests.

---

## Phase 5 — vocabulary alignment, now safe (R1)

### P5.1: Restrict the permitted affix enum to binder-resolvable families
**Spec:** `spec-tree-language.md` §4.2 step 6, §5.1; `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/vocab.py:17-25`'s own named blocker.
**Description:** after Phases 2–3 the resolvable set is far larger. `permitted_for_branch` must
return only ids that resolve to a generated `AtomRow`. The enum is the schema's `enum`, so an
unresolvable id becomes **unsampleable**, not rejected.
**Acceptance:**
- [x] P5.1 DONE 2026-09-15: `permitted_for_branch(b)` returns only binder-resolvable ids — resolvable computed from generated rows with per-op precision (template→pool excluded regardless of op; bare stems excluded; status.apply+status admitted (MC-1); Increased/More on concrete channels via identity; Flat needs a priced base from v3/v2/policy); live in pipeline (`generate_tree.py:118` feeds it); offerable 24 offensive / 15 defensive, both non-empty (measured after the bases-path fix)
- [x] Test asserts every permitted option is resolvable against real rows; count-identity updated to the offerable subset
- [x] Empty result raises `UnsatisfiableCell` naming branch+cell in `generate_node` (tested, pre-LLM)
- [x] P5.2 DONE: `classify_residue()` maps every unoffered family to closed reasons — live: 45 no-emitted-rows + 21 pool-channels-only + 19 structural-op + 0 bare + 0 unbased = 85 (taxonomy gained `unbased-channel` for concrete-but-unpriced; P3.3's pierce/overflow/zombieSpeed resolve into it); test pins taxonomy closure
- [x] P5.3 DONE: re-measured over the new enum — offerable 24/15 (uniform Herfindahl 0.042/0.067 vs old pick-concentration 0.027 over 101). Disposition: concentration is now BOUNDED by the offerable set; pick-spread within it needs a generation run — filed as quota/brief follow-up (no program session; tracked here, not built here)
- [x] Expander `does not exist` refusals are 0 (all 125 families read); tree-level picks of unauthored affixes (wither econ-*) are P1.2-class content gaps, counted in P5.2's no-emitted-rows residue, not expander misses
**Depends on:** built (P3.3's pool half remains refused-by-design pending module 2). **Scope:** M.

### P5.2: Reconcile the residue and record the boundary — FOLDED INTO P5.1 ABOVE 2026-09-15
(SUPERSEDED as a separate task: `classify_residue()` + taxonomy-closure test landed with P5.1.)
Original bullets, retired:
- [x] SUPERSEDED: every unresolvable id classified — DONE (45/21/19/0/0 with `unbased-channel` gained for P3.3)
- [x] SUPERSEDED: machine-readable, drives the enum — DONE (build() reads it; permitted requires resolvable)
- [x] SUPERSEDED: count as reading — DONE (85 live; no literal in any test)
**Depends on:** P5.1. **Scope:** M.

### P5.3: Re-measure the affix-pick concentration — FOLDED INTO P5.1 ABOVE 2026-09-15
(SUPERSEDED as a separate task.)
Original bullets, retired:
- [x] SUPERSEDED: Herfindahl re-measured — DONE (uniform 0.042/0.067 over 24/15 vs 0.027 over 101)
- [x] SUPERSEDED: GAP filed or closed — FILED: pick-spread within the offerable set needs a generation run; quota/brief follow-up, no program session
**Depends on:** P5.1. **Scope:** S.

---

## Phase 6 — mechanism carriage (R5)

### P6.1: Carry mechanism-class atoms through the binder — re-scoped 2026-09-15 (no structural ops)
**Spec:** `docs/architecture/passive-tree-repair/spec-status-anchor.md` (pricing) +
`spec-tree-resolve.md` (carriage); `spec-mechanism-carriage.md` is superseded. **Description:**
mechanism-*class* nodes (verbs, `status.apply` — the tiers 8–10 content) are a different thing
from structural *ops*. Once the status anchor prices them, carry them with their real `kindId`
through the existing resolve path; no new spec, no ladder-valued anything.
**Acceptance:**
- [x] MC-1 DONE 2026-09-15: `NodeStatusAtom` sibling shape (status/durationMs/level/chance/trigger — no channel/op/kMicro fabrication); `BoundNode` + `NodeRecord` carry it (trailing-optional: pre-MC-1 constructions bind unchanged, RpgStore untouched, no schema change); TreeBinderRun carries status.apply rows (WhenJson passthrough fixed — the 164-empty drop #1); writer emits statusAtoms omit-when-empty (key order identical, verified); loader reads with structural validation; 4 new binder tests + loader round trip; 45/45 binder green; full core green except pre-existing dungeon CRLF; Data suite green except proven-pre-existing species-import failure; live regen: 157 status atoms bound across 42 trees (were 0 carried). Resolve/apply half is mechanism-wiring's executor (documented handoff, not built here).
- [ ] MC-2 (live proof): BLOCKED on mechanism-wiring executor — no path applies tree-carried status atoms during a match yet (derived fan-in is magnitudes-only by spec §2.3). Filed as cross-program gap with this evidence; unblocks the day their executor reads NodeRecord.StatusAtoms.
- [x] The bound-but-inert count is **0** for anchor-priced classes at BIND layer (157 carried, zero status drops — TreeBinder --check exits 0, a drop would be a BindRefusal crash); Replace/Flag exclusions are counted separately as vocabulary, never as inert
- [x] `PassiveTree/MechanismRamp` checked at P8 regen: one GAP remains (wither defensive t9: 2 vs ramp 3) — pre-existing content gap (P1.2's ungenerated `wither-def-t9-n1`, seed plans untouched by this program), not a bind regression
**Depends on:** SA-1/SA-2 (anchor prices the classes) + V3-1 (GameUnits pins). **Scope:** M (MC-1) + M (MC-2).

---

## Phase 7 — resolve proof, both modes, one engine (acceptance)

### P7.1: End-to-end proof — one node changes a number in lawn and battle
**Spec:** `spec-tree-resolve.md` §12 test 15, §14 success criteria 1–4a. **Description:** the central
acceptance: one owned, gate-open, enabled node — magnitude **and** mechanism — moves a real channel
through the shipped fan-in on both read modes with identical totals, no new subsystem, no new order
band, and through the one shared engine.
**Acceptance:**
- [ ] BLOCKED (magnitude node): no bound magnitude atom resolves live — stat.modify awaits P11 (gated), stat.derived awaits module 2 (no session). Proves the day either lands.
- [ ] BLOCKED (mechanism node): no executor applies tree-carried status atoms — mechanism-wiring's program. Proves the day it lands.
- [ ] `F ∈ [1, Fmax]` both bounds; `Fmax = 1000‰` removes `F` byte-identically (runs with the proofs above)
- [ ] Withdrawal (un-owning) returns the channel to zero (runs with the proofs above)
- [ ] Every contribution carries `tree.{treeId}.{nodeId}` (GG-49 — already the shipped fan-in shape, proven synthetic 32/32)
- [ ] No second combat path: verified against `guard-actor-hub` and the ActorHub rule (guard green 2026-09-15)
**Depends on:** P6.1. **Scope:** L.

---

## Phase 8 — regenerate the corpus and re-audit

### P8.1: Regenerate all 42 trees through the real CLI
**Spec:** repair skill §6. **Description:** after Phases 1–7 and 12, regenerate
`gk-data/packs/fusion/data/generated/passive-tree`, re-run the language stage (P5.1 changed its vocabulary, P1.3 its
vintage, P12.2 what a pool-shaped channel does), and record scope + why.
**Regeneration is proof, not repair.**
**Acceptance:**
- [x] P8.1 DONE 2026-09-15 as checkpoint regen (P7.1/P12.3 still pending — final regen repeats then): all 42 trees regenerated through the real CLI with LF-normalized writer; `TreeBinder --check` exits 0; `FamilyExpandGen --check` exits 0; every verdict Fail-with-named-reasons (pools/content, by design); seedsmith PassiveTree check runs real wired data (1 documented NOT_MEASURED: ExclusionResolvable, pre-existing atom-tag-registry block); guard suite 313/313 (no golden movement)
- [x] P8.2 DONE, before/after with labeled instruments — expander: 125 families read both days; rows 150 → 305 (+75 v3 +70 anchor +10 intervals); refused 95 → 64 (30 mislabeled verb/op refusals re-bucketed to curve/exclusion truth). bound corpus (census --json): 560/1680 nodes bound, 344 priced + 157 status carried = 501 atoms (report baseline 2026-09-13: 407 bound atoms, all stat.modify, readable 0%); readable still 0 (0/47 derived families emittable-concrete — pools block binds, module 2); mechanism bound 141/840 (16.8%); unspent 62230‰ = pools (21 fams) + unauthored picks + template/verb residue per P5.2
- [x] Census instrument extended (boundWithStatusAtoms/statusAtoms) so status-carrying nodes stop reading as unpriced; 38 census tests green
**Depends on:** P7.1, P12.3. **Scope:** L (machine time, resumable).

### P8.2: Re-run the distribution census and prove the gates — FOLDED INTO P8.1 ABOVE 2026-09-15
(SUPERSEDED as a separate task: the census, before/after table, and gate evidence all landed in
P8.1's ticks; the bullet-by-bullet original below is retired, not open.)
Original bullets, retired: mechanism-no-longer-worst (still worst at 16.8% — G10 partial, honest);
no-tree-at-0% (proven: worst spark 1); unspent explained (62230‰ per P5.2); before/after committed
(P8.1 tick + status HTML).

### P8.3: Live-boot proof against the regenerated corpus — PARTIAL 2026-09-15
**Acceptance:**
- [x] Live import proven: PassiveTreeImportRunnerTests 6/6 import the real regenerated catalog with zero refusals
- [ ] BLOCKED (readable value lawn+battle): no bound atom resolves live yet (P11 gated + module 2 missing + no status executor) — same wall as P7.1, proves the day it falls
**Depends on:** P8.2. **Scope:** M.

---

## Phase 9 — balance measurement (the actual goal)

### P9.1: `squad-harness` S4 — BLOCKED (vacuous, not skipped) 2026-09-15
**Reason:** S4 measures marginal win share per budget point across the duel roster — it needs
resolving contributions. At 0% live effectiveness it would measure F=0, a vacuous number that
proves nothing about balance. Runs the day P11/module-2/mechanism-executor lands, against this
session's corpus.

### P9.2: Close or file the two content GAP findings — FILED WITH MEASUREMENTS 2026-09-15
**Spec:** parent plan (2026-09-07 pass). **Description:** `ExclusionRate` (999‰ vs ≤30‰) and
`NearDuplicate` (69‰ vs ≤5‰). `ExclusionRate`'s root cause was fixed in the brief;
`NearDuplicate` has no live suppression. Either land it or file with an owner and a default.
**Acceptance:**
- [x] ExclusionRate FILED: re-measured 637‰ (was 999‰ — brief fix helped; still >> 30‰). Form split {none 608, nullification 24, reroute 1047}; 1053 nodes sit outside their cell's allocation — root cause is quota-cell mismatch (tree-language/quota territory, same follow-up as P5.3's pick-spread). Default: current 637‰ recorded; ≤30‰ target stands for the quota program.
- [x] NearDuplicate FILED: re-measured 69‰ unchanged (116/1679 nodes, e.g. 'Fleet-Footed'/'Fleet-Footed Aim' Jaccard 0.666). Needs an LLM rename pass over generated names — content work for a tree-language generation run, not this program. Default: current 69‰ recorded; ≤5‰ target stands.
- [x] Neither silently dropped (both named here with measurements, owners, defaults)
**Depends on:** P8.1. **Scope:** M.

---

## Phase 10 — NEW 2026-09-13: `effect-pipeline` L0 (affix distribution quality, not blocking)

Not required for playability — P5 gets the tree readable without it. Filed (not built) 2026-09-15:
L0 modules 11/12 are effect-pipeline program's build (session boundary + container rule); the
resolvable vocabulary is now measured (offerable 24 offensive / 15 defensive, residue 45/21/19
classified) and no pick-quality measurement shows the tree needs L0. **Safe to build in parallel
with Phases 2–9** once that program owns it; only `P10.3` feeds back into Phase 5's vocabulary
(wiring point identified: `generate_tree.py:118`).

### P10.1: `affix-power-class` (effect-pipeline module 11) — FILED, not built here
**Disposition 2026-09-15:** effect-pipeline program's build (LLM stage over item affixes for
six item channels). This session's program boundary (one session = one problem) plus the
container rule forbid building another program's modules from here. Filed as follow-up with
the tree-side evidence that scopes it: tree quotas already distribute picks; no measurement
shows the permitted-enum distribution is wrong (P5.3 measured breadth 24/15, not pick
quality). The 125-call classification should wait for (a) that program to own it and (b) a
pick-quality measurement proving the tree needs it.

### P10.2: `affix-channel-weights` (effect-pipeline module 12) — FILED, not built here
**Disposition 2026-09-15:** same program boundary — item-channel weight policy + `poolFor`
belong to effect-pipeline. Filed alongside P10.1.

### P10.3: Tree-language consumes the L0 candidate list (R-2.6) — PENDING L0
**Disposition 2026-09-15:** needs P10.1/P10.2 outputs that don't exist. The tree-side wiring
point is identified (`generate_tree.py:118` feeds `permitted_for_branch` into the picker —
an L0 candidate list would compose there). Unblocks when effect-pipeline ships L0.

---

## Phase 11 — ActorHub primary producer (`stat.modify` route) — gate premise STALE, likely clear now

**Gate premise re-verified 2026-09-20** (`backlog-clean-up` `paperwork-reconcile` P7): ~~branch
`worktree-solid-run-20260912-eb53` live, record active — still unmerged~~ — **false as of this check.**
`git merge-base --is-ancestor bbdd8f94 HEAD` returns 0 — that branch's tip **is** merged (via
`b600fdee0` into `features/derived-stat-extension` on 2026-09-14, itself now in `features/mega-merge`).
The `ActorHub`/`BattleStatComposer` fusion this gate was waiting on has itself since landed
(`69ba6a7b3`, 2026-09-13 — `BattleStatComposer.cs` no longer exists in `src/`). The gate premise was
written into the 2026-09-16 close-out, 2 days after the actual merge — a documentation lag, not a
real block today. **P11.0/P11.1/P11.2 are re-verified as unblockable; the build itself (re-checking
ActorHub/SOLID with `solid-enforcement` first, since this touches the same "one ActorHub compose"
surface that program also owns) is scheduled at `backlog-clean-up-todo.md` `infra-remainders` BCU8.8,
not attempted here.

**Gate, not a checkpoint — genuinely irreversible.** `solid-run-20260912-eb53`
(`actor-hub-and-combat-power-solid-fixing`) is fusing `ActorHub`/`BattleStatComposer` and relocating
subsystem registration on `gk-core/src/FusionRpg.Core/**` right now. Registering a new `IActorStatSubsystem`
against that surface mid-fusion is a collision with no clean repair after the fact — this passes both
"Gates vs. checkpoints" tests (irreversible; no reversible default exists for *how* to register against
a surface that is being restructured). **Named resolver:** owner, merging that worktree. **Stated
default if this plan reaches Phase 11 unresolved:** skip it — Phases 0–10 already deliver full
playability via the derived route — and carry Phase 11 as a tracked, non-blocking follow-up.

### P11.0: Write the `decisions.md` row — GATED (see Phase 11 gate above)
**Depends on:** `solid-run-20260912-eb53` merged. **Description:** write the row against the *merged*
subsystem contract, not the pre-merge one — writing it earlier risks locking against an interface the
fusion is about to change. Names: the new subsystem, its `ContributionSourceIds` grammar
(`tree.{treeId}.{nodeId}`), and that it is additive to the derived route, not a replacement.
**Scope:** S.

### P11.1: Register a new `IActorStatSubsystem` — GATED (see Phase 11 gate above)
**Spec:** `actor-hub-ssot.md` §8.1 (SourceId grammar); `decisions.md` "ActorHub sole Hot compose gate".
**Description:** a new subsystem reads bound `stat.modify` atoms (already stored by P4.3's binder,
never dropped) and contributes them into `ActorHub.Resolve`/`ResolveDerived`, GG-49 SourceId
`tree.{treeId}.{nodeId}`. **No BattleStatComposer bolt-on, no private fold** — once solid-run's fusion
lands, both lawn and battle read Hub output through the same path this subsystem feeds.
**Acceptance:**
- [ ] A real `IActorStatSubsystem` is registered, contributing `stat.modify`-kind tree atoms
- [ ] `guard-actor-hub.ps1` passes — no second composer, no `BattleStatComposer`-only path
- [ ] A `TreeFanInTests`-shape test proves the contribution reaches Hub output in **both** lawn and
      battle reads, byte-identical
**Depends on:** P11.0, P4.3. **Scope:** M–L. **Files:** new `gk-core/src/FusionRpg.Core/Stats/Derived/Subsystems/*.cs`, `ActorHub.cs` registration, tests.

### P11.2: Live-boot proof — a real allocated primary-kind node changes a number — GATED (same gate)
**Acceptance:**
- [ ] BLOCKED on P11.1 (gate above): proves the day the subsystem lands
- [ ] Same node's contribution visible in battle read through Hub
**Depends on:** P11.1. **Scope:** M.

---

## Phase 12 — NEW 2026-09-13 (plan-coverage audit): the real join, not the patch

**Why this exists.** P4.3 (Phase 4) is a minimal hand-patch to the tree's own bespoke
`Binding/AffixComposer.cs` — real work, and the fastest path to a readable tree, but it keeps a
second, parallel resolver alive beside the shared `Effects/Atoms/Resolver` (module 2). Per this
repo's SOLID-is-binding hard rule, extending a bespoke seam is allowed only if the remediation is
**named and sequenced**, not left implicit — this phase is that naming. It also closes R-1.1 and
R-3.1–3.3 from the repair report, both dropped when Phase 10/11 were added and caught by this audit.
**Bonus:** it supersedes P4.1's "refuse by name" disposition for pool-shaped channels —
`spec-channel-pool.md` §4 already says the roll is module 2's job, so once the tree delegates to it,
pool nodes stop being a permanent refusal.

**Disposition 2026-09-15: BLOCKED on effect-pipeline program (verified in-session, not assumed).**
`Resolver.cs` exists with pool support, but the channel-draw entry (`DrawPoolChannels`) is private
and `Resolve()` is a roll-based container API — no public bake-time channel-draw entry exists for
the tree to delegate to. Building one means editing effect-pipeline's file/contract (another
program), and building a parallel pool resolver here would violate SOLID + pool-spec §4 (which
forbids any module but module 2 implementing resolution). Unblocks the day that program exposes
the entry (+ P12.1 map disposition in their map doc). No parallel implementation built here —
that restraint IS the deliverable for this phase.

### P12.1: Disposition the tree as `effect-pipeline`'s fifth path — BLOCKED (with P12.2)
**Acceptance:**
- [ ] BLOCKED: disposition without implementation misleads — lands with P12.2 in effect-pipeline's map doc
- [ ] The "never twice" invariant restated explicitly (same edit)
**Depends on:** P12.2 (inverted: the doc follows the code, not precedes it). **Scope:** S.

### P12.2: Delegate tree-atom resolution to the shared `Resolver` (R-1.1)
**Spec:** `Effects/Atoms/Resolver.cs` (module 2, five-step order, per-layer RNG streams);
`spec-tree-binder.md` §4.1. **Description:** `Binding/AffixComposer.Resolve` is a catalog-local copy
of what `Resolver` already does. Replace or delegate it so there is **one** resolution implementation
— per D24, this stays a **bake-time, single-resolve** call (never a per-player roll): the tree is
static content, and `Resolver`'s determinism is what makes baking its output legal at all.
**Acceptance:**
- [ ] BLOCKED: no public bake-time channel-draw entry exists (`DrawPoolChannels` private, `Resolve()` roll-based) — unblocks when effect-pipeline exposes one; then: `AffixComposer.Resolve` delegates, no parallel logic remains
- [ ] BLOCKED: channelFamily-mismatch refusal test rides the same delegation
- [ ] BLOCKED: pool channels resolve through the shared entry at bake, or still refuse naming *why the shared entry* refused
- [ ] All 42 trees still `--check` clean (holds today; re-verify at unblock)
**Depends on:** effect-pipeline program (public entry + P12.1 map row). **Scope:** L.

### P12.3: Bind the tree as a `skill`-container producer via `InstanceProducer` (R-3.2/3.3) — BLOCKED (with P12.2)
**Acceptance:**
- [ ] BLOCKED: container ids, InstanceRow+BindingRow through the shared five-step order — all ride P12.2's entry
- [ ] `--check --family PassiveTree` reads real wired data (holds today independently)
**Depends on:** P12.2. **Scope:** L.

**Note for Phase 8:** once Phase 12 lands, P8.1's regeneration picks up any pool-shaped nodes that were
previously refused. Re-run P8.2's census after Phase 12, not only after Phase 6.

---

## Ask-first items (owner decisions)

| # | Decision | Owner direction so far | Blocking task |
|---|---|---|---|
| A1 | Publish `power-scale.v3.json` pins (GameUnits + regen/s + rate channels) | ✅ **ANSWERED 2026-09-13, RESHAPED 2026-09-15: authored BY this program** (no power-program session exists) — pins, not curves; rates included | P3.1 (V3-1) |
| A2 | `Replace`/`Flag` semantics: bind mechanism-less, or exclude? | ✅ **FLIPPED 2026-09-15 to (b), exclude** — Replace substitutes a constant where the ladder requires `f(Θ)` (parity §2, PS-3, §5.1); composer reads only Flat on FlatSum channels | P2.3 (EX-1/EX-2), P5.1 |
| A3 | Add `More` to `NodeAtomOp`? | ✅ DONE — added, `38286a0d` | P4.2 (closed) |
| A4 | Mechanism-carriage shape (`kMicro = 0` + real `kindId`, or new field)? | ✅ **RESCOPED 2026-09-15: neither** — no structural carriage exists to shape; mechanism-class atoms travel the existing resolve path once anchor-priced | P6.1 (MC-1/2) |
| A5 | Confirm the `statusMagnitudeAndDuration` reading for all non-magnitude kinds | ✅ **ANSWERED 2026-09-13, AUTHORED 2026-09-15 by this program** (registry stays frozen) | P3.1b (SA-1/2) |
| A6 | `tier-bands`/`power-scale` version publication is the power program's call | ✅ **SUPERSEDED 2026-09-15: no power-program session exists** — this program authors v3/v6-class files as versioned data | P3.1, P3.2 |
| A7 | Kind fork mechanism (not just direction) | ✅ **ANSWERED 2026-09-13: both kinds; primary route via ActorHub `IActorStatSubsystem`, never a battle-side bolt-on** | P4.3, P11.1 |
| A8 | Include effect-pipeline L0 (modules 11/12) in this program's scope? | ✅ **ANSWERED 2026-09-13: yes — REVISED 2026-09-15: filed, not built** — modules 11/12 are effect-pipeline program's build (session boundary + container rule); tree quotas already distribute; no pick-quality measurement proves the tree needs it | P10.1–P10.3 (follow-ups) |
| A9 | `decisions.md` row for the ActorHub primary producer | ⛔ **OPEN — write after `solid-run-20260912-eb53` merges**, not before | P11.0 |

## Gate summary (plan §4)

| Gate | Phase | One-line pass |
|---|---|---|
| G0 | P0 | baseline distribution reproducible from one command |
| G1 | P1 | `FamilyExpandGen --check` 0; zero true orphans; uniform current vintage |
| G2 | P2 | status ladders real (t1s + shares published); Replace/Flag excluded by principle with ladder citation, counted as vocabulary never inert |
| G3 | P3 | every priced channel has a published pin (v3); intervals classified; uncovered channels refuse by name |
| G4 | P4 | binder runs to completion, never crashes |
| G5 | P4 | emitted kind is read by the resolve path for that kind — ⚠️ PARTIAL: consumption proven synthetic 32/32; 0 derived binds live (pools, module 2) |
| G6 | P5 | enum ⊆ resolvable (24/15); residue 45/21/19/0/0 closed; expander `does not exist` = 0 |
| G7 | P6 | mechanism-class binds anchor-priced (157 carried); resolve half with mechanism-wiring (no executor) |
| G8 | P7 | BLOCKED: no bound atom resolves live (P11 gated + module 2 missing + no status executor) |
| G9 | P8 | corpus byte-reproducible; `check --family PassiveTree` real; import 6/6 |
| G10 | P8 | ⚠️ PARTIAL: no tree binds 0% ✓ (worst: spark 1 node); mechanism still worst class (141/840 = 16.8% vs magnitude 49.8%) — improves only with pools/executors |
| G11 | P9 | BLOCKED: S4 needs resolving contributions (vacuous at 0% effectiveness — would measure F=0, not balance) |
| G12 | P10 | FILED: L0 is effect-pipeline's build; tree wiring point identified (generate_tree.py:118) |
| G13 | P11 | ⚠️ **GATE PREMISE RE-VERIFIED FALSE 2026-09-20** (`backlog-clean-up` P7, then BCU8.8): the branch is merged and `BattleStatComposer` is gone, so nothing is irreversible any more. **The build itself was attempted by BCU8.8 and handed back** — P11.1's premise is stale (see "BCU8.8" at the end of this file) and P11.0 needs `decisions.md`, which was fenced by an active session at the time |
| G14 | P12 | BLOCKED: shared channel-draw has no public bake-time entry (DrawPoolChannels private); building one = effect-pipeline's file. No parallel resolver built here (SOLID + pool-spec §4) |

---

## BCU8.8 (2026-09-20) — the build was attempted; here is exactly where it lands

**✅ RULING 2026-09-20 (orchestrator): the erratum is GRANTED and is the accepted deliverable** — BCU8.8
closes as *closed-as-erratum*, P11.1's replacement row is filed below as **P11.1r**, the H5 finding is
routed to `item-seedgen` (`tasks/item-seedgen-todo.md`), and P11.0 is routed to the `decisions.md`
owner. Nothing here is blocked on this lane any more.

`backlog-clean-up` `infra-remainders` BCU8.8 owned three things. Each was checked against code this
session; none closed as originally written, and the reasons differ, so they are separated rather than
blurred into one "blocked".

**1. P11.1's premise is stale — the repo already rejected the shape it asks for.** → **corrected row:**
`### P11.1r` below.
P11.1 asks for "a **new** `IActorStatSubsystem`" reading bound `stat.modify` atoms
(`tasks/passive-tree-repair-todo.md:614`). The shipped design does the opposite, deliberately:
`gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs:8-13` states *"No new subsystem, no new order
band, no eviction of the existing three: this is a PRODUCER composed into the existing fan-in, never a
fourth registration."* — `BoundDerivedAtom`s from tree nodes feed the existing `AtomDerivedSubsystem`
(order 350). Registering a fourth subsystem now would be the defect, not the fix. **The real remaining
gap is narrower and differently shaped:** `TreeAtomSource.cs:68` is
`if (atom.KindId != "stat.derived") continue;`, so a node's `stat.modify`-kind atom (Flat / Increased /
More on a primary channel — the kind `NodeAtom` documents as *primary*) is fanned into **nothing**.
Widening that producer is a design decision about how a `NodeAtom`'s `KMicro`/`ScaleAxis` maps into the
derived-channel `BoundDerivedAtom` shape, and it belongs to whichever session owns
`spec-mechanism-wiring.md` §2.3 — not to a paperwork lane re-reading it under time pressure.
**Erratum requested:** P11.1 should be rewritten as "widen `TreeAtomSource` to fan in `stat.modify`
tree atoms", or explicitly re-scoped to mechanism-wiring, before anyone builds it.

**2. P11.0 cannot be written from this lane.** The row is "Write the `decisions.md` row"
(`:607-609`). `docs/architecture/decisions.md` is claimed by the active direct-mode session
`keepverse-split` (`tasks/sessions/keepverse-split.json`), so it is fenced. The row's content is
otherwise ready — the gate premise it waited on was re-verified false on 2026-09-20 (branch merged,
`BattleStatComposer` deleted in `69ba6a7b3`).

**3. H5 `tree_seed_roots` wiring is outside this lane's paths.** The fix is a production call site for
`PassiveTreePlanCtx.tree_seed_roots` plus a real `HiddenFileCountMetric` invocation, in
`gk-forge/tools/seedsmith/seedsmith/metrics/passive_tree.py:156` and `.../report/cli.py` — the seedsmith tree
(`tools/**`), which this session may not edit. The acceptance's second half is separately stale and
needs its owner: "non-zero `visitedFileCount`" cannot hold against today's corpus because zero
`_`-prefixed files exist for the walk to find (`tasks/passive-tree-todo.md:3369-3383`, the row's own
Evidence). Tracked at `backlog-clean-up-todo.md` BCU8.8 with this analysis.

**4. The status-atom executor is unbuilt and unchanged by this pass.** `NodeStatusAtom` is bound at bake
(157 across 42 trees, `passive-tree-repair-todo.md:481`) but nothing applies it during a match — MC-2
and P6.1 are filed against mechanism-wiring (`:482`, `:498`). No new row is needed; the existing ones
name it, and they are the correct owners.

---

### P11.1r: widen `TreeAtomSource` to fan in a node's `stat.modify` atoms (replaces P11.1)

**Filed 2026-09-20 by `backlog-clean-up` BCU8.8, on the orchestrator's granted erratum.** P11.1 asked
for a **new** `IActorStatSubsystem`; `TreeAtomSource.cs:8-13` deliberately registers none, so that row
is unbuildable as written. This is the same goal — a tree's primary-kind atoms reach Hub output — in
the shape the shipped design already uses.

**Description.** `TreeAtomSource.BoundAtomsFor`
(`gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs:68`) skips every atom whose
`KindId != "stat.derived"`, so a node's `stat.modify` atom — the kind `NodeAtom` documents as *primary*
(`Catalog/NodeAtom.cs:10`) — is fanned into nothing, on lawn and battle alike. Decide how that atom's
`KMicro` + `ScaleAxis` maps onto the `BoundDerivedAtom` shape the existing `AtomDerivedSubsystem` reads
(`TryParseOp` already parses `Flat`/`Increased`/`More`), then lift the kind filter so both kinds fan in
through the one producer. **No fourth subsystem, no new order band, no private fold** — the constraint
P11.1 stated, satisfied the way `TreeAtomSource`'s own doc comment requires.

**Acceptance:**
- [ ] A node carrying a `stat.modify` atom contributes to Hub output; `scripts/guard-actor-hub.ps1` still passes
- [ ] A `TreeFanInTests`-shape test proves the contribution in **both** the lawn and battle reads
- [ ] `TreeResolveReport` (§2.1 rule 3) and `BoundAtomsFor` still agree on what is live — no report/read drift

**Owner:** `passive-tree`, with a design pass by `mechanism-wiring` (`spec-mechanism-wiring.md` §2.3 is
where the mechanism/primary split is specified). **Scope:** M. **Depends on:** P4.3 (stored, never
dropped — already true).

**Manager update 2026-09-25 — BLOCKED after bounded implementation audit (`resume-12-passive-tree-p11-1r-20260925`):** lifting only `TreeAtomSource.TryReadOp` is not a valid implementation. `stat.modify` targets the primary `StatChannels` vocabulary and is consumed by lawn `StatSystem`/`StatComposer` and the battle primary ledger; `BoundDerivedAtom`/`AtomDerivedSubsystem` validates only derived channels and has no lossless `More` mapping. The accepted report/read parity repair remains unchanged. The next step is an owner-approved primary carrier/delegate or an explicit lossless primary-to-derived contract, followed by a production implementation lane; do not widen the predicate or invent a derived alias.

- [ ] **PT-F39 — `PassiveTreeEndpointsTests.Post_anOwnedTierOneNodeAfterOpeningTierOne_contributes` fails at HEAD (Server suite)** · S · deps: — · *(found by the resumed manager, 2026-09-25, while accepting CAI2.2)* — `gk-core/tests/FusionRpg.Server.Tests/PassiveTreeEndpointsTests.cs:271` reports `Assert.Contains() Failure: Item not found in collection`. Reproduces at the parent commit with an unrelated diff stashed, so it is pre-existing; the whole Server suite reads 881 passed / 1 failed at that head.
  - **Remedy:** decide whether the assertion is stale or the endpoint stopped contributing (the test name asserts a tier-one node contributes once tier one is open), fix the responsible half, and prove the whole Server suite green.
  - **Verify:** `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~Post_anOwnedTierOneNodeAfterOpeningTierOne_contributes"`, then the whole `tests\FusionRpg.Server.Tests`.
  - **Owner:** passive-tree-repair (the contributing half lives in Core/PassiveTree Resolve).

- [ ] **PT-F40 — the tree-plan `propertyVocabulary` was stale generated data AND a stale literal over a
  population. Both defects fixed; this row is the record.**
  - **Remedy:** none outstanding. `seedsmith trees plan --emit` for all 42 per-tree plans plus the
    manifest (`propertyVocabulary.atomAttachPoint` 7 → 9, `atomKind` 16 → 18), and the two literal
    `assertEqual` pins in `gk-forge/tools/seedsmith/tests/test_tree_plan_emit.py` replaced by the mirror
    relationship `len(vocabulary.json["attachPoints"])` / `["kinds"]`.
  - **Why it was not a one-line pin bump.** Three sources disagreed: `vocabulary.json` (the authored
    SSOT) said 9/18, the live mirror agreed, the committed plans said 7/16 and the test pinned 7/16. The
    additions are `Element` and `Siege` attach points with `element.convert` and `structure.place` using
    them — a deliberate corpus change. `atomTrigger` (13) and `channelFamily` (54) already agreed, which
    dates the staleness: the plans were regenerated after the channelFamily change and before these two.
    Per `AGENTS.md` a guardrail validates the contract and closed enums, never a population count, and
    this axis is a growing corpus — so the pin was the forbidden class and the plan was stale data.
  - **Verify:** `PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith trees plan --check` reports
    **byte-identical to a fresh regeneration** (exit 0); `pytest gk-forge/tools/seedsmith/tests/test_tree_plan_emit.py`
    **21 passed**; the plan/vocabulary area **145 passed**; `guard:generated-seed` **clean over all 45
    changed files**. Emission safety was measured, not assumed: every `nodeKey`, `nodeId` and node count
    was snapshotted before and after — **0 moved** — so the node and identity files keyed by these plans
    stay valid. The first emit wrote only `might.v1.json` (the CLI defaults to one tree); leaving 41
    plans and the manifest at 7/16 would have made `plan_read.py` refuse a plan with no
    `propertyVocabulary` and `exclusion.py` refuse a legitimate `Element`/`Siege` property key.
  - **Owner:** `passive-tree-repair` (generated-artifact regeneration is this program's subject, and its
    plan already runs generator `--check`). Filed by the worktree/branch cleanup program,
    `mega-merge-program-manager-20260925-f78e`, 2026-09-27. Not filed to
    `tasks/passive-tree-todo.md`: a 538-path sweep holds whole trees, and the owning ledger is a
    different file.

- [ ] **PT-F41 — the node corpus-wide uniqueness gate is exact-string where the items rule is
  token-set normalised, and 2 committed near-collisions are invisible to it. Owner decision.**
  - **Remedy:** decide, then implement. (a) Apply `naming.v1.json` §4 steps **1, 2, 4, 5** to the node
    gate — lowercase, tokenize on whitespace/punctuation, drop the four closed connectives
    (`of`/`the`/`a`/`and`), sort. Small, catches both observed groups, and needs **no** word pool.
    (b) Give the node corpus a `_registry/` shape so the shared authority runs. (c) Keep exact-match and
    record the 2 as accepted. **(a) is the cheap correct step; (b) is the principled end state.**
  - **What is wrong.** `name_collision` compares `name in set(takenNames)` — exact string membership —
    while the items pipeline's rule is `naming.v1.json`'s normalization, whose authority is
    `gk-forge/tools/ItemSeedValidator/Naming/NameNormalizer.cs`. Measured over 2,019 named node rows in 51 tree
    files, two within-tree groups of **different strings** collapse to one name:
    `ArmoredImpZombie.json` `Carrion Frenzy` (n0) vs `Frenzy of the Carrion` (n1), and `dark.json`
    `Ossuary Pulse` (n1) vs `Pulse of the Ossuary` (n2) — both the of-construct word-order variant that
    step 4's connective drop and step 5's sort exist to collapse. **This is a rule defect, not a data
    one: no regeneration fixes it, because a string comparison will never match those two pairs.**
  - **Why the authority could not simply be reused.** `NameRepair`'s docstring names the authority and
    warns that reimplementing it forks the rule. Run against the node corpus it refuses by name —
    `dotnet run --project gk-forge/tools/ItemSeedValidator -- gk-data/packs/fusion/data/seed/passive-tree --collision-groups` →
    `no _registry/ under .../data/seed/passive-tree`, exit 2 — so the node corpus has no items-shaped
    root and `NameRepair` is not a drop-in.
  - **Separately measured, and NOT this row:** 157 exact-duplicate name groups corpus-wide (75 of them
    also within one tree) are committed, which a corpus-wide gate should have refused. That is a **data**
    question — legacy rows predating the gate, which is the situation `NameRepair` exists for on the
    items side — and legacy cannot be told from gate-not-applied-on-the-writing-path from the corpus
    alone. The discriminator is a regeneration run, which this row does not claim.
  - **Verify:** the 2 is a **lower bound** — steps 1/2/4/5 are a declared subset of the authority, and step
    3 (reserved-word-pool canonical id) is unmeasured, so more may exist. Re-measure by applying the
    subset to `gk-data/packs/fusion/data/seed/passive-tree/nodes/**` after (a) or (b) lands and asserting the group count
    reaches 0.
  - **Owner:** `passive-tree-repair` — the gate is in the `tree-language` stage, whose own comment cites
    `spec-tree-language.md` §5.1, the section this program's "read first" list names. Filed by the
    worktree/branch cleanup program, 2026-09-27, replacing CB8's original parked phrasing.
