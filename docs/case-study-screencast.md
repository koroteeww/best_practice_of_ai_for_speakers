# Case study: "Why I'll never make presentations by hand again"

A 14-minute screencast for a community of speakers, built in **one morning** from a real archive using an AI coding agent. The talk is itself a demonstration of the workflow in this repository.

## Starting point
- About 1,141 files in one speaker folder: drafts, finals, "finals of the second generation", scans and photos.
- The goal: show other speakers how AI can turn an archive back into working material.

## What was done
1. **Inventory.** The first prompt was "create a list of files", not "make a nice deck".
2. **Knowledge base.** PPTX slides, PDF pages and DOCX text went into SQLite, with OCR for scans and images.
3. **A decision mid-way.** Captioning images with a small local vision model took about a minute per picture. *"Stop, too slow."* It was replaced by OCR, and audio and video were left out deliberately.
4. **Reference notes.** The agent also saved guidelines (slide design, delivery, storytelling) as Markdown, so the next session starts with context.
5. **Search demo.** A remembered phrase ("first three seconds") found slide 69 in a regional talk. The same fragment was slide 57 in a 128-slide master deck. Both originals were shown side by side as evidence.
6. **Remix.** The same source became three formats: a 7-minute talk, a 30-minute workshop and a 3-minute English pitch, each with source slide numbers.
7. **Build.** First a standalone HTML deck (keyboard navigation, live search over a snapshot of the database). Then a PPTX built with python-pptx, with speaker notes generated from the script. Both were exported to PDF and checked frame by frame.

## Structure of the talk (13 slides)
| # | Slide | Purpose |
|---|---|---|
| 1 | Title + generated poster | Hook: "How did I live without AI? Don't know. But it cost $200 a month." |
| 2 | Speaker memes | Warm-up with a shared pain: `final_really_128slides.pptx` |
| 3 | 1,141 files | "I started with an inventory, not with design" |
| 4 | Knowledge base numbers | Every fragment now has an address |
| 5 | Decision | "We needed letters, not image descriptions" |
| 6 | How it works | Chat opens the folder and runs tools. Local tools ≠ a local LLM |
| 7 | Guidelines | The archive tells you *what* to take, the guidelines tell you *how* to show it |
| 8 | 128-slide master deck | How talks used to be assembled by hand |
| 9 | 87-slide regional talk | Where is the same advice in this version? |
| 10 | Search result | One phrase → slide 69, with the original as proof |
| 11 | Three formats | One source, three different jobs |
| 12 | Editor-in-chief | AI: search, structure, draft. Me: message, facts, rehearsal |
| 13 | First step | "Start with your longest talk" + call to action |

## Lessons
- **Show the evidence.** Every claim on screen had an original slide next to it.
- **Be honest about the demo.** The live search ran on a prepared snapshot, and the three formats were prepared in advance, not generated live. Say so.
- **Old platform numbers don't carry over** into a new talk as today's facts.
- **Mind privacy in the recording.** Keep only one harmless folder open, and check what extracted text ends up in a shared HTML file.
- **The script is the source of truth.** Speaker notes in the PPTX are generated from the same Markdown script used for rehearsal.

See [`examples/`](../examples/) for a generic version of the build script and a script template.
