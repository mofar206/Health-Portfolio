# mfPortfolio206 · Product, data & community

Three interactive projects rooted in South King County, built with static HTML, CSS, JavaScript, Python, and SQL. The portfolio also includes UW Informatics education and professional experience.

| Project | Working product | Evidence |
|---|---|---|
| Health, in context | Healthcare, mental health and food-access explorers | CDC county indicators; original neighborhood scenarios explicitly labeled illustrative |
| South County, connected | Eight-anchor bus schedule comparison, day/time filters and route-direction intervals | Official Metro GTFS Fall 2026 feed; 1,107,809 stop-time rows scanned |
| Permit Pulse | Search, status/type/year filters, record milestones, hypothetical review markers and CSV export | 2,983 distinct records from Renton's active permit layer, retrieved September 14, 2026 UTC |

## Run

No build step or account credentials required. Serve `dist/` in the Sites checkout, or the repository root in the GitHub Pages layout:

```sh
python3 -m http.server 4175
```

Open the local server in a browser. Data snapshots are checked in; external fonts have system fallbacks. The health project fetches public indicators separately and reports source errors without replacing them with fabricated data.

## Data pipeline

`analysis/build_data.py` uses the Python standard library. Download [Metro's official GTFS archive](https://metro.kingcounty.gov/GTFS/google_transit.zip) to a raw directory as `metro.zip`, then run:

```sh
python3 analysis/build_data.py --raw-dir /path/to/raw
python3 analysis/validate.py
```

The builder applies GTFS service calendars and exceptions, excludes no-pickup events, and keeps one trip event per anchor. The fixed example dates must fall inside the feed's coverage; update dates deliberately for a new feed. Metro source zip and Renton response hashes, retrieval times and methods are recorded in the processed JSON. Keep raw archives privately if exact reconstruction is required; official endpoints change over time.

Renton extraction first lists every object ID, fetches bounded batches, reconciles parcel rows by permit ID and checks date order. It uses no applicant/owner names or addresses. `analysis/queries.sql` documents status, application cohort, and interval queries; the builder executes a SQLite status reconciliation.

## Interpretation

- Transit counts describe selected stop groups, not whole cities. Group sizes differ. Scheduled intervals do not establish real wait times, reliability or equitable access.
- The Renton active layer is not a complete application history. Issued is not completed. Application-to-issue calendar days are not staff processing time. The adjustable age marker is a prototype review cue, not an official deadline.
- Health neighborhood values inherited from the original portfolio lack row-level evidence and remain illustrative. CDC PLACES county indicators are distinguished from those scenarios.
- These are independent portfolio projects, not agency products. No user interviews, employer impact, operational savings, or community outcomes are claimed without measurement.

## Validation

Offline checks reconcile permit counts/statuses and date intervals, validate transit references/geography and check local page/asset links. Browser checks cover transit loading, permit search, record dialogs and empty results. Native controls, visible focus, responsive layouts, and reduced-motion support are included. Further user and assistive-technology testing remains future work.

## Sources

- [King County Metro developer resources](https://kingcounty.gov/en/dept/metro/rider-tools/mobile-and-web-apps)
- [Renton Permit Case Parcels (Active)](https://gismaps.rentonwa.gov/as03/rest/services/Operational/PermitsAndConstruction/MapServer/41)
- [CDC PLACES county data](https://data.cdc.gov/resource/swc5-untb.json?locationid=53033&datavaluetypeid=CrdPrv)

Transit scheduling, geographic, and real-time data provided by permission of King County

## Reproduce the case-study findings

Run `python3 analysis/report_findings.py` to calculate the figures displayed in the transit and permit case studies and write `datasets/findings.json` (under `dist/` in the Sites checkout). The script checks same-anchor weekday/weekend counts and valid permit intervals.

The case studies connect those results to recommendations, requirements, tradeoffs, and a proposed evaluation plan. Planned research is explicitly distinguished from completed analysis.
