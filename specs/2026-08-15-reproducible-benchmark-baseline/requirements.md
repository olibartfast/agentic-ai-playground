# Reproducible Benchmark Baseline — Requirements

Status: planned. This packet covers Roadmap Phase 2 only.

## Goal

Turn the current benchmark outline into a versioned coding-agent task pack that
can be prepared from clean state, executed consistently across agents and model
sources, and scored with reviewable evidence.

## Users and Outcome

A contributor evaluating an agent/model pair can select the benchmark version,
prepare a scenario without altering its canonical inputs, give the declared
prompt and permissions to the agent, run the declared checks, and copy outcomes
into a comparable result record.

## In Scope

- Name and version the first coding-agent benchmark pack.
- Preserve endpoint health/model discovery as a separate preflight scenario.
- Provide the five current repository-work scenarios:
  1. read and summarize a small repository;
  2. create one file and verify its contents;
  3. modify one existing function and run focused tests;
  4. diagnose and fix a seeded compiler or test failure;
  5. complete a bounded multi-file refactor.
- Supply small, deterministic, license-compatible fixture inputs under version
  control. Each coding scenario starts from clean prepared state.
- Supply the exact prompt, initial state, allowed tools/permissions, timeout
  policy, expected artifacts, automated checks, and manual rubric for each
  scenario.
- Provide a safe preparation/reset path that never mutates canonical fixtures
  and refuses to overwrite a non-empty destination.
- Provide standard-library Python validation and self-tests where mechanical
  scoring is sufficient.
- Update benchmark documentation and the result template to record pack version,
  fixture revision, per-scenario status, and deviations from the contract.
- Document one model-free dry run of preparation, validation, failure output,
  and reset behavior.

## Out of Scope

- Running or scoring a real coding agent/model pair; that is Roadmap Phase 3.
- Choosing a winning agent, model, provider, runtime, or deployment target.
- Provisioning cloud GPUs or launching a self-hosted model.
- Building a hosted leaderboard, web UI, database, or telemetry service.
- Automatically judging prose quality when the declared rubric requires human
  review.
- Generalizing the first pack into a plugin system or orchestration framework.
- Modernizing the legacy LangGraph or A2A prototypes.

## Required Behavior

### Version identity

- The pack has a stable identifier and explicit version recorded by every
  result.
- Changing a prompt, fixture input, permissions, timeout, or pass criterion in a
  way that affects comparability requires a new benchmark version.
- Editorial clarifications that do not change execution may retain the version
  and must be visible in Git history.

### Preparation and isolation

- Canonical fixture content remains read-only during a run.
- Preparation accepts an explicit scenario and destination, creates a complete
  working copy, and exits without partial overwrite when the destination is not
  safe.
- Scenario-specific seeded state is deterministic and version controlled.
- A contributor can discard a run and recreate identical initial state without
  network access or a model API.

### Scenario contracts

- Every scenario is independently runnable from clean state.
- Prompts state the intended outcome without revealing the solution.
- Mechanical requirements map to executable validators.
- Subjective requirements use a short rubric with observable dimensions and a
  recorded reviewer decision.
- A validator failure explains which contract condition failed and exits
  non-zero.
- The endpoint preflight records the requested URL shape, returned model
  identity, protocol path, authentication mode without the secret, and result.

### Results and reporting

- A result distinguishes pass, fail, skipped, and invalid/deviated runs.
- Timeouts, retries, permission changes, human intervention, and prompt changes
  are recorded; they are not silently normalized into a pass.
- Result records contain the repository commit, benchmark version, fixture
  revision, agent/model/source configuration, and per-scenario outcome.
- Committed examples and logs contain no credentials or machine-specific secret
  values.

## Decisions and Rationale

- **Fresh state per coding scenario:** isolates capabilities and prevents an
  earlier edit from contaminating later scores.
- **Model-free pack validation:** fixture and scoring bugs must be discoverable
  without cost, credentials, or network access.
- **Standard-library Python for pack tooling:** Python already exists in the
  repository and this phase does not justify a root dependency stack.
- **Automation plus an explicit rubric:** deterministic checks should not be
  replaced by opinion, while semantic summaries should not be reduced to brittle
  string matching.
- **Endpoint preflight remains distinct:** API compatibility is evidence about
  the source/runtime path, not evidence that the agent can edit code correctly.

## Constraints and Context

- Follow `../mission.md` and `../tech-stack.md`.
- Preserve the benchmark categories already published in `benchmarks/README.md`.
- Keep fixtures small enough to inspect during review and cheap enough to run
  repeatedly.
- Do not require Docker, a cloud account, a GPU, or external package downloads
  for pack self-validation.
- The implementation may refine file names after repository discovery, but it
  must not weaken the behavior or evidence above without updating this packet.

## Acceptance Criteria

- All in-scope scenarios have complete, versioned contracts.
- Preparation and validation behave safely for both success and misuse paths.
- Pack self-tests and repository documentation checks pass.
- The result template can represent each required outcome and deviation.
- The dry run demonstrates reproducible clean state and expected validator
  failure/success without calling an agent.
- Requirements, plan, validation, roadmap, and implementation agree.
