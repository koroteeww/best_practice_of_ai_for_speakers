# Examples

## Script → editable PPTX

```bash
python examples/build_deck.py examples/example_script.md -o examples/out/example.pptx
python tools/check_render.py examples/out/example.pptx      # PDF + PNG previews, needs LibreOffice
```

[`example_script.md`](example_script.md) is a 10-slide version of the [case-study screencast](../docs/case-study-screencast.md). It shows the script format:

- every `###` section is a slide;
- `layout:`, `label:`, `heading:`, `number:`, `text:`, `caption:`, `image:` and `alt:` set the slide;
- `- A | B` lines are cards or columns;
- `> ` lines are **what you say**. They become the speaker notes.

Because the deck and the speaker notes come from the same file you rehearse with, the slides and the script never drift apart.

### Why build decks with code?
- **Reproducible.** Change one line in the script, rebuild, re-check.
- **Consistent.** Header, footer, numbering, colours and typography come from one theme.
- **Editable.** All text stays text, so the organizer can still fix a typo in PowerPoint.
- **AI-friendly.** An AI coding agent can edit the script or the theme, rebuild, render to PNG and *look* at the result.

### Ask an AI agent to extend it
> Add a layout `quote` (big quotation marks, quote text, author line) and a layout `compare` (archive slide image on the left, new slide on the right). Rebuild `example_script.md`, render it with `tools/check_render.py`, look at every PNG, and fix any overflow.

## Image prompts
See [docs/06-storytelling-and-humor.md](../docs/06-storytelling-and-humor.md#memes-and-generated-images) for a stand-up-poster prompt template. Generate images *without* text and add captions in the slide.
