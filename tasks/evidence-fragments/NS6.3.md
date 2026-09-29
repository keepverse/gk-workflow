# NS6.3 — Web cache translator

| Criterion | Command | Result |
|---|---|---|
| `cacheNotifyTranslator.ts` (domain `corpse-cache`) with authored sentences over `fmt.count` and `fmt.ref` (`sectorLabel`; lanes follow `laneLabel`'s rule, never splitting the id; unresolvable lane → `Pending`); registered in `translators.ts`; `samples()` for `cache.created` and `cache.decayed` | `cd web\fusion-rpg-web; npx vitest run src/stages/world/cacheClaim src/shell/notify/format` | `Test Files 5 passed, Tests 54 passed` |
| no regression | `npx vitest run src/shell/notify src/stages/world/cacheClaim src/features/notices src/lib/bus` | `Test Files 32 passed, Tests 205 passed` |
| `npm run build` | | `✓ built in 1m 47s` |

A `world_lane` place is never resolvable in v1: the wire carries only the bare lane id (no live
endpoint lookup exists anywhere yet), so `fmt.ref`'s resolver always returns `null` for `lane` and
the kit's own fallback renders `Pending` — this is the CORRECT, spec-anticipated behavior (test 5),
not a gap this task leaves open. `world_sector` resolves through the same static `sectorLabel` the
world translator already uses, and only `sector` becomes a `target` (a lane has no single point on
the map to target, matching `worldTranslator.ts`'s own precedent).
