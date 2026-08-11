# Creative-Teardown-Marketing

Pulls the ads a set of competitors are running right now and turns them into a messaging matrix. The matrix is one grid that shows which angles each competitor is pushing, so we can see the open space and decide where to position.

## Why this exists

Competitors tell you their strategy through the ads they pay to run. Those ads are public but scattered across ad libraries, and reading them one at a time tells you almost nothing. This tool gathers them in one place and structures them, so a marketing lead can look at a single page and answer three questions: what is each competitor claiming, which themes are crowded, and where is nobody playing.

## What it produces

A messaging matrix. Rows are competitors. Columns are message themes such as price, speed, trust and safety, ease of use, and ROI. Each cell shows how hard a competitor leans on that theme, with the example ad copy behind it. The output ships as a spreadsheet first and a shared dashboard later.

## How it works

Three stages:

1. Collect. Pull the active ads for a named list of competitors from public ad libraries such as the Meta Ad Library and the Google Ads Transparency Center, with more sources added over time.
2. Classify. Tag each ad by message theme and offer. This is where raw creative becomes structured data.
3. Assemble. Roll the tagged ads into the matrix and export it.

## Status

Early. The repo holds this README and nothing else yet. The first milestone is a working Collect stage for two competitors and two ad sources. Current tasks live in Issues.

## Team and ownership

The table below is a proposed split. Confirm it at kickoff and edit as needed. Everyone listed already has write access to the repo.

| Area | Owner | What it covers |
|------|-------|----------------|
| Build, all three stages | @spdooley5949 | Collect, Classify, and Assemble: the full pipeline that pulls the ads and produces the matrix |
| Ad collection pipeline | @andrewsilver314-ship-it | Stage 1, pulling ads from the libraries and keeping it running |
| Matrix logic and data | @catherinemchambers-coder | Stage 3, the data structure and building and exporting the matrix |
| Message classification | @jessfriedbergsmith-creator | Stage 2, the theme taxonomy and what counts as each angle |
| Data quality and testing | @JesseJ0k3s | Checking that pulled ads are real, current, and complete |
| Output and presentation | @williammlevine-917 | The deliverable, its format, the dashboard, and how it is shared |

## First milestones

1. Agree the competitor list and the exact matrix columns.
2. Pull the active ads for two competitors from one ad source.
3. Define the message themes and tag 20 sample ads by hand.
4. Build the first matrix from that sample and export it as a spreadsheet.

## How to contribute

1. Create a branch for your work. Do not commit straight to main.
2. Open a pull request when the work is ready.
3. Ask one teammate to review before you merge.

This keeps main clean and gives everyone a chance to catch problems early.

## Setup

To be written once the Collect stage exists. It will list the accounts and API keys each ad source needs, and how to run the tool.
