"""Run with python -m app.demo."""
from .core import Order, connect, dispatch_once, place_order


def main() -> None:
    conn = connect()
    place_order(conn, Order("ORDER-1001", "Blue notebook", 2))
    place_order(conn, Order("ORDER-1002", "Pencil pack", 3))
    delivered = dispatch_once(conn)
    print(f"Delivered outbox messages: {delivered}")
    for row in conn.execute("SELECT * FROM fulfilments ORDER BY order_id"):
        print(f"{row['order_id']}: {row['quantity']} x {row['item']}")
    conn.close()


if __name__ == "__main__":
    main()
