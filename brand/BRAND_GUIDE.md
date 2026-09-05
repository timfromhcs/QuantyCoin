# QuantyCoin QTY4 Brand Guide & Visual Identity System

**Protocol Generation**: `QTY4`  
**Status**: Official Active Standard  
**Date**: September 2026  

---

## 1. Brand Identity Overview

QuantyCoin QTY4 represents a technically serious, sovereign, post-quantum cryptocurrency engineered for high throughput, dual-lane mining, and mathematical determinism. The visual identity reflects:
- **Cryptographic Rigor**: Precision geometry, mathematical symmetry, and clean line weights.
- **Accessibility & Contrast**: High-contrast dark and light variants that maintain full legibility across any display.
- **Vector-First Source**: Scalable SVG masters with zero pixelation at icon sizes or high-DPI displays.

---

## 2. Official Visual Assets

| Asset | Path | Description | Best Used On |
| :--- | :--- | :--- | :--- |
| **Master Lockup** | `brand/logo.svg` | Transparent horizontal lockup with QTY4 badge | Medium/Dark surfaces |
| **Dark Canvas** | `brand/logo-dark.svg` | Solid `#0B0F17` background with electric cyan typography | Dark mode headers, GitHub dark |
| **Light Canvas** | `brand/logo-light.svg` | Solid `#FFFFFF` background with high-contrast slate typography | White paper headers, print, light UI |
| **Icon / Coin** | `brand/icon.svg` | Geometric Q torus with high-contrast core | App icons, avatars, favicons |
| **Monochrome** | `brand/monochrome.svg` | Pure single-color silhouette | Hardware engravings, stamps |
| **Palette Spec** | `brand/colors.json` | Machine-readable color definitions and contrast ratios | UI styling, CSS themes |

---

## 3. Color System & Contrast Assurance

```
┌─────────────────────────────────────────────────────────────────┐
│ #0B0F17          │ Dark Canvas   │ Primary dark mode background │
├─────────────────────────────────────────────────────────────────┤
│ #FFFFFF          │ Light Canvas  │ Primary light mode canvas    │
├─────────────────────────────────────────────────────────────────┤
│ #0284C7          │ Core Blue     │ Primary brand accent         │
├─────────────────────────────────────────────────────────────────┤
│ #38BDF8          │ Electric Cyan │ Verified consensus glow      │
├─────────────────────────────────────────────────────────────────┤
│ #0F172A          │ Dark Text     │ Text on light (17.4:1 AAA)   │
├─────────────────────────────────────────────────────────────────┤
│ #F8FAFC          │ Light Text    │ Text on dark (16.8:1 AAA)    │
└─────────────────────────────────────────────────────────────────┘
```

All primary text and indicator combinations exceed WCAG 2.1 AAA accessibility contrast standards.
