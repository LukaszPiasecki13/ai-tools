---
applyTo: "**/*.ts,**/*.html,**/*.scss"
description: "Angular and React coding standards: TypeScript strict mode, ESLint + Prettier, Signals, component patterns. Applied automatically to TS/HTML/SCSS files."
---

# Frontend Coding Standards

Angular and React projects. TypeScript strict mode, ESLint + Prettier.

## Formatting Rules (Prettier)

- Print width: 100 characters
- Quotes: single (`'`) in TS/JS, double in HTML attributes
- Semicolons: yes
- Trailing commas: ES5
- Indent: 2 spaces

## TypeScript Rules (strict mode)

Never use `any`. Use `unknown` + type narrowing instead.

```typescript
function parseResponse(data: unknown): Report {
  if (!isReport(data)) throw new Error('Invalid report data');
  return data;
}

// Unused vars: prefix with underscore
function handler(_event: Event, data: Report): void {
  process(data);
}
```

## Complexity Limits

| Metric | Limit |
|--------|-------|
| Cyclomatic complexity | max 15 |
| Lines per function | max 100 |
| `console.log` | error (only `console.warn`, `console.error` allowed) |

---

## Angular Standards

### Component Pattern (Angular 17+)
```typescript
@Component({
  selector: 'app-report-list',
  standalone: true,
  imports: [ReportCardComponent],  // no CommonModule with @if/@for
  templateUrl: './report-list.component.html',
  styleUrl: './report-list.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReportListComponent {
  // 1. Injections
  private readonly reportService = inject(ReportService);
  private readonly destroyRef = inject(DestroyRef);

  // 2. Inputs/Outputs (function-based - preferred for new code)
  companyId = input.required<string>();
  reportSelected = output<Report>();

  // 3. State (signals preferred)
  protected reports = signal<Report[]>([]);
  protected loading = signal(false);
  protected errorMessage = signal<string | null>(null);

  // 4. Computed values
  protected publishedCount = computed(() =>
    this.reports().filter(r => r.status === 'published').length
  );
}
```

### Template Control Flow (Angular 17+)
```html
<!-- Use @if/@for - no NgIf/NgFor needed -->
@if (loading()) {
  <app-spinner />
} @else {
  @for (report of reports(); track report.id) {
    <app-report-card [report]="report" />
  }
}
```

### Service Pattern
```typescript
@Injectable({ providedIn: 'root' })
export class ReportService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api/v1/reports';

  getByCompany(companyId: string): Observable<Report[]> {
    return this.http.get<Report[]>(this.baseUrl, { params: { company_id: companyId } });
  }
}
```

### Subscription Management (priority order)
1. `toSignal()` - converts Observable to Signal, auto-cleans on destroy (preferred for simple reads)
2. `async` pipe in template - no manual unsubscribe
3. `takeUntilDestroyed(this.destroyRef)` - for imperative code

### State Management Decision Matrix

| Scenario | Approach |
|----------|----------|
| Local UI state (toggle, form) | `signal()` in component |
| Shared state (2-3 components) | Service with `signal()` |
| Complex state (many actions, effects) | NgRx Store |
| Server cache (API responses) | Service + signal store |

### Selectors
- Element: `app-` prefix, kebab-case: `<app-report-card>`
- Directive: `app` prefix, camelCase: `appHighlight`

---

## React Standards

### Component Pattern
```tsx
interface ReportListProps {
  companyId: string;
  onReportSelect: (report: Report) => void;
}

export function ReportList({ companyId, onReportSelect }: ReportListProps): JSX.Element {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    loadReports(companyId, controller.signal);
    return () => controller.abort();
  }, [companyId]);
}
```

### Key Rules
- Function components only (no class components for new code)
- Custom hooks: `use` prefix, extract reusable state logic
- Never use `dangerouslySetInnerHTML` with user content
- Use `DOMPurify` if raw HTML rendering is required

---

## Naming Conventions

### TypeScript (Angular + React)

| Element | Convention | Example |
|---------|-----------|----------|
| File | kebab-case | `report-list.component.ts` |
| Class | PascalCase | `ReportListComponent` |
| Interface | PascalCase (no `I` prefix) | `Report`, `UserProfile` |
| Type alias | PascalCase | `LoadState<T>` |
| Enum | PascalCase | `ReportStatus` |
| Enum values | PascalCase | `ReportStatus.Draft` |
| Function | camelCase | `getReportById()` |
| Variable | camelCase | `reportCount` |
| Constant (module-level) | UPPER_SNAKE | `MAX_RETRIES` |
| Constant (local/function) | camelCase | `defaultConfig` |
| Observable | camelCase + `$` suffix | `reports$`, `loading$` |
| Signal | camelCase (no suffix) | `reports`, `loading` |
| Private member | no underscore (use `private`) | `private readonly service` |

### Angular-Specific

| Element | Convention | Example |
|---------|-----------|----------|
| Component | PascalCase + `Component` | `ReportListComponent` |
| Service | PascalCase + `Service` | `ReportService` |
| Directive | PascalCase + `Directive` | `HighlightDirective` |
| Pipe | PascalCase + `Pipe` | `DateFormatPipe` |
| Guard | PascalCase + `Guard` | `AuthGuard` |
| Interceptor | camelCase + `Interceptor` | `errorInterceptor` (fn) |
| Selector (element) | `app-` + kebab-case | `app-report-card` |
| Selector (directive) | `app` + camelCase | `appTooltip` |

### React-Specific

| Element | Convention | Example |
|---------|-----------|----------|
| Component | PascalCase | `ReportList` |
| Hook | camelCase + `use` prefix | `useReports()` |
| Context | PascalCase + `Context` | `AuthContext` |
| Props interface | PascalCase + `Props` | `ReportListProps` |
| Event handler | `handle` + Event | `handleClick`, `handleSubmit` |
| Event handler prop | `on` + Event | `onClick`, `onSubmit` |

### File Naming

| Type | Convention | Example |
|------|-----------|----------|
| TS/Angular file | kebab-case + suffix | `report-list.component.ts` |
| React component | PascalCase | `ReportList.tsx` |
| React util | camelCase | `useReports.ts` |
| Test file | same name + `.test`/`.spec` | `report.service.spec.ts` |
| Config file | kebab-case | `eslint.config.mjs` |
| Folder | kebab-case | `report-management/` |

### JSON Field Mapping

| Context | Convention | Example |
|---------|-----------|----------|
| Backend JSON field | snake_case | `created_at`, `company_id` |
| Frontend TS property | camelCase | `createdAt`, `companyId` |
