# 03 · From a messy folder to an AI knowledge base

The pipeline runs fully on your own machine. Nothing is sent to the cloud unless you choose to paste results into a chat. It can be resumed at any point.

```
your folder ──► inventory ──► text extraction ──► OCR (optional) ──► SQLite + FTS5 ──► Obsidian vault
                (paths,       (PPTX slides +     (scans, images     (search by        (deck / event /
                 sizes,        notes, PDF pages,  in PDFs and        phrase, with      topic notes)
                 dates)        DOCX, TXT)         inside PPTX)       file + number)
```

## Step 1 — Inventory (read-only)
Walk the folder and record path, extension, size and modified time for every file. Exclude the service folder. Print a count by extension. This answers "what do we have?" before anyone opens a file.

Typical result for a speaker archive: hundreds of JPG/PNG files, about 200 PDFs, about 130 PPTX, about 90 videos, about 60 audio files, plus DOCX, TXT, saved web pages and ZIPs.

## Step 2 — Extract text with provenance
| Format | What to extract | Unit |
|---|---|---|
| PPTX | text from text frames, tables and grouped shapes, **speaker notes**, the images each slide uses | slide number |
| PDF | page text and image count | page number |
| DOCX | paragraphs | document |
| TXT / MD / HTML | text (try UTF-8, UTF-16, CP1251) | document |
| XLSX | sheet rows | sheet |
| Images, video, audio | metadata only (size, duration), no content | file |

Store this in SQLite: `documents(path, …)` and `units(path, kind, number, text)`. Keep the path relative to the archive root. That pair of path and number is the address of every fact.

> **Order matters in PPTX.** Don't trust `slideN.xml` file names. The real order is in `ppt/presentation.xml` and its rels. `python-pptx` handles this for you.

## Step 3 — OCR what has no text layer (optional, slow)
Process the work in this order:
1. PDF pages with less than about 40 characters of text, which are probably scans;
2. standalone images;
3. pictures inside PPTX (`ppt/media/*`), linked back to their slide through the slide rels.

Use local **Tesseract** with your languages (e.g. `eng+rus`). Cache results by image SHA-256, because the same screenshot often appears in 10 versions of a deck. Save after every item so you can stop and resume.

**Lessons learned**
- OCR is noisy on stylised text, memes and photos. Filter out results that are mostly symbols before you show them.
- A small vision-language model on CPU (e.g. SmolVLM-256M) took about a minute per image and hallucinated details. It was stopped. For a speaker archive, OCR text gave more than captions did.
- Don't transcribe audio or video unless you have a concrete question for it.

## Step 4 — Full-text search
Create an FTS5 table (`tokenize="unicode61"` handles Cyrillic). Index file name, slide or page text, notes and OCR. A query like `"first three seconds"` returns the deck and the slide number in milliseconds. That is the moment the archive becomes useful: you remember a phrase but not where it was.

## Step 5 — Generate the Obsidian vault
For every deck (PPTX and PDF with the same name merged into one note), the script creates:
- frontmatter: event, year, topics, language, number of slides, files, `verified: false`;
- links to the original files and an embedded PDF preview;
- the full slide-by-slide text, with OCR from slide images in a collapsed callout;
- an empty "My notes" section (what worked, what to cut, best slides to reuse).

It also creates one note per event folder and one per topic. Topic assignment uses keywords on the file name and the first two slides, because the full text matches too many topics. You can also provide a JSON config that maps folders to events (year, city, format, audience, topics).

The script only overwrites notes marked `auto: true`, so your hand-written notes are safe when you rebuild.

## Step 6 — Use it with an AI agent
Point Claude Code, Codex or another agent with file access at the folder and say:

> "Use `_ai/kb.sqlite3`. Find everything I have said about *X*. Return file, slide number, a 1-line quote, and mark numbers older than 2 years as 'check'."

The agent queries SQLite, opens only the original slides it needs, and gives you sources you can check. See [07-prompt-library.md](07-prompt-library.md).

## Scripts in this repo
| Script | Does |
|---|---|
| `tools/build_knowledge_base.py` | Steps 1, 2 and 4 in one go |
| `tools/ocr.py` | Step 3, resumable, with a hash cache |
| `tools/search.py` | CLI search with file and slide numbers |
| `tools/build_obsidian_vault.py` | Step 5 |
| `tools/check_render.py` | PPTX → PDF via LibreOffice, checks page count and text |
