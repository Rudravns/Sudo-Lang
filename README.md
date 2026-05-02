# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.

## Sudo Code Language

A custom programming language interpreter written in Python.

### Files
- `sudo_interpreter.py` — the interpreter (parser + AST + evaluator)
- `example.sudo` — sample program exercising all base keywords
- `sudo-code.tmLanguage.json` — VS Code/Replit syntax-highlighting grammar

### Usage
```bash
python sudo_interpreter.py example.sudo
python sudo_interpreter.py myprogram.sudo
```

### Base Keywords
| Keyword    | Syntax example                         |
|------------|----------------------------------------|
| `SET`      | `SET x <- 5`                           |
| `INPUT`    | `INPUT name "Enter name:"`             |
| `DISPLAY`  | `DISPLAY "Hello"` / `DISPLAY x`        |
| `IF/ELSE`  | `IF x > 0 THEN ... ELSE ... END IF`    |
| `WHILE`    | `WHILE x < 10 DO ... END WHILE`        |
| `FOR`      | `FOR i FROM 1 TO 10 ... END FOR`       |
| `FUNCTION` | `FUNCTION name(a, b) ... END FUNCTION` |
| `RETURN`   | `RETURN value`                         |
| `TRY/ELSE` | `TRY ... EXCEPT error ...`             | 
| `CLEAR_CONSOLE` | `CLEAR_CONSOLE`                   |


### Extending the Language
1. Add the keyword name to the `KEYWORDS` set in `sudo_interpreter.py`
2. Add a parsing branch in `Parser.parse_statement()` (or `parse_block()` for block constructs)
3. Add an execution branch in `Interpreter.execute()`

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
=======
# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.

## Sudo Code Language

A custom programming language interpreter written in Python.

### Files
- `sudo_interpreter.py` — the interpreter (parser + AST + evaluator)
- `example.sudo` — sample program exercising all base keywords
- `sudo-code.tmLanguage.json` — VS Code/Replit syntax-highlighting grammar

### Usage
```bash
python sudo_interpreter.py example.sudo
python sudo_interpreter.py myprogram.sudo
```

### Base Keywords
| Keyword    | Syntax example                         |
|------------|----------------------------------------|
| `SET`      | `SET x <- 5`                           |
| `INPUT`    | `INPUT name "Enter name:"`             |
| `DISPLAY`  | `DISPLAY "Hello"` / `DISPLAY x`        |
| `IF/ELSE`  | `IF x > 0 THEN ... ELSE ... END IF`    |
| `WHILE`    | `WHILE x < 10 DO ... END WHILE`        |
| `FOR`      | `FOR i FROM 1 TO 10 ... END FOR`       |
| `FUNCTION` | `FUNCTION name(a, b) ... END FUNCTION` |
| `RETURN`   | `RETURN value`                         |
| `TRY/ELSE` | `TRY ... EXCEPT error ...`             | 
| `CLEAR_CONSOLE` | `CLEAR_CONSOLE`                   |


### Extending the Language
1. Add the keyword name to the `KEYWORDS` set in `sudo_interpreter.py`
2. Add a parsing branch in `Parser.parse_statement()` (or `parse_block()` for block constructs)
3. Add an execution branch in `Interpreter.execute()`

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
>>>>>>> 6b57c60b73b91e74482c9e44f1a09859fb26185e
