# `CAI4.3` — the Cold push's wire format is the only open question

Lane `cai3` (session `combat-ai-3`), 2026-09-23. Sharpened, not fixed: the payload shape is a routing
decision (a `Contracts` DTO lives outside every combat-ai lane's fence), and every other part of the row is
in fence and ready.

## THE DECISION ASKED, in one line

*Does the Cold push carry the COMPILED held-action list — which needs a wire form for `CompiledAction`'s
`ICompiledPredicate` condition tree, and therefore a DTO in `gk-core/src/FusionRpg.Contracts/**` (outside every
combat-ai lane's fence) plus a second producer of the compiled predicate — or does it carry the RAW rows
and let the injector compile through the one `ActionCompiler`, which the spec's own "the injector only
binds a ptr to a set Core produced" wording does not contemplate?*

## What was measured, and the command that measured it

| Fact | Command | Result |
|---|---|---|
| The spec's shape is "the server pushes the compiled list" | `sed -n '66,90p' docs/architecture/combat-ai/spec-lawn-held-actions.md` | steps 1–4: assemble → resolve each id through the `ActionCatalog` → sort → push the compiled list |
| No DTO for a compiled action exists | `grep -rn "CompiledAction" gk-core/src/FusionRpg.Contracts/` | **no matches** |
| …and none for the raw row either | `grep -rn "ActionRow\|ActionCompiler\|ActionCatalog" gk-core/src/FusionRpg.Contracts/ gk-fusion/src/FusionRpg.Injector/` | no matches outside this module's own `Lawn*` files |
| The compiled record is not JSON-shaped | `sed -n '31,52p' gk-core/src/FusionRpg.Core/Actions/CompiledAction.cs` | 21 members, `Condition` is an `ICompiledPredicate` interned tree, `Costs`/`Scopes`/`Targeting`/`Envelope` are compiled shapes |
| Option (b) is feasible: the injector already has the rung ladder | `grep -rn "RungTable\|RungPolicy" gk-fusion/src/FusionRpg.Injector/` | `RpgHost.cs:264-272` loads `action-rungs.v4.json` into `RungPolicy.Table`, the same file the server loads |
| The payload channel is untyped today | `sed -n '203,209p' gk-core/src/FusionRpg.Contracts/Dtos.cs` | `CommandDto.Payload` is `object?` |

## The three options

- **(a) Compiled-list payload (the spec's literal shape).** Needs a predicate-tree DTO plus a deserializer
  that rebuilds the same interned slots `ActionCompiler` builds — a second producer of the compiled
  predicate, the drift class this program exists to prevent. A typed DTO belongs in `Contracts`, which no
  combat-ai lane may edit.
- **(b) Raw-row payload, injector-side compile.** Feasible today: `RungPolicy.Table` is configured in the
  injector, and `ActionCompiler.Compile` is the one compiler, so this is a second *caller*, not a second
  implementation. Costs: a bigger payload; the container atom ids must be pushed too or every container
  action refuses; and the compile's refusals must be reported once (the `LawnBasicAttackRow.TryGet`
  posture).
- **(c) Narrowed projection (ids + the facts the policy reads).** Rejected on inspection:
  `CoreIntentPolicy` reads `Condition`, `Costs`, `Envelope` and `Targeting`, so narrowing changes decision
  semantics rather than the transport.

## Why the row stays open, and what is NOT blocked

Nothing in this row except the payload shape. `Injector/Effects/LawnHeldActionRegistry.cs`, the
`CheatCommandRunner` case, and the ADDITIVE `InjectorEntityRegistry.Remove`/`Clear` drops are all in this
lane's fence; the ptr→key resolution reuses `CheatState.ResolveBoundInstanceId` and the lawn species index
the spec's own table names. Whichever option is ruled, the push, the command case, the drop and the
`Remove(ptr)` / reused-ptr / `Clear()` tests land in ONE commit with both readers (server build + injector
parse) moved together (H7).

## NOT proved

- **No implementation was attempted**, so no build, test or guard was run for this row. The evidence above
  is reads only.
- **Option (b)'s compile-side refusals were not measured** (which action rows would actually fail
  `ActionCompiler.Compile` with the injector's `null` `statusBit`/`elementId`/`stockBit` interners, the way
  `RpgStore.BuildActionCatalog` passes them). That is the first thing the ruling's implementer should
  measure, and it decides whether option (b) needs those interners pushed as well.

## Reframed 2026-09-23: the spec answers the design question, so this is ROUTING

Re-read a day later, the spec does not leave the shape open. `spec-lawn-held-actions.md:73-80` gives four
numbered steps and says in so many words that **the server** assembles (`:75`), **resolves each
`AssembledAction.ActionId` to a `CompiledAction` through the same `ActionCatalog` path battle uses**
(`:76-78`), sorts (`:79`) and **"pushes the compiled list"** (`:80`). Its Boundaries section repeats it
(*"push from the server keyed by species / instance, never by ptr"*), and `:239` closes the other side:
*"the injector only binds a ptr to a set Core produced."*

So the compiled-list payload is the spec's answer, and the raw-row alternative is an **erratum** — not a free
choice between two designs. **What actually blocks the row is one file's fence:** the compiled list needs a
wire form, `CompiledAction`'s `Condition` is an interned predicate tree, no DTO exists
(`grep -rn "CompiledAction" gk-core/src/FusionRpg.Contracts/` returns nothing), and a typed DTO belongs in
`gk-core/src/FusionRpg.Contracts/**`, which no combat-ai lane may edit.

**The ask is therefore a grant or a route** — hand that path to a combat-ai lane, or route the DTO to a lane
that holds it — and not "pick between (a) and (b)". The raw-row option's one real attraction stays on the
record as the erratum's supporting evidence: the injector already configures `RungPolicy.Table` from
`action-rungs.v4.json` (`RpgHost.cs:278`), so `ActionCompiler.Compile` *could* run injector-side.
