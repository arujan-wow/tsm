#!/usr/bin/env python3
"""Daily WoW Report — fetches live ore & herb prices from wowpricehub.com and emails a styled report via Outlook."""

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
ORE_DB_PATH = REPO_ROOT / "references" / "ore-database.md"
HERB_DB_PATH = REPO_ROOT / "references" / "herb-database.md"
REALM = "us/area-52"
REALM_DISPLAY = "US — Area 52"
EMAIL_TO = "ian@herzingsmartsheet.consulting"
HEADER_IMG = "https://raw.githubusercontent.com/arujan-wow/tsm/main/assets/header-banner.jpg"
MAX_WORKERS = 6

# ---------------------------------------------------------------------------
# Parse item database (works for both ore-database.md and herb-database.md)
# ---------------------------------------------------------------------------
def parse_item_database(filepath):
    """Parse a markdown item database into a list of item dicts.
    Works for both ores and herbs — same table format."""
    text = filepath.read_text(encoding="utf-8")
    items = []
    current_expansion = ""

    # Match expansion headings (## Classic, ## The Burning Crusade, etc.)
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Track expansion headings
        if line.startswith("## ") and not line.startswith("## URL") and not line.startswith("## Quick") and not line.startswith("## Gold"):
            current_expansion = line[3:].strip()
            # Shorten display names
            exp_map = {
                "Classic": "Classic",
                "The Burning Crusade": "TBC",
                "Wrath of the Lich King": "WotLK",
                "Cataclysm": "Cata",
                "Mists of Pandaria": "MoP",
                "Warlords of Draenor": "WoD",
                "Legion": "Legion",
                "Battle for Azeroth": "BFA",
                "Shadowlands": "SL",
                "Dragonflight": "DF",
                "The War Within": "TWW",
                "Midnight (NEW)": "Midnight",
            }
            current_expansion = exp_map.get(current_expansion, current_expansion)

        # Parse table rows (skip header and separator rows)
        if line.startswith("|") and not line.startswith("| Ore") and not line.startswith("| Herb") and not line.startswith("|--"):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 6 and current_expansion:
                name = cols[0]
                try:
                    item_id = int(cols[1])
                except ValueError:
                    i += 1
                    continue
                zone = cols[2]
                # Parse ranges like "50-70" → midpoint
                nodes_hr = _parse_range(cols[3])
                yield_per_node = _parse_range(cols[4])
                notes = cols[5] if len(cols) > 5 else ""
                if nodes_hr and yield_per_node:
                    items.append({
                        "name": name,
                        "id": item_id,
                        "expansion": current_expansion,
                        "zone": zone,
                        "nodes_hr": nodes_hr,
                        "ore_node": yield_per_node,
                        "notes": notes,
                    })
        i += 1

    return items


def _parse_range(text):
    """Parse '50-70' → 60.0, or '8' → 8.0."""
    m = re.match(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", text.strip())
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2
    m2 = re.match(r"(\d+(?:\.\d+)?)", text.strip())
    if m2:
        return float(m2.group(1))
    return None


# ---------------------------------------------------------------------------
# Price fetching
# ---------------------------------------------------------------------------
def fetch_price(item, realm):
    """Fetch current price from wowpricehub.com. Returns float or None."""
    url = f"https://wowpricehub.com/{realm}/item/{item['name']}-{item['id']}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")

        # Strategy 1: JSON-LD structured data
        ld = soup.find("script", type="application/ld+json")
        if ld and ld.string:
            try:
                data = json.loads(ld.string)
                price_str = data.get("offers", {}).get("price", "")
                pm = re.search(r"[\d,.]+", str(price_str))
                if pm:
                    return float(pm.group().replace(",", ""))
            except (json.JSONDecodeError, ValueError):
                pass

        # Strategy 2: meta description
        meta = soup.find("meta", attrs={"name": "description"})
        if meta:
            content = meta.get("content", "")
            pm = re.search(r"(?:Current price|Market value)[:\s]*([\d,.]+)\s*gold", content, re.I)
            if pm:
                return float(pm.group(1).replace(",", ""))

        # Strategy 3: regex scan of full page text
        text = soup.get_text(" ", strip=True)
        # Look for patterns like "36.84 gold" near "Market Value" or "Current"
        pm = re.search(r"(?:market value|current)[^\d]{0,30}([\d,.]+)\s*(?:gold|g)", text, re.I)
        if pm:
            return float(pm.group(1).replace(",", ""))

        return None
    except Exception:
        return None


