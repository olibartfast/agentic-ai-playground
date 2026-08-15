# Coding Agent Test Suite — Validation

These commands define success before implementation. If the public file layout
changes, update this document in the same change.

## Suite Checks

- [ ] `python3 benchmarks/coding-agent-v1/scripts/check_pack.py` exits zero and
  prints all six task IDs exactly once.
- [ ] `python3 -m unittest discover -s benchmarks/coding-agent-v1/tests -v`
  exits zero without network access or third-party packages.
- [ ] Tests show that `check_pack.py` rejects a missing prompt, fixture, checker,
  or rubric; a duplicate task ID; and an unsupported result value.

## Workspace Preparation

- [ ] `prepare.py create-file DESTINATION` creates a complete runnable project
  in an explicitly chosen empty directory.
- [ ] Preparing the same task in two directories produces identical contents.
- [ ] Preparing different tasks produces their declared starting states.
- [ ] A non-empty destination is left unchanged and returns an error.
- [ ] A destination inside `benchmarks/coding-agent-v1/fixtures/` is rejected.
- [ ] Unknown task names and path traversal attempts leave no partial files.

## Result Checkers

- [ ] Each coding-task checker fails against its untouched starting fixture.
- [ ] Each checker fails against at least one representative wrong solution.
- [ ] Each checker passes a minimal known-good solution.
- [ ] `edit-function` and `fix-failing-test` run both focused and full tests.
- [ ] `fix-failing-test` rejects a result that changes or deletes test files.
- [ ] `multi-file-refactor` checks behavior and the requested file layout without
  requiring one exact implementation.
- [ ] Failure messages name the unmet requirement and use a non-zero exit code.

## Documentation Walkthrough

- [ ] A reviewer can use `benchmarks/README.md` to find a prompt, prepare a
  workspace, run its checker, record the result, and start over from clean state.
- [ ] Every prompt names allowed tools, time limit, expected output, and scoring
  method without revealing solution code.
- [ ] The summary rubric measures correct project understanding with observable
  criteria.
- [ ] The endpoint task records protocol and model identity without storing a
  credential or assuming one vendor.
- [ ] The result template records retries, prompt edits, permission changes,
  human help, and invalid or skipped tasks.

## Repository Checks

- [ ] `git diff --check` exits zero.
- [ ] New relative links resolve.
- [ ] Examples contain placeholders rather than credentials or local machine
  paths.
- [ ] The dry run leaves all canonical fixture files unchanged.
- [ ] Requirements, implementation, benchmark docs, and roadmap agree.

## Definition of Done

- [ ] Every check above has been run or recorded honestly as unmet.
- [ ] The model-free dry run is committed.
- [ ] Roadmap Phase 2 is marked complete only after all required evidence passes.
