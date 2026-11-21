# 08 · Many Obsidian vaults, one AI chat: the meta vault

Most speakers don't have one knowledge base. They have several: a personal one, one for the day job, one per big project, and one for talks. A good article or a new idea is often useful to two or three of them at once. Then the usual options are all bad:

- **Copy it everywhere.** Three copies drift apart, and soon you don't know which is the real one.
- **Open three or four AI chats**, one per vault. You end up explaining the same thing four times.
- **Use separate "projects" in an AI app.** Each project only sees its own files, so no project can see a connection between vaults.
- **Merge everything into one huge vault.** The work vault has an NDA, the personal one is private, and the speaking one is semi-public. They don't belong together.

This chapter describes a small **meta vault**: a folder that routes new material to the right vault and finds connections *between* vaults without moving everything around. It has been running on four real vaults with about 1,000 notes. A ready-to-copy template is in [`meta-vault-template/`](../meta-vault-template/), and the story of how it was built is in [the case study](case-study-meta-vault.md).

## The idea in one picture

```
            ┌──────────────── meta vault (one AI chat opens this) ───────────────┐
            │  CLAUDE.md      rules: one home, bridges, privacy, scenarios         │
            │  vaults/*.md    a profile for each vault: purpose, topics, interests │
            │  registry/      SQLite with a SHA-256 hash of every note             │
            │  digests/       "what's new" + up to 5 proposed bridges              │
            │  routing_log.md every decision, so the AI learns your corrections    │
            └───────┬──────────────┬──────────────┬──────────────┬────────────────┘
                    │              │              │              │
               personal          work          project        speaking
                vault        vault (NDA)        vault           vault
```

The vaults stay where they are and keep their own rules. The meta vault only reads them, and writes to them only after you say yes.

## How the AI sees all vaults from one chat

Obsidian itself does not link vaults: wikilinks and backlinks work only inside one vault. Two ways around it:

1. **Claude Code (or the Code tab in the Claude desktop app)**: open the meta vault folder and add the other vaults as extra working directories in `.claude/settings.json`:

   ```json
   {
     "permissions": {
       "additionalDirectories": [
         "D:/Vaults/Personal",
         "D:/Vaults/Work",
         "D:/Vaults/Project",
         "D:/Vaults/Speaking"
       ]
     }
   }
   ```

2. **Claude Desktop chat with an Obsidian MCP server** that accepts several vaults. This works too, but the folder approach is simpler and needs no extra software.

Other agents (Codex, Cursor, Gemini CLI) can use the same folder: `AGENTS.md` sends them to the same rules.

## Six rules

1. **One home.** Each piece of material has one main vault. The original lives only there.
2. **A bridge, not a copy.** Another vault gets a short **bridge note**: 2–5 lines, written in *that* vault's language, saying which of *its* tasks this solves, plus an `obsidian://open?...` link to the original. The text itself is not copied.
3. **The one-sentence test.** Propose a bridge only if you can say in one sentence which **specific task** it solves in the other vault. "Might be useful" fails the test. Most of the time the right answer is "this lives in one vault only".
4. **Check connections two ways.**
   - *By topic*: does it overlap with the "interests in other vaults" section of a vault profile?
   - *By mechanism* (the most valuable one): strip the domain words out of the material and state the problem in plain terms, such as "keep the attention of a group of strangers" or "get people to accept a change that comes from the top". Then look for the same problem in the other vaults, where it is described in different words. A small glossary maps one idea to the words each vault uses.
5. **You decide.** The AI only proposes bridges, in a reply or in a digest. It writes to a vault only after your "yes".
6. **At most five bridge proposals per digest**, strongest first. A weak link is worse than no link: if everything is connected to everything, nothing is.

Where these rules come from: in Luhmann's Zettelkasten only about 2% of links crossed between its main parts, cross-domain links are rare and valuable, and they don't appear by themselves. Knowledge-management research on *boundary objects* says knowledge crosses between fields better as an adapted shared artifact than as a copy. Recent work on LLM-based analogy search says that removing domain vocabulary finds analogies that share no keywords. All 30 sources are listed in [`meta-vault-template/meta/sources.md`](../meta-vault-template/meta/sources.md).

