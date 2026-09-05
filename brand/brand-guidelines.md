# QuantyCoin (QTY4) Brand Guidelines & Visual Identity System

**Protocol Version**: QTY4 (Protocol 70040)  
**Status**: Official Active Standard  
**Last Updated**: September 2026  

---

## 1. Brand Identity Overview

QuantyCoin (QTY4) is an open-source, sovereign Layer-1 cryptocurrency engineered on Asymmetric Dual Proof-of-Work (SHA-256D ASIC & RFC 7914 Scrypt 1024 CPU/GPU) with NIST FIPS 204 ML-DSA-44 post-quantum cryptography, pure 64-bit integer monetary arithmetic (`core.money.Amount`), 60-second block cadence, weighted chainwork, native SegWit & Bech32m addresses, Stratum V1/V2, and desktop GUI applications. See [BRAND_GUIDE.md](BRAND_GUIDE.md) for complete visual asset specifications.

The visual identity embodies **cryptographic rigor, open-source transparency, precision engineering, and sovereign decentralization**.

---

## 2. Official Brand Assets

All vector and raster brand assets are housed within the `/brand/` root directory:

| Asset Path | Format | Dimensions / ViewBox | Primary Purpose |
| :--- | :--- | :--- | :--- |
| `brand/logo.svg` | SVG | `750x180` | Primary horizontal lockup (mark + wordmark + QTY3 badge) |
| `brand/logo-mark.svg` | SVG | `512x512` | Standalone geometric Q icon for avatars, app icons, and coins |
| `brand/wordmark.svg` | SVG | `560x120` | Logotype for headers and linear media |
| `brand/monochrome.svg` | SVG | `512x512` | Pure single-color silhouette for hardware wallets and engravings |
| `brand/favicon.svg` | SVG | `64x64` | High-contrast favicon optimized for 16px–64px displays |
| `brand/social-preview.png` | PNG | `1200x630` | OpenGraph card for social previews, search engines, and web |
| `brand/github-social-preview.png`| PNG | `1280x640` | GitHub repository social preview header image |

---

## 3. Color Palette

The QuantyCoin color system is designed for high contrast and modern dark interfaces.

### Primary Colors

```
┌─────────────────────────────────────────────────────────────────┐
│ #0F172A          │ Slate 900     │ Primary Background & Canvas  │
├─────────────────────────────────────────────────────────────────┤
│ #0284C7          │ Sky 600       │ Core Brand Blue / PoW Relay  │
├─────────────────────────────────────────────────────────────────┤
│ #38BDF8          │ Sky 400       │ Electric Cyan / Active Glow  │
├─────────────────────────────────────────────────────────────────┤
│ #F8FAFC          │ Slate 50      │ Primary Typography & Heads   │
└─────────────────────────────────────────────────────────────────┘
```

### Secondary & Functional Accents

- **Subtle Surface**: `#1E293B` (Slate 800) — Container backgrounds, card strokes.
- **Border / Grid**: `#334155` (Slate 700) — Dividers, crosshair vectors.
- **Muted Text**: `#94A3B8` (Slate 400) — Captions, secondary metadata, hash displays.
- **Success / Validated**: `#10B981` (Emerald 500) — Consensus verification, tip match.
- **Warning**: `#F59E0B` (Amber 500) — Reorg alert, pending mempool.

---

## 4. Typography

### Primary Display & Interface Font
- **Family**: Inter, SF Pro Display, or system native sans-serif (`system-ui, -apple-system, sans-serif`).
- **Styles**:
  - `QUANTY`: ExtraBold / Black (Weight: 900), letter-spacing: -1.5px.
  - `COIN`: Regular / Light (Weight: 400), letter-spacing: -1.5px.
  - `QTY3` Badge: Bold (Weight: 800), all-caps, tracking: +1px.

### Monospace (Technical & Addresses)
- **Family**: JetBrains Mono, SF Mono, Consolas, or `monospace`.
- **Usage**: Bech32/Bech32m addresses (`qty1q...` SegWit, `qty1p...` ML-DSA-44 PQC, `qty1z...` Hybrid), hex hashes, block heights, RPC commands.

---

## 5. Logo Geometry & Anatomy

The QuantyCoin logo-mark consists of three core geometric elements:

1. **The Outer Torus (Q Ring)**: Represents the decentralized consensus network loop and circular transaction flow.
2. **The Inner Node Grid & Diamond Core**: Represents the cryptographic genesis block matrix and dual-lane target validation.
3. **The Dynamic Q-Tail**: Diagonal ray emerging from the core at 45 degrees, symbolizing peer-to-peer relay velocity and chain progression.

---

## 6. Clearspace & Minimum Sizing

- **Clearspace**: Maintain minimum breathing room equal to `1X` around all four sides of the mark, where `X` is the stroke thickness of the outer torus.
- **Minimum Digital Sizes**:
  - `logo-mark.svg` / `favicon.svg`: Minimum 16 × 16 px.
  - `logo.svg` (Horizontal): Minimum width 140 px.
  - App icons: 32 × 32 px, 64 × 64 px, 256 × 256 px.

---

## 7. Brand Misuse & Guardrails

To preserve protocol authenticity and security integrity:

- **DO NOT** modify the colors, gradients, or aspect ratios of the mark.
- **DO NOT** tilt, rotate, or distort the mark angles.
- **DO NOT** use legacy "v7.0", "v6.0", or deprecated logos/labels. The frozen protocol baseline is **QTY3**.
- **DO NOT** claim or imply endorsement or protocol identity equivalence with Bitcoin, Bitcoin Knots, or forks. QuantyCoin is an independent network with unique genesis, magic bytes, and ports.
- **DO NOT** place the color logo on busy or clashing photographic backgrounds without an opaque backdrop container.
