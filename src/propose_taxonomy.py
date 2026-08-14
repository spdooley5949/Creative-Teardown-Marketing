"""
Draft a starting taxonomy for a category the tool has never seen.

Samples up to 50 ads from a CSV, shows them to Opus, and writes a
config/<slug>.json the matrix can run against. The output is a first draft for
a human to edit, not a finished answer: which claims a category competes on is
a marketing judgment, and the model has only seen the ads.

Usage:
    venv/bin/python src/propose_taxonomy.py data/kits.csv --slug meal_kit
    venv/bin/python src/propose_taxonomy.py data/kits.csv --slug meal_kit \\
        --name "Meal kit delivery" --sample 50 --force

Then read config/meal_kit.json, edit it, and run:
    venv/bin/python src/build_matrix.py data/kits.csv --industry meal_kit

Why the draft deliberately includes themes the ads do NOT use
-------------------------------------------------------------
The point of the matrix is the empty column: the angle nobody is claiming. If
every theme were derived from the ads in front of it, every theme would have at
least one ad by construction and the whitespace column could never be empty.
The analysis would then be structurally incapable of finding its own headline.

So the model is asked for a mix: the claims this category actually makes, plus
standard angles a marketer in this category would recognise but which are absent
from the sample. Each theme is recorded with an `observed` flag saying which it
is, so whoever edits the file can see what is evidence and what is hypothesis.
"""
import argparse
import csv
import json
import os
import sys
from collections import defaultdict

from dotenv import load_dotenv
from anthropic import Anthropic

import taxonomy

MODEL = "claude-opus-5"
DEFAULT_SAMPLE = 50
N_THEMES = 8
N_AUDIENCES = 8

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE, ".env"))
API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    print("No API key found. Paste it into .env, then run check_key.py.")
    raise SystemExit(1)

client = Anthropic(api_key=API_KEY)


def _entry_schema(kind):
    return {
        "type": "array",
        "minItems": kind,
        "maxItems": kind,
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "definition": {"type": "string"},
                "observed": {"type": "boolean"},
            },
            "required": ["name", "definition", "observed"],
            "additionalProperties": False,
        },
    }


PROPOSAL_SCHEMA = {
    "type": "object",
    "properties": {
        "industry": {"type": "string"},
        "themes": _entry_schema(N_THEMES),
        "audiences": _entry_schema(N_AUDIENCES),
        "notes_for_editor": {"type": "string"},
    },
    "required": ["industry", "themes", "audiences", "notes_for_editor"],
    "additionalProperties": False,
}


def sample_ads(rows, limit):
    """Take up to `limit` ads, spread evenly across brands.

    A flat head() would hand back whichever brand happens to sit at the top of
    the sheet, and the taxonomy would be shaped by that one brand's vocabulary.
    Round-robin keeps a 40-ad brand from crowding out a 3-ad one.
    """
    by_brand = defaultdict(list)
    for r in rows:
        text = (r.get("ad_text") or "").strip()
        brand = (r.get("competitor") or "").strip()
        if text and brand:
            by_brand[brand].append(text)

    out = []
    order = sorted(by_brand)
    i = 0
    while len(out) < limit and any(by_brand[b] for b in order):
        b = order[i % len(order)]
        if by_brand[b]:
            out.append((b, by_brand[b].pop(0)))
        i += 1
    return out


def build_prompt(sample, industry_hint):
    lines = [f'{b}: "{t}"' for b, t in sample]
    brands = sorted({b for b, _ in sample})
    named = f"The category is described as: {industry_hint}.\n\n" if industry_hint else ""

    return (
        "You are a marketing strategist setting up a competitive messaging analysis "
        "for a category you are about to study.\n\n"
        + named
        + f"Below are {len(lines)} advertisements from {len(brands)} competitors "
        f"({', '.join(brands)}). Read them and design the two axes of a messaging "
        "matrix for this category.\n\n"
        + "\n".join(lines)
        + "\n\n"
        f"Propose exactly {N_THEMES} claim themes and exactly {N_AUDIENCES} audiences.\n\n"
        "Rules for the themes:\n"
        "- They are what a brand can claim, not what it sells. 'Faster delivery' is a "
        "claim; 'sells running shoes' is not.\n"
        "- They must be mutually distinguishable. A tagger reading one ad has to be "
        "able to decide between them without coin-flipping.\n"
        "- Cover the claims these ads actually make, AND include standard angles a "
        "marketer in this category would recognise that are ABSENT from this sample. "
        "The purpose of the matrix is to find the claim nobody is making, so a "
        "taxonomy drawn only from observed copy would make that impossible to see. "
        "Aim for roughly two to three unobserved angles, and be honest in the "
        "`observed` flag about which are which.\n"
        "- Name them the way a marketer would on a slide: short, concrete, no jargon.\n\n"
        "Rules for the audiences:\n"
        "- Who the copy speaks to, which may be a demographic, a use case, or a "
        "buying situation, whichever this category actually segments on.\n"
        "- Same honesty about `observed`.\n\n"
        "For each entry give a one-sentence definition precise enough that two "
        "different people tagging the same ad would agree.\n\n"
        "In notes_for_editor, say plainly what you were unsure about: which themes "
        "overlap, what a small sample may have hidden, and which calls a human "
        "should make before this is used."
    )


