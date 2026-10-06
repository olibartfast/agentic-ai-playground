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

None of these has been executed. They are the evidence the packet exists to
produce.

- [ ] A llama.cpp build at or after PR #29818 is on the host; record the build
      number and commit.
- [ ] `curl http://127.0.0.1:8080/v1/systemone` with the recipe's sample
      request returns `answers` and `usage.output_tokens == 0`.
- [ ] Router mode lists Julia-1, Laya, and Kev-4B in `/v1/models` and serves
      each by name.
- [ ] Observed VRAM recorded per model at the quantization used.
- [ ] `decision-v1` run against Julia-1, Laya, and Kev-4B, each committed as a
      dated result under `benchmarks/`.
- [ ] Each result reports accuracy per family, unsafe allows, the cutoff
      table, and median and 95th-percentile latency.

## Definition of done

- [ ] The serving recipe, model profile, benchmark, and roadmap agree.
- [ ] At least one model has a recorded `decision-v1` result on the host, or
      the packet records why it could not run.
