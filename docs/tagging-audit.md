# QA Audit: Tagged Ads sheet

**Status:** Review complete, corrections not yet applied.
**Owner:** Jessica Smith.
**Reviewed:** Aug 12, 2026, against the 101-ad run at `b9ded61`.
**Subject:** `output/messaging_matrix.xlsx` — 101 ads, 12 brands, 8 themes, 8 audiences, 3 ad types.

## How to read this

Row numbers are spreadsheet rows on the Tagged Ads sheet. Corrections go into `data/tags.json`, not the input CSV — tags are frozen by ad hash, so an edit there survives every future rebuild and no rerun is needed. Each finding below gives the key to edit.

Both matrix sheets were recomputed from the Tagged Ads rows and reconcile exactly. The arithmetic is correct. Everything below is a tagging judgment.

| Category | Count |
|---|---|
| Ads with an explicit offer but no Price / Value theme | 18 |
| Community / Belonging tags that are wrong in one direction or the other | 9 |
| Proof entries that are descriptors rather than evidence | 14 ads |
| Audience errors | 4 |
| Ad-type misclassifications affecting `--brand-only` | 4 |
| Ads with no themes at all | 2 |

## 1. Community / Belonging is mismeasured, and it is the headline

The Findings sheet names community as the primary whitespace: "only Gymshark (3), Alo (1) and Tracksmith (1) make any belonging claim." That count is wrong in both directions.

**Tagged as Community when the copy does not support it:**

- **Row 33, Tracksmith** — "Crafted For The Pursuit Of Personal Excellence." An individual-achievement line, not a belonging claim. This is Tracksmith's only Community tag and the sole basis for its 25% cell.
- **Row 84, Alo Yoga** — "Celeb-approved tennis skirts, trending for playful, empowered energy." Trend and endorsement language, not community. Alo's only Community tag.

**Not tagged as Community when the ad names an actual programme:**

- **Row 85, Alo Yoga** — "Join ALO Access." A named membership programme, tagged `Style / Design, Versatility / Gym-to-street` only. Key `ec210ab225cfaab7`.
- **Row 68, Gymshark** — "We'll guide you through every step with an 8-week couch-to-5k training plan, tips from those who've done it, and advice from a coach." Tagged `Innovation / New technology` and nothing else. A coached training programme is not new technology. Key `0701576ef5018959`.
- **Row 69, Gymshark** — "training tips and advice from a Running Coach." Tagged Performance and Versatility, no Community.
- **Row 22, Under Armour** — "Join UA Rewards."
- **Row 59, Nike** — "Free Delivery For Members. Become A Nike Member."

This matters more than any other finding here, because the commit that produced this run (`fd4dd4b`) states in its own message that depth surfaced "Alo's ALO Access membership, and Gymshark's couch-to-5K and half-marathon coaching content — all community or sustainability positions the thin sample missed." Those ads were collected. The tagger did not encode them. The narrative and the data disagree, and the matrix is what the presentation will show.

Corrected, Gymshark goes to roughly 5 of 10 ads, Alo to 2 of 9, Nike and Under Armour enter the column, and Tracksmith leaves it. Community stops being the thinnest theme, which removes the load-bearing support from the whitespace recommendation.

## 2. Price / Value is missing from 18 ads that carry an explicit offer

Scanning the copy for discount, percentage, price and instalment language finds 18 ads with an offer and no `Price / Value` theme:

| Rows | Brand | Offer in the copy |
|---|---|---|
| 21, 22, 89, 90 | Under Armour | "30-50% Off Sitewide", "25% Off BTS Gear", "Up To 50% Off", "40% Off Winter Picks" |
| 62, 63, 65 | Vuori | "Sign Up and Get 20% Off" (three separate ads) |
| 34, 35, 36 | Tracksmith | "from $54.00", "Free Shipping On Orders Over $150", "20% Off Your First Order" |
| 32 | Patagonia | "Up to 40% Off" |
| 37 | New Balance | "Up to 30% Off… 25% Off Select Shoes" |
| 82 | On | "save up to 40%" |
| 5 | lululemon | "We Made Too Much" |
| 15, 16 | Vuori | "Free Shipping On Orders $75+" |
| 69, 73 | Gymshark | "Student Discount", "Pay in 4 Installments" |

