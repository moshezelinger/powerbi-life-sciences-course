# The didactics of teaching Power BI

This is the differentiator. Not how to build a visual (the powerbi-visuals skill covers that) and not general data pedagogy (pedagogy.md covers that), but how to *teach* Power BI: the misconceptions students actually hold, the order to introduce ideas, what to demo versus what to have them build, how to assess, and a short grounding note so the teacher feels expert. Organized by the areas of the track. Pull the one or two areas the lesson touches; do not dump all of it.

A cross-cutting principle first: **teach with worked-example-then-fade.** Demo the mechanics once on one dataset, then hand students a new dataset to do the next step themselves with less help. Power BI overwhelms when students are asked to produce before they have seen it done. And **assess the model and the reasoning, not the picture.** A chart can look correct on top of a broken model or a wrong measure; grade what is underneath.

## Power Query / ETL

**The one idea to instill:** Power Query records *steps* that re-run automatically when the data refreshes. It is not one-time editing like Excel. Students who miss this build something that works once and breaks on the next file.

**Misconceptions to confront:**
- "I edited the data" (they think it is a one-time change, not a repeatable pipeline).
- Merge and append are the same thing. They are not: merge joins on a key and adds columns (like a JOIN); append stacks tables and adds rows (like UNION).
- Step order does not matter. It does: filtering before or after a transform changes the result, and a step can depend on a column an earlier step renamed.
- Data types are cosmetic. A wrong type silently breaks later steps and aggregations.

**Scaffolding sequence (demo, then fade):** connect to source, set data types, rename columns, filter rows, remove duplicates, then merge or append, then Group By. Demo the first few on a messy file; give them the next messy file to clean themselves.

**Errors to watch for:** hardcoding a value that will not survive refresh; expanding a merged table and pulling in every column instead of the needed ones; forgetting to set types so a later Group By misbehaves.

**How to assess:** show them the Applied Steps and ask them to predict the output, or give raw messy data and grade the cleaned result plus whether the steps are robust to a refreshed file.

**Teacher grounding:** to teach this confidently, be solid on one thing: every action becomes a step in the right pane, and the query re-runs top to bottom on refresh. If you can read the Applied Steps aloud and explain what each does, you can teach the unit.

## The data model (relationships, star schema)

**The one idea to instill:** Power BI is a *model* tool, not just a chart tool. The power comes from relationships between tables, not from one giant flat table.

**Misconceptions to confront:**
- One big flat table is the right way (an Excel habit). It is usually the wrong way; a star schema of a fact table plus dimension tables is cleaner and faster.
- Relationships are optional decoration. They are what makes a slicer on one table filter another.
- Cross-filter direction does not matter. Single versus both directions changes what filters what, and "both" invites ambiguity.
- A date column is enough; you never need a separate date table. For time intelligence you usually do.

**Scaffolding sequence:** start from the ERD (this connects directly to the relational-foundations unit: entities, primary and foreign keys). Then build one relationship visually and show how a slicer on the dimension filters the fact. Then have students build the remaining relationships and identify which tables are facts and which are dimensions.

**Errors to watch for:** many-to-many relationships created by accident; relating on the wrong key; expecting a slicer to filter across a relationship that does not exist.

**How to assess:** give a set of tables and have students design the model, draw the relationships, justify fact versus dimension, and predict what a given slicer will filter.

**Teacher grounding:** the mental model to hold is the star: one central fact table (the events, the measures) surrounded by dimension tables (the who, what, when, where) joined on keys. Filters flow from dimension to fact.

## DAX: measures versus calculated columns

**The one idea to instill:** a **measure** computes at query time for whatever is currently filtered or selected; a **calculated column** computes row by row when the data refreshes and is stored. Measures are dynamic answers; columns are static values.

**This is the single most common Power BI confusion.** Spend real time on it.

**Misconceptions to confront:**
- A calculated column reacts to slicers. It does not; it is fixed at refresh.
- Use a column where a measure is needed (or the reverse). Totals, ratios, and anything that should respond to selection want a measure.
- CALCULATE is magic. Frame it plainly: CALCULATE changes the filter context in which a measure is evaluated.
- Row context and filter context are the same. They are the deep distinction; introduce gently and by example, not by definition.

**Scaffolding sequence:** start with implicit aggregates (drag a number, get a sum), then write explicit measures for the same aggregates so students see the difference, then introduce CALCULATE as "answer the same question but change what is filtered." Save time intelligence for later.

**Errors to watch for:** writing a measure that hardcodes a filter that should come from a slicer; building a calculated column for something that should react to selection; SUMMARIZE and filter traps that quietly change the grain.

**How to assess:** give a business question ("average sales per city, respecting the slicer") and have students write the measure and explain, in one sentence, why a measure and not a column.

**Teacher grounding:** the one thing to be solid on is context. A measure sees the current filter context (the slicers, the row of the visual). A calculated column sees only its own row at refresh. If you can say which context a given formula runs in, you can teach DAX.

## Dashboards and visual design

**The one idea to instill:** a dashboard is not a collection of charts; it is a designed answer to a question, where every visual earns its place and interactivity serves exploration.

**Misconceptions to confront:**
- More visuals mean a better dashboard. Clutter hides the message; fewer, clearer visuals win.
- Any chart will do. Each visual should answer one question, and the chart type must fit the data (bars to compare, lines for time, a scatter for relationship).
- Decoration equals quality. 3D, heavy pies, and rainbow palettes reduce clarity.
- Interactivity is a gimmick. Slicers, cross-filtering, tooltips, and drillthrough exist to let the user explore, not to show off.

**Teach by critique.** Show a deliberately bad dashboard and have students diagnose and fix it against the design principles from the dashboard unit: direct attention, group related items (proximity), reduce visual noise, build a visual hierarchy, fit the audience, and use color consistently. Critique-then-rebuild teaches design better than a blank canvas.

**Scaffolding sequence:** one question per visual, then chart choice, then layout and grouping, then interactivity (slicers and cross-filter first, tooltips and drillthrough later), then color and cleanup.

**Errors to watch for:** a dashboard with no clear question; inconsistent colors carrying accidental meaning; slicers that do not filter because the model relationship is missing; tooltips and drillthrough added before the basics are clean.

**How to assess:** use the final-project rubric language early. Judge whether each visual answers a question, whether the model behind it is sound, and whether the design follows the principles, not merely whether visuals appear.

**Teacher grounding:** hold the unit-8 principles as a checklist and apply them to any dashboard in front of you. If you can point at a visual and say what question it answers and why that chart, you can lead the critique.

## When to use a concept simulator instead of Power BI

Some Power BI ideas are abstract and hard to *see* inside Power BI itself. For these, a small interactive artifact built in chat, projected by the teacher, teaches faster than the tool:
- **Filter context**: an artifact where clicking a slicer visibly changes a measure, so students see the measure recompute.
- **Measure versus calculated column**: side by side, one reacts to the filter and one does not.
- **JOIN and merge behavior**: show rows appearing or dropping as the join type changes.
- **Cross-filter direction**: show filters flowing one way versus both.
Build these as the interactive-concept-simulator route, then move to real Power BI for the mechanics.
