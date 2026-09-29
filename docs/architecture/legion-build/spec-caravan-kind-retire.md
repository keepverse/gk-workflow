# Spec: `caravan-kind-retire`

**Status: written against shipped code 2026-09-19** — every `file:line` below was opened this session.
Module id `caravan-kind-retire`, row 2 of the [legion-build map](../legion-build-map.md) (wave 1; no
dependencies). Ideal: [legion-build-ideal.md](../legion-build-ideal.md) §6.6 and owner decision **L3**
(*"a caravan is an automated legion, with or without a commander; no separate mode"*). Ownership: map X15;
`docs/architecture/trade-network/fleet-map.md:140` records that `fleet` consumes the result.

## Objective

`WorldEntityKind.Caravan` is declared and never constructed. A caravan is a legion on a trade standing
order (L3), so a separate kind can only invite a second mode. Remove it, and every place that names it.

Success looks like: the enum has four members, nothing in `src/`, `tests/` or `web/` names `Caravan`,
every existing save loads, and no golden moves.

## Scope and non-goals

- **In:** the enum member, its naming arm, its FE word, the tests that pin them, and the stale FE comment
  that points at the enum's old line numbers.
- **Out:** anything that makes a legion behave like a caravan — that is `standing-orders` (the
  `trade-route` kind) and `fleet`'s `trade-route-order`.

## What already exists

### Built but dead

| Finding | Evidence |
|---|---|
| Declared | `gk-core/src/FusionRpg.Core/World/WorldState.cs:61-67` (`Caravan` at `:66`) |
| Named | `gk-core/src/FusionRpg.Core/World/EntityNaming.cs:34` |
| Pinned by a Core test that constructs one by `with` | `gk-core/tests/FusionRpg.Core.Tests/World/EntityNamingTests.cs:72-76` |
| FE word | `gk-web/web/fusion-rpg-web/src/ui/world/worldEnums.ts:53`; test `gk-web/web/fusion-rpg-web/src/ui/world/worldEnums.test.ts:53` |
| FE comment cites a stale location (`WorldState.cs:51-58`; the enum is at `:61-67`) | `worldEnums.ts:48` |
| Never constructed by any production path | `grep` over `src/` finds only the declaration and the naming arm |

### Persistence and hash (why no save or golden moves)

| Finding | Evidence |
|---|---|
| Written by name | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:378` (`e.Kind.ToString()`) |
| Read by `Enum.Parse` | `RpgStore.World.cs:632` |
| Hashed by name | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:60` |

Because the kind is persisted and hashed **by name** and no row ever held `Caravan`, removing the member
changes no stored byte and no hash. A database that somehow held a `Caravan` row would fail loudly at
`Enum.Parse` on load — the right failure, and one no real save can reach.

## Design

1. Delete `Caravan` from `WorldEntityKind`. The enum is a closed vocabulary the code owns; removing a
   never-constructed member is the reviewed change.
2. Delete the `EntityNaming` arm.
3. Delete the FE entry and its test row; correct the FE comment to cite `WorldState.cs:61-67` by symbol
   rather than line (`WorldEntityKind`), so it cannot drift again.
4. Rewrite `EntityNamingTests.cs:72-76`: the case it pins (a non-legion kind gets its own ordinal
   sequence) is kept, using `Warband`, the next never-special kind.
5. Delete any i18n row that names the kind. None exists today (`gk-web/web/fusion-rpg-web/src/i18n/locales`
   holds no `caravan` entry); the implementing session re-greps rather than trusting this line.

## Tunables and numeric types

None.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~EntityNaming|FullyQualifiedName~WorldCanonical"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldStore"
cd gk-web/web/fusion-rpg-web; npm test -- worldEnums
```

## Structure

```
gk-core/src/FusionRpg.Core/World/WorldState.cs                 MODIFIED  enum member removed
gk-core/src/FusionRpg.Core/World/EntityNaming.cs               MODIFIED  arm removed
gk-core/tests/FusionRpg.Core.Tests/World/EntityNamingTests.cs  MODIFIED  case moved to Warband
gk-web/web/fusion-rpg-web/src/ui/world/worldEnums.ts          MODIFIED  entry removed, comment by symbol
gk-web/web/fusion-rpg-web/src/ui/world/worldEnums.test.ts     MODIFIED  row removed
```

## Testing strategy

- A closed-vocabulary membership test pins `WorldEntityKind` to `{Legion, Warband, Guard, Warlord}` with
  its reason (*"a caravan is a legion on an order — owner ruling L3"*). This is a declaration, not a
  population, so pinning it is the contract (`validation-ssot.md`).
- Every world golden and store round-trip passes unchanged (proves the by-name claim above by running it).
- The FE `translateForceKind` still throws loudly on an unknown kind (its `loudLookup`), so a stale server
  string is a visible failure, not a silent word.

## Boundaries

- **Always:** re-grep `src/`, `tests/`, `web/` for `Caravan`/`caravan` before closing.
- **Ask first:** nothing.
- **Never:** add a replacement kind; move caravan behaviour into a kind check anywhere.

## Success criteria

1. No `Caravan` in `src/`, `tests/`, `web/`.
2. Every world golden and store test green with no re-bless.
3. The membership test pins the four-member vocabulary with its reason.

## Interface exposed to dependents

`fleet` and `standing-orders` build caravans as legions; neither may reintroduce a kind.

## Hard edges

None. No migration (no row holds the value), no golden re-bless, no ruleset stamp interaction. **Round 6
C1:** this module is **wave 1**; it grants **no** capability and removes a dead kind, so it adds nothing to
wave 1's single `RulesetVersion` bump — and it never claims one of its own. It still names its wave, because
the wave's bump is what a world's stamp compares against
([landing-order.md](../trade-network/landing-order.md)).

## Dependencies

None.

## Design-gate checklist

```
[x] Subsystems: world entity vocabulary, world naming, the FE word table.
[ ] Session boundary — NOT recorded (docs-only spec session scoped by its caller).
[~] Read this session: DESIGN-GATE.md, PRINCIPLES.md §3-§13, legion-build map and ideal, the rows listed
    in spec-member-stack.md's checklist. Not read: the world-map row's documents.
[x] decisions.md checked: no lock covers WorldEntityKind.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py run on this file; no HIGH finding.
[x] Verified against code (declaration, naming arm, FE table, persistence by name, Enum.Parse on load,
    hash by name, the one test that constructs the value).
[x] Read the surrounding section of every rule quoted.
[~] "No golden moves" argued from persistence and hash by name (read); the test plan proves it by
    running the suites. Not run for this spec.
[x] No §2 invariant contradicted.
[x] Corrections propagated: the stale FE comment is fixed by this module.
[x] Pinned literal is a closed vocabulary with a stated reason.
[x] No event-refreshed cache.
[x] No ordering assumption.
[x] No actor magnitude.
[x] No parallel path.
[x] No new rule needing a registry row (the membership test is the enforcement).
```
