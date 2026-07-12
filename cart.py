# cart.py
carts: dict[str, list] = {}   # session_id → list of cart items

def add_to_cart(session_id: str, product: dict, qty: int = 1):
    cart = carts.setdefault(session_id, [])
    for item in cart:
        if item["id"] == product["id"]:
            item["qty"] += qty
            return
    cart.append({**product, "qty": qty})

def get_cart(session_id: str) -> list:
    return carts.get(session_id, [])

def clear_cart(session_id: str):
    carts[session_id] = []

def get_cart_total(session_id: str) -> float:
    return sum(item["mrp"] * item["qty"] for item in get_cart(session_id))