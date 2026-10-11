import json
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import run  # noqa: E402

QUESTIONS = run.load_questions(run.HERE / "questions.json")


def _case(family, label, case_id="c1"):
    return {"id": case_id, "family": family, "state": "s", "label": label, "rationale": "r"}


class LoadCasesTest(unittest.TestCase):
    def test_shipped_cases_are_valid(self):
        cases = run.load_cases(run.HERE / "cases.jsonl", QUESTIONS)
        self.assertEqual({c["family"] for c in cases}, set(QUESTIONS))

    def _write(self, lines):
        handle = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
        handle.write("\n".join(json.dumps(line) for line in lines))
        handle.close()
        return handle.name

    def test_rejects_label_outside_options(self):
        path = self._write([_case("shell_gate", "maybe")])
        with self.assertRaisesRegex(ValueError, "not an option"):
            run.load_cases(path, QUESTIONS)

    def test_rejects_duplicate_id(self):
        path = self._write([_case("shell_gate", "allow"), _case("shell_gate", "deny")])
        with self.assertRaisesRegex(ValueError, "duplicate id"):
            run.load_cases(path, QUESTIONS)


class BuildRequestTest(unittest.TestCase):
    def test_strips_local_labels_from_score_question(self):
        payload = run.build_request(_case("model_route", "mid"), QUESTIONS, model="m")
        question = payload["questions"]["model_route"]
        self.assertNotIn("labels", question)
        self.assertEqual(question["type"], "score")
        self.assertEqual(payload["model"], "m")

    def test_omits_model_when_unset(self):
        self.assertNotIn("model", run.build_request(_case("shell_gate", "allow"), QUESTIONS))


class ScoreAnswerTest(unittest.TestCase):
    def test_choice_uses_server_confidence(self):
        answer = {"choice": "deny", "probabilities": {"allow": 0.1, "ask": 0.2, "deny": 0.7}, "confidence": 0.6}
        record = run.score_answer(_case("shell_gate", "deny"), QUESTIONS["shell_gate"], answer)
        self.assertTrue(record["correct"])
        self.assertEqual(record["confidence"], 0.6)
        self.assertEqual(record["confidence_source"], "server")

    def test_choice_falls_back_to_top_probability(self):
        answer = {"probabilities": {"allow": 0.2, "ask": 0.5, "deny": 0.3}}
        record = run.score_answer(_case("shell_gate", "ask"), QUESTIONS["shell_gate"], answer)
        self.assertEqual(record["confidence"], 0.5)
        self.assertEqual(record["confidence_source"], "top probability")

    def test_flags_unsafe_allow(self):
        answer = {"probabilities": {"allow": 0.8, "ask": 0.1, "deny": 0.1}}
        record = run.score_answer(_case("shell_gate", "deny"), QUESTIONS["shell_gate"], answer)
        self.assertFalse(record["correct"])
        self.assertTrue(record["unsafe_allow"])

    def test_ask_predicted_for_deny_is_not_unsafe(self):
        answer = {"probabilities": {"allow": 0.1, "ask": 0.8, "deny": 0.1}}
        record = run.score_answer(_case("shell_gate", "deny"), QUESTIONS["shell_gate"], answer)
        self.assertFalse(record["unsafe_allow"])

    def test_score_maps_level_indices_to_labels(self):
        answer = {"score": 1.8, "probabilities": {"0": 0.1, "1": 0.2, "2": 0.7}, "confidence": 0.4}
        record = run.score_answer(_case("model_route", "frontier"), QUESTIONS["model_route"], answer)
        self.assertEqual(record["predicted"], "frontier")
        self.assertTrue(record["correct"])
        self.assertAlmostEqual(record["abs_level_error"], 0.2)

    def test_noul(self):
        question = {"type": "noul", "instructions": "q"}
        record = run.score_answer(_case("x", "no"), question, {"noul": 0.2})
        self.assertTrue(record["correct"])
        self.assertAlmostEqual(record["confidence"], 0.8)


class SummarizeTest(unittest.TestCase):
    def test_cutoffs_latency_and_errors(self):
        records = [
            {"family": "a", "correct": True, "confidence": 0.95, "confidence_source": "server",
             "unsafe_allow": False, "latency_s": 2.0},
            {"family": "a", "correct": False, "confidence": 0.6, "confidence_source": "server",
             "unsafe_allow": True, "latency_s": 0.1},
            {"family": "b", "correct": True, "confidence": 0.75, "confidence_source": "server",
             "unsafe_allow": False, "latency_s": 0.3},
            {"family": "b", "error": "URLError"},
        ]
        summary = run.summarize(records)
        self.assertEqual(summary["errors"], 1)
        self.assertEqual(summary["unsafe_allows"], 1)
        self.assertAlmostEqual(summary["accuracy"], 2 / 3)
        self.assertEqual(summary["cold_start_s"], 2.0)
        self.assertEqual(summary["latency_p50_s"], 0.1)
        by_cutoff = {row["cutoff"]: row for row in summary["cutoffs"]}
        self.assertAlmostEqual(by_cutoff[0.7]["coverage"], 2 / 3)
        self.assertEqual(by_cutoff[0.7]["accuracy"], 1.0)
        self.assertEqual(by_cutoff[0.9]["coverage"], 1 / 3)


class _OracleHandler(BaseHTTPRequestHandler):
    """Answers every choice with its first option; records requests."""

    requests = []

    def do_POST(self):  # noqa: N802
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        type(self).requests.append((self.path, self.headers.get("Authorization"), body))
        answers = {}
        for name, question in body["questions"].items():
            first = list(question["criteria"])[0]
            answers[name] = {"type": "choice", "choice": first, "probabilities": {first: 0.9}, "confidence": 0.9}
        data = json.dumps({"answers": answers, "usage": {"input_tokens": 10, "output_tokens": 0}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_args):
        pass


class EndToEndTest(unittest.TestCase):
    def test_runs_against_local_stub(self):
        server = HTTPServer(("127.0.0.1", 0), _OracleHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_port}/v1/systemone"
            cases = [c for c in run.load_cases(run.HERE / "cases.jsonl", QUESTIONS) if c["family"] == "shell_gate"]
            records = run.run(cases, QUESTIONS, url, model="stub", api_key="tok")
        finally:
            server.shutdown()
        summary = run.summarize(records)
        self.assertEqual(summary["errors"], 0)
        expected_allow = sum(c["label"] == "allow" for c in cases)
        self.assertEqual(summary["families"]["shell_gate"]["correct"], expected_allow)
        self.assertEqual(summary["unsafe_allows"], sum(c["label"] == "deny" for c in cases))
        path, auth, body = _OracleHandler.requests[0]
        self.assertEqual(path, "/v1/systemone")
        self.assertEqual(auth, "Bearer tok")
        self.assertEqual(body["model"], "stub")
        self.assertTrue(all(r["output_tokens"] == 0 for r in records))

    def test_unreachable_server_is_recorded_as_error(self):
        case = run.load_cases(run.HERE / "cases.jsonl", QUESTIONS)[0]
        records = run.run([case], QUESTIONS, "http://127.0.0.1:9/v1/systemone", timeout=2)
        self.assertIn("error", records[0])


if __name__ == "__main__":
    unittest.main()
