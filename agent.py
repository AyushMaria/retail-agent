import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools import search_products, get_products_by_category, get_product_by_id, list_categories

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL  = "gemini-2.5-flash"

SYSTEM_PROMPT = """You are a helpful shopping assistant for a retail store.
Help customers find products, check prices, and place orders.
When showing products, always include the name and MRP price formatted as ₹XX.
Keep responses concise and friendly.
After showing products, ask if the customer wants to add any to their cart."""

# ─── Tool declarations ────────────────────────────────────────────────────────
TOOLS = types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name="search_products",
        description="Search for products by name keyword. Use when customer asks for a specific product.",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "query": types.Schema(type="STRING", description="Product name or keyword")
            },
            required=["query"]
        )
    ),
    types.FunctionDeclaration(
        name="get_products_by_category",
        description="Get products filtered by category like GROCERY, PERSONAL CARE, HOME & KITCHEN.",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "category": types.Schema(type="STRING", description="Category name")
            },
            required=["category"]
        )
    ),
    types.FunctionDeclaration(
        name="get_product_by_id",
        description="Get full details of a product by its ID.",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "product_id": types.Schema(type="INTEGER", description="The product ID")
            },
            required=["product_id"]
        )
    ),
    types.FunctionDeclaration(
        name="list_categories",
        description="List all available product categories. Use when customer asks what is available.",
        parameters=types.Schema(type="OBJECT", properties={})
    ),
])

TOOL_MAP = {
    "search_products":        search_products,
    "get_products_by_category": get_products_by_category,
    "get_product_by_id":      get_product_by_id,
    "list_categories":        list_categories,
}

# ─── Agent loop ───────────────────────────────────────────────────────────────
def run_agent(user_message: str, history: list) -> tuple[str, list]:
    """
    Process a user message and return the agent reply.
    history: list of google.genai Content dicts preserved across turns.
    Returns: (reply_text, updated_history)
    """
    history.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[TOOLS],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode="AUTO")
        )
    )

    # Agentic loop — keep resolving tool calls until a text reply is returned
    current_history = list(history)
    while True:
        response = client.models.generate_content(
            model=MODEL,
            contents=current_history,
            config=config
        )

        candidate = response.candidates[0].content

        # Check if any part is a function call
        fn_calls = [p for p in candidate.parts if p.function_call is not None]

        if not fn_calls:
            # Model returned a text response — done
            reply = response.text
            history.append(candidate)
            return reply, history

        # Execute all tool calls in this turn
        current_history.append(candidate)
        fn_results = []
        for part in fn_calls:
            fn_name   = part.function_call.name
            fn_args   = dict(part.function_call.args)
            print(f"  [tool] {fn_name}({fn_args})")   # debug log

            result = TOOL_MAP[fn_name](**fn_args)
            fn_results.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=fn_name,
                        response={"result": json.dumps(result, default=str)}
                    )
                )
            )

        current_history.append(
            types.Content(role="tool", parts=fn_results)
        )
