# Resume 30 — `.commandcode` tracked-configuration review

## Task

Review the three dirty `.commandcode` paths using the captured evidence bundle, following the owner's
decision to treat them as **tracked configuration for review**. This is a read-only review lane. Do
not edit the source paths, add ignore rules, delete files, commit configuration, or merge anything.

The review is spawned from prepared boundary commit
`67f16a23be82ec513ab5a9cb542dadb0ff3f0d16`, whose only additions are the evidence bundle and this
lane's session record. The product comparison base remains `6d77888cc`.

The exact source paths are represented by the bundle at
`tasks/evidence-fragments/commandcode-config-review-20260925/`; read that bundle rather than the main
checkout or any path outside this worktree.

## Exact fence

Only these paths may be written:

- `tasks/evidence-fragments/commandcode-config-review-20260925/**` (already prepared; do not alter)
- `tasks/reports/resume-30-commandcode-config-review-20260925.md` (the report)

The three source paths are evidence references only:

- `.commandcode/settings.json`
- `.commandcode/taste/taste/taste.md`
- `.commandcode/taste/workflow/taste.md`

Do not read or write their main-checkout copies. Do not modify the manager's evidence bundle.

## Review questions

Read the captured `MANIFEST.md` and all three files, then inspect the repository's tracked assistant
configuration conventions and the current `git ls-files` state. Answer:

1. Is each file safe and portable to track, local-only, or unsafe to keep?
2. Does it contain secrets, machine-local paths, assistant/vendor watermarks, or permissions that
   would be dangerous in a committed repository?
3. Is the proposed ownership clear enough for a named tooling/configuration owner?
4. What exact patch or narrow policy would be needed if the owner chooses tracked configuration?
5. Which claims can be proved from the bundle, and which require the actual owner/main checkout?

Do not silently choose a policy. Recommend one option for each file and leave the owner decision
explicit. A report-only `done` is valid; no product or configuration implementation is authorized.

## Required verification

```powershell
Get-FileHash -Algorithm SHA256 tasks/evidence-fragments/commandcode-config-review-20260925/settings.json
Get-FileHash -Algorithm SHA256 tasks/evidence-fragments/commandcode-config-review-20260925/taste.md
Get-FileHash -Algorithm SHA256 tasks/evidence-fragments/commandcode-config-review-20260925/workflow-taste.md
```

```powershell
git status --short --branch
```

```powershell
python scripts/audit-doc-citations.py --scope tasks/reports/resume-30-commandcode-config-review-20260925.md --strict
```

```powershell
git diff --check
```

## Required report

Include the three source hashes, tracked/untracked state, exact evidence commands and outputs, risks,
recommended routing for each file, unresolved owner questions, and next steps. State explicitly that
no `.commandcode` source path, ignore rule, cleanup tool, or integration checkout was changed. End with
the runner `<<<REPORT {...} REPORT>>>` block. Do not merge or push.
