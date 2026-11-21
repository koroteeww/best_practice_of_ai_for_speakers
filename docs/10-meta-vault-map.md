# 10 · Make the meta vault visible: a map of links between vaults

[Chapter 08](08-many-vaults-one-ai-chat.md) describes a meta vault: one AI chat that sees several Obsidian vaults, routes new material to the right one and creates short **bridge notes** between them. After two days of real use it had a blind spot, and the owner found it in one minute:

> "You build all these bridges *inside* the four vaults. I open the meta vault in Obsidian and see nothing of what we did. There is a routing log, but you can't tell from it what leads where."

He was right. The meta vault held rules, profiles and a text log. Every connection the AI had made lived in the child vaults, and Obsidian can't link across vaults: wikilinks, backlinks and the graph work only inside one vault. So the vault that was supposed to be the centre had an empty graph. The connections existed only in the AI's head and in two dozen scattered files.

This chapter is the fix: a **map** inside the meta vault, generated from the child vaults, so that you (and the next AI session) can *see* the network of vaults, projects, materials and links. It is in the template as `python scripts/scan.py map`.

## What not to do

There are two tempting fixes. Both are worse.

1. **Move the bridges into the meta vault.** Then a child vault is blind again. When you or an agent work *inside* the speaking vault, the bridge must be right there in its `Ideas/` folder. Keep the bridges where they are, and **mirror** them in the meta vault.
2. **Put all vaults inside the meta vault** (symlinks or junctions), so Obsidian sees 1,000+ notes in one graph. The NDA work vault ends up inside another vault, backups double, notes with the same name break each other's links, and the graph turns into a hairball. You lose the whole point of "only strong links".

## The map: four kinds of nodes

```
map/
├── 00 Map.md                 hub: vaults, a from→to matrix, projects, the decision log
├── vaults/    Vault — X.md   one per vault: profile, projects, incoming and outgoing links
├── projects/  Project — Y.md one per project: its materials and where they went
├── materials/ <title>.md     one per original that has a decision: home vault, obsidian:// link, project
└── links/     A → B — Z.md   one per link: accepted ✅, rejected ❌, deferred ⏸, home only 🏠
```

- A **material** node points to the original (vault + `obsidian://` link). **The text is never copied**: a fifth copy would only drift.
- A **link** node connects the material node to the vault hub on the other side, says *why* (the `meta_why` sentence of the bridge) and keeps the decision and its date.
- Because everything is ordinary `[[wikilinks]]` inside the meta vault, Obsidian's graph, backlinks and search work. The template's `.obsidian/graph.json` shows only `map/` and colours the four kinds of nodes differently.

## Rejected links belong on the map too

A map that shows only accepted bridges forgets every "no". Then the next session proposes the same weak link again. In real use about a third of all decisions were **rejections** ("the original is already in that vault", "personal, stays private", "no task for it there") and one was **deferred** ("a story only after the release, when there is proof"). They are links with a status, and the map draws them.

## Generated, never hand-edited

The map is rebuilt by the script at the end of every `scan`, so it can't drift from the vaults. Everything in `map/` has `auto: true` and is regenerated from two sources:

| Source | What it gives |
|---|---|
| Bridge notes in the child vaults (`meta_source` + `meta_why` in frontmatter) | Accepted links. The scanner finds them itself |
| `config/decisions.json` | Projects (name, status 🟢/🟡/⚪, home, folders), display titles for materials, and every decision: accepted, rejected, deferred, home only, with a date and a comment |

The AI's routine after any routing decision becomes: write the bridge (if accepted) → add the decision to `decisions.json` → one line in `routing_log.md` (the human history with your corrections) → `scan`. The map follows.

## Privacy on the map

The meta vault now shows *names* of notes from every vault, so the map needs its own privacy rule:

- `mask_titles: true` on an NDA vault in `config/vaults.json`. Its notes appear on the map only under an anonymized title from `decisions.json` ("Work — AI rollout meeting at a subsidiary"), never under the real file name, which often contains a person's or a company's name. Without a title the map shows an anonymous label.
- The `obsidian://` link still encodes the real path. It only works on your computer, but if the meta vault itself is ever shared, drop those links for masked vaults.
- The map never shows descriptions from a masked vault.

## Projects as hubs, with a relevance filter

Material usually belongs to a project, and a project has a home. The template adds `meta/projects.md`: one row per project with its home vault and a status.

- 🟢 **now**: serves your current priorities; bridges make sense.
- 🟡 **background**: alive, not in focus; bridges only on request.
- ⚪ **archive**: closed; no bridges, only a *story* (with proof) or a *lesson*.

This one filter removed a whole class of bad proposals. A closed project from another country is a fine story for a talk, but it is not worth building bridges into your current projects.

## Three more rules that real use added

1. **Fact ≠ goal.** In a bridge, every number is marked: *verified* (with a source), *reported by the source, not rechecked*, or *a goal or hypothesis*. "A million listeners" in a lyric is a wish, not a result. A site-reported play count is reported, not audited.
2. **Stories only from real events with proof.** A bridge into the story bank needs a post, a video, a document or a published article. Material without proof yet gets a **deferred** link, not a made-up story.
3. **Personal → out needs its own yes.** Even if you published a family story yourself, a bridge that carries biography out of the personal vault is approved separately.

## A real session in numbers

One session, six new files (a published personal article, a website UX playbook, a music-research report and three album drafts):

- **3 homes:** personal vault ×2, speaking vault ×1. Each new note is also linked from an existing one (an identity note, a project list, the speaker profile), so nothing is orphaned.
- **4 bridges.** The strongest came from the mechanism test. A report on *why listeners choose songs* (jobs-to-be-done) contained an interview protocol: "tell me about the last time…, what else could you have chosen?". With the music words removed, it is exactly the missing step in a city-development project: checking whether the planned products solve a real job *before* writing the one-pagers. The two notes share no keywords.
- **1 deferred** (a story waits for the release), **3 rejected**, with reasons.
- After the map: 4 vault hubs, 13 projects, 27 materials and 33 links, back-filled from two days of decisions. No broken links.

## Adding a vault

A new child vault is one entry in `config/vaults.json` (path, bridge folder, rules file, privacy, `mask_titles` if NDA) plus a short profile in `vaults/`. At the next `scan` its hub appears on the map with all its incoming and outgoing links. Nothing else changes, so the setup grows from four vaults to ten without redesign.

## Start

```bash
cp config/decisions.example.json config/decisions.json   # then replace the examples
python scripts/scan.py scan    # updates the registry and rebuilds map/
```

Open the meta vault in Obsidian → `map/00 Map.md` → graph view (Ctrl/Cmd+G).
