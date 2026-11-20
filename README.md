# Best practice of using AI for speakers

> A practical playbook for speakers who want to turn years of slides, PDFs, photos and videos into a searchable knowledge base, and then use AI to prepare new talks faster without losing their own voice.

Made by **Aivan (Ivan) Koroteev**: TEDx speaker (RU/EN), AI engineer with a Computer Science degree (Bauman Moscow State Technical University), 13+ years in enterprise IT, speaker on Applied AI and creativity for introverts. Co-written with **Claude** (Anthropic).

---

## Why this exists

Every working speaker ends up with the same folder: `final.pptx`, `final_really.pptx`, `final_really_128slides_MEGA.pptx`, scans of thank-you letters, photos from events, and a few videos nobody has watched since. The material is valuable, but you can't search it, so every new talk starts from a blank slide.

This repository shows a workflow that has been tested on a real archive of about 1,100 files:

1. **Inventory**: list everything, change nothing.
2. **Extract**: pull the text of every slide and page into SQLite, then OCR the scans and the text inside images.
3. **Organize**: generate an **Obsidian** vault with one note per deck, one per event and one per topic, plus a story bank and dashboards.
4. **Create**: brief → slide map → assertion-evidence slides → editable PPTX built with code → render and check → rehearse.
5. **Stay the editor-in-chief.** AI searches, drafts and assembles. You choose the message, check the facts and say it out loud.

## What's inside

| Path | What it is |
|---|---|
| [`docs/01-principles.md`](docs/01-principles.md) | The ten rules everything else is built on |
| [`docs/02-obsidian-vault-for-speakers.md`](docs/02-obsidian-vault-for-speakers.md) | How to structure an Obsidian vault for talks, events, stories and proofs |
| [`docs/03-ai-knowledge-base-pipeline.md`](docs/03-ai-knowledge-base-pipeline.md) | Inventory → extraction → OCR → SQLite full-text search → Obsidian |
| [`docs/04-presentation-workflow-with-ai.md`](docs/04-presentation-workflow-with-ai.md) | From brief to a checked, editable PPTX with an AI coding agent |
| [`docs/05-slide-design-principles.md`](docs/05-slide-design-principles.md) | Visual hierarchy, cognitive load, avoiding "Death by PowerPoint", accessibility |
| [`docs/06-storytelling-and-humor.md`](docs/06-storytelling-and-humor.md) | Story structure, jokes and memes that support a point |
| [`docs/07-prompt-library.md`](docs/07-prompt-library.md) | Copy-paste prompts for the archive, briefs, remixes, rehearsal and image generation |
| [`docs/case-study-screencast.md`](docs/case-study-screencast.md) | Case study: a 13-slide screencast built in one morning from a speaker's archive |
| [`vault-template/`](vault-template/) | A ready-to-open Obsidian vault with templates, dashboards and example notes |
| [`tools/`](tools/) | Python scripts: build the knowledge base, OCR, search, generate the vault, check PPTX rendering |
| [`examples/`](examples/) | Build a styled 16:9 PPTX with speaker notes from a Markdown script |

## Quick start

```bash
git clone https://github.com/koroteeww/best_practice_of_ai_for_speakers.git
cd best_practice_of_ai_for_speakers
pip install -r tools/requirements.txt

# 1. Index your speaker folder (read-only; writes to <folder>/_ai/kb.sqlite3)
python tools/build_knowledge_base.py "D:/Talks"

# 2. Optional: OCR scans and text inside images (needs Tesseract)
python tools/ocr.py "D:/Talks" --lang eng+rus   # add --tessdata DIR if languages aren't found

# 3. Search the archive
python tools/search.py "D:/Talks" "first three seconds"

# 4. Generate an Obsidian vault on top of the folder
python tools/build_obsidian_vault.py "D:/Talks"
```

Then open `D:/Talks` in Obsidian as a vault and start from `_Base/Home.md`. If you'd rather start from an empty vault, open `vault-template/` instead.

To build an example deck:

```bash
python examples/build_deck.py examples/example_script.md -o examples/out/example.pptx
python tools/check_render.py examples/out/example.pptx   # optional, needs LibreOffice
```

## Who this is for

- Speakers, lecturers and trainers with a messy archive of talks.
- Event organizers and speaker bureaus who keep speaker materials.
- Anyone who prepares talks with ChatGPT, Claude, Codex or Claude Code and wants a source for every claim.

## Principles in one screen

- **Local-first.** Your archive stays on your disk. Scripts read the originals and never modify them.
- **Provenance.** Every fact the AI suggests comes with a file name and a slide number. If it has no source, you don't use it.
- **A file date is not an event date.** Folder names and timestamps are hints, not evidence.
- **Old numbers are historical until verified.** Platform stats from 2022 are not facts in 2026.
- **Privacy.** Passports, bank details, contracts and other people's faces stay out of prompts, out of search and out of public repos.
- **Render and look.** A PPTX that saves without errors can still look broken. Export it, look at every slide and rehearse with a timer.

## License

MIT. See [LICENSE](LICENSE). Links to third-party sources belong to their authors.
