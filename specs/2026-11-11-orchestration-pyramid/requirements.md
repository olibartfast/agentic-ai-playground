# Orchestration Pyramid — Requirements

Status: implemented, 2026-11-11.

## Problem

The repository's role guide and committed Codex/Claude examples describe an
architect-to-planner-to-implementer hierarchy. The intended operating model is
instead a main session that invokes an orchestrator for complex work; the
orchestrator selects only the specialists needed and coordinates architect,
planner, worker, reviewer, and explorer roles. Small tasks stay in the main
session.

## Scope

- Update `docs/role-agents.md` to define the shared role pyramid, boundaries,
  handoff flow, and each harness's actual enforcement limits.
- Align the repository's Claude Code, Codex, and OpenCode role examples and
  integration notes with the shared roles and user-selected model tiers.
- Add a versioned Hermes profile/delegation example and explain the required
  `advanced-delegation` plugin, Meta/DeepSeek-only routing, and verification
  limits.
- Update integration pointers and the older role-agent feature packet where
  they conflict with the new model.
- Keep Kilo role configuration outside this change; its current harness setup
  remains intact.

## Out of scope

- Editing personal global configuration under home directories, installing
  plugins, or changing credentials.
- Running paid model calls or claiming profile/model route availability that
  has not been verified.
- Changing Pi or Kilo role enforcement and model assignments.

## Acceptance criteria

- The guide states: main session handles small work directly; complex work is
  coordinated by one orchestrator; architect/planner/worker/reviewer/explorer
  are selected as needed; only the orchestrator delegates; only the worker is
  assigned implementation edits; reviewer returns actionable findings to a
  worker for correction and re-verification.
- Claude Code examples use Sonnet 5.5 orchestrator (medium), Fable 5.2
  architect (high), Opus 5.5 planner (high), Sonnet 5.5 worker (medium), Fable
  5.2 reviewer (high), and Haiku 5.5 explorer (low). Document Claude Code
  minimum version 2.1.321 and nesting depth 2. These role boundaries are
  behavioral unless the harness setting enforces them.
- Codex committed roles use the established local baseline: orchestrator
  `gpt-6.1-sol` low, architect `gpt-6-astra` high, planner `gpt-6.1-terra`
  medium, worker `gpt-6-luna` high, reviewer `gpt-6.1-sol` high. Explorer is
  optional and does not invent a model assignment.
- OpenCode roles use the current selected Meta/DeepSeek mapping: Muse Spark
  high for orchestrator/architect/reviewer, Muse Ember high for planner and low
  for explorer, DeepSeek Flash low for worker, with `steps: 25`; only the
  orchestrator can spawn tasks. DeepSeek here is the OpenCode model provider;
  this feature does not configure DeepSeek Harness.
- Hermes example routes Meta Muse Spark to orchestrator/architect/reviewer,
  Meta Muse Ember to planner/explorer, and DeepSeek Flash to worker, with
  requested effort levels. It documents only Meta and DeepSeek providers,
  depth 2, leaf defaults, and that Ember availability is unverified in the
  installed Meta model cache.
- No API keys or personal configuration values enter the repository.
- Existing unrelated harness instructions remain accurate and the changed
  relative links resolve.
