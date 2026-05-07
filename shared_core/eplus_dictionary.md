# E+ Dictionary — Complete Reference

> A cognitively-aligned, conversational programming language where code reads like a thought written down.

---

## Foundation

E+ v4 is a **cognitively-aligned conversational programming language** that mirrors how humans think (like speech) while remaining stable and executable (like writing).

**Core realization:** Humans do not think in full structured sentences, nor in symbolic syntax. They think in *incremental meaning chunks* — and when they write, they refine and structure those chunks. E+ v4 bridges this gap.

---

## Core Model — Speech → Writing Hybrid

E+ operates on two simultaneous layers:

| Layer | Character | Properties |
|---|---|---|
| **Cognitive (Speech-like)** | Incremental | One thought at a time, 1–3 entities, context-driven |
| **Structural (Writing-like)** | Persistent | Readable, executable, slightly more organized |

> The language must *feel* like thinking out loud, but *behave* like structured code.

---

## Non-Negotiable Rules

Every valid E+ program must follow these constraints:

1. **One line equals one cognitive step.**
2. **Each line involves at most 3 entities** (agent, action, target).
3. **No compressed multi-intent logic in a single line.**
4. **Flow must feel continuous** — like explaining something step by step.
5. **Symbols must not feel mechanical or repetitive**; words are preferred when clearer.

> **Design Test:** Any new feature must answer yes to: *"Does this feel like something a human would naturally say while explaining their reasoning?"*

---

## The E+ Dictionary

Intentionally minimal and semantically meaningful. Every element reflects how humans naturally express intent.

---

### 1. Entity Declaration — `@` (optional)

**Symbol:** `@`

**Purpose:** Marks a named entity. Optional in relaxed mode.

**Syntax:**
```
@user = < "Your name"
user = < "Your name"    ## both are valid
```

**Use Case:** Use `@` to emphasize that you're declaring a new entity in your mental model. It's optional but can make code more explicit about entity introduction.

**Mental Model:** *"I'm introducing a new thing into my world."*

---

### 2. Input — `<`

**Symbol:** `<`

**Purpose:** Receives something from outside the program.

**Syntax:**
```
age = < "Your age"
name = < "Enter your name"
```

**Use Case:** When you need to get data from the user or external source. Always paired with a prompt string.

**Mental Model:** *"I ask and receive."*

---

### 3. Output — `>`

**Symbol:** `>`

**Purpose:** Expresses or shows something.

**Syntax:**
```
> "Hello, world"
> result
> "Total: " + total
```

**Use Case:** Display information to the user. Can output strings, variables, or expressions.

**Mental Model:** *"I express or reveal something."*

---

### 4. Decision — `?`

**Symbol:** `?`

**Purpose:** Represents a question in thought. Mirrors internal reasoning: *"Is this true?"*

**Syntax:**
```
? (age > 17) →
    > "Allowed"

? (isValid) →
    > proceed()
```

**Use Case:** Conditional branching. Use when you need to check a condition and execute code only if it's true. Must be followed by a flow block (`→`).

**Mental Model:** *"I wonder if this is true... let me check."*

**Cognitive Rule:** Keep conditions simple. Avoid more than 2 logical operators (`and`, `or`) in a single condition.

---

### 5. Else — `else`

**Symbol:** `else` (keyword)

**Purpose:** Natural continuation after a condition. Provides fallback behavior when a condition is false.

**Syntax:**
```
? (age > 17) →
    > "Allowed"
else →
    > "Denied"
```

**Use Case:** Must semantically follow a condition block. Provides the alternative path when the `?` condition evaluates to false.

**Mental Model:** *"If not that, then this."*

---

### 6. Flow Block — `→`

**Symbol:** `→`

**Purpose:** Signals the continuation of thought into an indented block. Replaces braces and explicit indentation rules.

**Syntax:**
```
? (x) →
    > "yes"
    > "confirmed"

repeat item in list →
    > item
```

**Use Case:** Opens a block of code that belongs together. Used after `?`, `repeat`, and function definitions. All statements in the block must be indented.

**Mental Model:** *"This leads to..." or "...and then I do this:"*

---

### 7. Repeat — `repeat`

**Symbol:** `repeat` (keyword)

**Purpose:** Iteration in natural language.

**Syntax:**
```
## Iterate over a collection
repeat item in list →
    > item

## Infinite loop
repeat forever →
    > "running"
```

**Use Case:** 
- `repeat var in iterable` — Loop through each item in a collection
- `repeat forever` — Continuous loop (use for monitors, servers, etc.)

**Mental Model:** *"For each thing in this group, I do..." or *"Keep doing this forever."*

---

### 8. Function Definition — `[ ]`

**Symbol:** `[ ]`

**Purpose:** Defines a reusable thought or behavior.

**Syntax:**
```
[greet] (name) →
    > "Hello " + name

[calculateArea] (width, height) →
    area = width * height
    return area
```

**Use Case:** Encapsulate reusable logic. Functions can take parameters (max 3 recommended for cognitive clarity) and optionally return values.

**Mental Model:** *"Here's a thing I can do..." or *"This is a capability I have."*

**Cognitive Rule:** Keep function parameters to 3 or fewer. If you need more, consider grouping them into a single object.

---

### 9. Function Call — `call` or `^`

**Symbols:** `call` (keyword) or `^`

**Purpose:** Invokes a defined function. Two modes — readable and compact.

**Syntax:**
```
## Readable form
call greet("John")
call calculateArea(10, 20)

## Compact form
^greet("John")
^calculateArea(10, 20)
```

**Use Case:** Execute a function. Both forms are valid; use `call` for clarity, `^` for brevity.

**Mental Model:** *"I invoke this capability"* or *"Do this thing."*

**Cognitive Rule:** Limit function arguments to 3 or fewer for readability.

