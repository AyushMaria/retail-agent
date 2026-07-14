from supabase import create_client
import os
import json
from dotenv import load_dotenv
load_dotenv()

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

def search_products(query: str) -> list[dict]:
    """Search products by name keyword."""
    response = (
        supabase.table("products")
        .select("id, item_name, main_group, sub_group, mrp, upc_ean_code")
        .ilike("item_name", f"%{query}%")
        .limit(10)
        .execute()
    )
    return response.data

def get_products_by_category(category: str) -> list[dict]:
    """Get products filtered by main_group category."""
    response = (
        supabase.table("products")
        .select("id, item_name, main_group, sub_group, mrp")
        .ilike("main_group", f"%{category}%")
        .limit(20)
        .execute()
    )
    return response.data

def get_product_by_id(product_id: int) -> dict | None:
    """Get a single product's full details by ID."""
    response = (
        supabase.table("products")
        .select("*")
        .eq("id", product_id)
        .single()
        .execute()
    )
    return response.data

def list_categories() -> list[str]:
    """List all unique main_group categories."""
    response = (
        supabase.table("products")
        .select("main_group")
        .execute()
    )
    seen = set()
    categories = []
    for row in response.data:
        cat = row["main_group"]
        if cat and cat not in seen:
            seen.add(cat)
            categories.append(cat)
    return sorted(categories)

def place_order(session_id: str, items: list[dict], total: float,
                 customer_name: str = None, customer_phone: str = None) -> dict:
    """Save a confirmed order to Supabase. Stock is managed separately via barcode scanning at the shop."""
    try:
        response = (
            supabase.table("orders")
            .insert({
                "session_id":     session_id,
                "customer_name":  customer_name,
                "customer_phone": customer_phone,
                "items":          json.dumps(items),
                "total_amount":   total,
                "status":         "confirmed",
            })
            .execute()
        )
        order_id = response.data[0]["id"]
        return {"success": True, "order_id": order_id}
    except Exception as e:
        return {"success": False, "error": str(e)}
    
def check_stock(product_id: int) -> dict:
    """Check current available quantity for a product."""
    response = (
        supabase.table("products")
        .select("item_name, quantity")
        .eq("id", product_id)
        .single()
        .execute()
    )
    return response.data