This is not a missing rule — rows 41, 42, 43, 44, 45, 46, 58, 74, 75, 79, 88, 92 and 93 all received `Price / Value` correctly. It is applied inconsistently.

Two consequences for the matrix as printed:

- **Vuori and New Balance and Patagonia and Tracksmith all show an empty Price / Value cell.** Vuori runs a 20%-off acquisition offer in at least three of its ten ads and reads as a full-price brand.
- **The Findings sheet's commercial argument is not supported by its own matrix.** It states that undifferentiated claims "force competition on discount depth, which is exactly where Under Armour, Fabletics and New Balance already live." New Balance's Price / Value cell is blank, and Under Armour's shows 29% off seven ads while four of those seven are discount-led.

**Row 89, Under Armour** is the extreme case: "50% Off UA - Semi-Annual Event… Use Code SUMMER Take Up To 50% Off." It is classified `Promotional` and carries **no themes whatsoever**. Key `86526c39fe15af48`.

## 3. The "39% cite a proof point" headline is inflated

The corrected finding in `fd4dd4b` is that 39% of ads cite a proof point and 61% do not. 39 of 101 ads do have a non-empty proof field, so the arithmetic is right — but 14 of those 39 contain at least one entry that is a product descriptor rather than evidence:

- **Row 97, Arc'teryx** — "Gore-tex Jackets, Insulated Jackets" are sitelink product categories, not proof. Key `dd2d4b9d0fee4226`.
- **Row 77, On** — "New sockliner for easy step-in, Wider opening for better fit, More heel support" are feature descriptions.
- **Row 86, Alo Yoga** — "Performance-Engineered, Yogi-Tested" are marketing claims with no source.
- **Row 2, lululemon** — "Sweat-wicking, Breathable, Anti-stink." Worth noting as a regression: the same ad correctly returned no proof points in the 42-ad run.
- Also rows 34, 42, 45, 61, 62, 66, 74, 79, 84, 102.

Require a rating, review count, percentage, price or explicit guarantee and the figure is **31 of 101, or 31%**. The defensible statement is that roughly a third of ads carry hard proof, not 39%.

## 4. Fabletics: a colour read as an environmental claim

Rows 42 and 102 are two creative variants of the same offer, with identical body copy — "Our scrub sets are breathable, lightweight and wrinkle resistant. $15 for new Fabletics VIPs."

- Row 42's headline reads "**Affordable Green Scrubs**" and is tagged `Sustainability`. Key `f6e6029dab0a8805`.
- Row 102's headline reads "**Purple Scrub Sets In Stock**" and is not.

Same product, same offer, same body text. The only difference is the colour word in the headline. This is conclusive: the tagger read "Green" as an environmental claim. Fabletics' 25% Sustainability cell rests entirely on it and should be zero.

There is a second problem in the same place. Fabletics has only four ads and two of them are this one scrub promotion. Now that cells are percentages of a brand's own ads, a duplicated creative moves that brand's row by 25 points per copy. `validate()` dedupes only on exact competitor-plus-text matches, so near-identical creative variants pass through. Fabletics' 100% Price / Value and 100% Comfort cells should be read with that in mind.

## 5. Audience errors

- **Row 9, Nike — soccer jerseys tagged `Runners`.** Carried over from the 42-ad run and still present. The ad is "Gear Up For Soccer"; the tagger appears to be reading the model-extension list, where Pegasus and Vaporfly are running shoes. Key `ef53e1b3595fa0b6`.
- **Row 20, On — tagged `Everyday / athleisure, Gym & strength training`.** The copy is "superior comfort, cushioning and stability" from a running brand. There is no gym signal, and `Runners` is absent. Key `15701209a218b764`.
- **Row 60, Nike — "Kids Giannis Antetokounmpo Shoes" tagged `Men, Gym & strength training`.** A children's basketball shoe. Key `9f62c49823ff799d`.
- **Row 96, Arc'teryx — tagged `Runners`.** The copy covers "Skiing and Snowboarding. Men's Climbing Clothes and Accessories." Key `47400b92afafe9cb`.

