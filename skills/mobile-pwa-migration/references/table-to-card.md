# Table-to-Card Conversion

> How to convert wide data tables into mobile card layouts. Desktop keeps the table; mobile shows cards.

---

## Core Approach

Use conditional rendering with Tailwind visibility classes. Both layouts exist in the DOM but only one is visible at each breakpoint.

```tsx
{/* Desktop: standard table */}
<div className="hidden md:block">
  <Table>
    <TableHeader>...</TableHeader>
    <TableBody>
      {items.map(item => <TableRow key={item.id}>...</TableRow>)}
    </TableBody>
  </Table>
</div>

{/* Mobile: card list */}
<div className="block md:hidden space-y-3">
  {items.map(item => (
    <MobileCard key={item.id} item={item} />
  ))}
</div>
```

---

## Mobile Card Structure

Every mobile card follows this layout:

```tsx
function MobileCard({ item, onAction }) {
  return (
    <div className="border rounded-lg p-4 space-y-2">
      {/* Row 1: Title + Status */}
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-medium text-sm line-clamp-2">{item.title}</h3>
        <StatusBadge status={item.status} />
      </div>

      {/* Row 2: Secondary info */}
      <div className="flex items-center gap-3 text-xs text-muted-foreground">
        <PlatformIcon platform={item.platform} className="h-4 w-4" />
        <span>{item.secondaryInfo}</span>
        <span>{formatDate(item.updatedAt)}</span>
      </div>

      {/* Row 3: Actions (optional) */}
      <div className="flex items-center gap-2 pt-1">
        <Button variant="ghost" size="sm" onClick={() => onAction(item)}>
          Action
        </Button>
      </div>
    </div>
  );
}
```

### Card Information Hierarchy

| Priority | Content | Example |
|----------|---------|---------|
| **Primary** | Title/name (line-clamp-2) | Post title, campaign name |
| **Status** | Badge in top-right | Draft, Published, In Review |
| **Secondary** | Icons + labels in a row | Platform icon, format, pillar |
| **Metric** | Key number if applicable | Post count, impressions |
| **Timestamp** | Relative or short date | "2h ago", "Mar 5" |
| **Actions** | Buttons or dropdown | Edit, Delete, View |

### Key Rules

- Title gets `line-clamp-2` to prevent overflow
- Status badge stays top-right (consistent placement)
- Secondary info uses `text-xs text-muted-foreground`
- Actions use `Button variant="ghost" size="sm"` for minimal visual weight
- Cards use `space-y-2` for consistent internal spacing
- Card list uses `space-y-3` for between-card spacing

---

## Specific Table Conversions

### PostsTable (6 columns, ~910px)

Desktop columns: Title (300px), Status (120px), Platform (120px), Format (120px), Campaign (150px), Updated (100px)

Mobile card:
- Row 1: Title (line-clamp-2) + StatusBadge
- Row 2: PlatformIcon + Format + Campaign name
- Row 3: Updated timestamp + action menu (replaces right-click ContextMenu)

**Important:** PostsTable uses ContextMenu (right-click) for actions. On mobile, replace with a visible action button (three-dot menu or action buttons).

### CampaignsTable (5 columns, ~790px)

Desktop columns: Name (300px), Status (120px), Pillar (150px), Posts (100px), Updated (120px)

Mobile card:
- Row 1: Campaign name (line-clamp-2) + StatusBadge
- Row 2: Pillar name + Post count ("X posts")
- Row 3: Updated timestamp

### Analytics Posts Table (8 columns, ~900px+)

Desktop columns: Post, Platform, Published, Impressions, Reactions, Comments, Reposts, Actions

Mobile card:
- Row 1: Post title (line-clamp-2) + PlatformIcon
- Row 2: Published date
- Row 3: Metrics row — impressions, reactions, comments (use compact number format)
- Row 4: Actions (always visible, not group-hover)

---

## ContextMenu to Action Button

Desktop right-click menus don't work on mobile. Replace with visible action buttons.

```tsx
// BEFORE: Desktop right-click
<ContextMenu>
  <ContextMenuTrigger asChild>
    <TableRow>...</TableRow>
  </ContextMenuTrigger>
  <ContextMenuContent>
    <ContextMenuItem>Edit</ContextMenuItem>
    <ContextMenuItem>Delete</ContextMenuItem>
  </ContextMenuContent>
</ContextMenu>

// AFTER: In the mobile card, use a dropdown
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
      <MoreHorizontal className="h-4 w-4" />
    </Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent align="end">
    <DropdownMenuItem>Edit</DropdownMenuItem>
    <DropdownMenuItem>Delete</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

---

## Empty State

If the table/card list is empty, the EmptyState component works at any width. No changes needed.
