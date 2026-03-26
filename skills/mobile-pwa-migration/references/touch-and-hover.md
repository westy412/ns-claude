# Touch Targets and Hover Alternatives

> Guidelines for making interactive elements touch-friendly and replacing hover-dependent interactions with mobile alternatives.

---

## Touch Target Sizing

### Minimum Dimensions

All tappable elements must be at least **44px x 44px** on mobile (Apple HIG standard). This includes:
- Buttons
- Links
- Form inputs
- Select triggers
- Menu items
- Icon buttons
- Tab items

### Common Fixes

```tsx
// Icon button too small (32px)
// BEFORE
<Button variant="ghost" size="icon" className="h-8 w-8">

// AFTER — bigger on mobile
<Button variant="ghost" size="icon" className="h-11 w-11 md:h-8 md:w-8">
```

```tsx
// DropdownMenu items too short (32px with py-1.5)
// BEFORE
<DropdownMenuItem className="py-1.5">

// AFTER — taller on mobile
<DropdownMenuItem className="py-3 md:py-1.5">
```

```tsx
// Form input too short
// BEFORE
<Input className="h-9" />

// AFTER
<Input className="h-11 md:h-9" />
```

### Spacing Between Targets

Minimum **8px** between adjacent touch targets to prevent mis-taps.

```tsx
// Adjacent icon buttons
<div className="flex items-center gap-2 md:gap-1">
  <Button variant="ghost" size="icon">...</Button>
  <Button variant="ghost" size="icon">...</Button>
</div>
```

---

## Hover-to-Touch Conversions

### HoverCard (Radix)

Radix HoverCard supports touch natively — it opens on tap instead of hover. No code changes needed in most cases.

If the trigger needs adjustment:
```tsx
// Ensure trigger is large enough to tap
<HoverCardTrigger asChild>
  <span className="cursor-pointer min-h-[44px] inline-flex items-center">
    {content}
  </span>
</HoverCardTrigger>
```

### Tooltip (Radix)

Radix Tooltip shows on tap on touch devices. No changes needed for the component itself.

If you need tap-to-show explicitly:
```tsx
<TooltipProvider>
  <Tooltip delayDuration={0}>
    <TooltipTrigger asChild>
      <span className="min-h-[44px] inline-flex items-center">{trigger}</span>
    </TooltipTrigger>
    <TooltipContent>{message}</TooltipContent>
  </Tooltip>
</TooltipProvider>
```

### group-hover Visibility

Elements that appear on hover (edit icons, action buttons) should be always visible on mobile.

```tsx
// BEFORE — hidden until hover
<div className="group">
  <span>Content</span>
  <Button className="opacity-0 group-hover:opacity-100">Edit</Button>
</div>

// AFTER — visible on mobile, hover on desktop
<div className="group">
  <span>Content</span>
  <Button className="opacity-100 md:opacity-0 md:group-hover:opacity-100">Edit</Button>
</div>
```

### onMouseEnter / onMouseLeave

If JavaScript event handlers control visibility on hover, add touch alternative:

```tsx
// BEFORE
<div
  onMouseEnter={() => setShowActions(true)}
  onMouseLeave={() => setShowActions(false)}
>
  {showActions && <Actions />}
</div>

// AFTER — always show on mobile, hover on desktop
<div
  onMouseEnter={() => setShowActions(true)}
  onMouseLeave={() => setShowActions(false)}
>
  {/* Always visible on mobile */}
  <div className="md:hidden"><Actions /></div>
  {/* Hover-controlled on desktop */}
  <div className="hidden md:block">
    {showActions && <Actions />}
  </div>
</div>
```

### onMouseUp Text Selection

Text selection with `onMouseUp` handler (e.g., for inline comments) generally works with touch selection. The browser fires touch equivalents. Verify by testing — usually no code changes needed.

### ContextMenu (Right-Click)

Right-click menus don't work on mobile. Replace with visible action buttons on the mobile card/row:

```tsx
// Desktop: ContextMenu on right-click (keep as-is)
<ContextMenu>
  <ContextMenuTrigger>
    <div className="hidden md:block">
      <TableRow>...</TableRow>
    </div>
  </ContextMenuTrigger>
  <ContextMenuContent>...</ContextMenuContent>
</ContextMenu>

// Mobile: DropdownMenu with visible trigger
<div className="block md:hidden">
  <MobileCard>
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon"><MoreHorizontal /></Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>...</DropdownMenuContent>
    </DropdownMenu>
  </MobileCard>
</div>
```

---

## Date Picker on Mobile

Dual-month date pickers don't fit on mobile. Use responsive month count:

```tsx
// BEFORE
<Calendar numberOfMonths={2} />

// AFTER
import { useMediaQuery } from '@/hooks/use-media-query'

const isMobile = useMediaQuery('(max-width: 767px)')
<Calendar numberOfMonths={isMobile ? 1 : 2} />
```

If `useMediaQuery` doesn't exist yet, create a simple hook:

```tsx
// src/hooks/use-media-query.ts
import { useState, useEffect } from 'react'

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    const media = window.matchMedia(query)
    setMatches(media.matches)
    const listener = (e: MediaQueryListEvent) => setMatches(e.matches)
    media.addEventListener('change', listener)
    return () => media.removeEventListener('change', listener)
  }, [query])

  return matches
}
```
