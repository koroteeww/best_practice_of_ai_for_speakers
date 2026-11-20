# 04 · Presentation workflow with AI

How to go from an invitation to a checked, editable deck with ChatGPT, Claude, Codex or Claude Code and a few local tools.

## 1. Brief first: audience and outcome
Before anyone draws a slide, write down:

- **Who** is in the room, how many, and what they already know.
- **What** they should understand, feel or *do* afterwards.
- **Format**: stage keynote, webinar, workshop, or a PDF read without you.
- **Duration**, language and country.
- **Room setup**: projector and aspect ratio, sound for video, internet for live demos.
- **Organizer requirements**: template, logos, call to action.

Then write **one sentence** with the main idea, plus 3 to 5 supporting points. If the brief is incomplete, go ahead with what you have and list your assumptions.

**Dramaturgy:** hook with a problem the audience recognizes → promise → story or evidence → practical steps and examples → summary and one concrete action. In a workshop, budget time for demo, practice and questions. A deck that people read without you needs more context, or a separate version.

**Copy-paste brief:**
> Build a [PPTX / standalone HTML] for [N minutes] for [audience]. After the talk the listener should [action]. Use [sources] and keep [mandatory elements]. For each claim taken from my archive give the file name and slide number. Flag outdated numbers. Produce a script with speaker notes, export the deck, and check every frame at the size it will be shown.

## 2. Mine your own archive
Search the knowledge base by topic, audience, event name and synonyms in every language you speak. Open the original slides you find. Record *file + slide number* for reused stories, visuals and bio facts, and tell your original idea apart from an adaptation. Check the rights to photos, illustrations and logos.

## 3. The slide map
Keep the plan as a table and renumber it whenever you reorder:

| # | Job of the slide | Assertion (headline) | Evidence / visual | What I say | Source (file, #) | Check | Time |
|---|---|---|---|---|---|---|---|

- **One slide, one job:** hook, explain, prove, switch attention, give an instruction, or summarize.
- **Assertion-evidence** for explanatory slides. The headline states the conclusion ("Automation saves time on first drafts") and the body proves it with a diagram, chart, screenshot or example. This works especially well for technical content. Not every headline has to be a full sentence.
- Put on the slide only what the audience must *see*. Details go into the speaker notes or a handout.
- Never invent quotes, achievements, cases or statistics. Show the date, units and context for important numbers right on the slide.

## 4. Separate the jobs
Use different passes, even in the same chat:
1. **Gather:** facts and fragments with sources.
2. **Story:** order, transitions, the hook and the ending.
3. **Design:** layout, hierarchy, visuals.
4. **QA:** render and inspect.

Mixing these jobs is how you end up with pretty slides built on wrong facts.

## 5. Build an editable PPTX with code
An AI coding agent (Claude Code, Codex, etc.) with Python can build decks reproducibly:

- **`python-pptx`** creates and edits PPTX without PowerPoint: text, images, shapes, tables, charts and speaker notes. It doesn't cover every PPTX feature, so check complex templates, animation and media in the target app.
- Keep **text as text**: headings, captions and numbers go in editable text boxes, not baked into images.
- Set **alt text** on meaningful pictures (`pic._element.nvPicPr.cNvPr.set('descr', '...')`).
- Generate the **speaker notes from the same script file** you rehearse from, so the deck and the script never drift apart.
- Use 16:9 (13.333 × 7.5 in) unless the venue says otherwise.
- When editing an existing deck, **save under a new name**.
- Old slides can be **rendered from PDF with PyMuPDF** (`page.get_pixmap()`) and placed as evidence images with a caption "Archive: file, slide N".

See [`examples/build_deck.py`](../examples/build_deck.py). It turns a Markdown script into a 16:9 dark-theme deck with headers, footers, numbering and speaker notes.

Other options: **PptxGenJS** (JavaScript), the presentation features built into ChatGPT, Claude artifacts, or a standalone **HTML** deck when you need live search or interactive switches in a screencast.

## 6. Render and inspect
```bash
soffice --headless --convert-to pdf --outdir check talk.pptx
```
1. Make sure the slide count matches the page count.
2. Look at all pages as thumbnails, then open the suspicious ones at full size.
3. Check for overflowing or cut text and bad line breaks.
4. Check fonts, including Cyrillic and Latin in the same deck.
5. Check image crops, legends and captions, sources and contrast.
6. In the real PowerPoint, check notes, links, animation and embedded media.

LibreOffice output shows static rendering in LibreOffice. It **doesn't prove** PowerPoint compatibility. If you couldn't run a check, say so.

## 7. Rehearse
- Read the slide titles alone, as a story. Do they make sense?
- Check every number against the original.
- Say the whole talk out loud with a timer. Edit whatever doesn't sound like you.
- If you can, show a short fragment to someone from the target audience and ask them to repeat the main point back to you.

## Russian ↔ English
Adapt the talk, don't translate it word for word. Use understandable organization names, local examples, correct dates and units, and explain cultural references. Check how the speaker's name is spelled in official materials. After switching language, check line breaks again: English and Russian take up different space.

## Tool notes (as of late 2026)
- An **AI coding agent** works with the files and tools in *its* session. It is not PowerPoint, and local tools are not a local LLM: the model runs at the provider you selected.
- In the **OpenAI Responses API**, a PDF input gives the model both extracted text and page images, while PPTX gives text only. If the visual design matters, give the model a PDF. Check the docs for the product you actually use.

## Sources
- Microsoft: [Tips for creating and delivering an effective presentation](https://support.microsoft.com/en-us/office/tips-for-creating-and-delivering-an-effective-presentation-f43156b0-20d2-4c51-8345-0c337cefb88b)
- Microsoft: [Make your PowerPoint presentations accessible](https://support.microsoft.com/en-us/office/make-your-powerpoint-presentations-accessible-to-people-with-disabilities-6f7772b2-2f33-4bd2-8ca7-dae3b2b3ef25)
- Michael Alley / Penn State: [The Assertion-Evidence Approach](https://www.assertion-evidence.com/)
- [python-pptx documentation](https://python-pptx.readthedocs.io/en/latest/) · [PptxGenJS](https://gitbrent.github.io/PptxGenJS/)
- [LibreOffice command-line parameters](https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html)
- OpenAI: [File inputs (PDF)](https://developers.openai.com/api/docs/guides/pdf-files)
