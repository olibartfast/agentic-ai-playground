# Reproducible Benchmark Baseline — Implementation Plan

The groups below follow dependency order. Complete the focused checks at the end
of each group before moving to the next; update this plan in the same branch if
implementation discovery changes the design.

## Group 1 — Contract and version identity

1. Inventory the six published benchmark stages and assign each one a stable
   scenario identifier.
2. Define the pack manifest: benchmark identifier/version, fixture revision,
   scenario order, prompt path, preparation mode, permissions, timeout, validator,
   and rubric path.
3. Document versioning rules and the meanings of pass, fail, skipped, and
   invalid/deviated.
4. Add manifest validation that reports missing, duplicate, or inconsistent
   scenario metadata.

Observable result: one command can load the pack contract and list all declared
scenarios without contacting an external service.

## Group 2 — Immutable fixtures and safe preparation

5. Create the smallest readable Python fixture that can support the five coding
   tasks with standard-library tests.
6. Add deterministic scenario-specific starting states, including the seeded
   failure and bounded refactor inputs.
7. Implement preparation into an explicit destination with guards against
   canonical-fixture mutation, destination overwrite, path traversal, and
   partial output.
8. Add focused tests for identical recreation, scenario isolation, invalid
   identifiers, unsafe destinations, and already-populated destinations.

Observable result: every coding scenario can be recreated byte-for-byte in a
fresh directory, and misuse fails without changing existing files.

## Group 3 — Prompts, validators, and rubrics

9. Write one exact prompt and execution envelope for every scenario.
10. Implement mechanical validators for created/modified files, focused tests,
    the seeded repair, and the multi-file refactor.
11. Write the human rubric for the repository-summary scenario and any declared
    qualitative portion of the refactor.
12. Test each validator against a known failing fixture and a minimal known-good
    result; ensure failure output names the unmet criterion.
13. Define endpoint preflight evidence without embedding a live URL, key, or
    vendor-specific model assumption in the pack.

Observable result: a reviewer can trace every scenario requirement to a command
or a named rubric dimension, and validators reject known-bad outcomes.

## Group 4 — Result schema and contributor workflow

14. Extend `benchmarks/result-template.md` with benchmark identity, fixture
    revision, per-scenario outcomes, interventions, retries, deviations, and
    artifact references.
15. Rewrite `benchmarks/README.md` around the versioned pack workflow: preflight,
    prepare, execute, validate, record, and reset.
16. Add a checked-in model-free dry-run record showing preparation, an expected
    validation failure, a known-good validation pass, and clean reset.
17. Cross-link the benchmark pack, feature packet, technical boundaries, and
    roadmap using repository-relative links.

Observable result: a new contributor can follow one documented path from pack
selection to a complete empty result record without guessing hidden settings.

## Group 5 — Full validation and spec reconciliation

18. Run the complete automated checklist from `validation.md` in a clean
    temporary directory.
19. Perform the manual safety, readability, secret, and requirement traceability
    review.
20. Reconcile implementation discoveries across requirements, this plan,
    validation, the project constitution, and the roadmap.
21. Mark Roadmap Phase 2 complete only after all declared evidence exists; use
    the validated pack to create the Phase 3 feature packet.

Observable result: the versioned pack is internally consistent, self-validating,
safe to prepare, and ready for its first real agent/model baseline.