def fetch_token_price():
    """Fetch current WoW Token price and 24h change from wowtoken.app JSON API.
    Returns dict with keys: price, change, change_pct, or None on failure."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
    }
    try:
        # Get current price
        resp = requests.get("https://data.wowtoken.app/token/current.json", headers=headers, timeout=15)
        if resp.status_code != 200:
            return None
        current = resp.json()
        price = current.get("price_data", {}).get("us")
        if not price:
            return None

        # Get 24h history to compute change
        change = None
        change_pct = None
        try:
            hist_resp = requests.get("https://data.wowtoken.app/token/history/us/24h.json", headers=headers, timeout=15)
            if hist_resp.status_code == 200:
                history = hist_resp.json()
                if history and len(history) > 0:
                    oldest_price = history[0].get("value")
                    if oldest_price:
                        change = price - oldest_price
                        change_pct = round((change / oldest_price) * 100, 2)
        except Exception:
            pass  # Change data is optional — price alone is still useful

        return {"price": price, "change": change, "change_pct": change_pct}
    except Exception:
        return None


def fetch_all_prices(items, realm):
    """Fetch prices for all items in parallel. Returns list of result dicts."""
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        future_map = {pool.submit(fetch_price, item, realm): item for item in items}
        for future in as_completed(future_map):
            item = future_map[future]
            try:
                price = future.result()
            except Exception:
                price = None
            if price is not None and price > 0:
                gold_hr = item["nodes_hr"] * item["ore_node"] * price
                results.append({**item, "price": price, "gold_hr": gold_hr})

    results.sort(key=lambda x: x["price"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# HTML email generation
# ---------------------------------------------------------------------------
TSM_COLORS = {
    "body_bg": "#0a1628",
    "container_bg": "#132238",
    "card_bg": "#1a3050",
    "accent": "#4db8ff",
    "gold": "#ffd100",
    "text": "#c7d5e0",
    "bright": "#ffffff",
    "muted": "#6b8299",
    "tier1": "#ff6b6b",
    "tier2": "#ffa726",
    "tier3": "#66bb6a",
    "tier4": "#78909c",
    "row_alt": "#162a42",
    "herb_accent": "#66bb6a",
}
C = TSM_COLORS


def _tier_color(price):
    if price >= 100:
        return C["tier1"]
    if price >= 15:
        return C["tier2"]
    if price >= 5:
        return C["tier3"]
    return C["tier4"]


def _tier_label(price):
    if price >= 100:
        return "Premium", "100g+"
    if price >= 15:
        return "Profitable", "15 – 99g"
    if price >= 5:
        return "Moderate", "5 – 14g"
    return "Budget", "Under 5g"


def _format_gold(val):
    if val >= 1000:
        return f"{val:,.0f}g"
    return f"{val:,.2f}g"


def _reasoning(item):
    """Generate a short reasoning blurb explaining the gold/hr math and trade-offs."""
    nodes = item["nodes_hr"]
    ore = item["ore_node"]
    price = item["price"]
    gold_hr = item["gold_hr"]

    # Density assessment
    if nodes >= 50:
        density = "very dense spawns"
    elif nodes >= 25:
        density = "moderate spawns"
    elif nodes >= 10:
        density = "sparse spawns"
    else:
        density = "rare spawn"

    # Build the math string
    math = f"{nodes:.0f} nodes/hr x {ore:.1f} ore/node x {_format_gold(price)}"

    # Trade-off insight
    if price >= 100 and nodes < 15:
        insight = "High unit price but rare — patient farmers only."
    elif price >= 100:
        insight = "Premium price with solid density. Top shelf."
    elif gold_hr >= 4000:
        insight = "Volume play — massive spawns offset lower price."
    elif gold_hr >= 2000:
        insight = "Strong balance of price and farmability."
    elif nodes < 15:
        insight = "Niche — grab when you see it, don't dedicate a session."
    elif price < 5:
        insight = "Low value per unit. Only worth it in bulk."
    else:
        insight = "Solid mid-tier pick for steady income."

    return f"{math} = ~{_format_gold(gold_hr)}/hr. {insight}"


def _tier_rows(items, tier_num):
    """Generate table rows for a tier."""
    rows = ""
    for idx, item in enumerate(items):
        bg = C["row_alt"] if idx % 2 == 0 else C["card_bg"]
        tc = _tier_color(item["price"])
        reason = _reasoning(item)
        rows += f"""<tr style="background:{bg};">
  <td style="padding:10px 14px;color:{C['muted']};font-size:13px;">{idx + 1}</td>
  <td style="padding:10px 14px;color:{C['bright']};font-weight:600;">{item['name']}</td>
  <td style="padding:10px 14px;color:{C['muted']};font-size:13px;">{item['expansion']}</td>
  <td style="padding:10px 14px;color:{C['gold']};font-weight:700;font-size:15px;">{_format_gold(item['price'])}</td>
  <td style="padding:10px 14px;color:{C['accent']};font-weight:600;">~{_format_gold(item['gold_hr'])}/hr</td>
  <td style="padding:10px 14px;color:{C['text']};font-size:13px;">{item['zone']}</td>
  <td style="padding:10px 14px;color:{C['muted']};font-size:12px;line-height:1.4;max-width:200px;">{reason}</td>
