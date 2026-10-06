# ps1-ban — Wave 1 handoff for `mega-merge-program-manager-20260925-f78e`

Every item below is **measured on this machine at `ceb9df107`**, not inferred. Each is a path or a
behaviour the active session already owns, so none could be fixed from the ps1-ban program.

Reproduce any line with the command shown.

---

## 1. A dangling exemption entry — introduced by the ps1-ban delete, in your fenced registry

`gk-core/scripts/enforcement-registry.v1.json#local-operational-scripts` still lists a file this program deleted in `406b32f17`:

```
[local-operational-scripts] 1 of 20 missing
   - scripts/pi-web-windows-service.ps1
```

**It is the only truly dangling entry.** The other 20 "missing" paths in that table are
`tools/X/**` globs; expanding them shows every one matches at least one real directory, so they are
not defects. Verified by expanding globs rather than testing them literally:

```
literal paths that do not exist (TRULY dangling): 1
globs that DO match at least one directory:      20
globs that match NOTHING:                         0
```

**The fix is one line:** remove `"scripts/pi-web-windows-service.ps1"` from the
`local-operational-scripts` exemption. That entry was the owner ruling to delete the file — it
exists to serve a pi-agent workflow the owner no longer uses, and it calls
`Register-ScheduledTask` / `New-Service`, which need admin, so no agent and no CI could ever prove
a port of it. `bcu211-*` / `bcu212-proof` / `propagate-substrate-fix` / `_accept-sim-slice0` went the
same way and needed no exemption edits, because none of them was listed.

**Not fixed by this program on purpose:** `gk-core/scripts/enforcement-registry.v1.json` is in your fence.
Editing it would have been a boundary violation, so it is reported instead.

## 2. The guard that should have caught it does not check existence

`gk-core/scripts/verify-change.py:345-354` validates each `verificationExemptions` entry for **shape**
(`id`, `paths`, `reason` present) and rejects **catch-all roots** — but it never checks that a
listed path **exists**. So a deleted file keeps its exemption indefinitely, and
`guard-verification-boundaries.py` (which does check owner `paths` existence at its `:80`, `:84`,
`:92`) never looks at exemptions at all.

That is why this program's delete merged with `VERIFICATION BOUNDARY GUARD OK`, exit 0. **The green
was honest about the guards and silent about the exemption.** A one-line existence check in the
same loop would close it. This is the same failure shape as the vacuous globs in
`docs/architecture/ps1-ban-map.md` §`contract-scan-repair`: a check that stops being able to fail.

## 3. `verify-change` cannot dispatch a `.py` check — and now the message hides the cause

`gk-core/scripts/verify-change.py` runs a selected `script` check by PowerShell call operator, and a `.py`
path is not invokable that way. The refusal observed:

```
VERIFY-CHANGE REFUSED [plan]: BOUNDARY-MISSING: .claude/cmdc-agents/scripts/accept_lane.py
```

Read carefully, that message is **wrong about the cause.** The file has no *owner boundary*; the
actual blocker is that the dispatcher cannot launch a `.py` at all. A caller reading it will go add
a registry mapping, and the refusal will then repeat with the same text. The program hit this
twice: once as `BOUNDARY-MISSING` for a correctly-mapped-in-spirit path, and once as
`SESSION-NOT-ACTIVE`.

## 4. Correction to a claim this program made, now measured

The ps1-ban map and plan originally said a guard repointed at a `.py` would **silently** stop
running and the suite would read **green**. That was wrong, and it is corrected in `25f186ab9`.
Measured with a throwaway probe:

```
pwsh -NoProfile -File probe.py  ->  exit 64
   "Processing -File '...\probe.py' failed because the file does not have a
    '.ps1' extension. Specify a valid PowerShell script file name..."
python probe.py                 ->  exit 3,  "PYTHON ACTUALLY RAN"
```

`run-guards.ps1:191` is still `& $pwsh -NoProfile -File $script @guardArgs`, so a `.py` guard row
**fails loudly** — a red row with a named reason, not a pass. The gate is real (the guard cannot
execute) but it is **loud**. The genuinely silent failures are the vacuous globs, not the
dispatchers.

`run-guards.ps1:162` contains `foreach ($interpreter in @('dotnet','python','powershell'))`, which
looks like the interpreter dispatch this program needs. **It is not** — read its comment at
`:155-159`: it is a PATH-completeness **warning** so a red row is not mistaken for a verdict when
`PATH` lacks an interpreter. The dispatch is still hardcoded at `:191`.

## 5. What the ps1-ban program needs from you, and does not need

**Needs:** the Wave 0 dispatchers (map §1, ten sites) before any guard can shed its `.ps1`. The
heaviest is `run-guards.ps1:191`; `Directory.Build.targets:53` is the one with the worst failure
message (a missing script surfaces as `FUSIONRPG0002` "was pointed at a pack that is not this
cell's", blaming the game rather than the script).

**Does not need:** the ps1-ban program has no pending edit against anything you fence. Its own
unmerged work is `gk-core/scripts/checks/*` (a lane branch, `ps1ban/l3-checks`), which touches
`gk-core/scripts/verification-boundaries.v1.json` and `gk-core/tests/FusionRpg.Guard.Tests/GeneratorCheckCiParityTests.cs`
— the latter is in your fence, so that branch is **held, not merged**, and is described in
`tasks/ps1-ban-todo.md` Task 3.1-3.3.
