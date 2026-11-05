/* edits-engine.js: מנוע השינויים של דוח הלמידה. נטען גם בדוח התלמיד וגם במסע ההכנה למורה.
   המנוע דטרמיניסטי: אותו קלט נותן תמיד אותו פלט. אין בו מודל שפה ואין בו קריאות רשת.

   מבנה קובץ השינויים (edits-week1.js):
   window.PBI_EDITS = {
     version: 1, week: 1,
     lessons: {
       "1": {
         goal: "...", submit: "...",                 // הנחיות השיעור
         qOrder: ["l1-q2", "l1-q1", "l1-q3"],         // סדר השאלות בשיעור
         items: {
           "l1-3":  { t: "...", e: "...", h: "...", w: "..." },          // צעד
           "l1-q1": { q: "...", why: "...", options: { A: "..." },      // שאלה
                      rows: { count: "..." }, correct: "A" }
         }
       }
     }
   };

   כללים ששומרים על הניקוד:
   1. מזהים לא משתנים: לא מוסיפים ולא מוחקים שאלות, צעדים, אפשרויות או שורות.
      התשובות של התלמידים וה-JSON שבסיכום מזוהים לפי המזהים, ולכן שינוי סדר לא משנה אותם.
   2. תשובה נכונה אפשר לשנות רק בשאלה שכבר יש לה מפתח בקוד התלמיד (שיעורים 1 עד 3).
      בשאלות הגשה עם ציון אין מפתח בקוד התלמיד, וגם קובץ השינויים לא מוסיף אחד.
   3. שינוי לא תקין (מזהה לא קיים, תשובה נכונה שאינה אחת האפשרויות) לא מוחל, ונרשם ביומן. */
