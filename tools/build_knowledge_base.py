"""
Build a local, searchable knowledge base from a speaker's folder.

    python tools/build_knowledge_base.py "D:/Talks" [--exclude "Private docs" --exclude "Contracts"]

Read-only for your files. Writes only to <folder>/_ai/:
  inventory.json   every file: path, extension, size, modified time
  kb.sqlite3       documents, units (slide/page text + speaker notes), slide_images, FTS5 index

Safe to re-run: the database is rebuilt from scratch except the OCR table (see ocr.py).
"""
import argparse, json, os, posixpath, re, sqlite3, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path

for _s in (sys.stdout, sys.stderr):  # Windows consoles default to cp1251/cp437
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass
from xml.etree import ElementTree as ET

SERVICE = "_ai"
SKIP_DIRS = {SERVICE, ".obsidian", ".git", ".trash", "_Base"}
TEXT_EXT = {".txt", ".md", ".html", ".htm", ".csv", ".rtf", ".srt", ".vtt"}


def clean(s):
    s = (s or "").replace("\x0b", "\n").replace("\r", "")
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n", s).strip()


def inventory(root, excludes):
    files = []
    for directory, dirs, names in os.walk(root):
        rel_dir = Path(directory).relative_to(root).as_posix()
        dirs[:] = sorted(d for d in dirs
                         if not (rel_dir == "." and d in SKIP_DIRS) and not d.startswith(".")
                         and not any(f"{rel_dir}/{d}".lstrip("./").startswith(x) for x in excludes))
        for name in sorted(names):
            if name.startswith("~$"):
                continue
            p = Path(directory, name)
            try:
                st = p.stat()
            except OSError:
                continue
            files.append({
                "path": p.relative_to(root).as_posix(),
                "name": name,
                "extension": p.suffix.lower(),
                "size_bytes": st.st_size,
                "modified_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(timespec="seconds"),
            })
    return files


def shapes_text(shapes):
    out = []
    for sh in shapes:
        if sh.has_text_frame:
            out += [p.text for p in sh.text_frame.paragraphs if p.text.strip()]
        if getattr(sh, "has_table", False) and sh.has_table:
            out += [" | ".join(c.text.replace("\n", " / ") for c in row.cells) for row in sh.table.rows]
        if sh.shape_type == 6:  # group
            out += shapes_text(sh.shapes)
    return out


def extract_pptx(path):
    from pptx import Presentation
    units = []
    for i, slide in enumerate(Presentation(path).slides, 1):
        text = "\n".join(shapes_text(slide.shapes))
        notes = ""
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame.text if slide.notes_slide.notes_text_frame else ""
        pics = sum(1 for s in slide.shapes if s.shape_type == 13)
        units.append(("slide", i, clean(text), clean(notes), pics))
    return units


def slide_media(path):
    """slide number -> media files used on it (to link OCR of pictures back to slides)."""
    out = []
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        for name in names:
            m = re.fullmatch(r"ppt/slides/slide(\d+)\.xml", name)
            rels = f"ppt/slides/_rels/slide{m.group(1)}.xml.rels" if m else None
            if not m or rels not in names:
                continue
            for rel in ET.fromstring(z.read(rels)):
                target = rel.attrib.get("Target", "")
                if "/media/" in target:
                    out.append((int(m.group(1)), posixpath.normpath(posixpath.join("ppt/slides", target))))
    return out


def extract_pdf(path):
    import fitz
    with fitz.open(path) as doc:
        if doc.needs_pass:
            raise ValueError("password protected")
        return [("page", i + 1, clean(p.get_text()), "", len(p.get_images())) for i, p in enumerate(doc)]


