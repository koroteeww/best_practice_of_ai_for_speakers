---
type: system
---

# Projects: where each one lives

A routing map for the AI, not a task tracker. For each project it answers three questions: which vault is its **home**, where else it is mentioned, and whether it is worth spending bridges on **right now**. Status and descriptions live in the home vault; the machine-readable copy for the map is `projects` in `config/decisions.json`.

**Relevance filter:**
- 🟢 **now**: serves your current priorities. Bridges make sense.
- 🟡 **background**: alive but not in focus. Bridges only on direct request.
- ⚪ **archive**: closed. No bridges. Use it only as a *story* for the speaking vault (with proof) or a *lesson* for the personal vault.

## 🟢 Now

| Project | Home | Also mentioned in | Note for the AI |
|---|---|---|---|
| Day-job AI rollout | work `Home.md` | personal (as a life stage) | NDA: only anonymized methods leave the vault |
| Speaking career | speaking `Speaker profile.md` | personal `Now/Career track.md` | — |

## 🟡 Background

| Project | Home | Also mentioned in | Note for the AI |
|---|---|---|---|
| Music album | personal `Projects/Album/` | speaking (an older album story) | A new story only after the release, with proof |

## ⚪ Archive

| Project | Home | Note for the AI |
|---|---|---|
| Closed startup | personal `Projects/Startup.md` | Only as a lesson. Money and investors never leave the personal vault |

## How to use
- When filing new material, find its project here first: if the project has a home, the material goes there.
- New project: one row here, one entry in `decisions.json` → `projects`, one line in `routing_log.md`.
- A project moved to the archive: move its row to ⚪ and review its bridges during "clean up the bridges".
