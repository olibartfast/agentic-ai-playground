# Repository Guidelines

## Project Structure & Module Organization

This is a documentation-first playground that keeps experiment concerns
separate. Put model requirements in `models/`, hosted and self-operated API
backends in `serving/`, agent/IDE configuration in `integrations/`, and compute
runbooks in `deployments/`. `experiments/` is absent from the tree until a
prototype exists; recreate it when adding one. Reproducible tasks and result records belong in
`benchmarks/`; runnable framework prototypes belong in `experiments/`.

`docs/architecture.md` defines the routing model. Project intent and active
work contracts live in `specs/`.

## Spec-Driven Changes

Before planning multi-step work, read `specs/mission.md`,
`specs/tech-stack.md`, and `specs/roadmap.md`. Create feature packets as
`specs/YYYY-MM-DD-short-name/{requirements,plan,validation}.md`. Define scope
and validation before implementation, and update specifications in the same
change whenever requirements or architecture shift. Trivial documentation fixes
do not require a feature packet.

## Build, Test, and Development Commands

There is no root build system or universal test command. Use the narrowest
checks relevant to the files changed:

- `git diff --check` — detect whitespace errors before committing.
- `python3 -m py_compile <file>` — syntax-check a Python prototype without
  invoking an API.
- `python3 -m venv .venv` followed by
  `.venv/bin/pip install -r <requirements.txt>` — prepare a prototype's
  isolated environment. Pin dependencies and keep them current; an unmaintained
  pinned tree accumulates advisories whether or not the code is ever run.

Document and run exact focused checks in each feature's `validation.md`. Do not
claim network, model, or hardware validation from static inspection alone.

## Coding Style & Naming Conventions

Wrap Markdown prose near 80 columns, use descriptive headings, relative links,
and fenced blocks with language tags. Follow PEP 8 for Python: four-space
indentation, `snake_case` functions, and `PascalCase` classes. Name safe sample
configuration `*.example.json` or `*.example.yaml`; never embed credentials.

## Testing Guidelines

Add tests beside the maintained experiment or under its dedicated `tests/`
directory. Prefer deterministic, offline tests and names such as
`test_rejects_nonempty_destination`. Record manual endpoint, tool-call, and GPU
checks separately. The repository currently has no global coverage threshold.

## Commit & Pull Request Guidelines

Use short, imperative, sentence-case subjects, for example `Group inference
backends under serving`. Branches should use `agent/<short-description>`. Keep
commits scoped and avoid unrelated formatting. Pull requests should explain the
outcome and rationale, link the relevant spec or issue, list executed checks and
unmet manual validation, and include screenshots only for visual changes.

## Security & Configuration

Read secrets from environment variables and commit placeholders only. Bind
temporary inference servers to loopback; use SSH tunnels for remote experiments.
Never publish unauthenticated inference ports, and include shutdown steps in
cloud runbooks.
