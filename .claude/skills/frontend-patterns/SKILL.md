---
name: frontend-patterns
description: Angular component architecture, state management, reactive patterns, and UI best practices. Use when the user asks about Angular components, services, RxJS, routing, or frontend architecture.
---

# Frontend Patterns Skill (Angular)

## Component Architecture

### Component Types
| Type | Responsibility | Example |
|------|---------------|---------|
| Smart (Container) | Manages state, calls services | `ReportPageComponent` |
| Dumb (Presentational) | Renders UI, emits events | `ReportCardComponent` |
| Layout | Page structure, routing outlet | `MainLayoutComponent` |
| Utility | Reusable UI element | `LoadingSpinnerComponent` |

### Smart vs Dumb Pattern
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

// Dumb component - pure input/output
@Component({
  selector: 'app-report-list',
  template: `...`,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ReportListComponent {
  @Input({ required: true }) reports: Report[] = [];
  @Input() loading = false;
  @Output() reportSelected = new EventEmitter<Report>();
}
```

## State Management

### Signal-based State (Angular 16+)
```typescript
@Injectable({ providedIn: 'root' })
export class ReportStore {
  // State
  private _reports = signal<Report[]>([]);
  private _loading = signal(false);
  private _error = signal<string | null>(null);

  // Public read-only
  reports = this._reports.asReadonly();
  loading = this._loading.asReadonly();
  error = this._error.asReadonly();

  // Computed
  publishedReports = computed(() => 
    this._reports().filter(r => r.status === 'published')
  );

  // Actions
  async loadReports(): Promise<void> {
    this._loading.set(true);
    this._error.set(null);
    try {
      const data = await firstValueFrom(this.http.get<Report[]>('/api/reports'));
      this._reports.set(data);
    } catch (e) {
      this._error.set('Failed to load reports');
    } finally {
      this._loading.set(false);
    }
  }
}
```

### When to use what
| Pattern | Use when |
|---------|----------|
| Component state (signal) | Local UI state only |
| Service with signals | Shared state between components |
| NgRx/Store | Complex state with many actions and side effects |

## Reactive Patterns (RxJS)

### Common Operators
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

### Subscription Management
```typescript
// Prefer async pipe in templates
@Component({
  template: `
    @if (data$ | async; as data) {
      <app-list [items]="data"></app-list>
    }
  `
})

// Or use takeUntilDestroyed for imperative subscriptions
export class MyComponent {
  private destroyRef = inject(DestroyRef);
  
  ngOnInit() {
    this.dataService.data$.pipe(
      takeUntilDestroyed(this.destroyRef)
    ).subscribe(data => this.process(data));
  }
}
```

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

## Performance Patterns
- Use `OnPush` change detection on presentational components
- Lazy load feature modules/routes
- Use `trackBy` in `@for` loops
- Avoid complex computations in templates - use `computed()`
- Use virtual scrolling for long lists (`@angular/cdk`)

## Testing Patterns
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
