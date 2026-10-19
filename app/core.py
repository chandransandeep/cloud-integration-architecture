"""SQLite outbox prototype. For architecture demonstration, not production use."""
from __future__ import annotations
import json
import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    order_id: str
    item: str
    quantity: int


def connect(path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS orders (
          order_id TEXT PRIMARY KEY, item TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity > 0)
        );
        CREATE TABLE IF NOT EXISTS outbox (
          event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL,
          payload TEXT NOT NULL, delivered INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS processed_events (event_id TEXT PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS fulfilments (
          order_id TEXT PRIMARY KEY, item TEXT NOT NULL, quantity INTEGER NOT NULL
        );
    """)
    return conn


def place_order(conn: sqlite3.Connection, order: Order) -> bool:
    """Creates order and outbox event atomically; duplicates return False."""
    if not order.order_id.strip() or not order.item.strip() or order.quantity <= 0:
        raise ValueError("Nonempty order ID/item and positive quantity required")
    with conn:
        if conn.execute("SELECT 1 FROM orders WHERE order_id = ?", (order.order_id,)).fetchone():
            return False
        conn.execute("INSERT INTO orders VALUES (?, ?, ?)", (order.order_id, order.item, order.quantity))
        event = {"order_id": order.order_id, "item": order.item, "quantity": order.quantity}
        conn.execute(
            "INSERT INTO outbox(event_id,event_type,payload) VALUES (?, ?, ?)",
            (f"order-placed:{order.order_id}", "OrderPlaced", json.dumps(event)),
        )
    return True


def handle_event(conn: sqlite3.Connection, event_id: str, payload: str) -> bool:
    """Idempotent consumer, returns True only for first successful delivery."""
    data = json.loads(payload)
    with conn:
        if conn.execute("SELECT 1 FROM processed_events WHERE event_id=?", (event_id,)).fetchone():
            return False
        conn.execute(
            "INSERT INTO fulfilments VALUES (?, ?, ?)",
            (data["order_id"], data["item"], data["quantity"]),
        )
        conn.execute("INSERT INTO processed_events VALUES (?)", (event_id,))
    return True


def dispatch_once(conn: sqlite3.Connection) -> int:
    """Simulates successful broker delivery. Does not model distributed transactions."""
    rows = conn.execute(
        "SELECT event_id,payload FROM outbox WHERE delivered=0 ORDER BY event_id"
    ).fetchall()
    for row in rows:
        handle_event(conn, row["event_id"], row["payload"])
        with conn:
            conn.execute("UPDATE outbox SET delivered=1 WHERE event_id=?", (row["event_id"],))
    return len(rows)
