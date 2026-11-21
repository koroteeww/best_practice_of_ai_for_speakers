"""Meta vault: a registry of notes across all your Obsidian vaults, with SHA-256 hashes.

Commands:
  python scripts/scan.py scan            walk the vaults, update the registry, write registry/pending.md
  python scripts/scan.py pending         show what changed and has not been reviewed yet
  python scripts/scan.py ack [--vault ID] [--path VAULT:REL ...] [--all]
                                         mark notes as reviewed
  python scripts/scan.py find TEXT       search titles, paths and descriptions in all vaults
  python scripts/scan.py stats           per-vault summary, bridges, cleanup candidates
  python scripts/scan.py uri VAULT:REL   obsidian:// link to a note

Python standard library only. The vaults are read, never modified.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "vaults.json"
DB = ROOT / "registry" / "registry.sqlite"
PENDING_MD = ROOT / "registry" / "pending.md"
PENDING_JSON = ROOT / "registry" / "pending.json"

STALE_BRIDGE_DAYS = 180
WIKILINK = re.compile(r"\[\[([^\]|#]+)")

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except Exception:
        pass


def now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def load_vaults() -> list[dict]:
    return json.loads(CONFIG.read_text(encoding="utf-8"))["vaults"]


def connect() -> sqlite3.Connection:
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS notes (
            vault TEXT NOT NULL,
            path TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            reviewed_sha256 TEXT,
            size INTEGER,
            mtime TEXT,
            title TEXT,
            type TEXT,
            description TEXT,
            tags TEXT,
            words INTEGER,
            links INTEGER,
            meta_source TEXT,
            first_seen TEXT,
            changed_at TEXT,
            last_seen TEXT,
            deleted_at TEXT,
            PRIMARY KEY (vault, path)
        );
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            at TEXT, new INTEGER, changed INTEGER, deleted INTEGER, total INTEGER
        );
        """
    )
    return con


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm: dict[str, str] = {}
    current = None
    for line in text[3:end].splitlines():
        if not line.strip():
            continue
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if m:
            current = m.group(1)
            fm[current] = m.group(2).strip().strip('"\'')
        elif current and line.lstrip().startswith("- "):
            item = line.strip()[2:].strip().strip('"\'')
            fm[current] = (fm[current] + ", " + item).strip(", ")
    return fm


def note_info(path: Path, rel: str) -> dict:
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    fm = parse_frontmatter(text)
    h1 = re.search(r"^#\s+(.+)$", text, re.M)
    body = text.split("\n---", 2)[-1] if text.startswith("---") else text
    return {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size": len(raw),
        "mtime": dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
        "title": (h1.group(1).strip() if h1 else Path(rel).stem)[:200],
        "type": fm.get("type", "")[:50],
        "description": fm.get("description", "")[:400],
        "tags": fm.get("tags", "").strip("[]")[:200],
        "words": len(re.findall(r"\w+", body)),
        "links": len(WIKILINK.findall(text)),
        "meta_source": fm.get("meta_source", ""),
    }


def iter_notes(vault: dict):
    root = Path(vault["path"])
    excl = [e.replace("\\", "/").strip("/") for e in vault.get("exclude", [])]
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root).as_posix()
        rel_dir = "" if rel_dir == "." else rel_dir
        dirnames[:] = [
            d for d in dirnames
            if not any((f"{rel_dir}/{d}".strip("/")).startswith(e) for e in excl)
        ]
        for name in filenames:
            if name.lower().endswith(".md"):
                rel = f"{rel_dir}/{name}".strip("/")
                yield Path(dirpath) / name, rel


