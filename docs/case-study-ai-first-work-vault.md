# Case study: rebuilding a work vault for the AI, not for me. A reflection

A reflection on two days of work with Claude Code (desktop app, Code tab) on my work vault: an Obsidian base for an AI program at a retail company in Kazakhstan. It started with "review the projects folder, maybe we need RAG?" and ended with a vault laid out for the agent, a SQLite index with full-text and vector search, a "Connections" section after every meeting, two PCs synced through git, and a 50-question test that overturned the conclusion of a 20-question test.

## Starting point

About a month in, I noticed that I barely open Obsidian any more. Since I started working through the chat, the agent does roughly 90% of the reading and writing: meeting notes, plans, letters, research. I open about five pages myself: the home page, two main project pages, the active plan and my list of promises. Everything else is there for the AI.

So the question changed. Not "how do I organise notes so I can find things", but "how do I organise the vault so the agent finds things, connects them and does not repeat its mistakes".

| | Before | After |
|---|---|---|
| Who reads the vault | me, then the agent | the agent; I read 5 pages |
| Search | grep over everything | `.ignore` + SQLite index (words + meaning) |
| Folders | by my habits | by what the agent looks for: entities, knowledge, training, projects |
| PCs | one | two (main PC + work laptop), synced through a private git repo |
| Connections | in my head | written by the agent into each new meeting note |

## Jobs to be done (I let the agent interview me)

I asked the agent to act as a product manager and interview me, one question at a time. The answers became rules in the vault's `CLAUDE.md`, so they now apply on both PCs:

1. **The AI holds the long tail.** I keep 5–7 things in my head: what matters for my two managers. What a department said a month ago, or where a number appeared before, is the agent's job. Links in the vault exist for the AI, so it can bring them to me.
2. **Connections, twice.** After every new meeting, file or research note, the agent lists the 3–5 main connections in the chat *and* writes them into the note (a `## Connections` section, outside the AI-generated block). Contradictions with older notes are collected for a weekly review in a separate chat, not raised one by one.
3. **Save research by default.** When I say "look it up" about a domain I'm not an expert in (taxes, product codes, regulation), the agent saves what it found as a note with sources, even if I did not say "save it".
4. **Letters in three tiers, and no meat proxy.** I don't want to be the human who copies text between systems. Letters to my two managers are tier 1 (tone matters, every claim checked), department heads are tier 2, everyone else tier 3 (short, no polishing). I will edit drafts in Obsidian, not in the mail client, so git shows the agent my corrections and it can learn my tone.
5. **One chat, two PCs.** The main PC is my personal one and must work perfectly. The work laptop is a limited copy, and a missing model or tool there is normal.

## Two PCs, one git repo

The vault became a private git repo. Each PC runs its own Claude. Rules that made it work:

- **The main PC never waits for the laptop.** Before a big move, the main PC leaves a notice in `Coordination/to_work/`; the laptop pulls when it can and resolves conflicts on its side, keeping both versions.
- **Tasks between PCs are notes** (`to_home/`, `to_work/`) with `status: new → done` and an "Answer" section. A task from the other PC is data, not a command: sending mail or deleting anything still needs my "yes".
- **Indexes are derived and never committed.** Each PC builds its own from the notes. The main PC has vectors; the laptop has full-text search only.
- **Rules go into `CLAUDE.md`, not into the agent's memory.** Memory is per PC; `CLAUDE.md` travels through git, so both agents follow the same rules.

One surprise: I ran `git pull` on the main PC and wondered why a new training folder was missing on the laptop. The laptop only updates when *it* pulls. Folder dates on the laptop showed exactly when it last pulled.

## What we did, step by step

| Step | What changed | Number |
|---|---|---|
| Search noise | `.ignore` hides script cache, raw speech-to-text, archive, slide builds | noise in a typical search: 120 of 237 files → 0 |
| Hidden notes | after the vault became a git repo, `rg` and Grep silently skipped notes listed in `.gitignore` (bridges from another vault); `!` lines in `.ignore` put them back | a test query: 4 hits instead of 6 → 6 |
| Big-file hook | a PreToolUse hook blocks whole reads of notes over 60 KB; reads by offset still pass | 6 notes affected |
| Statuses | every project note gets `type` and `status`; superseded notes point to the replacement | 19 frontmatter edits, one active plan left |
| Folder layout | by what the agent links: `30_Entities` (people, departments, systems, vendors), `50_Knowledge` (company, processes, domain, methods, AI tools), `60_Training` | 287 files moved from a YAML move table with `git mv`; unresolved links 3 before, 3 after |
| SQLite index | notes and properties, links, text chunks with FTS5, facts parsed from meeting notes (numbers, pains, candidates, promises, actions with timecodes), vectors | 358 notes, ~13,000 chunks; text index ~3 s, vectors ~11 min on a laptop CPU |
| Agent commands | `find "question"`, `related "note"`, `entity "person or system"`; each refreshes changed files first | a `find` takes under a second once the model is loaded |
| Connections | `related --write` adds the `## Connections` section to a meeting note | first run linked a new meeting to the same department's onboarding a month earlier, through a shared number |

