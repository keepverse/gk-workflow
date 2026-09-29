# Legal injector/interop preflight — 2026-09-25

## Result

The owner supplied the machine-local legal source folders. A first build attempt intentionally pointed
`FUSIONRPG_GAME_DIR` at the MelonLoader-only source; it failed because that source has no
`BepInEx/core` or `BepInEx/interop` tree. This was an environment-selection mistake, not a product
failure.

After selecting the owner-provided BepInEx source and MelonLoader source separately, and selecting the
matching `pvzrh-3.9` bridge profile for the 3.9 MelonLoader source:

```text
FUSIONRPG_GAME_DIR = <owner-supplied BepInEx source>
FUSIONRPG_ML_GAMEDIR = <owner-supplied MelonLoader source>
FUSIONRPG_GAME_PROFILE = pvzrh-3.9
dotnet build gk-fusion/src/FusionRpg.Injector.BepInEx/FusionRpg.Injector.BepInEx.csproj -c Debug --nologo
# Build succeeded; 0 errors, 23 existing warnings; exit 0

dotnet build gk-fusion/src/FusionRpg.Injector.MelonLoader/FusionRpg.Injector.MelonLoader.csproj -c Debug --nologo
# Build succeeded; 0 errors, 23 existing warnings; exit 0
```

The first MelonLoader attempt used the default `pvzrh-3.8.1` profile against the 3.9 source and failed
at the known profile/pack mismatch (`SetZombie` overload). The matching `pvzrh-3.9` profile succeeds;
this is a required environment selection, not a new product defect. The required BepInEx core/interop
files and MelonLoader net6/Il2CppAssemblies files were checked before the builds. External logs are
retained outside the repository:

```text
bepLogSha256=609018CFBE49B41D33F8A8576530AB38D525E5906E7F9E4DD6A393829105D8E4
melonLogSha256=EEA6884A04FBFF459724420863F4A6942AAFEF9914BEC28CE2D9B32713637EF1
```

## Boundary

No game binary, loader DLL, interop DLL, machine path, or generated data was committed. The final
`post_merge_check.py` invocation must receive both environment variables at runtime and must still
run on a clean, stable integration head. This preflight is not a substitute for that merged-head gate
or for a live game proof.

<<<REPORT {"status":"done","summary":"Resolved the legal interop preflight: the MelonLoader-only path cannot build the BepInEx host, but the owner-provided separate BepInEx source and MelonLoader source satisfy the required references; the BepInEx build succeeds with 0 errors and 23 existing warnings. Machine-local paths and binaries remain untracked.","changed_files":["tasks/reports/legal-interop-preflight-20260925.md"],"verification":["required BepInEx core/interop files present in owner-supplied source","required MelonLoader net6/Il2CppAssemblies files present in owner-supplied source","BepInEx build exit 0, 0 errors, 23 warnings","MelonLoader build with FUSIONRPG_GAME_PROFILE=pvzrh-3.9 exit 0, 0 errors, 23 warnings","bep external log SHA-256 609018CFBE49B41D33F8A8576530AB38D525E5906E7F9E4DD6A393829105D8E4","melon external log SHA-256 EEA6884A04FBFF459724420863F4A6942AAFEF9914BEC28CE2D9B32713637EF1"],"open_issues":["current-head post-merge gate must be rerun with all three environment variables, including FUSIONRPG_GAME_PROFILE=pvzrh-3.9","live game proof remains separate"],"next_steps":["run the final gate after active lanes stabilize","use the owner-provided test slot for a scoped live proof if the final gate is green"]} REPORT>>>
