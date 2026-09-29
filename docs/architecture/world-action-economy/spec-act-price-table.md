# Spec: `act-price-table`

**Status: written against shipped code 2026-09-15** — every `file:line` below was opened this
session in the worktree. Module id `act-price-table`, row 1 of the
[world-action-economy map](../world-action-economy-map.md) (wave 1, no dependency).
Ideal: [world-action-economy-ideal.md](../world-action-economy-ideal.md)
§Tunables, §Module breakdown row 1, §Locked constraints preamble (the debit site itself belongs to
`budget-debit`, not here). Decisions: Owner resolutions 2026-09-15 (Q1 extend budget, Q2 small
allowance, Q3 claim+deposit, Q4 command kind, Q5/Q6 flat march-free).

## Objective

The world turn budget (`WorldEntity.MovementRemaining`) can price acts, but today it prices exactly
one thing — marching — plus the dowse-stance budget. This module adds the price list: per-verb
`*CostMilli` rows plus one hold-allowance number, all in the `movement` section of
`data/tuning/world.v{n}.json`, all loaded through the existing `WorldTuningHub` /
`MovementTuning` path. Nothing reads the new keys yet — that is `budget-debit`'s and
`hold-allowance`'s job. This module ships the table, the loader, and the key-name locks downstream
may rely on.

Success looks like: `world.v{n+1}.json` carries `movement.claimCostMilli` (and siblings) beside
`dowseBudgetMilli: 250`; `WorldTuningLoader.Parse` rejects a document missing any of them by name;
no golden moves, because no resolver reads them yet.

## Locked anchors

