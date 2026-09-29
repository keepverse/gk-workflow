# BCU4.1, 4.3, 4.4, 4.6 (partial) — creature-remainders batch

BCU4.1: no overlap between creature-seed `CreatureRank` (content-gen rank tier) and
`species-progression` (runtime levels) — decision recorded, no fenced-file edit needed.

BCU4.3: no session owns `creature-lawn-deploy-todo.md`; T4.1's deferred-death bridge needs a
real live-injector probe (qa-tester shaped) — scheduled, not built.

BCU4.4: real fusion test written. Found the box's own premise was impossible (recipe inputs are
always same-rung by a documented invariant); wrote the real testable claim (source rarity != output
rarity) instead. Found a second real thing: discovery bonus interferes with a naive souls-total
assertion — read back from `outcome.DiscoverySouls`.

```
$ dotnet test gk-core/tests/FusionRpg.Data.Tests --filter FusionInheritancePicksTests
8/8 (run twice for determinism, both green)
$ python scripts/audit-doc-citations.py --scope tasks/creature-standalone-todo.md --strict
0 HIGH (52 citations)
$ python scripts/audit-doc-citations.py --scope tasks/backlog-clean-up-todo.md --strict
0 HIGH (43 citations)
```

BCU4.2, BCU4.5: genuinely blocked (D2.2 incomplete; `cmdc/lane-c` fence on `creature-seed-todo.md`).
BCU4.6: F4/F5 re-confirmed live and unchanged; F1 routing blocked on the same fence as BCU4.5.
