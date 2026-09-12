---
name: react-patterns
description: React 19 architecture - component and hook design, TanStack Query server state, react-hook-form + zod forms, Radix UI primitives, Tailwind styling, and Testing Library patterns. Use when the user asks about React components, hooks, data fetching, forms, or frontend architecture in a React project.
---

<!-- GENERATED FILE - DO NOT EDIT.
     Source: skills/react-patterns/SKILL.md
     Regenerate: python scripts/sync_copilot.py -->

# React Patterns

React 19 + Vite. Language-level rules (strict mode, naming, formatting) live in the
`typescript-coding-standards` rule and are already in context — this skill covers
architecture only.

## Component Standards

```tsx
interface ReportListProps {
  companyId: string;
  onReportSelect: (report: Report) => void;
}

export function ReportList({ companyId, onReportSelect }: ReportListProps) {
  const { data: reports, isPending, error } = useReports(companyId);

  if (isPending) return <Spinner />;
  if (error) return <ErrorState error={error} />;

  return (
    <ul>
      {reports.map(report => (
        <ReportCard key={report.id} report={report} onSelect={onReportSelect} />
      ))}
    </ul>
  );
}
```

Rules that hold without exception:

- Function components only. No class components in new code.
- Do not annotate the return type as `JSX.Element` — let it infer; React 19 components may
  return strings, arrays, or `null`.
- `key` must be a stable domain id. Never an array index for a list that can reorder.
- Props interface is named `<Component>Props` and lives next to the component.

## Separate Server State From Client State

This is the single most important architectural decision in a React app.

| State kind | Owner | Never use |
|------------|-------|-----------|
| Server data (API responses) | TanStack Query | `useState` + `useEffect` fetching |
| URL-derived state (filters, page) | Router search params | duplicated `useState` |
| Form state | `react-hook-form` | per-field `useState` |
| Ephemeral UI (open/closed, hover) | `useState` | global store |
| Cross-cutting client state (theme, auth user) | Context, sparingly | prop drilling |

Fetching in `useEffect` and mirroring the result in `useState` re-implements caching,
deduplication, retry, and cancellation badly. Use the query library.

### TanStack Query

```tsx
// api/reports.ts — query keys are a typed, centralized contract
export const reportKeys = {
  all: ['reports'] as const,
  byCompany: (companyId: string) => [...reportKeys.all, 'company', companyId] as const,
  detail: (id: string) => [...reportKeys.all, 'detail', id] as const,
};

export function useReports(companyId: string) {
  return useQuery({
    queryKey: reportKeys.byCompany(companyId),
    queryFn: ({ signal }) => api.get<Report[]>('/reports', {
      params: { company_id: companyId },
      signal,
    }).then(r => r.data),
    staleTime: 30_000,
  });
}

export function useCreateReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ReportCreate) =>
      api.post<Report>('/reports', payload).then(r => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reportKeys.all });
    },
  });
}
```

- Always build query keys through a `*Keys` factory. Hand-written key arrays drift and
  silently break invalidation.
- Always forward the `signal` to the HTTP client so cancelled queries abort in flight.
- Invalidate on mutation success; only reach for optimistic updates when the latency is
  actually visible to the user.

## Custom Hooks

Extract a hook when logic is stateful **and** reused, or when a component's body no longer
fits on one screen. A hook that is called exactly once and never will be again is usually
better left inline.

```tsx
export function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);

  return debounced;
}
```

Every effect that starts something must return a cleanup that stops it — timers,
subscriptions, `AbortController`. Effects run twice in React StrictMode development;
a missing cleanup shows up as a duplicate request or a doubled listener.

### When `useEffect` is the wrong tool

| You want to | Do this instead |
|-------------|-----------------|
| Fetch data | TanStack Query |
| Derive a value from props/state | Compute during render |
| Reset state when a prop changes | `key` prop on the component |
| Respond to a user action | Handler function, not an effect |

## Forms: react-hook-form + zod

```tsx
const reportSchema = z.object({
  title: z.string().min(1).max(200),
  year: z.number().int().min(2020).max(2030),
});

type ReportForm = z.infer<typeof reportSchema>;

export function ReportForm({ onSubmit }: { onSubmit: (data: ReportForm) => void }) {
  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm<ReportForm>({ resolver: zodResolver(reportSchema) });

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <input {...register('title')} aria-invalid={!!errors.title} />
      {errors.title && <p role="alert">{errors.title.message}</p>}
      <button type="submit" disabled={isSubmitting}>Save</button>
    </form>
  );
}
```

The zod schema is the single source of truth: it types the form, validates it, and should
mirror the backend Pydantic schema field for field. When they disagree, the backend wins.

## Radix UI + Tailwind

Radix primitives supply behavior and accessibility; Tailwind supplies appearance. Do not
re-implement a dialog, dropdown, popover, or tabs by hand — focus trapping, escape handling,
and ARIA wiring are exactly what gets silently broken.

```tsx
<Dialog.Root open={open} onOpenChange={setOpen}>
  <Dialog.Portal>
    <Dialog.Overlay className="fixed inset-0 bg-black/50" />
    <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2
                               rounded-lg bg-white p-6 shadow-lg">
      <Dialog.Title className="text-lg font-semibold">Edit report</Dialog.Title>
      {children}
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

- Every `Dialog.Content` needs a `Dialog.Title` — Radix warns and screen readers lose the label without it.
- Conditional class names go through a `cn()` helper (`clsx` + `tailwind-merge`), never through
  string concatenation, so later utilities actually override earlier ones.

## Folder Structure

```
src/
├── features/
│   └── reports/
│       ├── components/          # Feature-local components
│       ├── api/                 # Query hooks + key factory
│       ├── schemas/             # zod schemas
│       └── types.ts
├── components/ui/               # Shared primitives (Radix wrappers)
├── hooks/                       # Cross-feature hooks
├── lib/                         # api client, cn(), formatters
└── routes/                      # Route components
```

Organize by feature, not by file type. A `components/` folder holding 80 unrelated
components is the failure mode this avoids.

## Performance

Measure before optimizing — the React Compiler and cheap re-renders make most manual
memoization dead weight.

- `React.memo` only after profiling shows a costly re-render.
- `useMemo` for genuinely expensive computation, not for object literals.
- `useCallback` only when the callback is a dependency of a memoized child or an effect.
- Split routes with `lazy()` + `<Suspense>`.
- Virtualize lists past a few hundred rows.

## Testing (Testing Library)

```tsx
test('emits selection when a report card is clicked', async () => {
  const onSelect = vi.fn();
  const user = userEvent.setup();

  render(<ReportList companyId="c1" onReportSelect={onSelect} />, {
    wrapper: createQueryWrapper(),
  });

  await user.click(await screen.findByRole('button', { name: /annual report/i }));

  expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({ id: '1' }));
});
```

- Query by role and accessible name. `getByTestId` is a last resort — if you need it, the
  markup is probably not accessible.
- Drive interaction with `userEvent`, not `fireEvent`.
- Wrap components under test in a fresh `QueryClient` per test with retries disabled, so one
  test's cache never leaks into the next.
