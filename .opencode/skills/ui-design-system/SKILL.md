---
name: ui-design-system
description: Design system for the responsive, modern, clean, futuristic UI - tokens, components, layouts, room display spec, theming, i18n and accessibility. Use before touching templates or CSS.
---
# UI design system - "Futuristic Clean"

## Principles
Mobile-first. Dark-first calm futurism: deep navy/graphite surfaces, subtle glass, restrained neon accents, generous spacing, one primary action per screen. Everything self-hosted (Tailwind built with the standalone CLI, DaisyUI, Inter + JetBrains Mono fonts, Lucide SVG icons). **No external CDN or font requests at runtime.**

## Tokens (define as CSS variables; map into Tailwind/DaisyUI theme; support light and dark)
Dark: bg `#0B1020`, surface `#111936`, elevated `#172046`, border `#24305E`, text `#E6EAF7`, muted `#8D98BF`, primary cyan `#22D3EE`, secondary violet `#8B5CF6`, success `#34D399`, warning `#FBBF24`, danger `#F87171`, info `#60A5FA`.
Light: bg `#F5F7FB`, surface `#FFFFFF`, border `#E2E8F4`, text `#0F172A`, muted `#64748B`, primary `#0891B2`, secondary `#7C3AED`, success `#059669`, warning `#D97706`, danger `#DC2626`.
Radius: cards 16px, inputs/buttons 12px, pills full. Shadows soft; glow only on primary/active elements. Glass: `bg-white/5` + `backdrop-blur` + 1px border `white/10` (dark).
Motion 150-200 ms ease-out; respect `prefers-reduced-motion`.
Type: Inter for UI; JetBrains Mono for clock, counts, percentages. Scale 12/14/16/20/24/32/48; room display body >= 24px.

## Status colors (consistent everywhere)
Belum = slate, Sedang = cyan, Selesai = green, Pending = amber, Batal = muted red, Terbawa = orange badge. Never color alone: add icon + text.

## Layout
Breakpoints: 360 / 768 / 1280 / 1920. Desktop: left sidebar. Mobile: bottom nav, sheets instead of modals where possible. Tables become stacked cards under 768px. Roster grid scrolls horizontally with a sticky first column. Touch targets >= 44px.

## Components (build once, reuse)
Button, IconButton, Card, Stat tile, Progress ring/bar (CSS/SVG, no heavy chart lib), Badge, Table/Card list, Form field with inline error, Select with search, Modal/Sheet, Toast, Empty state, Skeleton loader, Pagination, Tabs, Segmented control (week/day), Stale-data banner.

## States
Every screen/partial defines loading (skeleton), empty (helpful text + action), error (what happened + retry). HTMX swaps keep scroll and focus.

## Theming & language
Theme (light/dark/system) and language (id/en) are per user, applied server-side on render (no flash). Room display defaults to dark. All text via i18n; no text baked into images/CSS.

## Room display (1920x1080)
No interaction. Header: clock (mono), date, active shift(s) (two during overlap), "last updated" + stale banner when polling fails. Body: personnel per shift, job columns by status, kelengkapan, progress ring. Auto-page every 10 s when content overflows. Subtle position drift of accents to avoid burn-in. Public mode shows minimum data only.

## Supervisor dashboard
KPI tiles (persen selesai, per status, Terbawa, Pending, kelengkapan), personnel per shift, filter date/shift, drill-down to job detail. Works on phone.

## Accessibility
WCAG AA contrast, visible focus rings, labels on all inputs, `aria-live="polite"` for HTMX updates, keyboard operable, semantic HTML.

## Done check for any screen
Checked at 360, 768, 1280 widths, light and dark, id and en, empty/error states, no external requests (Network tab).
