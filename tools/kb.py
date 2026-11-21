"""
kb.py — a speaker-archive tool designed to be run by an AI agent (Claude Code, Codex, ...), not by a human.

OUTPUT GOES TO FILES, NOT THE CONSOLE
  Every call saves its result as JSON in <root>/_ai/kb_out/<time>_<command>.json
  (a copy in kb_out/last.json, a log of all calls in kb_out/history.jsonl; the last 300 results are kept).
  The console gets one line: "<file path>  |  <summary>". Read the file with your Read tool:
  no console-encoding problems, no truncation, and the next session can see what was already searched.
  Errors: {"error": ...} in the file, "ERROR: ..." in the summary, exit code 1.
  --stdout prints the full JSON instead; --text prints human-readable text instead.
  Images are returned as absolute PNG paths that the agent opens with its image/Read tool to *see* slides.

    python tools/kb.py --root "D:/Talks" <command> [args]        (or set KB_ROOT, or run from the folder)

COMMANDS
  update  [--full]                     build/refresh the slide index (incremental: only new/changed files)
  stats                                what is indexed: files, slides, languages, duplicates, OCR-only slides
  search  "<query>" [--lang ru|en|mix] [--folder X] [--type pptx|pdf|docx] [--limit N] [--exact]
                                       slides matching the query; identical slides from other versions are merged
  show    <path> <n> [--no-png]        full text of one slide: title, text, speaker notes, OCR + PNG preview
  outline <path> [--max N]             table of contents of a deck: number -> title
  decks   [--folder X] [--q word]      list of decks, newest first
  sheet   <path> [--from A --to B] | --hits "<query>"
                                       contact sheet: one PNG grid of up to 40 slides with numbers
  preview <path> <n> [<n> ...]         PNG of individual slides (e.g. to place an archive slide into a new deck)
  collect "<query>" [--limit N]        write a candidate list with previews into Obsidian: _Base/Collections/
  check   <new.pptx>                   render via LibreOffice, compare slide/page counts and text, find objects
                                       off the slide, slides without notes; returns a contact sheet to inspect

QUERY
  Words of 6+ letters match by stem ("seconds" -> "secon*", "секунды" -> "секун*"). "exact phrase".
  OR / NOT / parentheses use SQLite FTS5 syntax; implicit AND after a parenthesis is added for you.

FILES (all inside <root>/_ai/, originals are never modified)
  slides.sqlite3   slide index (one row per PPTX slide / PDF page / document)
  kb_out/          results of every call (see above)
  previews/ sheets/ pdf_cache/
  kb_config.json   optional: {"private": ["Contracts", "Personal/ID"], "soffice": "C:/.../soffice.com"}
OCR text is taken from _ai/kb.sqlite3 if tools/ocr.py has been run (scans, pictures inside slides).
Requires: python-pptx, PyMuPDF, Pillow. LibreOffice for rendering PPTX without a PDF twin and for `check`.
"""
import argparse, datetime, hashlib, json, os, re, shutil, sqlite3, subprocess, sys, tempfile, time, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass
try:
    import fitz
    fitz.TOOLS.mupdf_display_errors(False)
    fitz.TOOLS.mupdf_display_warnings(False)
except Exception:
    fitz = None

EXT = {".pptx", ".potx", ".pdf", ".docx", ".txt", ".md"}
SKIP_TOP = {"_ai", "_Base", ".obsidian", ".git", ".trash"}
OPS = {"AND", "OR", "NOT", "NEAR"}
TEXT_MODE = False
ROOT = AI = DB = None
CFG = {}


KEEP_FILES = 300
CALL = {}


# ------------------------------------------------------------------ output
def summary(obj):
    if "error" in obj:
        return f"ERROR: {obj['error']}"
    parts = [f"{k}={len(obj[k])}" for k in ("hits", "slides", "decks", "cells", "issues") if isinstance(obj.get(k), list)]
    parts += [f"{k}={str(obj[k])[:80]}" for k in ("matches", "total", "count", "items", "note", "processed", "units")
              if k in obj and not isinstance(obj[k], (list, dict))]
    parts += [f"{k}=yes" for k in ("sheet", "png") if obj.get(k)]
    return ", ".join(parts) or "ok"


