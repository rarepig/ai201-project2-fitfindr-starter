# README

## Tool Inventory

### `search_listings(description: str, size: str | None, max_price: float | None) -> list[dict]`
Searches the mock listings dataset for items matching the user's description, size, and price ceiling. Scores results by keyword overlap with the description (title matches weighted 2x, description and style_tags weighted 1x). Returns a list of matching listing dicts sorted by relevance, or an empty list if nothing matches.

### `suggest_outfit(new_item: dict, wardrobe: dict) -> str`
Given a thrifted item and the user's wardrobe, calls the Groq LLM to suggest 1–2 complete outfit combinations using specific wardrobe pieces. If `wardrobe["items"]` is empty, returns general styling advice without referencing specific pieces.

### `create_fit_card(outfit: str, new_item: dict) -> str`
Generates a short, casual Instagram-style caption based on the outfit suggestion and the thrifted item. Uses a higher LLM temperature (1.2) to ensure varied output. If `outfit` is empty or None, returns an error message string without calling the LLM.

### `compare_price(item: dict, listings: list[dict]) -> str`
Estimates whether a selected item's price is fair by comparing it against other listings returned by `search_listings`. Compares within the same category when possible, falls back to all listings otherwise. Returns a string with a price assessment and reasoning.

---

## How the Planning Loop Works

The planning loop checks the result of each tool call before deciding what to do next:

1. Parse the user query to extract `description`, `size`, and `max_price` using regex.
2. Call `search_listings()`. If the result is empty, store an error message in `session["error"]` and return early — no further tools are called.
3. If `len(results) >= 2`, call `compare_price()`. Otherwise, skip silently.
4. Call `suggest_outfit()` with the top result and the user's wardrobe.
5. Call `create_fit_card()` with the outfit suggestion and selected item.
6. Return the completed session dict.

---

## State Management

The agent maintains a `session` dictionary throughout a single interaction. Values are stored after each tool call and passed directly into the next tool without requiring user re-entry:

- `session["search_results"]` — full list of results from `search_listings`
- `session["selected_item"]` — top result, passed into `compare_price` and `suggest_outfit`
- `session["price_comparison"]` — string result from `compare_price`
- `session["outfit_suggestion"]` — string result from `suggest_outfit`, passed into `create_fit_card`
- `session["fit_card"]` — final caption string from `create_fit_card`
- `session["error"]` — set if any tool fails or returns nothing; causes early return

---

## Error Handling

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| `search_listings` | No results match the query | Sets `session["error"]`, returns early. Tells user: "No listings matched your search. Try raising your max price, removing the size filter, or using a different description." |
| `suggest_outfit` | Wardrobe is empty | Returns general styling advice without referencing specific wardrobe pieces. Does not crash. |
| `create_fit_card` | Outfit input is empty or None | Returns error message string without calling the LLM: "Could not generate a fit card — outfit description is missing. Please try again." |
| `compare_price` | Fewer than 2 listings available | Tool is not called at all. Skipped silently. |

**Concrete example from testing:**
Running `search_listings("designer ballgown", size="XXS", max_price=5)` returns `[]`. The agent sets `session["error"] = "No listings matched your search..."` and returns immediately without calling `suggest_outfit` or `create_fit_card`. In the Gradio UI, the error message appears in the first panel and the other two panels remain empty.

---

## Spec Reflection

**One way the spec helped:** Defining the planning loop's conditional logic in `planning.md` before writing any code made it straightforward to implement `run_agent()` — the branching conditions were already worked out, so implementation was mostly translating the spec into Python.

**One way implementation diverged from the spec:** The spec didn't address query parsing — how to extract `description`, `size`, and `max_price` from a natural language query. In implementation, regex was used to extract price and size, and the remaining text was used as the description after stripping common filler words. This wasn't planned in advance and could be improved with LLM-based parsing for more complex queries.

---

## AI Usage

**Instance 1 — `suggest_outfit` implementation:**
I gave Claude the Tool 2 spec from `planning.md` (inputs, return value, failure mode) and asked it to implement the function using Groq's `llama-3.3-70b-versatile`. The generated code handled the empty wardrobe case correctly. I reviewed the prompt structure and adjusted the wording to make outfit suggestions more specific to the wardrobe items rather than generic advice.

**Instance 2 — `run_agent` planning loop:**
I gave Claude the Architecture diagram and the Planning Loop + State Management sections from `planning.md` and asked it to implement `run_agent()` in `agent.py`. The generated code correctly branched on `search_listings` results and stored values in the session dict. I added the `compare_price` call and `price_comparison` key to the session, which wasn't in the original generated code, to match the full spec.