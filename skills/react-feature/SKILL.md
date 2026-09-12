---
name: react-feature
description: Scaffold a React feature slice - query hooks, schema, components, test - matching the project's existing structure.
disable-model-invocation: true
user-invocable: true
argument-hint: "[feature name - what it does]"
---

# React Feature Slice

Requested: **$ARGUMENTS**

## 1. Copy the project, not the template

Read one existing feature first and match it: folder layout, API client, query-key factory,
form library, component primitives, test setup. The `react-patterns` skill describes the
target architecture; this step is about the conventions specific to this codebase.

## 2. Build in this order

**Types and schema** (`features/<name>/schemas.ts`) — one zod schema, mirroring the backend
Pydantic model field for field. Derive the TS type from it with `z.infer`; never maintain
both by hand.

**API layer** (`features/<name>/api/`) — query-key factory plus the hooks:

```ts
export const reportKeys = {
  all: ['reports'] as const,
  list: (filters: ReportFilters) => [...reportKeys.all, 'list', filters] as const,
  detail: (id: string) => [...reportKeys.all, 'detail', id] as const,
};
```

Every hook forwards the `signal` so cancelled queries actually abort. Mutations invalidate
through the factory, never through a hand-written key array.

**Components** (`features/<name>/components/`) — container reads state, presentational
components take props. Handle all three states explicitly: pending, error, empty. An empty
list and a failed request must not render the same thing.

**Route** — lazy-loaded, wrapped in an error boundary.

## 3. Accessibility is part of the scaffold, not a follow-up

- Interactive elements are real `<button>`/`<a>`, never a `div` with `onClick`.
- Every input has an associated `<label>`; errors are announced (`role="alert"`).
- Dialogs, menus and tabs come from the project's Radix primitives — not hand-rolled.
- Nothing conveys meaning by color alone.

## 4. Tests, in the same task

```tsx
test('shows the empty state when the company has no reports', async () => {
  server.use(http.get('/api/reports', () => HttpResponse.json([])));
  render(<ReportList companyId="c1" />, { wrapper: createQueryWrapper() });

  expect(await screen.findByText(/no reports yet/i)).toBeInTheDocument();
});
```

Cover the loading, empty, error and populated states, and the primary user interaction.
Query by role and accessible name; a component that cannot be queried that way is not
accessible yet. Each test gets a fresh `QueryClient` with `retry: false`.

## 5. Finish

Run the focused tests, the linter and `tsc --noEmit`. Report the commands and their output.
State which backend endpoints the feature consumes, so any contract drift shows up in review.
