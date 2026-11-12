import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from mate.adapters.twilio import twiml_message, validate_signature
from mate.agent import MateAgent
from mate.config import Config
from mate.server import serve_in_thread


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.config = Config(
            host="127.0.0.1",
            port=0,
            data_dir=Path(self.tmp.name),
            openrouter_api_key=None,
        )
        self.agent = MateAgent(self.config)
        self.server, self.thread = serve_in_thread(self.config)
        self.port = self.server.server_address[1]
        self.base = f"http://127.0.0.1:{self.port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.tmp.cleanup()

    def _get(self, path: str):
        with urlopen(self.base + path, timeout=5) as response:
            return response.status, response.headers.get("Content-Type"), response.read()

    def _post(self, path: str, data: bytes, content_type: str, headers=None):
        req = Request(self.base + path, data=data, method="POST")
        req.add_header("Content-Type", content_type)
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)
        with urlopen(req, timeout=5) as response:
            return response.status, response.headers.get("Content-Type"), response.read()

    def test_health(self):
        status, _, body = self._get("/health")
        self.assertEqual(status, 200)
        payload = json.loads(body)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["openrouter"])

    def test_homepage(self):
        status, content_type, body = self._get("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", content_type)
        self.assertIn(b"Your mate while you shop", body)
        self.assertIn(b"fictional", body)

    def test_message_endpoint(self):
        status, _, body = self._post(
            "/api/message",
            json.dumps({"text": "cashback at Demo Shop", "user_id": "server-test"}).encode(),
            "application/json",
        )
        self.assertEqual(status, 200)
        payload = json.loads(body)
        self.assertEqual(payload["intent"]["name"], "cashback")
        self.assertIn("[demo]", payload["reply"])
        self.assertTrue(payload["demo"])

    def test_twilio_webhook(self):
        status, content_type, body = self._post(
            "/webhooks/twilio",
            urlencode({"Body": "code for Demo Shop", "From": "+15555550100"}).encode(),
            "application/x-www-form-urlencoded",
        )
        self.assertEqual(status, 200)
        self.assertIn("xml", content_type)
        self.assertIn(b"<Response>", body)
        self.assertIn(b"DEMO-", body)
        self.assertIn(b"[demo]", body)

    def test_twiml_escapes(self):
        xml = twiml_message('use 2 < 3 & "quotes"')
        self.assertIn("&lt;", xml)
        self.assertIn("&amp;", xml)
        self.assertIn("&quot;", xml)
        self.assertNotIn("< 3", xml)

    def test_signature_helper_rejects_empty(self):
        self.assertFalse(validate_signature("", "http://x", {}, ""))
        self.assertFalse(validate_signature("token", "http://x", {"Body": "hi"}, "nope"))


if __name__ == "__main__":
    unittest.main()
