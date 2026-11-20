"""
Generate an Obsidian vault on top of your speaker folder.

    python tools/build_obsidian_vault.py "D:/Talks" [--config my_vault_config.json]

Prerequisite: tools/build_knowledge_base.py (and optionally tools/ocr.py).

The vault root is your folder itself. Originals are never moved; notes link to them.
All notes go to <folder>/_Base/:
  Decks/    one note per deck (PPTX and PDF with the same name are merged), full slide text, OCR in a callout
  Events/   one note per event folder (configurable), with decks, media and a debrief section
  Topics/   one note per topic, listing its events and decks
Static files (Home, templates, .base dashboards, .obsidian settings) are copied from vault-template/
only if they don't exist yet.

Re-running overwrites only notes whose frontmatter contains `auto: true`.
Set `auto: false` in a note you edit by hand, and it will be left alone.

Config (JSON, optional): see tools/vault_config.example.json
"""
import argparse, collections, json, re, shutil, sqlite3, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = "_Base"
IMG = {".jpg", ".jpeg", ".png", ".webp", ".jfif", ".gif", ".svg"}
VIDEO = {".mp4", ".mov", ".webm", ".mkv"}
AUDIO = {".mp3", ".wav", ".aac", ".m4a"}
DECK = {".pptx", ".ppt", ".pdf", ".docx"}

DEFAULT_TOPICS = {
    "AI for business": {"description": "Applied AI: productivity, marketing, sales, agents, RAG.",
                        "keywords": r"\bai\b|\bии\b|нейросет|gpt|llm|artificial intelligence|искусствен|agent|агент"},
    "Public speaking": {"description": "Delivery, storytelling, stage confidence, introverts on stage.",
                        "keywords": r"public speaking|публичн\w* выступ|speaker|спикер|introvert|интроверт|tedx|storytelling"},
    "Video and social media": {"description": "Short video, social platforms, personal brand.",
                               "keywords": r"tik ?tok|тикток|reels|shorts|youtube|social media|соцсет|продвижен"},
    "Career and education": {"description": "Careers, lectures for students and schools, teaching.",
                             "keywords": r"career|карьер|student|студент|school|школ|lecture|лекци"},
}


