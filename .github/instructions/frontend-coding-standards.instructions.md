---
applyTo: ['**/*.ts', '**/*.html', '**/*.scss']
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
