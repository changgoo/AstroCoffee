---
version: alpha
name: AstroCoffee Calendar
colors:
  primary: "#b8422e"
  secondary: "#6a7178"
  tertiary: "#8e3b2b"
  neutral: "#1a1c1e"
  surface: "#fcfbf8"
  surface-muted: "#f1eee8"
  border: "#d7d1c8"
typography:
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.5
  heading:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 16px
    fontWeight: 700
    lineHeight: 1.2
rounded:
  sm: 4px
  md: 6px
  lg: 8px
  full: 9999px
---

# AstroCoffee Calendar

This project uses the DESIGN.md format as a local guide for visual decisions.
The upstream reference is the Google Labs `design.md` repository.

## Overview

The calendar should feel restrained, legible, and work-focused. It is a tool
for scanning dates and assignments quickly, not a promotional page.

The visual tone is warm and editorial: light surfaces, dark text, one muted
accent color, and clear separation between calendar cells and the assignment
list.

## Colors

Use a light neutral background with a warm surface tone. Keep the accent color
reserved for current-state indicators, primary actions, and selected details.

Avoid saturated blues, heavy gradients, and decorative color noise.

## Typography

Use a clean system sans-serif stack. Keep headings compact and readable.
Do not rely on large display type or oversized labels for routine UI.

## Layout

Use dense but organized spacing. Preserve clear gutters between the month grid
and the assignment panel.

Panels should be full-width within the main content column, with simple borders
instead of floating cards stacked inside other cards.

## Elevation & Depth

Keep depth subtle. Prefer borders, background contrast, and very light shadow
only where needed to separate surfaces.

## Shapes

Use small radii for containers and pills. Keep controls and list items
rectilinear and predictable.

## Components

Buttons, pills, list rows, and date tags should be compact and clearly labeled.
The assignment panel should present names on the left and date chips on the
right, wrapping cleanly on small screens.

## Do's and Don'ts

Do:

- Keep the calendar readable at a glance.
- Use one accent color consistently.
- Prefer borders and spacing over visual ornament.
- Ensure the assignment list remains scannable on mobile.

Don't:

- Add decorative gradients or background blobs.
- Use oversized cards for routine information.
- Introduce additional colors unless they encode meaning.
- Let labels or dates overlap or wrap unpredictably.