def cmd_scan(args) -> None:
    con = connect()
    first_run = con.execute("SELECT COUNT(*) FROM notes").fetchone()[0] == 0
    stamp = now()
    new = changed = deleted = total = 0
    for v in load_vaults():
        if not Path(v["path"]).is_dir():
            print(f"!! {v['id']}: folder not found: {v['path']}")
            continue
        seen = set()
        for path, rel in iter_notes(v):
            try:
                info = note_info(path, rel)
            except OSError as e:
                print(f"!! {v['id']}:{rel}: {e}")
                continue
            seen.add(rel)
            total += 1
            row = con.execute(
                "SELECT sha256, deleted_at FROM notes WHERE vault=? AND path=?", (v["id"], rel)
            ).fetchone()
            if row is None:
                new += 1
                reviewed = info["sha256"] if (first_run and not args.no_baseline) else None
                con.execute(
                    """INSERT INTO notes (vault, path, sha256, reviewed_sha256, size, mtime, title, type,
                       description, tags, words, links, meta_source, first_seen, changed_at, last_seen)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (v["id"], rel, info["sha256"], reviewed, info["size"], info["mtime"], info["title"],
                     info["type"], info["description"], info["tags"], info["words"], info["links"],
                     info["meta_source"], stamp, stamp, stamp),
                )
            else:
                is_changed = row["sha256"] != info["sha256"] or row["deleted_at"]
                if is_changed:
                    changed += 1
                con.execute(
                    """UPDATE notes SET sha256=?, size=?, mtime=?, title=?, type=?, description=?, tags=?,
                       words=?, links=?, meta_source=?, last_seen=?, deleted_at=NULL,
                       changed_at=CASE WHEN ? THEN ? ELSE changed_at END
                       WHERE vault=? AND path=?""",
                    (info["sha256"], info["size"], info["mtime"], info["title"], info["type"],
                     info["description"], info["tags"], info["words"], info["links"], info["meta_source"],
                     stamp, 1 if is_changed else 0, stamp, v["id"], rel),
                )
        for r in con.execute(
            "SELECT path FROM notes WHERE vault=? AND deleted_at IS NULL", (v["id"],)
        ).fetchall():
            if r["path"] not in seen:
                deleted += 1
                con.execute(
                    "UPDATE notes SET deleted_at=? WHERE vault=? AND path=?", (stamp, v["id"], r["path"])
                )
    con.execute(
        "INSERT INTO scans (at, new, changed, deleted, total) VALUES (?,?,?,?,?)",
        (stamp, new, changed, deleted, total),
    )
    con.commit()
    print(f"Scan {stamp}: total {total}, new {new}, changed {changed}, deleted {deleted}")
    if first_run and not args.no_baseline:
        print("First run: everything that already exists is taken as the baseline and will not be queued for review.")
    write_pending(con)


def pending_rows(con, vault: str | None = None):
    q = """SELECT * FROM notes WHERE deleted_at IS NULL
           AND (reviewed_sha256 IS NULL OR reviewed_sha256 != sha256)"""
    params: list = []
    if vault:
        q += " AND vault=?"
        params.append(vault)
    return con.execute(q + " ORDER BY vault, changed_at DESC", params).fetchall()


def obsidian_uri(vault: dict, rel: str) -> str:
    file = vault.get("uri_prefix", "") + (rel[:-3] if rel.endswith(".md") else rel)
    return "obsidian://open?vault={}&file={}".format(
        urllib.parse.quote(vault["obsidian_vault"]), urllib.parse.quote(file)
    )


def write_pending(con) -> None:
    vaults = {v["id"]: v for v in load_vaults()}
    rows = pending_rows(con)
    lines = [
        "---", "type: system", f"updated: {now()}", "---", "",
        "# To review", "",
        "Written by `scripts/scan.py`. New and changed notes the meta vault has not looked at yet.",
        "After review: `python scripts/scan.py ack --all` (or per vault / per file).", "",
    ]
    data = []
    for vid, v in vaults.items():
        vrows = [r for r in rows if r["vault"] == vid]
        lines.append(f"## {v['name']} — {len(vrows)}")
        for r in vrows:
            status = "new" if r["reviewed_sha256"] is None else "changed"
            desc = f" — {r['description']}" if r["description"] else ""
            bridge = " (bridge)" if r["meta_source"] else ""
            lines.append(f"- [{r['path']}]({obsidian_uri(v, r['path'])}) · {status}{bridge}, {r['words']} words{desc}")
            data.append({k: r[k] for k in r.keys()} | {"status": status, "uri": obsidian_uri(v, r["path"])})
        lines.append("")
    PENDING_MD.write_text("\n".join(lines), encoding="utf-8")
    PENDING_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def cmd_pending(args) -> None:
    con = connect()
    rows = pending_rows(con, args.vault)
    if not rows:
        print("Nothing new to review.")
        return
    for r in rows:
        status = "NEW" if r["reviewed_sha256"] is None else "CHG"
        print(f"{status} {r['vault']}:{r['path']}  [{r['words']} w] {r['description'][:100]}")
    print(f"Total: {len(rows)}")


def cmd_ack(args) -> None:
    con = connect()
    if args.all:
        n = con.execute("UPDATE notes SET reviewed_sha256=sha256 WHERE deleted_at IS NULL").rowcount
    elif args.vault:
        n = con.execute(
            "UPDATE notes SET reviewed_sha256=sha256 WHERE vault=? AND deleted_at IS NULL", (args.vault,)
        ).rowcount
    elif args.path:
        n = 0
        for p in args.path:
            vault, _, rel = p.partition(":")
            n += con.execute(
                "UPDATE notes SET reviewed_sha256=sha256 WHERE vault=? AND path=?", (vault, rel)
            ).rowcount
    else:
        sys.exit("Pass --all, --vault ID or --path VAULT:REL")
    con.commit()
    print(f"Marked as reviewed: {n}")
    write_pending(con)


def cmd_find(args) -> None:
    con = connect()
    like = f"%{args.text}%"
    rows = con.execute(
        """SELECT vault, path, description FROM notes WHERE deleted_at IS NULL
           AND (title LIKE ? OR path LIKE ? OR description LIKE ? OR tags LIKE ?)
           ORDER BY vault, path LIMIT ?""",
        (like, like, like, like, args.limit),
    ).fetchall()
    for r in rows:
        print(f"{r['vault']}:{r['path']}  {r['description'][:120]}")
    print(f"Found: {len(rows)}")


def cmd_stats(args) -> None:
    con = connect()
    for r in con.execute(
        """SELECT vault, COUNT(*) n, SUM(words) w,
           SUM(CASE WHEN reviewed_sha256 IS NULL OR reviewed_sha256!=sha256 THEN 1 ELSE 0 END) p,
           SUM(CASE WHEN meta_source!='' THEN 1 ELSE 0 END) b
           FROM notes WHERE deleted_at IS NULL GROUP BY vault"""
    ):
        print(f"{r['vault']:<10} notes {r['n']:>5}  words {r['w'] or 0:>8}  to review {r['p']:>4}  bridges {r['b']}")
    last = con.execute("SELECT * FROM scans ORDER BY id DESC LIMIT 1").fetchone()
    if last:
        print(f"Last scan: {last['at']}")
    cutoff = (dt.datetime.now() - dt.timedelta(days=STALE_BRIDGE_DAYS)).isoformat()
    stale = con.execute(
        "SELECT vault, path, mtime FROM notes WHERE meta_source!='' AND deleted_at IS NULL AND mtime < ?",
        (cutoff,),
    ).fetchall()
    if stale:
        print(f"\nBridges not edited for more than {STALE_BRIDGE_DAYS} days (cleanup candidates):")
        for r in stale:
            print(f"  {r['vault']}:{r['path']}  (last edit {r['mtime'][:10]})")
    broken = []
    for r in con.execute("SELECT vault, path, meta_source FROM notes WHERE meta_source!='' AND deleted_at IS NULL"):
        sv, _, sp = r["meta_source"].partition(":")
        if not con.execute(
            "SELECT 1 FROM notes WHERE vault=? AND path=? AND deleted_at IS NULL", (sv, sp)
        ).fetchone():
            broken.append(r)
    if broken:
        print("\nBridges whose original is gone:")
        for r in broken:
            print(f"  {r['vault']}:{r['path']} -> {r['meta_source']}")


def cmd_uri(args) -> None:
    vaults = {v["id"]: v for v in load_vaults()}
    vault, _, rel = args.target.partition(":")
    print(obsidian_uri(vaults[vault], rel))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--no-baseline", action="store_true",
                   help="on the first run, do not take existing notes as already reviewed")
    s.set_defaults(func=cmd_scan)
    s = sub.add_parser("pending")
    s.add_argument("--vault")
    s.set_defaults(func=cmd_pending)
    s = sub.add_parser("ack")
    s.add_argument("--all", action="store_true")
    s.add_argument("--vault")
    s.add_argument("--path", nargs="+")
    s.set_defaults(func=cmd_ack)
    s = sub.add_parser("find")
    s.add_argument("text")
    s.add_argument("--limit", type=int, default=40)
    s.set_defaults(func=cmd_find)
    s = sub.add_parser("stats")
    s.set_defaults(func=cmd_stats)
    s = sub.add_parser("uri")
    s.add_argument("target")
    s.set_defaults(func=cmd_uri)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
