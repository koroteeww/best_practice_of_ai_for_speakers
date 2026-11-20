"""
Render a PPTX to PDF with LibreOffice and run basic checks:
slide count == page count, every slide's text appears in the PDF, PNG previews for visual review.

    python tools/check_render.py talk.pptx [--soffice "C:/Program Files/LibreOffice/program/soffice.com"]

This proves static rendering in LibreOffice, NOT PowerPoint compatibility. Still look at every PNG yourself.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path


def find_soffice(explicit):
    for c in [explicit, os.environ.get("SOFFICE"), shutil.which("soffice"), shutil.which("soffice.com"),
              r"C:\Program Files\LibreOffice\program\soffice.com", "/Applications/LibreOffice.app/Contents/MacOS/soffice"]:
        if c and Path(c).exists():
            return c
    sys.exit("LibreOffice not found. Install it or pass --soffice PATH.")


def norm(s):
    return re.sub(r"\W+", "", s.lower())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pptx")
    ap.add_argument("--soffice")
    ap.add_argument("--out", help="folder for PDF and PNG previews (default: <pptx>_check)")
    a = ap.parse_args()
    import fitz
    from pptx import Presentation

    src = Path(a.pptx).resolve()
    out = Path(a.out) if a.out else src.with_name(src.stem + "_check")
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        r = subprocess.run([find_soffice(a.soffice), f"-env:UserInstallation={Path(profile).as_uri()}",
                            "--headless", "--convert-to", "pdf", "--outdir", str(out), str(src)],
                           capture_output=True, timeout=300)
    pdf = out / (src.stem + ".pdf")
    if r.returncode or not pdf.exists():
        sys.exit("Export failed: " + (r.stdout + r.stderr).decode("utf-8", "replace"))

    pres = Presentation(src)
    problems = []
    with fitz.open(pdf) as doc:
        if len(doc) != len(pres.slides):
            problems.append(f"slide count {len(pres.slides)} != PDF pages {len(doc)}")
        for i, (slide, page) in enumerate(zip(pres.slides, doc), 1):
            page_text = norm(page.get_text())
            for sh in slide.shapes:
                if sh.has_text_frame:
                    for p in sh.text_frame.paragraphs:
                        t = norm(p.text)
                        if len(t) > 3 and t not in page_text:
                            problems.append(f"slide {i}: text not found in render: {p.text[:60]!r}")
            page.get_pixmap(matrix=fitz.Matrix(1, 1)).save(out / f"slide_{i:02}.png")
            if not slide.has_notes_slide or not slide.notes_slide.notes_text_frame.text.strip():
                problems.append(f"slide {i}: no speaker notes")
    print(f"PDF and PNG previews: {out}")
    if problems:
        print("Check these:")
        for p in problems:
            print("  -", p)
    else:
        print("PASS: counts match, all text rendered, all slides have notes. Now LOOK at every PNG.")


if __name__ == "__main__":
    main()
