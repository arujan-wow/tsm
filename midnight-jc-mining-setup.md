# TSM Setup Guide: Midnight Jewelcrafting & Mining

> **How to use this file:** Work through each section in order.
> For each group: Create the group in TSM, then paste the import string.
> For each operation: Create it in TSM, then apply it to the matching group.

---

## STEP 1: CREATE GROUP STRUCTURE

In TSM, open the main window (minimap icon) > Groups tab.
Create this hierarchy:

```
Midnight Gold
├── Mining
│   ├── Raw Ore
│   ├── Midnight Ore & Stone
│   └── Rare Mining Materials
├── Prospecting
│   ├── Uncut Gems - Rare
│   ├── Uncut Gems - Uncommon
│   └── Byproducts
├── Cut Gems
│   ├── Eversong Diamonds (Meta)
│   ├── Stat Gems - Midnight
│   └── Stat Gems - TWW
├── Reagents
│   ├── Core Reagents
│   └── Special Blasphemites
├── Crafted Jewelry
│   ├── Rings & Necklaces
│   └── Jeweler's Settings
└── Profession Gear
    ├── JC Tools & Accessories
    └── Mining Tools & Accessories
```

---

## STEP 2: IMPORT ITEMS INTO EACH GROUP

Select the group in TSM, click Import, paste the string, click Import.
**Do /reload after each import to be safe.**

### Mining > Raw Ore
```
i:210930,i:210934,i:210936,i:210941
```
*(Bismuth, Aqirite, Ironclaw Ore, Null Stone)*

### Mining > Midnight Ore & Stone
```
i:237496,i:237507,i:237506,i:238602
```
*(Igneous Rock Specimen, Cloudy Quartz, Septarian Nodule, Star Metal Deposit)*

### Prospecting > Uncut Gems - Rare
```
i:212495,i:212505,i:212508,i:212511
```
*(Radiant Ruby, Extravagant Emerald, Stunning Sapphire, Ostentatious Onyx)*

### Prospecting > Uncut Gems - Uncommon
```
i:212498
```
*(Ambivalent Amber)*

### Prospecting > Byproducts
```
i:213398,i:213399
```
*(Handful of Pebbles, Glittering Glass)*

### Cut Gems > Eversong Diamonds (Meta)
```
i:240966,i:240971,i:240982
```
*(Powerful Eversong Diamond, Stoic Eversong Diamond, Indecipherable Eversong Diamond)*

### Cut Gems > Stat Gems - Midnight
```
i:240858,i:240878
```
*(Deadly Peridot, Versatile Garnet)*

> **NOTE:** More Midnight gem cuts will appear as you discover recipes in-game.
> Add them to this group as you learn them.

### Cut Gems > Stat Gems - TWW
```
i:213482,i:213509
```
*(Masterful Emerald, Masterful Amber — still relevant for TWW content)*

### Reagents > Core Reagents
```
i:213219,i:213399,i:213398,i:212514
```
*(Crushed Gemstones, Glittering Glass, Handful of Pebbles, Blasphemite)*

### Reagents > Special Blasphemites
```
i:213743,i:213746,i:213740
```
*(Culminating Blasphemite, Elusive Blasphemite, Insightful Blasphemite)*

### Crafted Jewelry > Rings & Necklaces
```
i:215133,i:215134
```
*(Binding of Binding, Fractured Gemstone Locket)*

