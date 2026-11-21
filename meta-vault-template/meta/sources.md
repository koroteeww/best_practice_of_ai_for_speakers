---
type: research
created: 2026-11-20
description: "Sources behind the meta vault: AI across several Obsidian vaults, and best practice for cross-domain links between knowledge bases"
---

# Research: what the meta vault is built on

Two web searches made on 20 November 2026. They are kept here so that any AI working with the meta vault knows where the rules in [CLAUDE.md](../CLAUDE.md) came from and can re-check the sources.

**Caveat:** most sources are blogs, forums and plugin pages, not research. The status of projects and plugins was not checked on the date of the search. Papers (arXiv, journals) were read only as abstracts and search excerpts.

## 1. Several Obsidian vaults and AI

### Conclusions
- **Obsidian doesn't link vaults.** Links and backlinks work inside one vault only, and forum requests for a "meta vault" have been open for years. Only `obsidian://open?vault=...&file=...` URIs work reliably, so bridges use them.
- **Cross-vault plugins exist** (Multi-Vault Navigator with `[[Vault::Note]]` syntax, Cross-Vault Sync that copies notes), but they have few downloads. The meta vault doesn't depend on them.
- **Claude Desktop can see several vaults through MCP** (obsidian-mcp, obx, Second Brain MCP). That's an option for the chat tab.
- **The common approach** is Claude Code + `CLAUDE.md` in the vault root + a separate service folder, and one topic per vault rather than one huge vault. Hence: separate vaults + a meta vault that adds them as extra directories.
- **A hash registry is common practice** (SHA-256 per file or per chunk; only changed files are re-processed). No ready-made registry for several vaults was found, so `scripts/scan.py` was written.
- **Semantic links** with embeddings: Reweave adds a wikilink by itself when cosine similarity is above 0.68. Postponed: vault profiles and note descriptions are enough for now.

