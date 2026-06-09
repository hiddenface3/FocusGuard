---
name: Lumina Cyber-Glass
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394e'
  surface-container-lowest: '#060d20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3e'
  surface-container-highest: '#2d3449'
  on-surface: '#dbe2fd'
  on-surface-variant: '#cac4d0'
  inverse-surface: '#dbe2fd'
  inverse-on-surface: '#283044'
  outline: '#948f9a'
  outline-variant: '#49454f'
  surface-tint: '#d0bcff'
  primary: '#e9ddff'
  on-primary: '#37265e'
  primary-container: '#d0bcff'
  on-primary-container: '#594983'
  inverse-primary: '#665590'
  secondary: '#adc6ff'
  on-secondary: '#122f5f'
  secondary-container: '#2c4677'
  on-secondary-container: '#9cb5ed'
  tertiary: '#6ffbbe'
  on-tertiary: '#003824'
  tertiary-container: '#4edea3'
  on-tertiary-container: '#005f40'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e9ddff'
  primary-fixed-dim: '#d0bcff'
  on-primary-fixed: '#210f48'
  on-primary-fixed-variant: '#4d3d76'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#adc6ff'
  on-secondary-fixed: '#001a42'
  on-secondary-fixed-variant: '#2c4677'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#005236'
  background: '#0b1326'
  on-background: '#dbe2fd'
  surface-variant: '#2d3449'
  surface-glass: rgba(45, 52, 73, 0.15)
  input-glass: rgba(11, 19, 38, 0.5)
  border-glow: rgba(208, 188, 255, 0.15)
  error-alert: '#ffb4ab'
  terminal-bg: '#060e20'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '500'
    lineHeight: '1.5'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-padding: 32px
  gutter: 24px
  card-gap: 16px
  section-margin: 48px
---

## Brand & Style
Lumina Cyber-Glass is a sophisticated, tech-forward aesthetic designed for high-focus utility and developer-centric environments. It merges **Glassmorphism** with **Corporate Modern** reliability. The brand personality is "Vigilant yet Unobtrusive," characterized by a dark, immersive atmosphere, vibrant neon accents for state indication, and high-precision typography.

The visual style relies on translucent layers, deep background blurs (20px+), and subtle radial glows that suggest a holographic or terminal-inspired interface. It targets power users who value information density and real-time feedback without visual clutter.

## Colors
The palette is rooted in a deep "Midnight Slate" (`#0b1326`) background, accented by low-opacity radial gradients in Primary (Lavender) and Secondary (Blue) to provide depth. 

- **Primary (`#d0bcff`):** Used for branding, active navigation states, and focus-related metrics.
- **Secondary (`#adc6ff`):** Used for informational icons and window-level identifiers.
- **Tertiary (`#4edea3`):** Reserved exclusively for "Active," "Live," and "Safe" status indicators.
- **Error (`#ffb4ab`):** High-contrast coral used for blocked items and destructive actions.

The "Glass" effect is achieved by using `surface-variant` colors at 15% opacity with high backdrop blur, ensuring text remain legible against the dark background.

## Typography
The system uses a dual-font approach:
1. **Inter** handles all UI choreography, providing a neutral and highly legible sans-serif for headlines and body content.
2. **JetBrains Mono** is utilized for "System" data, timestamps, terminal feeds, and uppercase labels. This reinforces the technical, precise nature of the tool.

Hierarchy is strictly enforced through weight (600+ for headers) and letter spacing (expanded for labels, condensed for large displays).

## Layout & Spacing
The layout follows a **Fixed-Fluid Hybrid** model. The main content is capped at a `1200px` max-width to ensure readability on ultrawide monitors.

- **Grid:** A 12-column layout. On desktop, a 4-column sidebar (left) and 8-column main content (right) split is standard.
- **Breakpoints:** On mobile and tablet (below `1024px`), the grid collapses into a single-column stack.
- **Rhythm:** An 8px base unit controls all margins and padding. Standard card padding is `24px` (3 units).
- **Navigation:** A fixed `64px` top bar provides a consistent anchor point, using a backdrop-blur of `xl` to separate it from the scrolling content.

## Elevation & Depth
Depth is created through **Glassmorphism** and **Light-Emitting Borders** rather than traditional shadows.

1.  **Base Layer:** Midnight background with soft radial gradients.
2.  **Panel Layer:** `glass-panel` utility. 15% opacity backgrounds with 20px blur. 1px solid white borders at 10% opacity, with 20% opacity on top/left edges to simulate a subtle top-down light source.
3.  **Active Layer:** Elements like the TopNavBar or Focused Inputs use a "Glow" shadow (`shadow-[0_0_15px_rgba(208,188,255,0.15)]`) to appear as if they are self-illuminated.
4.  **Terminal Layer:** Inset appearance created by using a darker, higher-opacity background (`surface-container-lowest/80`) to represent a "sunken" data feed.

## Shapes
The system uses a "Rounded" (Level 2) logic to soften the technical edge of the monospaced fonts and dark colors.

- **Cards/Panels:** `1rem` (rounded-xl) for main containers.
- **Inputs/Buttons:** `0.5rem` (rounded-lg) for standard interactive elements.
- **Status Pills:** Fully rounded (Pill-shaped) to distinguish them from structural elements.
- **Indicators:** Small dots (8px-12px) use a `pulse` animation to denote live states.

## Components
- **Buttons:**
    - *Primary:* Uses a `btn-primary-gradient` (Inverse-Primary to Secondary-Container). Features a hover transform (translateY -1px) and intensified glow.
    - *Ghost:* Dashed borders for "Add" actions, using `outline-variant` colors.
- **Inputs:**
    - *Glass Input:* Dark slate background (`0.5` opacity) with a focus state that adds a primary-colored border and `10px` outer glow.
- **Toggle Switches:** Custom styling where the track is `surface-variant` and transitions to a primary-gradient when active. The thumb is a crisp white circle.
- **Detection Feed:** A specific terminal component using `JetBrains Mono` with specific token colors for `process`, `window`, and `rule` keys to allow for rapid scanning.
- **Status Indicators:** Includes a `pulse-dot` animation (2s infinite) to provide a "heartbeat" feel to the live monitoring.
- **List Items:** Enclosed in `surface-container-low` backgrounds with color-coded borders (e.g., error-red for bad apps) to group items clearly within a panel.