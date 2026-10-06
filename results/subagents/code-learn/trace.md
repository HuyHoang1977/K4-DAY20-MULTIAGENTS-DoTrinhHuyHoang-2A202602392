### Human
The test suite of the `inventory` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: task
{"subagent_type": "explorer", "description": "Explore the workspace repository to understand the project structure, locate the inventory package and test files, and inspect their content."}

### Tool result
I have explored the repository and inspected the project structure, inventory package, and test files. Here are the concrete facts and findings:

### 1. Project Structure & Files
- **Workspace Root**: `workspace/`
- **Files**:
  - `workspace/CHANGELOG.md`
  - `workspace/README.md`
  - `workspace/inventory/__init__.py` (empty file)
  - `workspace/inventory/export.py`
  - `workspace/inventory/pricing.py`
  - `workspace/inventory/report.py`
  - `workspace/tests/test_report.py`

### 2. Module Contents & Code Snippets

#### `workspace/inventory/pricing.py`
```python
"""Price utilities for the inventory package."""
from decimal import Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "")
    return Decimal(cleaned)


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"))
```

#### `workspace/inventory/export.py`
```python
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: n

### Tool call: task
{"description": "Run pytest using the shell tool inside workspace/ to confirm the test failure details and see if there are any other test failures or configuration issues.", "subagent_type": "general-purpose"}

### Tool result
We ran `pytest` using the shell tool inside `workspace/` (with pythonpath configured to `workspace`) and discovered and resolved the test failures and configuration issues:

### 1. Test Discovery & Configuration Issues
* **Import Error / ModuleNotFoundError:** Running `pytest workspace/` directly failed during collection because `workspace/` is not automatically added to `sys.path` by pytest unless specified. Running with `python -m pytest -o pythonpath=workspace` successfully resolves imports from `inventory`.

### 2. Initial Test Failures (`workspace/tests/test_report.py`)
1. **`test_total_value_thousands_separator` Failed:** 
   * **Cause:** `parse_price` in `inventory/pricing.py` did not strip out thousands separator commas (e.g., `"$1,299.50"`), resulting in a `Decimal.InvalidOperation` exception.
   * **Fix:** Updated `parse_price` to remove commas. Also added support for accounting style negative prices in parentheses (e.g., `"(12.00)"`).
2. **`test_discount_rounding_half_up` Failed:** 
   * **Cause:** `apply_discount` used default decimal rounding (which is round-to-even) instead of the commercial round-half-up rule (`ROUND_HALF_UP`), and didn't guard against float/int percentage representations correctly.
   * **Fix:** Updated `apply_discount` to use `rounding=ROUND_HALF_UP` with `Decimal("0.01")`.

### 3. Additional Logic Checks & Enhancements
* **`low_stock` Threshold & Sorting:** Fixed `low_stock` to strictly use `< threshold` instead of `<= threshold` as per docs

### Tool call: task
{"subagent_type": "general-purpose", "description": "Run pytest and examine git diff or status in workspace using execute to ensure all tests pass and no unwanted changes were made."}

### Tool result
I have executed `pytest` specifying the `pythonpath=workspace` (so that Python can correctly locate the `inventory` package inside the workspace directory), and all tests passed successfully (8 passed). 

Additionally, I checked git status/repositories across the environment, and found that this workspace is not initialized as a git repository (no `.git` directory exists), meaning there are no git changes or modifications present.

### Tool call: read_file
{"file_path": "workspace/inventory/pricing.py"}

### Tool result
@@ lines 1-32 of 32 @@
"""Price utilities for the inventory package."""
from decimal import Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    text = text.strip()
    is_negative = False
    if text.startswith("(") and text.endswith(")"):
        is_negative = True
        text = text[1:-1].strip()
    cleaned = text.replace("$", "").replace(",", "")
    val = Decimal(cleaned)
    return -val if is_negative else val


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    from decimal import ROUND_HALF_UP
    discounted = price * (100 - Decimal(str(percent))) / 100
    return discounted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

### Tool call: read_file
{"file_path": "workspace/inventory/export.py"}

### Tool result
@@ lines 1-15 of 15 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    price = parse_price(item["price"])
    name = item["name"]
    if "," in name or '"' in name:
        name = '"' + name.replace('"', '""') + '"'
    return f'{name},{price:.2f},{item["qty"]}'

### Tool call: read_file
{"file_path": "workspace/inventory/report.py"}

### Tool result
@@ lines 1-26 of 26 @@
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    names = [item["name"] for item in items if item["qty"] < threshold]
    return sorted(names, key=lambda s: s.lower())

### Tool call: task
{"description": "Run pytest via execute tool to verify that all tests pass.", "subagent_type": "general-purpose"}

### Tool result
I ran pytest on the workspace by setting the Python path (`python -m pytest workspace -o pythonpath=workspace`), and all 8 tests passed successfully:

```
============================== 8 passed in 0.01s ==============================
```

### Assistant
[{'type': 'text', 'text': 'I have fixed the source code of the `inventory` package so that all unit tests pass and every function strictly conforms to its docstring specification.\n\n### Summary of Changes\n\n1. **`workspace/inventory/pricing.py`**:\n   - Updated `parse_price(text)` to remove thousands separator commas (`","`) and dollar signs (`"$"`), and added support for accounting-style negative numbers enclosed in parentheses (e.g., `"(12.00)"` -> `Decimal("-12.00")`).\n   - Updated `apply_discount(price, percent)` to use explicit commercial rounding (`ROUND_HALF_UP`) when quantizing to 2 decimal places and ensure safe decimal arithmetic with percentage values.\n\n2. **`workspace/inventory/export.py`**:\n   - Updated `to_csv_row(item)` to strictly follow RFC 4180: item names containing commas or double quotes are enclosed in double quotes, and internal double quotes are escaped by doubling them.\n\n3. **`workspace/inventory/report.py`**:\n   - Updated `low_stock(items, threshold)` to check for strictly below (`<`) the threshold and return item names sorted alphabetically, ignoring case (`key=lambda s: s.lower()`).', 'extras': {'signature': 'EmAKXgFpFH0T0IAPeM+b4O5gA4GjIpLJ8GSieP2ZTkfA9Fc9j6xvLbAgibnIAVCMp4BwyrG9DvSd4QO1Idee3hRN6RFw3+zQP6YNASwD7qDW6OBr9AvkAGF4L2HO5OawthA='}}]