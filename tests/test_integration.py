import unittest
from app.core import Order, connect, dispatch_once, handle_event, place_order


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.conn = connect()

    def tearDown(self):
        self.conn.close()

    def test_atomic_order_and_outbox(self):
        self.assertTrue(place_order(self.conn, Order("A-1", "Pen", 2)))
        self.assertEqual(self.conn.execute("SELECT count(*) FROM orders").fetchone()[0], 1)
        self.assertEqual(self.conn.execute("SELECT count(*) FROM outbox").fetchone()[0], 1)

    def test_duplicate_order_is_not_replaced(self):
        self.assertTrue(place_order(self.conn, Order("A-1", "Pen", 2)))
        self.assertFalse(place_order(self.conn, Order("A-1", "Other", 4)))
        self.assertEqual(self.conn.execute("SELECT item FROM orders").fetchone()[0], "Pen")

    def test_delivery_and_replay_are_idempotent(self):
        place_order(self.conn, Order("A-1", "Pen", 2))
        row = self.conn.execute("SELECT event_id,payload FROM outbox").fetchone()
        self.assertEqual(dispatch_once(self.conn), 1)
        self.assertFalse(handle_event(self.conn, row["event_id"], row["payload"]))
        self.assertEqual(self.conn.execute("SELECT count(*) FROM fulfilments").fetchone()[0], 1)
        self.assertEqual(dispatch_once(self.conn), 0)

    def test_validation_does_not_store_order(self):
        with self.assertRaises(ValueError):
            place_order(self.conn, Order("A-1", "Pen", 0))
        self.assertEqual(self.conn.execute("SELECT count(*) FROM orders").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
