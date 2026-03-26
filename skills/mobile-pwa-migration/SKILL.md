---
name: mobile-pwa-migration
description: Patterns and constraints for mobile-responsive page migrations in ns-content-workforce-app. Load when implementing mobile responsive changes for the Content Workforce PWA. Provides 7 recurring transformation patterns, touch target guidelines, hover-to-touch alternatives, and table-to-card conversion patterns.
user-invocable: false
---

# Mobile PWA Migration

Reference patterns for making Content Workforce pages mobile-responsive. Every page migration follows the same core patterns. Apply them consistently.

## Critical Constraint

**Desktop must not change.** All mobile changes are additive. Never remove or modify desktop styles — only add mobile-first styles with `md:` breakpoint overrides.

```
CORRECT:  className="px-3 md:px-6"           (mobile gets 12px, desktop keeps 24px)
CORRECT:  className="hidden md:block"          (hidden on mobile, visible on desktop)
CORRECT:  className="flex-col md:flex-row"     (stacked on mobile, side-by-side on desktop)

WRONG:    className="px-3"                     (desktop lost its px-6)
WRONG:    Removing an existing className        (desktop behavior changed)
WRONG:    Wrapping in a conditional render      (unless truly needed for different components)
```

## Breakpoint

Mobile is `< md (768px)`. Use Tailwind's `md:` prefix for desktop styles. This is the ONLY breakpoint used. Do not use `sm:`, `lg:`, or `xl:` unless they already exist in the code.

## Technology Constraints

- **Tailwind CSS 4** — No tailwind.config file. Uses `@theme inline` in globals.css. Default breakpoints (sm:640, md:768, lg:1024)
- **shadcn/ui** — Do NOT modify base components in `components/ui/`. Use className overrides on usage sites
- **Next.js 16 + React 19** — Use `viewport` export (not meta tag). Server components by default
- **PageHeader** — Used by 38+ pages. Changes must be backward-compatible with existing `actions` prop

## Quick Pattern Reference

Seven recurring patterns. Apply the matching pattern for each element you encounter:

| # | Pattern | Transformation | Reference |
|---|---------|---------------|-----------|
| 1 | Two-column layouts | `flex-col md:flex-row` or `grid-cols-1 md:grid-cols-12` | [patterns.md](references/patterns.md) |
| 2 | Fixed-width selects | `w-[Npx]` to `w-full md:w-[Npx]` | [patterns.md](references/patterns.md) |
| 3 | Wide data tables | `hidden md:block` table + `block md:hidden` card list | [table-to-card.md](references/table-to-card.md) |
| 4 | Toolbars | Stack vertically, search full-width on own row | [patterns.md](references/patterns.md) |
| 5 | Kanban boards | `hidden md:block` on container, default to list view | [patterns.md](references/patterns.md) |
| 6 | Generous padding | `px-3 md:px-6` or `p-4 md:p-6` | [patterns.md](references/patterns.md) |
| 7 | Card header actions | `flex-col md:flex-row` with `gap-2` | [patterns.md](references/patterns.md) |

## Reference Files

| Topic | File | When to Load |
|-------|------|--------------|
| Pattern transformations (1,2,4,5,6,7) | [patterns.md](references/patterns.md) | When applying any of the 6 layout patterns |
| Table-to-card conversion (pattern 3) | [table-to-card.md](references/table-to-card.md) | When converting a data table to mobile cards |
| Touch targets and hover alternatives | [touch-and-hover.md](references/touch-and-hover.md) | When handling interactive elements, hover states, or touch targets |
| Post Detail page specifics | [post-detail.md](references/post-detail.md) | When working on the Post Detail page (3-column grid, tabs, feedback panel) |

## Touch Targets

- Minimum **44px x 44px** for all tappable elements
- **8px** minimum spacing between adjacent touch targets
- Form inputs: minimum **44px height** on mobile
- DropdownMenu items: `py-3 md:py-1.5` (48px mobile, 32px desktop)

## Hover-to-Touch Quick Reference

| Desktop Pattern | Mobile Alternative |
|----------------|-------------------|
| `HoverCard` | Tap to open (Radix supports this natively) |
| `Tooltip` | Tap to show (Radix supports this natively) |
| `group-hover:opacity-100` | `opacity-100 md:opacity-0 md:group-hover:opacity-100` |
| `onMouseEnter`/`onMouseLeave` visibility | Always visible on mobile |
| `ContextMenu` (right-click) | Visible action button on mobile |
| `onMouseUp` text selection | Works with touch selection (verify) |

## Page Migration Checklist

For every page you migrate, verify:

- [ ] No horizontal overflow at 375px viewport width
- [ ] All touch targets >= 44px
- [ ] Padding reduced (`p-4 md:p-6` or `px-3 md:px-6`)
- [ ] Fixed-width elements made responsive (`w-full md:w-[Npx]`)
- [ ] Multi-column layouts stack on mobile
- [ ] Tables replaced with card layouts on mobile
- [ ] Hover interactions have touch alternatives
- [ ] Desktop layout unchanged at >= 768px
- [ ] No TypeScript errors
