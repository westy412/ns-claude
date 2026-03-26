# Layout Pattern Transformations

> Detailed before/after transformations for the 6 recurring layout patterns (patterns 1, 2, 4, 5, 6, 7). Pattern 3 (tables) has its own reference file.

---

## Pattern 1: Two-Column Side-by-Side Layouts

Desktop shows two columns. Mobile stacks vertically.

### Flex Layout

```tsx
// BEFORE (desktop-only)
<div className="flex items-start gap-6">
  <div className="w-72 shrink-0">Sidebar</div>
  <div className="flex-1">Main</div>
</div>

// AFTER (responsive)
<div className="flex flex-col md:flex-row items-start gap-4 md:gap-6">
  <div className="w-full md:w-72 md:shrink-0">Sidebar</div>
  <div className="flex-1">Main</div>
</div>
```

### Grid Layout (grid-cols-12)

This pattern appears in Post Detail tabs (ContentTab, InfographicTab, CarouselTab, ImagesTab). See `post-detail.md` for the specific transformation.

```tsx
// BEFORE
<div className="grid grid-cols-12 gap-6">
  <div className="col-span-2">Timeline</div>
  <div className="col-span-6">Editor</div>
  <div className="col-span-4">Feedback</div>
</div>

// AFTER
<div className="grid grid-cols-1 md:grid-cols-12 gap-4 md:gap-6">
  <div className="md:col-span-2">Timeline (mobile: horizontal strip or dropdown)</div>
  <div className="md:col-span-6">Editor (mobile: full width)</div>
  <div className="md:col-span-4">Feedback (mobile: expandable section)</div>
</div>
```

### Authenticated Layout Shell

Already handled in Phase 1 foundation. Desktop sidebar + main stays. Mobile gets full-width main with drawer navigation.

---

## Pattern 2: Fixed-Width Select Triggers

Any element with a hardcoded pixel width becomes full-width on mobile.

```tsx
// BEFORE
<SelectTrigger className="w-[180px]">

// AFTER
<SelectTrigger className="w-full md:w-[180px]">
```

### Known Instances

| Component | Current | Mobile |
|-----------|---------|--------|
| EntitySelector | `w-[180px]` | `w-full md:w-[180px]` |
| PeriodSelector | `w-[160px]` | `w-full md:w-[160px]` |
| CampaignToolbar group | `w-[160px]` | `w-full md:w-[160px]` |
| CampaignToolbar sort | `w-[180px]` | `w-full md:w-[180px]` |
| SearchInput | `w-64` | `w-full md:w-64` |
| Analytics entity filter | `w-[180px]` | `w-full md:w-[180px]` |
| Analytics date range | `w-[260px]` | `w-full md:w-[260px]` |
| Settings entity selectors | `w-64` | `w-full md:w-64` |

**Note:** Some of these (EntitySelector, PeriodSelector, SearchInput) are fixed in Phase 1 at the component level. Others need fixing at the usage site.

---

## Pattern 4: Toolbars with Multiple Inline Controls

Desktop shows all controls in a single row. Mobile stacks them.

```tsx
// BEFORE
<div className="flex items-center gap-3 px-6 py-3">
  <PeriodSelector />
  <FilterDropdown />
  <SearchInput className="w-64" />
  <ViewToggle />
</div>

// AFTER
<div className="flex flex-col md:flex-row md:items-center gap-3 px-3 md:px-6 py-3">
  <SearchInput className="w-full md:w-64" />
  <div className="flex items-center gap-3">
    <PeriodSelector />
    <FilterDropdown />
    <ViewToggle />
  </div>
</div>
```

**Rules:**
- Search goes full-width on its own row on mobile
- Filter/sort/view controls group together on a second row
- ViewToggle hides kanban option on mobile (if applicable)
- Reduce horizontal padding: `px-3 md:px-6`

---

## Pattern 5: Kanban Boards

Kanban columns (`w-72 min-w-72`) don't fit on mobile. Hide the entire board.

```tsx
// BEFORE
<KanbanBoard posts={posts} />

// AFTER
<div className="hidden md:block">
  <KanbanBoard posts={posts} />
</div>
```

**Also required:**
- ViewToggle should hide the kanban option on mobile
- Default view should be list on mobile
- Applies to: `KanbanBoard`, `CampaignKanbanBoard`, `CampaignPostKanbanBoard`

**Implementation approach:** The ViewToggle component likely controls which view renders. On mobile, either:
1. Filter out the kanban option from ViewToggle
2. Or wrap the kanban in `hidden md:block` and ensure list view renders by default

Prefer option 2 (simpler, no component modification needed).

---

## Pattern 6: Generous Padding

Reduce padding on mobile. Desktop keeps current values.

| Element | Current | Mobile |
|---------|---------|--------|
| PageHeader | `px-6` | `px-3 md:px-6` |
| Content area | `p-6` | `p-4 md:p-6` |
| Toolbar | `px-6 py-3` | `px-3 md:px-6 py-3` |
| Cards | `p-5` or `p-6` | `p-4 md:p-5` or `p-4 md:p-6` |
| Settings cards | `p-6` | `p-4 md:p-6` |

**Note:** PageHeader padding is fixed in Phase 1 at the component level. Content area and toolbar padding must be fixed per-page.

---

## Pattern 7: Card Header Action Rows

Desktop shows title + actions in a single row. Mobile stacks them.

```tsx
// BEFORE
<div className="flex items-center justify-between">
  <div className="flex items-center gap-2">
    <Icon />
    <h3>Title</h3>
  </div>
  <div className="flex items-center gap-2">
    <Button>Action 1</Button>
    <Button>Action 2</Button>
    <Button>Action 3</Button>
  </div>
</div>

// AFTER
<div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
  <div className="flex items-center gap-2">
    <Icon />
    <h3>Title</h3>
  </div>
  <div className="flex items-center gap-2">
    <Button>Action 1</Button>
    <Button>Action 2</Button>
    <Button>Action 3</Button>
  </div>
</div>
```

**If too many actions (4+):** Consider collapsing into a DropdownMenu overflow on mobile:

```tsx
<div className="flex items-center gap-2">
  <Button className="md:hidden">
    <MoreHorizontal />
  </Button>
  <div className="hidden md:flex items-center gap-2">
    <Button>Action 1</Button>
    <Button>Action 2</Button>
    <Button>Action 3</Button>
  </div>
</div>
```
