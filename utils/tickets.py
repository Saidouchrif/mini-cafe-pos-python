import os
from typing import Any, Optional

from PyQt5.QtWidgets import QMessageBox

from database import get_conn
from models import get_cafe_name


def generate_and_print_ticket(order_id: int, parent: Optional[Any] = None) -> None:
    conn = get_conn()
    c = conn.cursor()

    c.execute(
        """
        SELECT o.id, o.total, o.date, u.username
        FROM orders o
        JOIN users u ON o.serveur_id = u.id
        WHERE o.id=?
        """,
        (order_id,),
    )
    order = c.fetchone()

    if not order:
        conn.close()
        return

    c.execute(
        """
        SELECT p.name, oi.qty, oi.price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id=?
        """,
        (order_id,),
    )
    items = c.fetchall()
    conn.close()

    order_id_value, total, date_str, serveur_name = order
    cafe_name = get_cafe_name()

    lines = []
    lines.append(f"        {cafe_name}")
    lines.append("   Ticket de caisse officiel")
    lines.append("--------------------------------")
    lines.append(f"Serveur : {serveur_name}")
    lines.append(f"Date    : {date_str}")
    lines.append(f"N° Cmd  : {order_id_value}")
    lines.append("--------------------------------")

    for name, qty, price in items:
        line_total = qty * price
        lines.append(f"{name} x{qty}  {line_total:.2f} DH")

    lines.append("--------------------------------")
    lines.append(f"TOTAL À PAYER : {total:.2f} DH")
    lines.append("--------------------------------")
    lines.append("Merci pour votre visite !")
    lines.append("À très bientôt.")
    lines.append("")

    ticket_text = "\n".join(lines)
    ticket_name = f"ticket_{order_id_value}.txt"

    with open(ticket_name, "w", encoding="utf-8") as f:
        f.write(ticket_text)

    try:
        os.startfile(ticket_name, "print")
    except Exception:
        QMessageBox.information(
            parent,
            "Ticket généré",
            f"Ticket enregistré dans : {os.path.abspath(ticket_name)}\n"
            "Vous pouvez l'imprimer manuellement.",
        )
