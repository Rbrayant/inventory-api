"""Prepare real source changes, then commit, push and open the PR yourself."""
import argparse
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("version", choices=["v1.0.0", "v1.1.0", "v1.2.0"])
args = parser.parse_args()
source = root / "demo" / args.version
(root / "app/main.py").write_text((source / "main.py").read_text())
for name in ["test_filter.py", "test_quantity.py"]:
    destination = root / "tests" / name
    if (source / name).exists():
        destination.write_text((source / name).read_text())
    else:
        destination.unlink(missing_ok=True)
(root / "VERSION").write_text(args.version + "\n")
print(f"Prepared {args.version}. Review, test, commit and open a PR.")
