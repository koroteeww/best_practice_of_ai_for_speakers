# AGENTS.md

Instructions for any AI agent (Codex, Gemini CLI, Cursor and others) working in this folder.

All rules are in [CLAUDE.md](CLAUDE.md). They are written for Claude but fit any agent: read that file first and follow it.

Reading order:
1. [CLAUDE.md](CLAUDE.md): purpose, rules, privacy, scenarios.
2. [config/vaults.json](config/vaults.json): paths to the vaults. If you can't see them as extra directories, open them by these absolute paths.
3. `vaults/*.md`: vault profiles. Before writing to any vault, read its own rules file (`rules_file` in the config).
4. [meta/sources.md](meta/sources.md): why the rules are what they are, with sources.
5. [routing_log.md](routing_log.md) and the latest file in `digests/`: what has already been decided.

Note registry: `python scripts/scan.py --help` (Python standard library only, never modifies the vaults).
