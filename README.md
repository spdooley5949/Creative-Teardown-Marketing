# Creative Teardown

Reads a sheet of competitor ads, classifies every one of them, and produces a
messaging matrix that shows what an entire category is claiming, who it is
talking to, what it offers as evidence, and which territory nobody has taken.

Built for a competitive teardown of fitness apparel. The category is a
configuration choice, not a hard-coded assumption; the tool works on any set of
brands whose ads you can collect.

## Why this exists

Competitors publish their strategy every day in the ads they pay to run. That
signal is public, but it sits scattered across ad libraries in a form nobody
reads as a whole. Teams end up arguing about positioning from memory and
anecdote.

Reading fifty ads one at a time tells you almost nothing. Reading fifty ads as a
grid tells you where the category has converged, which is exactly where paid
media gets expensive and differentiation disappears. The empty columns are worth
more than the full ones.

## What it produces

A five-sheet Excel workbook at `output/messaging_matrix.xlsx`.

| Sheet | What it holds |
|---|---|
| **Findings** | The strategic read in plain English: headline, the whitespace and what to do about it, each brand's positioning and signature proof, the proof points the category leans on, and ranked recommendations. This is the sheet you present. |
| **Messaging Matrix** | Brands down the side, claim themes across the top. Each cell is the percent of that brand's ads using that theme. |
| **Audience Matrix** | Same layout, for who each brand addresses. |
| **Proof Points** | The specific evidence each brand cites: ratings, review counts, guarantees, shipping and return terms, discounts. |
| **Tagged Ads** | Every ad with its type, themes, audiences and proof points. The receipts sheet. Any number in the matrices traces back to specific rows here. |

## How it works

**1. Collect.** Ads are gathered by hand from the Google Ads Transparency
Center, which is public and needs no login, into `data/ads.csv`. Four columns,
spelled exactly: `competitor`, `ad_text`, `format`, `first_seen`. One row per ad.
For the primary dataset, collection is deliberately manual — the tool itself does
not scrape. A second, larger historical dataset was contributed separately and
gathered a different way. See **Datasets and how each was collected** below.

**2. Tag.** Claude Haiku reads each ad and returns its themes, its audiences,
its ad type and any concrete proof points it cites. Tags are written to
`data/tags.json` and reused on later runs (see Reproducibility below).

**3. Assemble.** Counts are rolled into the matrices, Claude Opus reads the
finished matrix and writes the strategic findings, and the workbook is written
out with live Excel formulas in the category row.

## Three design decisions that matter

**Reproducibility.** Language models do not return identical output for identical
input. Two consecutive runs over the same 42 ads once moved 14 tag assignments
and rewrote the headline finding, with one theme swinging between 1, 2 and 3 ads.
Tags are now frozen to `data/tags.json`, keyed by a hash of the ad, and reused on
every later run. The numbers hold still between runs, rebuilding costs no tagging
calls, and a reviewer's correction to a tag survives the next rebuild. Run with
`--retag` to score everything from scratch.

**Normalized cells.** Matrix cells are the percent of each brand's ads, not raw
counts, with the denominator shown in the `Ads` column. Brands are sampled at
different depths — 18 ads for one, 3 for another — and raw counts would rank
brands by how much of them happened to be collected rather than by what they
actually say.

**Ad-type classification.** Search results are dominated by product-feed and
discount ads that say nothing about positioning. Every ad is classified as
**Brand**, **Product** or **Promotional**. In the current dataset only 16 of 101
ads are brand-level, against 62 product and 23 promotional. Running with
`--brand-only` rebuilds the analysis on brand-level copy alone.

## What it can do

- Classify any ad against a configurable set of eight claim themes and eight audiences
- Assign multiple themes and multiple audiences per ad
- Extract concrete proof points as free text, so evidence is comparable across brands
- Flag whitespace automatically: themes and audiences no competitor is using
- Produce reproducible output that does not drift between runs
- Accept human corrections that persist permanently
- Reconcile every matrix figure against the underlying tagged data
- Rebuild in seconds once tags are frozen, at no model cost for tagging

## Configuring it for another category

Edit two lists at the top of `src/build_matrix.py`. They become the matrix
columns.

```python
THEMES = [...]      # the claim types you want to track
AUDIENCES = [...]   # the segments you want to track
```

Change these and delete `data/tags.json`, or run `--retag`, so every ad is
rescored against the new definitions. Leaving stale tags in place while changing
the lists will produce a matrix that silently disagrees with itself.

## Setup

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

Create a `.env` file in the project root with one line:

```
ANTHROPIC_API_KEY=your-key-here
```

`.env` is gitignored and must never be committed. Verify the key with
`venv/bin/python check_key.py`. Get a key at console.anthropic.com.

## Running it

```bash
venv/bin/python src/build_matrix.py data/ads.csv
```

| Flag | Effect |
|---|---|
| `--retag` | Ignore saved tags and rescore every ad. Use after changing themes or audiences. |
| `--brand-only` | Build the matrices from brand-level ads only, excluding product and promotional. |

Output lands at `output/messaging_matrix.xlsx`. GitHub cannot preview Excel in
the browser, so download the file rather than expecting the page to render.

## Datasets and how each was collected

Two datasets sit in this repo. They were gathered by different people using
different methods, and the difference matters when citing either one.