def propose(sample, industry_hint):
    kwargs = dict(
        model=MODEL,
        max_tokens=8000,
        output_config={"format": {"type": "json_schema", "schema": PROPOSAL_SCHEMA}},
        messages=[{"role": "user", "content": build_prompt(sample, industry_hint)}],
    )
    try:
        with client.beta.messages.stream(
            betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs
        ) as stream:
            resp = stream.get_final_message()
    except Exception:
        with client.messages.stream(**kwargs) as stream:
            resp = stream.get_final_message()

    if resp.stop_reason == "refusal":
        print("The model declined to draft a taxonomy for this data.")
        raise SystemExit(1)

    text = next((b.text for b in resp.content if b.type == "text"), None)
    if not text:
        print("Empty response from the model. Try again.")
        raise SystemExit(1)
    return json.loads(text)


def to_config(proposal, slug, ad_types):
    """Flatten the proposal into the shape build_matrix reads.

    `themes` and `audiences` are plain string lists so the matrix code needs no
    special handling; the definitions and observed flags ride along under
    `_notes` for whoever edits the file.
    """
    return {
        "industry": proposal["industry"],
        "themes": [t["name"] for t in proposal["themes"]],
        "audiences": [a["name"] for a in proposal["audiences"]],
        "ad_types": ad_types,
        "_notes": {
            "drafted_by": f"src/propose_taxonomy.py using {MODEL}",
            "review_before_use": (
                "A first draft from the ads alone. Edit the names, merge anything "
                "that overlaps, and check the unobserved themes are angles this "
                "category could plausibly claim rather than ones it cannot."
            ),
            "editor_notes": proposal["notes_for_editor"],
            "themes": {t["name"]: {"definition": t["definition"], "observed": t["observed"]}
                       for t in proposal["themes"]},
            "audiences": {a["name"]: {"definition": a["definition"], "observed": a["observed"]}
                          for a in proposal["audiences"]},
        },
    }


def main():
    p = argparse.ArgumentParser(
        description="Draft a config/<slug>.json taxonomy from a sheet of ads."
    )
    p.add_argument("csv_path", help="CSV of ads with competitor and ad_text columns")
    p.add_argument("--slug", required=True, help="filename to write, e.g. meal_kit")
    p.add_argument("--name", default=None, help="human name for the category")
    p.add_argument("--sample", type=int, default=DEFAULT_SAMPLE,
                   help=f"how many ads to show the model (default {DEFAULT_SAMPLE})")
    p.add_argument("--force", action="store_true", help="overwrite an existing config")
    a = p.parse_args()

    slug = a.slug.strip().replace(" ", "_").replace("-", "_").lower()
    out_path = os.path.join(BASE, "config", slug + ".json")
    if os.path.exists(out_path) and not a.force:
        print(f"config/{slug}.json already exists. Pass --force to overwrite it.")
        raise SystemExit(1)

    csv_path = a.csv_path if os.path.isabs(a.csv_path) else os.path.join(BASE, a.csv_path)
    if not os.path.exists(csv_path):
        print(f"No file at {csv_path}")
        raise SystemExit(1)
    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    missing = [c for c in ("competitor", "ad_text") if not rows or c not in rows[0]]
    if missing:
        print(f"{os.path.basename(csv_path)} needs column(s): {', '.join(missing)}")
        raise SystemExit(1)

    sample = sample_ads(rows, a.sample)
    if not sample:
        print("No usable ads in that sheet.")
        raise SystemExit(1)

    brands = sorted({b for b, _ in sample})
    print(f"Sampled {len(sample)} of {len(rows)} ads across {len(brands)} brands.")
    if len(sample) < 20:
        print("  Note: under 20 ads is thin. The draft will need more editing.")
    print(f"Asking {MODEL} to draft {N_THEMES} themes and {N_AUDIENCES} audiences...\n")

    proposal = propose(sample, a.name)

    # Reuse the default ad types: Brand/Product/Promotional are category-neutral.
    default_types = taxonomy.load(BASE, taxonomy.DEFAULT_SLUG)["ad_types"]
    config = to_config(proposal, slug, default_types)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"Industry: {config['industry']}\n")
    for label, key in (("THEMES", "themes"), ("AUDIENCES", "audiences")):
        print(label)
        for n in config[key]:
            seen = config["_notes"][key][n]["observed"]
            print(f"  {'seen in ads ' if seen else 'NOT in ads '} {n}")
            print(f"                {config['_notes'][key][n]['definition']}")
        print()

    print("Editor notes from the model:")
    print(f"  {proposal['notes_for_editor']}\n")
    print(f"Written to config/{slug}.json")
    print("Read it, edit it, then run:")
    print(f"  venv/bin/python src/build_matrix.py {a.csv_path} --industry {slug}")


if __name__ == "__main__":
    main()
