# Case study: one month with an AI agent, in numbers

What came of one month (25 Oct to 24 Nov 2026, with nearly all the work done between 9 and 24 November) of building personal knowledge vaults with Claude Code. I did not estimate any of these numbers. A script counted the files in the vaults, and the rest comes from Claude Code's built-in usage report (`/insights`). The method itself is in [03 · Knowledge base pipeline](03-ai-knowledge-base-pipeline.md), [08 · Many vaults, one AI chat](08-many-vaults-one-ai-chat.md) and [10 · Meta vault map](10-meta-vault-map.md). This page answers one question: **how much can one person build in a month, and what did it really take?**

## The short version

Five connected Obsidian vaults hold **1,210 notes** and about **13,500 internal links**. The agent wrote about **6,000 lines of Python** to build and maintain them. I wrote almost none of the text myself: I set the tasks, made the decisions and corrected the meaning.

## Vault by vault

Counts were taken on 24 Nov 2026 and cover Markdown notes only, without settings, trash or attachments. "New" means the file was created during the month.

| Vault | Notes | New this month | Links | What's inside |
|---|---:|---:|---:|---|
| Personal | 117 | 87 (+22 older notes extended) | ~1,100 | reflection, research and sources, projects, timeline |
| Work (NDA) | 357 | 304 | ~4,400 | meetings, processes, methods, reference |
| Study program on new cities | 258 | 258 | ~3,800 | 49 lectures, 41 people, 47 concepts, 20 organizations |
| Speaking | 364 | 364 | ~3,500 | 281 deck cards, 38 events, 8 topics, story bank, ideas |
| Meta vault | 114 | 114 | ~700 | the map of links between vaults; 93 of its notes are generated |
| **Total** | **1,210** | **1,127** | **~13,500** | |

The speaking vault sits on top of a 6-year archive: 1,250 files (about 12 GB), indexed into 8,826 searchable units (slides, PDF pages and documents). Of the 8,291 slides that contain text, only 2,951 are unique, so **about two out of three slides were copies**. See [case-study-screencast](case-study-screencast.md) for what that index made possible.

Around the vaults the agent also built:
- a meta vault with 13 projects and 35 recorded routing decisions, rejections included, plus about 30 bridges between vaults;
- a Telegram bot that drops ideas into the meta vault's inbox;
- a weekly backup of every vault to two cloud drives;
- two public methodology repositories, including this one.

## How the work went

From Claude Code's usage report for 9–21 Nov. It covers all my sessions in that window, not only the vault work.

- **71 sessions, 578 messages from me, 12 active days**, so about 48 messages a day.
- **511 files changed, +43,727 lines.** Markdown far outweighed code: 704 Markdown edits against 338 in Python.
- **Median time for me to reply: 2.3 minutes.** 27% of my messages were sent while several sessions ran in parallel.
- **Outcomes:** 23 sessions fully achieved, 26 mostly achieved, 1 unclear.
- **Friction:** 19 times the agent misunderstood the request, and 19 times it picked the wrong approach. There were also 9 cases of buggy code.

About 18 sessions went into the knowledge vaults. The rest were work deliverables, small automation tools, publishing, and personal admin.

## Vaults are born in a day

| Day | What happened |
|---|---|
| 11 Nov | work vault: 128 notes |
| 18 Nov | study-program vault: 247 notes |
| 20 Nov | speaking vault: 337 notes generated from the indexed archive |
| 23 Nov | meta vault map: 92 notes regenerated |

After each spike came days of small additions: a transcript, a call note, a bridge, a rule. **Building a vault takes a day. Deciding what goes where takes weeks.**

## What I learned

1. **The AI didn't write for me. It organized what I already had.** The vaults hold about 1.3 million words, and I typed almost none of them. They are transcripts, lectures, OCR'd slides and exported chats that had sat unread for years. Now they can be found and linked. Be honest about this when you quote numbers: "1,210 notes" doesn't mean "1,210 notes I wrote".
2. **The bottleneck is my decisions, not the agent's speed.** The agent can generate 250 notes in an afternoon. Whether a note lives in the personal or the work vault, and whether it deserves a bridge at all, is my call. Most of the time the right answer is "one vault only".
3. **Links and rules matter more than note count.** The useful output is the ~13,500 links, the 35 routing decisions (rejections are decisions too) and the `CLAUDE.md` rules in every vault. Those rules are why the next session doesn't repeat the last session's mistake.
4. **A rule in a file beats a rule in my head.** Once a correction was written into `CLAUDE.md`, the mistake stopped coming back. When I only said it in chat, it came back in the next session.
5. **Verification is the weak spot.** The typical failures were the same few: answering from general knowledge instead of searching my own vault, links that were never opened, a "master" file broken while notes were being moved, and not stopping at once when told to. All of these are fixed by standing rules and checks, not by better prompts.
6. **My role is editor-in-chief.** I send one message with several tasks, let the agent run, and correct intent rather than syntax. 578 messages in 12 days is a lot of steering. The agent is a very fast junior colleague, not an expert.

## Privacy

This page gives counts only. It shows no note titles, names, company details or quotes. The work vault is under NDA, so only its size and folder types are listed. The usage report also contains personal topics, and those are summarized as "personal admin". Use the same rule for your own numbers: **publish counts and lessons, never content.**

## Reproduce it

Count your own vaults the same way: walk each vault, skip `.obsidian` and trash, count `.md` files, `[[links]]` and files created after a date. Then run `/insights` in Claude Code for the session side. Do it again a month later and compare.