- **Dowse is the precedent, not a suggestion** (`world-action-economy-ideal.md` Step 0.5;
  `LaneCost.cs:51-56` comment: *"Never a const here … exactly the kind of number a balance pass
  wants to move"*). Every key below is per-mille, `*Milli`-suffixed (tunables-ssot T6), lives in
  the `movement` section beside `dowseBudgetMilli`, and is read through `WorldTuningHub` — never a
  `const`, never a second file, never a parallel loader.
- **Values are provisional content, not locked numbers.** Every value in §Tunables ships as a
  starting default the balance pass moves first — the program's own standing precedent
  (dowse 250: *"a starting value, not a measured one"*; upkeep 50 in the same ship-with-default-
  then-tune shape). A later tune changes the JSON and re-blesses goldens; it never touches code.
  Downstream modules may rely on key names, units, and these defaults — never on the numbers being
  final.
- **Flat per-act-per-legion** (Owner resolution Q5). No member-count scaling, no level curve (one
  power ladder — flat per-mille spends need no ladder read at all), no faction/stance discount.
  If playtesting ever evidences scaling, that is a new spec, not a quiet widening of this table.
- **T7 separation: this change retunes nothing.** `PointsPerTurn` 1000, scout 500, hold 0, dowse
  250 are the fixed frame costs are measured against (`ideal.md` §Tunables). This module adds rows;
  it does not move any existing number, so no golden may move with it.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `movement` section exists with exactly one priced act: `dowseBudgetMilli: 250` | `gk-core/data/tuning/world.v5.json:83-85` |
| `MovementTuning` record carries it: `MovementTuning(int DowseBudgetMilli)` | `gk-core/src/FusionRpg.Core/World/WorldTuning.cs:19` |
| Loader parses it as a required int; missing key throws naming the path | `WorldTuning.cs:125-127` (`Int(mv, "dowseBudgetMilli", "movement")`; `RequireInt` rejects non-integers `:192-197`) |
| `WorldTuningHub` is the single configuration point; missing `Configure` throws, never a built-in default | `WorldTuning.cs:224-234` (tunables-ssot T5) |
| `BudgetFor` reads the tunable for dowse, consts for everything else | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:32,35,47-57` |
| Per-mille arithmetic discipline exists: `long` widen, divide-by-1000-last, clamp | `LaneCost.cs:131-144` (`cost = cost * type.CostMultiplierMilli / 1000`) |
| Publish path: never hand-edit; `publish.py` writes `world.v{n+1}.json`, old version stays | `world.v5.json:7` (`_meta.rebalance`); v2–v5 notes model provisional-then-tune |
| Schema-only additions that nothing reads move no golden (the v3 precedent: growth shipped at identity 0/1000‰) | `world.v5.json:9` (v3Note) |

### Real gap

| Gap | What this module builds |
|---|---|
| No `*CostMilli` key besides lane/ley/dowse exists anywhere in tuning or code | §Design 1: five priced rows + one allowance number |
| `MovementTuning` has exactly one field; the loader knows exactly one movement key | §Design 2: extend record + parse arms, same shape |
| Hold-stance budgets 0, so a priced garrison act has no number to read | §Design 1: `holdAllowanceMilli`, the "small allowance" number (Owner resolution Q2) |
| `clear`/`sustain` candidacy is undecided (Owner resolution Q3 priced claim+deposit only) | §Design 3: reserved key names, no rows — a later spec prices or drops them |

## Design

### 1. The rows — `movement` section, `world.v{n+1}.json`

Priced now (Owner resolution Q3 + the load/unload verbs this economy must eventually cover):

| Key | Provisional value | Why this default (content call, not a lock) |
|---|---|---|
| `claimCostMilli` | 250 | The marquee act; one dowse-sized quarter-turn — a band that claims cannot also have scouted far. Matches the HOMM3 DD shape (a real act costs a real fraction of the day). |
| `depositCostMilli` | 100 | A tenth of a turn: handing goods over is quicker than prying a cache open. |
| `withdrawCostMilli` | 100 | Symmetric with deposit — same counter, opposite direction. |
| `loadCostMilli` | 50 | Packing the legion's own packs is the cheapest act; intentionally below deposit so stash-vs-pack routing has a legible price order (50 < 100 < 250). |
| `unloadCostMilli` | 50 | Symmetric with load. |
| `holdAllowanceMilli` | 250 | The Q2 "small allowance": a holding garrison may spend one dowse-sized act per turn. Large enough to do exactly one real thing, small enough that holding still means holding. |

All values are **provisional spec-time content calls** (Locked anchors): the balance pass moves
them first, exactly as dowse-250 was *"a starting value, not a measured one."* The load-bearing
part of this table is the key names, the units, and the price order (load/unload < deposit/
withdraw < claim) — not the integers.

### 2. Loader wiring — extend `MovementTuning`, no new path

```csharp
public sealed record MovementTuning(
    int DowseBudgetMilli,
    int ClaimCostMilli,
    int DepositCostMilli,
    int WithdrawCostMilli,
    int LoadCostMilli,
    int UnloadCostMilli,
    int HoldAllowanceMilli);
```

Parse arms follow the existing one-line shape (`WorldTuning.cs:126-127`):

```csharp
var movement = new MovementTuning(
    DowseBudgetMilli: Int(mv, "dowseBudgetMilli", "movement"),
    ClaimCostMilli: Int(mv, "claimCostMilli", "movement"),
    DepositCostMilli: Int(mv, "depositCostMilli", "movement"),
    WithdrawCostMilli: Int(mv, "withdrawCostMilli", "movement"),
    LoadCostMilli: Int(mv, "loadCostMilli", "movement"),
    UnloadCostMilli: Int(mv, "unloadCostMilli", "movement"),
    HoldAllowanceMilli: Int(mv, "holdAllowanceMilli", "movement"));
```

No change to `WorldTuningHub` (single `Configure`, throw-if-missing — `WorldTuning.cs:224-234`
already does the right thing). No new file, no new loader class, no host-side change beyond
shipping the new JSON (tunables-ssot §7.2: hosts load and inject; Core parses). A document missing
any key fails loudly at boot naming it (T5) — the same rejection the dowse key already gets.

Publish via the standing tool (`python gk-core/tools/tuning/publish.py world <dotted.key>=<value> [...]`
→ `world.v{n+1}.json`), with a `_meta.v{n+1}Note` in the v2/v3 style naming this spec, the
provisional stance, and the program precedent. The old version stays on disk for revert (T4).

### 3. Named candidates — reserved, not priced

`clearCostMilli` and `sustainCostMilli` are **reserved key names** for the verbs Owner resolution
Q3 left out. No rows ship, nothing reads them, and the loader must NOT accept-or-require them
until a later spec prices them (a half-present key is worse than an absent one: T5 would turn an
undecided verb into a boot failure). `dowseBudgetMilli` already exists and is untouched.
`build` stacks nothing (Owner resolution Q3) — no `buildCostMilli` is reserved.

### 4. Numeric types

Keys are `int` per-mille, matching `DowseBudgetMilli` (`WorldTuning.cs:19`) and every other
`*Milli` in the file — a per-act cost on a 1000-point turn budget cannot approach `int` range,
and consistency with the sibling key beats a solitary `long`. The `long`/checked discipline
(widen before multiplying, divide by 1000 last, overflow throws — `LaneCost.cs:131-144`) applies
at the **debit arithmetic**, which `budget-debit` owns, not here. No literals in code: the loader
reads every number from JSON; `MovementPolicy` gains no `const` for any of these keys.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldTuning"
python gk-fusion/scripts/guard-single-writer.py   # untouched, but this spec's non-touch list overlaps its seam
```

(Tuning publish: `python gk-core/tools/tuning/publish.py world movement.claimCostMilli=250 [...]` —
exact command at implementation time; values per §Design 1.)

## Structure

```
data/tuning/world.v{n+1}.json   NEW VERSION — movement gains 6 keys (§Design 1); _meta.v{n+1}Note
gk-core/src/FusionRpg.Core/World/WorldTuning.cs   EXTENDED — MovementTuning fields + Parse arms (§Design 2)
tests/.../WorldTuning*   EXTENDED — missing-key rejection per new key; round-trip of new rows
test bootstraps that construct MovementTuning   UPDATED — `gk-core/tests/FusionRpg.E2E.Tests/ContractTuningTestBootstrap.cs`,
  `tests/FusionRpg.Core.Tests/ContractTuningTestBootstrap.cs`, `gk-core/tests/FusionRpg.Server.Tests/WorldPolicyTestBootstrap.cs`
  (positional/new-field construction breaks until the 6 new args are supplied — update in the same change, not a follow-up)
UNTOUCHED: LaneCost.cs (no BudgetFor change), TurnEngine.cs (no refill change),
           WorldCommand.cs (no new kinds), every resolver/verb body (no debit logic),
           PointsPerTurn / ScoutPointsPerTurn / dowseBudgetMilli values
```

## Code style

```csharp
// One line per key, same shape as the dowse arm — a new priced verb is a new line, never a new path.
ClaimCostMilli: Int(mv, "claimCostMilli", "movement"),
```

## Testing strategy

- **Missing key rejects by name:** delete each new key in turn from a candidate document —
  `WorldTuningRejection` names `movement.<key>` (T5; mirrors the existing dowse rejection).
- **Non-integer rejects:** a string/float/negative for any new key rejects (same `RequireInt`
  path; negativity is a config error — a cost is never negative — and must fail at load, not at
  debit).
- **Round-trip:** parse of the shipped `world.v{n+1}.json` yields the §Design 1 values through
  `WorldTuningHub.Tuning.Movement.*`.
- **No golden moves:** the full world-map golden set is byte-identical before/after — nothing
  reads the new keys yet (the v3 identity-value precedent). If any golden moves, this module is
  wrong, not "also a rebalance" (T7).

## Boundaries

- **Always:** `*Milli` suffix with per-mille units (T6); missing key throws naming it (T5);
  publish via tool, never hand-edit (T4); old version stays (revert = restore a file).
- **Ask first:** pricing a reserved candidate (`clear`/`sustain`) — that is a later spec's
  decision, not implementation latitude; changing any provisional value for balance reasons
  outside a declared balance pass (T7).
- **Never:** debit logic of any kind (budget-debit owns the seam); new `WorldCommandKind`s
  (claim-pricing / plan Task 4A.1 owns kinds); refill/`BudgetFor`/frame changes (fixed frame,
  Locked anchors); a second pool, count cap, or level curve (ideal §Rejected — Fork B/C need
  their own overturn evidence); `const` costs in code (T1/T3); silent defaults for missing keys
  (T5).

## Success criteria

1. `world.v{n+1}.json` parses with all six keys visible at
   `WorldTuningHub.Tuning.Movement.*`. 2. Each missing/new-key violation rejects naming the key.
3. World-map goldens byte-identical (nothing reads the keys yet). 4. `budget-debit` and
   `hold-allowance` can start against the key names, units, and defaults below without
   re-asking this module for anything.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `movement.claimCostMilli` (int ‰, default 250) | `budget-debit` (module 2) — the per-claim spend |
| `movement.depositCostMilli` / `withdrawCostMilli` (int ‰, default 100) | `budget-debit` — the per-deposit/withdraw spends |
| `movement.loadCostMilli` / `unloadCostMilli` (int ‰, default 50) | `budget-debit` — the per-load/unload spends |
| `movement.holdAllowanceMilli` (int ‰ budget points, default 250) | `hold-allowance` (module 3) — the garrison act allowance |
| `WorldTuningHub.Tuning.Movement.*` load path; missing-key rejection naming `movement.<key>` | both — the only supported read seam; no direct JSON read, no default |
| Reserved (not shipped): `clearCostMilli`, `sustainCostMilli` | future spec — names held so two specs do not mint two spellings |

## Non-touch list (explicit)

This module does not: implement debit-after-refill or refill-minus-spent (budget-debit);
create `WorldCommandKind`s or payload/admission arms (claim-pricing / Task 4A.1); change the
Snapshot refill, `BudgetFor`, or any stance frame value; retune `PointsPerTurn`/scout/hold/dowse;
price `clear`/`sustain`/`build`; add count caps (Fork C is unevidenced); touch Status/ActorHub/
Combat/Injector/FE surfaces.

## Design-gate checklist

```
[x] Subsystems: world-map tuning surface (Core parser) + data/tuning/world.v{n}.json — no
    Status/ActorHub/Combat/Injector/FE subsystem touched.
[x] Session boundary: worktree empire-development-20260915-b7e2 only; main checkout untouched.
    (Spec-only session: one new file under docs/architecture/world-action-economy/.)
[ ] Session-boundary record + scripts/session-boundary-check.py — NOT run this session
    (no code edited, no commit attempted; honest gap, one sentence).
[x] Read this session: world-action-economy-map.md row 1; world-action-economy-ideal.md
    §Tunables + module breakdown row 1 + Locked constraints preamble; tunables-ssot.md
    (§1 Grey-zone tiebreaker, T1/T4/T5/T6/T7, §7.2); DESIGN-GATE.md §1 Tunable-number row +
    §2 invariants 11/12/13 + §5 checklist.
[x] Checked decisions.md for a lock: Owner resolutions 2026-09-15 (Q1–Q6) are the governing
    locks; no other "action economy" lock exists — greenfield confirmed by the ideal doc's
    own decisions.md grep.
[x] Every factual claim cites file:line (see §What already exists table).
[x] Verified claims against CODE, not comments: WorldTuning.cs (record :19, loader :125-127,
    hub :224-234), LaneCost.cs (:32-57, :131-144), world.v5.json (:7, :83-85) all opened
    in-session in the worktree.
[x] Read the surrounding section of every rule quoted (tunables T-rules cited with their
    §1-class/§7-host context; dowse comment cited with its W30 balance-not-structural section).
[x] Tested (not assumed) constraints: no suite run — spec phase, and this module's core
    constraint claim ("no golden moves") is stated as an acceptance test for implementation,
    not as a measured result.
[x] Nothing contradicts a §2 invariant: SQL untouched (no Data change); no magnitude cap
    (costs are spends with named refusals downstream, allowance is a tuned number, not a
    progression ceiling); no f(level); no second pool/composer/path (Fork B/C rejections
    restated in Boundaries, not relitigated).
[x] Corrections propagated: Q3 scope (claim+deposit priced, build excluded, clear/sustain
    reserved) appears in Design, Tunables-equivalent table, Interface, and Non-touch list
    identically.
[x] No assertion pins a derived-population count, item total, generated name/description
    text, or per-cycle outcome. (Integers named: 250/100/50 are provisional content
    defaults with a stated balance-pass owner, not guardrails; 1000/500/0/250 frame values
    are cited live-code readings.)
[x] No event-refreshed cache introduced. (N/A — no cache, no triggers.)
[x] No acceptance criterion fixes an ordering. (N/A — debit order belongs to budget-debit;
    this module's criteria are order-independent load/reject/shape tests.)
[x] No actor combat/derived magnitude produced or consumed — no Hub-adjacent subsystem touched.
[x] No SOLID-violating parallel path: one tuning file, one record, one loader, one hub —
    reuse of the dowse path throughout; the parallel price engine is named in §Rejected-by-
    reference (ideal §Rejected) and restated as a Never in Boundaries.
```
