# Creative Teardown: What We Learned

**Shane Dooley · 12 August 2026**

## Bottom line

We set out to find where a category's messaging is crowded and where it is open.
We found it. The more useful discovery was about the method: the analysis was
never the hard part, the data was, and our first confident answer was wrong
because we did not collect enough of it.

The tool works and the finding holds. What follows is what the process taught us
that the workbook does not show.

---

## What we built

A pipeline that reads competitor ads, classifies each one, and produces a
messaging matrix showing what a category claims, who it addresses, what evidence
it offers, and which territory nobody has taken.

Final dataset: 101 live search ads across 12 fitness apparel brands, collected
from the Google Ads Transparency Center on 12 August 2026.

**The finding.** Performance appears in 59% of ads, comfort in 58%, versatility
in 51%. Across twelve brands the language is close to interchangeable: "buttery
soft," "built to move in," "looks as good as it feels." Community and belonging
appears in 6% of ads — six in total, five of them Gymshark's — and is the
emptiest column in the set. Separately, 67% of ads make a claim with no hard
evidence attached to it. (These are the post-audit numbers; see the section on
the human audit below.)

The recommendation is not "claim community." Gymshark already owns the claim,
carrying it in half its ads through coached couch-to-5K and half-marathon
programmes. The recommendation is that the territory is uncontested — ten brands
have ceded it to one competitor — and nobody, including the owner, attaches a
single participation number to it. A measurable programme beats an unproven
claim, and it is the one move a rival cannot copy by reformulating a fabric.

---

## Six things the process revealed

### 1. The bottleneck was collection, not intelligence

Classifying 101 ads took roughly ninety seconds of model calls. Collecting them
took hours of manual work. Every genuinely hard problem in this project sat on
the input side, and none of them were the part that looked impressive.

This inverts the intuition we started with. We assumed the analysis was the
value and the data was plumbing. The opposite was true.

### 2. Sample depth decided whether the answer was true

Our first pass used 42 ads, two to four per brand. It concluded that three
brands cited no proof at all and that the category's problem was that nobody
substantiates anything.

That was false. The Transparency Center shows roughly four ads per advertiser
until you click "See all ads," and those four skew toward product listings, which
do not carry ratings. The brand-level ads do. Collecting the full lists took the
set to 101 ads and showed that **all twelve brands cite proof**.

Vuori, which we had labelled the worst offender, runs 4.6 from 13,593 reviews and
a 100% product guarantee.

The corrected finding is stronger than the original: 61% of ads cite nothing,
which is a claim about discipline across an entire category rather than three
brands being careless. But we only reached it by going back.

**The lesson is not "collect more data." It is that a shallow sample does not
produce a vague answer, it produces a confident wrong one.** That is far more
dangerous.

### 3. Model output is not reproducible unless you make it so

Running the tool twice on identical data with no code changes moved 14 tag
assignments, swung one theme between 1, 2 and 3 ads, and rewrote the headline
finding entirely.

Nobody can present numbers that change when you press the button twice. We fixed
it by tagging once and freezing the results to a committed file that later runs
read from. Ten lines of code, and it was the most commercially important decision
in the build.

It also made human review worth doing. Before the freeze, any correction a
reviewer made would have been overwritten on the next run.

### 4. Most search advertising is not positioning

Only 16 of 101 ads were brand-level. The other 85 were product listings and
discount offers. "Golf Gloves and Mitts. Nike.com" tells you what Nike bids on,
not what Nike stands for.

Anyone analyzing ad libraries without separating these is measuring keyword
strategy and calling it brand strategy. We added an ad-type classification so the
analysis can be run on brand-level copy alone, and so the limitation is stated
rather than hidden.

### 5. The valuable output was the empty column

Counting what brands say is straightforward. Noticing what none of them say is
harder, and it is the part a spreadsheet of scraped ads will not hand you.

Every recommendation we produced came from absence, not presence.


