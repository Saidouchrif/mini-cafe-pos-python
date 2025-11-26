from datetime import datetime
from typing import Any, Dict, List, Optional

from database import get_conn


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, username, role FROM users WHERE username=? AND password=?",
        (username, password),
    )
    row = c.fetchone()
    conn.close()
    if row:
        user_id, uname, role = row
        return {"id": user_id, "username": uname, "role": role}
    return None


def get_all_servers(include_admin: bool = False) -> List[Dict[str, Any]]:
    conn = get_conn()
    c = conn.cursor()
    if include_admin:
        c.execute("SELECT id, username, role FROM users ORDER BY username")
    else:
        c.execute(
            "SELECT id, username, role FROM users WHERE role != 'admin' ORDER BY username"
        )
    rows = c.fetchall()
    conn.close()
    return [
        {"id": r[0], "username": r[1], "role": r[2]}
        for r in rows
    ]


def create_server(username: str, password: str, role: str = "serveur") -> None:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, password, role),
    )
    conn.commit()
    conn.close()


def update_server(user_id: int, username: str, password: str) -> None:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET username=?, password=? WHERE id=?",
        (username, password, user_id),
    )
    conn.commit()
    conn.close()


def delete_server(user_id: int) -> bool:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False
    role = row[0]
    if role == "admin":
        conn.close()
        return False
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return True


def get_categories() -> List[Dict[str, Any]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name FROM categories ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1]}
        for r in rows
    ]


def create_category(name: str) -> None:
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def update_category(category_id: int, name: str) -> None:
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE categories SET name=? WHERE id=?", (name, category_id))
    conn.commit()
    conn.close()


def delete_category(category_id: int) -> bool:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM products WHERE category_id=?", (category_id,))
    row = c.fetchone()
    if row and row[0] > 0:
        conn.close()
        return False
    c.execute("DELETE FROM categories WHERE id=?", (category_id,))
    conn.commit()
    conn.close()
    return True


def get_products_by_category(category_id: int) -> List[Dict[str, Any]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, name, price FROM products WHERE category_id=? ORDER BY name",
        (category_id,),
    )
    rows = c.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "price": r[2]}
        for r in rows
    ]


def create_product(name: str, price: float, category_id: int) -> None:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO products (name, price, category_id) VALUES (?, ?, ?)",
        (name, price, category_id),
    )
    conn.commit()
    conn.close()


def update_product(product_id: int, name: str, price: float, category_id: int) -> None:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "UPDATE products SET name=?, price=?, category_id=? WHERE id=?",
        (name, price, category_id, product_id),
    )
    conn.commit()
    conn.close()


def delete_product(product_id: int) -> None:
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()


def create_order(serveur_id: int, cart: Dict[int, Dict[str, Any]]) -> int:
    total = sum(item["price"] * item["qty"] for item in cart.values())
    conn = get_conn()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "INSERT INTO orders (serveur_id, total, date) VALUES (?, ?, ?)",
        (serveur_id, total, now_str),
    )
    order_id = c.lastrowid
    for product_id, item in cart.items():
        c.execute(
            "INSERT INTO order_items (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
            (order_id, product_id, item["qty"], item["price"]),
        )
    conn.commit()
    conn.close()
    return order_id


def get_orders_between_dates(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        SELECT o.id, o.total, o.date, u.username
        FROM orders o
        JOIN users u ON o.serveur_id = u.id
        WHERE date(o.date) BETWEEN ? AND ?
        ORDER BY o.date
        """,
        (start_date, end_date),
    )
    rows = c.fetchall()
    conn.close()
    return [
        {"id": r[0], "total": r[1], "date": r[2], "serveur": r[3]}
        for r in rows
    ]


def get_order_items(order_id: int) -> List[Dict[str, Any]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        SELECT p.name, oi.qty, oi.price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id=?
        """,
        (order_id,),
    )
    rows = c.fetchall()
    conn.close()
    return [
        {"name": r[0], "qty": r[1], "price": r[2], "total": r[1] * r[2]}
        for r in rows
    ]


def get_cafe_name() -> str:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT cafe_name FROM settings ORDER BY id LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        return row[0]
    return "Café Caisse Manager"


def update_cafe_name(new_name: str) -> None:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM settings ORDER BY id LIMIT 1")
    row = c.fetchone()
    if row:
        settings_id = row[0]
        c.execute(
            "UPDATE settings SET cafe_name=? WHERE id=?",
            (new_name, settings_id),
        )
    else:
        c.execute(
            "INSERT INTO settings (cafe_name) VALUES (?)",
            (new_name,),
        )
    conn.commit()
    conn.close()
