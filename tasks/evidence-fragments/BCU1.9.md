# BCU1.9 — deferred-fix list reconciled

Re-checked the one remaining deferred item (`gk-core/scripts/verification-boundaries.v1.json`): still fenced
by lane-b and lane-d2 (test-verification-boundary's own registry), stays deferred.

Found and fixed a real gap: two of my own wave-1 banners used paraphrased wording instead of the
spec's literal mandated phrase, so `pipeline-audit-v2`'s exact-phrase suppression regex missed them.

```
$ python gk-core/scripts/audit-program-pipeline.py --only todo-header-vs-boxes --json | python -c "import json,sys; d=json.load(sys.stdin); print([x['program'] for x in d if x['program'] in ['rift-gate','onboarding-rift','debug-mcp','game-control','achievement-title','story-scene']])"
[]
```

CB1 checkpoint: all 3 boxes ticked (commit list, pipeline-audit-v2 check, spot-check record above).
