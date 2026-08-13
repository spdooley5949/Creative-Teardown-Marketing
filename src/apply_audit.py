"""Apply the PR #10 tagging audit to data/tags.json.

Community ruling (Shane's call, 12 Aug): only named, participatory programmes
count — coached training plans, memberships with content behind them. Loyalty
and shipping perks (UA Rewards, Nike Member) stay out; that boundary is what
separated real belonging from adiClub boilerplate in the five-year set.
"""
import csv, hashlib, json, re, sys

import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMUNITY = "Community / Belonging"
PRICE = "Price / Value"
log = []

def key(c, t):
    return hashlib.sha256(f"{c}\x00{t}".encode("utf-8")).hexdigest()[:16]

rows = list(csv.DictReader(open(f"{BASE}/data/ads.csv")))
byk = {key(r["competitor"], r["ad_text"]): r for r in rows}

def find(sub, brand=None):
    m = [k for k, r in byk.items()
         if sub.lower() in r["ad_text"].lower() and (not brand or r["competitor"] == brand)]
    assert len(m) == 1, f"{sub!r} matched {len(m)} ads: {[byk[k]['ad_text'][:40] for k in m]}"
    return m[0]

doc = json.load(open(f"{BASE}/data/tags.json"))
T = doc["tags"]

def add_theme(k, th, why):
    if th not in T[k]["themes"]:
        T[k]["themes"].append(th)
        log.append(f"+ {th:<28} {byk[k]['competitor']:<13} {why}")

def drop_theme(k, th, why):
    if th in T[k]["themes"]:
        T[k]["themes"].remove(th)
        log.append(f"- {th:<28} {byk[k]['competitor']:<13} {why}")

def set_type(k, ty, why):
    if T[k]["ad_type"] != ty:
        log.append(f"~ ad_type {T[k]['ad_type']}->{ty:<12} {byk[k]['competitor']:<13} {why}")
        T[k]["ad_type"] = ty

def fix_aud(k, remove=(), add=(), why=""):
    for a in remove:
        if a in T[k]["audiences"]:
            T[k]["audiences"].remove(a)
            log.append(f"- aud {a:<26} {byk[k]['competitor']:<13} {why}")
    for a in add:
        if a not in T[k]["audiences"]:
            T[k]["audiences"].append(a)
            log.append(f"+ aud {a:<26} {byk[k]['competitor']:<13} {why}")

# ---- 1. Community: programmes in, non-claims out --------------------------
add_theme(find("Join ALO Access"), COMMUNITY, "named membership programme (audit r85)")
k_c25 = find("couch-to-5k")
add_theme(k_c25, COMMUNITY, "8-week coached programme (audit r68)")
drop_theme(k_c25, "Innovation / New technology", "a coached plan is not new technology")
k_half = find("advice from a Running Coach")
add_theme(k_half, COMMUNITY, "coached content (audit r69)")
drop_theme(find("Stay Ready For Race Day", "Tracksmith"), COMMUNITY,
           "individual achievement, not belonging (audit r33)")
drop_theme(find("empowered energy", "Alo Yoga"), COMMUNITY,
           "trend/celebrity language, not community (audit r84)")
# Deliberately NOT community: UA Rewards, Nike Member — loyalty perks.

# ---- 2. Price / Value trigger rule (audit rec #2) -------------------------
OFFER = re.compile(
    r"\d+% off|save up to \d+%|up to \d+% off|\$\d|code [A-Z]{3,}|pay in 4|"
    r"installment|student discount|free shipping on orders|we made too much|"
    r"\d+%\s*off", re.I)
for k, r in byk.items():
    if OFFER.search(r["ad_text"]):
        add_theme(k, PRICE, f'offer: "{OFFER.search(r["ad_text"]).group(0)[:28]}"')

# ---- 3. Proof: evidence only (audit rec #3) -------------------------------
HARD = re.compile(r"\d|%|\$|guarant", re.I)
dropped = 0
for k, v in T.items():
    keep = [p for p in v["proof_points"] if HARD.search(p)]
    n = len(v["proof_points"]) - len(keep)
    if n:
        dropped += n
        v["proof_points"] = keep
log.append(f". proof: removed {dropped} descriptor entries (no number/price/guarantee)")

# ---- 4. Audiences ---------------------------------------------------------
fix_aud("ef53e1b3595fa0b6", remove=["Runners"], why="soccer jerseys are not runners (audit r9)")
fix_aud("15701209a218b764", remove=["Gym & strength training"], add=["Runners"],
        why="running-shoe copy, no gym signal (audit r20)")
fix_aud("9f62c49823ff799d", remove=["Men", "Gym & strength training"],
        why="kids' basketball shoe (audit r60)")
fix_aud("47400b92afafe9cb", remove=["Runners"], add=["Outdoor & hiking"],
        why="ski/climbing copy (audit r96)")

# ---- 5. Ad types ----------------------------------------------------------
set_type("089fe0b44ff08b3f", "Product", "golf gloves are a product ad (audit r8)")
set_type(k_c25, "Brand", "coached programme is brand-level (audit r68)")
set_type(k_half, "Brand", "coached content is brand-level (audit r69)")
set_type(find("Clothing store. Open now", "Alo Yoga"), "Product",
         "storefront listing is not brand positioning (audit r12)")

# ---- 6. Over-tags ---------------------------------------------------------
drop_theme("415a6402e534a5df", "Sustainability", "clearance is not circularity (audit r79)")
drop_theme("415a6402e534a5df", "Style / Design", "no supporting language (audit r79)")
drop_theme(find("Integration Of Fitness, Surf"), "Innovation / New technology",
           '"A New Perspective" is not technology (audit r13)')
drop_theme("70e27aafa53a7e7f", "Versatility / Gym-to-street",
           "pure sale ad, no versatility claim (audit r32)")
drop_theme("47400b92afafe9cb", "Versatility / Gym-to-street",
           "climbing/ski gear (audit r96)")
drop_theme("f6e6029dab0a8805", "Sustainability",
           'the word "Green" is a colour (audit s4)')

json.dump(doc, open(f"{BASE}/data/tags.json", "w"), indent=1, sort_keys=True)
print(f"{len(log)} corrections applied\n" + "\n".join("  " + l for l in log))

# ---- summary --------------------------------------------------------------
com = [byk[k]["competitor"] for k, v in T.items() if COMMUNITY in v["themes"]]
proof = sum(1 for v in T.values() if v["proof_points"])
types = {}
for v in T.values():
    types[v["ad_type"]] = types.get(v["ad_type"], 0) + 1
print(f"\nCommunity now: {len(com)} ads -> {sorted(set(com))}")
print(f"Ads with hard proof: {proof}/101 = {round(100*proof/101)}%  (no proof: {round(100*(101-proof)/101)}%)")
print(f"Ad types: {types}")
