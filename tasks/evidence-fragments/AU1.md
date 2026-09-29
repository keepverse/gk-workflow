# AU1 — propagate `commanderOnly` vs aura decision (docs only)

`aura-skill-map.md` decision #5 ("keep both, relationship defined... they stack; budgets stay
separate") was already settled 2026-08-31 but never propagated into the two docs that still called it
an open question, letting three sessions re-raise it. Propagated, not re-decided:

| File | Change |
|---|---|
| `docs/architecture/aura-skill/spec-aura-content.md` §10.2 | Open question replaced with the map's answer + a note on why it was stale |
| `docs/architecture/aura-skill-ideal.md:878` (Q9 table row) | "Unacknowledged second answer... undecided" replaced with the map's answer |

Nothing deleted (D1's original "delete `commanderOnly`" framing was already withdrawn before this
session — see `backlog-clear-todo.md`'s own correction). `roles.commanderOnly` and its four real
consumers outside `src/` (ItemSeedValidator, seedsmith, item test fixture, build-log) are untouched.

| Verify | Result |
|---|---|
| `dotnet test tests\FusionRpg.ItemSeedValidator.Tests` | **86/86 green** (unaffected — doc-only change) |
