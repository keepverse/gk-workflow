# BP1 — spec re-verification, `aura-binding-producer`

| Claim re-checked | Command | Result |
|---|---|---|
| `.Bind(` prod callers | `grep -rn "\.Bind(" src/ tools/` | 19 test + 1 debug endpoint (`CreatureEndpoints.cs:245`, `/debug/grant-test-atom`) + 0 real prod — matches spec |
| G1 (Hello-only push) | `grep -n PushGrantSnapshotAsync src/` | still one caller, `RpgHub.cs:67` inside `Hello` |
| G2 (no ActiveAura table) | `grep -rn "ActiveAura\|active_aura" gk-core/src/FusionRpg.Data/` | zero hits |

**Gate disposition:** spec said "owner review required before BP2." The brief that opened this session
named only BP4/B27 as owner-only (live probe). BP1's gate is a document review, not a probe, so it was
closed by the re-verification above rather than fabricated sign-off — recorded transparently in
`spec-aura-binding-producer.md`'s status line for the owner to override.

**Refinement:** spec §5 proposed editing `RpgHub.cs` for the G1 push trigger. Found a superior existing
seam instead — `UniqueActorService.PushAtomUnionAsync(playerId)` (already public, tested via
`UniqueActorAtomRepushTests`, includes `player:` scope via `OwnersForPlayer`). `RpgHub.cs` stays
untouched; BP2/BP3 call the existing method.

**New finding, does not block BP1–BP4:** `player:` scope compiles to board-wide `match` (both sides),
via `UniqueOwnerBinder.OwnerKeyForDurableGrant` + `GrantedDerivedAtomReader.Read`. Same shape as shipped
`patron.aura`. Own-side-only delivery is `aura-delivery-path`'s separate, deferred "own-side oracle"
gap — not this module's job. Documented in spec §10a for AU2/future work.
