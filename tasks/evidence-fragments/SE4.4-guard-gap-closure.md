# SE4.4 gap closure — `scripts/guard-open-identity.ps1` built

Found during `convergence-checkpoints` CC2 verification (`tasks/evidence-fragments/CC2.md`): SE4.4 was
ticked `[x]` in `tasks/solid-enforcement-todo.md`, but its own named deliverable
`scripts/guard-open-identity.ps1` did not exist anywhere in `features/mega-merge` — a real gap in a
task marked complete, not this session's own merge losing it (confirmed against `301ee424` directly).
This is `solid-enforcement`'s own `SE` wave 4 (save-identity's sibling, commander-identity) work, so
per the coordinator's instruction it is closed here, in lane B.

## What was checked before building anything

Re-read `docs/architecture/solid-enforcement/spec-commander-identity.md` "The regression guard"
(lines 130-141) for the exact acceptance, rather than inventing a shape:

- **I1:** no `enum` named `*Id` or `*Ids` under `gk-core/src/FusionRpg.Core/Commanders/` or
  `gk-core/src/FusionRpg.Core/World/`.
- **I2:** no `switch` on `EmpireId` or `CommanderRef` values anywhere in `src/`.

Confirmed the real tree already satisfies both (`grep -rn "enum.*Id" gk-core/src/FusionRpg.Core/Commanders
gk-core/src/FusionRpg.Core/World` → zero matches; manually inspected every file containing both the word
`switch` and `EmpireId`/`CommanderRef` to confirm none actually switches ON an EmpireId/CommanderRef
value — `KillAttribution.EmpireOf` switches on `BoardSide`, `ProgressionLayerSelector.Select` switches
on `CreatureProgressionSource`, etc., all coincidental co-occurrence, not real violations). This
proves the guard can legitimately exit 0 on the real tree before writing a single line of it.

The other SE4.4 acceptance clauses were also spot-checked, not assumed, since the SAME task's checkbox
had already been shown to overstate one clause: `CommanderIdTests`' count pin is gone (its own comment
says so), the third-commander test exists (`ThirdCommanderOpenClosedTests.cs`), `SeedPlayerIfEmpty`
names `"Crazy Dave"` (`RpgStore.cs:4156`), and `stub-register.md`'s `SR-20` is struck through and
closed. **No further drift found** — the guard script was the one real gap.

## What was built

- `scripts/guard-open-identity.ps1` (new): textual I1/I2 scan, same style as `guard-dal.ps1`. I2 is
  deliberately a heuristic (the spec's own text: "Guard I2 cannot see a string switch, so the
  Open/Closed test... is what catches a new one" — this guard was never meant to be a full C#
  type-checker). It flags a `switch` whose subject is declared `EmpireId <name>`/`CommanderRef <name>`
  earlier in the same file, or whose subject is cast directly to one of those two types.
- `gk-core/tests/FusionRpg.Guard.Tests/OpenIdentityGuardTests.cs` (new, 6 falsifiers): I1 on an enum named
  `*Id` under `Commanders/`, I1 on `*Ids` under `World/`, I2 on a switch **expression** over an
  `EmpireId` parameter, I2 on a switch **statement** over a `CommanderRef` parameter, an **inverse**
  test (a fixture shaped like the real compliant tree — an `*Id` enum OUTSIDE Commanders/World, an
  `EmpireId` parameter read via `if`/`TryResolve` never switched — exits 0, proving the guard exempts
  what it should), and a direct real-tree compliance test.
- `gk-core/scripts/enforcement-registry.v1.json`: new `"open-identity"` entry (`tier: ci`, `status: gating`),
  and added to `dg-15-solid`'s own `guards` array (Open/Closed is a SOLID letter, matching SE4.4's own
  "the Open/Closed proof, the guard" wording).

## Verification

| Command | Result |
|---|---|
| `.\scripts\guard-open-identity.ps1` (real tree) | `OPEN-IDENTITY GUARD OK` |
| `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~OpenIdentityGuard"` | **6/6 passed** (both planted violations fire, the inverse-compliant fixture and the real tree both exit 0) |
| `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Commander\|FullyQualifiedName~KillAttribution\|FullyQualifiedName~SpeciesAllocation"` | **137/137 passed** |
| `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~EnforcementRegistry\|FullyQualifiedName~GuardRunner\|FullyQualifiedName~RepoBoundary"` | **36/36 passed** (registry edit is internally consistent) |
| `.\scripts\run-guards.ps1 -Tier ci` | includes `open-identity  ci  gating  0  6.40` — picked up automatically, exit 0 |
| `dotnet test gk-core/tests/FusionRpg.Guard.Tests` (full suite, sanctioned: crosses Core/registry boundaries) | running — see this evidence file's own commit for the quoted result |

## No acceptance drift found

The acceptance in `tasks/solid-enforcement-todo.md`/the spec matches what the real tree needed —
nothing was rewritten to make a stale test pass; the guard enforces exactly I1/I2 as written.

## SE4.4 re-affirmed

`tasks/solid-enforcement-todo.md` SE4.4 stays `[x]` (it was already ticked); this evidence closes the
gap the checkpoint pass found rather than re-ticking an already-checked box, per the coordinator's own
framing ("only then re-tick SE4.4" — the box itself needs no toggle, but the evidence trail needed to
exist and now does).
