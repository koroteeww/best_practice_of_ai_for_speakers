# Speaker archive — instructions for the AI agent

*Copy this file (and `AGENTS.md`) into the root of your speaker folder. Edit the [bracketed] parts.*

This folder is [Name]'s archive of talks: PPTX, PDF, photos, videos, proofs. New talks in [languages] are often assembled from it. **You run the tools below yourself.** The human doesn't. Show the human results: candidate lists, slide maps, finished files and slide images.

Never move or modify originals. Save new decks as new files in `_New/<date>_<topic>/`.

## Tool: `kb.py`
`python [path/to]/kb.py --root . <command>`. It returns compact JSON. Errors come back as `{"error": …}` with exit code 1. Paths are relative to this folder. `png` and `sheet` fields are absolute image paths: **open them with your image/Read tool to see the slides.**

| Task | Command |
|---|---|
| Refresh the index (run before each task, takes seconds) | `kb.py --root . update` |
| What is indexed | `kb.py --root . stats` |
| Find slides | `kb.py --root . search "query" [--lang en] [--folder X] [--limit 15]` |
| Full text + image of one slide | `kb.py --root . show "<path>" <n>` |
| Table of contents of a deck | `kb.py --root . outline "<path>"` |
| List decks, newest first | `kb.py --root . decks [--folder X] [--q word]` |
| See many slides at once | `kb.py --root . sheet "<path>" --from 1 --to 24`, then open `sheet` |
| See the top hits as images | `kb.py --root . sheet --hits "query" --limit 12` |
| PNGs to place into a new deck | `kb.py --root . preview "<path>" 14 69 --width 1600` |
| Candidate list for the human (Obsidian) | `kb.py --root . collect "topic"` |
| Verify a deck you built | `kb.py --root . check "_New/…/deck.pptx"`, then open `sheet` and fix the `issues` |

**Reading `search` results:**
- `copies` and `also` list the same slide in other versions. Cite the newest or final one.
- `ocr_only: true` means the match was found only in recognized text. Look at the image before quoting it.

**Queries:**
- words of 6 or more letters match by stem;
- `"exact phrase"` matches exactly;
- `OR` binds tighter than a space, so write `"short video" OR "vertical video"`.

**Languages:** for a talk in [English], search in [English] **and** in [native language]. Most material may exist only in one of them. Adapt it, don't translate word for word.

## Workflow for a new talk
1. **Brief:** audience, length, language, format, and what the listener should do afterwards. Go ahead with what you have and list your assumptions. Ask at most 3–5 questions.
2. **Explore:** run `search` with synonyms in both languages, then `outline` the best 2–3 decks, then `sheet` over the relevant ranges. Look at the images.
3. **Candidates:** run `collect`, or give a table of point → source (path, slide n) → reuse / adapt / redraw.
4. **Slide map:** # | job | assertion headline | evidence/visual | what I say | source | to check | time.
5. **Build:** python-pptx script next to the output. Keep text editable. Archive slides can go in as images, captioned "Archive: file, slide N". Add alt text, and take the speaker notes from the script.
6. **Check:** run `check`, open the sheet, fix, and check again. Tell the human what wasn't verified (LibreOffice rendering ≠ PowerPoint).

Speaker profile (bio, numbers, credentials): [path to profile note]. Design and storytelling guidelines: [path or link].

## Rules
- Platform, AI and audience numbers on old slides are **history**. Mark them "check" or present them as the past.
- A file date is not an event date. A folder name is a hint, not a fact.
- Never invent cases, quotes, credentials or statistics. Every claim taken from the archive needs a source: file and slide number.
- **Private: never open, quote or send to external services:**
  - [ID and bank documents folder];
  - [contracts folder];
  - personal phone numbers and messenger QR codes on old slides: don't carry them into new material without permission.
- Other people's faces and voices (deepfake or voice-clone demos) are not used in public material without their consent.
