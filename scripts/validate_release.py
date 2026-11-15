"""Enforce a release version bump against the parent commit."""
import re
import subprocess
from pathlib import Path

version = Path("VERSION").read_text().strip()
if not re.fullmatch(r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
    raise SystemExit("VERSION must use vMAJOR.MINOR.PATCH")
result = subprocess.run(["git", "show", "HEAD^:VERSION"], text=True,
                        capture_output=True)
if result.returncode == 0:
    previous = result.stdout.strip()
    if tuple(map(int, version[1:].split('.'))) <= tuple(
            map(int, previous[1:].split('.'))):
        raise SystemExit("Every main release must increase VERSION")
print(version)
