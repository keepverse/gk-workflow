# Spec: notify-vocabulary

**Status: Draft — Phase 1 (Specify), awaiting owner review.** Module `notify-vocabulary` of the
[notification-ssot map](../notification-ssot-map.md), wave 1, no dependencies. Every other module in
the program reads what this one declares.

**Rulings it carries:** R-N2 (open category registry, rail default, 100 per category, the word is
*category*), R-N4 (making a category Critical is a reviewed change), R-N5 (the dedup key is a field
from day one), R17 (a wire `playerId` is the save; map §Identity).

**Strengthen pass 2026-09-18:** adds the closed `NotifyDelivery` enum and the `rev` field the
catch-up cursor needs (map §Strengthen pass S2, S3), and sequences the catalog versions across the
three modules that publish them (S13).

---

## Objective

Give the program one place for each vocabulary, so the server, the store and the web cannot drift
apart:

| Vocabulary | Open or closed | Where it lives |
|---|---|---|
| **Categories** — what a notification is about | **Open** (R-N2). A feature adds rows for the categories it owns | `gk-core/data/tuning/notification-catalog.v1.json` `categories[]` (new) |
| **Promotions** — which categories default to the toast, and which may be Critical | **Closed, reviewed** (R-N2, R-N4) | Same file, `promotions` block (new) |
| **Channel** — where it is delivered | Closed: `toast · rail · off` | `NotifyChannel` (`gk-web/web/fusion-rpg-web/src/shell/notify/catalog.ts`). The world's old `stages/world/notify/categories.ts` that first held it is GONE as of NS5.11. It is web-only, because the server never routes by channel (the player's setting is web-side, `spec-world-notify.md` §6) |
| **Severity** | Closed: `routine · important · critical` | C# `NotifySeverity` + TS union (new) |
| **Argument kind** — the typed slots a message may carry | Closed: `magnitude · count · worldTurn · ref · domainToken` | C# `NotifyArgKind` + TS union (new) |
| **Reference kind** — what a `ref` argument points at | Closed: `sector · lane · faction · legion · structure · cache` | C# `NotifyRefKind` + TS union (new) |
| **Delivery** — may this batch toast? | Closed: `live · catchUp` | C# `NotifyDelivery` + TS union (new) |
| **Numbers** — retention and repeat window | Tunable | `gk-core/data/tuning/notification.v1.json` (new) |
| **Wire shapes** | Contract | `gk-core/src/FusionRpg.Contracts/NotificationDtos.cs` (new) |

**Why the category list is open and the rest is closed.** R-N2 makes categories open so each feature
can register its own, and it keeps that safe with the rule already in the world's old `categories.ts:19-22` (GONE as of NS5.11; it is the catalogue's own `promotions` block now, `gk-core/data/tuning/notification-catalog.v3.json:100`): *"Every
category not in this list defaults to the rail and has to earn a promotion."* In the catalog, **no
category row can name a channel or a severity**. A row always lands on the rail at `routine` or
`important`. Only an edit to `promotions` can make a category a toast default or let it go Critical,
and that edit is a visible diff in one block. An open list whose rows could promote themselves would
be the spam surface R-N2 warns about.

