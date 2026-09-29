# BCU7.2 — disabledReasonGuard, already fixed

No session fences either file. Live-verified: CommandersLayer.tsx:155,190 and
CommanderSheetFooter.tsx:41 (real path ui/actor/, task's own path was stale) already carry real
title reasons on every disabled button.

```
$ npx vitest run src/ui/disabledReasonGuard.test.ts
6/6 green, 0 violations
```

Fixed upstream of this session, most likely one of the many features/mega-merge lanes. Also fixed
a doc-citation exemption wording gap on BCU7.1's own title line (D1: cited GearTab.tsx after
deleting it without the line itself saying so).