## Why this matters for a speaker

The speaking vault is usually the vault that **receives the most**. Your work gives you cases, your projects give you examples, and your personal notes give you stories and lessons. Bridges bring all of that into the speaking vault as short, ready-to-use pointers, without leaking private or NDA details. In the first digest on real vaults:

- an internal corporate AI training (work vault) became an anonymized **event note** with a lesson for the next talk: "they needed a workshop, not a lecture";
- notes on presentation skills from a project vault became an idea note: "meaning beats slides, a counterweight to AI-generated decks";
- the strongest link came from the **mechanism test**: "citizen engagement" in an urban-development vault and "building a community of AI practitioners" in the work vault are the same problem (getting people to take part in a change they didn't ask for), described with no shared keywords.

## The registry: notice what changed

You can't ask an AI to re-read 1,000 notes every day. The registry script (`scripts/scan.py`, Python standard library only) keeps a SQLite table with one row per note: vault, path, SHA-256 hash, title, `type`, `description`, tags, word count, and the hash at the last review.

```bash
python scripts/scan.py scan      # walk all vaults; first run = baseline
python scripts/scan.py pending   # new and changed notes not reviewed yet
python scripts/scan.py ack --all # after a digest, mark everything reviewed
python scripts/scan.py find "storytelling"   # search all vaults at once
python scripts/scan.py stats     # bridges older than 180 days, bridges whose original is gone
python scripts/scan.py uri work:Methods/Note.md   # obsidian:// link for a bridge
```

On the **first run everything that exists is taken as the baseline**, so you don't start with a queue of 1,000 notes. After that, only what changed shows up in the digest.

## Three scenarios

| You say | The AI does |
|---|---|
| "File this: `<link, text or file>`" (or drop files into `inbox/`) | States what it is in 1–2 sentences → picks the main vault and the exact folder by that vault's rules → for every other vault, "bridge: yes/no, because…" → shows the plan → writes only after your yes → logs the decision |
| "What's new?" | Runs the scan, reads only the new and changed notes, writes `digests/YYYY-MM-DD.md`: a short summary per vault + up to 5 proposed bridges with checkboxes. You tick the ones you want, it creates them |
| "Clean up the bridges" | Lists bridges with no edits for 180+ days and bridges whose original disappeared. Deletes nothing without your yes |

Every decision, including every rejected bridge, goes into `routing_log.md`. When you correct a route ("no, AI tools live in my personal vault"), the correction becomes a rule in `CLAUDE.md`, so you don't have to say it twice.

## Privacy is part of the design

- **Each vault's own rules come first.** Before writing anywhere, the AI reads that vault's profile and its own `CLAUDE.md`, `AGENTS.md` or "how to use this vault" note.
- **Work (NDA) → out:** only anonymized methods and conclusions. No names, company numbers, vendors, offers or quotes from transcripts. You approve every such bridge on its own.
- **Personal → out:** only ideas and techniques. No biography, money, debts, relationships or health unless you explicitly allow it.
- Read-only folders (raw transcripts, sources) are listed in the config, and the AI never edits them.

## Weekly backup

Once several vaults depend on one setup, back them up. `scripts/backup.py` zips every vault and the meta vault itself, then copies the archives into folders that Dropbox, Google Drive or OneDrive already sync. It keeps the last 6 archives per vault, skips files over 20 MB (usually PPTX and PDF that have originals elsewhere) and lists them in the log. Encryption is opt-in per vault (`encrypt: true`, AES-256 via 7-Zip, password only from an environment variable). On Windows, register it in Task Scheduler with "run as soon as possible after a missed start", so a laptop that was off on Sunday evening still gets its backup on Monday morning.

## Start in 15 minutes

1. Copy [`meta-vault-template/`](../meta-vault-template/) next to your vaults.
2. Fill `config/vaults.json` (paths, which folder takes bridges, which folders are read-only, privacy level).
3. Write one short profile per vault in `vaults/`: purpose, topics, what goes in, what doesn't, interests in other vaults.
4. Add the vault paths to `.claude/settings.json` and open the folder in Claude Code.
5. Run `python scripts/scan.py scan`, then say: **"What's new? Write the first digest."**