**Why the word is "category".** R-N2 settles it: `NotifyChannel` already means the delivery surface
(`categories.ts:17` in the world's old copy, GONE as of NS5.11; the catalogue owns `NotifyChannel` now), and the repo also has "channels" for derived stats. This module never uses
"channel" for a topic.

## Design

### 1. The catalog file (runtime catalog, tunables-ssot §1)

It holds identity and player English, and no numbers. That is the "runtime catalog" class, a sibling
file to the numbers per tunables-ssot §2, and the GG-62 home for player words.

**Rows arrive with the module that can render them.** v1, written by this module, ships
`categories: []` and empty promotions. That is a valid catalog, because the parser pins no count.
The versions are sequenced, one publisher each, so no two modules publish the same `vN`:

| Version | Publisher | Adds |
|---|---|---|
| v1 | `notify-vocabulary` (wave 1) | The empty catalog |
| v2 | `world-notify-source` (wave 5) | The eight `world-notify` categories (`categories.ts:7-15` in the world's old copy, GONE as of NS5.11), `territory.lost` and `promotions.toast` |
| v3 | `cache-notify-source` (wave 6) | `cache.created` and `cache.decayed` |

If the wave order ever changes, whichever module lands later reads the current version and publishes
the next one. Neither hard-codes the number it expects to find. Every bump updates the two load sites
in the same change: the Server's load line (§4) and the web import in `shell/notify/catalog.ts`. So `notify-format`'s coverage guard is green at every wave, since no row exists before
its translator does, and the world's `categories.ts` (GONE as of NS5.11 — the catalogue replaced it:
`gk-core/data/tuning/notification-catalog.v3.json`) served the world rail until then. The example below shows
the shape once those later versions have landed:

```jsonc
{
  "schemaVersion": 1,
  "version": 1,
  "_meta": { "owner": "docs/architecture/notification-ssot/spec-notify-vocabulary.md" },
  "categories": [
    {
      "id": "loam.shortfall",
      "domain": "world",
      "displayName": "A part of your territory cannot pay its keep",
      "messageKeys": ["world.turn-entry"]
    },
    { "id": "territory.lost", "domain": "world", "displayName": "Ground you held is gone", "messageKeys": ["world.turn-entry"] },
    { "id": "cache.created", "domain": "corpse-cache", "displayName": "Fallen gear left on the field", "messageKeys": ["cache.created"] },
    { "id": "cache.decayed", "domain": "corpse-cache", "displayName": "Fallen gear rotting away", "messageKeys": ["cache.decayed"] }
    // … the other seven world rows, same shape
  ],
  "promotions": {
    "toast": ["loam.shortfall", "loam.release", "legion.runway"],
    "critical": []
  }
}
```

- `promotions.toast` becomes `TOAST_TIER` moved here as it is (the world's old `categories.ts:23`, GONE as of NS5.11), in
  `world-notify-source`'s v2.
- `promotions.critical` ships **empty**, following the hard-block list precedent
  (`world-stage/spec-world-notify.md` §5: it "defaults to empty and every addition is argued"). Each
  addition is argued in the spec of the source that wants it.
- `messageKeys` closes the set of messages a category can carry. The publisher refuses any other key
  (`notify-service`), and the web guard (`notify-format`) proves every listed key renders.
- `domain` names the owning domain translator (`notify-format`'s registry key).
- The catalog is hand-authored, not seedsmith output. Version bumps follow T4 (`v{n+1}`, the old file
  kept). `gk-core/tools/tuning/publish.py` gains `notification-catalog` support in the same change that first
  bumps it. The v1 file is written once by this module.

### 2. The numbers file (tunable, tunables-ssot §2)

```jsonc
{
  "schemaVersion": 1,
  "version": 1,
  "_meta": {
    "owner": "docs/architecture/notification-ssot/spec-notify-vocabulary.md",
    "note": "Working values, not a validated balance decision."
  },
  "retainPerCategory": 100,
  "repeatWindowWorldTurns": 3
}
```

| Key | Unit | Meaning | Why tunable |
|---|---|---|---|
| `retainPerCategory` | rows, per (player, category) | R-N2's retention tail. Beyond it the oldest row goes, whatever its state | R-N2: "It is a tunable, not a `const`… plainly yes for a retention depth" |
| `repeatWindowWorldTurns` | world turns | A non-Critical draft is suppressed when the same (player, category, subject) was stored within this many world turns. Turn-counted only, per ideal finding M6: every source in this program runs on the world clock. A wall-clock source must bring its **own** separately named key; the two clock domains never share a number | A per-turn warning (legion runway every turn) is exactly what a balance pass tunes by feel (ideal §Tunables) |

Missing keys reject the load by name (T5). There are no built-in defaults.

**Structural, not tunable, with the reason in a comment:** the toast visible cap
(`shell/Toasts.tsx:13`, `VISIBLE_CAP = 3`, a band-4 layout limit), the 5000 ms toast duration
(`shell/toastStack.ts:29`, a UI polish constant per ideal finding H3), and the REST page size
(`notify-service`).

### 3. Closed enums and wire shapes (Contracts)

```csharp
// gk-core/src/FusionRpg.Contracts/NotificationDtos.cs (new)
namespace FusionRpg.Contracts;

/// <summary>Closed. Ordered: a larger value outranks a smaller one in the toast selection
/// (notify-client §Design 4). Raising a category's ceiling is an edit to the catalog's
/// promotions block, never a field a source sets for itself (R-N4).</summary>
public enum NotifySeverity { Routine = 0, Important = 1, Critical = 2 }

/// <summary>Closed. The typed slots a message may carry. `DomainToken` is opaque to the shared
/// primitives. Only the translator of the domain that owns the category may read it.</summary>
public enum NotifyArgKind { Magnitude, Count, WorldTurn, Ref, DomainToken }

/// <summary>Closed. Whether a batch may toast. Live = it just happened (the newest turn of a commit).
/// CatchUp = it is late (a boot run, a lagging turn); the client never toasts it
/// (notify-service §2).</summary>
public enum NotifyDelivery { Live, CatchUp }

public enum NotifyRefKind { Sector, Lane, Faction, Legion, Structure, Cache }

public sealed class NotifyArgDto
{
    [JsonPropertyName("name")] public string Name { get; set; } = "";
    [JsonPropertyName("kind")] public NotifyArgKind Kind { get; set; }
    /// <summary>Kind-shaped JSON: Magnitude = {unit,value,op?,channel?} (the web's `Magnitude`,
    /// contract/types.ts:94); Count = long; WorldTurn = int; Ref = {refKind,id}; DomainToken = string.</summary>
    [JsonPropertyName("value")] public JsonElement Value { get; set; }
}

public sealed class NotificationDto
{
    [JsonPropertyName("seq")] public long Seq { get; set; }                 // store row id; the history `before` cursor
    [JsonPropertyName("rev")] public long Rev { get; set; }                 // per-save change counter; the catch-up `since` cursor
    [JsonPropertyName("dedupKey")] public string DedupKey { get; set; } = ""; // R-N5 — stable across push and GET
    [JsonPropertyName("category")] public string Category { get; set; } = "";
    [JsonPropertyName("severity")] public NotifySeverity Severity { get; set; }
    [JsonPropertyName("sourceId")] public string SourceId { get; set; } = "";
    [JsonPropertyName("messageKey")] public string MessageKey { get; set; } = "";
    [JsonPropertyName("args")] public List<NotifyArgDto> Args { get; set; } = new();
    [JsonPropertyName("subjectKey")] public string? SubjectKey { get; set; }
    [JsonPropertyName("worldId")] public string? WorldId { get; set; }
    [JsonPropertyName("worldTurn")] public int? WorldTurn { get; set; }
    [JsonPropertyName("state")] public string State { get; set; } = "unread"; // unread | read | dismissed
    [JsonPropertyName("createdUtc")] public string CreatedUtc { get; set; } = "";
}

public sealed class NotificationBatchDto
{
    [JsonPropertyName("playerId")] public long PlayerId { get; set; }       // the SaveId (R17); wire name kept
    [JsonPropertyName("delivery")] public NotifyDelivery Delivery { get; set; }
    [JsonPropertyName("items")] public List<NotificationDto> Items { get; set; } = new();
}

public sealed class NotificationStateChangedDto
{
    [JsonPropertyName("playerId")] public long PlayerId { get; set; }       // the SaveId (R17)
    [JsonPropertyName("state")] public string State { get; set; } = "";     // read | dismissed
    [JsonPropertyName("changes")] public List<NotificationStateChangeDto> Changes { get; set; } = new();
}

public sealed class NotificationStateChangeDto
{
    [JsonPropertyName("seq")] public long Seq { get; set; }
    [JsonPropertyName("rev")] public long Rev { get; set; }
}

public static class NotificationEvents
{
    public const string Batch = "NotificationBatch";          // R-N6: the only content event
    public const string StateChanged = "NotificationStateChanged";
}
```

Enums serialize as camelCase strings, the way the existing DTOs are written. `WorldTurn` is `int`
because world turns are `int` everywhere they are held (`TurnReport.Add`'s callers,
`WorldHeaderRow.CurrentTurn`, `RpgStore.World.cs:737-740`). `Seq` and `Rev` are `long`, following the
ideal's finding H4 and `CLAUDE.md` numeric rule 1.

### 4. Loading (T7.2 / T8)

- **Core** (`gk-core/src/FusionRpg.Core/Notify/NotificationCatalog.cs`, new) is a pure parser over strings.
  It builds a `NotificationCatalog` with `TryGet(categoryId)`, `CeilingOf(categoryId)`
  (`Critical` if the id is in `promotions.critical`, otherwise `Important`), plus
  `NotificationTuning`. The default channel is a web concern (`catalog.ts`, `defaultChannelOf`). The parser rejects: a duplicate id; a promotion naming an unregistered id;
  a `critical` id missing from `toast`; an empty `messageKeys`; a row carrying a `channel` or
  `severity` field.
- **Server** loads both files at the composition root, beside the other tuning loads
  (`gk-core/src/FusionRpg.Server/Program.cs:30`), and registers them as singletons. The csproj already copies
  every `gk-core/data/tuning/**/*.json` next to the exe (`gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj:30`), so
  a new file needs no build change.
- **Web** imports the catalog JSON directly, the same way `lib/bus/actorSurface.ts:3-4` already
  imports catalog files, through `shell/notify/catalog.ts` (new). There is no REST endpoint for it.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Notify"
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~NotificationCatalog"
cd web\fusion-rpg-web; npm test -- shell/notify/catalog; npm run build
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
python scripts\audit-magic-numbers.py --domain notification
```

New paths get a row in `gk-core/scripts/verification-boundaries.v1.json` in the same change. An unmapped path
is a verification-boundary defect (AGENTS.md "Verification boundary").

## Project structure

```
gk-core/data/tuning/notification-catalog.v1.json              → categories (open) + promotions (reviewed)
gk-core/data/tuning/notification.v1.json                      → retainPerCategory, repeatWindowWorldTurns
gk-core/src/FusionRpg.Contracts/NotificationDtos.cs           → enums + DTOs + event names
gk-core/src/FusionRpg.Core/Notify/NotificationCatalog.cs      → pure parser + queries
gk-core/src/FusionRpg.Core/Notify/NotificationTuning.cs       → pure parser
gk-core/src/FusionRpg.Server/Program.cs                       → host load (two lines beside :30-77)
gk-web/web/fusion-rpg-web/src/shell/notify/catalog.ts        → typed view of the JSON; NotifyCategoryId = string;
                                                        TS mirror of the wire DTOs (NotificationItem, NotifyArg)
gk-core/tests/FusionRpg.Core.Notify.Tests/Notify/NotificationCatalogTests.cs
gk-core/tests/FusionRpg.Guard.Tests/NotificationCatalogContractTests.cs   → reads the real files
gk-web/web/fusion-rpg-web/src/shell/notify/catalog.test.ts
```

## Code style

```ts
// shell/notify/catalog.ts — a category id is an open string. Promotion is read from ONE block.
import catalogJson from "../../../../../data/tuning/notification-catalog.v1.json";

export type NotifyCategoryId = string;
export type NotifyChannel = "toast" | "rail" | "off";
export type NotifySeverity = "routine" | "important" | "critical";

const toastTier = new Set<string>(catalogJson.promotions.toast);

/** Registered but unpromoted means the rail. A category can never grant itself the toast (R-N2). */
export function defaultChannelOf(id: NotifyCategoryId): NotifyChannel {
  return toastTier.has(id) ? "toast" : "rail";
}
```

## Testing strategy

Every assertion is on the contract or a closed enum. None pins how many categories exist, because
that list is **open** and its size is a reading (validation-ssot, DESIGN-GATE §3 rule 7).

1. **Closed enums are pinned, with the reason.** `NotifySeverity` has 3 members, `NotifyArgKind` 5,
   `NotifyRefKind` 6, `NotifyDelivery` 2, and the web-only `NotifyChannel` 3. These are declarations the code owns, and a new member is a
   reviewed change that also needs a `notify-format` primitive. The C# and TS unions hold identical
   members wherever both sides hold the enum; the Guard test reads both files.
2. **No self-promotion.** Every catalog row has no `channel` or `severity` field. Every id in
   `promotions.*` is a registered category. `critical ⊆ toast`.
3. **Every category is renderable.** Every row has a non-empty `domain` and `messageKeys`. The
   rendering half of this proof belongs to `notify-format`.
4. **Load rejection names the key.** A tuning file missing `retainPerCategory` or
   `repeatWindowWorldTurns` throws with that key's name (T5).
5. **An empty catalog is valid.** v1's `categories: []` parses, and every query answers "unknown"
   for any id. (The equivalence of `promotions.toast` with `TOAST_TIER` is `world-notify-source`'s
   test, because v2 is where it becomes true.)

## Boundaries

- **Always:** default a new category to the rail; put promotions only in `promotions`; carry the
  retention tail's exemption comment where `retainPerCategory` is read (`notify-store`); publish a
  changed number as `v{n+1}`.
- **Ask first:** any edit to `promotions.toast` or `promotions.critical` (R-N2, R-N4); a new member
  of any closed enum.
- **Never:** a `channel` or `severity` field on a category row; the word "channel" for a topic; a
  category-count assertion; a built-in default for a missing tunable.

## Success criteria

1. Both JSON files exist; Core parses them and the Server injects them; the web types the catalog.
2. The closed enums match across C# and TS wherever both sides hold them, proven by the Guard
   test.
3. No category can reach toast or Critical except through `promotions`, proven by test 2.
4. `retainPerCategory` and `repeatWindowWorldTurns` are the only numbers, and each has a unit.
5. `verify-change.ps1` green on the changed paths; `audit-magic-numbers.py` has no new M1/M2.

## Seedsmith / generator

None. The catalog is an authored runtime catalog (tunables-ssot §1), and the numbers file is
authored and published through `gk-core/tools/tuning/publish.py`. No `_meta.model` provenance, no generator.

## Open questions

None. R-N2 and R-N4 decide the open/closed split. The empty Critical list follows the precedent above.
