"""Tests for the local server (pipeline-app/serve.py), requirements R-SRV-1 to R-SRV-3.

The server is started on a free port inside the test. No test starts a live run: the
only requests to /api/run are ones the server must refuse, so no API quota is used.
"""

import http.client
import importlib.util
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("serve", ROOT / "pipeline-app" / "serve.py")
serve = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(serve)

VALID_RUN = {"goal": "canary", "scenarios": ["direct"], "model": "gemini-3.5-flash-lite", "runs": 1, "turns": 1}


class TestValidateRequest(unittest.TestCase):
    """Technique: equivalence partitioning and boundary value analysis on a live run
    request (R-SRV-2). Runs and turns are valid from 1 to 5, scenarios from 1 to 3."""

    def check(self, **change):
        return serve.validate_request({**VALID_RUN, **change})

    def test_TC_SRV_01_valid_request(self):
        req = self.check()
        self.assertEqual((req.model, req.runs, req.turns, len(req.combo)), ("gemini-3.5-flash-lite", 1, 1, 1))

    def test_TC_SRV_02_runs_and_turns_boundaries(self):
        for field in ("runs", "turns"):
            for ok in (1, 5):
                self.assertEqual(getattr(self.check(**{field: ok}), field), ok)
            for bad in (0, 6, -1, 2.5, "3"):
                with self.subTest(field=field, value=bad), self.assertRaises(ValueError):
                    self.check(**{field: bad})

    def test_TC_SRV_03_scenario_count_boundaries(self):
        self.assertEqual(len(self.check(scenarios=["direct", "authority", "roleplay"]).combo), 3)
        for bad in ([], ["direct", "authority", "roleplay", "fiction"], ["direct", "direct"], ["nope"], "direct"):
            with self.subTest(scenarios=bad), self.assertRaises(ValueError):
                self.check(scenarios=bad)

    def test_TC_SRV_04_model_and_goal_classes(self):
        self.assertEqual(self.check(model="gemini-3.1-flash-lite").model, "gemini-3.1-flash-lite")
        self.assertEqual(self.check(model="gemini-" + "x" * 61).model, "gemini-" + "x" * 61)  # longest allowed
        for bad in ("gpt-4.1-mini", "Gemini-3.5-flash", "gemini-", "gemini-3.5 flash", "gemini-3.5;rm", "gemini-" + "x" * 62):
            with self.subTest(model=bad), self.assertRaises(ValueError):
                self.check(model=bad)
        with self.assertRaises(ValueError):
            self.check(goal="steal")

    @unittest.expectedFailure
    def test_TC_SRV_05_true_is_not_a_number(self):
        """[R-SRV-2] Known issue ISS-10: Python counts True as the number 1, so {"runs": true} passes."""
        with self.assertRaises(ValueError):
            self.check(runs=True)

    @unittest.expectedFailure
    def test_TC_SRV_06_true_is_not_a_scale(self):
        """[R-APP-2] Known issue ISS-10: the same in the Data section: {"scale": true} builds 1 copy."""
        from datalab.lab import DataLab
        with self.assertRaises(ValueError):
            DataLab().handle({"action": "build", "scale": True})


