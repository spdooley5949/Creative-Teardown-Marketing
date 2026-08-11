# Product Requirements Document: Creative Teardown

**Status:** Draft, living document.
**Owner:** Shane Dooley.
**Last updated:** Aug 11, 2026.

## Problem and purpose

Competitors broadcast their strategy through the ads they pay to run, but that signal sits scattered across ad libraries and no one reads it as a whole. Teams end up guessing at positioning. This tool collects the ads a set of competitors are running right now on Google and turns them into one messaging matrix, so a marketer can see what each brand claims, who they target, which proof points repeat, and where no one is competing.

## Goals and success metrics

- A marketer can open one Excel file and read the competitive messaging landscape in under five minutes.
- Covers 5 to 8 competitors and their currently running Google ads.
- Every ad is tagged by claim, audience, and proof point.
- The matrix flags at least one clear whitespace angle no competitor is using.
- Course definition of done: the matrix is built, reviewed, and presented by Thursday Aug 13.

## Scope

In scope for the MVP:
- Google Ads Transparency Center as the single ad source.
- Manual collection of ad copy into a shared sheet.
- A tool that reads the sheet, classifies each ad, and outputs the messaging matrix as Excel.
- A short presentation of the findings.

Explicitly not in scope for the MVP:
- Automated or scheduled scraping of any ad site.
- Meta, LinkedIn, TikTok, or other ad sources.
- A live dashboard or web app.
- Any paid data provider.
- Historical trend analysis over time.

## User stories and requirements

- As a marketer, I want to see every claim each competitor is making, so I can tell how they position.
- As a marketer, I want to see which audiences each competitor addresses, so I can spot who they are chasing.
- As a marketer, I want recurring proof points surfaced, so I know what evidence the category leans on.
- As a marketer, I want the empty cells in the matrix called out, so I can find an unclaimed angle.
- As the builder, I want to load a clean sheet of ad copy and get a formatted matrix back, without hand-building it.

## Constraints

- Deadline: complete by Thursday Aug 13. Two working days.
- Team: five collaborators plus the builder, working in parallel.
- Data: the Google Ads Transparency Center has no public API, so collection is manual for the MVP.
- Tooling: classification uses Claude, which requires an API key.
- The output must be Excel, since that is where the audience works.

## Open questions

- Final competitor list: who are the 5 to 8? (Owner: William)
- Exact matrix columns: which claim types, audiences, and proof points? (Owner: William and Jess)
- Who presents on Thursday, and to whom?
- Do we wire in the Claude API for auto-tagging, or hand-tag for the MVP and automate later?

---

This is a living document. It gets revised as the team learns more, not written once and frozen.
