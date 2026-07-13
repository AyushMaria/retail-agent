# cart.py
carts: dict[str, list] = {}
pending_checkout: dict[str, bool] = {}   # tracks if a session is awaiting confirmation

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
    pending_checkout[session_id] = False

def get_cart_total(session_id: str) -> float:
    return sum(item["mrp"] * item["qty"] for item in get_cart(session_id))

def is_cart_empty(session_id: str) -> bool:
    return len(get_cart(session_id)) == 0

def start_checkout(session_id: str) -> dict:
    """Prepare an order summary and mark session as awaiting confirmation."""
    if is_cart_empty(session_id):
        return {"error": "Cart is empty. Add items before checking out."}
    pending_checkout[session_id] = True
    return {
        "items": get_cart(session_id),
        "total": get_cart_total(session_id),
        "message": "Please confirm to place this order."
    }

def is_awaiting_confirmation(session_id: str) -> bool:
    return pending_checkout.get(session_id, False)