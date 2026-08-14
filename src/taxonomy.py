"""
The claim themes, audiences and ad types the matrix is built from.

These used to be three hardcoded lists at the top of build_matrix.py, which tied
the whole tool to fitness apparel. They now live in config/<slug>.json, one file
per industry, chosen at run time:

    venv/bin/python src/build_matrix.py data/ads.csv --industry fitness_apparel
    venv/bin/python src/build_matrix.py data/kits.csv --config config/meal_kit.json

The default is fitness_apparel, so every existing command behaves exactly as it
did before this file existed. Use propose_taxonomy.py to draft a config for a
new industry.

Tags are stored per industry (data/tags.json for the default, data/tags.<slug>.json
for anything else). Two industries can never share a tag file, because a cached
tag is only meaningful against the taxonomy that produced it.
"""
import hashlib
import json
import os

DEFAULT_SLUG = "fitness_apparel"
REQUIRED_KEYS = ("themes", "audiences", "ad_types")


def _config_dir(base):
    return os.path.join(base, "config")


def resolve(argv):
    """Pull --industry <slug> or --config <path> out of a command line.

    Accepts both "--industry x" and "--industry=x". Returns the raw string, or
    None if neither flag is present. Unknown flags are ignored, so this is safe
    to call from any script that imports build_matrix.
    """
    for i, a in enumerate(argv):
        for flag in ("--industry", "--config"):
            if a == flag and i + 1 < len(argv):
                return argv[i + 1]
            if a.startswith(flag + "="):
                return a.split("=", 1)[1]
    return None


def load(base, ref=None):
    """Load a taxonomy by slug or path. Returns a dict with a 'slug' added."""
    ref = ref or DEFAULT_SLUG

    if ref.endswith(".json") or os.sep in ref:
        path = ref if os.path.isabs(ref) else os.path.join(base, ref)
        slug = os.path.splitext(os.path.basename(path))[0]
    else:
        slug = ref
        path = os.path.join(_config_dir(base), slug + ".json")

    if not os.path.exists(path):
        available = sorted(
            os.path.splitext(f)[0]
            for f in os.listdir(_config_dir(base))
            if f.endswith(".json")
        ) if os.path.isdir(_config_dir(base)) else []
        print(f"No taxonomy at {os.path.relpath(path, base)}")
        if available:
            print(f"Available: {', '.join(available)}")
        print("Draft one for a new category with:")
        print("  venv/bin/python src/propose_taxonomy.py data/your_ads.csv --slug your_category")
        raise SystemExit(1)

    with open(path, encoding="utf-8") as fh:
        try:
            tax = json.load(fh)
        except json.JSONDecodeError as exc:
            print(f"{os.path.relpath(path, base)} is not valid JSON: {exc}")
            raise SystemExit(1)

    for k in REQUIRED_KEYS:
        if not tax.get(k) or not isinstance(tax[k], list):
            print(f"{os.path.relpath(path, base)} needs a non-empty '{k}' list.")
            raise SystemExit(1)
        if len(tax[k]) != len(set(tax[k])):
            print(f"{os.path.relpath(path, base)} has duplicate entries in '{k}'.")
            raise SystemExit(1)

    tax["slug"] = slug
    tax.setdefault("industry", slug.replace("_", " ").title())
    return tax


def fingerprint(tax):
    """Short hash of the taxonomy, used to detect a config change under cached tags."""
    payload = json.dumps(
        {k: tax[k] for k in REQUIRED_KEYS}, sort_keys=True, ensure_ascii=False
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def is_default(tax):
    return tax["slug"] == DEFAULT_SLUG


def tags_path(base, tax, stem="tags"):
    """data/tags.json for the default industry, data/tags.<slug>.json otherwise.

    The default keeps its original filename on purpose: data/tags.json is
    committed, is what the published numbers reconcile against, and must not
    move when this feature lands.
    """
    name = f"{stem}.json" if is_default(tax) else f"{stem}.{tax['slug']}.json"
    return os.path.join(base, "data", name)


def output_path(base, tax, stem, ext="xlsx"):
    """output/<stem>.xlsx for the default industry, <stem>_<slug>.xlsx otherwise."""
    name = f"{stem}.{ext}" if is_default(tax) else f"{stem}_{tax['slug']}.{ext}"
    return os.path.join(base, "output", name)
