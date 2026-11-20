# 02 · An Obsidian vault for speakers

Obsidian works well for a speaker's knowledge base:
- the notes are plain Markdown files on your own disk;
- links between notes are first-class;
- **Bases** (a core plugin since Obsidian 1.9) turns note properties into sortable, filterable tables without any community plugin.

## Make the whole archive the vault

Open your **existing speaker folder** as the vault, and keep all generated and handwritten notes in one subfolder (`_Base/`). Then:
- the originals stay where they are, so nothing moves and nothing breaks;
- notes can link straight to `Kazan_2022/talk.pptx` or embed `![[photos/stage.jpg|200]]`;
- folders you don't want indexed go into `userIgnoreFilters` in `.obsidian/app.json`, such as thumbnails, voice datasets and private documents.

```
Talks/                      ← vault root = your existing archive
├── .obsidian/
├── _ai/                    ← SQLite knowledge base, logs (generated)
├── _Base/                  ← all notes live here
│   ├── Home.md             ← dashboard and navigation
│   ├── Speaker profile.md  ← single source of truth for bio, numbers, proofs
│   ├── How to use this vault.md
│   ├── Events.base         ← table views: by year, planned, paid, needs check
│   ├── Decks.base          ← table views: all, recent, English, best-rated
│   ├── Topics/             ← signature talks (one note per topic)
│   ├── Events/             ← one note per event or series
│   ├── Decks/              ← one note per deck with full slide text
│   ├── Story bank/         ← reusable stories, cases, numbers, jokes, demos
│   ├── Ideas/  Inbox/      ← raw input
│   └── Templates/
├── 2024_Tomsk/ …           ← your original folders, untouched
```

## Note types and properties

Use **Latin property keys** so Bases, Dataview and scripts can rely on them. Values can be in any language.

| Note type | Key properties |
|---|---|
| `event` | `date`, `year`, `city`, `venue`, `format`, `duration_min`, `audience`, `audience_size`, `topics`, `organizer`, `paid`, `fee`, `status` (`request` → `planned` → `done`), `video_link`, `verified` |
| `deck` | `event`, `year`, `topics`, `lang`, `slides`, `files`, `rating`, `used_again`, `verified` |
| `topic` | `status` (`active`, `draft`, `retired`) |
| `story` | `kind` (story, case, number, joke, quote, demo), `topics`, `hook`, `source`, `checked`, `used_in`, `works` |
| `request` | `received`, `organizer`, `event_date`, `fee`, `status` |

`auto: true` marks notes that a script may regenerate. Before you edit one by hand, set it to `auto: false`.

## The lifecycle of one talk

1. **Inbox.** An organizer writes to you. Create a note from the *Organizer request* template with the date, audience, format and fee.
2. **Event.** Once it's agreed, create an *Event* note with `status: planned`. It shows up on the Home dashboard.
3. **Prepare.**
   - Link the event to a **Topic**. Take the synopsis and key points from the topic note.
   - Take stories from the **Story bank**.
   - Find old slides with full-text search over `Decks/`, which holds the text of every slide.
4. **Deliver.** Link the new PPTX or PDF from the event note.
5. **Debrief within 24 hours.** Write down the audience reaction, questions from the room, what to improve and any leads. Set `status: done`.
6. **Proofs.** Put the thank-you letter, invoice or act, photos and video link in the event folder. Update the numbers in *Speaker profile* (e.g. "50+ talks").
7. **Harvest.** Every story, joke or case that worked becomes its own note in the Story bank. That's how it gets found next time.

## Hub notes (Maps of Content)

- **Home**: navigation, upcoming events, talks by year, recent decks.
- **Topic notes**: a synopsis for organizers, key points, versions for 15, 45 and 90 minutes, and links to every event and deck on the topic. An embedded Base lists the topic's stories.
- **Speaker profile**: a 30-second intro for the host, numbers, credentials, video links, press, and documents for organizers. Update it here first, then rebuild the media kit from it.
- **Proofs**: thank-you letters, certificates, contracts and acts for paid talks. Link to these files but don't extract their text, because they contain personal data.

## Bases examples

```yaml
# Events.base
filters:
  and:
    - file.inFolder("_Base/Events")
views:
  - type: table
    name: By year
    groupBy:
      property: note.year
      direction: DESC
    order: [file.name, note.city, note.format, note.audience, note.status, note.verified]
  - type: table
    name: Planned
    filters:
      or:
        - note.status == "planned"
        - note.status == "request"
    order: [file.name, note.date, note.city, note.fee]
```

To embed one view in a note: `![[Events.base#Planned]]`. To show the stories of a topic inside the topic note:

````markdown
```base
filters:
  and:
    - file.inFolder("_Base/Story bank")
    - topics.contains(link("AI for business"))
views:
  - type: table
    name: Stories
    order: [file.name, hook, used_in]
```
````

## Useful plugins (optional)

| Plugin | Why |
|---|---|
| **Bases** (core) | Dashboards without code |
| **Templates** (core) | Event, story, topic, request and deck templates |
| **Slides** (core) / **Advanced Slides** / **Take the Floor** | Present a note as slides, with speaker notes on your own screen |
| **Outliner** | Write the talk as a tree. Some speakers read the outline on stage instead of a teleprompter. Rehearse on the device you'll use on stage |
| **Dataview** | Queries more complex than Bases can do |
| **Omnisearch** | Smart search, including the text inside PDFs |

## Rules that keep the vault useful

- **One story per note** in the Story bank, so a story can serve any topic.
- **Link, don't copy.** Reference slides and files instead of pasting their content into new notes.
- **Don't split the vault.** One vault makes surprising connections more likely.
- **Ignore the noise.** Keep thumbnails, voice datasets, saved web pages (`*_files/`) and private documents out of search and the graph.
- **Weekly inbox review.** Each item becomes an event, a story or an idea, or gets deleted.

## Sources and inspiration
- Obsidian Help: [Bases](https://help.obsidian.md/bases), [Properties](https://help.obsidian.md/properties), [Templates](https://help.obsidian.md/plugins/templates)
- [Take the Floor plugin](https://community.obsidian.md/plugins/take-the-floor)
- [Academic Obsidian (talks and papers as source notes linked to topics)](https://www.emilevankrieken.com/blog/2025/academic-obsidian)
- [10 PKM lessons from using Obsidian every day](https://recapio.com/digest/10-essential-pkm-lessons-from-using-obsidian-every-day-for-5-years-by-mike-schmitz)
- [Obsidian meeting template with people and project links](https://www.obsibrain.com/blog/obsidian-meeting-template-get-organized-get-productive)
- [An introduction to Dataview](https://publish.obsidian.md/hub/04+-+Guides%2C+Workflows%2C+%26+Courses/Guides/An+Introduction+to+Dataview)
