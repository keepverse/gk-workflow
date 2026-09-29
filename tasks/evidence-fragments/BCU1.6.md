# BCU1.6 — paperwork-reconcile P6 (creatures/species)

6 files: creature-progression-todo.md, creature-seed-todo.md, species-build-todo.md,
creature-corpus-self-heal-todo.md, creature-lawn-deploy-todo.md, creature-standalone-todo.md.

Live verifications performed (not just paraphrase from the lane report):
```
$ grep -n "_resolveBoundInstanceId" gk-core/src/FusionRpg.Core/Stats/Aptitudes/SpeciesAllocationSource.cs
118:        if (_resolveBoundInstanceId is not null)
$ grep -n "KnownMissingPlanSpecies =" gk-core/tests/FusionRpg.Core.Tests/Creatures/SpeciesBuildPlanCatalogRealFileTests.cs
102:    static readonly IReadOnlyList<string> KnownMissingPlanSpecies = Array.Empty<string>();
$ python -m seedsmith creatures run status --json
{"state": "idle", "message": "no in-progress or paused run"}
```

`audit-doc-citations.py --strict`: pre-existing HIGH findings on creature-seed-todo.md (2),
species-build-todo.md (1), creature-lawn-deploy-todo.md (2) all confirmed as unmodified context lines
in my diff hunks (checked line-by-line, not just hunk range, since one false-positive-looking case
turned out to share a hunk without being the changed line).
