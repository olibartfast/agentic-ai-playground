# Decision Models for Agent Harnesses — Validation

## Offline checks

Executed 2026-10-06 in a cloud sandbox with Python 3, no GPU and no model
server:

- [x] `python3 -m py_compile benchmarks/decision-v1/run.py`
- [x] `python3 -m unittest discover -s benchmarks/decision-v1/tests` — 14
      tests pass, including an end-to-end run against a local stub server.
- [x] `python3 benchmarks/decision-v1/run.py --validate-only` reports 39 valid
      cases: 18 `shell_gate`, 12 `tool_select`, 9 `model_route`.
- [x] Pointing the runner at a closed port records every case as an error and
      exits non-zero rather than reporting a score.
- [x] `git diff --check` reports no whitespace errors.
- [x] Every relative Markdown link in the change resolves.

The stub server proves request shape and scoring against this packet's reading
of the API. It does not prove `llama-server` returns the same field names;
that is the first host check below.

## Host checks (RTX 3060 6 GB)

Executed 2026-10-11 on the i5-11400H + RTX 3060 Laptop host, single-model
`llama-server` instances, one model at a time. Full numbers in
[`benchmarks/2026-10-11-system1-decision/`](../../benchmarks/2026-10-11-system1-decision/result.md).

- [x] A llama.cpp build at or after PR #29818 is on the host; record the build
      number and commit. — source build `~/repos/llama.cpp-system1` at
      `23b0202`, `llama-server --version` reports 0.6.0-dev **build 956**.
- [x] `curl http://127.0.0.1:8080/v1/systemone` with the recipe's sample
      request returns `answers` and `usage.output_tokens == 0`. — Julia-1
      returned `answers.gate` with probabilities + `confidence` 0.958 and
      `output_tokens == 0`. (Note: the same state batched with all three
      `decision-v1` questions via `ghostgrid decide` returned a different
      verdict — single-question and batched numbers are not comparable.)
- [ ] Router mode lists Julia-1, Laya, and Kev-4B in `/v1/models` and serves
      each by name. — **not tested**; all runs used single-model servers
      (`-m <file>`), where the `model` field is ignored.
- [x] Observed VRAM recorded per model at the quantization used. — Julia-1
      Q8_0: 349 MiB; Laya Q8_0: 695 MiB; Kev-4B Q4_K_M: 5029 MiB (776 MiB
      free of 6144 MiB).
- [x] `decision-v1` run against Julia-1, Laya, and Kev-4B, each committed as a
      dated result under `benchmarks/`. — accuracy 0.487 / 0.667 / 0.872,
      unsafe allows 0 / 5 / 1; see the dated result. A 36-case CV draft
      (`decision-cv-v1`: 0.556 / 0.556 / 0.750) is committed alongside.
- [x] Each result reports accuracy per family, unsafe allows, the cutoff
      table, and median and 95th-percentile latency. — in the dated result;
      confidence source is `server` throughout.

## Definition of done

- [x] The serving recipe, model profile, benchmark, and roadmap agree.
- [x] At least one model has a recorded `decision-v1` result on the host, or
      the packet records why it could not run. — three models recorded;
      router mode remains the open item.