### Primary — `data/ads.csv`

101 ads, 12 brands, collected 12 August 2026 by Shane Dooley.

Gathered by hand from the Google Ads Transparency Center: search each advertiser,
click "See all ads," read the live text ads, transcribe them. No automation, no
scraping, no OCR. Every ad was read by a person before it entered the file.

Current-state snapshot only. `first_seen` holds the collection date, not the true
first-seen date. This is the dataset behind the headline finding.

### Historical — `data/competitor_ads_5yr_v2.csv`

1,786 ads, 8 brands, `first_seen` spanning 2021 to 2026, contributed by
@andrewsilver314-ship-it.

Collected differently: a year-stratified harvest with ad text extracted by OCR
from rendered creatives, assisted by tooling rather than transcribed by hand.
Some brands were dropped because the harvest hit rate limits. This is a different
provenance from the primary set and is documented as such rather than blended
into it.

Two consequences. Occasional OCR artifacts survive in the text ("running-lnspired"
for "inspired"), which is itself evidence the text is genuine extraction rather
than anything generated. And because the sample is year-stratified rather than
random, the brand mix swings hard between years — 2021 is 86% Adidas and Puma —
so **year-over-year trend lines from this data are not valid** and are not
claimed anywhere in this project.

### Why both exist

The historical set is used as corroboration, not as primary evidence. Four brands
appear in both: lululemon, Nike, New Balance and Under Armour. Comparing their
claim profiles across the two datasets is an independent replication check, since
neither collection method or collector influenced the other.

Mean absolute gap across all overlapping brand-theme pairs: **8 percentage
points**. lululemon and New Balance agree within 6, Nike and Under Armour within
10, with the larger gaps concentrated in Comfort and Style where the manual
sample is smallest.

Community and Belonging — the finding the whole analysis rests on — agrees within
**0 to 4 points on all four brands**, and stays at or below 5% of the category in
five of six years across the historical set. The gap is not an artifact of one
sample, one collector, one method, or one month.

## Current dataset

101 ads across 12 fitness apparel brands, collected 12 August 2026.

| Brand | Ads | | Brand | Ads |
|---|---|---|---|---|
| lululemon | 18 | | Nike | 8 |
| On | 12 | | Under Armour | 7 |
| Arc'teryx | 12 | | Tracksmith | 4 |
| Vuori | 10 | | New Balance | 4 |
| Gymshark | 10 | | Fabletics | 4 |
| Alo Yoga | 9 | | Patagonia | 3 |

Headline result: performance appears in 59% of ads and comfort in 58%, with
versatility at 53% — the three claims are near-interchangeable across all twelve
brands. Community and belonging appears in 5%, five ads across three brands, and
is the emptiest column in the set. 61% of ads make a claim with no evidence
attached.

## Limitations

These are real and should be stated whenever the output is presented.

**Source.** Google Ads Transparency Center only. No Meta, TikTok, LinkedIn, or
organic search.

**Provenance differs by dataset.** The 101-ad primary set was transcribed by hand.
The 1,786-ad historical set was harvested with tooling and OCR by a teammate. Do
not describe the whole project as hand-collected. See Datasets above.

**Format.** Text ads only. Most spend in this category goes to video and image
creative, which carries no copy to analyze. This is a teardown of *search
messaging*, not of brand strategy as a whole.

**Sample depth.** Uneven by design, from 18 ads down to 3. Patagonia, Tracksmith,
New Balance and Fabletics are thin because they genuinely run few search text
ads, which has been confirmed rather than assumed. Percentages keep the
comparison valid, but a three-ad brand still carries a wide error bar. Say "of
the ads we sampled."

**Dates.** The `first_seen` column holds the collection date, not the true
first-seen date, which would require opening each ad individually. Do not cite
it.

**No trend claims.** The historical set carries real dates but is year-stratified,
so its brand mix changes sharply year to year. Nothing in this project claims a
year-over-year trend, and any such claim built on this data would be measuring
sample composition rather than category behaviour.

**Tagging.** No human has audited the tags. The tagger is a language model making
judgment calls. The arithmetic reconciles exactly; that is a different claim from
the tags being correct. `data/tags.json` is editable, and corrections there are
permanent.

**A correction worth recording.** An earlier version of this analysis, built on
42 ads, concluded that three brands cited no proof at all. That was false, and it
was a sampling artifact: the Transparency Center shows roughly four ads per
advertiser until you click "See all ads," and those four skew toward product
listings, which do not carry ratings. Collecting the full lists showed all twelve
brands cite proof. Read past the first screen of any source.

## Repo layout

```
data/ads.csv        input: one row per ad, four columns
data/tags.json      frozen tags for the primary set, committed, hand-editable
data/competitor_ads_5yr_v2.csv   historical set, 2021-2026, contributed
data/tags_trend.json             frozen tags for the historical set
src/build_matrix.py the primary tool: current-state matrix
src/trend_analysis.py  the historical analyser, separate tags and output
output/             generated workbook
docs/PRD.md         product requirements
check_key.py        API key check
```

## Contributing

`main` is protected. Changes arrive by pull request; direct pushes and force
pushes are blocked, and the branch cannot be deleted.

If you are collecting ads and do not use git, you do not need to. Attach your CSV
to a comment on your issue, or use **Add file → Upload files** in the browser and
open a pull request from there.
