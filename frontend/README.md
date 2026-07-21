# MCP Secret Manager Frontend

Next.js 15 frontend bootstrap for MCP Secret Manager.

## Installation

The recommended workflow is Docker from the repository root:

```bash
make up
```

If Node.js is available locally:

```bash
npm install
```

## Scripts

```bash
npm run dev
npm run build
npm run start
npm run lint
npm run test
npm run typecheck
npm run format
npm run format:check
```

## Architecture

- `app/`: App Router, root layout and minimal home page.
- `providers/`: global ThemeProvider and QueryProvider.
- `components/`: shared UI and future shadcn/ui components.
- `features/`: product features, intentionally empty for this bootstrap.
- `lib/`: frontend infrastructure and generic utilities.
- `lib/api/`: HTTP client, runtime API configuration, response parsing, error normalization and generic HTTP helpers.
- `lib/auth/`: authentication state contracts, session helpers, route protection helpers and extension points.
- `hooks/`: shared non-business hooks.
- `config/`: public non-sensitive frontend configuration.
- `styles/`: Tailwind CSS v4 global foundations.
- `assets/`: public visual assets without sensitive data.
- `types/`: shared frontend types.
- `tests/`: cross-cutting frontend tests.

## Conventions

- Use the `@/*` alias for frontend imports.
- Keep feature-specific code inside `features/`.
- Keep shared components free of business logic.
- Keep providers global, explicit and non-sensitive.
- Use TanStack Query for server state only.
- Use `lib/api/` for backend communication; components must not call `fetch` directly.
- Keep API errors normalized through the shared error hierarchy.
- Use `AuthProvider`, `useAuth`, `AuthGuard` and `GuestGuard` for session-aware UI boundaries.
- Keep authentication based on minimal session state; never store tokens or secrets in browser storage.
- Keep DTOs and feature services inside their future feature boundaries.
- Use React Hook Form and Zod for future forms.

## Start

```bash
npm run dev
```
