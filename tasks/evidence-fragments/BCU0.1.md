# BCU0.1 — lawn-signal-ownership

Edited `docs/architecture/lawn-playable-map.md` (new "Signal ownership: `PUT /api/players/current`"
section + corrected owner-framing intro), `docs/architecture/lawn-tuning-profile-map.md` (corrected
sibling-program paragraph), `docs/architecture/lawn-playable/spec-actor-liveness-refresh.md` (new
"Signal ownership" section, `Player` row, rule 4).

Live code check:
```
$ grep -n "DefaultEnabled" gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackFeature.cs
56:    public const bool DefaultEnabled = true;
```

Effect: `SP6.6` (lane B) named as sole owner of the `PUT /api/players/current` notice;
`actor-liveness-refresh` extends it (Ladder/CommanderAllocation/UniqueAllocation/Equip/Tree +
reserved `empireId`), never a second `Player`-kind channel. combat-ai's CAI4.1/CAI4.2 entry condition
(`tasks/combat-ai-todo.md:529`, edge E1) is satisfied.
