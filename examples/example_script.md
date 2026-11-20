---
title: Why I'll never make presentations by hand again
subtitle: How AI turned a speaker's archive back into working material
author: Your Name
footer: YOUR NAME  /  SPEAKERS COMMUNITY
---

<!--
Script format used by build_deck.py

Every "### " section is one slide. Lines starting with "> " are what you SAY:
they become the speaker notes. You rehearse from the same file the deck is built from.

Slide fields (one per line, "key: value"):
  layout   title | statement | big-number | cards | two-columns | image
  label    small amber kicker above the heading
  heading  main headline (assertion style: say the conclusion)
  accent   (title) big highlighted word
  number   (big-number) the figure
  text     body text; use \n for line breaks
  image    path relative to this file; alt: alt text for accessibility
  caption  small grey source/caveat line at the bottom
  - A | B  card or column (cards: title | body; two-columns: left/right blocks)
Plain lines that are none of the above are ignored (use them as stage directions).
-->

### 01 · 00:00 · Hook
layout: title
label: SCREENCAST
heading: Why I'll never
accent: EVER
text: make presentations by hand again
caption: How AI rebuilt one morning's work from a speaker's whole archive
> How did I live without AI? I don't know. But it used to cost me about two hundred dollars a month for an assistant. Now I pay twenty dollars for AI, and it handled my speaker folder better than I expected.

### 02 · 00:55 · Shared pain
layout: statement
label: WARM-UP
heading: Everyone has final_really.pptx
text: Mine is final_really_128slides_MEGA.pptx
> Almost every speaker has a file called final, really. Mine is final really, 128 slides, mega. And it's funny because I really have those 128 slides.
Pause after "Mine is". Don't show the file name before you say it.

### 03 · 01:30 · Inventory
layout: big-number
label: SOURCE FOLDER
heading: I started with an inventory, not with design
number: 1,141
text: files in one speaker folder
caption: Snapshot of the initial inventory.
> The first prompt was not "make it beautiful". It was "create a list of files". Name, format, date changed. A date changed is not the date of the talk — that's a decision for a human.

### 04 · 02:30 · Knowledge base
layout: cards
label: KNOWLEDGE BASE
heading: Now every fragment has an address
- 3,664 | PPTX slides with text
- 2,760 | PDF pages
- 9,181 | OCR records from scans and pictures
caption: Different units — don't add them up. Versions of the same deck are counted separately.
> Instead of "I think you talked about this somewhere", I get a file name and a slide number.

### 05 · 03:30 · A decision on the way
layout: two-columns
label: DECISION
heading: We needed letters, not image descriptions
- About a minute | per picture with a small local vision model. Stopped.
- OCR instead | Tesseract reads text from scans and images locally.
caption: Audio and video were deliberately left out.
> I wanted the model to describe every picture. One minute per image. I said: stop, too slow. We kept OCR. Automation got a boundary because I set one.

### 06 · 05:40 · How it works
layout: cards
label: HOW IT WORKS
heading: The chat opens the folder and runs tools
- AI agent | Dialogue and the working folder
- Local tools | Extract text, render slides
- SQLite | Keeps results between sessions
caption: Local tools ≠ a local LLM. The model runs at the provider you selected.
> The agent gets access to the files and tools of this session. The laptop runs local programs; the model itself runs in the cloud.

### 07 · 08:35 · Search
layout: two-columns
label: SEARCH RESULT
heading: One phrase leads to slide 69
- Query | “first three seconds”
- Found | Slide 57 in the master deck, slide 69 in a regional talk
caption: Show the original slide next to the result. That's your evidence.
> I remembered the advice about the first three seconds, but not where it was. Search found it in two decks.

### 08 · 10:05 · Three formats
layout: cards
label: REMIX
heading: One source. Three different jobs.
- 7 min talk | Why short video matters for business · src 14, 69, 70
- 30 min workshop | Shoot your first clip on a phone · src 65, 66, 69, 70
- 3 min EN pitch | Make your first three seconds count · src 14, 69, 76
> Same source, different audience, different order, different job.

### 09 · 12:05 · Editor-in-chief
layout: two-columns
label: AUTHOR'S ROLE
heading: I am still the editor-in-chief
- AI | Finds fragments\nProposes structure\nAssembles the draft
- Me | Chooses the message\nChecks the facts\nRehearses out loud
caption: Don't carry old platform numbers into a new talk without checking.
> I delegated search, rough structure and assembly. Audience, promise, and what to say in my own name stayed with me.

### 10 · 13:05 · First step
layout: statement
label: YOUR FIRST STEP
heading: Start with your longest talk.
text: “Find the key points and slide numbers. Build three versions. Flag what needs checking.”
> Take your longest talk. Ask for topics and slide numbers. Let AI propose three versions and flag what's outdated. Then pick the one you actually want to tell.
