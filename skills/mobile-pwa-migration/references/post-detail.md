# Post Detail Page — Mobile Patterns

> Specific patterns for the hardest page in the app: Post Detail (`posts/[id]/page.tsx` + tab components). This page has 7-9 tabs, recurring 3-column grid layouts, and hover-dependent interactions.

---

## Tab Bar

Post Detail has 7-9 tabs (Content, Infographic, Carousel, Images, Metadata, Hooks, Details, plus optional tabs). At 375px these overflow.

The foundation phase adds `overflow-x-auto` to the Tabs component globally. Verify the tab bar scrolls horizontally on this page. If the global fix isn't sufficient, add at the usage site:

```tsx
<TabsList className="overflow-x-auto flex-nowrap">
  <TabsTrigger>Content</TabsTrigger>
  <TabsTrigger>Infographic</TabsTrigger>
  {/* ... */}
</TabsList>
```

Add `scrollbar-hide` utility if visible scrollbar is ugly:
```css
/* In globals.css — may already exist from Phase 1 */
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
```

---

## 3-Column Grid Transformation

Four tabs share the same layout pattern:

| Tab | Col 1 | Col 2 | Col 3 |
|-----|-------|-------|-------|
| ContentTab | col-span-2 (timeline) | col-span-6 (editor) | col-span-4 (feedback) |
| InfographicTab | col-span-3 (timeline) | col-span-5 (preview) | col-span-4 (feedback) |
| CarouselTab | col-span-2 (timeline) | col-span-6 (slides) | col-span-4 (feedback) |
| ImagesTab | col-span-3 (timeline) | col-span-5 (images) | col-span-4 (feedback) |

### Desktop (unchanged)

```
+--------+------------------+------------+
| Timeline|    Editor/       |  Feedback  |
| (narrow)|   Preview        |   Panel    |
|         |  (main content)  |            |
+--------+------------------+------------+
```

### Mobile (stacked)

```
+---------------------------+
| [v1] [v2] [v3] [current]  |  <- Timeline as horizontal strip or dropdown
+---------------------------+
| Editor / Preview           |  <- Full width
| (main content area)        |
+---------------------------+
| [Show Feedback]            |  <- Expandable section or button
+---------------------------+
```

### Implementation

```tsx
// BEFORE
<div className="grid grid-cols-12 gap-6">
  <div className="col-span-2">
    <VersionTimeline versions={versions} />
  </div>
  <div className="col-span-6">
    <Editor content={content} />
  </div>
  <div className="col-span-4">
    <FeedbackPanel feedback={feedback} />
  </div>
</div>

// AFTER
<div className="space-y-4 md:space-y-0 md:grid md:grid-cols-12 md:gap-6">
  {/* Timeline: horizontal strip on mobile, vertical column on desktop */}
  <div className="md:col-span-2">
    <div className="md:hidden">
      <MobileVersionSelector versions={versions} current={currentVersion} onChange={setVersion} />
    </div>
    <div className="hidden md:block">
      <VersionTimeline versions={versions} />
    </div>
  </div>

  {/* Editor: full width on mobile */}
  <div className="md:col-span-6">
    <Editor content={content} />
  </div>

  {/* Feedback: expandable section on mobile, always visible on desktop */}
  <div className="md:col-span-4">
    <div className="md:hidden">
      <MobileFeedbackSection feedback={feedback} />
    </div>
    <div className="hidden md:block">
      <FeedbackPanel feedback={feedback} />
    </div>
  </div>
</div>
```

---

## Mobile Version Selector

Replace the vertical version timeline with a compact mobile alternative:

**Option A: Horizontal scrollable strip**
```tsx
function MobileVersionSelector({ versions, current, onChange }) {
  return (
    <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
      {versions.map(v => (
        <button
          key={v.id}
          onClick={() => onChange(v)}
          className={cn(
            "shrink-0 px-3 py-2 rounded-md text-sm border min-h-[44px]",
            v.id === current.id
              ? "bg-primary text-primary-foreground border-primary"
              : "bg-background border-border"
          )}
        >
          v{v.number}
        </button>
      ))}
    </div>
  )
}
```

**Option B: Dropdown selector** (if many versions)
```tsx
function MobileVersionSelector({ versions, current, onChange }) {
  return (
    <Select value={current.id} onValueChange={(id) => onChange(versions.find(v => v.id === id))}>
      <SelectTrigger className="w-full h-11">
        <SelectValue>Version {current.number}</SelectValue>
      </SelectTrigger>
      <SelectContent>
        {versions.map(v => (
          <SelectItem key={v.id} value={v.id}>
            Version {v.number} — {formatDate(v.createdAt)}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
```

Prefer Option A if typically < 5 versions, Option B if more.

---

## Mobile Feedback Section

Replace the always-visible feedback panel with an expandable section:

```tsx
function MobileFeedbackSection({ feedback }) {
  const [isOpen, setIsOpen] = useState(false)
  const feedbackCount = feedback?.length ?? 0

  return (
    <div className="border rounded-lg">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full p-4 min-h-[44px]"
      >
        <span className="font-medium text-sm">
          Feedback {feedbackCount > 0 && `(${feedbackCount})`}
        </span>
        <ChevronDown className={cn("h-4 w-4 transition-transform", isOpen && "rotate-180")} />
      </button>
      {isOpen && (
        <div className="px-4 pb-4 border-t">
          <FeedbackPanel feedback={feedback} />
        </div>
      )}
    </div>
  )
}
```

---

## Hover Interactions on Post Detail

| Interaction | Location | Mobile Fix |
|-------------|----------|------------|
| HoverCard on ReadinessIndicator | `page.tsx` | Radix handles tap-to-open natively. Ensure trigger is >= 44px |
| Tooltip on locked tabs | `page.tsx` | Radix handles tap-to-show natively. No changes |
| onMouseOver/onMouseOut feedback highlights | `ArticleEditor.tsx` | Highlights should be tappable. Add onClick handler that does the same as onMouseOver |
| onMouseUp text selection comment | `ArticleEditor.tsx` | Touch selection fires equivalent events. Verify — likely no changes needed |

---

## Post Detail Page-Level Changes

Beyond the tab components:

1. **Outer padding:** `p-6` to `p-4 md:p-6`
2. **Page header actions:** StatusBadge + action buttons may overflow. Use Pattern 7 (card header actions) to stack
3. **Readiness indicator:** Ensure HoverCard trigger is large enough for touch (44px)
4. **Tab content padding:** Each tab's content area `p-6` to `p-4 md:p-6`
