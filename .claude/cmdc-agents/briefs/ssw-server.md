# Task: PT7b — the second producer of `patron:aura` must stop stamping `match`

**First action:** merge the integration branch into your own branch — `git merge --no-ff features/mega-merge` (HEAD `3f4d6411`). Your base is `cmdc/scope-side-wide`, which already carries the side-wide key work (`181910db`, `57fc1c25`, `7d916731`, `80e455bd`); keep those commits.

Programs: `tasks/creature-standalone-todo.md` row **PT7b** (filed by the `scope-side-wide` lane) and the
`aura-skill` program's doc-citation row. Read both rows before writing anything, plus
`docs/architecture/aura-skill/spec-aura-binding-producer.md` (the producer contract) and the SSW commits
already on `cmdc/scope-side-wide` (`181910db`, `57fc1c25`, `7d916731`).

## The defect you are fixing

`gk-core/src/FusionRpg.Server/PatronEndpoints.cs:82` — `TryBuildPatronSessionGrant` builds the session grant for
grant id `patron:aura` with `OwnerKey = "match"` and an implicit owner kind. That grant is upserted into
the effect-grant session at every `pvzrh` board.start and pushed again on Hello/bind re-push, so whichever
write reaches the injector bag last decides the key's scope. `scope-side-wide` widened the grammar
(`EffectOwnerKey.PlantSide` = `plant:*`) and made `InMemoryEffectGrantStore.ForOwner` honour a side-wide
key; this second producer therefore **overwrites the side-wide scope with the match scope**, and PT7
criterion 2 ("a patron-shaped grant does not apply on the zombie side") cannot pass live until this line
moves.

## What to do

1. `TryBuildPatronSessionGrant` stamps `EffectOwnerKey.PlantSide` (`plant:*`) and the owner kind that
   accompanies a side key. If the `EffectGrantDto` shape needs a kind field to express it, add it in
   `gk-core/src/FusionRpg.Contracts` rather than inventing a second grammar.
2. **Contracts mirror**: `gk-core/src/FusionRpg.Contracts/EffectDtos.cs` `EffectOwnerKeys` (line 151) has no
   side-wide member — the Core constants live in `gk-core/src/FusionRpg.Core/Effects/EffectProcAndOwner.cs`
   because Contracts was outside that lane's fence. Add the mirror there so no producer hand-spells
   `"plant:*"`.
3. The injector's own plugin (`PatronSecondaryPlugin`) already stamps the side-wide key; make the two
   producers agree, and say in a comment which one wins on reconnect (they must converge, not fight).
4. **Test at the real seam**: a `gk-core/tests/FusionRpg.Server.Tests` test that goes through the real grant
   projection (not a hand-built DTO) and asserts the grant that leaves the server carries the plant-side
   key and that a zombie-side lookup does not match it. A Core-only unit test is not enough — the defect
   is a second producer, so the proof must be on the producer.
5. Re-anchor the doc citation `docs/architecture/aura-skill/spec-aura-binding-producer.md:312` if your
   change moves it, in the same commit, and run `scripts/guard-doc-citations.ps1 -Strict`.

## Do not

- Do not touch the `instance:` Hot guard or the `player:` stub in `StatApplyScope.cs` — both are
  deliberate (S-INSTANCE-KEY-HOT and a match-wide stub).
- Do not change the side-wide key's existing semantics: `IsMatchWide(plant:*)` stays `false`.
- A moved battle golden means your change is wrong. Do not re-bless any golden.

## Verification

> **Runner note:** the runner takes the *first code span of each bullet in this section* as a
> verification command and runs it **verbatim** — a placeholder like `<every changed path>` is never
> substituted, so it is run as written and fails with a shell error. Each bullet below is therefore a
> real, substitution-free command; run the full `verify-change.ps1` yourself with your real changed
> paths and report the **numbers printed**, never the exit code alone (TVB-F3).

Boundary check -- run it yourself with your real changed paths (the runner cannot substitute a
placeholder, so this is deliberately not one of the bullets above), then report the numbers printed:

```powershell
./scripts/verify-change.ps1 -Paths <paths you changed> -Session ssw-server
```
- `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StatApplyScope|FullyQualifiedName~Patron"`
- `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Patron"`
- `pwsh -NoProfile -File scripts/guard-actor-hub.ps1`
- `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict`

Run them in the FOREGROUND. On `user-mapped section open`, run `dotnet build-server shutdown` and retry.
