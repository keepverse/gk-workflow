# Resume 35 — TVB-F39: make `FusionRpg.slnx` buildable in one environment

## The defect (measured, not inferred)

`FusionRpg.slnx` includes three injector hosts. No single environment can compile all three, at head
`6b0397849`:

| Host | Profile source | Pack source | Fails with |
|---|---|---|---|
| `FusionRpg.Injector.BepInEx` | `GameProfile` ← `FUSIONRPG_GAME_PROFILE`, default `pvzrh-3.8.1` | `FUSIONRPG_GAME_DIR` | `FUSIONRPG_GAME_PROFILE=pvzrh-3.9` (what the 3.9 pack needs) → **4× CS0266** in `Bridges/pvzrh-3.9/ZombieCombatFields.cs:13-14` |
| `FusionRpg.Injector.MelonLoader` (legacy) | `GameProfile` ← `FUSIONRPG_GAME_PROFILE`, default `pvzrh-3.8.1` | `FUSIONRPG_ML_GAMEDIR` | pointed at the 3.9 pack → **2× CS1501** in `Bridges/pvzrh-3.8.1/CreateZombieSpawn.cs:11` (`SetZombie` 5-arg Blooms call vs 4-arg 3.9 interop) |
| `FusionRpg.Injector.MelonLoader.39` | **hardcodes** `pvzrh-3.9` | `FUSIONRPG_ML_GAMEDIR` | pointed at the 3.8.1 Blooms pack → **4× CS0266** in `Bridges/pvzrh-3.9/ZombieCombatFields.cs:13-14` |

Both Melon hosts read the **same** `FUSIONRPG_ML_GAMEDIR`, and they need **different** packs. That is
the core defect. `post_merge_check.py` builds the solution, so it can never reach GREEN — it reports
`build: non-interop project errors: FusionRpg.Injector.MelonLoader.csproj` and exits 1.

Evidence reproduced in this session (all four directions):
- legacy ML + 3.9 pack → 2× CS1501
- legacy ML + Blooms 3.8.1 pack → **Build succeeded**
- MelonLoader.39 + Blooms 3.8.1 pack → 4× CS0266
- BepInEx + 3.8.1 Bep pack + `FUSIONRPG_GAME_PROFILE=pvzrh-3.9` → 4× CS0266; profile unset → **Build succeeded**

All three packs exist on this machine. CI never builds the solution (it runs per-project
`dotnet test`), which is why the defect survived until the merged-head gate exercised the matrix.

## Task

Make the build topology satisfy the matrix in `docs/architecture/game-versioning.md` §Model —
`GameProfile × LoaderHost → one compiled DLL` — so that **one environment with the legal packs builds
Make the build topology satisfy the matrix in `docs/architecture/game-versioning.md` §Model —
`GameProfile × LoaderHost → one compiled DLL` — so that **one environment with the legal packs builds
the whole solution**, without breaking `deploy-play.py` or `publish_player.py`.

- **(A) Per-host pack variables** — e.g. `FUSIONRPG_ML_GAMEDIR` stays the 3.9/default pack for
  `MelonLoader.39`, and the legacy host reads a separate `FUSIONRPG_ML_GAMEDIR_38`
  (falling back to `FUSIONRPG_ML_GAMEDIR` only when the project's own profile matches).
- **(B) Resolve per project from `game-profiles.json`** — the catalog already carries
  `fingerprints.assemblyCSharpLengths` per profile (`3.8.1`: `[8316416, 7772672]`; `3.9`: `[8405504]`).
  A small shared props/targets file could pick the right pack per host by fingerprint.
- **(C) Per-host profile hardcoding** — the legacy host hardcodes `pvzrh-3.8.1` the way
  `MelonLoader.39` hardcodes `pvzrh-3.9`, so `FUSIONRPG_GAME_PROFILE` stops leaking across hosts.

Whatever you choose must also stop `FUSIONRPG_GAME_PROFILE` from silently re-pointing a host at a
bridge its interop cannot satisfy — that leak is the second half of the defect.

## Exact fence

1. `FusionRpg.slnx` (only if the fix changes what is in the solution)
2. `gk-fusion/src/FusionRpg.Injector.BepInEx/FusionRpg.Injector.BepInEx.csproj`
3. `gk-fusion/src/FusionRpg.Injector.MelonLoader/FusionRpg.Injector.MelonLoader.csproj`
4. `gk-fusion/src/FusionRpg.Injector.MelonLoader.39/FusionRpg.Injector.MelonLoader.39.csproj`
1. `FusionRpg.slnx` (only if the fix changes what is in the solution)
2. `gk-fusion/src/FusionRpg.Injector.BepInEx/FusionRpg.Injector.BepInEx.csproj`
3. `gk-fusion/src/FusionRpg.Injector.MelonLoader/FusionRpg.Injector.MelonLoader.csproj`
4. `gk-fusion/src/FusionRpg.Injector.MelonLoader.39/FusionRpg.Injector.MelonLoader.39.csproj`
5. `Directory.Build.props` (or a new `Directory.Build.targets` beside it — name it in the report)
6. `gk-fusion/scripts/deploy-play.py`
7. `scripts/publish_player.py`
8. `scripts/guard-injector-compile.py`
9. `tasks/sessions/resume-35-slnx-topology-20260925.json` (this record only)
10. `docs/architecture/game-versioning.md` (only if the env contract changes — say so)

## Hard rules

- **Never record a machine-local pack path** (`H:\Games\...`) in any tracked file. Paths come from env
  or `game-profiles.json` fingerprints only.
- **Never make the build silently skip a host.** A skipped host must print its reason at high
  importance (as `MelonLoader.39` does today) and must never be counted as a compiled host.
- Keep `deploy-play.py --loader-host BepInEx` and `--loader-host MelonLoader` working, and keep
  `publish-player.ps1`'s per-profile Drop layout exactly as it is.
- Commit nothing; leave the tree dirty for harvest. Never create a branch or push.

## Required verification — this GATES your claim

```powershell
# 1) The whole solution builds with the legal packs (this is the fix's own proof).
$env:FUSIONRPG_GAME_DIR  = '<BepInEx 3.8.1 source root, e.g. the FULL MOD TOOL pack>'
- **Never record a machine-local pack path** (`H:\Games\...`) in any tracked file. Paths come from env
  or `game-profiles.json` fingerprints only.
- **Never make the build silently skip a host.** A skipped host must print its reason at high
  importance (as `MelonLoader.39` does today) and must never be counted as a compiled host.
- Keep `deploy-play.py --loader-host BepInEx` and `--loader-host MelonLoader` working, and keep
  `publish_player.py`'s per-profile Drop layout exactly as it is.
- Commit nothing; leave the tree dirty for harvest. Never create a branch or push.
dotnet build gk-fusion/src/FusionRpg.Injector.MelonLoader/FusionRpg.Injector.MelonLoader.csproj -c Debug --nologo
dotnet build gk-fusion/src/FusionRpg.Injector.MelonLoader.39/FusionRpg.Injector.MelonLoader.39.csproj -c Debug --nologo

# 3) The compile guard still passes.
.\scripts\guard-injector-compile.ps1
```

Report the exact command text and the numbers/lines each printed. If you cannot make the whole
solution build in one environment, **say so and stop** — do not claim a partial build as the fix.

## End with

```
<<<REPORT {"status":"done|blocked","summary":"...","shape_chosen":"A|B|C","changed_files":[...],"commits":[],"verification":[{"command":"...","result":"..."}],"not_proved":["..."]} REPORT>>>
```
# 3) The compile guard still passes.
.\scripts\guard-injector-compile.py
```
