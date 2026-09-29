# Spec: notify-format

**Status: Draft — Phase 1 (Specify), awaiting owner review.** Module `notify-format` of the
[notification-ssot map](../notification-ssot-map.md), wave 2, depends on `notify-vocabulary`.
It is built **before** any domain translator (R-N3).

---

## Objective

R-N3: *"Each domain owns its own event→text translation, mirroring `world-playback`… and they compose
from one shared set of formatting and i18n pieces… the shared formatting layer has to be defined
**up front**."* This module is that shared layer, on the web. It holds three things and no domain
vocabulary:

1. **Argument primitives.** They turn each closed `NotifyArgKind` (`notify-vocabulary` §3) into player
   text through the formatters the web already has. A magnitude goes through `formatMagnitude`
   (`gk-web/web/fusion-rpg-web/src/i18n/magnitude.ts:15`), the one number formatter, which is locale-aware
   and unit-aware. A reference goes through a **resolver the domain supplies**, and a reference with
   no name renders as the repo's `Pending` placeholder (`contract/pending.ts`), never as the raw id
   (GG-23, GG-62).
2. **The translator contract.** A `NotifyTranslator` maps `(messageKey, args)` to
   `{ title, body, target? }`, where `target` is a typed reference the mount may turn into a one-click
   action (`spec-world-notify.md` §7's click budget).
3. **The translator registry.** Keyed by the catalog's `domain`, it has one entry per owning domain.
   Its guard proves every `(category, messageKey)` pair in the catalog renders through a registered
   translator, never through the fallback.

**Why the web, not the server.** The existing translation (`stages/world/playbackTable.ts:247`),
the number formatter and the i18n catalogs (`src/i18n/locales`) are all on the web. The server has no
i18n. Moving text to the server would mean a second magnitude formatter in C#, which is the drift R-N3
exists to prevent (map §Where this map departs).

## Design

### 1. Contract

```ts
// shell/notify/format/translator.ts (new)
import type { NotifyArg, NotificationItem } from "../catalog";

export type NotifyTarget = { refKind: NotifyRefKind; id: string };

export type NotifyText = {
  /** Authored copy. Never an id, never an engine token (GG-23 / GG-62). */
  title: string;
  body: string;
  /** Optional. The mount decides whether a target becomes an action (notify-client §Design 6). */
  target?: NotifyTarget;
};

/** One per domain. Owns that domain's message keys and is the ONLY reader of its domainToken args. */
export type NotifyTranslator = {
  domain: string;
  translate(item: NotificationItem, fmt: NotifyFormatKit): NotifyText | null; // null = unknown key → designed fallback
  /** Representative items per message key, for the coverage guard (§Testing 3). Test-facing only. */
  samples(messageKey: string): readonly NotificationItem[];
};
```

### 2. The shared kit (`NotifyFormatKit`)

| Primitive | Arg kind | Built on |
|---|---|---|
| `fmt.magnitude(arg)` | `magnitude` | `formatMagnitude` (`i18n/magnitude.ts:15`) with the active locale |
| `fmt.count(arg)` | `count` | `formatMagnitude({ unit: "count", value })`, as `playbackTable.ts:31` already builds a count |
| `fmt.turn(arg)` / `fmt.turnsFrom(arg, now)` | `worldTurn` | One wording for "turn N" and for "in N turns", shared by every domain |
| `fmt.ref(arg, resolver)` | `ref` | A `NotifyRefResolver` the **domain** passes in, for example the world's `sectorLabel` (`stages/world/labels.ts:17`). An unresolvable reference renders the `Pending` placeholder |
| `fmt.categoryName(id)` | — | The catalog `displayName` (GG-62's authored row) |

There is **no** primitive for `domainToken`. That kind is opaque to shared code by definition
(`notify-vocabulary` §3).

### 3. The fallback is designed, never raw

When a translator returns `null`, or no translator is registered for a domain, the item renders as
`fmt.categoryName(category)` with a neutral body. In development it is also marked visibly and logged
once. This is `describePlaybackEntry`'s own discipline (`playbackTable.ts:247-270`: "never the raw
token either way"). The guard below makes the fallback unreachable for any catalog-declared key.

### 4. Registry

`shell/notify/format/registry.ts` exports `registerTranslator(t)` and `translatorFor(domain)`.
Domain translators live **with their domain** (`stages/world/notify/worldTranslator.ts` in
`world-notify-source`) and register from one index file, `shell/notify/format/translators.ts`, so the
guard can see every one. That index file is the only place shared code imports a domain module: it
is the list, and it holds no logic.

## Commands

```powershell
cd web\fusion-rpg-web
npm test -- shell/notify/format
npm run build
npm run extract        # only when a primitive adds lingui-managed copy
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

## Project structure

```
gk-web/web/fusion-rpg-web/src/shell/notify/format/
  translator.ts          → NotifyTranslator, NotifyText, NotifyTarget
  kit.ts                 → NotifyFormatKit (the primitives above)
  registry.ts            → registerTranslator / translatorFor
  translators.ts         → the one index of domain translators (import list only)
  render.ts              → renderNotification(item): NotifyText — translator or designed fallback
  kit.test.ts
  render.test.ts
  coverageGuard.test.ts  → every catalog (category, messageKey) resolves without the fallback
```

## Code style

```ts
// render.ts — the only entry point a surface calls. Surfaces never call a translator directly.
export function renderNotification(item: NotificationItem): NotifyText {
  const translator = translatorFor(catalogDomainOf(item.category));
  const text = translator?.translate(item, kit) ?? null;
  return text ?? designedFallback(item); // category displayName + neutral body; never the id
}
```

## Testing strategy

Vitest, colocated. Contract assertions only. There are no counts of categories or keys, and no
assertion on authored sentence text (DESIGN-GATE §3 rule 7): tests check **that** a sentence exists
and that it contains no raw id, not **what** it says.

1. **Every closed arg kind has a primitive**, except `domainToken`, which must have none. The set of
   kinds is taken from the vocabulary's union, so adding a kind without a primitive fails.
2. **Refs never leak ids.** An unresolvable `ref` renders the `Pending` placeholder, and the output
   does not contain the id string.
3. **Coverage guard.** For each catalog category and each of its `messageKeys`, the domain's
   translator must supply at least one sample item through a `samples(messageKey)` export on
   `NotifyTranslator`. Only the domain can build a meaningful `domainToken`, which is why the samples
   are the translator's. Every sample must render without `null`, and the output must not contain the
   category id or a raw engine token. A catalog key with no samples fails. The loop runs over the
   catalog at test time, so the guard grows with the open registry without a pinned number.
4. **Designed fallback.** An unknown domain renders `categoryName` plus the neutral body, and in
   development logs once.

## Boundaries

- **Always:** format numbers through `formatMagnitude`; resolve references through the domain's
  resolver; route every render through `renderNotification`.
- **Ask first:** a new primitive. It changes `NotifyArgKind`, a closed enum owned by
  `notify-vocabulary`.
- **Never:** domain vocabulary in `shell/notify/format/` (for example parsing `loam.shortfall:` here);
  a primitive that reads a `domainToken`; a raw id or token on a player surface; a second magnitude
  formatter.

## Success criteria

1. The kit, contract, registry and designed fallback exist, and nothing domain-specific is in
   `shell/notify/format/` apart from the import list in `translators.ts`.
2. The coverage guard passes over the real catalog once the domain translators register.
3. `npm test` and `npm run build` green.

## Seedsmith / generator

None. Shared formatting code. The copy it formats is authored by each domain translator, and the
category names are authored catalog rows (GG-62).

## Open questions

None. R-N3 decided the split and the up-front order. The web location follows from where the
existing translation and i18n already live.