def emit(obj):
    """Save the result to <root>/_ai/kb_out/<time>_<command>.json (+ last.json, history.jsonl).
    The console gets one line: file path | summary. The agent reads the file with its Read tool."""
    if TEXT_MODE or CALL.get("stdout") or AI is None:
        print(to_text(obj) if TEXT_MODE else json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
        return
    out_dir = AI / "kb_out"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
    data = json.dumps(dict(command=CALL.get("cmd"), args=CALL.get("args"), at=ts, **obj), ensure_ascii=False, indent=1)
    f = out_dir / f"{ts}_{CALL.get('cmd', 'kb')}.json"
    f.write_text(data, encoding="utf-8")
    (out_dir / "last.json").write_text(data, encoding="utf-8")
    with (out_dir / "history.jsonl").open("a", encoding="utf-8") as h:
        h.write(json.dumps(dict(at=ts, command=CALL.get("cmd"), args=CALL.get("args"), file=f.name, summary=summary(obj)),
                           ensure_ascii=False) + "\n")
    for old in sorted(out_dir.glob("2*_*.json"))[:-KEEP_FILES]:
        old.unlink(missing_ok=True)
    print(f"{f}  |  {summary(obj)}")


def fail(msg):
    emit({"error": msg})
    sys.exit(1)


def to_text(o, ind=0):
    pad = "  " * ind
    if isinstance(o, dict):
        return "\n".join(f"{pad}{k}: " + (("\n" + to_text(v, ind + 1)) if isinstance(v, (dict, list)) and v else str(v)) for k, v in o.items())
    if isinstance(o, list):
        return "\n".join(to_text(x, ind) for x in o)
    return pad + str(o)


def norm_path(p):
    p = p.replace("\\", "/")
    if os.path.isabs(p):
        try:
            p = Path(p).resolve().relative_to(ROOT).as_posix()
        except ValueError:
            pass
    return p.lstrip("./")


def connect(must_exist=True):
    if must_exist and not DB.exists():
        fail("No index yet. Run: python tools/kb.py --root <folder> update")
    return sqlite3.connect(DB)


# ------------------------------------------------------------------ indexing
def clean(s):
    s = (s or "").replace("\x0b", "\n").replace("\r", "")
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n", s).strip()


def ocr_ok(t, limit=1500):
    """Drop OCR noise: keep text only if it is mostly real words."""
    t = clean(t)
    toks = t.split()
    good = [w for w in toks if len(w) >= 3 and re.fullmatch(r"[^\W\d_][^\W\d_\-]+[.,:;!?»)]?", w)]
    return t[:limit] if len(good) >= 3 and len(good) / max(len(toks), 1) >= 0.5 else ""


def lang_of(t):
    c, l = len(re.findall(r"[а-яё]", t.lower())), len(re.findall(r"[a-z]", t.lower()))
    if not c and not l:
        return ""
    return "en" if l > c * 2 else "ru" if c > l * 2 else "mix"


def chash(t):
    n = re.sub(r"\W+", "", t.lower())
    return hashlib.md5(n.encode()).hexdigest()[:16] if len(n) > 15 else ""


def shapes_text(shapes, titles):
    out = []
    for sh in shapes:
        try:
            if sh.is_placeholder and sh.placeholder_format.type in (1, 3) and sh.text_frame.text.strip():
                titles.append(sh.text_frame.text.strip())
        except Exception:
            pass
        if sh.has_text_frame:
            out += [p.text for p in sh.text_frame.paragraphs if p.text.strip()]
        if getattr(sh, "has_table", False) and sh.has_table:
            out += [" | ".join(c.text.replace("\n", " / ") for c in row.cells) for row in sh.table.rows]
        if sh.shape_type == 6:
            out += shapes_text(sh.shapes, titles)
    return out


def extract(p):
    ext = p.suffix.lower()
    if ext in (".pptx", ".potx"):
        from pptx import Presentation
        rows = []
        for i, s in enumerate(Presentation(p).slides, 1):
            titles = []
            text = clean("\n".join(shapes_text(s.shapes, titles)))
            notes = ""
            try:
                if s.has_notes_slide and s.notes_slide.notes_text_frame is not None:
                    notes = clean(s.notes_slide.notes_text_frame.text)
            except Exception:
                pass
            rows.append(("slide", i, titles[0] if titles else (text.split("\n")[0] if text else ""), text, notes))
        return rows
    if ext == ".pdf":
        with fitz.open(p) as d:
            return [("page", i, clean(pg.get_text()).split("\n")[0], clean(pg.get_text()), "") for i, pg in enumerate(d, 1)]
    if ext == ".docx":
        with zipfile.ZipFile(p) as z:
            root = ET.fromstring(z.read("word/document.xml"))
        paras = ["".join(x.text or "" for x in q.iter() if x.tag.endswith("}t")) for q in root.iter() if q.tag.endswith("}p")]
        t = clean("\n".join(x for x in paras if x.strip()))
        return [("document", 1, t.split("\n")[0] if t else "", t[:200000], "")]
    raw = p.read_bytes()
    for enc in ("utf-8-sig", "utf-16", "cp1251", "latin-1"):
        try:
            t = clean(raw.decode(enc))
            break
        except UnicodeError:
            continue
    return [("document", 1, t.split("\n")[0] if t else "", t[:200000], "")]


def cmd_update(a):
    private = tuple(x.strip("/") for x in CFG.get("private", []))
    c = connect(False)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, mtime REAL, size INTEGER, units INTEGER, error TEXT);
    CREATE TABLE IF NOT EXISTS slides(path TEXT, kind TEXT, number INTEGER, title TEXT, text TEXT, notes TEXT,
        ocr TEXT, lang TEXT, chash TEXT, PRIMARY KEY(path, kind, number));""")
    if a.full:
        c.executescript("DELETE FROM files; DELETE FROM slides;")
    disk = {}
    for r, ds, fs in os.walk(ROOT):
        rel = Path(r).relative_to(ROOT).as_posix()
        if rel == ".":
            ds[:] = [d for d in ds if d not in SKIP_TOP and not d.startswith(".")]
        ds[:] = [d for d in ds if not d.endswith("_files")]
        for f in fs:
            p = f if rel == "." else f"{rel}/{f}"
            if not f.startswith("~$") and Path(f).suffix.lower() in EXT and not (private and p.startswith(private)):
                st = os.stat(os.path.join(r, f))
                disk[p] = (st.st_mtime, st.st_size)
    known = {p: (m, s) for p, m, s in c.execute("SELECT path, mtime, size FROM files")}
    gone = [p for p in known if p not in disk]
    todo = sorted(p for p in disk if known.get(p) != disk[p])
    for p in gone + todo:
        c.execute("DELETE FROM slides WHERE path=?", (p,))
        c.execute("DELETE FROM files WHERE path=?", (p,))

    ocr_slide, ocr_page = {}, {}
    ocr_db = AI / "kb.sqlite3"  # written by tools/build_knowledge_base.py + tools/ocr.py
    if ocr_db.exists() and todo:
        b = sqlite3.connect(f"file:{ocr_db.as_posix()}?mode=ro", uri=True, timeout=60)
        want = set(todo)
        try:
            for path, num, text in b.execute("SELECT path, number, text FROM ocr WHERE error IS NULL AND kind='page'"):
                if path in want and text:
                    ocr_page.setdefault((path, int(num)), []).append(text)
            for path, slide, text in b.execute("""SELECT s.path, s.slide, o.text FROM slide_images s JOIN ocr o
                    ON o.path=s.path AND o.kind='pptx_image' AND o.number=s.media WHERE o.error IS NULL"""):
                if path in want and text:
                    ocr_slide.setdefault((path, slide), []).append(text)
        except sqlite3.OperationalError:
            pass
        b.close()

    t0 = time.time()
    for i, p in enumerate(todo, 1):
        rows, err = [], None
        try:
            rows = extract(ROOT / p)
        except Exception as e:
            err = f"{type(e).__name__}: {e}"[:300]
        for kind, num, title, text, notes in rows:
            src = ocr_slide.get((p, num), [])[:4] if kind == "slide" else ocr_page.get((p, num), []) if kind == "page" else []
            ocr = "\n".join(dict.fromkeys(x for x in (ocr_ok(s) for s in src) if x))
            if not title and ocr:
                title = ocr.split("\n")[0]
            title = re.sub(r"\s+", " ", clean(title))[:150]
            c.execute("INSERT OR REPLACE INTO slides VALUES (?,?,?,?,?,?,?,?,?)",
                      (p, kind, num, title, text, notes, ocr, lang_of(f"{text} {notes}" if text or notes else ocr), chash(text or ocr)))
        c.execute("INSERT OR REPLACE INTO files VALUES (?,?,?,?,?)", (p, *disk[p], len(rows), err))
        if i % 20 == 0:
            c.commit()
            print(f"{i}/{len(todo)} {time.time() - t0:.0f}s {p}", file=sys.stderr, flush=True)
    c.commit()
    c.executescript("""
    DROP TABLE IF EXISTS fts;
    CREATE VIRTUAL TABLE fts USING fts5(path UNINDEXED, kind UNINDEXED, number UNINDEXED,
        filename, title, text, notes, ocr, tokenize="unicode61 remove_diacritics 2", prefix='3 5');
    INSERT INTO fts SELECT path, kind, number, replace(replace(path,'_',' '),'/',' '), title, text, notes, ocr FROM slides;""")
    c.commit()
    n = c.execute("SELECT count(*), count(DISTINCT path) FROM slides").fetchone()
    emit({"files_on_disk": len(disk), "processed": len(todo), "removed": len(gone), "units": n[0], "indexed_files": n[1],
          "seconds": round(time.time() - t0, 1), "index": str(DB)})


# ------------------------------------------------------------------ query + rendering
def build_query(q, exact):
    if exact or '"' in q:
        return q
    out = []
    for tok in re.findall(r"\(|\)|[^\s()]+", q):
        if tok in OPS or tok in "()":
            out.append(tok)
            continue
        w = re.sub(r"[^\w\-]", "", tok)
        if not w:
            continue
        out.append(f'"{w}"' if "-" in w else w[: max(4, len(w) - 2)] + "*" if len(w) >= 6 and not w.isdigit() else w)
    res = []
    for tok in out:  # FTS5 rejects implicit AND after ')'
        if res and tok not in OPS and tok != ")" and res[-1] not in OPS and res[-1] != "(":
            res.append("AND")
        res.append(tok)
    return " ".join(res)


def fts(c, sql, args):
    try:
        return c.execute(sql, args).fetchall()
    except sqlite3.OperationalError as e:
        fail(f"FTS query «{args[0]}»: {e}. Simplify: words, \"phrases\", OR, parentheses.")


RANK = "bm25(fts, 0,0,0, 2.0,6.0,3.0,1.5,1.0)"  # filename, title, text, notes, ocr


def ranked(c, query, exact, extra_sql="", extra_args=(), limit=15):
    fq = build_query(query, exact)
    rows = fts(c, f"""SELECT f.path, f.kind, f.number, s.title, s.lang, s.chash, snippet(fts, -1, '[', ']', '…', 18),
                        length(coalesce(s.text,''))<10 AND length(s.ocr)>0
                      FROM fts f JOIN slides s ON s.path=f.path AND s.kind=f.kind AND s.number=f.number
                      WHERE fts MATCH ? {extra_sql} ORDER BY {RANK} LIMIT ?""", [fq, *extra_args, limit * 8])
    groups, order = {}, []
    for path, kind, num, title, lang, ch, snip, ocr_only in rows:
        k = ch or f"{path}#{num}"
        if k in groups:
            groups[k]["also"].append(f"{path}#{num}")
            continue
        groups[k] = dict(path=path, n=num, kind=kind, title=title or "", lang=lang,
                         snippet=" ".join(snip.split())[:300], ocr_only=bool(ocr_only), also=[])
        order.append(k)
    hits = [groups[k] for k in order[:limit]]
    for h in hits:
        h["copies"] = len(h["also"]) + 1
        h["also"] = h["also"][:6]
        if not h["ocr_only"]:
            h.pop("ocr_only")
    return fq, len(rows), hits


def stem_key(p):
    return re.sub(r"[\s_+\-]+", " ", Path(p).stem.lower()).strip()


def n_units(c, path):
    return c.execute("SELECT max(number) FROM slides WHERE path=?", (path,)).fetchone()[0] or 0


def find_soffice():
    for cand in [CFG.get("soffice"), os.environ.get("SOFFICE"), shutil.which("soffice"), shutil.which("soffice.com"),
                 r"C:\Program Files\LibreOffice\program\soffice.com", "/Applications/LibreOffice.app/Contents/MacOS/soffice"]:
        if cand and Path(cand).exists():
            return cand
    raise RuntimeError("LibreOffice not found: set SOFFICE or \"soffice\" in _ai/kb_config.json")


def convert_pdf(src):
    src = Path(src)
    cache = AI / "pdf_cache"
    cache.mkdir(exist_ok=True)
    pdf = cache / f"{hashlib.md5(f'{src}|{src.stat().st_mtime}'.encode()).hexdigest()[:16]}.pdf"
    if not pdf.exists():
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([find_soffice(), f"-env:UserInstallation={Path(tmp, 'profile').as_uri()}", "--headless",
                            "--convert-to", "pdf", "--outdir", tmp, str(src)], capture_output=True, timeout=900)
            made = list(Path(tmp).glob("*.pdf"))
            if not made:
                raise RuntimeError("LibreOffice could not convert the file")
            shutil.move(str(made[0]), pdf)
    return pdf


def pdf_for(c, path):
    """The file itself if PDF; else a PDF twin (same folder, same name, same page count); else a LibreOffice render."""
    if path.lower().endswith(".pdf"):
        return ROOT / path
    parent, stem, n = Path(path).parent.as_posix(), stem_key(path), n_units(c, path)
    for (cand,) in c.execute("SELECT path FROM files WHERE lower(path) LIKE '%.pdf'"):
        if Path(cand).parent.as_posix() == parent and stem_key(cand) == stem and n_units(c, cand) == n:
            return ROOT / cand
    return convert_pdf(ROOT / path)


def render(c, path, numbers, width=960):
    out_dir = AI / "previews"
    out_dir.mkdir(exist_ok=True)
    h = hashlib.md5(path.encode()).hexdigest()[:10]
    out = {n: out_dir / f"{h}_{n:03}_{width}.png" for n in numbers}
    missing = [n for n, p in out.items() if not p.exists()]
    if missing:
        with fitz.open(pdf_for(c, path)) as d:
            for n in missing:
                if 1 <= n <= len(d):
                    pg = d[n - 1]
                    z = width / max(pg.rect.width, 1)
                    pg.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False).save(out[n])
    return {n: p for n, p in out.items() if p.exists()}


def contact_sheet(items, name, cols=4, cell=480):
    from PIL import Image, ImageDraw, ImageFont
    if not items:
        return None
    ims = []
    for p, label in items:
        im = Image.open(p).convert("RGB")
        im.thumbnail((cell, cell))
        ims.append((im, label))
    ch = max(i.height for i, _ in ims) + 28
    sheet = Image.new("RGB", (cols * (cell + 8) + 8, ((len(ims) + cols - 1) // cols) * (ch + 8) + 8), "white")
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
    for k, (im, label) in enumerate(ims):
        x, y = 8 + (k % cols) * (cell + 8), 8 + (k // cols) * (ch + 8)
        d.rectangle([x - 1, y - 1, x + im.width, y + im.height], outline="#999")
        sheet.paste(im, (x, y))
        d.text((x + 2, y + im.height + 4), label[:60], fill="black", font=font)
    out_dir = AI / "sheets"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{re.sub(r'[^\w\-]+', '_', name)[:60]}_{hashlib.md5(name.encode()).hexdigest()[:6]}.png"
    sheet.save(out)
    return out


# ------------------------------------------------------------------ commands
def cmd_stats(a):
    c = connect()
    emit({
        "root": str(ROOT), "files": c.execute("SELECT count(*) FROM files").fetchone()[0],
        "units": dict(c.execute("SELECT kind, count(*) FROM slides GROUP BY kind")),
        "units_by_lang": dict(c.execute("SELECT coalesce(nullif(lang,''),'none'), count(*) FROM slides GROUP BY 1")),
        "units_with_text": c.execute("SELECT count(*) FROM slides WHERE chash!=''").fetchone()[0],
        "unique_slide_texts": c.execute("SELECT count(DISTINCT chash) FROM slides WHERE chash!=''").fetchone()[0],
        "text_only_in_ocr": c.execute("SELECT count(*) FROM slides WHERE length(coalesce(text,''))<10 AND length(ocr)>30").fetchone()[0],
        "with_speaker_notes": c.execute("SELECT count(*) FROM slides WHERE length(notes)>10").fetchone()[0],
        "read_errors": [dict(path=p, error=e) for p, e in c.execute("SELECT path, error FROM files WHERE error IS NOT NULL")][:20],
        "index_modified": datetime.datetime.fromtimestamp(DB.stat().st_mtime).isoformat(timespec="minutes"),
    })


def filters(a):
    sql, args = "", []
    for cond, val in (("s.lang=?", getattr(a, "lang", None)), ("f.path LIKE ?", a.folder and f"%{a.folder}%"),
                      ("lower(f.path) LIKE ?", getattr(a, "type", None) and f"%.{a.type}")):
        if val:
            sql += f" AND {cond}"
            args.append(val)
    return sql, args


def cmd_search(a):
    c = connect()
    sql, args = filters(a)
    fq, matches, hits = ranked(c, a.query, a.exact, sql, args, a.limit)
    emit({"query": fq, "matches": matches, "hits": hits,
          "hint": None if hits else "Nothing found: try synonyms, the other language, fewer words, OR."})


def cmd_show(a):
    c = connect()
    path = norm_path(a.path)
    r = c.execute("SELECT kind,title,text,notes,ocr,lang FROM slides WHERE path=? AND number=?", (path, a.n)).fetchone()
    if not r:
        fail(f"{path} #{a.n} is not in the index")
    out = dict(path=path, n=a.n, kind=r[0], total=n_units(c, path), lang=r[5], title=r[1], text=r[2], notes=r[3] or None, ocr=r[4] or None)
    if not a.no_png:
        try:
            out["png"] = str(render(c, path, [a.n]).get(a.n))
        except Exception as e:
            out["png_error"] = str(e)
    emit(out)


def cmd_outline(a):
    c = connect()
    path = norm_path(a.path)
    rows = c.execute("SELECT number, title, length(text), length(ocr), length(notes) FROM slides WHERE path=? ORDER BY number", (path,)).fetchall()
    if not rows:
        fail(f"{path} is not in the index")
    emit({"path": path, "total": len(rows), "slides": [
        [n, (t or "")[:90] + ("" if (tl or 0) > 10 else " (text only in OCR)" if (ol or 0) > 10 else " (empty)") + (" [notes]" if (nl or 0) > 10 else "")]
        for n, t, tl, ol, nl in rows[: a.max]]})


def cmd_decks(a):
    c = connect()
    sql = """SELECT f.path, f.units, f.mtime, (SELECT title FROM slides s WHERE s.path=f.path ORDER BY number LIMIT 1),
                    (SELECT lang FROM slides s WHERE s.path=f.path GROUP BY lang ORDER BY count(*) DESC LIMIT 1)
             FROM files f WHERE (lower(f.path) LIKE '%.pptx' OR lower(f.path) LIKE '%.pdf')"""
    args = []
    if a.folder:
        sql += " AND f.path LIKE ?"
        args.append(f"%{a.folder}%")
    if a.q:
        sql += " AND (f.path LIKE ? OR f.path IN (SELECT path FROM slides WHERE number<=2 AND title LIKE ?))"
        args += [f"%{a.q}%", f"%{a.q}%"]
    rows = c.execute(sql + " ORDER BY f.mtime DESC", args).fetchall()
    emit({"count": len(rows), "decks": [dict(path=p, units=u, modified=datetime.date.fromtimestamp(m).isoformat(), lang=l, first=(t or "")[:80])
                                         for p, u, m, t, l in rows[: a.limit]]})


def cmd_preview(a):
    c = connect()
    path = norm_path(a.path)
    try:
        emit({"path": path, "png": {str(k): str(v) for k, v in render(c, path, a.n, a.width).items()}})
    except Exception as e:
        fail(str(e))


def cmd_sheet(a):
    c = connect()
    items = []
    if a.hits:
        sql, args = filters(a)
        _, _, hits = ranked(c, a.hits, False, sql + " AND f.kind IN ('slide','page')", args, a.limit)
        for h in hits:
            try:
                png = render(c, h["path"], [h["n"]]).get(h["n"])
            except Exception:
                png = None
            if png:
                items.append((png, f"{len(items) + 1}. {Path(h['path']).name[:40]} #{h['n']}", h["path"], h["n"]))
        name = "hits_" + a.hits
    else:
        if not a.path:
            fail("Give a deck path or --hits \"query\"")
        path = norm_path(a.path)
        total = n_units(c, path)
        if not total:
            fail(f"{path} is not in the index")
        lo = a.from_ or 1
        hi = min(a.to or total, lo + 39)
        try:
            pngs = render(c, path, list(range(lo, hi + 1)), 480)
        except Exception as e:
            fail(str(e))
        items = [(p, f"#{n}", path, n) for n, p in sorted(pngs.items())]
        name = f"{Path(path).stem}_{lo}-{hi}"
    sheet = contact_sheet([(p, l) for p, l, *_ in items], name, cols=a.cols)
    emit({"sheet": str(sheet) if sheet else None, "cells": [dict(label=l, path=p, n=n) for _, l, p, n in items],
          "note": "Open `sheet` with your image/Read tool to see the slides (max 40 per sheet; use --from/--to)."})


def cmd_collect(a):
    c = connect()
    _, _, hits = ranked(c, a.query, a.exact, limit=a.limit)
    title = re.sub(r'[\\/:*?"<>|#^\[\]]', " ", a.query).strip()[:80]
    note = ROOT / "_Base" / "Collections" / f"Collection — {title}.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    L = ["---", "type: collection", f'query: "{a.query}"', f"created: {datetime.date.today()}", "auto: false", "---", "",
         f"# Collection: {a.query}", "", "Candidate slides for a new talk. Tick the ones to use.", ""]
    for i, h in enumerate(hits, 1):
        where = {"slide": "slide", "page": "page"}.get(h["kind"], "doc")
        link = f"`{h['path']}`" if re.search(r"[#^\[\]|]", h["path"]) else f"[[{h['path']}|{Path(h['path']).name}]]"
        L += [f"## {i}. {h['title'][:90] or Path(h['path']).name}", "",
              f"- [ ] use · {link} · **{where} {h['n']}**" + (f" · {h['lang']}" if h["lang"] else ""), f"- {h['snippet']}"]
        if h["also"]:
            L.append(f"- also in: {'; '.join(h['also'][:5])}")
        if h["kind"] in ("slide", "page") and not a.no_png:
            try:
                png = render(c, h["path"], [h["n"]]).get(h["n"])
                if png:
                    L.append(f"\n![[{png.relative_to(ROOT).as_posix()}|480]]")
            except Exception:
                pass
        L.append("")
    note.write_text("\n".join(L), encoding="utf-8")
    emit({"note": note.relative_to(ROOT).as_posix(), "items": len(hits)})


def cmd_check(a):
    from pptx import Presentation
    src = Path(a.pptx).resolve()
    if not src.exists():
        fail(f"No such file: {src}")
    try:
        pdf = convert_pdf(src)
    except Exception as e:
        fail(str(e))
    pres, issues, cells = Presentation(src), [], []
    out_dir = AI / "previews"
    out_dir.mkdir(exist_ok=True)
    h = hashlib.md5(str(src).encode()).hexdigest()[:8]
    with fitz.open(pdf) as d:
        if len(d) != len(pres.slides):
            issues.append(f"{len(pres.slides)} slides but {len(d)} PDF pages")
        for i, (s, pg) in enumerate(zip(pres.slides, d), 1):
            page_text = re.sub(r"\W+", "", pg.get_text().lower())
            for sh in s.shapes:
                if sh.has_text_frame:
                    for p in sh.text_frame.paragraphs:
                        t = re.sub(r"\W+", "", p.text.lower())
                        if len(t) > 3 and t not in page_text:
                            issues.append(f"#{i}: text not rendered: {p.text[:50]}")
                if sh.left is not None and sh.width is not None and (
                        sh.left + sh.width > pres.slide_width * 1.01 or sh.top + sh.height > pres.slide_height * 1.01):
                    issues.append(f"#{i}: object goes off the slide: {sh.name}")
            if not (s.has_notes_slide and s.notes_slide.notes_text_frame.text.strip()):
                issues.append(f"#{i}: no speaker notes")
            if i <= 60:
                png = out_dir / f"check_{h}_{i:03}.png"
                pg.get_pixmap(matrix=fitz.Matrix(480 / pg.rect.width, 480 / pg.rect.width), alpha=False).save(png)
                cells.append((png, f"#{i}"))
    emit({"pptx": str(src), "pdf": str(pdf), "slides": len(pres.slides), "issues": issues[:80],
          "sheet": str(contact_sheet(cells, f"check_{src.stem}")),
          "next": "Open `sheet` and inspect every slide. LibreOffice rendering is not PowerPoint."})


def main():
    global TEXT_MODE, ROOT, AI, DB, CFG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.environ.get("KB_ROOT", "."), help="speaker folder (default: KB_ROOT or current dir)")
    ap.add_argument("--text", action="store_true", help="human-readable output to the console (no file)")
    ap.add_argument("--stdout", action="store_true", help="full JSON to the console instead of a file")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("update"); p.add_argument("--full", action="store_true")
    sp.add_parser("stats")
    p = sp.add_parser("search"); p.add_argument("query"); p.add_argument("--lang", choices=["ru", "en", "mix"])
    p.add_argument("--folder"); p.add_argument("--type", choices=["pptx", "pdf", "docx"])
    p.add_argument("--limit", type=int, default=15); p.add_argument("--exact", action="store_true")
    p = sp.add_parser("show"); p.add_argument("path"); p.add_argument("n", type=int); p.add_argument("--no-png", action="store_true")
    p = sp.add_parser("outline"); p.add_argument("path"); p.add_argument("--max", type=int, default=200)
    p = sp.add_parser("decks"); p.add_argument("--folder"); p.add_argument("--q"); p.add_argument("--limit", type=int, default=100)
    p = sp.add_parser("preview"); p.add_argument("path"); p.add_argument("n", nargs="+", type=int); p.add_argument("--width", type=int, default=960)
    p = sp.add_parser("sheet"); p.add_argument("path", nargs="?"); p.add_argument("--from", dest="from_", type=int)
    p.add_argument("--to", type=int); p.add_argument("--hits"); p.add_argument("--lang", choices=["ru", "en", "mix"])
    p.add_argument("--folder"); p.add_argument("--limit", type=int, default=12); p.add_argument("--cols", type=int, default=4)
    p = sp.add_parser("collect"); p.add_argument("query"); p.add_argument("--limit", type=int, default=15)
    p.add_argument("--exact", action="store_true"); p.add_argument("--no-png", action="store_true")
    p = sp.add_parser("check"); p.add_argument("pptx")
    a = ap.parse_args()
    TEXT_MODE = a.text
    CALL.update(cmd=a.cmd, stdout=a.stdout,
                args={k: v for k, v in vars(a).items() if k not in ("cmd", "text", "stdout", "root") and v not in (None, False)})
    ROOT = Path(a.root).resolve()
    if not ROOT.is_dir():
        fail(f"Root folder not found: {ROOT}")
    AI = ROOT / "_ai"
    AI.mkdir(exist_ok=True)
    DB = AI / "slides.sqlite3"
    cfg = AI / "kb_config.json"
    CFG = json.loads(cfg.read_text(encoding="utf-8")) if cfg.exists() else {}
    if fitz is None:
        fail("PyMuPDF is not installed: pip install -r tools/requirements.txt")
    globals()["cmd_" + a.cmd](a)


if __name__ == "__main__":
    main()
