# BCU6.3 — X7/D27 ContainerKind re-check

X7 has been fully landed for a while: `ContainerRow.cs:31-43` ships Gem/Charm/Combo/Consumable
(D27's four asks), plus Relic/EmpireTitle/ActorTitle/SpeciesProgression appended since. Six separate
stale "not landed" claims found scattered across item-todo.md, all corrected in place, history kept.

`ConsumableLimits.ConsumableContainerKindAvailable = true` (ConsumableDef.cs:230) confirms the one
named flip-line already flipped 2026-09-07.

```
$ python scripts/audit-doc-citations.py --scope tasks/item-todo.md --strict
16 pre-existing HIGH, none inside any of the 6 edit hunks (line-number filter confirmed)
```