### Sources
| Source | About |
|---|---|
| [Obsidian MCP setup guide (contextbolt)](https://contextbolt.com/blog/obsidian-mcp-claude/) | overview of MCP servers for Obsidian and how to set them up in Claude |
| [obsidian-mcp (stevenstavrakis)](https://playbooks.com/mcp/stevenstavrakis/obsidian-mcp) | MCP server: several vaults as arguments in `claude_desktop_config.json` |
| [obx configuration](https://zach-snell.github.io/obx/getting-started/configuration) | MCP server with vault switching (`allowed-vaults`) |
| [Second Brain MCP setup](https://glama.ai/mcp/servers/@CoMfUcIoS/obsidian-mcp-sb/blob/791837daeb717813a3d2fa78048cda6803e302da/SETUP.md) | several vaults as separate MCP server entries |
| [Cross-vault links (Obsidian forum)](https://forum.obsidian.md/t/cross-vault-links/28798) | links between vaults are not supported; workarounds |
| [Meta-vaults request (Obsidian forum)](https://forum.obsidian.md/t/allow-creation-of-meta-vaults-across-unrelated-folders/36640) | request for a "meta vault" over several folders, not implemented |
| [Multi-Vault Navigator](https://community.obsidian.md/plugins/multi-vault-navigator) | plugin: search across vaults and `[[Vault::Note]]` links |
| [Cross-Vault Sync](https://community.obsidian.md/plugins/cross-vault-sync) | plugin: copies notes between vaults via `sync_targets` frontmatter |
| [Kenneth Reitz: Obsidian vaults and Claude Code](https://kennethreitz.org/essays/2026-03-06-obsidian_vaults_and_claude_code) | essay: Obsidian vaults as a working environment for Claude Code |
| [Obsidian + Claude Code integration guide (starmorph)](https://blog.starmorph.com/blog/obsidian-claude-code-integration-guide) | full integration guide, `CLAUDE.md` as the control file |
| [Agent-readable vault setup (okhlopkov)](https://okhlopkov.com/second-brain-obsidian-claude-code/) | how to structure a vault so an agent reads it well |
| [SHA-256 for RAG change detection (DEV)](https://dev.to/asquare8/why-i-used-sha-256-to-solve-a-problem-most-rag-tutorials-pretend-doesnt-exist-2gbc) | hash so unchanged files aren't re-processed; downside: renaming a heading changes the hash too |
| [Basic Memory: how it works](https://www.mintlify.com/basicmachines-co/basic-memory/concepts/how-it-works) | Markdown knowledge base, detects changes with SHA-256 |
| [markdown-vault-mcp](https://socket.dev/pypi/package/markdown-vault-mcp) | MCP: re-indexes by hash, hybrid semantic search |
| [Reweave semantic links](https://vachsark-homepage.pages.dev/blog/reweave-semantic-links) | adds wikilinks by embeddings, similarity threshold 0.68 |

## 2. Cross-domain connections: best practice

### Conclusions that became rules
- **Cross-domain links are rare and valuable, and they don't appear by themselves.** According to one analysis of Luhmann's Zettelkasten, only about 2% of its links crossed between its two main parts. The system doesn't make links on its own. Hence: at most 5 bridges per digest and the one-sentence test.
- **The "everything is connected to everything" trap.** Deleting extra links is better than collecting them. Hence the "clean up the bridges" command.
- **Link when you create a note.** A regular review is the safety net. If the number of notes grows and no new links appear, the practice is dead. Hence: bridge checks when filing from the inbox, plus the digest.
- **Boundary objects.** Knowledge crosses between fields better through a shared, adapted artifact than through a copy. A simple transfer works when the context is shared; when contexts differ, it has to be re-interpreted for the new place. Hence: a bridge instead of a copy, written in the target vault's language.
- **Of-knowledge and about-knowledge.** Neighbouring fields usually need a general idea of the material, not deep knowledge. Hence: 2–5 lines in a bridge, not a summary.
- **The same concept has different names in different fields,** so agree on terms first. Hence the [glossary](glossary.md).
- **Analogy search by mechanism.** Classic literature-based discovery links fields through a shared term (A–B–C). Newer LLM work strips the domain vocabulary and compares the problem itself, so it finds analogies with no shared words. Hence the "by mechanism" check in `CLAUDE.md`. In the first digest it found the most valuable link: "citizen engagement" → "a community of AI practitioners".

### Sources
| Source | About |
|---|---|
| [Can AI bridge disciplinary boundaries?](https://rachelageorge.substack.com/p/can-ai-bridge-disciplinary-boundaries) | interdisciplinarity alone isn't enough, you need a shared process; fields understand terms differently |
| [What Does it Mean to be a Knowledge Integrator? (Waterloo)](https://uwaterloo.ca/knowledge-integration/resources/what-does-it-mean-be-knowledge-integrator) | an integrator knows other fields' language and methods well enough to connect them |
| [Of-Knowledge vs About-Knowledge (EU Journal of Futures Research)](https://eujournalfuturesresearch.springeropen.com/track/pdf/10.1186/s40309-018-0150-z) | deep knowledge vs a general idea: which level you need depends on the task |
| [Team Science Best Practice #2](https://theteamsciencelab.substack.com/p/team-science-best-practice-2-facilitate) | discuss approaches and methods across disciplines early, before problems appear |
| [What Luhmann's Zettelkasten Teaches Us](https://martijnaslander.github.io/luhmann-zettelkasten/blog/lessons-for-knowledge-systems.html) | analysis of Luhmann's archive: ~2% of links between parts, most links structural (secondary source) |
| [Zettelkasten connection practice](https://commons-os.github.io/patterns/zettelkasten-connection-practice/) | review the network regularly; the sign of a dead practice is no new links |
| [Zettelkasten Forum: Schmidt on serendipity](https://forum.zettelkasten.de/discussion/comment/6925) | Schmidt: the archive produces unexpected knowledge by linking dissimilar ideas (serendipity after Merton) |
| [Revisiting Luhmann's 1981 article](https://danallosso.substack.com/p/revisiting-luhmanns-1981-zettelkasten) | the system doesn't make links by itself; they have to be written down |
| [Boundary objects in KM research (XJTLU)](https://scholar.xjtlu.edu.cn/en/publications/application-of-boundary-objects-in-knowledge-management-research-) | review 2008–2018: boundary objects support shared understanding and knowledge transfer |
| [Knowing across boundaries (JKM)](https://unpaywall.org/10.1108%2FJKM-05-2015-0194) | knowledge brokers and boundary objects in exchange between groups |
| [Boundary Spanning (concept wiki)](https://concepts.dsebastien.net/concept/boundary-spanning/) | crossing boundaries in a personal knowledge system: read across disciplines and link notes from different areas |
| [Recent Advances in Literature-Based Discovery](https://arxiv.org/pdf/2506.12385) | survey of LBD since 2000: Swanson's A–B–C model |
| [Make LBD Great Again](https://arxiv.org/pdf/2502.16450) | reproducible LBD pipelines; LLMs help describe fields and find bridging terms |
| [Idea-Catalyst / Sparking Scientific Creativity](https://www.alphaxiv.org/abs/2603.12226) | restate the problem without its domain and look for analogies in distant fields |
| [Same Problem, Different Field](https://arxiv.org/pdf/2609.07595) | strip domain vocabulary and compare the mechanism: finds pairs with no shared terms |
