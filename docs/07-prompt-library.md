# 07 · Prompt library

Copy, replace the `[brackets]` and paste into ChatGPT, Claude or an AI coding agent that has access to your folder.

## Archive and knowledge base

**First contact with a messy folder**
> Don't change or move any files. Create a service folder `_ai/` and write an inventory of every file there: path, extension, size, modified date. Exclude `_ai/`. Show me counts by extension and the 20 largest files. Point out folders that look private (passports, contracts, bank details), and don't open those.

**Extraction**
> Using the inventory, extract the text of every PPTX slide (including speaker notes) and every PDF page into `_ai/kb.sqlite3`, keeping the path and slide/page number. For DOCX and TXT store the full text. Don't process audio or video. Save progress after each file so the job can resume.

**Find a fragment**
> Search `_ai/kb.sqlite3` for everything I have said about **[topic]** in Russian and English, including synonyms. For each hit return: file, slide/page number, a one-line quote and the year from the path if there is one. Group duplicates across versions of the same deck. Mark any number older than two years as **CHECK**.

**Map the archive**
> From the knowledge base, list my recurring topics. For each one give 2–3 representative decks (file + slide range), the likely audience, and the years it appears in. Treat folder names and dates as hints and label your guesses.

## Building a talk

**Brief**
> I'm speaking to **[audience, size]** at **[event]**, **[N] minutes**, **[format]**, in **[language]**. After the talk they should **[action]**. Ask me at most 5 questions about anything critical that is missing, then propose one main idea and 3–5 supporting points.

**Slide map**
> Build a slide map as a table: # | job of the slide | assertion headline | evidence/visual | what I say | source (file, slide) | needs checking | time. Use only material from my archive or from sources you cite. Don't invent quotes, cases or statistics.

**Remix one source into three formats**
> Take **[deck, slides X–Y]** and propose three versions:
> (1) a 7-minute conference talk;
> (2) a 30-minute workshop where people leave with a draft;
> (3) a 3-minute English pitch.
> For each version list the source slide numbers, what changes, and one exercise or call to action.

**Build the deck**
> Write a Python script with python-pptx that builds a 16:9 deck from `script.md`:
> - every `###` section is a slide, and the `>` quote is the speaker notes;
> - dark background, white text, one accent colour;
> - headings, captions and numbers stay editable text, and pictures get alt text;
> - save to a new file.
>
> Then export it to PDF with LibreOffice, render every page to PNG, look at all of them, and list any overflow, crops, font or contrast problems.

## Rehearsal and QA

**Headline story test**
> Here are only my slide titles. Retell the talk from them in 5 sentences. Where does the logic jump? Which title doesn't make a claim?

**Fact check**
> List every number, date, name and quote in this deck. For each one give the source I used, or mark it **UNSOURCED**. Flag platform or AI stats older than 12 months.

**Sounds like me?**
> Here is my script and three transcripts of my past talks. Point out sentences that don't sound like me (too formal, too generic, clichés) and suggest rewrites in my voice.

**Q&A prep**
> Act as a sceptical [CFO / teacher / engineer] in the audience. Ask the 10 hardest questions about this talk, then suggest short honest answers. Where I have no evidence, say so.

## After the talk

**Debrief**
> Here are my notes from the event: [reaction, questions, what went wrong]. Fill in the "Debrief" section of my event note. Suggest 1–3 stories or cases worth saving to the Story bank, and anything to update in my speaker profile.

**Organizer follow-up**
> Draft a short thank-you message to the organizer of [event]. Ask for photos and video and offer the slides. Keep it in my tone: [examples]. Don't send it, just draft it.
