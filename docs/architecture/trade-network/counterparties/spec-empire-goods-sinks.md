# Spec: `empire-goods-sinks`

**Status: written 2026-09-19 against the approved map. Spec phase; no build authorized.** Every
`file:line` below was opened in this session. Module id `empire-goods-sinks`, row 10 of the
[counterparties map](../counterparties-map.md) (wave 3; depends on `empire-treasury` and `need-vector`).
Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §7.4 (an empire *"spends them on world-scoped
sinks"*), principle 10, §10 C3 (*"Every AI empire now runs the same goods economy with world-scoped
sinks"*), §12 (v1 exclusions); [empire-economy-ssot.md](../../empire-economy-ssot.md) §2 (*"Some buildings
cost essence alongside loam"*). Session record: `tasks/sessions/trade-network-idea-20260919.json`.

## Objective

Give every empire's banked goods **somewhere to go**, the same way for the player and for every AI empire,
so an AI treasury cannot only grow and Shape B throttles AI empires exactly as it throttles the player.
The v1 sink owned here is the **compound structure cost**: a structure that costs goods alongside loam,
paid from the builder's banked goods — the player's wallet or an AI empire's treasury.

Success looks like: an enemy empire that banks fire essence spends it raising the buildings that need it;
the player pays the same goods for the same building from the wallet; a build the builder cannot pay for is
refused with a reason, never half-paid; the economy report shows an AI treasury whose net flow falls as
well as rises.

## Scope and non-goals

**In scope:** the goods-cost term on a structure build, its affordability check and payment for both kinds
of builder, the logged pre-step affordability input that makes the player's side replayable, the
planned-sinks demand term registered into `need-vector`, and the report rows.

**Non-goals:** the goods cost *values* (bands in `empire-seed`'s structure corpus); legion equipment
production and doctrine goods upkeep (both consume **located** goods where a legion stands — `legion-build`
owns them, §4); siege preparation (excluded from v1, map contradiction C3); trade payments (`exchange`).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| A build pays loam from the building legion's carried loam, and rubble/ironwork from the sector, inside `Step` | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:128-150` |
| The Data-side pre-step / post-step pattern for a build cost the step cannot see (relics): validate immediately before `Step`, spend immediately after the diff for every build the report shows started | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WonderBuild.cs:10-12`, `:53`, `:164`; called at `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:544`, `:611` |
| Materials are a player-keyed balance with no location | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs:185-195` |
| Replay re-steps each turn's **stored** commands, not the in-memory rewritten ones | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:771-776` |

### Wiring gap

Compound building costs are designed but no structure cost reads a good (`empire-economy-ssot.md` §2).

### Real gap

Every goods sink on the map.

## Design

### 1. The goods-cost term

A structure definition gains `GoodsCost`: a list of `(goodId, qty)` resolved from `empire-seed`'s
`costProfile` band table, scaled by the building sector's content scale (PS-5: the cost reads the same
scale as the goods that pay it, `sector-yield` `essence-loop-read`). A structure with an empty list costs no
goods — every structure that exists today.

### 2. Who pays, and from where

| Builder | Pays from | Checked | Paid |
|---|---|---|---|
| An AI empire (dominant, rival) | its treasury (`empire-treasury`) | inside `Step`, in `BuildResolver`, with the loam and rubble checks | inside `Step`: `EmpireTreasury.TryDebit`, all-or-nothing with the other costs |
| The player | the banked wallet (Data-side, unlocated) | **before `Step`**, in the commit transaction: the wallet covers every goods cost of the turn's admitted `build` commands in reveal order | **after `Step`**, in the same transaction, for each build the report shows started (`build.started:`), through `trade-foundation` `material-ledger` with a dedupe key |
| A clan, the wild | nothing | a build naming a goods cost is refused `build.no-banked-goods` | — |

- The two columns are the same rule over two stores. The player's wallet is outside the step by design
  (principle 9; economy-principles P13), so the player's half follows the relic precedent's pre/post shape
  (`RpgStore.WonderBuild.cs:10-12`).
- **The pre-step answer is logged.** The relic gate rewrites commands in memory before `Step`
  (`RpgStore.WonderBuild.cs:53`) while replay steps the stored commands (`RpgStore.WorldTurns.cs:773`); a
  gate whose verdict is not stored is a replay hazard (read, not run — noted for that program's owners).
  This module stores its verdict as a **registered kind of the one logged step-input record**,
  `rpg_world_step_inputs` owned by `relation-facts` (`spec-relation-facts.md` §3): `input_kind = 'goods-cover'`,
  `input_key = <command_id>`, `value = '1'|'0'`, written before `Step`, passed to `Step` in the one
  `StepInputs` value, and read back by replay. `BuildResolver` refuses an uncovered player build with
  `build.goods-short`. *(Corrected by the 2026-09-20 audit: the first draft created a second table,
  `rpg_world_goods_cover`, beside the one record — the parallel logged-input channel map C17 and round-5 X14
  rule out: "counterparties keeps one step-input table".)*
- **All-or-nothing:** a build is either paid in full — loam, rubble, ironwork and goods — or refused with
  nothing spent.

### 3. The planned-sinks demand term

This module registers `planned-sinks` into `need-vector` (`IDemandTerm`): a faction's demand for good `g`
includes the goods cost of the cheapest structure it can currently build that costs `g`, looked ahead
`needs.reserveTurns`. So an AI wants what its next building needs **before** the build is refused — the
AI-side reason the treasury drains.

### 4. The sinks this module does not own (named, so silence is not mistaken for coverage)

| Sink | Pays from | Owner | Why here only as a symmetry check |
|---|---|---|---|
| Legion equipment production | located goods in the producing sector's warehouse (`legion-build-ideal.md` §6.7: *"Pieces are located goods"*, produced by a sector building) | `legion-build` | It applies to every owner of a producing building by construction; this module asserts that |
| A doctrine's goods upkeep | located goods *"through the existing cargo and supply paths"* (`legion-build-ideal.md` §6.5) | `legion-build` | Same |
| Siege preparation | — | excluded from v1 (ideal §12: *"warehouse goods seeding a siege depot"*) | Map contradiction C3 |

The approved map listed legion equipment and doctrine upkeep as sinks of this module. They consume
**located** goods, not the treasury, so they belong to the program that owns them; this module keeps the
obligation to test that each applies to every empire kind. The map is corrected.

### 5. The report

`trade-foundation` `economy-report` gains, per empire: goods banked in, goods sunk by reason (structure
cost; later ones by their owners), treasury balance. P1: an AI treasury's net flow is not monotone positive
over a scripted campaign **once a policy files builds** — until `trade-ai` does, the report prints the
treasury line with a verdict column and asserts only the arithmetic (the `sector-yield` *"declared, not
hidden"* practice). P6: sink share by reason is printed.

**The sink is finite; the faucet is not (audit 2026-09-20).** Banking at Counting Houses pays every turn for
as long as the empire holds ground; structure goods costs are paid once per building and once per tier, and
an empire's slots and tier ladders are finite. So once an AI empire has built what its ground allows, its
treasury has no drain left and grows every turn — the P1 assertion above then fails by construction on a long
enough campaign, and P2 (territorial income needs territorial upkeep) has no treasury term. The player's
banked goods do not have this problem, because the player also spends them on account-scoped sinks (fusion,
the item workbench) an AI empire does not have.

**CQ2 is answered (round 6).** *"Legion equipment and doctrine upkeep may draw on banked goods when local
stock runs short — the same rule for the player and every AI, so no handicap."*
([../decisions-round-4.md](../decisions-round-4.md) Round 6 CQ2). That is the recurring drain the treasury
was missing, and it is recurring by nature: a legion is re-equipped as it takes losses and pays doctrine
upkeep every turn it is fielded, for as long as the empire fields legions — so the sink scales with the same
thing the faucet does, the ground held. Consequences this module takes:

- **Two sink reasons join `GoodsCost`'s**, both recurring: `legion-equip` (a fitting or refit whose local
  located stock is short) and `doctrine-upkeep` (a per-turn doctrine cost whose local stock is short). They
  are `stock-deltas` fact kinds like every other draw, and they debit the **treasury**, not a sector.
- **Local stock first, always.** The banked draw is a *fallback*: the sector's located stock
  (`sector-yield` `legion-equipment-stock`) is spent first, and only the shortfall reaches the treasury.
  A rule that spent banked goods while local stock sat unused would turn banking into the cheap path and
  make lanes pointless.
- **Symmetric by construction, and tested as such.** The same fallback applies to the player's wallet. The
  test is the family's own symmetry rule (umbrella invariant 11): one fixture, the same legion and the same
  shortfall, once with a player owner and once with an AI owner, must debit the same quantity for the same
  reason. Neither side gets an allowance the other lacks.
- **The legion-build side is an ask, not a rule written here.** *Which* fittings and which doctrine upkeep
  may fall back, in what order, and what happens when the treasury is empty too, belong to `legion-build`
  (`legion-equipment`, `legion-doctrine`) and `sector-yield` `legion-equipment-stock` §3a. This module owns
  only the treasury debit and its reasons.
- **The P1 assertion changes with it.** The *"only while a goods-cost build is available"* caveat and its
  "ladder complete" verdict column are **withdrawn**: with a recurring sink the treasury line is asserted
  over the whole campaign. The one thing still gated on `trade-ai` filing builds is the *build* half of the
  sink, which is unchanged.

### 6. The capability flag

`counterparties.sinks` joins `world-stamp`'s registry — in **`counterparties` wave 3**, sharing that wave's
single `RulesetVersion` bump with `counterparties.clanEconomy` and `.conquest` (round 6 C1; row 17 of
[../landing-order.md](../landing-order.md) §2). Without it, `GoodsCost` is ignored, the two CQ2 fallback
reasons never fire, and every build costs what it costs today.

## Tunables

- `needs.reserveTurns` (`data/tuning/trade.v{n}.json`, turns; starting 3 — see `spec-need-vector.md`),
  added by this module with its demand term.
- Goods cost values: `empire-seed` bands, not here.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| goods cost, balances, reserved and covered quantities | `long`, `checked`; scaling through `ContentScale.Apply` (widen, multiply, divide once) | value-normalised magnitudes scale with `P(Θ)` (PRINCIPLES §5) |

## Acceptance (contract)

1. **Symmetry:** the same structure in the same sector costs the player and an AI empire the same goods,
   paid from their respective banked stores.
2. **All-or-nothing:** a build short of any one cost term — loam, rubble, ironwork or a good — spends
   nothing and drops with a named reason (`build.goods-short` for goods).
3. **Replay:** a turn with a covered and an uncovered player build replays byte-identically from the stored
   commands and the stored cover rows, with no wallet read.
4. **Idempotent payment:** re-committing a turn spends nothing twice (material-ledger dedupe key).
5. **Treasury drains:** an AI empire that builds a goods-cost structure reduces its treasury by exactly the
   cost, and the stock delta records `sink`.
6. **No faucet named without its sink:** every goods cost row resolved from `empire-seed` names the stock it
   drains; a good with a faucet and no sink fails the report's registry check.
7. **Located-goods sinks are symmetric:** for `legion-build`'s equipment production and doctrine upkeep, the
   player and an AI empire with identical holdings consume identical goods (asserted when those land).
8. **Legacy:** without the flag, a build costs exactly what it costs today and the hash is unchanged.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Trade/Sinks/StructureGoodsCostTests.cs` (new): symmetry,
  all-or-nothing, treasury debit, uncovered player build refusal given the cover input.
- `gk-core/tests/FusionRpg.Data.Tests/WorldTurnCommitTests.cs` (extend): pre-step `goods-cover` rows in the one
  step-input record, post-step payment, idempotent re-commit, replay reads the cover rows through the same
  `StepInputs` read the band snapshot uses. In memory.

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs','tests/FusionRpg.Core.Tests/World/Trade/Sinks/StructureGoodsCostTests.cs','gk-core/tests/FusionRpg.Data.Tests/WorldTurnCommitTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Trade.Sinks|FullyQualifiedName~WonderBuild"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurnCommit|FullyQualifiedName~Materials"
python gk-core/scripts/guard-dal.py ; python gk-core/scripts/audit-overflow.py
```

Crosses Core and Data: the full suite once at module end.

## Hard edges

- **Wallet spend in the turn commit.** The player's payment writes the materials balance inside the world
  commit transaction; it must go through `material-ledger`'s one verb (P14), never a direct write.
- **Corpus dependency.** No structure costs goods until `empire-seed` bands give it one; the module can land
  with the mechanism and zero goods-cost rows.
- **Shared reservation shape.** `exchange` `settlement-payment` reserves souls before the step and settles
  after it. Both verdicts now live in the one step-input record as registered kinds (`soul-budget`,
  `goods-cover`); ask A13 is superseded by `exchange`'s E-A7 and by this correction (audit 2026-09-20: this
  bullet still asked `exchange` to copy a separate cover table).
- **A new step-input kind** (`goods-cover`) widens `relation-facts`' closed `input_kind` vocabulary — a
  reviewed change made in this module's change, pinned in that module's test.

## Dependencies

| Consumes | From |
|---|---|
| `EmpireTreasury.TryDebit` | `empire-treasury` |
| `IDemandTerm` registration | `need-vector` |
| Goods cost bands (`costProfile`) | `empire-seed` structure corpus |
| `material-ledger`, `stock-deltas` (`sink`), `economy-report` | `trade-foundation` (A10) |
| Content scale read | `sector-yield` `essence-loop-read` |

| Exposes | To |
|---|---|
| `GoodsCost` on a structure, the cover input, `build.goods-short` | `trade-ai` (build planning), `trade-surface` (why a build was refused), `exchange` (A13) |

## Contradictions found

1. **The map's sink list** named legion equipment production and doctrine upkeep as this module's; both
   consume located goods owned by `legion-build` (§4). Corrected in the map.
2. **Relic gate replay** (observation, not verified by a run): the wonder relic gate's verdict is not
   stored, while replay steps stored commands. Outside this fence; recorded for the loam-relics-wonders
   program. This module does not copy that shape.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: structures and BuildResolver, economy (P1, P5, P6), materials wallet, turn commit, replay,
    AI demand, tunables.
[~] Session boundary: trade-network-idea-20260919; session-boundary-check.py not re-run for this
    docs-only file.
[x] Read this session: as spec-need-vector.md's checklist, plus legion-build-ideal §6.5, §6.7 and the
    wonder relic gate in RpgStore.WonderBuild.cs.
[x] decisions.md: Empire resource registry (:108) — no new quantity here; costs drain registered ones.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: 0 HIGH.
[x] Verified against code: BuildResolver cost checks, the relic pre/post calls, replay's stored-command
    loop, materials keying.
[x] Surrounding sections read (§7.4, §10 C3, §12; empire-economy-ssot §2).
[x] The relic replay point is stated as read-not-run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: the sink list in the map; A13.
[x] No population pinned.
[x] No cache; the cover table is a logged input written once per turn.
[x] Ordering: cover is decided in reveal order, the same order Step uses.
[x] No actor magnitude.
[x] No SOLID-violating path: one cost term, two stores behind one rule; the reservation shape shared.
[ ] Registry row: none proposed.
```

## Audit 2026-09-20

Fixed here: the player's goods-cover verdict used its own table beside `relation-facts`' one step-input record —
a parallel channel ruled out by map C17 and round-5 X14; it is now the `goods-cover` kind of that record, and
the stale "ask `exchange` to copy this table" bullet is replaced. Opened: the AI treasury's only sink is finite
while its faucet is perpetual (P1/P2) — owner question CQ2 in the map; the report's P1 treasury assertion is
scoped until it is answered. Checked and clean: all-or-nothing payment; symmetry between wallet and treasury;
PS-5 cost scaling through the one content-scale read; material-ledger dedupe; legacy hash unchanged without
the flag. **Verification boundary:** `src/FusionRpg.Core/World/Trade/**` resolves only to `core-fallback`
(`gk-core/scripts/verification-boundaries.v1.json`); the program's first implementing task adds a
`core-world-trade-counterparties` owner boundary (`src/FusionRpg.Core/World/Trade/**`,
`src/FusionRpg.Core/World/Diplomacy/**`, `src/FusionRpg.Core/World/Facts/**` and their test folders). The Data
half stays on its existing Data owner.
