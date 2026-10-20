"""Smoke test for the Vercel webhook endpoint.

Starts the handler on a local port and checks that:
  - GET  /api/webhook returns the diagnostics payload
  - POST /api/webhook accepts an update and answers 200
"""
import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer

from api.webhook import handler

MOCK_UPDATE = {
    "update_id": 123456789,
    "message": {
        "message_id": 1,
        "from": {"id": 123456, "is_bot": False, "first_name": "Test"},
        "chat": {"id": 123456, "type": "private"},
        "date": 1609459200,
        "text": "/start",
    },
}


class TestWebhook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def _url(self, path="/api/webhook"):
        return f"http://127.0.0.1:{self.port}{path}"

    def test_get_returns_diagnostics(self):
        with urllib.request.urlopen(self._url(), timeout=30) as resp:
            self.assertEqual(resp.status, 200)
            payload = json.loads(resp.read().decode("utf-8"))
        self.assertIn(payload.get("status"), ("ok", "error"))
        self.assertIn("bot", payload)
        self.assertIn("webhook", payload)

    def test_post_accepts_update(self):
        req = urllib.request.Request(
            self._url(),
            data=json.dumps(MOCK_UPDATE).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            self.assertEqual(resp.status, 200)


if __name__ == "__main__":
    unittest.main()
