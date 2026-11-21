# Tools

Python 3.10+. `pip install -r tools/requirements.txt`

| Script | What it does | Needs |
|---|---|---|
| **`kb.py --root <folder> <command>`** | **The agent's tool** ([docs/09](../docs/09-tools-for-ai-agents.md)). Results are saved as JSON files in `_ai/kb_out/`, and the console gets one line. Commands:<br>• `update`: slide-level index<br>• `search`: duplicates merged<br>• `show`, `outline`, `decks`<br>• `sheet`: contact-sheet PNG<br>• `preview`<br>• `collect`: Obsidian candidate list<br>• `check`: verify a built deck<br>Uses OCR from `ocr.py` if present | python-pptx, PyMuPDF, Pillow; LibreOffice for `check` and for PPTX without a PDF twin |
| `build_knowledge_base.py <folder>` | Inventory + text of every PPTX slide (with speaker notes), PDF page, DOCX and TXT → `<folder>/_ai/kb.sqlite3` with FTS5 search | python-pptx, PyMuPDF |
| `ocr.py <folder> --lang eng+rus` | OCR for scanned PDF pages, images and pictures inside PPTX. Resumable, SHA-256 cache | Tesseract, Pillow |
| `search.py <folder> "phrase"` | Full-text search. Prints the file and the slide/page number | — |
| `build_obsidian_vault.py <folder> [--config cfg.json]` | Generates `_Base/` notes (Decks, Events, Topics) and copies the vault template | — |
| `check_render.py deck.pptx` | PPTX → PDF via LibreOffice, compares slide and page counts, checks the text rendered, warns about missing notes, writes PNG previews | LibreOffice |

**Privacy:**
- `--exclude "Private"` in `build_knowledge_base.py` keeps folders out of the inventory, extraction and search entirely.
- `private_folders` in the vault config keeps them out of the generated notes.
- The scripts never modify or move your files. They write only to `_ai/` and `_Base/`.

**Config:** copy `vault_config.example.json` and map your folder prefixes to events (title, year, city, format, audience, topics, paid). Topics are regex keywords matched against the file name and the first two slides.
