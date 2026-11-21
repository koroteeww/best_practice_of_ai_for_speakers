# Meta vault: a dispatcher for several Obsidian vaults

You work from the meta vault. All vaults listed in [config/vaults.json](config/vaults.json) are visible from here (they are added as extra directories in `.claude/settings.json`). Your job is to decide where new material goes and to find useful connections between vaults, **without dragging everything everywhere**.

| id | Vault | Profile |
|---|---|---|
| `personal` | personal notes, reflection | `vaults/personal.md` |
| `work` | day job, **NDA** | `vaults/work.md` |
| `project` | a big side project | `vaults/project.md` |
| `speaking` | talks, events, story bank | [vaults/speaking.md](vaults/speaking.md) |

*Edit this table to match your vaults. Write the missing profiles from [vaults/example-profile.md](vaults/example-profile.md).* Why the rules below look the way they do: [meta/sources.md](meta/sources.md).

## The map in this vault (what the owner actually sees)
This vault is the centre. Everything done between vaults must be visible here as links: [map/00 Map.md](map/00%20Map.md).
- `map/vaults/` — a hub per vault; `map/projects/` — a hub per project; `map/materials/` — a node per original that has a decision (home, `obsidian://` link, project; **the text is never copied**); `map/links/` — a node per link: accepted ✅, rejected ❌, deferred ⏸, home only 🏠.
- Everything in `map/` is `auto: true` and rebuilt by `python scripts/scan.py map` (it also runs at the end of `scan`). Never edit it by hand.
- **Source of truth:** accepted bridges are found by the scanner via `meta_source`; projects, display titles and every decision (including rejections and deferrals) live in [config/decisions.json](config/decisions.json).
- Bridges stay in the child vaults, where they are needed while working inside a vault. The map mirrors them, it doesn't replace them.
- A vault with `mask_titles: true` (NDA) appears on the map only under anonymized titles from `decisions.json`: no names of people or companies.

## Before writing to any vault
1. Read the vault's profile in `vaults/`.
2. Read **the vault's own rules** (`rules_file` in the config). They win over the rules below: format, frontmatter, folders, what must not be touched.
3. Check whether a similar note already exists: `python scripts/scan.py find <word>` plus a search in the vault. Appending to an existing note is better than creating a new one.
4. If the material belongs to a project, check [meta/projects.md](meta/projects.md): where the project lives and whether it is 🟢 now / 🟡 background / ⚪ archive. No bridges for ⚪.

## Rules
1. **One home.** Each piece of material has one main vault. The original lives only there.
2. **A bridge, not a copy.** Another vault gets a short bridge note ([templates/bridge.md](templates/bridge.md)): 2–5 lines in *that* vault's language about which of *its* tasks this solves, plus an `obsidian://` link to the original. Text is not copied.
3. **One-sentence test.** Propose a bridge only if you can say in one sentence which **specific task** it solves in the other vault. "Might be useful" fails. Most often the right answer is "one vault only".
4. **Two checks for a connection:**
   - *by topic*: overlap with the "Interests in other vaults" section of the profiles;
   - *by mechanism* (most valuable): strip the domain vocabulary and state the problem abstractly ("keep the attention of a group of strangers", "get people to accept a top-down change"). Then look for the same problem in the other vaults, described in other words. Use [meta/glossary.md](meta/glossary.md) to map terms between vaults.
5. **The owner decides.** Bridges are only proposed first (in a reply or a digest). Write to vaults only after a "yes".
6. **At most 5 bridge proposals per digest**, strongest first. Skip a weak link rather than make everything connected to everything.
7. **Fact ≠ goal.** Mark every number in a bridge: verified (with a source), reported by the source but not rechecked, or a goal/hypothesis. Stories for the speaking vault come only from real events with proof (a post, a video, a document). No proof yet → a **deferred** link, never an invented or "averaged" story.

## Owner's decisions about where topics live
- *(Record routing decisions here, e.g. "General material on AI tools → personal vault, `Sources/AI tools/`; bridges in work and speaking." Add the date.)*

## Privacy
- **Work (NDA) → out:** only anonymized methods and conclusions. No names, company numbers, vendors, offers, quotes from transcripts. The owner approves each such bridge separately.
- **Personal → out:** only ideas and techniques. No biography, money, debts, relationships or health unless explicitly allowed.
- Folders listed in `readonly` are never edited. Don't bulk-read large raw transcripts.

## Scenarios

### "File this" (a link, text, file, or files in `inbox/`)
1. Say what it is in 1–2 sentences.
2. Pick the **main vault** and the exact folder by its rules. Explain why in one line.
3. Check bridges (rules 3–4). For each other vault: "bridge: yes/no, because…".
4. Show the plan: main vault + 0–2 bridges. After confirmation, write, remove the file from `inbox/`, add every decision (accepted and rejected) to `config/decisions.json`, a line to [routing_log.md](routing_log.md), then run `python scripts/scan.py scan` so the map is rebuilt. A new project is a row in `meta/projects.md` and in `projects` in `decisions.json`.

### "What's new" / digest
1. `python scripts/scan.py scan`, then read `registry/pending.json` (only new and changed notes).
2. Read only the notes from that list, large ones in parts. Skip bridges (`meta_source` in frontmatter).
3. Write `digests/YYYY-MM-DD.md` from [templates/digest.md](templates/digest.md): a short summary per vault, then up to 5 proposed bridges with checkboxes.
4. When the owner has ticked boxes, create the ticked bridges, record all decisions in `config/decisions.json` and `routing_log.md`, run `python scripts/scan.py scan` (rebuilds the map), then `python scripts/scan.py ack --all`.

### "Clean up the bridges"
`python scripts/scan.py stats`: bridges with no edits for 180+ days and bridges whose original is gone. Propose deleting or updating. Delete nothing without a "yes".

### Backup
`python scripts/backup.py` zips every vault and this folder into the destinations in `config/backup.json`. Archives have no password by default; `encrypt: true` per vault turns on AES-256 via 7-Zip with the password from `OBSIDIAN_BACKUP_PASSWORD`. Never write passwords into files. Don't turn on encryption unless the owner asks for it.

## Bridge notes
- Go into the target vault's `bridge_folder` from the config, following that vault's rules (frontmatter, language, link format).
- Required frontmatter: `meta_source: <vault_id>:<path to original>` (the scanner counts bridges by it) and `meta_why: <one sentence>`.
- Link to the original: `python scripts/scan.py uri <vault_id>:<path>`.

## Adding a vault
One entry in `config/vaults.json` (id, path, `bridge_folder`, `rules_file`, privacy, `mask_titles: true` if NDA) and a profile in `vaults/<id>.md`. Its hub and links appear on the map at the next `scan`.

## Learning from decisions
Every decision, including a rejected bridge, is a line in `routing_log.md`. If the owner corrects a route, log the correction and, if it is a rule, add it to the vault profile or to "Owner's decisions" above. Read the latest log entries before a new decision.
