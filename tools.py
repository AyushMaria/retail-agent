from supabase import create_client
import os
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