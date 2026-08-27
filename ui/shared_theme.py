"""
QuantyCoin Cyberpunk Dark Mode Theme & Base HTML UI Framework
Branding: Obsidian #0A0D14 | Quanty Cyan #00F0FF | Neon Violet #8A2BE2 | Slate Grey #1E2433
"""

CYBERPUNK_CSS = """
:root {
  --bg-obsidian: #0A0D14;
  --bg-card: #121724;
  --bg-card-hover: #181F30;
  --bg-slate: #1E2433;
  --bg-input: #0e121a;
  --accent-cyan: #00F0FF;
  --accent-violet: #8A2BE2;
  --accent-pink: #FF007A;
  --accent-green: #00FF88;
  --text-main: #F1F5F9;
  --text-muted: #94A3B8;
  --border-color: #1E293B;
  --border-cyan: rgba(0, 240, 255, 0.4);
  --border-violet: rgba(138, 43, 226, 0.4);
  --glow-cyan: 0 0 15px rgba(0, 240, 255, 0.25);
  --glow-violet: 0 0 15px rgba(138, 43, 226, 0.25);
  --font-main: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--bg-obsidian);
  color: var(--text-main);
  font-family: var(--font-main);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: var(--bg-obsidian);
}
::-webkit-scrollbar-thumb {
  background: var(--bg-slate);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--accent-cyan);
}

/* Header & Brand Navbar */
.navbar {
  background: rgba(18, 23, 36, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: var(--text-main);
}

.logo-icon {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-violet));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-family: var(--font-mono);
  color: #000;
  box-shadow: var(--glow-cyan);
}

.brand-title {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.brand-title span {
  color: var(--accent-cyan);
}

.brand-badge {
  font-size: 11px;
  background: rgba(0, 240, 255, 0.1);
  color: var(--accent-cyan);
  border: 1px solid var(--border-cyan);
  padding: 2px 8px;
  border-radius: 12px;
  font-family: var(--font-mono);
}

/* Layout Container */
.container {
  flex: 1;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 24px;
}

/* Grid & Cards */
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s ease-in-out;
}

.card:hover {
  border-color: rgba(0, 240, 255, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: 12px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-main);
  font-family: var(--font-mono);
}

/* Buttons */
.btn {
  background: var(--bg-slate);
  color: var(--text-main);
  border: 1px solid var(--border-color);
  padding: 10px 18px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.btn:hover {
  background: var(--bg-card-hover);
  border-color: var(--accent-cyan);
  box-shadow: var(--glow-cyan);
  color: #FFF;
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent-cyan), #00A3FF);
  color: #000;
  border: none;
  font-weight: 700;
  box-shadow: var(--glow-cyan);
}

.btn-primary:hover {
  filter: brightness(1.15);
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
  color: #000;
}

.btn-violet {
  background: linear-gradient(135deg, var(--accent-violet), #6A0DAD);
  color: #FFF;
  border: none;
  font-weight: 700;
  box-shadow: var(--glow-violet);
}

.btn-violet:hover {
  filter: brightness(1.15);
  box-shadow: 0 0 20px rgba(138, 43, 226, 0.5);
}

.btn-danger {
  background: rgba(255, 0, 122, 0.15);
  color: var(--accent-pink);
  border: 1px solid rgba(255, 0, 122, 0.3);
}

.btn-danger:hover {
  background: var(--accent-pink);
  color: #FFF;
}

/* Inputs & Form Controls */
.input-group {
  margin-bottom: 16px;
}

.input-label {
  display: block;
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 6px;
  font-weight: 500;
}

.input-control {
  width: 100%;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  font-family: var(--font-mono);
  outline: none;
  transition: border-color 0.2s;
}

.input-control:focus {
  border-color: var(--accent-cyan);
  box-shadow: var(--glow-cyan);
}

/* Tables */
.table-container {
  overflow-x: auto;
  margin-top: 12px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

th {
  background: var(--bg-slate);
  color: var(--text-muted);
  padding: 10px 14px;
  font-weight: 600;
  border-bottom: 1px solid var(--border-color);
}

td {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  font-family: var(--font-mono);
}

tr:hover td {
  background: rgba(0, 240, 255, 0.02);
}

/* Badges & Status Pills */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 20px;
  font-family: var(--font-mono);
}

.status-online {
  background: rgba(0, 255, 136, 0.1);
  color: var(--accent-green);
  border: 1px solid rgba(0, 255, 136, 0.3);
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-green);
  box-shadow: 0 0 8px var(--accent-green);
}

/* Tabs */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 8px;
}

.tab-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  padding: 8px 16px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--text-main);
  background: var(--bg-card);
}

.tab-btn.active {
  color: var(--accent-cyan);
  background: rgba(0, 240, 255, 0.1);
  border: 1px solid var(--border-cyan);
}
"""


def render_html_page(title: str, app_name: str, body_content: str, custom_js: str = "") -> str:
    """Renders complete standalone Cyberpunk Dark Mode HTML document."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — QuantyCoin v3.0</title>
  <style>{CYBERPUNK_CSS}</style>
</head>
<body>
  <header class="navbar">
    <a href="/" class="brand-logo">
      <div class="logo-icon">Q</div>
      <div class="brand-title">Quanty<span>Coin</span></div>
      <div class="brand-badge">{app_name}</div>
    </a>
    <div style="display: flex; align-items: center; gap: 16px;">
      <div class="status-pill status-online">
        <div class="status-indicator"></div>
        <span>MAINNET v3.0</span>
      </div>
    </div>
  </header>

  <main class="container">
    {body_content}
  </main>

  <footer style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 12px; border-top: 1px solid var(--border-color);">
    QuantyCoin Core Ecosystem v3.0.0 &bull; High-Speed Quantum & AI Era Layer-1 &bull; MIT License
  </footer>

  <script>
    {custom_js}
  </script>
</body>
</html>
"""
