---
name: angular-patterns
description: Angular architecture - standalone components, signals, RxJS subscription management, state management, folder structure, and component testing. Use when the user asks about Angular components, services, RxJS, routing, change detection, or frontend architecture in an Angular project.
---

<!-- GENERATED FILE - DO NOT EDIT.
     Source: skills/angular-patterns/SKILL.md
     Regenerate: python scripts/sync_copilot.py -->

# Angular Patterns

Angular 17+. Language-level rules (strict mode, naming, formatting) live in the
`typescript-coding-standards` rule and are already in context — this skill covers
architecture only.

## Component Standards

```typescript
@Component({
  selector: 'app-report-list',
  standalone: true,
  imports: [ReportCardComponent],  // no CommonModule when using @if/@for
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

Member order is fixed: injections → inputs/outputs → state → computed → lifecycle → methods.

### Template Control Flow (Angular 17+)

```html
@if (loading()) {
  <app-spinner />
} @else {
  @for (report of reports(); track report.id) {
    <app-report-card [report]="report" />
  }
}
```

`track` is mandatory in `@for` — without it Angular re-creates every DOM node on each change.

### Selectors

- Element: `app-` prefix, kebab-case → `<app-report-card>`
- Directive: `app` prefix, camelCase → `appHighlight`

## Component Architecture

| Type | Responsibility | Example |
|------|---------------|---------|
| Smart (Container) | Manages state, calls services | `ReportPageComponent` |
| Dumb (Presentational) | Renders UI, emits events | `ReportCardComponent` |
| Layout | Page structure, routing outlet | `MainLayoutComponent` |
| Utility | Reusable UI element | `LoadingSpinnerComponent` |

```typescript
// Smart component - knows about services and state
@Component({
  selector: 'app-report-list-page',
  template: `
    <app-report-list
      [reports]="reports()"
      [loading]="loading()"
      (reportSelected)="onSelect($event)">
    </app-report-list>
  `
})
export class ReportListPageComponent {
  private reportService = inject(ReportService);
  reports = signal<Report[]>([]);
  loading = signal(true);
}
```

A dumb component takes inputs and emits outputs. It never injects a service that talks to
the network — that is the line between the two types.

## Service Pattern

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

## State Management

### Signal store

```typescript
@Injectable({ providedIn: 'root' })
export class ReportStore {
  private _reports = signal<Report[]>([]);
  private _loading = signal(false);
  private _error = signal<string | null>(null);

  // Public read-only projections
  reports = this._reports.asReadonly();
  loading = this._loading.asReadonly();
  error = this._error.asReadonly();

  publishedReports = computed(() =>
    this._reports().filter(r => r.status === 'published')
  );

  async loadReports(): Promise<void> {
    this._loading.set(true);
    this._error.set(null);
    try {
      this._reports.set(await firstValueFrom(this.http.get<Report[]>('/api/reports')));
    } catch {
      this._error.set('Failed to load reports');
    } finally {
      this._loading.set(false);
    }
  }
}
```

Writable signals stay private; expose `asReadonly()` so state changes only through actions.

### Decision matrix

| Scenario | Approach |
|----------|----------|
| Local UI state (toggle, form) | `signal()` in component |
| Shared state (2-3 components) | Service with `signal()` |
| Complex state (many actions, effects) | NgRx Store |
| Server cache (API responses) | Service + signal store |

## Subscription Management

Priority order — pick the first one that fits:

1. `toSignal()` — Observable to Signal, auto-cleans on destroy (preferred for simple reads)
2. `async` pipe in the template — no manual unsubscribe
3. `takeUntilDestroyed(this.destroyRef)` — for imperative subscriptions

```typescript
export class MyComponent {
  private destroyRef = inject(DestroyRef);

  ngOnInit() {
    this.dataService.data$
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(data => this.process(data));
  }
}
```

A `.subscribe()` without one of these three is a memory leak. Treat it as a review blocker.

## RxJS Operators

```typescript
// HTTP with error handling
this.http.get<Report[]>('/api/reports').pipe(
  retry(2),
  catchError(err => {
    this.errorService.handle(err);
    return of([]);
  })
);

// Search with debounce
this.searchControl.valueChanges.pipe(
  debounceTime(300),
  distinctUntilChanged(),
  switchMap(term => this.searchService.search(term))
);

// Combine latest data
combineLatest([this.reports$, this.filters$]).pipe(
  map(([reports, filters]) => this.applyFilters(reports, filters))
);
```

Use `switchMap` for cancel-previous semantics (search, navigation), `concatMap` when order
matters, `mergeMap` only when concurrency is genuinely safe.

## Folder Structure

```
feature/
├── feature.component.ts        # Smart/container component
├── feature.component.html
├── feature.component.scss
├── feature.routes.ts           # Lazy-loaded routes
├── components/                 # Dumb components
│   ├── feature-list/
│   └── feature-card/
├── services/                   # Feature-specific services
│   └── feature.service.ts
├── models/                     # Interfaces and types
│   └── feature.model.ts
└── pipes/                      # Feature-specific pipes
```

## HTTP Error Handling

The API error contract itself is defined by the `error-handling-patterns` rule and the
project's ADR; this section only covers the Angular side.

### HTTP Error Interceptor

- 401: call `AuthService.logout()` + navigate to `/login`
- 403: show permission denied notification
- 0 (network error): show connection error notification
- All others: `throwError(() => error)` - handled at component level

### Component Error State

Use `LoadState<T>` discriminated union: `idle | loading | success | error`. Store in
`signal<LoadState<T>>()`. Read the machine-readable `code` from the error body; use the
human-readable `detail`/`message` only as a fallback, with a generic default such as
`'An unexpected error occurred'`.

## Performance

- `OnPush` change detection on presentational components
- Lazy load feature routes
- `track` in every `@for`
- No complex expressions in templates — use `computed()`
- Virtual scrolling for long lists (`@angular/cdk`)

## Testing

```typescript
describe('ReportListComponent', () => {
  it('should emit reportSelected when card is clicked', () => {
    const fixture = TestBed.createComponent(ReportListComponent);
    const component = fixture.componentInstance;
    const spy = jest.spyOn(component.reportSelected, 'emit');

    component.reports = [mockReport];
    fixture.detectChanges();

    const card = fixture.debugElement.query(By.css('.report-card'));
    card.triggerEventHandler('click', null);

    expect(spy).toHaveBeenCalledWith(mockReport);
  });
});
```

Assert on rendered output and emitted events, never on private fields.
