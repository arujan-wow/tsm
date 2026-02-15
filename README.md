# arujan-wow-tsm

WoW gold-making tools — TSM setup guides, ore price scanning, and farming analysis. Built as a [Claude Code](https://claude.ai/claude-code) plugin.

## Related

- [Midnight TSM Group Setup](https://github.com/MonChiSub/Midnight-TSM_Group_Setup) — Full TSM group import strings for Midnight Jewelcrafting & Mining

## Guides

- **[midnight-jc-mining-setup.md](midnight-jc-mining-setup.md)** — Step-by-step TSM setup for Midnight JC + Mining (groups, operations, import strings)

## Skills

### `/ore-scan [realm]`

Scans live ore prices from [wowpricehub.com](https://wowpricehub.com) across all WoW expansions (Classic through Midnight), ranks them by gold value, and recommends the best ores to farm.

**Usage:**
```
/ore-scan              # defaults to US Area 52
/ore-scan us/illidan   # specify a different realm
/ore-scan eu/tarren-mill
```

**What it does:**
1. Fetches live auction house prices for ~45 ores across 12 expansions
2. Ranks all ores into tiers (Premium 100g+, Profitable 15-99g, Moderate 5-14g, Budget <5g)
3. Calculates estimated gold/hour based on farmability and current prices
4. Provides Top 5 farming recommendations with zones and routes
5. Highlights sleeper picks with hidden value (transmute, prospect upside, low competition)

**Requires:** Claude Code with WebFetch access

## Setup

Clone this repo and add it as a Claude Code plugin:

```bash
git clone https://github.com/arujan-wow/tsm.git arujan-wow-tsm
```

The `.claude-plugin/plugin.json` manifest registers the plugin. The `/ore-scan` command will be available in Claude Code sessions within or referencing this repo.

## Data

- **[references/ore-database.md](references/ore-database.md)** — Complete ore reference with item IDs, farming zones, yield estimates, and wowpricehub URL patterns for all expansions