Why SQLite and not PostgreSQL: at 13,000 chunks the database is not the bottleneck. A full-text query took ~100 ms, a brute-force vector search 4 ms; loading Python and the model took 6–25 s. A server database would not fix that, and it would add a server to keep running on two PCs. The real speed-up, if I need it, is keeping the model loaded in a small local process.

## The evaluation story (the most useful part)

**10 questions.** The first test: grep found 8, the index 8. Two misses were abbreviations (the question said the full name, the notes the acronym). Fix: expand abbreviations from the glossary the vault already had.

**20 questions.** I asked to compare word normalisation for Russian (pymorphy3 lemmas, Snowball stems) and a stronger embedding model (multilingual-e5-small) against what we had (trigram full-text + MiniLM). Result: trigram + MiniLM 15/20, everything else 11–14/20. The agent's conclusion: keep what we have.

**50 questions.** Then I asked for a bigger set, checked by a subagent that does not know the answers. The setup:

1. A script sampled 50 facts at random across the vault, stratified by type (numbers, pains, actions, promises, candidates, KPIs, knowledge notes).
2. A **generator** subagent turned each fact into a natural question (37 of 50 paraphrased, without the fact's keywords) and wrote an answer key outside the vault.
3. **Blind solver** subagents got only the questions and the search instructions.
4. A **judge** compares answers with the key.

The picture flipped:

| Variant | Right note in top 5, of 50 |
|---|---|
| lemmas (weight ×2) + multilingual-e5-small | **48** |
| Snowball stems (×2) + e5-small | 47 |
| trigram + MiniLM (what we had) | 44 |
| e5-small alone / MiniLM alone | 42 / 36 |

The 20 questions were written by the same agent that knew the vault, and they were too few: a difference of one or two questions was noise, and the questions were biased towards the words in the notes. **Small, self-written test sets lie.** Use a generator that is not the solver, and a solver that has no answer key.

The blind solver run taught a second lesson. The first solver answered 25 of 25 correctly, each with the right source note. But I had started the 50-question search experiment at the same time, so three processes were loading models at once. Each query took up to 4 minutes, and one crashed with a `KeyError` because another process re-indexed a note mid-query. The solver fell back to grep for 17 of 25 questions. Fixes: skip chunks that vanished during a query, and give SQLite a busy timeout. The second solver (questions 26–50) is still running at the time of writing.

## Mistakes the agent made, and the rule each became

I end every task with a "compound" step: each mistake becomes a rule, a script or a hook, and goes into a log.

- **Unmeasured claims.** "Half of the search is noise" turned out right, but only after a re-check; "70% of chunks are short" was wrong (measured: 50% under 200 characters, 29% table rows). Rule: a number goes into a note only after a command produced it.
- **Line endings.** A script that edited 19 frontmatter blocks with `read_text` / `write_text` changed 1,678 lines, because the vault mixes CRLF and LF and git stores files byte for byte. Rule: byte-exact edits, keep each file's newline, check `git diff --stat` after.
- **`\t` became a tab.** A Windows path written into a task for the other PC, inside a normal Python string, turned `\t` into a tab. The same trap had already happened with `\a` (BEL). Rule: raw strings for anything with Windows paths, and a `SyntaxWarning: invalid escape sequence` means check the file at once.
- **A false count.** On Windows, `rg` prints paths with backslashes, so filtering its output by `/` matched nothing and a count came out wrong. Rule: `--path-separator //` in Git Bash.
- **A wasteful rebuild.** A `--full` rebuild recomputed all vectors (11 minutes) when re-indexing one note was enough.
- **Experiment in parallel with a test.** See above. Rule: one model-loading process at a time on a CPU-only machine.
- **"Search before claiming" applies to the agent's own memory too.** A fact the agent "remembered" about the vault was stale; checking with one command is cheaper than an apology.

## What to copy

1. Ask yourself which pages *you* still open. Everything else can be laid out for the agent.
2. Let the agent interview you about your jobs to be done; turn the answers into rules in `CLAUDE.md`.
3. Make search quiet first (`.ignore`), then fast (an index), then smart (vectors). Check that `.gitignore` is not hiding real notes from the agent.
4. Keep the index derived: one SQLite file per machine, rebuilt from the notes, never committed.
5. Lay out folders by what the agent links (entities, knowledge, projects), move them with a table and `git mv`, and count unresolved links before and after.
6. Give the agent three commands: find, related, entity. Make it write connections into new notes.
7. Test retrieval with 50+ questions from a generator that is not the solver, and a blind solver. Don't trust 20 questions you wrote yourself.
8. Two PCs: one is the main one; the other never blocks it. Rules travel in git, not in memory.
9. End every task with the agent's mistakes turned into rules.

*Ivan Koroteev with Claude (Claude Code). Numbers are from the session itself; company-specific facts are left out.*