</tr>\n"""
    return rows


def _tier_section(label, price_range, color, items, item_label="Ore"):
    if not items:
        return ""
    return f"""
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
  <tr><td style="padding:12px 16px;background:{color};border-radius:8px 8px 0 0;">
    <span style="color:{C['bright']};font-weight:700;font-size:16px;font-family:'Cinzel',Georgia,serif;">{label}</span>
    <span style="color:{C['text']};font-size:13px;margin-left:8px;font-family:'Cinzel',Georgia,serif;">({price_range})</span>
  </td></tr>
  <tr><td style="padding:0;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:{C['card_bg']};border-radius:0 0 8px 8px;">
      <tr style="background:{C['body_bg']};">
        <th style="padding:8px 14px;color:{C['muted']};font-size:12px;text-align:left;font-weight:400;">#</th>
        <th style="padding:8px 14px;color:{C['muted']};font-size:12px;text-align:left;font-weight:400;">{item_label}</th>
        <th style="padding:8px 14px;color:{C['muted']};font-size:12px;text-align:left;font-weight:400;">Xpac</th>
        <th style="padding:8px 14px;color:{C['muted']};font-size:12px;text-align:left;font-weight:400;">Price</th>
        <th style="padding:8px 14px;color:{C['muted']};font-size:12px;text-align:left;font-weight:400;">Gold/Hr</th>
        <th style="padding:8px 14px;color:{C['muted']};font-size:12px;text-align:left;font-weight:400;">Farm Zone</th>
        <th style="padding:8px 14px;color:{C['muted']};font-size:12px;text-align:left;font-weight:400;">Why</th>
      </tr>
      {_tier_rows(items, 0)}
    </table>
  </td></tr>
