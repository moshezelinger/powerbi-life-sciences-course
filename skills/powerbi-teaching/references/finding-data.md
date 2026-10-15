# Finding and vetting datasets for the classroom

The web-search capability is what makes this skill more than a chart generator. But a raw dataset is not a lesson. This file is how to find one that fits and how to reject one that does not.

## Where to look (prefer these over random search results)

**Israeli / Hebrew sources** (labels already in Hebrew, locally relevant, high motivation):
- data.gov.il — the Israeli government open-data portal. Broad: transport, environment, health, education, municipal data.
- The Central Bureau of Statistics (CBS, halamas) — demographics, prices, education, environment, with downloadable tables.
- Ministry of Education open data and municipal (iriya) portals — school, city, and regional data students recognize.

**Science-friendly, clean, multilingual** (the workhorses for science lessons):
- Our World in Data — excellent for climate, energy, health, population, food. Clean, documented, downloadable CSVs, CC-BY licensed. Usually the fastest path to a good science dataset.
- World Bank Open Data — country indicators over time, good for comparison and trend questions.
- Gapminder — curated, teaching-oriented global development data.
- NASA / NOAA climate data and WHO health data for physical and life sciences.
- OpenNeuro and similar repositories for neuro/cognitive datasets when the topic calls for it.

**General repositories** (use with license care):
- Kaggle Datasets and the UCI Machine Learning Repository. Rich but check the license and provenance before classroom use.

## Search strategy

1. Search the topic plus a data cue: `<topic> open data`, `<topic> dataset CSV`, `<topic> our world in data`. Include the year only when recency matters.
2. Prefer a government or curated source (OWID, World Bank, CBS) over an aggregator or a forum.
3. Before committing, web_fetch the actual file or its landing page and read the real column names, units, and row count. Never design a lesson around a dataset you have not opened.
4. If the best data is behind a download button or an API, note that and fetch what is accessible; do not invent columns you did not see.

## Vetting checklist (run every item before building)

- **Supports the question.** Does the data actually let students answer the Step 1 question? If not, change the question or the dataset. This is the most common failure.
- **License.** Is classroom use allowed? CC-BY, public domain, and government open data are safe (attribute them). Unclear license means find another source.
- **Size.** Can it reduce to classroom scale (a handful of rows, categories, or points)? If not, plan the aggregation now (Step 3).
- **Cleanliness.** Missing values, inconsistent units, weird encodings? Budget cleanup time or pick a cleaner source.
- **Language.** Are labels in Hebrew, or will they need translating for the class? OWID and World Bank are English; plan to translate the handful of labels students will actually see.
- **Age-appropriateness.** No distressing, graphic, or sensitive content for the age group. Check before it reaches a screen.
- **Honesty.** Is the dataset representative, or would it mislead? A biased sample can be a lesson in itself, but only if you name it.

## When to invent or simplify instead

Real data motivates, but it is not sacred. Invent or hand-simplify data when the real thing is too large, too messy, or too slow to prepare for the time available, or when you need a clean contrast to isolate one idea. Make the simplification explicit to yourself and, where useful, to students (recognizing that real data is messy is itself a learning goal). Keep invented data plausible so students build correct intuitions.
