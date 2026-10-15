# Syllabus map: Information & Data Analysis track (מגמת מידע ונתונים, 785589)

The built-in map of the track, extracted from the official program (v1.4, Aug 2025). If the teacher supplies their own syllabus file or project knowledge, that overrides this. Use this to ground the understanding goal, the dataset choice, the representation, and the language of the instructions. Grade 11 is יא, grade 12 is יב. Hours are the official budget; a single activity must stay well inside a unit's hours.

## The sequence at a glance

| # | Unit | Grade | Hours | What it is really about |
|---|---|---|---|---|
| 1 | יסודות מערכות מידע וארגון נתונים (relational data foundations) | יא | 20 | Tables, fields, primary/foreign keys, ERD, relationship types (1:1, 1:N, N:N), data lakes. The mental model of structured data. |
| 2 | ETL / Power Query | יא | 40 | Extract-Transform-Load. Connect to sources, clean, rename, filter, merge/append, Group By, reusable steps that re-run on refresh. |
| 3 | SQL | יא | 40 | SELECT/FROM/WHERE/GROUP BY/ORDER BY/HAVING/DISTINCT, computed columns, CASE WHEN, operators, aggregates, JOINs (INNER/LEFT/RIGHT/SELF), subqueries, temp tables. |
| 4 | מבוא לכלי BI (intro to a BI tool) | יא | 10 | First contact with Power BI (or Tableau): environment, basic tasks. A runway into the full BI unit. |
| 5 | ניהול ידע בארגון (knowledge management) | יא | 30 | Collecting, organizing, sharing, preserving, and making knowledge accessible; personal and organizational KM; KM with AI tools. |
| 6 | EDA (exploratory data analysis) | יב | 50 | Variable types, distributions, descriptive stats (mean, median, sd), frequency tables, missing values, outliers. First look at the data. |
| 7 | כלי BI (the BI tool in depth) | יב | 60 | Connect sources, data prep, build the data model (relationships, fact vs dimension), measures and computed columns, KPIs, dashboards. |
| 8 | דשבורד (dashboard) | יב | 40 | What a dashboard is; effective-dashboard rules; choosing the right chart per question; filters and tooltips; visual-design principles (attention, proximity/grouping, reducing visual noise, hierarchy, audience fit, color). |
| 9 | Storytelling | יב | 10 | Data storytelling: beginning (question), middle (visual evidence), end (conclusion / call to action). |
| 10 | מהו דוח אנליטי (the analytical report) | יא-יב | 20 | What an analytical report is; analytical-research traits; market research & BI; report structure; the process of producing one. |
| 11 | פרויקט גמר: דוח אנליטי (final project) | יב | 220 | The full cycle: find datasets, define the client, define the research question, EDA, cleaning, advanced analysis, insights, dashboard, recommendations, presentation. Graded by a rubric. |

## How to read the stage for lesson design

- **Units 1 to 3 (data foundations, ETL, SQL)** are hands-on with structured data. Best data: small, slightly messy, relational (a couple of related tables). Best route: often a small interactive tool or a real Power BI/Power Query build, because the skill being taught is manipulation, not just reading. Language of instructions: precise, operation-oriented ("write a query that...", "add a step that...").
- **Unit 4 (intro BI)** is a gentle on-ramp. Keep the Power BI tasks minimal and confidence-building.
- **Unit 5 (knowledge management)** is conceptual and reflective, not chart-heavy. Data lessons here are lighter; favor discussion, organizing, and AI-tool use.
- **Unit 6 (EDA)** is where representations of distribution and spread matter most: histograms, strip plots, frequency tables, and the average-hides-variation misconception. Route: static images or a small interactive explorer.
- **Units 7 to 9 (BI tool, dashboard, storytelling)** are the heart of the Power BI work. The real Power BI route is the default. Dashboard-design lessons should foreground the visual-design principles listed in unit 8.
- **Units 10 to 11 (analytical report, final project)** are integrative. Here the skill's job is usually to help find and vet a real dataset, sharpen the research question, and produce a dashboard-ready reduced dataset, then hand structure to the lesson planner and the report rubric.

## Two anchor moments to know

- **End of grade 11**: students submit a project proposal (research question, client, dataset). Lessons late in יא should build toward locating datasets and framing an analytical question.
- **End of grade 12 (around April)**: final project and practical exam (dashboard + presentation). The back half of יב is project work against the rubric.
