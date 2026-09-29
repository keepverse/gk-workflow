# spec — `file-move-tool`

**Module 16 of `solid-remediation`.** Register entries: none. Depends on `green-baseline`.

Sequenced late, where its cost lands on nothing else — no module depends on it.

## Objective

A tool that moves a file **and rewires it**: namespace, `using` directives across callers, and the
project file when the move crosses assemblies. Then apply it to the four genuinely misfiled files.

## The honest framing

The ideal doc justified this module as free work during the merge window — *"that window is otherwise
dead time, and the tool is the one piece of work that needs no exclusivity."* **The merge is done and
there is no window**, so the tool costs real time now.

The measured input is small:

| Measure | Value |
|---|---|
| C# files scanned | 1,313 |
| namespace ≠ folder | 102 |
| …`FusionRpg.Data` flat-root **convention** | 89 |
| …injector host shims | 9 |
| **Genuinely misfiled** | **4** |

```
src/FusionRpg.Core/Actions/BasicAttack.cs          declares FusionRpg.Core.Battle
src/FusionRpg.Core/Actions/TimelineDispatch.cs     declares FusionRpg.Core.Battle
src/FusionRpg.Core/Actions/TurnOrderRecord.cs      declares FusionRpg.Core.Battle.Timeline
gk-core/src/FusionRpg.Server/Achievements/AchievementEvaluator.cs   declares FusionRpg.Server
```

The first three are `partial class BattleEngine` bodies living under `Actions/`. The fourth arrived with
the `achievement-title` merge.

**Every one already declares the namespace it should**, so moving them is `git mv` plus nothing — no call
site changes at all. A tool is not required to do this work.

**Owner ruling 2026-09-17, after seeing that measurement: keep it, scoped to earn its keep.** So the
deliverable is a tool worth reaching for next time, not a wrapper around four renames.

## Scope — what makes it worth building

| Capability | Why |
|---|---|
| Move a file and set its namespace to match the destination folder | The base case |
| Rewire `using` directives across **every caller** | The part `git mv` cannot do, and the reason a manual move is risky at scale |
| Update the project file when the move **crosses assemblies** | Where a manual move silently breaks the build |
| Refuse a move that would create a cycle between assemblies | A move that compiles can still be architecturally wrong |
| Dry-run that prints the full change set | A move tool nobody can preview will not be trusted twice |

The four known files exercise **only the first**. Build the rest against a synthetic fixture, or the tool
will be untested exactly where it is dangerous.

## Boundaries

- **Always:** dry-run first; the tool prints what it will change before changing it
- **Ask first:** moving anything beyond the four measured files. The 89 `FusionRpg.Data` files are a
  **convention**, not a defect — "fixing" them would be a large diff with no behaviour change and no
  defect closed
- **Never:** move a file whose namespace is already correct for its current folder just to satisfy a
  pattern

## Tests to write

- Moving within an assembly rewires callers' `using` directives
- Moving across assemblies updates the project file
- A move that would create an assembly cycle is refused, naming the cycle
- Dry-run changes nothing
- The four real files move with **zero** call-site changes — the measurement, asserted

Assert the tool's **contract**. Never assert how many files in the repo are misfiled: that is a reading
that changes whenever code ships.

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths gk-core/tools/FileMove/** <tests> -Session solid-remediation-<date>
```

- [ ] Tool moves and rewires, with dry-run
- [ ] Assembly-cycle refusal tested against a synthetic fixture
- [ ] The four files moved; build green; no call-site diff
- [ ] The 89 convention files untouched

## Success criteria

The next misfiled file is moved by a tool instead of by hand — and the four known ones are in the right
folders, which is a two-minute outcome that this module deliberately spends longer to make repeatable.
