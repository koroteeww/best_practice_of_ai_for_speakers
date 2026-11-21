# Meta vault template

A folder that lets one AI chat (Claude Code, or any agent that reads `AGENTS.md`) work across several Obsidian vaults: route new material to the right vault, propose short bridge notes between vaults, track changes with a hash registry, and back everything up weekly. The practice is explained in [docs/08](../docs/08-many-vaults-one-ai-chat.md), and the story of building it is in the [case study](../docs/case-study-meta-vault.md).

## Setup

1. Copy this folder somewhere next to your vaults, for example `D:/Vaults/Meta`.
2. `config/vaults.example.json` → `config/vaults.json`. For each vault set `path`, `obsidian_vault` (the vault name as Obsidian shows it), `bridge_folder`, `readonly`, `exclude`, `rules_file` and `privacy`. If your vault's Obsidian root is a parent folder of `path`, put the sub-path into `uri_prefix`.
3. `.claude/settings.example.json` → `.claude/settings.json` with the same paths, so Claude Code sees all vaults from one chat.
4. Edit the vault table in `CLAUDE.md` and write one profile per vault in `vaults/` (start from `vaults/example-profile.md`).
5. First scan: `python scripts/scan.py scan`. Everything that exists becomes the baseline.
6. Open this folder in Claude Code and say: **"What's new? Write the first digest."**

Optional backup: `config/backup.example.json` → `config/backup.json`, point `destinations` at folders synced by Dropbox / Google Drive / OneDrive, try `python scripts/backup.py --dry-run`, then schedule it (see below).

## Files

| Path | What it is |
|---|---|
| `CLAUDE.md` | Rules for the AI: one home, bridges, the one-sentence test, privacy, scenarios |
| `AGENTS.md` | Reading order for other agents (Codex, Cursor, Gemini CLI) |
| `config/vaults.json` | Paths and rules of each vault |
| `vaults/*.md` | One profile per vault: purpose, topics, what goes in, interests in other vaults |
| `meta/glossary.md` | One idea, different words in each vault, for the mechanism test |
| `meta/sources.md` | 30 sources behind the rules, with short conclusions |
| `templates/bridge.md`, `templates/digest.md` | Note templates |
| `routing_log.md` | Every routing decision and every rejected bridge |
| `scripts/scan.py` | Hash registry: `scan`, `pending`, `ack`, `find`, `stats`, `uri` |
| `scripts/backup.py` | Weekly zip of every vault to your cloud folders |
| `inbox/`, `digests/` | Drop zone for new material; generated digests |
| `registry/` | Generated: SQLite registry, `pending.md/json`, backup log (not committed) |

Both scripts use only the Python 3.10+ standard library and never modify your vaults.

## Scheduling the backup

**Windows (PowerShell):**

```powershell
$a = New-ScheduledTaskAction -Execute "python.exe" -Argument '"D:\Vaults\Meta\scripts\backup.py"' -WorkingDirectory "D:\Vaults\Meta"
$t = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 20:00
$s = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "Obsidian weekly backup" -Action $a -Trigger $t -Settings $s
```

`-StartWhenAvailable` runs a missed backup as soon as the computer is on again.

**macOS / Linux (cron):** `0 20 * * 0 cd ~/Vaults/Meta && python3 scripts/backup.py`