## 6. Theme over-tagging

- **Row 79, On** carries seven of the eight available themes on a single ad. `Sustainability` comes from "last season: last chance for pieces from previous seasons," which is clearance, not circularity; `Style / Design` has no supporting language. Key `415a6402e534a5df`.
- **Row 13, Vuori** takes five themes and five audiences off two sentences of positioning copy. `Innovation / New technology` comes from the phrase "A New Perspective."
- **Row 32, Patagonia** — a pure sale ad ("Up to 40% Off. Select Styles Are Now On Sale") is tagged `Versatility / Gym-to-street` and nothing else. Both wrong: no versatility claim, and the missing theme is Price / Value. Key `70e27aafa53a7e7f`.
- **Row 96, Arc'teryx** — `Versatility / Gym-to-street` on climbing and ski gear.
- **Rows 15 and 16, Vuori** have near-identical copy and both classify as `Brand`, but row 15 is tagged Performance, Style and Versatility while row 16 is tagged Comfort alone. One of the two is wrong regardless of which reading you prefer.

## 7. Ad-type misclassification, which corrupts `--brand-only`

Only 16 of 101 ads classify as `Brand`, so each error moves that subset by roughly six points. `--brand-only` is offered as the answer to the objection that search copy is not where positioning lives, which makes this column load-bearing.

- **Row 8, Nike — "Golf Gloves and Mitts" classified `Brand`.** It is a product ad for gloves. Key `089fe0b44ff08b3f`.
- **Rows 68 and 69, Gymshark** — coach-led training content classified `Product`. These are the clearest brand-level ads Gymshark runs and they are excluded from brand-only mode.
- **Row 12, Alo Yoga** — a local storefront listing classified `Brand`.

## 8. Two ads carry no themes

- **Row 12, Alo Yoga** — "ALO. Clothing store. Open now. Call or get Directions." Correctly blank; a storefront listing carries no message. Noting it so the blank is not mistaken for a bug.
- **Row 89, Under Armour** — a 50%-off ad, blank in error. See section 2.

## 9. The CATEGORY % row is still blank

Both matrix sheets write the CATEGORY row as a live formula with no cached value. Excel fills it on open, but anything reading the file without recalculating — Numbers preview, Google Sheets import, openpyxl — sees an empty row. If the deck is built from a screenshot or an export rather than from Excel itself, the category weighting will be missing.

## What changed since the 42-ad audit

The previous pass reviewed the superseded 42-ad run. Freezing tags in `data/tags.json` resolved the reproducibility problem it raised — corrections now persist and mis-tags no longer re-roll between runs. Six of its thirteen findings were resolved in the rebuild; seven reproduced and are restated above with current row numbers.

The trade is that mis-tags are now durable in the other direction too. Everything in this document is frozen in `tags.json` and will appear in every future rebuild, including `--brand-only`, until the entries are edited.

## Recommended prompt changes

Correcting the entries above fixes this run. These three changes reduce the same errors recurring on the next batch of ads:

1. **Require a quote per theme.** Have the tagger return the phrase that triggered each theme. A theme it cannot quote for is an over-tag, and this is the single highest-leverage change — it addresses sections 1, 3 and 6 at once.
2. **Give Price / Value an explicit trigger list.** Any percentage off, price point, code, instalment plan or free-shipping threshold sets the theme. Section 2 is 18 ads and is the largest single defect in the sheet.
3. **Separate proof from description.** State that a proof point must contain a number, a named third party, or a stated guarantee, and that fabric and feature adjectives are not proof. This is what makes the headline proof statistic trustworthy.

One judgment call is outstanding for the owner rather than the tool. Audience is multi-select, so a single ad can add to five audience columns and the Audience Matrix totals exceed the ad count. Combined with per-brand normalization, a brand whose ads are tagged generously reads as covering more of the market than one tagged tightly, independent of what its ads actually say.
