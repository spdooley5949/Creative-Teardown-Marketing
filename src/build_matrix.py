"""
Build the competitor messaging matrix from a sheet of ads.

Reads a CSV of collected ads, uses Claude to tag each ad by message theme,
audience, and proof points, then writes a formatted Excel matrix showing what
each competitor claims, how hard they lean on each theme, and where nobody is
playing (the whitespace).

Usage:
    venv/bin/python src/build_matrix.py [path/to/ads.csv]

Default input:  data/sample_ads.csv
Output:         output/messaging_matrix.xlsx
"""
import csv
import json
import os
import sys
from collections import defaultdict

from dotenv import load_dotenv
from anthropic import Anthropic
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# Message themes the matrix tracks. Edit this list to fit your category.
THEMES = [
    "Price / Value",
    "Speed / Efficiency",
    "Ease of Use",
    "Integrations / All-in-one",
    "Trust / Scale",
    "Customer Support",
    "Enterprise / Security",
    "Innovation / AI",
]

MODEL = "claude-haiku-4-5-20251001"

# Resolve paths from the project root, so the script runs from anywhere.
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE, ".env"))
API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    print("No API key found. Paste it into .env, then run check_key.py.")
    raise SystemExit(1)

client = Anthropic(api_key=API_KEY)


def tag_ad(competitor, ad_text):
    """Ask Claude to tag one ad. Returns {themes, audience, proof_points}."""
    prompt = (
        "You are analyzing a competitor's advertisement.\n\n"
        f"Brand: {competitor}\n"
        f'Ad copy: "{ad_text}"\n\n'
        "From this exact list of message themes, choose every one the ad clearly uses:\n"
        f"{THEMES}\n\n"
        "Also identify the primary audience the ad speaks to, and any concrete proof "
        "points it cites (numbers, customer counts, guarantees, awards).\n\n"
        "Reply with ONLY a JSON object, no other text, in this exact shape:\n"
        '{"themes": ["..."], "audience": "...", "proof_points": ["..."]}'
    )
    resp = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}
    data["themes"] = [t for t in data.get("themes", []) if t in THEMES]
    data["audience"] = data.get("audience", "") or ""
    data["proof_points"] = data.get("proof_points", []) or []
    return data


def read_ads(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_workbook(rows, tags):
    """rows: list of ad dicts. tags: parallel list of tag dicts."""
    competitors = sorted({r["competitor"] for r in rows})
    # counts[competitor][theme] = number of that brand's ads using the theme
    counts = defaultdict(lambda: defaultdict(int))
    for r, t in zip(rows, tags):
        for theme in t["themes"]:
            counts[r["competitor"]][theme] += 1

    wb = Workbook()

    # ---- Sheet 1: Messaging Matrix ----
    ws = wb.active
    ws.title = "Messaging Matrix"

    header_fill = PatternFill("solid", fgColor="1F3864")
    header_font = Font(color="FFFFFF", bold=True)
    brand_font = Font(bold=True)
    center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    thin = Side(style="thin", color="BBBBBB")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    whitespace_fill = PatternFill("solid", fgColor="FCE4D6")
    lean_fill = PatternFill("solid", fgColor="DDEBF7")

    # Header row
    ws.cell(row=1, column=1, value="Competitor")
    for j, theme in enumerate(THEMES, start=2):
        ws.cell(row=1, column=j, value=theme)
    for j in range(1, len(THEMES) + 2):
        c = ws.cell(row=1, column=j)
        c.fill = header_fill
        c.font = header_font
        c.alignment = center
        c.border = border

    # Competitor rows
    for i, comp in enumerate(competitors, start=2):
        bc = ws.cell(row=i, column=1, value=comp)
        bc.font = brand_font
        bc.alignment = left
        bc.border = border
        for j, theme in enumerate(THEMES, start=2):
            n = counts[comp][theme]
            c = ws.cell(row=i, column=j, value=(n if n else None))
            c.alignment = center
            c.border = border
            if n:
                c.fill = lean_fill

    # Totals row with live SUM formulas, so the numbers tie out
    total_row = len(competitors) + 2
    tc = ws.cell(row=total_row, column=1, value="TOTAL")
    tc.font = brand_font
    tc.alignment = left
    tc.border = border
    for j in range(2, len(THEMES) + 2):
        col = get_column_letter(j)
        c = ws.cell(row=total_row, column=j)
        c.value = f"=SUM({col}2:{col}{total_row - 1})"
        c.font = brand_font
        c.alignment = center
        c.border = border

    # Highlight whitespace: themes no competitor uses at all
    whitespace = []
    for j, theme in enumerate(THEMES, start=2):
        if sum(counts[comp][theme] for comp in competitors) == 0:
            whitespace.append(theme)
            for i in range(1, total_row + 1):
                ws.cell(row=i, column=j).fill = whitespace_fill

    ws.column_dimensions["A"].width = 16
    for j in range(2, len(THEMES) + 2):
        ws.column_dimensions[get_column_letter(j)].width = 15
    ws.freeze_panes = "B2"

    # Legend / notes below the table
    note_row = total_row + 2
    ws.cell(row=note_row, column=1,
            value="Cell = number of that brand's ads using the theme. "
                  "Blue = a theme in play. Peach columns = whitespace (no competitor is using it).")
    ws.cell(row=note_row, column=1).font = Font(italic=True, color="666666")

    # ---- Sheet 2: Tagged Ads (the detail behind the matrix) ----
    ws2 = wb.create_sheet("Tagged Ads")
    headers = ["Competitor", "Ad copy", "Themes", "Audience", "Proof points", "Format", "First seen"]
    for j, h in enumerate(headers, start=1):
        c = ws2.cell(row=1, column=j, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = center
        c.border = border
    for i, (r, t) in enumerate(zip(rows, tags), start=2):
        vals = [
            r["competitor"],
            r["ad_text"],
            ", ".join(t["themes"]),
            t["audience"],
            ", ".join(t["proof_points"]),
            r.get("format", ""),
            r.get("first_seen", ""),
        ]
        for j, v in enumerate(vals, start=1):
            c = ws2.cell(row=i, column=j, value=v)
            c.alignment = left
            c.border = border
    widths = [16, 55, 28, 26, 30, 10, 12]
    for j, w in enumerate(widths, start=1):
        ws2.column_dimensions[get_column_letter(j)].width = w
    ws2.freeze_panes = "A2"

    return wb, whitespace


def main():
    in_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "data", "sample_ads.csv")
    if not os.path.isabs(in_path):
        in_path = os.path.join(BASE, in_path)
    rows = read_ads(in_path)
    print(f"Read {len(rows)} ads from {os.path.relpath(in_path, BASE)}. Tagging with Claude...")

    tags = []
    for r in rows:
        t = tag_ad(r["competitor"], r["ad_text"])
        tags.append(t)
        print(f"  {r['competitor']}: {', '.join(t['themes']) or '(no clear theme)'}")

    wb, whitespace = build_workbook(rows, tags)
    out_dir = os.path.join(BASE, "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "messaging_matrix.xlsx")
    wb.save(out_path)

    print(f"\nSaved matrix to {os.path.relpath(out_path, BASE)}")
    if whitespace:
        print("Whitespace (no competitor is using these themes):")
        for w in whitespace:
            print(f"  - {w}")
    else:
        print("No whitespace: every theme is used by at least one competitor.")


if __name__ == "__main__":
    main()