</table>"""


def _token_price_card(token_data):
    """Generate a WoW Token price card with buy/wait signal."""
    if not token_data:
        return ""
    price = token_data["price"]
    change = token_data.get("change")
    change_pct = token_data.get("change_pct")

    # Buy signal logic (perspective: buying token with USD, selling for gold)
    # Higher gold price = more gold per token = better time to buy
    if change is not None and change_pct is not None:
        if change_pct >= 3:
            signal = "Strong Buy"
            signal_color = "#66bb6a"
            signal_icon = "&#9650;&#9650;"  # ▲▲
            signal_note = f"Up {change_pct:.1f}% in 24h — gold value spiking, great time to buy and sell for gold."
        elif change_pct >= 1:
            signal = "Buy"
            signal_color = "#66bb6a"
            signal_icon = "&#9650;"  # ▲
            signal_note = f"Up {change_pct:.1f}% in 24h — token yields more gold, good time to buy."
        elif change_pct >= 0:
            signal = "Neutral"
            signal_color = C["muted"]
            signal_icon = "&#9644;"  # ▬
            signal_note = "Flat or minor rise — fine to buy, no rush."
        elif change_pct >= -2:
            signal = "Hold"
            signal_color = C["tier2"]
            signal_icon = "&#9660;"  # ▼
            signal_note = f"Down {abs(change_pct):.1f}% in 24h — gold value dipping, consider waiting."
        else:
            signal = "Wait"
            signal_color = C["tier1"]
            signal_icon = "&#9660;&#9660;"  # ▼▼
            signal_note = f"Down {abs(change_pct):.1f}% in 24h — gold value dropping, wait for recovery."

        change_sign = "+" if change > 0 else ""
        change_html = f"""
        <td style="width:12px;"></td>
        <td style="background:{C['body_bg']};border-radius:8px;padding:10px 18px;">
          <p style="color:{C['muted']};font-size:11px;margin:0;">24h Change</p>
          <p style="color:{signal_color};font-size:18px;font-weight:700;margin:2px 0 0 0;">{change_sign}{change:,}g ({change_sign}{change_pct:.1f}%)</p>
        </td>
        <td style="width:12px;"></td>
        <td style="background:{C['body_bg']};border-radius:8px;padding:10px 18px;">
          <p style="color:{C['muted']};font-size:11px;margin:0;">Signal</p>
          <p style="color:{signal_color};font-size:18px;font-weight:700;margin:2px 0 0 0;">{signal_icon} {signal}</p>
        </td>"""
    else:
        change_html = ""
        signal_note = "24h trend data unavailable."

    return f"""
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
  <tr><td style="background:linear-gradient(135deg,#1a3050,#0f3460);border:2px solid {C['gold']};border-radius:12px;padding:24px;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr><td>
        <p style="color:{C['gold']};font-size:12px;text-transform:uppercase;letter-spacing:2px;margin:0 0 4px 0;font-family:'Cinzel',Georgia,serif;">WoW Token — US Region</p>
        <table cellpadding="0" cellspacing="0" style="margin-top:10px;"><tr>
          <td style="background:{C['body_bg']};border-radius:8px;padding:10px 18px;">
            <p style="color:{C['muted']};font-size:11px;margin:0;">Current Price</p>
            <p style="color:{C['gold']};font-size:22px;font-weight:700;margin:2px 0 0 0;">{price:,}g</p>
          </td>
          {change_html}
        </tr></table>
        <p style="color:{C['text']};font-size:13px;margin:14px 0 0 0;line-height:1.5;font-style:italic;">{signal_note}</p>
      </td></tr>
    </table>
  </td></tr>
</table>"""


def _top_pick_card(item, accent=None, label="Top Pick of the Day"):
    ac = accent or C['accent']
    return f"""
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
  <tr><td style="background:linear-gradient(135deg,#1a3050,#0f3460);border:2px solid {ac};border-radius:12px;padding:24px;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td style="vertical-align:top;">
          <p style="color:{ac};font-size:12px;text-transform:uppercase;letter-spacing:2px;margin:0 0 4px 0;font-family:'Cinzel',Georgia,serif;">{label}</p>
          <p style="color:{C['bright']};font-size:28px;font-weight:900;margin:0 0 6px 0;font-family:'Cinzel Decorative','Cinzel',Georgia,serif;">{item['name']}</p>
          <p style="color:{C['muted']};font-size:14px;margin:0 0 16px 0;">{item['expansion']} &middot; {item['zone']}</p>
          <table cellpadding="0" cellspacing="0"><tr>
            <td style="background:{C['body_bg']};border-radius:8px;padding:10px 18px;margin-right:12px;">
              <p style="color:{C['muted']};font-size:11px;margin:0;">Price</p>
              <p style="color:{C['gold']};font-size:22px;font-weight:700;margin:2px 0 0 0;">{_format_gold(item['price'])}</p>
            </td>
            <td style="width:12px;"></td>
            <td style="background:{C['body_bg']};border-radius:8px;padding:10px 18px;">
              <p style="color:{C['muted']};font-size:11px;margin:0;">Est. Gold/Hr</p>
              <p style="color:{ac};font-size:22px;font-weight:700;margin:2px 0 0 0;">~{_format_gold(item['gold_hr'])}</p>
            </td>
          </tr></table>
        </td>
      </tr>
      <tr><td style="padding-top:14px;">
        <p style="color:{ac};font-size:12px;font-weight:600;margin:0 0 4px 0;">The Math</p>
        <p style="color:{C['text']};font-size:13px;margin:0;line-height:1.5;">{item['nodes_hr']:.0f} nodes/hr &times; {item['ore_node']:.1f} yield/node &times; {_format_gold(item['price'])} = <span style="color:{C['gold']};font-weight:700;">~{_format_gold(item['gold_hr'])}/hr</span></p>
        <p style="color:{C['muted']};font-size:12px;margin:6px 0 0 0;font-style:italic;">{item.get('notes', '')}</p>
      </td></tr>
    </table>
  </td></tr>
