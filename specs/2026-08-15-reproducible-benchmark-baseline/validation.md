# Reproducible Benchmark Baseline — Validation

This evidence is defined before implementation. File names below establish the
intended public commands; if discovery requires a different layout, update this
document and the implementation together before claiming completion.

## Automated — Pack Integrity

- [ ] `python3 benchmarks/coding-agent-v1/scripts/validate_pack.py` exits zero
  and lists the endpoint preflight plus all five coding scenarios exactly once.
- [ ] `python3 -m unittest discover -s benchmarks/coding-agent-v1/tests -v`
  exits zero without downloading packages, reading credentials, or accessing
  the network.
- [ ] Manifest tests reject an unknown scenario, duplicate identifier, missing
  prompt/validator/rubric, and unsupported outcome value.
- [ ] Every mechanically testable requirement is associated with an executable
  validator; every remaining qualitative requirement names a rubric.

## Automated — Preparation Safety

- [ ] Preparing the same scenario twice into two empty temporary destinations
  produces identical file trees and content hashes.
- [ ] Preparing different scenarios does not leak seeded state between them.
- [ ] Preparation refuses a non-empty destination and leaves its content
  unchanged.
- [ ] Preparation refuses a destination inside the canonical fixture tree.
- [ ] Invalid scenario names and path-traversal input fail non-zero without
  leaving partial output.
- [ ] Tests confirm that preparation never calls a model API or network service.

## Automated — Validator Behavior

- [ ] Each validator fails against its untouched or deliberately incorrect
  starting state with a criterion-specific message.
- [ ] Each validator passes against a minimal known-good result.
- [ ] The seeded diagnostic scenario begins with the declared failing check and
  its known-good result passes the full fixture suite.
- [ ] The refactor validator checks behavior and declared structural boundaries,
  not an exact private implementation.
- [ ] Validator exit codes distinguish valid pass/fail execution from an invalid
  pack or missing prerequisite.

## Automated — Repository Hygiene

- [ ] `git diff --check` exits zero.
- [ ] All links added by this phase resolve to repository files or intentional
  external references.
- [ ] A secret-pattern scan of new fixtures, examples, and dry-run artifacts
  finds placeholders only, never live credentials.
- [ ] The standard-library tooling runs under the documented minimum Python 3
  version in a clean environment.

## Manual — Contributor Walkthrough

- [ ] From `benchmarks/README.md`, a reviewer can identify the current pack,
  prepare each scenario, find its exact prompt and permissions, run validation,
  interpret the outcome, and reset without undocumented knowledge.
- [ ] The endpoint preflight states what to record without implying that one API
  dialect, vendor, or model is universally supported.
- [ ] The summary rubric rewards correct repository understanding and does not
  expose answer text in the agent prompt.
- [ ] Prompts specify outcomes and constraints without prescribing routine
  implementation details.
- [ ] Timeouts, retries, interventions, permission changes, and deviations have
  visible fields in the result template.
- [ ] Canonical fixture inputs remain unchanged after a complete dry run.

## Manual — Scope and Traceability

- [ ] Every item under `requirements.md` **In Scope** maps to a task and to
  validation evidence.
- [ ] No item under **Out of Scope** was introduced implicitly.
- [ ] The benchmark retains the six categories currently promised by
  `benchmarks/README.md`.
- [ ] Documentation consistently distinguishes endpoint compatibility, agent
  behavior, model behavior, runtime behavior, and deployment placement.
- [ ] The project constitution, feature packet, benchmark docs, result template,
  and roadmap tell the same story.

## Definition of Done

- [ ] Every automated check above has been executed, not merely inspected.
- [ ] Every manual item is checked by a reviewer or explicitly recorded as an
  unmet criterion.
- [ ] The model-free dry run and its expected failure/success evidence are
  committed without credentials or machine-specific paths.
- [ ] Requirements, plan, and validation reflect implementation discoveries.
- [ ] Roadmap Phase 2 is marked complete and Phase 3 is specified only after all
  Phase 2 evidence passes.