(function (root) {
  "use strict";

  var STEP_FIELDS = ["t", "e", "h", "w"];
  var LESSON_FIELDS = ["goal", "submit"];
  var REQUIRED_STEP = { t: 1, e: 1 };

  function clone(x) { return JSON.parse(JSON.stringify(x)); }
  function isObj(x) { return !!x && typeof x === "object" && !Array.isArray(x); }
  function str(x) { return typeof x === "string"; }
  function byId(list) { var m = {}; (list || []).forEach(function (x) { m[x.id] = x; }); return m; }
  function hasKey(q) { return q && q.correct !== undefined && q.correct !== null; }

  function correctValid(q, c) {
    var opts = byId(q.options);
    if (q.type === "choice") return str(c) && !!opts[c];
    if (q.type === "match") {
      if (!isObj(c)) return false;
      return (q.rows || []).every(function (r) { return str(c[r.id]) && !!opts[c[r.id]]; });
    }
    return false;
  }

  // apply(base, edits) -> { lessons, log }. base לא משתנה.
  function apply(base, edits) {
    var out = clone(base), log = [];
    if (!isObj(edits) || !isObj(edits.lessons)) return { lessons: out, log: log };
    out.forEach(function (L) {
      var e = edits.lessons[L.n];
      if (!isObj(e)) return;
      LESSON_FIELDS.forEach(function (f) {
        if (str(e[f]) && e[f].trim()) L[f] = e[f];
      });
      var items = isObj(e.items) ? e.items : {};
      var known = {};
      L.steps.forEach(function (s) {
        known[s.id] = 1;
        var x = items[s.id];
        if (!isObj(x)) return;
        STEP_FIELDS.forEach(function (f) {
          if (!str(x[f])) return;
          if (x[f].trim()) s[f] = x[f];
          else if (REQUIRED_STEP[f]) log.push("שיעור " + L.n + ", " + s.id + ": שדה " + f + " לא יכול להיות ריק. השינוי לא הוחל.");
          else delete s[f];
        });
      });
      L.qs.forEach(function (q) {
        known[q.id] = 1;
        var x = items[q.id];
        if (!isObj(x)) return;
        if (str(x.q) && x.q.trim()) q.q = x.q;
        if (str(x.why) && x.why.trim() && hasKey(q)) q.why = x.why;
        if (isObj(x.options)) (q.options || []).forEach(function (o) {
          if (str(x.options[o.id]) && x.options[o.id].trim()) o.text = x.options[o.id];
        });
        if (isObj(x.rows)) (q.rows || []).forEach(function (r) {
          if (str(x.rows[r.id]) && x.rows[r.id].trim()) r.label = x.rows[r.id];
        });
        if (x.correct !== undefined) {
          if (!hasKey(q)) log.push("שיעור " + L.n + ", " + q.id + ": לשאלה אין מפתח בקוד התלמיד, ולכן לא מוסיפים לה תשובה נכונה.");
          else if (!correctValid(q, x.correct)) log.push("שיעור " + L.n + ", " + q.id + ": התשובה הנכונה אינה אחת האפשרויות. השינוי לא הוחל.");
          else q.correct = clone(x.correct);
        }
      });
      Object.keys(items).forEach(function (id) {
        if (!known[id]) log.push("שיעור " + L.n + ": המזהה " + id + " לא קיים בדוח. השינוי לא הוחל.");
      });
      if (Array.isArray(e.qOrder)) {
        var qm = byId(L.qs), seen = {}, next = [];
        e.qOrder.forEach(function (id) { if (qm[id] && !seen[id]) { seen[id] = 1; next.push(qm[id]); } });
        L.qs.forEach(function (q) { if (!seen[q.id]) next.push(q); });
        L.qs = next;
      }
    });
    return { lessons: out, log: log };
  }

  // diff(base, work) -> edits: רק מה שבאמת שונה מהמקור.
  function diff(base, work) {
    var out = { version: 1, week: 1, lessons: {} };
    var wm = {};
    work.forEach(function (W) { wm[W.n] = W; });
    base.forEach(function (B) {
      var W = wm[B.n];
      if (!W) return;
      var e = {}, items = {};
      LESSON_FIELDS.forEach(function (f) { if ((W[f] || "") !== (B[f] || "")) e[f] = W[f] || ""; });
      var ws = byId(W.steps);
      B.steps.forEach(function (s) {
        var w = ws[s.id], x = {};
        if (!w) return;
        STEP_FIELDS.forEach(function (f) { if ((w[f] || "") !== (s[f] || "")) x[f] = w[f] || ""; });
        if (Object.keys(x).length) items[s.id] = x;
      });
      var bq = byId(B.qs);
      var bOrder = B.qs.map(function (q) { return q.id; }).join("|");
      var wOrder = W.qs.map(function (q) { return q.id; });
      if (wOrder.join("|") !== bOrder) e.qOrder = wOrder;
      W.qs.forEach(function (q) {
        var b = bq[q.id], x = {};
        if (!b) return;
        if ((q.q || "") !== (b.q || "")) x.q = q.q || "";
        if (hasKey(b) && (q.why || "") !== (b.why || "")) x.why = q.why || "";
        var bo = byId(b.options), oc = {};
        (q.options || []).forEach(function (o) { if (bo[o.id] && o.text !== bo[o.id].text) oc[o.id] = o.text; });
        if (Object.keys(oc).length) x.options = oc;
        var br = byId(b.rows), rc = {};
        (q.rows || []).forEach(function (r) { if (br[r.id] && r.label !== br[r.id].label) rc[r.id] = r.label; });
        if (Object.keys(rc).length) x.rows = rc;
        if (hasKey(b) && JSON.stringify(q.correct) !== JSON.stringify(b.correct)) x.correct = clone(q.correct);
        if (Object.keys(x).length) items[q.id] = x;
      });
      if (Object.keys(items).length) e.items = items;
      if (Object.keys(e).length) out.lessons[B.n] = e;
    });
    return out;
  }

  // validate(work) -> רשימת שגיאות שחוסמות את ההחלה.
  function validate(work) {
    var errs = [];
    work.forEach(function (L) {
      var p = "שיעור " + L.n + ": ";
      LESSON_FIELDS.forEach(function (f) {
        if (L[f] !== undefined && !String(L[f]).trim()) errs.push(p + (f === "goal" ? "המטרה" : "מה מגישים") + " לא יכול להיות ריק.");
      });
      L.steps.forEach(function (s, i) {
        if (!String(s.t || "").trim()) errs.push(p + "בצעד " + (i + 1) + " חסר טקסט.");
        if (!String(s.e || "").trim()) errs.push(p + "בצעד " + (i + 1) + " חסר \"מה אמור להופיע\".");
      });
      L.qs.forEach(function (q, i) {
        var n = p + "שאלה " + (i + 1) + " (" + q.id + ") ";
        if (!String(q.q || "").trim()) errs.push(n + "בלי ניסוח.");
        (q.options || []).forEach(function (o) { if (!String(o.text || "").trim()) errs.push(n + "יש אפשרות ריקה (" + o.id + ")."); });
        (q.rows || []).forEach(function (r) { if (!String(r.label || "").trim()) errs.push(n + "יש שורה ריקה (" + r.id + ")."); });
        if (hasKey(q) && !correctValid(q, q.correct)) errs.push(n + "התשובה הנכונה אינה אחת האפשרויות.");
      });
    });
    return errs;
  }

  // אזהרות: טקסטים שמזכירים מספר שאלה, כשסדר השאלות השתנה.
  function orderWarnings(base, work) {
    var warn = [], bm = {};
    base.forEach(function (B) { bm[B.n] = B; });
    work.forEach(function (W) {
      var B = bm[W.n];
      if (!B) return;
      if (W.qs.map(function (q) { return q.id; }).join("|") === B.qs.map(function (q) { return q.id; }).join("|")) return;
      var re = /שאל(?:ה|ות)\s+\d/;
      var texts = [["מה מגישים", W.submit || ""]];
      W.qs.forEach(function (q, i) { texts.push(["שאלה " + (i + 1), q.q || ""]); });
      W.steps.forEach(function (s, i) { texts.push(["צעד " + (i + 1), s.t || ""]); });
      texts.forEach(function (t) {
        if (re.test(t[1])) warn.push("שיעור " + W.n + ", " + t[0] + ": הטקסט מזכיר מספר שאלה, והסדר השתנה. כדאי לבדוק שהמספר עדיין נכון.");
      });
    });
    return warn;
  }

  var api = { apply: apply, diff: diff, validate: validate, orderWarnings: orderWarnings, correctValid: correctValid, hasKey: hasKey, version: 1 };
  root.PBIEdits = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : this);