</table>"""


def _farming_tips(top5, accent=None):
    ac = accent or C['accent']
    tips = ""
    for i, item in enumerate(top5):
        tips += f"""
<tr><td style="padding:14px 16px;background:{C['card_bg'] if i % 2 == 0 else C['row_alt']};border-radius:6px;margin-bottom:8px;">
  <p style="color:{ac};font-size:14px;font-weight:700;margin:0 0 4px 0;">{i+1}. {item['name']} — ~{_format_gold(item['gold_hr'])}/hr</p>
  <p style="color:{C['text']};font-size:13px;margin:0;line-height:1.5;">
    <span style="color:{C['gold']};">Zone:</span> {item['zone']}<br>
    <span style="color:{C['gold']};">Math:</span> {item['nodes_hr']:.0f} nodes/hr &times; {item['ore_node']:.1f} yield/node &times; {_format_gold(item['price'])}<br>
    <span style="color:{C['muted']};font-style:italic;">{_reasoning(item).split('. ', 1)[-1] if '. ' in _reasoning(item) else ''}</span>
  </p>
</td></tr>
<tr><td style="height:6px;"></td></tr>"""
    return tips


def _section_divider(title, accent):
    """Generate a visual section divider between ore and herb blocks."""
    return f"""
<table width="100%" cellpadding="0" cellspacing="0" style="margin:32px 0 24px 0;">
  <tr>
    <td style="border-top:2px solid {accent};padding-top:18px;">
      <p style="color:{accent};font-size:20px;font-weight:900;margin:0;font-family:'Cinzel Decorative','Cinzel',Georgia,serif;letter-spacing:1px;">{title}</p>
    </td>
  </tr>
</table>"""


def _item_section_html(results, accent, item_label, section_title):
    """Generate the full tier tables + top pick + farming tips for a category (ore or herb)."""
    if not results:
        return ""

    tier1 = [r for r in results if r["price"] >= 100]
    tier2 = [r for r in results if 15 <= r["price"] < 100]
    tier3 = [r for r in results if 5 <= r["price"] < 15]
    tier4 = [r for r in results if r["price"] < 5]

    by_gold_hr = sorted(results, key=lambda x: x["gold_hr"], reverse=True)
    top5 = by_gold_hr[:5]
    top_pick = by_gold_hr[0] if by_gold_hr else None

    html = _section_divider(section_title, accent)
    if top_pick:
        html += _top_pick_card(top_pick, accent=accent, label=f"Top {item_label} Pick")
    html += _tier_section("Tier 1 — Premium", "100g+", C['tier1'], tier1, item_label)
    html += _tier_section("Tier 2 — Profitable", "15 – 99g", C['tier2'], tier2, item_label)
    html += _tier_section("Tier 3 — Moderate", "5 – 14g", C['tier3'], tier3, item_label)
    html += _tier_section("Tier 4 — Budget", "Under 5g", C['tier4'], tier4, item_label)
    html += f"""
    <!-- TOP 5 {item_label.upper()} FARMING PICKS -->
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
      <tr><td style="padding:12px 16px;background:{accent};border-radius:8px 8px 0 0;">
        <span style="color:{C['body_bg']};font-weight:700;font-size:16px;font-family:'Cinzel',Georgia,serif;">Top 5 {item_label} Farming Picks (by Gold/Hr)</span>
      </td></tr>
      <tr><td style="padding:8px 0;">
        <table width="100%" cellpadding="0" cellspacing="0">
          {_farming_tips(top5, accent=accent)}
        </table>
      </td></tr>
    </table>"""
    return html


def generate_html(ore_results, date_str, token_data=None, herb_results=None):
    herb_results = herb_results or []

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Cinzel+Decorative:wght@700;900&display=swap" rel="stylesheet">
</head>
<body style="margin:0;padding:0;background:{C['body_bg']};font-family:'Cinzel',Georgia,'Times New Roman',serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:{C['body_bg']};">
<tr><td align="center" style="padding:0;">
<table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;">

  <!-- HEADER BANNER -->
  <tr><td align="center" style="padding:0;margin:0;line-height:0;font-size:0;">
    <img src="{HEADER_IMG}" width="640" align="center" style="width:100%;max-width:640px;height:auto;display:block;border-radius:12px 12px 0 0;margin:0 auto;" alt="Earthen Dwarves Daily WoW Report">
  </td></tr>

  <!-- TITLE BAR -->
  <tr><td style="background:{C['container_bg']};padding:24px 28px 20px 28px;">
    <p style="color:{C['gold']};font-size:28px;font-weight:900;margin:0 0 4px 0;font-family:'Cinzel Decorative','Cinzel',Georgia,serif;letter-spacing:1px;">Daily WoW Report</p>
    <p style="color:{C['muted']};font-size:13px;margin:0;font-family:'Cinzel',Georgia,serif;">{date_str} &middot; {REALM_DISPLAY} &middot; Source: wowpricehub.com</p>
  </td></tr>

  <!-- CONTENT -->
  <tr><td style="background:{C['container_bg']};padding:4px 28px 28px 28px;">

    {_token_price_card(token_data)}

    {_item_section_html(ore_results, C['accent'], "Ore", "Ore Market")}

    {_item_section_html(herb_results, C['herb_accent'], "Herb", "Herb Market")}

  </td></tr>

  <!-- FOOTER -->
  <tr><td style="background:{C['body_bg']};padding:20px 28px;border-top:1px solid {C['card_bg']};">
    <p style="color:{C['muted']};font-size:12px;margin:0;text-align:center;">
      Scanned {len(ore_results)} ores + {len(herb_results)} herbs across all expansions &middot; Prices are snapshots and may fluctuate<br>
      Generated by <span style="color:{C['accent']};">arujan-wow-tsm</span>
    </p>
  </td></tr>

</table>
</td></tr>
</table>
</body></html>"""
    return html


