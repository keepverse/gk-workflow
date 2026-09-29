# Spec: `mode-profile` (lawn-tuning-profile module 2)

**Program:** [lawn-tuning-profile](../lawn-tuning-profile-map.md) · **Ideal:**
[lawn-tuning-profile-ideal.md](../lawn-tuning-profile-ideal.md) ·
**Depends on:** nothing · **Unblocks:** `base-relative-read`, `lawn-combat-baseline`,
`zombie-power-source`, `lawn-resource-scale`
**Status:** spec, 2026-09-16. Not built.

## Objective

Give a mode — lawn, battle, delve, siege, sim — one **named row of dials** that the one `ActorHub`
reads while composing an actor, so the lawn can be tuned without moving battle, and so a later module
has somewhere to put a number instead of inventing a constant.

Today every mode shares one set: the lawn and the web battle read the same
`battle-resources.v{n}.json` and the same aptitude edges, and battle's set was tuned at Θ=20 against a
1,000-hp ladder baseline while the lawn's base values are vanilla PvZ's (a pea is 20). That single
sharing is the root of M1, M2, M4 and M5 — the individual numbers are symptoms.

**This module ships the seam and nothing else.** Its own acceptance is that **every existing caller
and every golden is byte-identical** afterwards, because the battle row is the identity. A module that
changes a number and the seam at once cannot tell which one moved the golden.

## Tech stack

`FusionRpg.Core` (parser + the profile type, no I/O), `data/tuning/mode-profiles.v1.json` published
through `gk-core/tools/tuning/publish.py`, hosts inject (`tunables-ssot.md` §7.2). No new dependency.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActorHub|ModeProfile|Tuning"
dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~ActorHub|Golden"
python gk-core/scripts/guard-actor-hub.py
.\scripts\verify-change.ps1 -Paths <changed files> -Session <session id>
python gk-core/tools/tuning/publish.py mode-profiles <dotted.key>=<value>
```

## Project structure

| What | Where |
|---|---|
| The profile type + parser (pure, no file read) | `src/FusionRpg.Core/Stats/Derived/ModeProfile.cs` |
| The tuning file | `data/tuning/mode-profiles.v1.json` |
| Host load + inject (server) | server composition root, beside the existing tuning loads |
| Host load + inject (injector) | `RpgHost` startup, beside the existing tuning loads |
| Tests | `tests/FusionRpg.Core.Tests/Stats/ModeProfileTests.cs` |

## The shape

```csharp
/// One mode's dials. A mode row is DATA: the modes themselves are a closed vocabulary the code owns
/// (RuntimeId), the dials inside a row are a balance surface a pass moves.
public sealed record ModeProfile(
    string ModeId,                                   // matches RuntimeId — lawn, battle, delve, siege, sim
    IReadOnlyDictionary<string, FamilyDials> Families);
```

Rules the shape has to keep:

1. **The mode id is the closed vocabulary**, so it is validated against `RuntimeId` and a row naming
   an unknown mode is a refusal, not a silent skip. A missing row falls back to `battle` — the
   identity — so a host that has not been taught about a new mode behaves exactly as today.
2. **One row in, at the top.** `ActorHubBootstrap.CreateDefault` takes an optional `ModeProfile`
   (default `null` = today's behaviour, exactly like the `starLoyalty` / `draughts` / `statusDerivedMods`
   arms already there). Bare `CreateDefault()` callers — hundreds of tests — are untouched. This is the
   established opt-in seam, not a new one.
3. **The profile is read by subsystems, never by a new composer.** `mode-profile` registers nothing of
   its own; it hands a row to the subsystems that later modules change.
4. **No mode-local number anywhere else.** After this module, a later module that wants a lawn number
   has exactly one place to put it, and a guard can say so.

## Tunables

`data/tuning/mode-profiles.v1.json`, owner `docs/architecture/lawn-tuning-profile/spec-mode-profile.md`,
published as `v{n+1}` through `gk-core/tools/tuning/publish.py` — never hand-edited
(`tunables-ssot.md`). The v1 file ships with:

| Key | v1 value | Meaning |
|---|---|---|
| `modes.battle.*` | the values in force today | The identity row. Byte-identical behaviour. |
| `modes.lawn.*` | **the same values as battle** | A named row that does nothing yet, so later modules change one number at a time. |

Every later module adds its own keys to the lawn row, each marked `UNMEASURED` until a sweep sizes it,
the posture `aptitudes.v{n}.json` and `action-timing.v1.json` already ship under.

## Code style

The dial's unit and its owner live next to the number, not in a separate doc:

```csharp
/// <summary>The mode's scale for one channel family. `null` means "this mode does not dial this
/// family" and the family composes exactly as it does today — never 0, which would silently zero a
/// contribution and read as a balance decision nobody made.</summary>
public sealed record FamilyDials(double? Scale, string? ReadFunction);
```

## Testing strategy

Contract and closed vocabulary only (`validation-ssot.md`):

- ✅ Every `modeId` in the file parses to a known `RuntimeId`; an unknown one throws with the id named.
- ✅ A `CreateDefault` with no profile composes bit-identically to `CreateDefault` with the battle row —
  the identity property, asserted, not assumed.
- ✅ A missing family, a missing mode, and an empty file each fall back to today's behaviour.
- ✅ The existing battle/delve/siege goldens are unchanged. **If a golden moves, this module is wrong** —
  that is the acceptance, not a thing to re-bless.
- ❌ Never assert how many dials a row has, or any dial's value. Those are readings.

## Boundaries

- **Always:** keep Core I/O-free (parser takes a string/stream, hosts read the file); default to today's
  behaviour on anything absent; publish `v{n+1}`.
- **Ask first:** nothing. The identity row makes this reversible by construction.
- **Never:** register a second composer or a mode-local fold (`guard-actor-hub.py` fails it, and the
  2026-09-12 `BattleStatComposer` incident is why); read the file from Core; give the lawn row a
  different *formula* — this module carries dials, and a new read function is `base-relative-read`'s
  job, behind its own module.

## Numeric types

A dial is a ratio, so `double` is correct and allowed (the 2026-09-15 ruling: precision is not
overflow). It multiplies a magnitude that is already `long` at its own boundary; the widen-before-
multiply rule applies at the multiplication site, in the consuming module, not here.

## ActorHub gate

**Contribute-through-Hub.** No new fold, no new composer, no new channel. The profile reaches
subsystems already registered by `ActorHubBootstrap.CreateDefault`, through the same optional-delegate
seam four existing contributions use.

## Success criteria

1. `data/tuning/mode-profiles.v1.json` exists, ships a battle row and an identical lawn row, and is
   loaded by both hosts.
2. `ActorHubBootstrap.CreateDefault` accepts an optional profile; bare callers are unchanged.
3. Core reads no file (the `tunables-ssot.md` §7.2 line holds).
4. **Every golden and every existing test is byte-identical.** This is the module's whole proof.
5. `guard-actor-hub.py` green.

## Open questions

None.
