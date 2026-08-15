# Project Mission

Status: reconstructed brownfield constitution, 2026-08-15. This document is
derived from the current README, architecture, benchmark guidance, and recent
repository history. Maintainer corrections should update this file before they
shape implementation.

## Purpose

Agentic AI Playground helps practitioners compare coding agents, model sources,
models, inference runtimes, and deployment targets without confusing those
independent choices. It turns exploratory setup notes into repeatable, safe,
and reviewable experiments.

## Audience

- Developers evaluating a coding agent or model for hands-on engineering work.
- Practitioners deciding whether to use a managed API or operate an inference
  endpoint on local or rented compute.
- Maintainers who need comparable evidence before expanding an experiment to
  more expensive hardware or more complex routing.

## Product Promise

A contributor should be able to choose one path through the repository, verify
the endpoint contract, connect an agent, run the same bounded benchmark, and
record enough context for another person to understand and reproduce the run.

## Success Criteria

- The repository keeps agent, source, model, runtime, and deployment choices
  explicit in both documentation and result records.
- At least one inexpensive path works end to end before scale-out paths are
  treated as ready.
- Benchmark runs declare the repository snapshot, prompts, permissions, pass
  criteria, model/runtime configuration, latency, reliability, and cost.
- Setup guidance does not expose secrets or an unauthenticated inference port.
- Model and hardware claims distinguish verified facts from assumptions and
  point contributors to the evidence they must check.
- A fresh contributor or coding-agent session can continue from versioned
  repository artifacts rather than reconstructing intent from chat history.

## Operating Principles

- Prefer one measured end-to-end slice over a broad catalog of untested setup
  combinations.
- Compare like with like: keep the task pack, repository snapshot, prompt,
  permissions, and scoring criteria fixed when comparing runs.
- Test endpoint compatibility and tool use separately from prose quality.
- Record observed values; do not substitute advertised aggregate capacity for
  a measured model, runtime, or hardware configuration.
- Keep specifications and implementation synchronized in the same change.
- Replan after validated work changes cost, feasibility, or the best delivery
  order.

## Non-Goals

- Training or fine-tuning foundation models.
- GPU kernel development or low-level inference optimization.
- Operating a public production inference service.
- Exhaustively documenting every agent, model, provider, or runtime before one
  reference path is reproducible.
- Declaring a universal winner from runs with different tasks or conditions.

## Assumptions to Confirm

- The primary outcome is a reproducible practitioner reference, not a hosted
  application or leaderboard service.
- Initial evidence may be checked into the repository as Markdown result
  records, with large raw logs stored elsewhere and linked when appropriate.
- Portability and low setup cost are more important for the first benchmark
  pack than high-throughput orchestration.
