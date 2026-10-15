# Pedagogy: Bloom, teaching methods, gamification, neuropedagogy

The general pedagogy layer for Power BI lessons. Use it together with powerbi-didactics.md (the tool-specific teaching knowledge). This file covers: choosing a representation for a dashboard, the "demands interpretation" principle, age calibration, Bloom's taxonomy for graded questioning, a teaching-method menu, a gamification menu, and the twenty neuropedagogy principles applied to data lessons.

Choosing how to show data and how to question students are pedagogical decisions. This file covers: matching the representation to the goal, the "demands interpretation" principle, age calibration, Bloom's taxonomy for graded questioning, a teaching-method menu for variety, a gamification menu, and the twenty neuropedagogy principles with how they apply here.

## Match the representation to the goal

Pick the encoding that makes the target idea visible and arguable.
- Compare amounts across categories: bars or a dot plot.
- Change over time: a line.
- Relationship between two variables: a scatter (where "correlation is not causation" lives).
- Part of a whole, only for a few large parts: one stacked bar beats a pie.
- Distribution and spread (to fight "the average tells the whole story"): a histogram or strip plot, not just the mean. Central to the EDA unit.
- A data model or table relationships: an ERD-style diagram (units 1 and 7).
- Spatial pattern: a simple map or a region-by-measure heatmap.

If two encodings fit, prefer the one that forces interpretation over the one that hands it over.

## The "demands interpretation" principle

A representation that pre-chews the insight teaches nothing. If the chart shouts its conclusion, students read the title and stop thinking. Sometimes a messier view (a raw scatter instead of a fitted line, unsorted bars) teaches more because students must do the reasoning. Leave the argument for them.

## Age calibration

- **Grade 11 (יא):** one or two variables at a time; prefer aggregated or already-reduced data; short concrete tasks; simple interactivity (one filter). In ETL and SQL, small messy relational data is ideal because manipulating it is the skill.
- **Grade 12 (יב):** two or three variables and the relationships between them; raw messy data becomes teachable; questions can ask for a claim with evidence or a critique of the data; richer interactivity (filter plus cross-highlight) when exploration is the objective, as in the BI and dashboard units.

Density, variable count, and interactivity are the dials. Down for younger, up for older.

## Bloom's taxonomy: graded questioning

Build student prompts that climb, and tag each so the teacher sees the cognitive demand. Use verbs at each level:

- **Remember**: identify, list, name. "Name the two tables this JOIN combines."
- **Understand**: explain, summarize, classify. "Explain in your words why these rows dropped."
- **Apply**: use, compute, run. "Write a query that returns average sales per city."
- **Analyze**: compare, differentiate, break down. "Compare the INNER and LEFT results. What differs and why?"
- **Evaluate**: judge, critique, justify. "Which chart tells the truth more honestly here? Defend it."
- **Create**: design, build, compose. "Design a dashboard view that answers the client's question."

A good activity spans several levels so weaker and stronger students each find a rung. Match the top level to the teacher's B2 choice: a recall/understand lesson need not reach Create; a final-project lesson should.

## Teaching-method menu (for variety)

Vary the format so lessons do not blur together. Pick per the teacher's B3 choice or the goal:
- **Notice and wonder**: open with "what do you notice / what do you wonder" before any interpretation. Everyone can enter.
- **Think-pair-share**: individual guess, then pairs, then class. Good for prediction before revealing data.
- **Claim-evidence-reasoning (CER)**: a claim, backed by a specific data point, with explicit reasoning. The core analytical-report move; rehearse it often in this track.
- **Prediction before reveal**: students predict the result of a query or the shape of a distribution, then check. The gap is where learning happens.
- **Jigsaw**: groups each analyze a slice, then teach each other. Good for a multi-part dataset.
- **Live build / worked example then fade**: demonstrate a Power Query or DAX step, then have students do the next one with less help.

## Gamification menu (optional, only if it fits)

- **Query/insight challenge**: fastest or most elegant correct query; most surprising true insight from a dataset.
- **Points and badges**: light framing for a sequence of tasks (a "clean the data" badge, a "found the outlier" badge).
- **Escape-room framing**: each correct step unlocks the next clue in the dataset.
- **Dashboard critique gallery**: students score each other's dashboards against the unit-8 design principles.
Keep it in service of the goal; drop it if it adds noise.

## The twenty neuropedagogy principles (APA Top 20) in a data lesson

These are the same principles a dedicated neuropedagogy lesson-planner skill uses. When that skill is present, hand it the data core and let it tag the full lesson. When it is not, apply the most relevant few here. How they land in this track:

Cognition and learning:
1. Growth mindset: frame data skills as learnable; praise process (a clean query, a careful check), not talent.
2. Prior knowledge: connect a new technique to what students already did (a JOIN builds on the key relationships from unit 1).
3. Move beyond memorization to application and transfer: prefer "use it on new data" over "recite the syntax."
4. Practice with feedback: short query/EDA reps with immediate check-your-answer.
5. Distributed practice and retrieval: revisit JOINs or distributions across lessons, not once.
6. Clear, explained goals: state the understanding goal aloud; it is Step 0.
7. Support self-regulation and metacognition: ask students to explain their steps and what they would check next.

Motivation:
8. Intrinsic motivation via authentic, relevant data: real datasets (data.gov.il, OWID) beat toy numbers.
9. Mastery goals over performance goals: reward getting it right eventually, not being first.
10. Realistic, informative expectations and feedback.
11. Set challenging but attainable tasks: reduce data to human scale so the task is reachable.

Social and emotional:
12. Learning is social: pairs, jigsaw, peer critique.
13. Emotional wellbeing affects learning: keep the tool from overwhelming; scaffold Power BI.
14. A positive, low-threat climate for making and fixing mistakes (messy data is normal).

Context and assessment:
15. Manage attention and cognitive load: reduce visual noise (unit-8 principles), few categories, one idea at a time.
16. Clear expectations and rubrics: use the project rubric language early.
17. Formative assessment guides teaching: notice-and-wonder and quick checks reveal misconceptions.
18. Summative assessment fairness and clarity.
19. Reliability and validity of assessment: judge the reasoning, not just the chart.
20. Interpreting assessment sensibly: read student work for the thinking behind it.

Apply the subset that fits the lesson; do not force all twenty.