### Crafted Jewelry > Jeweler's Settings
```
i:213777
```
*(Magnificent Jeweler's Setting — adds sockets, always in demand)*

### Profession Gear > JC Tools & Accessories
```
i:240955,i:240959,i:246526,i:244629,i:244630,i:244814,i:244713,i:244714,i:259181
```
*(Silvermoon Loupes, Sin'dorei Jeweler's Loupes, Mage-Eye Precision Loupes,
Apprentice Jeweler's Apron, Sin'dorei Jeweler's Cover,
Thalassian Gemshaper's Grand Cover, Farstrider Clampers,
Sin'dorei Clampers, Giga-Gem Grippers)*

### Profession Gear > Mining Tools & Accessories
```
i:238010,i:238015,i:246534,i:244715,i:259173,i:244719,i:259175
```
*(Thalassian Pickaxe, Sun-Blessed Pickaxe, Sunforged Pickaxe,
Farstrider Hardhat, Rock Bonkin' Hardhat,
Farstrider Rock Satchel, Heavy-Duty Rock Assister)*

### Rare / Special Materials
```
i:236952,i:238581,i:259198,i:259199,i:238583,i:238584,i:238585
```
*(Mote of Pure Void, Speculative Voidstorm Crystal,
Void-Touched Eversong Diamond Fragments, Harandar Stone Sample,
Poorly Rounded Vial, Shattered Glass, Vintage Soul Gem)*

---

## STEP 3: CREATE OPERATIONS

### OPERATION 1: "Sell Raw Ore" (Auctioning)
**Apply to:** Mining > Raw Ore, Mining > Midnight Ore & Stone

| Setting              | Value                              |
|----------------------|------------------------------------|
| Duration             | 24h                                |
| Min Price            | `max(110%avgbuy, 80%dbmarket)`     |
| Normal Price         | `max(125%avgbuy, 100%dbmarket)`    |
| Max Price            | `200%dbmarket`                     |
| Undercut Amount      | `0c`                               |
| Post Cap             | 20                                 |
| Stack Size           | 200                                |
| When Below Min       | Don't Post                         |
| Cancel Undercut      | Yes                                |

> **Why these strings:** `avgbuy` protects you if you bought ore to flip.
> `dbmarket` keeps you competitive. The `max()` ensures you never sell at a loss.

---

### OPERATION 2: "Sell Uncut Gems" (Auctioning)
**Apply to:** Prospecting > Uncut Gems - Rare, Prospecting > Uncut Gems - Uncommon

| Setting              | Value                              |
|----------------------|------------------------------------|
| Duration             | 12h                                |
| Min Price            | `max(110%avgbuy, 85%dbmarket)`     |
| Normal Price         | `110%dbmarket`                     |
| Max Price            | `300%dbmarket`                     |
| Undercut Amount      | `0c`                               |
| Post Cap             | 10                                 |
| Stack Size           | 1                                  |
| When Below Min       | Don't Post                         |
| Cancel Undercut      | Yes                                |

> 12h duration because this market is competitive. Cancel scan every 1-2 hours
> during peak times (evenings, raid nights).

---

### OPERATION 3: "Sell Cut Gems" (Auctioning)
**Apply to:** Cut Gems (all sub-groups)

| Setting              | Value                                    |
|----------------------|------------------------------------------|
| Duration             | 12h                                      |
| Min Price            | `max(120%crafting, dbmarket)`            |
| Normal Price         | `max(150%crafting, 120%dbmarket)`        |
| Max Price            | `max(300%crafting, 500%dbmarket)`        |
| Undercut Amount      | `0c`                                     |
| Post Cap             | 5                                        |
| Stack Size           | 1                                        |
| When Below Min       | Don't Post                               |
| Cancel Undercut      | Yes                                      |

> **This is your money maker.** The `crafting` source ensures you never sell
> below your material cost. `120%crafting` minimum guarantees 20% profit floor.

---

### OPERATION 4: "Sell Jewelry" (Auctioning)
**Apply to:** Crafted Jewelry (all sub-groups)

| Setting              | Value                              |
|----------------------|------------------------------------|
| Duration             | 24h                                |
| Min Price            | `120%crafting`                     |
| Normal Price         | `200%crafting`                     |
| Max Price            | `500%crafting`                     |
| Undercut Amount      | `0c`                               |
| Post Cap             | 3                                  |
| Stack Size           | 1                                  |
| When Below Min       | Don't Post                         |
| Cancel Undercut      | Yes                                |

---

### OPERATION 5: "Sell Byproducts & Reagents" (Auctioning)
**Apply to:** Prospecting > Byproducts, Reagents (all sub-groups), Rare / Special Materials

| Setting              | Value                              |
|----------------------|------------------------------------|
| Duration             | 24h                                |
| Min Price            | `80%dbmarket`                      |
| Normal Price         | `100%dbmarket`                     |
| Max Price            | `200%dbmarket`                     |
| Undercut Amount      | `0c`                               |
| Post Cap             | 20                                 |
| Stack Size           | 200                                |
| When Below Min       | Don't Post                         |
| Cancel Undercut      | Yes                                |

---

### OPERATION 6: "Sell Profession Gear" (Auctioning)
**Apply to:** Profession Gear (all sub-groups)

| Setting              | Value                              |
|----------------------|------------------------------------|
| Duration             | 24h                                |
| Min Price            | `max(120%crafting, 90%dbmarket)`   |
| Normal Price         | `max(150%crafting, 110%dbmarket)`  |
| Max Price            | `400%dbmarket`                     |
| Undercut Amount      | `0c`                               |
| Post Cap             | 2                                  |
| Stack Size           | 1                                  |
| When Below Min       | Don't Post                         |
| Cancel Undercut      | Yes                                |

---

### OPERATION 7: "Buy Ore to Prospect" (Shopping)
**Apply to:** Mining > Raw Ore

| Setting              | Value                              |
|----------------------|------------------------------------|
| Max Price            | `85%destroy`                       |
| Even Stacks Only     | No                                 |

> `destroy` = TSM's calculated value of what you get from prospecting the ore.
> Buying at 85% means ~10% profit after the 5% AH cut on gems you sell.
>
> **Launch week exception:** You can go up to `95%destroy` in weeks 1-2
> because gem prices are inflated and sell fast.

---

### OPERATION 8: "Snipe Cheap Materials" (Shopping)
**Apply to:** All Mining and Prospecting groups

| Setting              | Value                              |
|----------------------|------------------------------------|
| Max Price            | `70%dbmarket`                      |

> Use this for quick shopping scans to catch underpriced mats.

---

### OPERATION 9: "Craft Cut Gems" (Crafting)
**Apply to:** Cut Gems (all sub-groups)

| Setting              | Value                                           |
|----------------------|-------------------------------------------------|
| Min Restock          | 2                                               |
| Max Restock          | 10                                              |
| Min Profit           | `100g`                                          |
| Craft Value Override | `first(dbminbuyout, dbmarket)`                  |

> TSM will only queue gem cuts that have 100g+ profit. Adjust up/down
> based on your server. High-pop servers: try 50g. Low-pop: try 200g.

---

### OPERATION 10: "Craft Jewelry" (Crafting)
**Apply to:** Crafted Jewelry (all sub-groups)

| Setting              | Value                              |
|----------------------|------------------------------------|
| Min Restock          | 1                                  |
| Max Restock          | 3                                  |
| Min Profit           | `500g`                             |
| Craft Value Override | `first(dbminbuyout, dbmarket)`     |

> Higher min profit because jewelry sells slower. You don't want to tie up
> materials in stock that sits.

---

## STEP 4: ASSIGN OPERATIONS TO GROUPS

| Group                              | Auctioning Op        | Shopping Op           | Crafting Op      |
|------------------------------------|----------------------|-----------------------|------------------|
| Mining > Raw Ore                   | Sell Raw Ore         | Buy Ore to Prospect   | —                |
| Mining > Midnight Ore & Stone      | Sell Raw Ore         | Snipe Cheap Materials | —                |
| Prospecting > Uncut Gems - Rare    | Sell Uncut Gems      | Snipe Cheap Materials | —                |
| Prospecting > Uncut Gems - Uncommon| Sell Uncut Gems      | Snipe Cheap Materials | —                |
| Prospecting > Byproducts           | Sell Byproducts      | —                     | —                |
| Cut Gems > Eversong Diamonds       | Sell Cut Gems        | —                     | Craft Cut Gems   |
| Cut Gems > Stat Gems - Midnight    | Sell Cut Gems        | —                     | Craft Cut Gems   |
| Cut Gems > Stat Gems - TWW         | Sell Cut Gems        | —                     | Craft Cut Gems   |
| Reagents > Core                    | Sell Byproducts      | Snipe Cheap Materials | —                |
| Reagents > Special Blasphemites    | Sell Byproducts      | Snipe Cheap Materials | —                |
| Crafted Jewelry > Rings & Necks    | Sell Jewelry         | —                     | Craft Jewelry    |
| Crafted Jewelry > Settings         | Sell Jewelry         | —                     | Craft Jewelry    |
| Profession Gear > JC Tools         | Sell Profession Gear | —                     | —                |
| Profession Gear > Mining Tools     | Sell Profession Gear | —                     | —                |

---

## DAILY WORKFLOW

### Morning / Login
1. **`/tsm destroy`** — prospect any ore in your bags
2. **Shopping scan** on "Buy Ore to Prospect" — buy anything under 85% destroy
3. **Crafting scan** — queue profitable gem cuts and jewelry
4. **Post scan** — list everything on the AH

### Every 1-2 Hours (During Peak)
5. **Cancel scan** — cancel undercut auctions
6. **Post scan** — relist cancelled items

### Farming Session
7. Mine a route for 30-60 min
8. **Decision point:** Is ore selling for MORE than destroy value?
   - **Yes** → sell raw ore directly
   - **No** → prospect it, cut gems, sell gems
9. Post everything

### Before Logout
10. Final cancel scan + post scan with 24h duration
11. Check TSM Accounting: which items are actually selling?

---

## PRICING QUICK REFERENCE

| Scenario                         | String to Use                        |
|----------------------------------|--------------------------------------|
| Never sell below purchase price  | `max(110%avgbuy, X%dbmarket)`        |
| Never sell below crafting cost   | `max(120%crafting, X%dbmarket)`      |
| Prospecting profitable?          | Buy ore below `85%destroy`           |
| Launch week (aggressive)         | Buy ore below `95%destroy`           |
| Snipe deals                      | `70%dbmarket`                        |
| Only craft fast-sellers          | Override: `first(dbminbuyout, dbmarket)` |

---

## LAUNCH WEEK CHEATSHEET

| Timeframe  | Priority                                                    |
|------------|-------------------------------------------------------------|
| Week 1-2   | Sell EVERYTHING raw. Ore, gems, reagents. Volume over optimization. |
| Week 2-3   | Start prospecting if ore < 95% destroy. Cut high-demand gems.      |
| Week 3-4   | Tighten to 85% destroy. Focus on best-selling gem cuts only.       |
| Month 2+   | Full JC pipeline: prospect → cut → sell. Add jewelry crafting.     |

---

## NOTES

- **TSM Desktop App** must be running to update pricing data. Keep it open.
- **Quality variants:** Midnight uses Silver/Gold quality ranks. TSM handles
  these as separate items. Add quality variants to groups as they appear.
- **Add new items** to groups as you discover Midnight recipes. This covers
  confirmed items but the expansion will have more.
- **Cancel scanning is king** for cut gems. The player on top of the AH
  listing sells the most. Budget 5 min every hour during peak.

---

*Generated 2026-02-12. Update item lists as new Midnight recipes are discovered.*
