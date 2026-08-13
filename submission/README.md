# FROZEN — Friday submission

**Do not edit anything in this folder.**

This is the exact state of the deliverable as of **12 August 2026**, frozen so that
work continuing on the rest of the repo can never break what gets presented and
submitted. If something goes wrong upstairs, everything needed is here and needs
no rebuilding.

Also tagged in git as `friday-submission`. To recover the whole repo at this
state: `git checkout friday-submission`.

## What is in here

| File | What it is |
|---|---|
| `Dooley_Creative_Teardown_Findings.pptx` | The 10-slide deck. Fallback if the browser version misbehaves. |
| `live_deck.html` | The interactive presentation. Open in any browser, works offline. |
| `review_page.html` | The findings page shared with the team. Opens offline. |
| `messaging_matrix.xlsx` | The 5-sheet workbook. The analytical deliverable. |
| `messaging_trend.xlsx` | The 1,762-ad historical analysis. |
| `REFLECTION.md` | The write-up of what the process revealed. |
| `ads.csv` | The 101 primary ads, exactly as analysed. |
| `tags.json` | The frozen, audited tags behind every number. |

Both HTML files are fully self-contained. All 101 ads are embedded, so they work
with no internet connection. Double-click either one.

## The numbers this state represents

101 ads, 12 brands, listed 12 August 2026, tags audited by Jessica Smith with 42
corrections applied.

- Performance 59% of ads, Comfort 58%, Versatility 51%, Style 36%
- Price / Value 34%, Innovation 14%, Sustainability 7%, **Community 6%**
- Community is 6 ads: Gymshark 5, Alo Yoga 1. Ten brands at zero.
- 67% of ads carry no hard evidence
- 16 of 101 ads are brand-level
- Replicated against a separate 1,786-ad dataset: community agrees within 0–4 points

## Integrity

Verify nothing has changed by comparing hashes:

```bash
shasum -a 256 submission/* | cut -c1-16
```

| File | Size | SHA-256 (first 16) |
|---|---|---|
| `Dooley_Creative_Teardown_Findings.pptx` | 66,969 bytes | `34850108b7fab201` |
| `REFLECTION.md` | 9,564 bytes | `7ccc1a741e466930` |
| `ads.csv` | 23,633 bytes | `2226ac52c8369bca` |
| `live_deck.html` | 70,733 bytes | `bd424a1a31379612` |
| `messaging_matrix.xlsx` | 28,424 bytes | `3abe26b56c5a8c37` |
| `messaging_trend.xlsx` | 180,188 bytes | `81f324c4d7b07f87` |
| `review_page.html` | 33,733 bytes | `db9ce46165a5407c` |
| `tags.json` | 31,091 bytes | `3606a3962a8b9b10` |

Frozen 12 August 2026.
