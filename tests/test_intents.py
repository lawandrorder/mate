import unittest

from mate.intents import (
    INTENT_BALANCE,
    INTENT_CASHBACK,
    INTENT_CODE,
    INTENT_GREET,
    INTENT_HELP,
    INTENT_SHARE,
    INTENT_TRACK,
    INTENT_UNKNOWN,
    INTENT_WATCH,
    parse_intent,
)


class IntentTests(unittest.TestCase):
    def test_cashback_at_store(self):
        intent = parse_intent("cashback at Everlane")
        self.assertEqual(intent.name, INTENT_CASHBACK)
        self.assertEqual(intent.store, "Everlane")

    def test_any_deals_at_store(self):
        intent = parse_intent("any deals at Everlane?")
        self.assertEqual(intent.name, INTENT_CASHBACK)
        self.assertEqual(intent.store, "Everlane")

    def test_about_to_buy(self):
        intent = parse_intent("about to buy these sunglasses at Quay")
        self.assertEqual(intent.name, INTENT_CASHBACK)
        self.assertEqual(intent.store, "Quay")

    def test_code_for_store(self):
        intent = parse_intent("code for Brooklinen")
        self.assertEqual(intent.name, INTENT_CODE)
        self.assertEqual(intent.store, "Brooklinen")

    def test_any_codes(self):
        intent = parse_intent("any codes for Brooklinen?")
        self.assertEqual(intent.name, INTENT_CODE)
        self.assertEqual(intent.store, "Brooklinen")

    def test_track_number(self):
        intent = parse_intent("track 1Z999AA10123456784")
        self.assertEqual(intent.name, INTENT_TRACK)
        self.assertEqual(intent.tracking_number, "1Z999AA10123456784")

    def test_wheres_my_store_order(self):
        intent = parse_intent("where's my LANEIGE order?")
        self.assertEqual(intent.name, INTENT_TRACK)
        self.assertEqual(intent.store, "LANEIGE")
        self.assertIsNone(intent.tracking_number)

    def test_watch_url(self):
        intent = parse_intent("watch https://shop.example/item")
        self.assertEqual(intent.name, INTENT_WATCH)
        self.assertEqual(intent.url, "https://shop.example/item")

    def test_price_drop_phrasing(self):
        intent = parse_intent("can you track the price on this? https://shop.example/item")
        self.assertEqual(intent.name, INTENT_WATCH)
        self.assertTrue(intent.url.startswith("https://"))

    def test_bare_url(self):
        intent = parse_intent("https://shop.example/item")
        self.assertEqual(intent.name, INTENT_WATCH)

    def test_share_roommate(self):
        self.assertEqual(parse_intent("tell my room-mate").name, INTENT_SHARE)
        self.assertEqual(parse_intent("share tracking with my roommate").name, INTENT_SHARE)

    def test_balance_help_greet(self):
        self.assertEqual(parse_intent("what's my balance").name, INTENT_BALANCE)
        self.assertEqual(parse_intent("help").name, INTENT_HELP)
        self.assertEqual(parse_intent("hey").name, INTENT_GREET)

    def test_empty_is_unknown(self):
        self.assertEqual(parse_intent("").name, INTENT_UNKNOWN)
        self.assertEqual(parse_intent("asdf qwer zxcv").name, INTENT_UNKNOWN)


if __name__ == "__main__":
    unittest.main()
