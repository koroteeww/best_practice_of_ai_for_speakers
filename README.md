# Best practice of using AI for speakers

> A practical playbook for speakers who want to turn years of slides, PDFs, photos and videos into a searchable knowledge base, and then use AI to prepare new talks faster without losing their own voice.

Made by **Aivan (Ivan) Koroteev**: TEDx speaker (RU/EN), AI engineer with a Computer Science degree (Bauman Moscow State Technical University), 13+ years in enterprise IT, speaker on Applied AI and creativity for introverts. Co-written with **Claude** (Anthropic).

🌐 **Website:** [ivankoroteev.ru/en](https://ivankoroteev.ru/en) · 🎤 **Public speaking training for software engineers and IT teams:** [creativityforintroverts.com](https://creativityforintroverts.com/public-speaking-training-for-software-engineers-and-it-teams/)

---

## Why this exists

Every working speaker ends up with the same folder: `final.pptx`, `final_really.pptx`, `final_really_128slides_MEGA.pptx`, scans of thank-you letters, photos from events, and a few videos nobody has watched since. The material is valuable, but you can't search it, so every new talk starts from a blank slide.

This repository shows a workflow that has been tested on a real archive of about 1,100 files:

1. **Inventory**: list everything, change nothing.
2. **Extract**: pull the text of every slide and page into SQLite, then OCR the scans and the text inside images.
3. **Organize**: generate an **Obsidian** vault with one note per deck, one per event and one per topic, plus a story bank and dashboards.
4. **Create**: brief → slide map → assertion-evidence slides → editable PPTX built with code → render and check → rehearse.
5. **Stay the editor-in-chief.** AI searches, drafts and assembles. You choose the message, check the facts and say it out loud.
6. **Connect your vaults.** If you keep several knowledge bases (personal, work, projects, talks), one AI chat can see them all through a small **meta vault**: one home for each note, short bridges instead of copies, at most five proposals at a time. See [docs/08](docs/08-many-vaults-one-ai-chat.md).
7. **Build the tools for the agent, not for you.** The AI runs the scripts: give it JSON results saved as files (not printed to the console), slide addresses, merged duplicates, contact sheets it can *look at*, and a `check` command for its own decks. See [docs/09](docs/09-tools-for-ai-agents.md).

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
| [`docs/08-many-vaults-one-ai-chat.md`](docs/08-many-vaults-one-ai-chat.md) | Several Obsidian vaults (personal, work, projects, speaking), one AI chat: a meta vault that routes material, proposes bridges and backs everything up |
| [`docs/09-tools-for-ai-agents.md`](docs/09-tools-for-ai-agents.md) | Designing tools for the AI agent: JSON, slide addresses, duplicate merging, contact sheets, self-check. Lessons from an 8,800-slide archive |
| [`docs/case-study-screencast.md`](docs/case-study-screencast.md) | Case study: a 13-slide screencast built in one morning from a speaker's archive |
| [`docs/case-study-meta-vault.md`](docs/case-study-meta-vault.md) | Case study and reflection: building the meta vault for four real vaults in one session with Claude Code |
| [`vault-template/`](vault-template/) | A ready-to-open Obsidian vault with templates, dashboards and example notes |
| [`meta-vault-template/`](meta-vault-template/) | A ready-to-copy meta vault: `CLAUDE.md` rules, vault profiles, hash registry, bridge and digest templates, weekly backup |
| [`tools/kb.py`](tools/kb.py) | **The agent's tool**: slide-level index and search, slide text and PNG, contact sheets, Obsidian candidate lists, `check` for built decks. Results are saved as JSON files in `_ai/kb_out/`, and the console shows one line |
| [`agent-template/`](agent-template/) | `CLAUDE.md` + `AGENTS.md` to drop into a speaker folder, so any agent session knows the tools, the workflow and the privacy rules |
| [`tools/`](tools/) | Other Python scripts: build the knowledge base, OCR, simple search, generate the vault, check PPTX rendering |
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

**If an AI agent will do the work (recommended):**
1. Copy [`agent-template/CLAUDE.md`](agent-template/CLAUDE.md) and `AGENTS.md` into `D:/Talks` and fill in the bracketed parts.
2. Tell the agent: *"Index my archive with tools/kb.py and build a 20-minute English talk on X."*

The agent runs these itself:

```bash
python tools/kb.py --root "D:/Talks" update
python tools/kb.py --root "D:/Talks" search "first three seconds"
python tools/kb.py --root "D:/Talks" sheet --hits "first three seconds"   # PNG grid the agent looks at
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

## Author and contacts

**Aivan Koroteev** is an AI engineer and TEDx speaker. He gives talks, workshops and corporate training on Applied AI, AI for presentations, and creativity and public speaking for introverts, in English and Russian.

- Website: https://ivankoroteev.ru/en
- Public speaking training for software engineers and IT teams: https://creativityforintroverts.com/public-speaking-training-for-software-engineers-and-it-teams/
- TEDx: [Creativity for introverts](https://www.youtube.com/watch?v=2OBxE1Y1J_c)

If this playbook helped you, star the repo or open an issue with your own workflow.

## License

MIT. See [LICENSE](LICENSE). Links to third-party sources belong to their authors.
