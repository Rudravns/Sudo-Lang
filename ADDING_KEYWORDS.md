# How to Add a New Keyword to Sudo Code

Follow these 3 steps in order. Each step is in a different file inside the `sudo_lang/` folder.

---

## Step 1 — Register the keyword (`sudo_lang/nodes.py`)

Add the keyword name (uppercase string) to the `KEYWORDS` set:

```python
KEYWORDS = {
    "SET",
    "DISPLAY",
    # ... existing keywords ...
    "PRINT",   # <-- add your new keyword here
}
```

This prevents the parser from treating your keyword as an unknown identifier.

---

## Step 2 — Parse it (`sudo_lang/parser.py`)

### 2a — Add a dispatch branch in `parse_statement()`

Inside the `if / elif` chain, add a new branch that calls your parser method:

```python
elif keyword == "PRINT":
    return self._parse_print(tokens, line)
```

### 2b — Write the parser method

Add a new `_parse_<keyword>()` method to the `Parser` class.
Return a `node(...)` dict that describes what was written on the line.

**Simple (single-line) keyword:**
```python
def _parse_print(self, tokens, line):
    """PRINT expression — prints with a newline prefix."""
    expr = " ".join(tokens[1:])
    return node("PRINT", expr=expr)
```

**Block keyword (has a body that ends with END):**
```python
def _parse_repeat(self, tokens, line):
    """REPEAT n TIMES ... END REPEAT"""
    count_expr = " ".join(tokens[1:-1])   # everything between REPEAT and TIMES
    body, _ = self.parse_block({"END"})
    if not self._at_end():
        self._consume()                    # consume END REPEAT
    return node("REPEAT", count=count_expr, body=body)
```

---

## Step 3 — Execute it (`sudo_lang/interpreter.py`)

Add a new `elif` branch inside `execute()` that handles your node type:

**Simple keyword:**
```python
elif t == "PRINT":
    print("\n" + str(self.eval_expr(stmt["expr"], scope)))
```

**Block keyword:**
```python
elif t == "REPEAT":
    count = int(self.eval_expr(stmt["count"], scope))
    for _ in range(count):
        self.run(stmt["body"], scope)
```

---

## Quick checklist

| # | File | What to do |
|---|------|-----------|
| 1 | `sudo_lang/nodes.py` | Add keyword string to `KEYWORDS` set |
| 2 | `sudo_lang/parser.py` | Add `elif` in `parse_statement()` + write `_parse_<keyword>()` |
| 3 | `sudo_lang/interpreter.py` | Add `elif` in `execute()` to run the new node type |

---

## Example `.sudo` usage (after adding PRINT and REPEAT)

```
REPEAT 3 TIMES
    PRINT "hello"
END REPEAT
```
