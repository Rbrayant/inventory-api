"""Require a version newer than all existing release tags."""
import re
import subprocess
from pathlib import Path

pattern = r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
version = Path("VERSION").read_text().strip()
if not re.fullmatch(pattern, version):
    raise SystemExit("VERSION must use vMAJOR.MINOR.PATCH")

current = tuple(map(int, version[1:].split(".")))
tags = subprocess.check_output(
    ["git", "tag", "--list", "v*"], text=True
).splitlines()

for tag in tags:
    if re.fullmatch(pattern, tag):
        released = tuple(map(int, tag[1:].split(".")))
        if current <= released:
            raise SystemExit("VERSION must exceed existing release tags")

print(version)
