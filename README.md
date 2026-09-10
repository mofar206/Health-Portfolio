# Health Equity Portfolio · Mohamed Farah

A five-page interactive portfolio exploring healthcare access, behavioral health facilities, and food access in King County, Washington.

## Explore

- **Healthcare access:** ZIP lookup across the original neighborhood scenario dataset and comparative insurance bars.
- **Mental health:** six facility scenarios with population-to-facility ratios calculated from their inputs. Zero facilities produces an undefined ratio, not an invented value.
- **Food access:** six neighborhoods can be compared in either selector. Percentage differences use percentage points.
- **Public context:** CDC PLACES county estimates, observation years, crude prevalence, and confidence intervals are requested separately from neighborhood scenarios.

## Run locally

The site uses static HTML, CSS, and JavaScript, with no build dependencies. Serve the directory containing `index.html` with any static HTTP server. For this Sites checkout, that directory is `dist/`; on the GitHub branch, the same files are at the repository root.

## Data provenance

The original neighborhood records lack row-level citations and extraction artifacts. They are preserved and explicitly labeled **illustrative**, not presented as official findings, validated estimates, or current care availability. The portfolio does not make USDA food-access or HRSA shortage designations.

CDC requests filter `locationid=53033`, the desired measure, and `datavaluetypeid=CrdPrv`. The app checks values and geography, shows the returned observation year, and does not silently substitute mock values if a source fails.

Supplemental Census requests use ACS 2022 profile data for Washington state 53, King County 033. During validation, the Census API returned a key-required page. The interface reports that limitation explicitly. A future authenticated integration should keep credentials server-side; do not put a private API key into this public repository.

Sources:

- [Original portfolio revision](https://github.com/mofar206/Health-Portfolio/tree/b8cee6183288813f5af19f90b4ce088ed26a0b73)
- [CDC PLACES county data](https://data.cdc.gov/resource/swc5-untb.json?locationid=53033&datavaluetypeid=CrdPrv)
- [ACS 2022 profile documentation](https://api.census.gov/data/2022/acs/acs1/profile.html)
- [USDA Food Access Research Atlas documentation](https://www.ers.usda.gov/data-products/food-access-research-atlas/documentation)

## Design and accessibility

Responsive layouts, semantic navigation, native form controls, visible keyboard focus, polite result announcements, reduced-motion support, and explicit loading, missing-record, and source-error states. System font fallbacks preserve readability if externally hosted fonts are unavailable.

## Validation

Checked JavaScript syntax; all five HTML routes and local assets; link fragments, unique IDs, and form labels; every neighborhood scenario; calculated ratios and zero-denominator handling; comparison differences; invalid values; and current CDC response contracts. Browser visual and interaction testing has not been performed.

## Next research milestone

Replace scenario records with a reproducible, geography-aligned dataset. Include source URLs and vintages per record, uncertainty, extraction scripts, and measured validation. Do not claim project impact or health outcomes before they have been evaluated.
