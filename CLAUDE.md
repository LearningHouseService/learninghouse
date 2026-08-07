# CLAUDE.md

Read [AGENTS.md](AGENTS.md) for project architecture, conventions and developer commands, and
[docs/modernization-plan.md](docs/modernization-plan.md) for the phased roadmap and the open
decisions.

## Claude Code-Specific

- When compacting, preserve the full list of modified files.
- When starting work on a phase from the modernization plan, check off its acceptance criteria
  explicitly before considering the phase done, and say which ones could not be verified locally.
- Python work happens in `core/`; run `ruff check .`, `ruff format .`, `pyright` and `pytest`
  from there, not from the repository root.
- The working tree lives on an ecryptfs home directory where `git stash` and `git diff` sometimes
  fail with short-read errors on `ui/` assets. Compare file contents against `HEAD` before
  believing that such a file is modified.
