"""Weekly zip backup of your Obsidian vaults.

  python scripts/backup.py              back up every vault to every enabled destination
  python scripts/backup.py --only personal speaking
  python scripts/backup.py --dry-run    show what would go into the archives, write nothing
  python scripts/backup.py --dest D:\\tmp\\test   put the archives into one folder (for testing)

Settings: config/backup.json; vault list: config/vaults.json (+ extra_folders).
Each vault → <dest>/<id>/<id>_YYYY-MM-DD.zip; the last `keep` archives are kept.
Files larger than max_file_mb are skipped (usually PPTX/PDF that have originals elsewhere); they are listed in the log.
With encrypt: true for a vault, its archive is AES-256 encrypted via 7-Zip using OBSIDIAN_BACKUP_PASSWORD.
Log: registry/backup_log.md. The vaults are only read.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "registry" / "backup_log.md"
SEVEN_ZIP = [r"C:\Program Files\7-Zip\7z.exe", "7z"]

for s in (sys.stdout, sys.stderr):
    try:
        s.reconfigure(encoding="utf-8")
    except Exception:
        pass


def load():
    cfg = json.loads((ROOT / "config" / "backup.json").read_text(encoding="utf-8"))
    vaults = json.loads((ROOT / "config" / "vaults.json").read_text(encoding="utf-8"))["vaults"]
    folders = [{"id": v["id"], "path": v["path"]} for v in vaults] + cfg.get("extra_folders", [])
    return cfg, folders


def collect(folder: Path, exclude_dirs: set[str], max_bytes: int):
    files, skipped = [], []
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for name in filenames:
            p = Path(dirpath) / name
            try:
                size = p.stat().st_size
            except OSError:
                continue
            if size > max_bytes:
                skipped.append((p.relative_to(folder).as_posix(), size))
            else:
                files.append(p)
    return files, skipped


def find_7z():
    for c in SEVEN_ZIP:
        if Path(c).exists() or shutil.which(c):
            return c
    return None


def make_zip(folder: Path, files: list[Path], out: Path, password: str | None):
    if password:
        exe = find_7z()
        if not exe:
            raise RuntimeError("encryption needs 7-Zip")
        lst = out.with_suffix(".lst")
        lst.write_text("\n".join(str(f.relative_to(folder)) for f in files), encoding="utf-8")
        r = subprocess.run(
            [exe, "a", "-tzip", "-mem=AES256", f"-p{password}", "-scsUTF-8", str(out), f"@{lst}"],
            cwd=folder, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        lst.unlink(missing_ok=True)
        if r.returncode != 0:
            raise RuntimeError("7-Zip: " + (r.stderr or r.stdout)[-500:])
    else:
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for f in files:
                z.write(f, f.relative_to(folder).as_posix())
        with zipfile.ZipFile(out) as z:
            bad = z.testzip()
            if bad:
                raise RuntimeError(f"corrupt file in archive: {bad}")


def rotate(dir_: Path, vid: str, keep: int):
    old = sorted(dir_.glob(f"{vid}_*.zip"))
    for p in old[:-keep] if keep > 0 else []:
        p.unlink()


def mb(n):
    return f"{n / 1e6:.1f} MB"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--dest")
    a = ap.parse_args()

    cfg, folders = load()
    dests = [{"name": "custom", "path": a.dest}] if a.dest else [
        d for d in cfg["destinations"] if d.get("enabled") and d.get("path")
    ]
    if not dests and not a.dry_run:
        sys.exit("No enabled destinations in config/backup.json")
    for d in dests:
        anchor = Path(d["path"]).anchor
        if not anchor or not Path(anchor).exists():
            print(f"!! drive not available: {d['path']}")
    exclude = set(cfg.get("exclude_dirs", []))
    max_bytes = int(cfg.get("max_file_mb", 20) * 1e6)
    stamp = dt.date.today().isoformat()
    opts = cfg.get("vault_options", {})
    log = [f"\n## {dt.datetime.now():%Y-%m-%d %H:%M}" + (" (dry-run)" if a.dry_run else "")]

    for f in folders:
        vid = f["id"]
        if a.only and vid not in a.only:
            continue
        src = Path(f["path"])
        if not src.is_dir():
            print(f"!! {vid}: folder missing {src}")
            log.append(f"- **{vid}**: folder not found")
            continue
        o = opts.get(vid, {})
        password = None
        if o.get("encrypt"):
            password = os.environ.get("OBSIDIAN_BACKUP_PASSWORD")
            if not password:
                print(f"-- {vid}: skipped, set OBSIDIAN_BACKUP_PASSWORD (encrypt: true)")
                log.append(f"- **{vid}**: skipped, no encryption password set")
                continue
        files, skipped = collect(src, exclude, max_bytes)
        total = sum(p.stat().st_size for p in files)
        line = f"{vid}: {len(files)} files, {mb(total)} uncompressed; large files skipped: {len(skipped)}"
        if a.dry_run:
            print(line)
            for s, n in skipped:
                print(f"    > {s} ({mb(n)})")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / f"{vid}_{stamp}.zip"
            try:
                make_zip(src, files, out, password)
            except Exception as e:
                print(f"!! {vid}: {e}")
                log.append(f"- **{vid}**: error: {e}")
                continue
            size = out.stat().st_size
            placed = []
            for d in dests:
                target_dir = Path(d["path"]) / vid
                try:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    part = target_dir / (out.name + ".part")
                    shutil.copy2(out, part)
                    os.replace(part, target_dir / out.name)
                    rotate(target_dir, vid, int(cfg.get("keep", 6)))
                    placed.append(d["name"])
                except OSError as e:
                    print(f"!! {vid} → {d['name']}: {e}")
                    log.append(f"- **{vid}** → {d['name']}: error: {e}")
        enc = ", encrypted" if password else ""
        print(f"ok {line}; archive {mb(size)}{enc} → {', '.join(placed) or 'nowhere'}")
        log.append(f"- **{vid}**: {len(files)} files, archive {mb(size)}{enc} → {', '.join(placed) or 'nowhere'}")
        for s, n in skipped:
            log.append(f"  - not archived (large): `{s}` ({mb(n)})")

    if not a.dry_run:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        if not LOG.exists():
            LOG.write_text("---\ntype: system\n---\n\n# Backup log\n", encoding="utf-8")
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(log) + "\n")


if __name__ == "__main__":
    main()
