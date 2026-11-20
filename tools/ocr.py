"""
Local OCR for scans and text inside images. Resumable, with a SHA-256 cache.

    python tools/ocr.py "D:/Talks" --lang eng+rus [--limit 200] [--tesseract "C:/Program Files/Tesseract-OCR/tesseract.exe"]

Order of work:
  1. PDF pages with almost no text layer (scans)
  2. standalone images
  3. pictures inside PPTX (ppt/media/*), linked to slides via the slide_images table

Run build_knowledge_base.py first. Results go to the `ocr` table of _ai/kb.sqlite3 and into the search index.
Nothing leaves your computer. Stop at any time (Ctrl+C) and run again to continue.
"""
import argparse, hashlib, io, os, shutil, sqlite3, subprocess, sys, zipfile
from pathlib import Path

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".jfif", ".bmp", ".tif", ".tiff", ".gif"}


def find_tesseract(explicit):
    for c in [explicit, os.environ.get("TESSERACT"), shutil.which("tesseract"),
              r"C:\Program Files\Tesseract-OCR\tesseract.exe"]:
        if c and Path(c).exists():
            return c
    sys.exit("Tesseract not found. Install it (https://github.com/tesseract-ocr/tesseract) or pass --tesseract PATH.")


def to_png(data):
    from PIL import Image, ImageOps
    with Image.open(io.BytesIO(data)) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((2200, 2200))
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        return buf.getvalue()


def tasks(root, db):
    for path, num in db.execute("""SELECT path, number FROM units WHERE kind='page' AND length(coalesce(text,'')) < 40
                                   ORDER BY path, number"""):
        yield "page", path, num
    for (path,) in db.execute("SELECT path FROM documents ORDER BY path"):
        if Path(path).suffix.lower() in IMG_EXT:
            yield "image", path, 0
    for (path,) in db.execute("SELECT DISTINCT path FROM slide_images ORDER BY path"):
        try:
            with zipfile.ZipFile(root / path) as z:
                for name in z.namelist():
                    if name.startswith("ppt/media/") and Path(name).suffix.lower() in IMG_EXT:
                        yield "pptx_image", path, name
        except (OSError, zipfile.BadZipFile):
            pass


def load(root, kind, path, num):
    if kind == "page":
        import fitz
        with fitz.open(root / path) as doc:
            return doc[int(num) - 1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).tobytes("png")
    if kind == "image":
        return to_png((root / path).read_bytes())
    with zipfile.ZipFile(root / path) as z:
        return to_png(z.read(num))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--lang", default="eng", help="Tesseract languages, e.g. eng+rus")
    ap.add_argument("--limit", type=int, default=0, help="stop after N new items (0 = all)")
    ap.add_argument("--tesseract")
    ap.add_argument("--tessdata", help="folder with *.traineddata (if Tesseract can't find its languages)")
    args = ap.parse_args()
    root = Path(args.folder).resolve()
    dbp = root / "_ai" / "kb.sqlite3"
    if not dbp.exists():
        sys.exit("Run build_knowledge_base.py first.")
    tess = find_tesseract(args.tesseract)
    db = sqlite3.connect(dbp)
    done = {r[0] for r in db.execute("SELECT source FROM ocr WHERE error IS NULL")}  # failed items are retried
    env = dict(os.environ, OMP_THREAD_LIMIT="1")
    extra = ["--tessdata-dir", args.tessdata] if args.tessdata else []
    count = errors = 0
    try:
        for kind, path, num in tasks(root, db):
            key = f"{kind}:{path}:{num}"
            if key in done:
                continue
            text, err, digest = "", None, None
            try:
                data = load(root, kind, path, num)
                digest = hashlib.sha256(data).hexdigest()
                cached = db.execute("SELECT text FROM ocr WHERE sha256=? AND error IS NULL LIMIT 1", (digest,)).fetchone()
                if cached:
                    text = cached[0]
                else:
                    p = subprocess.run([tess, "stdin", "stdout", *extra, "-l", args.lang, "--psm", "3"], input=data,
                                       capture_output=True, env=env, timeout=120)
                    if p.returncode:
                        raise RuntimeError(p.stderr.decode("utf-8", "replace")[:300])
                    text = p.stdout.decode("utf-8", "replace").strip()
            except Exception as e:
                err = f"{type(e).__name__}: {e}"[:300]
                errors += 1
                if errors <= 3:
                    print(f"OCR error on {path}: {err}", flush=True)
            db.execute("INSERT OR REPLACE INTO ocr VALUES (?,?,?,?,?,?,?)", (key, path, kind, str(num), text, err, digest))
            db.commit()
            count += 1
            if count % 10 == 0:
                print(f"OCR {count}: {path}", flush=True)
            if args.limit and count >= args.limit:
                break
    except KeyboardInterrupt:
        print("Interrupted; progress is saved.")
    sys.path.insert(0, str(Path(__file__).parent))
    from build_knowledge_base import rebuild_search
    rebuild_search(db)
    print(f"OCR: {count} items processed, {errors} errors; search index updated.")


if __name__ == "__main__":
    main()
