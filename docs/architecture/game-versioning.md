# Game versioning (profile × loader)

PVZ Fusion keeps shipping new builds. FusionRpg supports a **matrix of game profiles × loader hosts**, not one forever DLL.

See also: [dual-host-roadmap.md](../../gk-fusion/docs/injector/dual-host-roadmap.md), [melonloader-assembly-csharp-39.md](../research/melonloader-assembly-csharp-39.md), catalog [`game-profiles.json`](../../gk-fusion/game-profiles.json).

## Model

```text
GameProfile (pvzrh-3.8.1 | pvzrh-3.9 | …)
    × LoaderHost (BepInEx | MelonLoader)
    → one compiled injector DLL + DropIntoGame subtree
```

- **Shared** hooks / Writer / Server / Core — one tree.
- **Version bridges** under `gk-fusion/src/FusionRpg.Injector/Bridges/{profile}/` absorb field width and arity (zombie HP Int32 vs Int64; `CreateZombie.SetZombie` + Harmony postfix). Shared hooks never assign `theHealth` / `theMaxHealth` or call `SetZombie` directly.
- **3.8.1 Melon** SetZombie is **5-arg** (`isIdle`); Bep 3.8.1 and Melon 3.9 are **4-arg**. One `#if FUSIONRPG_MELON` is allowed **only** inside the 3.8.1 spawn/Harmony bridge file.
- **No** runtime reflection adapters. **No** `#if` in every hook. **No** dual-load.

### Build topology — one host project per cell

A cell is the unit a build can produce, so **a host project *is* one cell** and the pack it compiles
against is that cell's pack. The cell table lives in `Directory.Build.props` (one row per host
project: cell, loader, env var); `Directory.Build.targets` holds the two consequences:

- A requested profile that disagrees with the cell is **reported, never obeyed** (`FUSIONRPG0001`).
  The bridge is chosen by the cell, so no env var and no `-p:` can point a 3.8.1 interop at the
  `pvzrh-3.9` bridge.
- A cell is **refused** when the pack it resolved is another cell's (`FUSIONRPG0002`), checked by
  `gk-fusion/scripts/guard-game-profile.py` against the fingerprints below — the same matcher
  `deploy-play.py` and `publish-player.ps1` already run. A pack is never silently assumed.

A cell with no pack root resolves nothing and the project takes its own skip path, printing
`NOT COMPILED — skipping …` at high importance. A skipped host is never counted as a compiled host,
which is what lets `FusionRpg.slnx` build on a machine that holds only some of the packs.

Measured defect this replaced (2026-09-25, TVB-F39): both MelonLoader hosts read the one
`FUSIONRPG_ML_GAMEDIR` and needed **different** packs, while the BepInEx and 3.8.1 MelonLoader hosts
read the one `FUSIONRPG_GAME_PROFILE` and were re-pointed at `Bridges/pvzrh-3.9`. No environment could
build the solution: a 3.9 pack gave the 3.8.1 host 2× CS1501, a 3.8.1 pack gave the 3.9 host 4×
CS0266, and `FUSIONRPG_GAME_PROFILE=pvzrh-3.9` gave the BepInEx host 4× CS0266.

## Support policy

| Rule | Meaning |
|---|---|
| Current + previous | At most two active profiles; older freeze on last known-good DLL |
| New game drop | New profile id + dump doc + bridge + Drop path — not silent retarget |
| Protocol | One Server/Core; events carry injector `game` id (`pvzrh-*`) |
| Refuse | Building/deploying a profile against the wrong pack fingerprint |

## Profiles (v1)

| Id | Packs | Loaders | Zombie HP | SetZombie |
|---|---|---|---|---|
| `pvzrh-3.8.1` | FULL MOD TOOL Bep, Blooms Melon | Bep + Melon | Int32 | Bep 4 / Blooms Melon 5 |
| `pvzrh-3.9` | `PVZ-Fusion-3.9_MelonLoader` | Melon first | Int64 | Melon 4 |

Fingerprints (GameAssembly / ACS sizes) live in [`game-profiles.json`](../../gk-fusion/game-profiles.json).

## Drop layout

```text
DropIntoGame/
  pvzrh-3.8.1/
    BepInEx/       FusionRpg.Injector.dll
    MelonLoader/   FusionRpg.Injector.MelonLoader.dll
  pvzrh-3.9/
    MelonLoader/   FusionRpg.Injector.MelonLoader.39.dll
```

Legacy flat `DropIntoGame\*.dll` and unscoped `DropIntoGame\BepInEx\` remain accepted for 3.8.1 Bep.

## Launcher

1. Detect loader (Bep vs Melon; refuse Both).
2. Resolve **game profile** from fingerprints. `launcher.json` does not exist in this repository —
   `GameProfile` is a field in a per-machine runtime settings file the
   player's own install writes, per `gk-fusion/src/FusionRpg.Launcher/Services/LauncherSettings.cs:40`).
3. Install only `DropIntoGame/{profile}/{loader}/`.
4. Clear error if payload missing for that cell of the matrix.

## Author process (new Fusion build)

1. `.\scripts\dump-game-profile.ps1` → `docs/research/game-types-{id}.md`
2. Diff HP widths / TakeDamage / SetZombie / namespace
3. Add `Bridges/{id}/` + host flavor (csproj `GameProfile`)
4. Nested Drop + fingerprint row in `game-profiles.json`
5. LIVE checklist with profile + loader header
6. Update this doc’s profile table

## Env

| Var | Role |
|---|---|
| `FUSIONRPG_GAME_DIR` | Bep pack root. Read by the BepInEx cell only while BepInEx has a single cell (today it does). |
| `FUSIONRPG_ML_GAMEDIR` | Melon pack root, **loader-wide**. Not read by any MelonLoader cell while that loader has two: a shared root cannot say which cell it holds. A caller that already knows the cell passes `-p:MlGameDir` instead. |
| `FUSIONRPG_GAME_DIR_PVZRH_3_8_1` | Bep pack root **for cell pvzrh-3.8.1** |
| `FUSIONRPG_ML_GAMEDIR_PVZRH_3_8_1` | Melon pack root **for cell pvzrh-3.8.1** (the Blooms 3.8.1 `Game Files`) |
| `FUSIONRPG_ML_GAMEDIR_PVZRH_3_9` | Melon pack root **for cell pvzrh-3.9** |
| `FUSIONRPG_GAME_PROFILE` | **Script layer only.** `deploy-play.py` / `publish-player.ps1` read it to choose *which* host project to build. MSBuild no longer reads it: a host project is one cell and is not re-targeted, and a request that disagrees is reported (`FUSIONRPG0001`). |

Per-cell names are the profile id upper-cased with `-` and `.` → `_`; the cell table that binds them
lives in `Directory.Build.props`, so adding a cell is one explicit row plus its host project
("Author process" step 3). A loader-wide root is honoured only while that loader has one cell, and a
table that forgot a row degrades to "that cell needs its own root" (a loud skip) rather than to a
wrong pack.

Resolution order for a cell's pack: explicit `-p:GameDir` / `-p:MlGameDir` → the cell's own env var →
the loader-wide root while assignable. Whatever resolves is fingerprinted, and a pack that is not the
cell's fails the build.

Deploy/publish must pass profile guards when fingerprints are known.