---

### 10. Return — `return` or `=>`

**Symbols:** `return` (keyword) or `=>`

**Purpose:** Emits a value from a function block.

**Syntax:**
```
## Readable form (preferred)
return result
return x + y

## Compact form
=> result
=> x + y
```

**Use Case:** Exit a function and optionally provide a value back to the caller. Use inside function definitions.

**Mental Model:** *"I give back this result"* or *"This is what I produce."*

---

### 11. Assignment — `=`

**Symbol:** `=`

**Purpose:** Standard assignment. Already intuitive across all programming contexts.

**Syntax:**
```
allowed = false
count = 0
name = "Alice"
total = price * quantity
```

**Use Case:** Store a value in a named variable. Can assign literals, expressions, or results from input/function calls.

**Mental Model:** *"I name this value"* or *"This thing is now called..."*

---

### 12. Remove — `remove` or `~~`

**Symbols:** `remove` (keyword) or `~~`

**Purpose:** Deletes a named value.

**Syntax:**
```
## Readable form (preferred)
remove temp
remove cache

## Compact form
~~temp
~~cache
```

**Use Case:** Clean up variables that are no longer needed. Useful for memory management or resetting state.

**Mental Model:** *"I discard this"* or *"This is no longer relevant."*

---

### 13. Comment — `##`

**Symbol:** `##`

**Purpose:** Human-readable annotation. Never affects execution.

**Syntax:**
```
## checking user eligibility
## This function calculates the total price
## TODO: add error handling
```

**Use Case:** Explain intent, add notes, or temporarily disable code. Comments are for humans only and are stripped during transpilation.

**Mental Model:** *"I'm noting this for myself or others."*

---

### 14. System Call — `sys`

**Symbol:** `sys` (keyword)

**Purpose:** Passes a native expression directly to the target language runtime. Enables OS-level operations without breaking E+'s cognitive model.

**Syntax:**
```
## Assign result to variable
ram = sys "psutil.virtual_memory().percent"
currentTime = sys "datetime.now()"

## Execute without capturing result
sys "os.system('clear')"
sys "print('Direct output')"
```

**Use Case:** Access native system capabilities (file I/O, network, process control, hardware monitoring) that aren't part of E+'s core abstractions. Use sparingly — only when E+'s built-in constructs aren't sufficient.

**Mental Model:** *"I reach into the underlying system to do this specific thing."*

**Examples:**

```
## Monitor RAM usage
ram = sys "psutil.virtual_memory().percent"

## Kill a process
sys "os.system('kill -9 $(pgrep heavy_process)')"

## Get current timestamp
now = sys "time.time()"
```

---

## Cognitive Flow Examples

### Example 1 — Natural Decision Flow

```
## check if user is of legal age
age = < "Age"
allowed = false
? (age > 17) →
    allowed = true
? (allowed) →
    > "Allowed"
else →
    > "Denied"
```

**What this demonstrates:** Sequential thinking, conditional branching, and natural fallback with `else`.

---

### Example 2 — Loop as Thought Sequence

```
repeat item in list →
    valid = check item
    ? (valid) →
        > item
```

**What this demonstrates:** Iteration combined with conditional filtering — processing items one at a time.

---

### Example 3 — Function as Reusable Thought

```
[add] (a, b) →
    result = a + b
    return result

sum = call add(10, 20)
> sum
```

**What this demonstrates:** Encapsulation of logic, parameter passing, and return values.

---

### Example 4 — System Monitor (RAM)

```
## monitor RAM continuously
repeat forever →
    ram = sys "psutil.virtual_memory().percent"
    ? (ram > 80) →
        sys "os.system('kill -9 $(pgrep heavy_process)')"
        > "Process killed"
```

**What this demonstrates:** Infinite loops, system integration, and real-world operational logic.

---

## Quick Reference Table

| Construct | Symbol/Keyword | Purpose | Example |
|---|---|---|---|
| Entity Declaration | `@` (optional) | Mark a named entity | `@user = < "Name"` |
| Input | `<` | Receive external data | `age = < "Your age"` |
| Output | `>` | Display information | `> "Hello"` |
| Decision | `?` | Conditional check | `? (age > 17) →` |
| Else | `else` | Fallback after condition | `else →` |
| Flow Block | `→` | Open indented block | `? (x) →` |
| Repeat | `repeat` | Iteration | `repeat item in list →` |
| Infinite Loop | `repeat forever` | Continuous execution | `repeat forever →` |
| Function Definition | `[ ]` | Define reusable logic | `[greet] (name) →` |
| Function Call | `call` or `^` | Invoke function | `call greet("John")` |
| Return | `return` or `=>` | Emit from function | `return result` |
| Assignment | `=` | Store value | `count = 0` |
| Remove | `remove` or `~~` | Delete variable | `remove temp` |
| Comment | `##` | Annotation | `## note` |
| System Call | `sys` | Native operation | `ram = sys "psutil...` |

---

## Design Philosophy Summary

E+ is built on a single principle: **code should read like a thought written down**.

- **Minimal symbols:** Only use symbols when they enhance clarity (`?` for questions, `→` for flow).
- **Natural keywords:** Prefer words like `repeat`, `else`, `return` over cryptic symbols.
- **One thought per line:** Each statement represents a single cognitive step.
- **Three-entity limit:** No more than agent, action, and target in one line.
- **Continuous flow:** Code should feel like explaining something step by step.

> **The Ultimate Test:** Before adding or using any construct, ask:
>
> *"Does this feel like something a human would naturally say while explaining their reasoning?"*
>
> If yes — it belongs in E+. If no — reconsider.

---

*E+ v4 — a cognitive programming layer that sits above real languages, guiding how humans think before they execute. Not a replacement. An interface evolution.*
