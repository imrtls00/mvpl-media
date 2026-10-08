#!/usr/bin/env python3
"""Delete media older than N days (default 15) from images/ and reels/.

Age comes from MANIFEST.tsv (path<TAB>YYYY-MM-DD added), not git history,
because the clone may be shallow. Files missing from the manifest are
treated as added today, so they are never deleted by surprise.

  python3 scripts/cleanup_media.py                 # dry run
  python3 scripts/cleanup_media.py --apply         # delete, commit, push
  python3 scripts/cleanup_media.py --keep keep.txt # skip paths/URLs listed in keep.txt
                                                   # (media still used by scheduled or draft posts)
Also stamps .last_cleanup so the weekly check knows when it last ran.
"""
import argparse, datetime as dt, subprocess, sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--days", type=int, default=15)
ap.add_argument("--apply", action="store_true")
ap.add_argument("--keep", help="text file; any file whose path appears in it is kept")
ap.add_argument("--today", help="YYYY-MM-DD override, for tests")
a = ap.parse_args()

today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
keep_text = Path(a.keep).read_text() if a.keep else ""
man_path = root / "MANIFEST.tsv"
rows = [l.rstrip("\n").split("\t") for l in man_path.read_text().splitlines()[1:] if l.strip()]
man = {p: d for p, d in rows}

on_disk = [str(p.relative_to(root)) for d in ("images", "reels") for p in (root / d).rglob("*")
           if p.is_file() and p.name != ".gitkeep"]
for p in on_disk:
    man.setdefault(p, today.isoformat())

delete, kept = [], []
for p in sorted(man):
    if p not in on_disk:
        continue
    age = (today - dt.date.fromisoformat(man[p])).days
    if age > a.days:
        (kept if p in keep_text else delete).append((p, age))

for p, age in delete: print(f"DELETE {p} ({age}d)")
for p, age in kept: print(f"KEEP   {p} ({age}d, still referenced)")
print(f"{len(delete)} to delete, {len(kept)} kept, {len(on_disk)} on disk")

if not a.apply:
    print("dry run. use --apply to delete."); sys.exit(0)

gone = {p for p, _ in delete}
for p in gone: (root / p).unlink()
man = {p: d for p, d in man.items() if p not in gone and p in on_disk}
man_path.write_text("path\tadded\n" + "".join(f"{p}\t{d}\n" for p, d in sorted(man.items())))
(root / ".last_cleanup").write_text(today.isoformat() + "\n")
g = lambda *c: subprocess.run(["git", "-C", str(root), *c], check=True)
g("add", "-A")
g("commit", "-m", f"Cleanup: remove {len(gone)} media older than {a.days} days")
g("push", "origin", "HEAD")
