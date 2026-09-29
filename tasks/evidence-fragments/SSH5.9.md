# SSH5.9 — combo-bind carries the circuit

`ComboBindTarget.Circuit` is the evaluator's own `CombinationResult.Circuit` (SSH4.6 mints it that way),
and the read side contributes it as `EquippedAtomInput.Circuit`, so `EquipAtomSource` renders
`combo:{role}:{host}:{comboId}#c{circuit}` (SSH4.5's Combo arm). This row proves the two consequences.

| Criterion | Command | Result |
|---|---|---|
| `the_same_word_in_two_circuits_is_two_contributions` | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~EquipProjectionSockets\|FullyQualifiedName~EquipAtomSourceId"` | **13 passed / 0** |
| `one_identity_per_circuit_is_the_only_limit` | (above) | **13 passed / 0** |
| the row's verify filter | same filter | 13/0 |
| scoped verifier | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/tests/FusionRpg.Core.Items.Tests/Items/EquipProjectionSocketsTests.cs') -Session strain-splice-host-20260922"` | **exit 0** — Core.Items.Tests 1404/0 |

What the tests assert, precisely:

- **Two circuits, two contributions.** An eight-socket host carries the same word in circuit 0 and
  circuit 1: the projection yields TWO bindings whose instance ids differ only by `#c0`/`#c1`, and the
  Hub sees two SourceIds differing only by the circuit suffix — nothing suppressed (R12: no count cap).
- **One identity per circuit is the only limit.** Two Strains on one fill: a four-socket host (ONE
  circuit) fires exactly one identity; an eight-socket host (two circuits) fires two, one per circuit —
  and both bind through the one projection, one per circuit.

`SSH4.9` (the live probe) is the remaining strain-splice-host row.