### 6. A human audit moved the numbers a machine had verified

After the tags were frozen, Jessica Smith read all 101 ads against their tags
(PR #10) and found 42 errors that every one of our automated checks had passed
over — because our checks verified arithmetic, and these were judgment errors.

The catches ranged from systematic to almost comic. Eighteen ads carried an
explicit discount with no price theme, which moved Price / Value from 15% of the
category to 34% and revealed Under Armour running price language in 86% of its
ads. Fourteen "proof points" were fabric adjectives rather than evidence, which
took the honest proof figure from 39% to 33%. And Fabletics' entire
sustainability score rested on one ad headlined "Affordable **Green** Scrubs" —
the identical ad in purple was not tagged. The model had read a colour as an
environmental claim.

The headline itself was mistagged in both directions: Tracksmith's "pursuit of
personal excellence" (individual achievement, not belonging) held the theme,
while Gymshark's coached programmes and Alo's membership did not. One judgment
call surfaced that only an owner could make: are loyalty perks community? We
ruled no — "free shipping for members" is a discount mechanism, the same
boilerplate that made adiClub look like belonging in the five-year set. Coached
programmes are community. That ruling is recorded in the audit script and the
README, so the boundary is inspectable rather than implicit.

The finding survived, sharpened: community went from "nobody claims it" to "one
brand owns it, uncontested and unproven." Freezing the tags is what made the
audit worth doing — every correction is now permanent. The lesson: arithmetic
verification catches broken pipelines; only a human reading the receipts catches
a colour word masquerading as a strategy.

---

## Is there a business here?

Honestly assessed, not as built.

**What works.** As an internal tool it makes one analyst as productive as three.
The interpretation layer is genuinely good, and the discipline around
reproducibility and stated limitations is better than most commercial output.

**What does not.** Three problems, in order of severity.

*We do not own the data.* Collection is manual, and automating it would mean
scraping a source whose terms do not permit it. That is a legal constraint, not
an engineering one.

*The market is occupied.* SEMrush, SimilarWeb, Adbeat and Sensor Tower already
sell competitive ad intelligence with real data pipelines and years of history.
They compete on exactly the axis where we have nothing.

*Our differentiation is a prompt.* The analysis layer is the most copyable
component in the stack. A competitor with the data could add it in a sprint. We
cannot add their data at all.

There is also a product gap: one snapshot is a report, not a subscription.
"Nike shifted a third of its search messaging toward durability this quarter" is
valuable. "Here is what twelve brands say today" is a deliverable you sell once.

**Where money could be.** Services rather than software is the realistic path. An
agency runs teardowns for clients and uses this internally, billing for judgment
rather than access. It needs no additional product work and no data rights.
Alternatively, sell the interpretation engine to organizations that already have
licensed ad data, partnering rather than competing on collection.

---

## What we would do differently

**Collect before analyzing.** We built the analysis first and fitted data to it.
The correct order was to establish what could actually be collected, at what
depth, and only then decide what the analysis could honestly claim.

**Read past the first screen of any source.** The single line that cost us a
false finding was assuming the default view was the whole list.

**Design for reproducibility from the start.** We discovered the drift problem by
accident. It should have been a requirement on day one for anything producing
numbers a person will repeat out loud.

**Separate the artifact from the strategy.** Recognizing that search ads are
mostly product feeds should have shaped the collection plan, not arrived as a
mid-project caveat.

---

## What this was worth

The deliverable is a defensible read of a category and a tool that reproduces it
on demand. That has real value and it is what we set out to build.

The more durable outcome is a working method for interrogating our own analysis:
sample deep enough to be wrong out loud, freeze what should not move, classify
what you are actually measuring, and state the limits in the same breath as the
finding.

We found false conclusions in our own work — first a sampling artifact, then a
layer of tagging errors a teammate's audit surfaced — and corrected both
publicly before anyone acted on them. On a two-day project, that is the result
worth keeping.
