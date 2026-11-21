# 09 · Tools for the AI agent, not for the human

At some point the speaker said the obvious thing: *"You understand that you, the AI, will run these Python scripts, not me?"* That changes how the tools should be designed. The human never types `python search.py`. They write "build me a 20-minute English talk on AI for business from my archive", and an agent (Claude Code, Codex, T3 Code, Cursor…) runs the tools, reads the output, looks at slides and builds the deck.

This chapter describes the design that came out of that, and the tool that implements it: [`tools/kb.py`](../tools/kb.py), plus a drop-in instruction file for the speaker folder: [`agent-template/`](../agent-template/).

## Design rules for agent-facing tools

| Rule | Why |
|---|---|
| **JSON output**, one object per call | The agent parses it instead of guessing from pretty text. `--text` exists for the rare case a human looks. |
| **Results go to files, not the console** (`_ai/kb_out/<time>_<command>.json`, `last.json`, `history.jsonl`) | The console prints one line: path + summary. The agent reads the file with its Read tool, so there are no console-encoding problems and no truncated output. The history shows the next session what was already searched. This was the speaker's own request: "save all these JSONs into your folder, and that's it". |
| **Errors are data**: `{"error": "..."}` + exit code 1 | A traceback wastes context and hides the fix. Say what to do: "No index yet. Run: … update". |
| **ASCII command names, one entry point** with subcommands | Shells on Windows mangle non-Latin script names, and one `--help` is enough to learn everything. |
| **Force UTF-8 stdout** | Windows consoles default to cp1251 or cp437, so one `→` character can crash a script after it has done its work. |
| **Silence library noise** (e.g. MuPDF structure warnings) | Every stray stderr line costs agent context. |
| **Return images as file paths** | Agents with vision open the PNG with their image/Read tool. Seeing the slide beats any text description. |
| **Contact sheets** | One image with 16–40 numbered slides. The agent "skims" a whole deck in a single tool call. |
| **Addresses everywhere** | Every hit is `path` + slide number `n`. Anything the agent says about the archive can be checked. |
| **Collapse duplicates** | In a real archive, about 2 of every 3 slides were copies from other versions of the same talk. Without merging, the top 10 results are the same slide 10 times. |
| **Mark uncertainty** | `ocr_only: true` when the match is only in recognized text: check the picture before quoting. |
| **Incremental and idempotent** | `update` re-reads only new or changed files (seconds), so the agent can run it before every task. |
| **Read-only toward originals** | The tool writes only to `_ai/` and to the notes folder. |
| **A verification command** | `check` renders the agent's own PPTX and lists concrete problems. The agent fixes them and checks again *before* showing the human. |

## The commands

```bash
python tools/kb.py --root "D:/Talks" update                  # index slides (incremental)
python tools/kb.py --root "D:/Talks" search "first three seconds" --lang en
python tools/kb.py --root "D:/Talks" show "2022/TikTok_master.pptx" 57      # full text + PNG
python tools/kb.py --root "D:/Talks" outline "2022/TikTok_master.pptx"      # number -> title
python tools/kb.py --root "D:/Talks" sheet "2022/TikTok_master.pptx" --from 1 --to 24
python tools/kb.py --root "D:/Talks" sheet --hits "attention retention" --limit 12
python tools/kb.py --root "D:/Talks" preview "2022/TikTok_master.pptx" 14 69 --width 1600
python tools/kb.py --root "D:/Talks" collect "AI for business"              # candidates note in Obsidian
python tools/kb.py --root "D:/Talks" check "_New/2026-12_forum/deck.pptx"   # verify the agent's own deck
```

Each call prints one line, for example `D:/Talks/_ai/kb_out/20261121-081736-136_search.json  |  hits=5, matches=32`. The agent then reads that file. One `search` hit inside it looks like this:

```json
{"path":"Regional/Social_media_4.pdf","n":69,"kind":"page","title":"Structure of a video story","lang":"ru",
 "snippet":"1) Grab attention in the [first] [3] [seconds]: voice, caption, text over video…",
 "also":["Master/TikTok_2022.pdf#57","Image_Academy_2022.pdf#39"],"copies":15}
```

`copies: 15` is itself a finding: the speaker reused this idea in 15 files. It is a signature point, worth keeping.

## What the agent's workflow looks like

1. **`update`, then `stats`.** Make sure the index is fresh and see what is there.
2. **Search in both languages.** For an English talk, search in English *and* in the speaker's native language. In the reference archive only about 300 of 8,800 slides were in English, while almost every topic existed in Russian. Adapt, don't translate word for word.
3. **`outline` the 2–3 best decks, then `sheet` over the relevant ranges, and look at them.** Much of a speaker's meaning is visual: memes, photos, charts.
4. **`collect`** gives the human a short list with previews and checkboxes. The human decides what goes in.
5. **Slide map → build with python-pptx** (see [`examples/build_deck.py`](../examples/build_deck.py)). Archive slides can go in as images from `preview`, captioned "Archive: file, slide N".
6. **`check` → open the sheet → fix → `check` again.** Then tell the human what was and wasn't verified.

## The instruction file is part of the tool

A tool is useless if the next agent session doesn't know it exists. Put a `CLAUDE.md` (read automatically by Claude Code) and an `AGENTS.md` (read by Codex and others) in the speaker folder. They should cover:

- what the folder is and the rule that originals are never modified;
- the command table, and how to read the JSON;
- the workflow above;
- privacy rules: which folders never to open, and which data never to carry into new slides (phone numbers and QR codes on old slides, other people's faces and voices);
- "old platform numbers are history", and "a file date is not an event date".

A ready template is in [`agent-template/`](../agent-template/). Copy both files into your speaker folder and edit the bracketed parts.

## Lessons

- **Seeing matters.** Text extraction found the slide, but the contact sheet showed that half of the meaning was in the pictures. Give the agent a cheap way to look.
- **Duplicates tell you something.** Merge them in results, but report the count: an idea copied into 15 decks is a signature point.
- **The bilingual gap is real.** An agent that searches only in the talk's language misses most of the archive.
- **Verification belongs to the agent's loop**, not the human's. The human should get a deck that has already been rendered, inspected and fixed, plus an honest list of what wasn't checked (LibreOffice is not PowerPoint).
