"""
Build a styled, editable 16:9 PPTX from a Markdown talk script.

    python examples/build_deck.py examples/example_script.md -o examples/out/example.pptx

- One "### " section = one slide; "> " lines = speaker notes (you rehearse from the same file).
- Layouts: title, statement, big-number, cards, two-columns, image (see example_script.md).
- All text stays editable; pictures get alt text; every slide gets a header, footer and number.
- Dark stage theme: near-black background, white text, one amber accent. Change THEME below.

Generalised from a real screencast build. After building, render and look:
    python tools/check_render.py examples/out/example.pptx
"""
import argparse, io, re
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

THEME = dict(bg="12131B", card="1D202C", line="363A4A", ink="FFFFFF", muted="C4C8D4", accent="FFBE62", font="Segoe UI")


def rgb(h):
    return RGBColor.from_string(h)


class Deck:
    def __init__(self, meta, total):
        self.p = Presentation()
        self.p.slide_width, self.p.slide_height = Inches(13.333), Inches(7.5)
        cp = self.p.core_properties
        cp.title, cp.author, cp.subject = meta.get("title", ""), meta.get("author", ""), meta.get("subtitle", "")
        self.footer, self.total = meta.get("footer", meta.get("author", "")), total

    def text(self, s, content, x, y, w, h, size=22, ink=None, bold=False):
        box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        for i, row in enumerate(content.replace("\\n", "\n").split("\n")):
            para = tf.add_paragraph() if i else tf.paragraphs[0]
            para.line_spacing = 1.08
            run = para.add_run()
            run.text = row
            f = run.font
            f.name, f.size, f.bold, f.color.rgb = THEME["font"], Pt(size), bold, rgb(ink or THEME["ink"])
        return box

    def panel(self, s, x, y, w, h, color=None):
        sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(color or THEME["card"])
        sh.line.fill.background()
        return sh

    def image(self, s, path, x, y, w, h, alt):
        from PIL import Image
        data = Path(path).read_bytes()
        with Image.open(io.BytesIO(data)) as im:
            iw, ih = im.size
        k = min(w / iw, h / ih)
        pic = s.shapes.add_picture(io.BytesIO(data), Inches(x + (w - iw * k) / 2), Inches(y + (h - ih * k) / 2),
                                   Inches(iw * k), Inches(ih * k))
        pic._element.nvPicPr.cNvPr.set("descr", alt or "")  # alt text for accessibility
        return pic

    def slide(self, f, notes):
        s = self.p.slides.add_slide(self.p.slide_layouts[6])
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = rgb(THEME["bg"])
        n = len(self.p.slides)
        if f.get("label"):
            self.text(s, f"{n:02}   /   {f['label']}", .62, .36, 12, .36, 13, THEME["accent"], True)
        self.panel(s, .62, 6.86, 12.08, .013, THEME["line"])
        self.text(s, self.footer, .62, 7.01, 10.8, .26, 10, THEME["muted"])
        self.text(s, f"{n:02} / {self.total:02}", 11.86, 7.01, .85, .26, 10, THEME["muted"])
        if f.get("caption"):
            self.text(s, f["caption"], .67, 6.28, 12, .34, 13, THEME["muted"])
        s.notes_slide.notes_text_frame.text = notes
        return s

    # ---- layouts -------------------------------------------------------
    def title(self, s, f, base):
        self.text(s, f.get("heading", ""), .60, 1.18, 7.6, .9, 46, bold=True)
        if f.get("accent"):
            self.text(s, f["accent"], .57, 2.07, 7.6, 1.15, 69, THEME["accent"], True)
        self.text(s, f.get("text", ""), .60, 3.23, 7.4, 1.7, 40, bold=True)
        if f.get("image"):
            self.image(s, base / f["image"], 8.08, 1.18, 4.59, 4.93, f.get("alt", ""))

    def statement(self, s, f, base):
        self.text(s, f.get("heading", ""), .62, 1.5, 12, 2.2, 50, bold=True)
        self.text(s, f.get("text", ""), .65, 4.1, 11.5, 1.6, 28, THEME["muted"])

    def big_number(self, s, f, base):
        self.text(s, f.get("heading", ""), .60, .88, 12.1, 1.0, 36, bold=True)
        self.text(s, f.get("number", ""), .62, 2.1, 7, 1.6, 110, THEME["accent"], True)
        self.text(s, f.get("text", ""), .70, 4.05, 11, .7, 32, bold=True)

    def cards(self, s, f, base):
        self.text(s, f.get("heading", ""), .60, .88, 12.1, 1.0, 36, bold=True)
        items = f["items"][:4] or [("", "")]
        w = (12.08 - .14 * (len(items) - 1)) / len(items)
        size = 40 if max(len(t) for t, _ in items) < 9 else 28  # same size on every card
        for i, (t, b) in enumerate(items):
            x = .62 + i * (w + .14)
            self.panel(s, x, 2.3, w, 3.6)
            self.text(s, t, x + .24, 2.6, w - .45, 1.0, size, THEME["accent"], True)
            self.text(s, b, x + .24, 3.85, w - .45, 1.9, 20, THEME["muted"])

    def two_columns(self, s, f, base):
        self.text(s, f.get("heading", ""), .60, .88, 12.1, 1.0, 36, bold=True)
        for i, (t, b) in enumerate((f["items"] + [("", ""), ("", "")])[:2]):
            x = .62 + i * 6.12
            self.panel(s, x, 2.3, 5.94, 3.6)
            self.text(s, t, x + .28, 2.6, 5.4, .7, 30, THEME["accent"], True)
            self.text(s, b, x + .28, 3.5, 5.4, 2.2, 24)

    def image_layout(self, s, f, base):
        self.text(s, f.get("heading", ""), .60, .88, 12.1, 1.0, 36, bold=True)
        if f.get("image"):
            self.image(s, base / f["image"], .62, 2.0, 12.08, 4.1, f.get("alt", ""))


def parse(md):
    meta = {}
    m = re.match(r"---\n(.*?)\n---\n", md, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        md = md[m.end():]
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    slides = []
    for block in re.split(r"^### ", md, flags=re.M)[1:]:
        f, notes, items = {}, [], []
        for line in block.splitlines()[1:]:
            if line.startswith("> "):
                notes.append(line[2:].strip())
            elif line.startswith("- ") and "|" in line:
                a, b = line[2:].split("|", 1)
                items.append((a.strip(), b.strip().replace("\\n", "\n")))
            elif re.match(r"^[a-z]+: ", line):
                k, v = line.split(": ", 1)
                f[k] = v.strip()
        f["items"] = items
        slides.append((f, " ".join(notes)))
    return meta, slides


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script")
    ap.add_argument("-o", "--out", default="examples/out/deck.pptx")
    a = ap.parse_args()
    src = Path(a.script)
    meta, slides = parse(src.read_text(encoding="utf-8-sig"))
    deck = Deck(meta, len(slides))
    layouts = {"title": deck.title, "statement": deck.statement, "big-number": deck.big_number,
               "cards": deck.cards, "two-columns": deck.two_columns, "image": deck.image_layout}
    for f, notes in slides:
        s = deck.slide(f, notes)
        layouts.get(f.get("layout", "statement"), deck.statement)(s, f, src.parent)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    deck.p.save(out)
    print(f"{len(slides)} slides → {out}")


if __name__ == "__main__":
    main()
