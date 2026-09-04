#!/usr/bin/env python3
"""Tests for the dependency-free monitoring health-check helper."""
from __future__ import annotations

import http.server
import subprocess
import threading
import unittest
from pathlib import Path
import sys


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        status = 503 if self.path == "/degraded" else 204
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        pass


class HealthcheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def run_check(self, url: str) -> tuple[int, str]:
        completed = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("healthcheck.py")), url],
            capture_output=True,
            text=True,
            check=False,
        )
        return completed.returncode, completed.stdout + completed.stderr

    def test_successful_endpoint_returns_zero(self) -> None:
        result, output = self.run_check(self.base_url + "/health")
        self.assertEqual(result, 0)
        self.assertIn("status=204", output)

    def test_http_error_returns_nonzero(self) -> None:
        result, output = self.run_check(self.base_url + "/degraded")
        self.assertEqual(result, 1)
        self.assertIn("health=FAIL", output)


if __name__ == "__main__":
    unittest.main()
