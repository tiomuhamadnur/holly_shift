---
description: Close the session - run checks, update PROGRESS.md, commit
---
Follow AGENTS.md section 2 (SESSION END):
1. Run `make check` and show the result summary. If red, fix or record exactly why in Blockers.
2. Update PROGRESS.md: tick finished tasks, rewrite the CURRENT STATE table (date, phase, active task, last done, next step with exact files, blockers, model, branch, last make check), and append ONE line to Session Log in the format `YYYY-MM-DD HH:MM | model | task | result | make check | next step`.
3. If a decision or open question came up, add it to Open Items / Decision Log.
4. Commit with a Conventional Commit message.
5. Reply with 5 lines max: what is done, what is next, anything the human must decide.