# ---------------------------------------------------------------------------
# Send via Outlook
# ---------------------------------------------------------------------------
def send_via_outlook(html, subject, to_email):
    import win32com.client
    import pythoncom
    pythoncom.CoInitialize()
    outlook = win32com.client.Dispatch("Outlook.Application")
    outlook._FlagAsMethod("CreateItem")
    mail = outlook.CreateItem(0)
    mail.To = to_email
    mail.Subject = subject
    mail.HTMLBody = html
    mail.Send()
    print(f"Email sent to {to_email}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Parsing ore database...")
    ores = parse_item_database(ORE_DB_PATH)
    print(f"Found {len(ores)} ores")

    print("Parsing herb database...")
    herbs = parse_item_database(HERB_DB_PATH)
    print(f"Found {len(herbs)} herbs")

    print(f"Fetching prices from wowpricehub.com ({REALM})...")
    # Fetch ore and herb prices in parallel using separate thread pools
    with ThreadPoolExecutor(max_workers=2) as pool:
        ore_future = pool.submit(fetch_all_prices, ores, REALM)
        herb_future = pool.submit(fetch_all_prices, herbs, REALM)
        ore_results = ore_future.result()
        herb_results = herb_future.result()
    print(f"Got prices for {len(ore_results)}/{len(ores)} ores, {len(herb_results)}/{len(herbs)} herbs")

    if not ore_results and not herb_results:
        print("ERROR: No prices fetched. Check network or wowpricehub availability.")
        sys.exit(1)

    print("Fetching WoW Token price...")
    token_data = fetch_token_price()
    if token_data:
        print(f"WoW Token: {token_data['price']:,}g", end="")
        if token_data.get("change") is not None:
            print(f" ({token_data['change']:+,}g / {token_data['change_pct']:+.1f}%)")
        else:
            print()
    else:
        print("WARNING: Could not fetch WoW Token price (will skip section)")

    date_str = datetime.now().strftime("%B %d, %Y")
    print("Generating email...")
    html = generate_html(ore_results, date_str, token_data, herb_results=herb_results)

    # Also save a local copy for debugging
    out_path = REPO_ROOT / "scripts" / "last_report.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Saved preview to {out_path}")

    subject = f"Daily WoW Report — {date_str}"
    print(f"Sending to {EMAIL_TO}...")
    send_via_outlook(html, subject, EMAIL_TO)
    print("Done!")


if __name__ == "__main__":
    main()
