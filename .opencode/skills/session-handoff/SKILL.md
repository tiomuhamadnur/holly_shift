---
name: session-handoff
description: How to resume, hand off and record progress so any model or session can continue instantly. Use at the start and end of every session.
---
# Session handoff

## Why
Free/weaker models lose context fast and the model may change between sessions. `PROGRESS.md` is the only memory that matters. Chat history is not trusted.

## Start
1. `PROGRESS.md` lines 1-60 -> CURRENT STATE.
2. Active phase section only.
3. `git status -sb`, `git log --oneline -5`.
4. Post a plan (task ID, files max 5, plan max 5 bullets, tests).

## During
- One task per session. If a task is size L, split it into S/M subtasks in PROGRESS.md first.
- Commit small and green. Branch per task.
- Same error twice: stop, write hypotheses under Blockers, ask the human.
- After ~30 messages or when repeating yourself: wrap up and start a new session.

## End
1. `make check`.
2. Tick tasks. Rewrite CURRENT STATE completely (do not append to it).
3. Append one Session Log line: `YYYY-MM-DD HH:MM | model | task | result | make check | next step`.
4. Keep only the last 20 session log lines; compress older ones into one summary line per phase.
5. Record decisions in Decision Log and questions in Open Items with a proposed default.
6. Commit.

## CURRENT STATE must always answer
Which phase and task is active? What was finished last? What exactly is the next step (files, function names)? What blocks it? Which model and branch? Was the last `make check` green?

## Never
Leave the repo red without recording it. Edit BRD silently. Mark a task done without a passing check.
