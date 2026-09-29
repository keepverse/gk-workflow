# `.commandcode` tracked-config review evidence

**Captured:** 2026-09-25
**Owner decision:** review these paths as tracked configuration; do not silently ignore or delete them.

These are byte-for-byte copies of the three dirty main-checkout paths at capture time. The review lane
must read this bundle, not the manager or main checkout directly.

| Bundle file | Source path | SHA-256 | Current checkout state |
|---|---|---|---|
| `settings.json` | `.commandcode/settings.json` | `4CB9784F1025E84C8FE9827BA47545A1AD9772EF3D1A8643F3E1EDA654C02FAA` | untracked |
| `taste.md` | `.commandcode/taste/taste/taste.md` | `1DBDCD9A3C9B5111EC5F5C3F01DC64789E81CD5214CE4915E922E610ABC1D14F` | modified |
| `workflow-taste.md` | `.commandcode/taste/workflow/taste.md` | `9F36148D37A22571A353D510106F01E0458694236D1DA132A4D91B785B4CF9EB` | untracked |

The copies are evidence only. They are not a request to edit the source paths, add an ignore rule, or
merge them. The review report must recommend one of: tracked with a named owner and exact patch,
local-only with an explicit narrow policy, or explicit owner-authorized removal. It must call out
portability, secret, machine-local, and assistant-watermark risks.
