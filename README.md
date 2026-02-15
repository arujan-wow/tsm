# arujan-wow-tsm

<p align="center">
  <img src="assets/header-banner.jpg" alt="Earthen Dwarves Morning Ore Report" width="640">
</p>

**WoW gold-making toolkit** — live ore price scanning, daily email reports, TSM setup guides, and farming analysis. Built as a [Claude Code](https://claude.ai/claude-code) plugin.

---

## Features

### `/ore-scan` — Live Ore Market Scanner

Scans live auction house prices from [wowpricehub.com](https://wowpricehub.com) across **all 12 WoW expansions** (Classic through Midnight), ranks every ore by value, and tells you exactly what to farm and where.

```
/ore-scan              # defaults to US Area 52
/ore-scan us/illidan   # specify a different realm
/ore-scan eu/tarren-mill
```

**What it does:**
- Fetches live prices for **~45 ores** across Classic, TBC, WotLK, Cata, MoP, WoD, Legion, BFA, Shadowlands, Dragonflight, TWW, and Midnight
- Ranks all ores into tiers — **Premium** (100g+), **Profitable** (15-99g), **Moderate** (5-14g), **Budget** (<5g)
- Calculates **estimated gold/hour** using: `nodes/hr × ore/node × current price`
- Provides **Top 5 farming picks** with zones, routes, and reasoning
- Highlights **sleeper picks** with hidden value (transmute targets, prospect upside, low competition)

### Daily Ore Report Email

Automated daily email delivered at **8:00 AM** with a full market snapshot — no manual scanning required.

- Fetches all ore prices in parallel from wowpricehub.com
- **"Why" column** on every ore explaining the math and trade-off logic (e.g., "Volume play — massive spawns offset lower price" vs "High unit price but rare — patient farmers only")
- **Top Pick of the Day** highlight card with gold/hr breakdown
- Tiered ranking tables with farming zones
- **Top 5 Farming Picks** sorted by actual gold/hr, not just unit price
- Styled with a WoW-themed dark blue design using Cinzel fantasy fonts

### TSM Setup Guides

- **[Midnight JC + Mining Setup](midnight-jc-mining-setup.md)** — Complete step-by-step TSM configuration with group hierarchies, import strings, and auctioning/crafting/mailing operations for Midnight Jewelcrafting and Mining

---

## Related Projects

- [Midnight TSM Group Setup](https://github.com/MonChiSub/Midnight-TSM_Group_Setup) — Full TSM group import strings for Midnight JC & Mining

---

## Data

- **[references/ore-database.md](references/ore-database.md)** — Complete ore reference database with item IDs, wowpricehub URL patterns, farming zones, node density estimates, and ore yield data for all expansions

---

## Setup

### Claude Code Plugin

Clone and use as a Claude Code plugin for interactive `/ore-scan`:

```bash
git clone https://github.com/arujan-wow/tsm.git arujan-wow-tsm
```

The `.claude-plugin/plugin.json` manifest registers the plugin automatically. The `/ore-scan` command is available in any Claude Code session within this repo.

**Requires:** Claude Code with WebFetch access

### Daily Email (Windows)

The daily ore report runs via Windows Task Scheduler (`\WoW\DailyOreReport`) and sends through Outlook desktop.

**Requirements:**
- Python 3.10+ with `requests`, `beautifulsoup4`, `pywin32`
- Outlook desktop (Classic) signed in
- Task Scheduler entry pointing to `scripts/daily_ore_email.py`

```bash
pip install requests beautifulsoup4 pywin32
```

**Configuration** (top of `scripts/daily_ore_email.py`):
- `REALM` — default `us/area-52`, change to your realm
- `EMAIL_TO` — recipient email address
