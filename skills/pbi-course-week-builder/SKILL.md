---
name: "pbi-course-week-builder"
description: "Use when building, revising or checking a week of Moshe's high-school Power BI course: student learning-report app, teacher prep app, slide outline, teacher guide or print checklist."
---

# Building a week of the Power BI course

This skill runs the method that produced week 1, version 4 of Moshe's course (claude.ai project "קורס Power BI"). The detailed template, style rules and pedagogy live in the project, not here. This file is the procedure and the short list of rules that must hold even if the project file cannot be read.

All deliverables are in Hebrew. Follow Moshe's writing preferences: native Hebrew, verbs over nouns, one idea per sentence, no em or en dashes, no middle dot.

## Sources of truth (read before writing anything)

Read with the Projects tool (`project_read`), not from local disk:

1. `claude/מערכת/מדריך פיתוח שבוע חדש.md`: the authoritative guide. Template anatomy of both apps and the three docs, the fixed glossary, before/after examples, pedagogy, process, pre-delivery checklist, decision log. If it conflicts with this skill, the guide wins. If Moshe says something different in the chat, Moshe wins.
2. `claude/מערכת/check_week.py`: the style and structure checker.
3. The latest `claude/סיכום שיחה - ...` file and `claude/סל המאגרים לקורס Power BI.md`: status, decisions, what was checked in the data.
4. `claude/שבוע 1/אפליקציות/*.html`: the app code that serves as the template for a new week.
5. `claude/נתונים/`: the class data files. Every number comes from these.

If the Projects tool is not available, ask Moshe to attach the guide and the checker, and say which rules you are working from until he does.

The project instructions require asking Moshe before activating another skill (for example the humanizer or powerbi-teaching). Ask once for the set you need.

## Procedure for a new week

1. **Status snapshot.** In three to five lines: where the course stands, what was taught (only what Moshe reported), what is open. Do not assume planned lessons were taught.
2. **Week map.** One row per lesson: title (context plus principle), subtitle, dataset, principle, opening question, times. Get Moshe's approval before writing materials.
3. **Data check in code.** Load the class files, compute every number the week will show (expected values, checkpoints, answers, slide numbers). Save the script. New findings go into the dataset basket file.
4. **Write content as data first.** LESSONS (student app), STATIONS (teacher app), LOC (button locations), PASTE, glossary. Then the docs. Design comes last.
5. **Approval file.** An RTL Markdown file with 10 to 15 checkboxes, each with the full proposed text. Never a 100-item file: Moshe found that too much to follow.
6. **Build and check.**
   - Run `python3 check_week.py <files>` on every app and doc. Zero errors. Read every warning and either fix it or state why it stays.
   - Browser test with Playwright: desktop 1366 px; phone 390 px with text size "גדול מאוד" (localStorage `pbi-view-v1` = `{"size":"xl","layout":"auto"}`, then reload) in dark mode. No page errors, no horizontal scroll, the tour reaches every stop, clicking a [[button]] chip shows its location.
7. **Publish.** Republish to the same artifact URL. Never change step, question or task ids, storage keys or capabilities. On a redeploy omit `capabilities` and `files`, so the stored ones are kept.
8. **Docs and copies.** Update the slide outline, teacher guide and print checklist (Claude Docs, find-and-replace edits, then export and scan). Replace the copies in the project and update the conversation summary.
9. **After a class.** Collect only the missing facts with a short form: what they finished, where they got stuck, what they understood and the evidence, what to change. Keep observation, interpretation and decision separate, then update the next lesson.

## Fields built for automatic checking

While preparing a lesson's learning report, and again when revising it, offer Moshe once, briefly and as an option (never as the default), to make answer fields checkable by code. Offer it per question, with the reason ("this answer is one number, so a script can check it"). Suggest the field type that fits: fill (a number or short text), click (choice, checkbox) or drag (ordering, matching).

If he accepts, the report must meet the contract defined in the `rubric-feedback-docx` skill (section "מסלול דטרמיניסטי"): a stable id per field, a declared field type, and a JSON export of the answers. That skill owns the rubric format, the checking scripts and the Word comments. Do not restate its rules here.

Once the lesson's questions are approved, offer to hand off to `rubric-feedback-docx` to draft the rubric for those ids, with the correct answers already computed in step 3. Open questions (reasoning, interpretation) stay open and are marked "teacher judgment".

## Rules that always hold

- Students: second person plural ("פתחו"). Teacher: infinitive, present plural or neutral wording ("לבדוק", "פותחים", "לרשותך"). No gendered address.
- The person acts, not the tool, in titles and instructions.
- A step says only what to do. Any explanation goes in the step's `w` field, shown as "למה עושים את זה?". Every step has `e` ("מה אמור להופיע").
- Questions split into parts א, ב, ג. The first is answered from the screen, the next asks for reasoning, and each says where the answer is found.
- No spoilers: intros ask, they do not answer. A finding appears only at the step where students discover it. This includes the glossary, the dataset cards and the slides. Teacher materials may give answers.
- Fixed glossary, with its definition the first time in each lesson: רשימת הצעדים (Applied Steps), ה"מתכון" של Power Query; מאמץ דגימה; נרמול; השוואה הוגנת; ממוצע לכידות בסבב. Extend the glossary in the guide before using a new term.
- "לחצו על X". Button names in English, as in the UI. Every [[button]] has a LOC entry: "בסרגל העליון, בלשונית Home".
- Slide text in short bullet points, up to 25 words per slide.
- Teacher prep tasks in 5-minute blocks; station totals and the running total are computed from the tasks.
- Never state a conclusion the data does not support. Mark any demo outside Power BI as a prototype. List what was not tested in Power BI.
- A change to something Moshe already approved is proposed, never made silently.

## Keeping the method current

When Moshe approves a new rule or reverses one, propose the exact edit to the guide: the relevant section plus one line in its decision log (section 12). If the checker should enforce it, propose the matching pattern for `check_week.py` too. The guide stays the single place where the rules live.