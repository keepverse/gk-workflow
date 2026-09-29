# aura-skill T25 — the §10a `patron.aura` precedent citation is re-anchored

`docs/architecture/aura-skill/spec-aura-binding-producer.md` §10a (line 311) had recorded the patron
aura as its *precedent for accepting a match-wide scope* — and its own parenthetical
(`PatronSecondaryPlugin.cs:29`, `OwnerKey = EffectOwnerKeys.Match`) went false when `scope-side-wide`
SSW2 moved that plugin to the side-wide key. Re-anchored here because the PT7b producer fix completes
the same scope move, so no reader can follow the old sentence into the old behaviour.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| §10a names the CURRENT plugin key and the side-wide alternative | read back at `spec-aura-binding-producer.md:311-320` | PASS — `PatronSecondaryPlugin.cs:40`, `EffectOwnerKey.PlantSide` (`plant:*`, ownerKind `plant`), gate named as `StatApplyScope.OwnerKeyCovers` with `IsMatchWide("plant:*")` false | `docs/architecture/aura-skill/spec-aura-binding-producer.md` |
| §10a's own `player:` finding is intact (still open, unchanged) | same read | PASS — `player:{id}` → `UniqueOwnerBinder.OwnerKeyForDurableGrant:27-30` → `match` → `GrantedDerivedAtomReader.Read:104` collects it for every entity, both sides; the section says so explicitly and adds that no side-wide spelling exists for it yet | same |
| Doc citations resolve after the edit (the gate the row names) | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0 — 1679 documents, 24807 citations checked, D1/D2/D3/D4 0 HIGH | — |

| The document this row changes is clean under the per-path audit verify-change runs | `python scripts/audit-doc-citations.py --strict --scope docs/architecture/aura-skill/spec-aura-binding-producer.md` (the same check `verify-change.ps1` runs per doc path) | PASS — 1 document, 20 citations, D1/D2/D3/D4 all **0 HIGH**. The `tasks/aura-skill-todo.md` scope the same command audits is 0 HIGH too, after the T26 fix in this commit. The runner's own exit 1 comes from its `guard: session-boundary` short-circuit, diagnosed in `tasks/evidence-fragments/creature-standalone-pt7b.md` and T26 | `tasks/aura-skill-todo.md` T26 |

`docs/**` was outside `scope-side-wide`'s writable paths, which is why SSW2 filed this as its own row
instead of fixing it in place; the doc change rides in the same commit as the code move that made the
old sentence false.
