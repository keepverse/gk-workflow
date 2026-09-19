"""kvsplit: deterministic migration of the legacy monorepo into the Keepverse workspace.

The migrated repositories are this tool's OUTPUT. Same source SHA + same rules + same tool
version must produce byte-identical staged trees. Anything the tool cannot handle becomes a
residue item; residue is fixed by changing rules/transforms or by a source commit in the
legacy repo, never by editing output.
"""

__version__ = "0.1.0"
