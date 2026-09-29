# Evidence — rpg-simulator RS-F4 (the seed seam's spec)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). Row RS-F4; module `seed-seam` (map row 11). **Spec-only increment** — the row's own
wording is that the fix *"must be decided by its own spec, not smuggled into a runner"*, and the one product
consequence it names (§5/§6) wants a ruling before four live routes change what a player can compute.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The spec exists, names the shape, and every citation resolves | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-doc-citations.ps1 -Strict` | 0 HIGH for the new document (the two HIGH D3 findings are a LOAM document, RS-F18) | `docs/architecture/rpg-simulator-spec-seed-seam.md` |
| The map indexes it as a module | read: module table row 11 `seed-seam`, and the dependency-direction sentence now names it | row 11 present, `seed-seam` feeds `readback-verdict`'s digest | `docs/architecture/rpg-simulator-map.md` |
| RS-F4's acceptance branch (b) is satisfied, not left implicit | read: `tasks/rpg-simulator-plan.md` §11 item 3 | "the corpus's declared digest covers **host-stable readings only** … the reason is measured, not assumed" + the 71–110-pointer measurement | `tasks/rpg-simulator-plan.md` |
| The measured surface is corrected | `grep -rn "Guid.NewGuid().ToByteArray\|BitConverter.ToUInt64" src/ --include=*.cs` | **4** mint sites (`CreatureEndpoints.cs:95`, `ExpeditionEndpoints.cs:38`, `FusionEndpoints.cs:39`, `WebMatchService.cs:122`) — the row named 2 | `docs/architecture/rpg-simulator-spec-seed-seam.md` §0/§4 |
| The derivation reuses the house chain rather than inventing one | read: `gk-core/src/FusionRpg.Core/Effects/Atoms/WorldSeed.cs:24` + `gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:26` | `WorldSeed.DeriveRollSeed` is documented as *"the ONE place `hash(worldSeed, streamName, targetId)` is computed … never reimplements it"*; `SeededRng.DeriveStream` is the primitive under it, and its doc refuses `string.GetHashCode` | same |

**Not implemented, on purpose, and the blocker is named exactly:** increment 1 (the named helper + the four
call sites) waits on the **predictability ruling** the spec's §5/§6 states — the derivation is public, so a
client could compute a chosen key's roll offline; the capability is not new (a player can already reroll
without limit) but its cost drops from pay-per-roll to compute-per-roll. Increment 2 (the corpus's declared
digest covering roster and battle values) depends on increment 1. A guard that fails a fifth mint is owed
*with* increment 1, not before it.

**Refused shapes, each with its reason, are in the spec §6** — a `seed` body field, a `/api/sim/*` seed route
(D3 (b)), a server-global seed config (wrong scope: a seed is per-request), and a per-save secret (it would
defeat the fresh-host reproducibility the double-run falsifier exists to measure).
