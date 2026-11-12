import tempfile
import unittest
from pathlib import Path

from mate.agent import MateAgent
from mate.config import Config


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.agent = MateAgent(
            Config(data_dir=Path(self.tmp.name), openrouter_api_key=None)
        )
        self.user = "test-user"

    def tearDown(self):
        self.tmp.cleanup()

    def test_help_mentions_commands(self):
        reply = self.agent.handle("help", self.user)
        self.assertIn("cashback at", reply.text)
        self.assertFalse(reply.demo)

    def test_cashback_is_labeled_demo(self):
        reply = self.agent.handle("cashback at Demo Shop", self.user)
        self.assertEqual(reply.intent.name, "cashback")
        self.assertIn("[demo]", reply.text.lower())
        self.assertIn("demo.mate.local", reply.text)
        self.assertIn("Demo Shop", reply.text)
        self.assertIn("does not", reply.text.lower())

    def test_code_is_placeholder(self):
        reply = self.agent.handle("code for Demo Shop", self.user)
        self.assertIn("DEMO-", reply.text)
        self.assertIn("placeholder", reply.text.lower())
        self.assertNotRegex(reply.text, r"\b[A-Z]+-EVERLANE-35\b")

    def test_track_and_share(self):
        first = self.agent.handle("track DEMO-123456", self.user)
        self.assertIn("DEMO-123456", first.text)
        self.assertIn("shipped", first.text.lower())
        second = self.agent.handle("where's my order DEMO-123456", self.user)
        self.assertIn("out for delivery", second.text.lower())
        share = self.agent.handle("tell my room-mate", self.user)
        self.assertIn("room-mate", share.text.lower())
        self.assertIn("No real message", share.text)

    def test_share_without_package(self):
        reply = self.agent.handle("tell my room-mate", "fresh-user")
        self.assertIn("don't have a demo package", reply.text.lower())

    def test_watch_and_balance(self):
        watch = self.agent.handle("watch https://shop.example/nimbus-lamp", self.user)
        self.assertIn("https://shop.example/nimbus-lamp", watch.text)
        self.assertIn("demo price", watch.text.lower())
        balance = self.agent.handle("balance", self.user)
        self.assertIn("$0.00", balance.text)
        self.assertIn("[demo]", balance.text)

    def test_unknown_without_llm(self):
        reply = self.agent.handle("what's the weather in helsinki", self.user)
        self.assertEqual(reply.intent.name, "unknown")
        self.assertFalse(reply.used_llm)
        self.assertIn("cashback at", reply.text)


if __name__ == "__main__":
    unittest.main()