def safe(name, n=90):
    name = re.sub(r'[\\/:*?"<>|#^\[\]]', " ", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    return name[:n].strip() or "untitled"


BAD = re.compile(r"[#^\[\]|]")


def link_file(path, alias=None):
    alias = (alias or Path(path).name).replace("|", " ").replace("[", "(").replace("]", ")")
    return f"[{alias}](<{path}>)" if BAD.search(path) else f"[[{path}|{alias}]]"


def embed(path, width=180):
    return f"- {link_file(path)}" if BAD.search(path) else f"![[{path}|{width}]]"


def q(s):
    return '"' + str(s).replace("\\", "/").replace('"', "'") + '"'


def write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and "auto: true" not in p.read_text(encoding="utf-8")[:800]:
        return False
    p.write_text(text, encoding="utf-8", newline="\n")
    return True


def ocr_ok(t):
    t = re.sub(r"\s+\n", "\n", (t or "").replace("\r", "")).strip()
    toks = t.split()
    good = [w for w in toks if len(w) >= 3 and re.fullmatch(r"[^\W\d_][^\W\d_\-]+[.,:;!?»)]?", w)]
    if len(good) < 4 or len(good) / max(len(toks), 1) < 0.6:
        return ""
    return t[:700]


def lang_of(text):
    cyr = len(re.findall(r"[а-яё]", text.lower()))
    lat = len(re.findall(r"[a-z]", text.lower()))
    return "en" if lat > cyr * 1.5 else ("ru" if cyr else "")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--config", help="JSON with events / topics / private folders")
    ap.add_argument("--template", default=str(REPO / "vault-template"))
    a = ap.parse_args()
    root = Path(a.folder).resolve()
    dbp = root / "_ai" / "kb.sqlite3"
    if not dbp.exists():
        sys.exit("Run tools/build_knowledge_base.py first.")
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8")) if a.config else {}
    topics = cfg.get("topics") or DEFAULT_TOPICS
    private = tuple(cfg.get("private_folders", []))
    events = cfg.get("events", {})

    # copy static template files (never overwrite)
    tpl = Path(a.template)
    if tpl.exists():
        for src in tpl.rglob("*"):
            rel = src.relative_to(tpl)
            if src.is_file() and not src.name.startswith("Example") and not (
                    rel.parts[0] == BASE and len(rel.parts) > 1 and rel.parts[1] in ("Decks", "Events", "Topics")):
                dst = root / rel
                if not dst.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)

    db = sqlite3.connect(dbp)
    docs = {p: (ext, m) for p, ext, m in db.execute("SELECT path, extension, modified_utc FROM documents")}
    units = collections.defaultdict(list)
    for p, kind, num, text, notes in db.execute("SELECT path, kind, number, text, notes FROM units ORDER BY path, number"):
        units[p].append((kind, num, text or "", notes or ""))
    ocr_page = {(p, int(n)): t for p, n, t in db.execute("SELECT path, number, text FROM ocr WHERE kind='page' AND error IS NULL")}
    slide_ocr = collections.defaultdict(list)
    for p, s, t in db.execute("""SELECT si.path, si.slide, o.text FROM slide_images si
                                 JOIN ocr o ON o.path=si.path AND o.kind='pptx_image' AND o.number=si.media
                                 WHERE o.error IS NULL"""):
        if ocr_ok(t):
            slide_ocr[(p, s)].append(ocr_ok(t))

    # events: configured prefixes, otherwise each top-level folder
    def event_for(path):
        best = None
        for k in events:
            if path == k or path.startswith(k.rstrip("/") + "/"):
                best = k if best is None or len(k) > len(best) else best
        if best:
            return best
        top = path.split("/")[0] if "/" in path else "(root)"
        events.setdefault(top, {})
        return top

    def ev_title(k):
        e = events.get(k, {})
        return safe(e.get("title") or (k if k != "(root)" else "Files in the root folder"))

    def ev_year(k):
        e = events.get(k, {})
        if e.get("year"):
            return e["year"]
        m = re.search(r"(?<!\d)(20\d{2})(?!\d)", k)
        return int(m.group(1)) if m else None

    def topics_for(head, default):
        found = [t for t, v in topics.items() if v.get("keywords") and re.search(v["keywords"], head.lower())]
        return list(dict.fromkeys(list(default) + found))[:3]

    # group decks
    groups = collections.OrderedDict()
    for p in sorted(docs):
        ext = docs[p][0]
        if ext not in DECK or p.startswith(private) or "_files/" in p:
            continue
        stem = re.sub(r"[\s_+]+", " ", Path(p).stem.lower()).strip()
        groups.setdefault((str(Path(p).parent), stem), []).append(p)

    used, decks = set(), []
    order = {".pptx": 0, ".ppt": 1, ".docx": 2, ".pdf": 3}
    for (folder, _), paths in groups.items():
        paths.sort(key=lambda x: order.get(Path(x).suffix.lower(), 9))
        main_p = paths[0]
        slides, src = [], main_p
        for p in paths:
            us = units.get(p, [])
            if any(t or n for _, _, t, n in us):
                src = p
                for kind, num, text, notes in us:
                    if kind == "page" and len(text) < 15:
                        text = ocr_ok(ocr_page.get((p, num), "")) or text
                    slides.append((kind, num, text, notes, slide_ocr.get((p, num), [])))
                break
        else:
            for p in paths:
                pages = sorted((n, t) for (pp, n), t in ocr_page.items() if pp == p)
                if pages:
                    src, slides = p, [("page", n, ocr_ok(t), "", []) for n, t in pages]
                    break
        evk = event_for(main_p)
        head = " ".join(s[2] for s in slides[:2]) + " " + Path(main_p).name
        body_text = " ".join(s[2] for s in slides)
        first = next((s[2].split("\n")[0][:80] for s in slides if s[2]), "")
        base = safe(Path(main_p).stem.replace("+", " "))
        title, i = base, 1
        while title.lower() in used:
            i += 1
            title = safe(f"{base} ({Path(folder).name or 'root'})") + ("" if i == 2 else f" {i}")
        used.add(title.lower())
        decks.append(dict(title=title, paths=paths, src=src, slides=slides, event=evk, first=first,
                          topics=topics_for(head, events.get(evk, {}).get("topics", [])),
                          lang=lang_of(body_text + " " + head), year=ev_year(evk),
                          modified=(docs[main_p][1] or "")[:10]))

    # deck notes
    for d in decks:
        fm = ["---", "type: deck", "auto: true", f"event: {q('[[' + ev_title(d['event']) + ']]')}",
              f"year: {d['year'] or ''}", f"modified: {d['modified']}", "topics:"]
        fm += [f"  - {q('[[' + t + ']]')}" for t in d["topics"]]
        fm += [f"lang: {d['lang']}", f"slides: {len(d['slides'])}", "files:"] + [f"  - {q(p)}" for p in d["paths"]]
        fm += ["rating:", "used_again: false", "verified: false", "---", ""]
        b = [f"# {d['title']}", ""]
        if d["first"]:
            b += [f"> {d['first']}", ""]
        b.append("**Files:** " + " · ".join(link_file(p, Path(p).suffix[1:].upper() + ": " + Path(p).name) for p in d["paths"]))
        b.append(f"**Event / series:** [[{ev_title(d['event'])}]]")
        if d["topics"]:
            b.append("**Topics:** " + ", ".join(f"[[{t}]]" for t in d["topics"]))
        b += ["", "## My notes", "- What worked:", "- What to cut / improve:", "- Best slides to reuse:", ""]
        pdfs = [p for p in d["paths"] if p.lower().endswith(".pdf") and not BAD.search(p)]
        if pdfs:
            b += ["> [!example]- PDF preview", f"> ![[{pdfs[0]}]]", ""]
        if d["slides"]:
            b += ["## Slide / page text", f"*Extracted automatically from `{Path(d['src']).name}`. OCR can be wrong: check the original.*", ""]
            label = {"slide": "Slide", "page": "Page", "document": "Text"}
            for kind, num, text, notes, extra in d["slides"]:
                if not (text or notes or extra):
                    continue
                b.append(f"### {label.get(kind, kind)} {num}")
                if text:
                    b.append(text)
                if notes:
                    b += ["> [!note]- Speaker notes"] + ["> " + ln for ln in notes.split("\n")]
                if extra:
                    b.append("> [!quote]- Text in pictures (OCR)")
                    for e in extra[:3]:
                        b += ["> " + ln for ln in e.split("\n")]
                b.append("")
        write(root, f"{BASE}/Decks/{d['title']}.md", "\n".join(fm + b) + "\n")

    # event notes
    by_event = collections.defaultdict(list)
    for d in decks:
        by_event[d["event"]].append(d)
    media = collections.defaultdict(lambda: collections.defaultdict(list))
    for p, (ext, _) in docs.items():
        if p.startswith(private) or "_files/" in p:
            continue
        kind = "img" if ext in IMG else "av" if ext in VIDEO | AUDIO else None
        if kind:
            media[event_for(p)][kind].append(p)
    for k in list(events):
        if k not in by_event and k not in media:
            continue
        e = events.get(k, {})
        t = ev_title(k)
        fm = ["---", "type: event", "auto: true", f"year: {ev_year(k) or ''}", f"city: {q(e.get('city', ''))}",
              f"format: {q(e.get('format', ''))}", f"audience: {q(e.get('audience', ''))}", "topics:"]
        fm += [f"  - {q('[[' + x + ']]')}" for x in e.get("topics", [])]
        fm += [f"folder: {q(k if k != '(root)' else '')}", f"paid: {'true' if e.get('paid') else ''}", "fee:",
               "organizer:", "date:", "video_link:", f"status: {e.get('status', 'done')}", "verified: false", "---", ""]
        b = [f"# {t}", ""]
        if e.get("description"):
            b += [e["description"], ""]
        b += ["> [!warning] Year, city and format were inferred from folder names. Check them and fill in date, organizer, fee and video link.", ""]
        if k != "(root)":
            b += [f"**Folder:** `{k}`", ""]
        if by_event.get(k):
            b += ["## Decks and documents", ""]
            for d in sorted(by_event[k], key=lambda d: d["title"]):
                b.append(f"- [[{d['title']}]] — {len(d['slides'])} slides/pages" + (f" · “{d['first'][:60]}”" if d["first"] else ""))
            b.append("")
        m = media.get(k, {})
        if m.get("av"):
            b += ["## Video and audio", ""] + [f"- {link_file(p)}" for p in sorted(m["av"])[:60]] + [""]
        if m.get("img"):
            imgs = sorted(m["img"])
            b += [f"## Photos and images ({len(imgs)})", ""] + [embed(p) for p in imgs[:12]]
            if len(imgs) > 12:
                b += ["", f"…and {len(imgs) - 12} more in the folder."]
            b.append("")
        b += ["## Debrief", "- Audience size and reaction:", "- Questions from the room:", "- What worked:",
              "- What to improve:", "- Feedback, thank-you letters, proofs:", "- Leads and contacts:", ""]
        write(root, f"{BASE}/Events/{t}.md", "\n".join(fm + b) + "\n")

    # topic notes
    for name, v in topics.items():
        ds = [d for d in decks if name in d["topics"]]
        evs = sorted({d["event"] for d in ds} | {k for k, e in events.items() if name in e.get("topics", [])})
        b = ["---", "type: topic", "auto: true", "status: active", "---", "", f"# {name}", "", v.get("description", ""), "",
             "## Synopsis for organizers", "*(2–3 sentences: audience pain → what they get → format. Set `auto: false` before editing.)*", "",
             "## Key points", "- ", "", "## Versions", "- 15 min:", "- 45 min:", "- 90 min / workshop:", "",
             "## Events", ""]
        b += [f"- [[{ev_title(k)}]]" for k in evs] or ["- —"]
        b += ["", f"## Decks ({len(ds)})", ""]
        b += [f"- [[{d['title']}]]" + (f" · {d['year']}" if d["year"] else "") for d in sorted(ds, key=lambda d: (-(d["year"] or 0), d["title"]))]
        b += ["", "## Stories and cases", "```base", "filters:", "  and:", f'    - file.inFolder("{BASE}/Story bank")',
              f'    - topics.contains(link("{name}"))', "views:", "  - type: table", "    name: Stories",
              "    order:", "      - file.name", "      - hook", "      - used_in", "```", ""]
        write(root, f"{BASE}/Topics/{safe(name)}.md", "\n".join(b) + "\n")

    print(f"Vault ready: {len(decks)} decks, {len([k for k in events if k in by_event or k in media])} events, {len(topics)} topics.")
    print(f"Open {root} in Obsidian as a vault and start with {BASE}/Home.md")


if __name__ == "__main__":
    main()