class TestHttp(unittest.TestCase):
    """Technique: equivalence partitioning on who is asking (R-SRV-1): the right page,
    another host name, another website, no token, a wrong token; and on the request
    itself (R-SRV-3): wrong type, too large, unknown path."""

    @classmethod
    def setUpClass(cls):
        cls.lab = serve.Lab("test-token")
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), serve.make_handler(cls.lab, 1))
        cls.port = cls.server.server_address[1]
        cls.server.RequestHandlerClass = serve.make_handler(cls.lab, cls.port)
        cls.server.handle_error = lambda request, address: None  # keep the test output clean
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def send(self, method, path, body=None, host=None, token="test-token", origin=None, content_type="application/json", length=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        headers = {"Host": host or f"127.0.0.1:{self.port}"}
        if token is not None:
            headers["X-Lab-Token"] = token
        if origin:
            headers["Origin"] = origin
        data = None
        if body is not None:
            data = body if isinstance(body, bytes) else json.dumps(body).encode()
            headers["Content-Type"] = content_type
            headers["Content-Length"] = str(len(data)) if length is None else length
        conn.request(method, path, data, headers)
        res = conn.getresponse()
        status, payload = res.status, res.read()
        conn.close()
        return status, payload

    def test_TC_SRV_07_page_loads_for_the_right_host(self):
        """[R-SRV-1]"""
        status, payload = self.send("GET", "/", token=None)
        self.assertEqual(status, 200)
        self.assertIn(b"window.CANARY_LAB_LIVE", payload)
        self.assertIn(b"Canary Lab", payload)

    def test_TC_SRV_08_other_host_names_are_refused(self):
        """[R-SRV-1]"""
        for host in ("evil.example", f"evil.example:{self.port}", "127.0.0.1:1"):
            with self.subTest(host=host):
                self.assertEqual(self.send("GET", "/", host=host, token=None)[0], 403)
                self.assertEqual(self.send("POST", "/api/datalab", {"action": "options"}, host=host)[0], 403)

    def test_TC_SRV_09_api_needs_the_token(self):
        """[R-SRV-1]"""
        self.assertEqual(self.send("POST", "/api/datalab", {"action": "options"}, token=None)[0], 403)
        self.assertEqual(self.send("POST", "/api/datalab", {"action": "options"}, token="guess")[0], 403)
        self.assertEqual(self.send("GET", "/api/job/abc", token=None)[0], 403)

    def test_TC_SRV_10_other_websites_are_refused(self):
        """[R-SRV-1]"""
        status, _ = self.send("POST", "/api/datalab", {"action": "options"}, origin="https://evil.example")
        self.assertEqual(status, 403)

    def test_TC_SRV_11_right_token_and_origin_are_served(self):
        """[R-SRV-1]"""
        status, payload = self.send("POST", "/api/datalab", {"action": "options"}, origin=f"http://127.0.0.1:{self.port}")
        self.assertEqual(status, 200)
        self.assertIn("models", json.loads(payload))

    def test_TC_SRV_12_wrong_type_and_size(self):
        """[R-SRV-3]"""
        self.assertEqual(self.send("POST", "/api/datalab", {"action": "options"}, content_type="text/plain")[0], 415)
        self.assertEqual(self.send("POST", "/api/datalab", b"x" * (serve.MAX_BODY + 1))[0], 413)
        self.assertEqual(self.send("POST", "/api/datalab", b"{}", length="0")[0], 413)

    def test_TC_SRV_13_size_boundary(self):
        """[R-SRV-3] Technique: boundary value analysis: a body of exactly MAX_BODY bytes is accepted."""
        body = json.dumps({"action": "options", "pad": ""}).encode()
        exact = body.replace(b'""', b'"' + b"x" * (serve.MAX_BODY - len(body)) + b'"')
        self.assertEqual(len(exact), serve.MAX_BODY)
        self.assertEqual(self.send("POST", "/api/datalab", exact)[0], 200)

    def test_TC_SRV_14_bad_run_requests_start_nothing(self):
        """[R-SRV-2]"""
        status, payload = self.send("POST", "/api/run", {**VALID_RUN, "runs": 9})
        self.assertEqual(status, 400)
        self.assertIn("runs", json.loads(payload)["error"])
        self.assertEqual(self.lab.jobs, {})
        self.assertTrue(self.lab.busy.acquire(blocking=False))  # the run lock was not taken
        self.lab.busy.release()

    def test_TC_SRV_15_unknown_paths(self):
        """[R-SRV-3]"""
        self.assertEqual(self.send("GET", "/secrets", token=None)[0], 404)
        self.assertEqual(self.send("POST", "/api/other", {"a": 1})[0], 404)
        self.assertEqual(self.send("GET", "/api/job/unknown")[0], 404)

    def test_TC_SRV_16_bad_datalab_request_gives_400(self):
        """[R-SRV-3]"""
        status, payload = self.send("POST", "/api/datalab", {"action": "sort", "algorithm": "bogo"})
        self.assertEqual(status, 400)
        self.assertIn("error", json.loads(payload))

    @unittest.expectedFailure
    def test_TC_SRV_17_length_that_is_not_a_number(self):
        """[R-SRV-3] Known issue ISS-09: a Content-Length that is not a number crashes the request
        handler, so the browser gets a dropped connection instead of an error message."""
        self.assertEqual(self.send("POST", "/api/datalab", b'{"action": "options"}', length="abc")[0], 400)


if __name__ == "__main__":
    unittest.main()
