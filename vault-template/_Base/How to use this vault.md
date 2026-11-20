---
type: hub
auto: false
---

# How to use this vault

## Lifecycle of a talk
1. **Inbox.** A request arrives. Create a note from the *Organizer request* template.
2. **Event.** Once it's agreed, create a note from the *Event* template with `status: planned`. It appears on [[Home]].
3. **Prepare.**
   - Link the event to a topic in `Topics/`.
   - Take stories from `Story bank/`.
   - Find old slides by searching `Decks/`.
4. **Deliver.** Link the new deck from the event note.
5. **Debrief within 24h.** Write down the reaction, questions, what to improve and any leads. Set `status: done`.
6. **Proofs.** Add the thank-you letter, invoice, photos and video. Update the numbers in [[Speaker profile]].
7. **Harvest.** Every story, joke or case that worked becomes its own note in `Story bank/`.

## Rules
- One story per note. Link, don't copy.
- Property keys are in Latin (`year`, `topics`, `status`). Values can be in any language.
- `auto: true` means a script may regenerate the note. Set `auto: false` before you edit it by hand.
- `verified: false` means the value was inferred automatically. Check it before you use it in a media kit.
- Keep passports, bank details and contracts out of notes and out of search (`userIgnoreFilters` in `.obsidian/app.json`).

## Rebuild after adding files
```
python tools/build_knowledge_base.py "<this folder>"
python tools/ocr.py "<this folder>" --lang eng
python tools/build_obsidian_vault.py "<this folder>"
```