def extract_docx(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    paras = []
    for p in root.iter():
        if p.tag.endswith("}p"):
            t = "".join(x.text or "" for x in p.iter() if x.tag.endswith("}t"))
            if t.strip():
                paras.append(t)
    return [("document", 1, clean("\n".join(paras)), "", 0)]


def extract_text(path):
    raw = Path(path).read_bytes()
    for enc in ("utf-8-sig", "utf-16", "cp1251", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeError:
            continue
    if path.suffix.lower() in (".html", ".htm"):
        text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
    return [("document", 1, clean(text)[:200000], "", 0)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--exclude", action="append", default=[],
                    help="relative folder prefix to skip entirely (private documents). Repeatable.")
    args = ap.parse_args()
    root = Path(args.folder).resolve()
    out = root / SERVICE
    out.mkdir(exist_ok=True)

    files = inventory(root, [e.replace("\\", "/").strip("/") for e in args.exclude])
    (out / "inventory.json").write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "excluded": args.exclude, "file_count": len(files), "files": files,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    counts = {}
    for f in files:
        counts[f["extension"] or "(none)"] = counts.get(f["extension"] or "(none)", 0) + 1
    print(f"Inventory: {len(files)} files")
    for ext, n in sorted(counts.items(), key=lambda x: -x[1])[:15]:
        print(f"  {ext:8} {n}")

    db = sqlite3.connect(out / "kb.sqlite3")
    db.executescript("""
    DROP TABLE IF EXISTS documents; DROP TABLE IF EXISTS units; DROP TABLE IF EXISTS slide_images; DROP TABLE IF EXISTS search;
    CREATE TABLE documents(path TEXT PRIMARY KEY, name TEXT, extension TEXT, size_bytes INTEGER, modified_utc TEXT, status TEXT);
    CREATE TABLE units(path TEXT, kind TEXT, number INTEGER, text TEXT, notes TEXT, pictures INTEGER, PRIMARY KEY(path, kind, number));
    CREATE TABLE slide_images(path TEXT, slide INTEGER, media TEXT, PRIMARY KEY(path, slide, media));
    CREATE TABLE IF NOT EXISTS ocr(source TEXT PRIMARY KEY, path TEXT, kind TEXT, number TEXT, text TEXT, error TEXT, sha256 TEXT);
    CREATE VIRTUAL TABLE search USING fts5(path UNINDEXED, kind UNINDEXED, number UNINDEXED, text, tokenize="unicode61");
    """)
    for i, f in enumerate(files, 1):
        p, ext = root / f["path"], f["extension"]
        status, units = "metadata only", []
        try:
            if ext in (".pptx", ".potx"):
                units = extract_pptx(p)
                for slide, media in slide_media(p):
                    db.execute("INSERT OR IGNORE INTO slide_images VALUES (?,?,?)", (f["path"], slide, media))
            elif ext == ".pdf":
                units = extract_pdf(p)
            elif ext == ".docx":
                units = extract_docx(p)
            elif ext in TEXT_EXT:
                units = extract_text(p)
            if units:
                has_text = any(u[2] or u[3] for u in units)
                status = "text extracted" if has_text else "no text layer (scan or images: run ocr.py)"
        except Exception as e:  # keep going, record the error
            status = f"error: {type(e).__name__}: {e}"[:300]
        db.execute("INSERT INTO documents VALUES (?,?,?,?,?,?)",
                   (f["path"], f["name"], ext, f["size_bytes"], f["modified_utc"], status))
        for kind, num, text, notes, pics in units:
            db.execute("INSERT OR REPLACE INTO units VALUES (?,?,?,?,?,?)", (f["path"], kind, num, text, notes, pics))
        if i % 50 == 0:
            db.commit()
            print(f"  {i}/{len(files)}", flush=True)
    db.commit()
    rebuild_search(db)
    n_units = db.execute("SELECT count(*) FROM units").fetchone()[0]
    print(f"Done: {n_units} slides/pages/documents in {out / 'kb.sqlite3'}")


def rebuild_search(db):
    db.execute("DELETE FROM search")
    db.execute("""INSERT INTO search(path, kind, number, text)
                  SELECT u.path, u.kind, u.number, d.name || '\n' || coalesce(u.text,'') || '\n' || coalesce(u.notes,'')
                  FROM units u JOIN documents d USING(path)""")
    db.execute("""INSERT INTO search(path, kind, number, text)
                  SELECT path, 'ocr:' || kind, number, text FROM ocr WHERE error IS NULL AND length(text) > 20""")
    db.execute("""INSERT INTO search(path, kind, number, text)
                  SELECT path, 'file', 0, name FROM documents WHERE path NOT IN (SELECT path FROM units)""")
    db.commit()


if __name__ == "__main__":
    sys.exit(main())
