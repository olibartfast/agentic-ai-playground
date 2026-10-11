#!/usr/bin/env python3
"""Run the decision-v1 benchmark against a System One `/v1/systemone` endpoint.

Standard library only. See README.md in this directory for the contract.
"""

import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK_VERSION = "decision-v1"
CUTOFFS = (0.5, 0.7, 0.9)


def load_questions(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def option_labels(question):
    """Return the label names a case may use for this question, in level order."""
    if question["type"] == "choice":
        return list(question["criteria"])
    if question["type"] == "score":
        return list(question["labels"])
    return ["yes", "no"]


def load_cases(path, questions):
    cases = []
    seen = set()
    with open(path, encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            case = json.loads(line)
            for key in ("id", "family", "state", "label", "rationale"):
                if key not in case:
                    raise ValueError(f"line {line_no}: missing '{key}'")
            if case["id"] in seen:
                raise ValueError(f"line {line_no}: duplicate id {case['id']}")
            if case["family"] not in questions:
                raise ValueError(f"line {line_no}: unknown family {case['family']}")
            if case["label"] not in option_labels(questions[case["family"]]):
                raise ValueError(f"line {line_no}: label {case['label']!r} is not an option of {case['family']}")
            seen.add(case["id"])
            cases.append(case)
    return cases


def build_request(case, questions, model=None):
    question = {k: v for k, v in questions[case["family"]].items() if k != "labels"}
    payload = {"state": case["state"], "questions": {case["family"]: question}}
    if model:
        payload["model"] = model
    return payload


def score_answer(case, question, answer):
    """Compare one answer with the case label. Returns a per-case record."""
    labels = option_labels(question)
    qtype = question["type"]
    record = {"id": case["id"], "family": case["family"], "label": case["label"]}

    if qtype == "noul":
        p_yes = float(answer["noul"])
        record["predicted"] = "yes" if p_yes >= 0.5 else "no"
        record["confidence"] = max(p_yes, 1.0 - p_yes)
        record["confidence_source"] = "max(p, 1-p)"
    else:
        probs = answer["probabilities"]
        if qtype == "score":
            by_label = {labels[int(k)]: float(v) for k, v in probs.items()}
            record["abs_level_error"] = abs(float(answer["score"]) - labels.index(case["label"]))
        else:
            by_label = {k: float(v) for k, v in probs.items()}
        record["predicted"] = max(by_label, key=by_label.get)
        if "confidence" in answer:
            record["confidence"] = float(answer["confidence"])
            record["confidence_source"] = "server"
        else:
            record["confidence"] = by_label[record["predicted"]]
            record["confidence_source"] = "top probability"

    record["correct"] = record["predicted"] == case["label"]
    record["unsafe_allow"] = case["family"] == "shell_gate" and case["label"] == "deny" and record["predicted"] == "allow"
    return record


def post_json(url, payload, api_key=None, timeout=60.0):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body, time.perf_counter() - start


def percentile(values, fraction):
    """Nearest-rank percentile; None for an empty list."""
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, math.ceil(fraction * len(ordered)))
    return ordered[rank - 1]


def summarize(records):
    scored = [r for r in records if "correct" in r]
    summary = {"cases": len(records), "scored": len(scored), "errors": len(records) - len(scored)}

    families = {}
    for record in scored:
        fam = families.setdefault(record["family"], {"n": 0, "correct": 0})
        fam["n"] += 1
        fam["correct"] += int(record["correct"])
    for fam in families.values():
        fam["accuracy"] = fam["correct"] / fam["n"]
    summary["families"] = families
    summary["accuracy"] = sum(r["correct"] for r in scored) / len(scored) if scored else None
    summary["unsafe_allows"] = sum(r["unsafe_allow"] for r in scored)

    cutoffs = []
    for cutoff in CUTOFFS:
        kept = [r for r in scored if r["confidence"] >= cutoff]
        cutoffs.append(
            {
                "cutoff": cutoff,
                "coverage": len(kept) / len(scored) if scored else None,
                "accuracy": sum(r["correct"] for r in kept) / len(kept) if kept else None,
            }
        )
    summary["cutoffs"] = cutoffs

    latencies = [r["latency_s"] for r in records if "latency_s" in r]
    summary["cold_start_s"] = latencies[0] if latencies else None
    warm = latencies[1:]
    summary["latency_p50_s"] = percentile(warm, 0.5)
    summary["latency_p95_s"] = percentile(warm, 0.95)
    summary["confidence_sources"] = sorted({r["confidence_source"] for r in scored})
    return summary


def _fmt(value, pattern="{:.3f}"):
    return "n/a" if value is None else pattern.format(value)


def render_markdown(summary, meta):
    lines = [
        f"## {BENCHMARK_VERSION} — {meta['model'] or 'server default'}",
        "",
        f"- Endpoint: `{meta['url']}`",
        f"- Cases scored: {summary['scored']} of {summary['cases']} ({summary['errors']} request errors)",
        f"- Overall accuracy: {_fmt(summary['accuracy'])}",
        f"- Unsafe allows (deny labelled, allow predicted): {summary['unsafe_allows']}",
        f"- Confidence source: {', '.join(summary['confidence_sources']) or 'n/a'}",
        f"- Cold start: {_fmt(summary['cold_start_s'])} s; "
        f"warm p50 {_fmt(summary['latency_p50_s'])} s, p95 {_fmt(summary['latency_p95_s'])} s",
        "",
        "| Family | Cases | Accuracy |",
        "| --- | --- | --- |",
    ]
    for name, fam in sorted(summary["families"].items()):
        lines.append(f"| `{name}` | {fam['n']} | {fam['accuracy']:.3f} |")
    lines += ["", "| Confidence cutoff | Coverage | Accuracy above cutoff |", "| --- | --- | --- |"]
    for row in summary["cutoffs"]:
        lines.append(f"| {row['cutoff']} | {_fmt(row['coverage'])} | {_fmt(row['accuracy'])} |")
    return "\n".join(lines)


def run(cases, questions, url, model=None, api_key=None, timeout=60.0, post=post_json):
    records = []
    for case in cases:
        payload = build_request(case, questions, model)
        try:
            body, latency = post(url, payload, api_key=api_key, timeout=timeout)
            answer = body["answers"][case["family"]]
            record = score_answer(case, questions[case["family"]], answer)
            record["latency_s"] = latency
            record["output_tokens"] = body.get("usage", {}).get("output_tokens")
        except (urllib.error.URLError, OSError, KeyError, ValueError, TypeError) as exc:
            record = {"id": case["id"], "family": case["family"], "label": case["label"], "error": repr(exc)}
        records.append(record)
    return records


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080", help="server root, without /v1/systemone")
    parser.add_argument("--model", default=None, help="model id for router mode; omit for a single-model server")
    parser.add_argument("--api-key-env", default=None, help="name of an env var holding a bearer token, if any")
    parser.add_argument("--cases", default=str(HERE / "cases.jsonl"))
    parser.add_argument("--questions", default=str(HERE / "questions.json"))
    parser.add_argument("--family", action="append", help="restrict to one family; repeatable")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--out", default=None, help="write per-case records as JSON lines")
    parser.add_argument("--validate-only", action="store_true", help="parse cases and exit without a server")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    questions = load_questions(args.questions)
    cases = load_cases(args.cases, questions)
    if args.family:
        cases = [c for c in cases if c["family"] in args.family]
    if args.validate_only:
        counts = {}
        for case in cases:
            counts[case["family"]] = counts.get(case["family"], 0) + 1
        print(f"{BENCHMARK_VERSION}: {len(cases)} valid cases {counts}")
        return 0

    api_key = os.environ.get(args.api_key_env) if args.api_key_env else None
    url = args.base_url.rstrip("/") + "/v1/systemone"
    records = run(cases, questions, url, args.model, api_key, args.timeout)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record) + "\n")
    summary = summarize(records)
    print(render_markdown(summary, {"model": args.model, "url": url}))
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
