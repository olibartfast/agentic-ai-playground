# Benchmarks

Run the same task sequence for every model/backend pair:

1. Endpoint health and model discovery.
2. Read and summarize a small repository.
3. Create one file and verify its contents.
4. Modify one existing function and run its tests.
5. Diagnose and fix a compiler or test failure.
6. Complete a bounded multi-file refactor.

Record results under a dated experiment directory using
[`result-template.md`](result-template.md). Do not compare runs unless the
repository commit, prompt, tool permissions, and pass criteria match.

