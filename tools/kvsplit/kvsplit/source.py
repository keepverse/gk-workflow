"""Read the legacy repo's tracked tree at a pinned commit, through git only.

Never reads the working tree: a dirty checkout, untracked files and concurrent edits in the
legacy repo cannot change what the tool sees.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


class SourceError(RuntimeError):
    pass


@dataclass(frozen=True)
class Entry:
    path: str      # repo-relative, '/'-separated
    mode: str      # git mode, e.g. 100644, 100755, 120000, 160000
    kind: str      # blob | commit
    oid: str       # object id


def _git(repo: Path, *args: str) -> bytes:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if proc.returncode != 0:
        raise SourceError(f"git {' '.join(args)} failed: {proc.stderr.decode(errors='replace').strip()}")
    return proc.stdout


class GitSource:
    """Tracked entries and blob bytes of `repo` at commit `rev`."""

    def __init__(self, repo: Path, rev: str) -> None:
        self.repo = Path(repo)
        self.sha = _git(self.repo, "rev-parse", "--verify", f"{rev}^{{commit}}").decode().strip()
        self._entries: list[Entry] | None = None
        self._blobs: dict[str, bytes] = {}

    def entries(self) -> list[Entry]:
        if self._entries is None:
            raw = _git(self.repo, "ls-tree", "-r", "-z", "--full-tree", self.sha)
            out: list[Entry] = []
            for rec in raw.split(b"\0"):
                if not rec:
                    continue
                meta, path = rec.split(b"\t", 1)
                mode, kind, oid = meta.decode().split(" ")
                out.append(Entry(path.decode("utf-8"), mode, kind, oid))
            out.sort(key=lambda e: e.path)
            self._entries = out
        return self._entries

    def paths(self) -> list[str]:
        return [e.path for e in self.entries()]

    def load_blobs(self) -> dict[str, bytes]:
        """Bytes of every blob entry, keyed by path. One `git cat-file --batch` process."""
        if self._blobs:
            return self._blobs
        blobs = [e for e in self.entries() if e.kind == "blob"]
        proc = subprocess.Popen(
            ["git", "-C", str(self.repo), "cat-file", "--batch"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        assert proc.stdin and proc.stdout
        try:
            for e in blobs:
                proc.stdin.write(e.oid.encode() + b"\n")
                proc.stdin.flush()
                header = proc.stdout.readline().decode().split()
                if len(header) != 3 or header[1] != "blob":
                    raise SourceError(f"cat-file: unexpected header {header!r} for {e.path}")
                size = int(header[2])
                data = proc.stdout.read(size)
                proc.stdout.read(1)  # trailing LF
                if len(data) != size:
                    raise SourceError(f"cat-file: short read for {e.path}")
                self._blobs[e.path] = data
        finally:
            proc.stdin.close()
            proc.wait()
        if proc.returncode != 0:
            raise SourceError("git cat-file --batch exited with an error")
        return self._blobs
