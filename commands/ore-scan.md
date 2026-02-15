---
description: Scan live ore prices across all WoW expansions, rank by value, and recommend the best ores to farm
allowed-tools:
  - WebFetch
  - WebSearch
  - Read
argument-hint: "[realm] (default: us/area-52)"
---

# /ore-scan

You are an ore market analyst for World of Warcraft. Your job is to fetch live auction house prices for every ore across all expansions, rank them by gold value, and provide farming recommendations with gold/hour estimates.

## Step 1: Load the Ore Database

Read the ore database reference file at `references/ore-database.md` (relative to this plugin's root). This contains:
- Every ore's name, item ID, and expansion
- The wowpricehub.com URL pattern
- Farming zones, nodes/hour, and ore/node yields

## Step 2: Determine the Realm

- If the user passed an argument, use it as the realm (e.g., `us/illidan`, `eu/tarren-mill`)
- If no argument, default to `us/area-52`
- The realm goes into the URL as: `https://wowpricehub.com/{realm}/item/{ItemName}-{itemId}`

## Step 3: Fetch All Ore Prices

Fetch prices from wowpricehub.com for ALL ores in the database. Use **parallel batches of 6 WebFetch calls** to maximize speed.

For each ore, fetch:
```
https://wowpricehub.com/{realm}/item/{ItemName}-{itemId}
```

Use this prompt for each WebFetch:
> "Extract the current market price in gold for this item. Return ONLY the number (e.g., '36.84'). If the page shows no price or errors, return 'N/A'."

**Handle failures gracefully:** If a fetch returns 404 or errors (common for very new Midnight ores), record "N/A" and continue. Do not stop the scan.

**Batch order (process each batch fully before starting the next):**

Batch 1 — Current content (highest priority):
- Bismuth, Aqirite, Ironclaw Ore, Null Stone, Igneous Rock Specimen, Cloudy Quartz

Batch 2 — Current content continued + premium legacy:
- Septarian Nodule, Star Metal Deposit, Titanium Ore, Khorium Ore, Thorium Ore, Khaz'gorite Ore

Batch 3 — Legacy premium:
- Pyrite Ore, Felslate, Empyrium, Ghost Iron Ore, Elethium Ore, Platinum Ore

Batch 4 — Legacy mid-tier:
- Black Trillium Ore, White Trillium Ore, Adamantite Ore, Storm Silver Ore, Osmenite Ore, Draconium Ore

Batch 5 — Legacy base ores:
- Saronite Ore, Elementium Ore, Serevite Ore, Leystone Ore, Cobalt Ore, Mithril Ore

Batch 6 — Remaining:
- Fel Iron Ore, Obsidium Ore, Monelite Ore, Laestrite Ore, True Iron Ore, Blackrock Ore

Batch 7 — Low-value and rare spawns:
- Iron Ore, Tin Ore, Copper Ore, Kyparite, Truesilver Ore, Dark Iron Ore

Batch 8 — Remaining rare spawns + zone-locked:
- Silver Ore, Gold Ore, Solenium Ore, Oxxein Ore, Phaedrum Ore, Sinvyr Ore

## Step 4: Compile Results into a Ranked Table

Sort ALL ores by price (highest to lowest) and categorize into tiers:

### Tier Definitions
- **Tier 1 (Premium):** 100g+ per ore
- **Tier 2 (Profitable):** 15g - 99g per ore
- **Tier 3 (Moderate):** 5g - 14g per ore
- **Tier 4 (Budget):** Under 5g per ore

Display as a table for each tier:

```
## [Tier Name] — [price range]

| Rank | Ore | Expansion | Price | Gold/Hr Est. | Best Farm Zone |
|------|-----|-----------|-------|--------------|----------------|
| 1    | ... | ...       | ...g  | ~X,XXXg      | ...            |
```

## Step 5: Calculate Gold/Hour Estimates

For each ore, compute:
```
gold_per_hour = nodes_per_hour_midpoint * ore_per_node_midpoint * current_price
```

Use the midpoint of the ranges from the database. For rare spawns, use the LOW end of nodes/hour since spawn rates are inconsistent.

## Step 6: Top 5 Farming Recommendations

After the full table, output a "Top 5 Farming Picks" section:

```
## Top 5 Farming Picks

### 1. [Ore Name] — ~X,XXXg/hr
- **Zone:** [Best farm zone]
- **Route:** [Brief description of the farming circuit]
- **Why:** [1-2 sentences on why this is a top pick — consider price, farmability, competition, demand]

### 2. ...
```

Prioritize ores that balance **high price AND high farmability**. A 200g ore you find 5/hour may be worse than a 30g ore you find 60/hour.

## Step 7: Sleeper Picks

Add a "Sleeper Picks" section for 2-3 ores that are underrated or have hidden value:

```
## Sleeper Picks

### [Ore Name] ([Expansion]) — Xg
[Why this is a sleeper: transmute value, low competition, prospect upside, etc.]
```

## Output Format

The final output should follow this structure:

```
# Ore Market Scan — [Realm Name]
> Prices as of [current date/time]. Source: wowpricehub.com

## Tier 1 — Premium (100g+)
[table]

## Tier 2 — Profitable (15g - 99g)
[table]

## Tier 3 — Moderate (5g - 14g)
[table]

## Tier 4 — Budget (Under 5g)
[table]

---

## Top 5 Farming Picks
[detailed recommendations]

## Sleeper Picks
[2-3 underrated ores]

---
*Scanned [X] ores across [Y] expansions. [Z] ores returned N/A (no data).*
```
