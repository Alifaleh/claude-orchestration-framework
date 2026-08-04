---
paths: ["**/*.ts", "**/*.tsx", "**/*.astro"]
---

# TypeScript / Frontend

- Strict TypeScript: never silence errors with `any`, `as unknown as`, or `@ts-ignore`. If suppression is unavoidable, use `@ts-expect-error` with a reason.
- Types are erased at runtime: validate external data (API responses, env vars, form input) at the boundary before trusting it.
- Next.js App Router: Server Components by default; add `"use client"` only where interactivity requires it.
- Type gate before done: `npx tsc --noEmit` plus the project's lint command must pass. UI behavior is verified with Playwright MCP per global rules.
