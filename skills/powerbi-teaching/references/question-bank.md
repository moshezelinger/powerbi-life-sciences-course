# Question bank for the opening conversation

The skill opens by asking the teacher a few of these as tappable choice questions via `ask_user_input_v0`. Pick only the subset that changes the build, scale the count to complexity (one or two for a focused ask, a few more for an open one), and always leave a skip-and-build path.

Two rules for every question:
1. Choice format, two to four short mutually-exclusive options, so the teacher taps.
2. Phrase it so the same question can later be posed to students almost unchanged. The teacher rehearsing the inquiry is the point.

## A. Scoping (ask first, pick the few that matter)

**A1. Which Power BI area / unit.** "Which part of Power BI is this for?" Options from the syllabus: Power Query / ETL, data model and relationships, DAX / measures, dashboards, or the final-project dashboard. Determines the aid, the data, and the language. Skip if the request names it.

**A2. Understanding goal / misconception.** "What should students walk away understanding?" Offer two or three concrete goals for that area from powerbi-didactics.md, plus "something else (I will type it)." Example for DAX: "a measure reacts to the slicer, a column does not", "when to use CALCULATE", "why a total is a measure, not a column".

**A3. Data source.** "Where should the data come from?" Options: "search the web for a real dataset", "I will provide a file", "invent a small dataset for this idea". For Power Query, bias toward a small messy real file; for the data model, toward a few related tables.

**A4. Lesson length.** "How long is this?" Options: short (up to ~20 min), a full lesson, spans several lessons. Keeps it inside the hour budget.

## B. Pedagogy and aid (ask when they change the build)

**B1. Teaching aid.** "How should students meet the idea?" Options: "illustrate it with a picture", "let them click an interactive simulator", "build it hands-on in Power BI". Default to the simulator for abstract ideas (filter context, join behavior) and to real Power BI when the mechanics are the lesson.

**B2. Cognitive target (Bloom).** "What should students mostly do?" Options: "recall and understand", "apply a technique", "analyze and compare", "evaluate or create". Sets where the prompts sit.

**B3. Teaching method.** "How do you want to run it?" Options: "notice and wonder", "demo then fade", "think-pair-share", "critique and fix" (great for dashboards), "let the skill choose".

**B4. Gamification.** "Add a game element?" Options: "yes, a challenge or competition", "yes, points/badges", "no, keep it plain". Only if it fits.

## C. Teacher framing (ask once for areas the teacher finds harder)

**C1. How the teacher frames the idea.** "In one tap, how do you usually explain this?" Offer two or three framings the skill can match its language to, plus "suggest a framing for me." Calibrates the output and quietly surfaces where the teacher may want the grounding note from powerbi-didactics.md, without putting them on the spot.

## D. The handoff to students

The goal from A2, the Bloom target from B2, and the student-facing investigation question become the prompts posed to students in Step 6, as an interactive artifact or as text. Tell the teacher this briefly.

## Worked examples

Focused: "a 20-minute lesson on measures vs calculated columns, grade 12." Area and length are given, so ask only A2 (which facet of the confusion) and A3 (data source), then build, offering skip after the first screen.

Open: "something on dashboards." Ask a few more: A1 (BI tool vs dashboard vs final project), A2 (goal), B1 (aid, likely critique-and-fix or real build), B4 (gamification), then build.
