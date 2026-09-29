# Spec: `system-commands`

**Status:** written 2026-09-19 (round-4 reconciliation) against `features/mega-merge`. Every `file:line`
below was opened in this session. Module §2.10 of the [trade-foundation map](../trade-foundation-map.md),
added by owner decision **Q10** in [../decisions-round-4.md](../decisions-round-4.md) (*"System-issued
world commands — one shared path, built in **trade-foundation**"*). **Round 5 X11 (2026-09-20):** the
system-only set is exactly **`release-warden`, `rift-window`, `rift-arrive`**; `depart` and `advance` are
the player's own orders, never system kinds.

**Consumers that asked for it:** `world-continuity` (`release-warden` from `world-warden`; its
`advance-carry` and `hibernation-clock` specs were also cited, but under X11 the legion departure and the
advance are the player's own `depart`/`advance` orders, not system kinds: [../../world-continuity/spec-world-warden.md](../../world-continuity/spec-world-warden.md)
§3, [../../world-continuity/spec-coarse-step.md](../../world-continuity/spec-coarse-step.md) §3,
[../../world-continuity/spec-world-state-vocabulary.md](../../world-continuity/spec-world-state-vocabulary.md)
§5) and `rift-trade` (`rift-window`, `rift-arrive`: [../rift-trade-map.md](../rift-trade-map.md) ask A7,
[../rift-trade/spec-rift-route.md](../rift-trade/spec-rift-route.md) §4,
[../rift-trade/spec-crossing-handoff.md](../rift-trade/spec-crossing-handoff.md)).

## Objective

Some world orders are not a commander's choice: a warden released because its mechanic was retired, a
cross-world route's window opening, goods arriving from another world. They must still be ordinary
`WorldCommand` rows — logged, replayed, resolved by the one resolver that owns their kind — or replay
would never reproduce them (the side-channel write warden-mortality rules out). This module is the
**one** path that files such an order: one closed set of system kinds, one admission rule that keeps them
out of every commander's hands, one Data filing function, and one deterministic command-id rule.

Success looks like: `world-continuity` and `rift-trade` register their kinds here and file through one
function; no player or AI can submit a system kind; a retried filing writes nothing; and a replay of a
turn that held system commands re-derives the same state.

## Scope and non-goals

**In scope:** the closed system-kind registry; the `Origin` of a command and its persistence; the
admission arm; the Data filing function; the command-id helper; the not-active-gate exemption.

**Not in scope:** any system kind's meaning or resolver (each owning program's: `WardenResolver` for
`release-warden`, `rift-trade` for its two kinds); which system kinds a hibernating world's coarse step
accepts (`world-continuity` `coarse-step`'s allow-list); the not-active gate itself
(`world-continuity` `world-state-vocabulary` §5).

## What already exists

### Built

| Fact | Evidence |
|---|---|
| One command shape for every commander; the kinds are a closed list | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:1-9`, `:124-130`, `:133-140` |
| Admission is one pure gate; it already refuses a retired kind for every path (submit, policy commit, `Reveal`'s re-admission) | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:17-34` |
| `Reveal` re-admits every stored command before resolving it | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:219-237` |
| Command ids are bounded at 64 characters | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:15`, `:36-39` |
| The command log: primary key `(world_id, turn, commander_id, command_id)`, a `reason` column | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:20-33`, `:57` |
| The one insert, shared by the player submit and the policy commit | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:133`, `:159-202`, `:285` |
| A replayed filing is detected by id | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:143` (`CommandExistsUnlocked`) |
| The commit reads the turn's commands once, inside its transaction | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:539` |
| One row back into a command, shared by both listers | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:818-835` (`ReadCommandRow`) |

### Wiring gap

None. No system-issued command exists in code today: `world-continuity` and `rift-trade` each specify
one, and each named a different owner for the path (`world-continuity/spec-world-state-vocabulary.md` §5
defines `FileSystemCommandUnlocked` there; `rift-trade-map.md` ask A7 asked `world-continuity` to name an
owner). Round 4 Q10 names this module.

### Real gap

No command records where it came from; admission cannot tell a system order from a forged one; nothing
generates a deterministic id for an order no one typed.

## Design

### 1. `Origin` — where a command came from

`WorldCommand.Origin` (`enum CommandOrigin { Commander, System }`, default `Commander`). It is **not** on
the wire request (`WorldCommandRequest`) and not in the payload JSON: nothing a client sends can set it.
It is persisted in a new column `rpg_world_commands.origin TEXT NOT NULL DEFAULT 'commander'` (added with
`EnsureColumn`, beside `reason` at `RpgStore.WorldTurns.cs:57`) and hydrated by `ReadCommandRow`, so the
commit and the report replay hand `Step` the same origin. Every existing row reads `commander`.

`Origin` is not hashed: it changes which commands are admitted, and the admitted commands are what the
state hash already reflects.

### 2. The closed system-kind registry

```csharp
// src/FusionRpg.Core/World/Turn/SystemCommandKinds.cs (new)
public static class SystemCommandKinds
{
    public static readonly IReadOnlyList<string> All;      // ordinal; shipped empty
    public static bool IsSystem(string kind);
}
```

A system kind is also a member of `WorldCommandKinds.All` (one kind list, `IsKnown` unchanged). Each
owning program adds its kinds to both lists **in the change that ships the kind's resolver**:
`release-warden` (`world-continuity` `world-warden`), `rift-window` and `rift-arrive` (`rift-trade`). **That
is the whole set (round 5 X11)**: `depart` and `advance` (`world-continuity` `advance-carry`) are the
player's own orders, admitted like any commander's, and are never registered here. The registry's members
are a closed vocabulary of three, pinned in a test with that reason (a fourth system kind is a reviewed
change to the round-5 register).

### 3. The admission arm

`WorldCommandAdmission.Admit` gains one check right after the known-kind check (before any shape check,
the position the retired-kind refusal already uses, `WorldCommandAdmission.cs:26-34`):

| Kind | Origin | Result |
|---|---|---|
| system kind | `Commander` | refused, `kind.system-only` |
| ordinary kind | `System` | refused, `kind.not-system` |
| system kind | `System` | continue to the kind's own shape rules |
| ordinary kind | `Commander` | unchanged |

Because `Reveal` re-admits every stored command (`TurnEngine.cs:219-237`), a system kind that reached the
log any other way is dropped at resolution too. The commander of a system command is still a faction of
the world — the faction on whose behalf the effect happens (`world-warden` uses the sector's owner) — so
`Reveal`'s commander ordering, fog audiences and per-commander `seq` work unchanged.

### 4. The filing function (Data)

```csharp
// src/FusionRpg.Data/Sqlite/RpgStore.SystemCommands.cs (new) — internal to FusionRpg.Data
internal bool FileSystemCommandUnlocked(
    SqliteConnection db, SqliteTransaction tx, string worldId, WorldCommand command, string reason);
```

1. Sets `Origin = System` on the command it files; the caller cannot file an ordinary kind through it.
2. Runs `WorldCommandAdmission.Admit` — **never bypassed**.
3. Returns `false` and writes nothing when `CommandExistsUnlocked` finds the id (a retry).
4. Otherwise inserts through the existing `InsertCommandUnlocked` into the world's open turn, with
   `reason` (bounded like every reason, `RpgStore.WorldTurns.cs:197-200`) and `origin = 'system'`.
5. Bypasses exactly one gate: `world-continuity`'s not-active gate on player submissions
   (`world-state-vocabulary` §5), so a hibernating world can receive a system order. It never bypasses
   admission, the kind list or the map-world check.

It runs in the **caller's** transaction. A filer that acts at commit time (`rift-window`) calls it before
the commit's command read (`RpgStore.WorldTurns.cs:539`), so the order resolves in the same turn. No
route or endpoint reaches it; `guard-dal.py` already keeps its SQL in Data.

System commands never count toward `WaitForAllCommitted`: the commit gate waits on factions, and a system
order is filed by the server, not awaited from anyone.

### 5. Deterministic ids

```csharp
// src/FusionRpg.Core/World/Turn/SystemCommandId.cs (new)
public static string For(string prefix, params string[] parts);
```

`prefix:` + `parts` joined by `:` when the result fits the 64-character bound; otherwise `prefix:` +
the first 16 hex digits of SHA-256 over the joined parts (the `rift:a:` shape `rift-trade` already
specified). Pure, culture-invariant. The same logical event always yields the same id, so a retried
filing is a no-op by the log's primary key. Prefixes are registered with their kinds (`release-warden`,
`rift:w`, `rift:a`, …) and must be unique (a test).

## Tunables

None.

## Numeric types

None.

## Acceptance (contract)

1. A player submission or an AI policy order of a system kind is refused with `kind.system-only`, on
   every path (submit, policy commit, `Reveal`).
2. `FileSystemCommandUnlocked` refuses an ordinary kind (`kind.not-system`) and writes nothing.
3. A system command filed through the function is admitted at `Reveal` and resolved by its kind's own
   resolver; the report replay of that turn re-derives the same state (origin is hydrated).
4. Filing the same logical event twice writes one row (deterministic id + `CommandExistsUnlocked`).
5. Every existing command row reads back with `Origin = Commander`; every existing world replays
   byte-identically (no hash, no kind, no admission outcome changes for a row with no system kind).
6. `SystemCommandId.For` output is ≤ 64 characters for every input and identical across cultures;
   registered prefixes are unique.
7. The function files into a non-active world (the one gate it bypasses) and still runs admission.
8. `SystemCommandKinds.All` ⊆ `WorldCommandKinds.All` (a join test); once all three owners have shipped,
   its membership is exactly `release-warden`, `rift-window`, `rift-arrive` (closed vocabulary, X11), and
   neither `depart` nor `advance` is ever a member (asserted).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Turn/SystemCommandAdmissionTests.cs` (new): items 1, 6, 8, with a
  fixture system kind registered in the test (the shipped registry is empty).
- `tests/FusionRpg.Data.Tests/World/SystemCommandFilingTests.cs` (new, in-memory store): items 2–5, 7.

```powershell
.\scripts\verify-change.ps1 -Paths @(
  'gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs',
  'gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs',
  'src/FusionRpg.Core/World/Turn/SystemCommandKinds.cs',
  'src/FusionRpg.Core/World/Turn/SystemCommandId.cs',
  'src/FusionRpg.Data/Sqlite/RpgStore.SystemCommands.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs',
  'tests/FusionRpg.Core.Tests/World/Turn/SystemCommandAdmissionTests.cs',
  'tests/FusionRpg.Data.Tests/World/SystemCommandFilingTests.cs') -Session <active-session-id>
python gk-core/scripts/guard-dal.py
```

Crosses Core and Data: the full suite runs once at module end (AGENTS.md "Verification boundary",
point 2).

## Structure

```
gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs            MODIFIED — Origin (not on the wire)
gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs   MODIFIED — the system arm
src/FusionRpg.Core/World/Turn/SystemCommandKinds.cs      (new, shipped empty)
src/FusionRpg.Core/World/Turn/SystemCommandId.cs         (new)
src/FusionRpg.Data/Sqlite/RpgStore.SystemCommands.cs     (new) — FileSystemCommandUnlocked
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs         MODIFIED — origin column, insert, hydrate
tests/…                                                  (new, above)
```

## Boundaries and hard edges

- **Always:** file system orders only through this function; admission always runs; one kind list.
- **Ask first:** a system kind resolved anywhere but its owning resolver; a second exempted gate.
- **Never:** put `Origin` on the wire or in the payload; write world state from Data instead of filing a
  command; a second filing path in any program.
- **Hard edge — command log shape.** One additive column with a default; no migration, no backup owed
  (`decisions.md:90` reserves those for key-widening). Existing rows are `commander`.

## Dependencies and interface

**Depends on:** nothing in this sub-program. `world-continuity`'s not-active gate is the one gate this
function bypasses; if this module lands first, there is nothing yet to bypass.

| Exposed | Consumer |
|---|---|
| `SystemCommandKinds`, `SystemCommandId.For` | `world-continuity` (`world-warden` — `release-warden`), `rift-trade` (`rift-route` — `rift-window`; `crossing-handoff` — `rift-arrive`) |
| `FileSystemCommandUnlocked` | the same, Data-side |
| `CommandOrigin` on hydrated commands | `world-continuity` `coarse-step` (its allow-list reads kind and origin) |

**Re-pointing owed by other programs (reported, not edited here):** `world-continuity/spec-world-state-vocabulary.md`
§5 and `spec-coarse-step.md` §3 define `FileSystemCommandUnlocked` as theirs; `rift-trade-map.md` A7 and
`spec-rift-route.md` §4 address the seam to `world-continuity`. Each should cite this module.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world commands (kinds, admission, log, hydration), world turn (Reveal), Data commit path.
[~] Session boundary: trade-network-idea-20260919 covers this file; the check was not re-run (docs only).
[x] Read this session: decisions-round-4 (Q10); world-continuity spec-world-warden §3, spec-coarse-step §3,
    spec-world-state-vocabulary §5; rift-trade-map A7; spec-rift-route §4; spec-crossing-handoff.
[x] decisions.md: additive schema rule (:90).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file.
[x] Verified against code: the kind list, admission's retired-kind precedent, Reveal's re-admission, the
    insert and its reason column, the commit's command read, ReadCommandRow.
[x] Surrounding sections read: SubmitWorldCommands' map-world refusal; the policy commit's admission.
[x] Constraints tested, not assumed: none claimed; replay identity is acceptance 5.
[x] No §2 invariant contradicted: determinism (logged commands, deterministic ids), SQL only in Data.
[x] Corrections propagated: the three foreign specs that name another owner are listed above.
[x] No population pinned; the system-kind registry is a closed vocabulary with its reason.
[x] No event-refreshed cache.
[x] Ordering: a retried filing is idempotent in any order.
[x] No actor magnitude.
[x] No SOLID fork: one kind list, one admission gate, one insert, one filing function.
[x] Registry row: "system kinds only through FileSystemCommandUnlocked" is enforced by admission
    (acceptance 1), not a scan.
```
