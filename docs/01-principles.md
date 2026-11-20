# 01 · Principles

These rules came out of turning a real speaker archive (about 1,100 files built up over 5 years) into an AI-assisted knowledge base. Each one is here because breaking it caused a problem.

## 1. The speaker is the editor-in-chief
AI finds fragments, proposes structures and assembles drafts. The speaker chooses the main message, the promise to the audience, and what is worth saying in their own name. The final test is to read the talk out loud. If it doesn't sound like you, edit it.

## 2. Inventory before intelligence
The first prompt is "create a list of files", not "make a beautiful deck". A plain inventory (path, type, size, modified date) shows what you have, where duplicates are, and where the private documents live. Everything else builds on it.

## 3. Never touch the originals
Scripts open archives read-only and write only into a service folder (`_ai/`). If you edit an existing deck, work on a copy. This makes the whole process safe to repeat.

## 4. Every fact needs an address
A good answer looks like "file `X.pptx`, slide 57", not "you mentioned this somewhere". Store the extracted text per slide and per page so AI can always point to a source, and check the original before you use a quote, a number or a date.

## 5. Hints are not evidence
- A file's modified date says when it was edited, not when you gave the talk.
- A folder called `City_2024` may hold decks from other events.
- The same paragraph in two decks doesn't tell you which one came first.
- OCR and automatic summaries help you search. They are not proof.

Keep a `verified: false` property on anything inferred automatically and turn it to `true` only after a human has checked it.

## 6. Old numbers are historical
Statistics about platforms, AI models, prices and user counts go out of date quickly. When you reuse an old slide, mark its numbers as "check" and update them, or present them as history ("in 2022 we saw…").

## 7. Stop what doesn't pay off
Set limits on automation. In the reference project, describing every image with a small local vision model took about a minute per picture, so it was stopped. Plain OCR gave the text that was actually needed. Audio and video transcription was left out on purpose. Choose the cheapest method that answers the real question.

## 8. Privacy by default
Leave these out of extraction, search indexes, prompts and public repositories:
- passports and tax IDs, bank details, signed contracts;
- private contact lists;
- other people's photos and voices (faceswap and voice-clone demos need consent);
- client materials under NDA.

The fact that a file exists doesn't mean you may publish it.

## 9. One vault, linked notes
Use one Obsidian vault, with one idea per note and links instead of copies. Topics, events, decks and stories connect through links and properties, so a story told at three events lives in one note that links to all three.

## 10. Render, look, rehearse
Saving a PPTX without errors doesn't mean it looks right. Export it to PDF and look at every slide, both as thumbnails and at full size. Then check text overflow, fonts (Cyrillic and Latin), contrast, image crops, the speaker notes and the timing. If you skipped a check, say so.
