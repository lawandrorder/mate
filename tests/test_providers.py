import tempfile
import unittest
from pathlib import Path

from mate.jobs.watch import run_watch
from mate.providers.cashback import DemoCashbackProvider
from mate.providers.codes import demo_code
from mate.providers.prices import DemoPriceProvider, _demo_price
from mate.store import JsonStore
from mate.config import Config
from mate.agent import MateAgent


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = JsonStore(Path(self.tmp.name) / "mate.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_demo_code_shape(self):
        self.assertEqual(demo_code("Demo Shop", "web"), "DEMO-WEB-DEMOSHOP")

    def test_cashback_credits_are_local(self):
        provider = DemoCashbackProvider(self.store)
        self.assertEqual(provider.balance("u"), 0.0)
        total = provider.credit_demo("u", 4.2, "demo credit")
        self.assertEqual(total, 4.2)
        self.assertEqual(provider.balance("u"), 4.2)

    def test_price_is_stable_for_same_url(self):
        url = "https://shop.example/nimbus-lamp"
        self.assertEqual(_demo_price(url), _demo_price(url))
        provider = DemoPriceProvider(self.store)
        first = provider.watch(url, "u")
        again = provider.watch(url, "u")
        self.assertEqual(first.last_price, again.last_price)
        self.assertFalse(first.dropped)

    def test_watch_job_simulate_drop(self):
        config = Config(data_dir=Path(self.tmp.name))
        agent = MateAgent(config)
        agent.handle("watch https://shop.example/nimbus-lamp", "u")
        lines = run_watch(config, simulate_drop=True)
        joined = "\n".join(lines)
        self.assertIn("[demo] Price drop", joined)
        self.assertIn("nimbus-lamp", joined)
        # Second pass should not drop again.
        again = "\n".join(run_watch(config, simulate_drop=True))
        self.assertIn("No demo drops", again)


if __name__ == "__main__":
    unittest.main()
