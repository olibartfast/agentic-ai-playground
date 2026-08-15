# Coding Agent Test Suite — Implementation Plan

## 1. Create the Suite Index

1. Add `benchmarks/coding-agent-v1/README.md` and `benchmark.json`.
2. Register these task IDs: `endpoint-check`, `repository-summary`,
   `create-file`, `edit-function`, `fix-failing-test`, and
   `multi-file-refactor`.
3. Add `scripts/check_pack.py` to reject missing files, duplicate IDs, and
   unsupported result values.
4. Test the index with intentionally broken copies of the metadata.

Result: `python3 benchmarks/coding-agent-v1/scripts/check_pack.py` lists six
valid tasks and exits zero.

## 2. Build the Starting Projects

5. Create one small, readable standard-library Python project for the coding
   tasks. Give every task its own complete fixture directory.
6. Seed the intended starting state: an untouched project, a requested missing
   file, an editable function, one real failing test, or code ready to split.
7. Add `scripts/prepare.py TASK DESTINATION` with overwrite and path-safety
   checks.
8. Test that preparing the same task twice produces identical files and that
   one task's state cannot appear in another.

Result: a contributor can create a disposable workspace for any coding task
without altering `fixtures/`.

## 3. Write Tasks and Check Results

9. Add one Markdown prompt per task under `prompts/`. State the outcome, allowed
   tools, time limit, and required final response without giving away a solution.
10. Add `scripts/check_result.py TASK WORKSPACE` and task-specific checker code.
11. Add the repository-summary rubric under `rubrics/` with named, observable
    scoring criteria.
12. Test each checker against the untouched fixture, an incorrect result, and a
    minimal known-good result. For `fix-failing-test`, verify that the agent did
    not edit the tests.

Result: every mechanical task has a clear pass/fail command; the summary task
has a short human checklist.

## 4. Document One Complete Dry Run

13. Update `benchmarks/README.md` with the sequence: endpoint check, prepare,
    give the prompt to an agent, validate, record results, and delete the copy.
14. Expand `benchmarks/result-template.md` with suite version, task outcomes,
    retries, intervention, deviations, and artifact links.
15. Add `examples/dry-run.md` showing preparation, an expected failed check, a
    known-good check, and fixture verification without calling an agent API.

Result: a new contributor can follow the README without guessing commands or
hidden settings.

## 5. Finish and Replan

16. Run every command in `validation.md` and review every manual item.
17. Update requirements, plan, or validation if implementation changed a file
    name or behavior.
18. Mark Roadmap Phase 2 complete only when the dry run and all checks pass.
19. Create the Phase 3 spec for the first real managed-agent run.
