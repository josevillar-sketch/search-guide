#!/usr/bin/env python3
"""Builds the three printable one-pagers in this folder. Run: python3 classroom/build.py"""
import pathlib
HERE = pathlib.Path(__file__).parent
CSS = """
@page{size:letter;margin:.55in}
*{box-sizing:border-box}
html{font:10.4pt/1.38 Georgia,'Times New Roman',serif;color:#1c1b19;background:#f4f1ea}
body{max-width:7.4in;margin:0 auto;padding:.4in .25in;background:#fff}
h1{font:700 20pt/1.1 'Helvetica Neue',Arial,sans-serif;margin:0 0 2pt;letter-spacing:-.01em}
h2{font:700 11.5pt/1.2 'Helvetica Neue',Arial,sans-serif;margin:0 0 4pt}
h3{font:700 9pt/1.2 'Helvetica Neue',Arial,sans-serif;text-transform:uppercase;letter-spacing:.06em;margin:8pt 0 2pt;color:#5b564c}
p{margin:0 0 5pt} ul,ol{margin:0 0 5pt;padding-left:15pt} li{margin-bottom:2pt}
.kicker{font:700 8pt/1 'Helvetica Neue',Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#8a5a00;margin-bottom:5pt}
.lede{font-size:11pt;margin-bottom:9pt}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10pt}
.card{border:1.2pt solid #1c1b19;border-radius:5pt;padding:9pt 10pt}
.card.a{border-top:5pt solid #a3470f}.card.b{border-top:5pt solid #17557a}
.band{background:#f3efe4;border-radius:5pt;padding:7pt 10pt;margin:8pt 0}
.rule{font:700 9.2pt/1.3 'Helvetica Neue',Arial,sans-serif;border:1.2pt solid #1c1b19;padding:6pt 9pt;border-radius:5pt;margin:8pt 0}
.foot{font:8pt/1.3 'Helvetica Neue',Arial,sans-serif;color:#6b665b;margin-top:8pt;border-top:.6pt solid #bbb;padding-top:4pt}
table{width:100%;border-collapse:collapse;margin:6pt 0}
th,td{border:.9pt solid #1c1b19;padding:5pt 6pt;vertical-align:top;text-align:left}
th{font:700 9.2pt/1.2 'Helvetica Neue',Arial,sans-serif;background:#f3efe4}
td.q{font:700 9.5pt/1.2 'Helvetica Neue',Arial,sans-serif;width:1.15in;background:#faf8f2}
td.q small{display:block;font-weight:400;color:#5b564c;margin-top:2pt}
.blank td{height:.98in}.blank td.q{height:auto}
.line{border-bottom:.8pt solid #1c1b19;height:17pt;margin-bottom:2pt}
.name{display:flex;gap:14pt;font:9pt 'Helvetica Neue',Arial,sans-serif;margin:4pt 0 8pt}
.name span{flex:1;border-bottom:.8pt solid #1c1b19;padding-bottom:10pt}
code{font:9.2pt ui-monospace,Menlo,Consolas,monospace;background:#f3efe4;padding:0 3pt;border-radius:2pt}
.page{break-after:page}.page:last-child{break-after:auto}
.ex{font-style:italic;color:#3d3a33}
@media print{html,body{background:#fff}body{padding:0;max-width:none}}
@media (max-width:640px){.two{grid-template-columns:1fr}body{padding:16px}}
"""
def page(fn, title, body):
    (HERE/fn).write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{CSS}</style></head><body>
{body}
</body></html>
""", encoding="utf-8")

FOOT = '<div class="foot">Room 63 · AP Research · Mater Academy · Mr. Portela · {x}</div>'

# ---------- 1. Own data or public data? ----------
page("own-data-or-public-data.html", "Own data or public data?", f"""
<style>html{{font-size:10pt}}.card{{padding:7pt 9pt}}.band{{margin:6pt 0}}</style>
<div class="kicker">AP Research · Choosing a method</div>
<h1>Own data or public data?</h1>
<p class="lede">Two roads can lead to evidence for your paper. This page does not change your question. Your question is the one in your log.</p>
<div class="band"><b>Ask first:</b> does the evidence you need already exist? Spend twenty minutes looking before you decide to collect anything. Search the SDA archive, the Pew Research Center datasets, and Google Dataset Search. All three are in the Research Library.</div>
<div class="two">
<div class="card a"><h2>Road A · Collect your own data</h2>
<p>Surveys, interviews, observations, or an experiment that <b>you</b> run with people.</p>
<h3>Before you collect anything</h3>
<ol><li>Risk screen: who takes part, what they do, what could go wrong.</li>
<li>Consent form for adults. For anyone under 18: a guardian's permission <b>and</b> the student's own assent.</li>
<li>Data plan: where the data lives, who sees it, when you delete it.</li>
<li>Mr. Portela's approval of your proposal <b>and</b> every survey or interview question, with the date you may start. A College Board rule.</li></ol>
<h3>What you gain</h3><ul><li>Data shaped to your question.</li><li>A population you can reach: your school or community.</li></ul>
<h3>What it costs</h3><ul><li>Review takes time. Ask Mr. Portela how long it takes this year, then count backward from your deadline.</li><li>Small samples. You must say what a small sample cannot show.</li><li>Limits. A study with more than minimal risk cannot be approved.</li><li>To publish, compete, or present publicly, you also need a registered review board. Say so early.</li></ul></div>
<div class="card b"><h2>Road B · Analyze public data</h2>
<p>Data someone else already collected and released, with every person's identity removed.</p>
<h3>Before you analyze anything</h3>
<ol><li>Your risk screen still gets filled in. It records that your study has no human participants.</li>
<li>Read the codebook: the exact question people were asked, the answer choices, the years.</li>
<li>Save the file or table you export. It is your data file.</li>
<li>Record the dataset's name, release, and the date you used it.</li></ol>
<h3>What you gain</h3><ul><li>Thousands of respondents instead of dozens.</li><li>Change over time. The General Social Survey starts in 1972.</li><li>No consent forms, because you contact no one.</li></ul>
<h3>What it costs</h3><ul><li>You can only use the questions that were asked, in the words they were asked.</li><li>The people surveyed may not be your population. The General Social Survey covers U.S. adults, not teenagers.</li></ul></div>
</div>
<div class="band"><b>A third road:</b> analyzing published texts or media, such as news articles, speeches, or advertisements. Texts are not participants. Posts by private people are different, so ask before using social media.</div>
<div class="rule">On every road: each number in your paper traces to your own file · you justify your method with a methods text you cite · you state what your data cannot show.</div>
<h3>My decision today (it can change)</h3><div class="line"></div>
{FOOT.format(x="Own data or public data?")}
""")

# ---------- 2. Method planning grid ----------
ROWS = [("Why?","Why this method fits your question. Why this and not another method."),
        ("What?","The instrument and how long it takes one person."),
        ("When?","Dates, and how many times."),
        ("Who?","Who you gather data from, how many, how you reach them."),
        ("After gathering data","How you will analyze it and what you will compare.")]
def grid(cells=None, blank=True):
    out = ['<table class="%s"><tr><th></th><th>Method 1: ____________________</th><th>Method 2 (if you use one): ____________</th></tr>' % ("blank" if blank else "")]
    if cells: out[0] = '<table><tr><th></th><th>Method 1: %s</th><th>Method 2: %s</th></tr>' % cells[0]
    for i,(q,h) in enumerate(ROWS):
        a,b = (cells[i+1] if cells else ("",""))
        out.append(f'<tr><td class="q">{q}<small>{h}</small></td><td class="ex">{a}</td><td class="ex">{b}</td></tr>')
    return "\n".join(out)+"</table>"
EX = [("Short questionnaire","One-to-one interviews"),
 ("To get counts: how often people use the room and at what times.","To learn the reasons behind the counts. Interviews, not a focus group, because schedules are personal and people speak more freely alone."),
 ("12 questions on paper. About 5 minutes.","6 open questions. About 15 minutes. Notes by hand, no recording."),
 ("One week, once per person, after approval is logged.","The week after the questionnaires come back."),
 ("Students who use the room. Guardian permission and student assent first. Aim: every user that week.","Volunteers from the questionnaire group. Aim: 5 or 6."),
 ("Tally each answer. Compare by grade level. Report every count with its total.","Code the notes for repeated reasons. Report each theme with how many people raised it."),]
page("method-planning-grid.html", "Method planning grid", f"""
<section class="page"><div class="kicker">AP Research · Plan before you write the method section</div>
<h1>Method planning grid</h1>
<div class="name"><span>Student code</span><span>Period</span><span>Date</span></div>
<p>Copy your question from your log, word for word. Then plan each method in its own column. One method is fine: leave the second column empty.</p>
<div class="line"></div><div class="line"></div>
{grid()}
<div class="two"><div><h3>Approval I need before I start</h3><div class="line"></div></div><div><h3>Methods text I will cite to justify this</h3><div class="line"></div></div></div>
{FOOT.format(x="Method planning grid · page 1")}</section>
<section class="page"><div class="kicker">Example only · do not copy</div>
<h1>What a filled-in grid looks like</h1>
<p class="lede">The topic here is invented to show the level of detail: <i>how students use the library's quiet study room</i>. Your grid comes from your own question.</p>
{grid(EX, blank=False)}
<div class="band"><b>What to notice.</b> Every "why" names a reason, and one rejects an alternative. The second method explains the first: the interviews give reasons for the counts. The "who" for Method 2 comes out of Method 1. Each "after" says what will be compared and how it will be reported.</div>
<div class="rule">If two methods do not connect, you have two small studies. Ask: what does Method 2 tell me that Method 1 cannot?</div>
<h3>Check your own grid</h3>
<ul><li>Could a classmate run my study from this page alone?</li><li>Does each "why" give a reason, not a description?</li><li>Is the time I ask of each person stated?</li><li>Do I know what approval I need, and have I allowed time for it?</li><li>Can I name what my data will <b>not</b> be able to show?</li></ul>
{FOOT.format(x="Method planning grid · page 2")}</section>
""")

# ---------- 3. SDA lab ----------
page("sda-lab.html", "SDA lab: national survey data in one period", f"""
<section class="page"><div class="kicker">Teacher page · one 45-minute period</div>
<h1>SDA lab: national survey data in one period</h1>
<p class="lede">Students learn to find a variable in the General Social Survey, read its codebook entry, run one table, and save it. Nobody's question is rewritten. The lab only shows what public data exists.</p>
<h3>Setup</h3>
<ul><li>Go to <code>sda.berkeley.edu</code>, choose <b>Archive</b>, then <b>General Social Survey (GSS) Cumulative Datafile 1972-2024 - release 3 (SDA 4)</b>. No login.</li>
<li>Test once on a student iPad before class. Results open in a new tab, so pop-ups must be allowed.</li></ul>
<h3>Run of the period</h3>
<table><tr><th style="width:.7in">Minutes</th><th>What happens</th></tr>
<tr><td>0 to 5</td><td>Frame it: real researchers reuse data. Thousands of adults answered these questions, and the answers are free. Hand out the student sheet.</td></tr>
<tr><td>5 to 15</td><td><b>Demo on the board.</b> Type <code>consci</code> in <b>Row</b> and <code>degree</code> in <b>Column</b>. Leave the weight as it is. Press <b>Run the Table</b>. Then open the <b>Codebook</b> tab and show the exact question for <code>consci</code>.</td></tr>
<tr><td>15 to 35</td><td>Students work through steps 1 to 5 on their sheet. Circulate. The common snag is a variable that was only asked in some years.</td></tr>
<tr><td>35 to 45</td><td>Students finish the record box and the two exit lines. Collect the sheets.</td></tr></table>
<h3>What the demo should show</h3>
<p>Confidence in the scientific community, by highest degree. In the row "a great deal," the column percentages rise from <b>34.6</b> for less than high school to <b>60.5</b> for a graduate degree. Valid cases: <b>47,772</b>. Checked on November 11, 2026. A newer data release may shift these slightly.</p>
<h3>Three things to say out loud</h3>
<ul><li><b>Read down, compare across.</b> Each column adds to 100. Compare the same row across columns.</li>
<li><b>A pattern is not a cause.</b> The table shows that two answers go together. It cannot show that one produces the other.</li>
<li><b>The question is the measurement.</b> Whatever the survey asked, in those exact words, is what the number means.</li></ul>
<h3>Useful moves</h3>
<ul><li>Change over time: put <code>year</code> in <b>Column</b>.</li>
<li>Recent years only: type <code>year(2018-2024)</code> in <b>Selection Filter(s)</b>.</li>
<li>Save the table: open <b>Create and Download CSV File</b> before running. Charts are under <b>Chart Options</b>.</li></ul>
<div class="rule">Rule for this lab: a student may discover that a dataset fits their question, or that it does not. The lab never suggests new wording for a question.</div>
{FOOT.format(x="SDA lab · teacher page")}</section>
<section class="page"><div class="kicker">Student sheet · SDA lab</div>
<h1>Find it, read it, run it, save it</h1>
<div class="name"><span>Student code</span><span>Period</span><span>Date</span></div>
<ol>
<li><b>Open the data.</b> <code>sda.berkeley.edu</code>, then Archive, then the General Social Survey 1972-2024, release 3.</li>
<li><b>Search.</b> Use the <b>Search</b> tab. Try key words from your own question as it stands in your log. Do not change your question to fit a variable. If nothing fits, write "no match" below. That is a real finding.</li>
<li><b>Read the codebook</b> for one variable. Find the exact question people were asked and the answer choices.</li>
<li><b>Run one table.</b> Your variable goes in <b>Row</b>. Put a group to compare, such as <code>degree</code>, <code>sex</code>, or <code>year</code>, in <b>Column</b>. Press <b>Run the Table</b>.</li>
<li><b>Save it.</b> Run it again with <b>Create and Download CSV File</b> open, or screenshot the table. This file is your data.</li>
</ol>
<table>
<tr><th colspan="2">Record box: copy from the screen, exactly</th></tr>
<tr><td class="q">Dataset and release</td><td style="height:.36in"></td></tr>
<tr><td class="q">Variable name and label</td><td style="height:.36in"></td></tr>
<tr><td class="q">Exact question asked<small>from the codebook</small></td><td style="height:.7in"></td></tr>
<tr><td class="q">Answer choices</td><td style="height:.42in"></td></tr>
<tr><td class="q">Years it was asked</td><td style="height:.36in"></td></tr>
<tr><td class="q">Column variable</td><td style="height:.36in"></td></tr>
<tr><td class="q">Valid cases<small>bottom of the results</small></td><td style="height:.36in"></td></tr>
<tr><td class="q">Weight shown</td><td style="height:.36in"></td></tr>
</table>
<h3>One thing this table shows (give the numbers)</h3><div class="line"></div><div class="line"></div>
<h3>One thing this table cannot show</h3><div class="line"></div><div class="line"></div>
<div class="band">If you use this in your paper: cite the General Social Survey (NORC at the University of Chicago, gss.norc.org) in the class citation style. Give the release from your record box, and say you analyzed it through SDA on today's date.</div>
{FOOT.format(x="SDA lab · student sheet")}</section>
""")

# ---------- 4. Method section checklist ----------
def checks(items):
    return "<table>"+"".join(f'<tr><td style="width:.34in;text-align:center;font-size:13pt">&#9744;</td><td><b>{a}</b> {b}</td></tr>' for a,b in items)+"</table>"
page("method-section-checklist.html", "Method section checklist", f"""
<div class="kicker">AP Research · Academic paper · Self-check, then peer check</div>
<h1>Method section checklist</h1>
<div class="name"><span>Writer's code</span><span>Reader's code</span><span>Date</span></div>
<div class="band"><b>What College Board asks of this section:</b> it "explains and provides justification for the chosen method, process, or approach and its alignment with the research question." Two verbs, <b>explain</b> and <b>justify</b>, and one test, <b>alignment</b>.</div>
<div class="two"><div>
<h3>Explain: could a reader repeat it?</h3>
{checks([("Who or what.","Who or what was studied, how many, and how they were chosen."),
("Instrument.","The survey, interview guide, dataset, or texts are described. The full instrument is in an appendix."),
("Steps.","What was done, in order, with dates and how long each part took."),
("Analysis.","How the data was analyzed, named plainly: counts, a comparison, coding for themes.")])}
<h3>Ethics: is it on the page?</h3>
{checks([("Approval.","Says the study was approved before any data was collected."),
("Consent and privacy.","Says how people agreed to take part and how their identities are protected. For public data: says no participants were contacted.")])}
</div><div>
<h3>Justify: why this, and not something else?</h3>
{checks([("Alignment.","One or two sentences connect the method to the research question in the writer's own words."),
("The road not taken.","Names at least one other method and gives a reason it was not used."),
("A methods source.","Cites a methods text or a published study for the choice. A blog or infographic does not count."),
("Limits.","Names what this method cannot show. Small sample, one school, one year, self-report.")])}
<h3>Evidence: can it be traced?</h3>
{checks([("Every number.","Each number in the section matches the writer's own data file."),
("Nothing borrowed.","No number, example, or wording comes from a sample paper or a template.")])}
</div></div>
<h3>Reader: one place I could not follow (ask a question; do not rewrite it)</h3><div class="line"></div><div class="line"></div>
<h3>Writer: what I will change, in my own words</h3><div class="line"></div><div class="line"></div>
<div class="rule">Readers ask questions and point to gaps. They do not write, rewrite, or suggest wording. The paper is the writer's own work.</div>
{FOOT.format(x="Method section checklist")}
""")

# ---------- 5. Research Library (student page; published as an artifact) ----------
# Every link here must also be in the verified part of RESOURCES.md; tools/check_links.py enforces it.
NEEDS = [("start","Start here"),("data","Find data that already exists"),("method","Choose and justify a method"),
         ("people","Study people safely"),("analyze","Analyze what you collected"),("cite","Cite it")]
TAGS = {"cite":"Cite it in your paper","nocite":"Read it, do not cite it","ask":"Ask Mr. Portela first","tool":"Tool"}
LIB = [
 ("start","cite","AP Research Course and Exam Description","College Board","https://apcentral.collegeboard.org/media/pdf/ap-research-course-and-exam-description.pdf",
  "The rules of the course and the rubrics your paper and presentation are scored on.","Read the rubric for the paper before you draft anything."),
 ("start","nocite","Scored student papers, 2023 to 2026","College Board","https://apcentral.collegeboard.org/courses/ap-research/exam/past-exam-questions",
  "Real papers and presentations with the scores they earned and the reasons.","Study how strong papers are built. Never borrow their wording, numbers, or questions."),
 ("start","nocite","Guidance for AI tools","College Board","https://apcentral.collegeboard.org/exam-administration-ordering-scores/administering-exams/exam-policies/artificial-intelligence-tools",
  "What you may and may not use AI for in AP Capstone.","Read it before you use any AI tool for this course."),
 ("data","cite","SDA: Survey Documentation and Analysis","UC Berkeley","https://sda.berkeley.edu/archive.htm",
  "National survey data you can analyze in your browser. No login. Includes the General Social Survey since 1972.","Read the codebook first. You can only use the questions that were asked."),
 ("data","cite","General Social Survey","NORC at the University of Chicago","https://gss.norc.org/",
  "The survey's own site: the exact questionnaires and a list of studies that used it.","Use it to see how each question was worded."),
 ("data","tool","Google Dataset Search","Google","https://datasetsearch.research.google.com/",
  "A search engine for datasets. Use it to find out whether data on your topic already exists.","It finds data. You still judge who collected it, from whom, and when."),
 ("data","ask","Pew Research Center datasets","Pew Research Center","https://www.pewresearch.org/datasets/",
  "Raw data behind Pew's national surveys.","Downloading needs an account, and Pew's terms limit how the data is reused. Ask first."),
 ("data","ask","IPUMS USA","University of Minnesota","https://usa.ipums.org/usa/",
  "Census data on households, work, language, and migration.","Needs a registered account, and the files are large. SDA's census files are the easier start."),
 ("data","cite","CDC WONDER","Centers for Disease Control and Prevention","https://wonder.cdc.gov/",
  "Public health counts and rates: births, deaths, and more, by year, place, age, and sex.","Small local counts are hidden. Write down the exact query you ran."),
 ("method","cite","Social Science Research: Principles, Methods, and Practices","Anol Bhattacherjee, University of South Florida","https://digitalcommons.usf.edu/oa_textbooks/3/",
  "A free textbook on the whole research process. Use it to justify the method you chose.","Written for graduate students. Read the chapter you need, not the whole book."),
 ("method","cite","OpenIntro Statistics","OpenIntro","https://www.openintro.org/book/os/",
  "A free statistics textbook. Use it when you must explain a mean, a comparison, or a correlation.","College level. Check the edition on the title page before you cite it."),
 ("method","nocite","Types of research methods","Litmaps blog","https://www.litmaps.com/articles/types-of-research-methods",
  "A plain overview of qualitative, quantitative, and mixed methods.","A company blog with no sources. Use it to get oriented, then cite a real methods text."),
 ("people","ask","Room 63 consent and assent forms","Mr. Portela","",
  "The forms for a guardian's permission, a student's own agreement, and adult consent, in English and Spanish.","No form goes out, and no data is collected, until your proposal and questions are approved."),
 ("people","nocite","Informed consent templates and guidance","UC Berkeley","https://cphs.berkeley.edu/informedconsent.html",
  "What a real university consent form contains, with a checklist.","Models only. A form must never suggest that Berkeley approved your study."),
 ("analyze","tool","jamovi","jamovi project","https://www.jamovi.org/",
  "Free statistics software that works like a spreadsheet.","Use coded data only: no names in any file you upload. You still have to justify the test you run."),
 ("analyze","tool","Taguette","Taguette project","https://www.taguette.org/",
  "A free tool for coding interviews and open-ended answers: highlight a passage, give it a tag.","Use the installed version, not the web version, for anything from participants."),
 ("cite","tool","ZoteroBib","Zotero","https://zbib.org/",
  "A free bibliography builder. No account. Paste a title or link, pick the class style.","It saves only on that device. Copy your list out before you leave a shared iPad. Check every entry."),
]
def card(need,tag,title,who,url,what,care):
    head = f'<a href="{url}" target="_blank" rel="noopener">{title}</a>' if url else title
    host = url.split('/')[2].replace('www.','') if url else 'ask in Room 63'
    return (f'<li class="item" data-need="{need}"><div class="top"><span class="tag t-{tag}">{TAGS[tag]}</span>'
            f'<span class="host">{host}</span></div><h3>{head}</h3><p class="who">{who}</p>'
            f'<p>{what}</p><p class="care"><b>Mind this.</b> {care}</p></li>')
sections = "".join(
    f'<section class="need" id="{k}" data-need="{k}"><h2>{label}</h2><ul class="items">'
    + "".join(card(*r) for r in LIB if r[0]==k) + '</ul></section>' for k,label in NEEDS)
chips = '<button type="button" class="chip" id="chip-all" data-need="all" aria-pressed="true">Everything</button>' + "".join(
    f'<button type="button" class="chip" id="chip-{k}" data-need="{k}" aria-pressed="false">{label}</button>' for k,label in NEEDS)
(HERE/"research-library.html").write_text(f"""<title>Room 63 Research Library</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,650;9..144,900&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Space+Mono:wght@400;700&display=swap">
<style>
/* Layout: one reading column of index cards, grouped by what the student needs to do next. Same paper, brass and pine as the Room 63 Search Guide. */
:root{{--ground:#ece4d2;--card:#fbf7ee;--card-2:#f3ead6;--ink:#1d1812;--ink-soft:#4a3f31;--hair:#c9b996;--edge:#7d6a45;--brass-text:#6d4f14;--pine:#245e55;--on-pine:#fbf7ee;--oxide:#9c3322;--plum:#6d3a73;--focus:#245e55;
--display:"Fraunces",Georgia,"Times New Roman",serif;--body:"Atkinson Hyperlegible",Verdana,system-ui,sans-serif;--mono:"Space Mono","Courier New",ui-monospace,monospace}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--ground:#07201b;--card:#0f2a25;--card-2:#15392f;--ink:#f3ead6;--ink-soft:#c9bb9c;--hair:#2f5a50;--edge:#b8995a;--brass-text:#e2b964;--pine:#7fd1c0;--on-pine:#07201b;--oxide:#f08a74;--plum:#d9a5dc;--focus:#f0c56a;color-scheme:dark}}}}
:root[data-theme="dark"]{{--ground:#07201b;--card:#0f2a25;--card-2:#15392f;--ink:#f3ead6;--ink-soft:#c9bb9c;--hair:#2f5a50;--edge:#b8995a;--brass-text:#e2b964;--pine:#7fd1c0;--on-pine:#07201b;--oxide:#f08a74;--plum:#d9a5dc;--focus:#f0c56a;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{background:var(--ground);color:var(--ink);font:1.0625rem/1.5 var(--body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:1.5rem 3rem}}
.wrap{{max-width:44rem;margin:0 auto;display:flex;flex-direction:column;gap:1.5rem}}
.eyebrow{{font:700 .75rem/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--brass-text);margin:0 0 .6rem}}
h1{{font:900 clamp(2rem,7vw,3rem)/1.02 var(--display);margin:0 0 .6rem;text-wrap:balance;letter-spacing:-.01em}}
.lede{{margin:0;color:var(--ink-soft);max-width:36rem}}
.rule{{border:2px solid var(--ink);background:var(--card);padding:.8rem 1rem;font-weight:700}}
.rule span{{display:block;font-weight:400;color:var(--ink-soft);margin-top:.25rem}}
.chips{{display:flex;flex-wrap:wrap;gap:.5rem}}
.chip{{font:700 .9rem/1.2 var(--body);padding:.55rem .8rem;border:1.5px solid var(--edge);background:transparent;color:var(--ink);border-radius:999px;cursor:pointer;min-height:44px}}
.chip[aria-pressed="true"]{{background:var(--pine);border-color:var(--pine);color:var(--on-pine)}}
.chip:focus-visible,a:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.need h2{{font:650 1.45rem/1.15 var(--display);margin:0 0 .75rem;padding-bottom:.4rem;border-bottom:1.5px solid var(--hair);text-wrap:balance}}
.items{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:.75rem}}
.item{{background:var(--card);border:1px solid var(--hair);padding:.9rem 1rem;min-width:0}}
.top{{display:flex;flex-wrap:wrap;gap:.5rem;justify-content:space-between;align-items:center;margin-bottom:.5rem}}
.tag{{font:700 .72rem/1 var(--mono);letter-spacing:.04em;text-transform:uppercase;padding:.3rem .45rem;border:1.5px solid currentColor}}
.t-cite{{color:var(--pine)}}.t-nocite{{color:var(--oxide)}}.t-ask{{color:var(--plum)}}.t-tool{{color:var(--brass-text)}}
.host{{font:.75rem/1 var(--mono);color:var(--ink-soft);overflow-wrap:anywhere}}
.item h3{{font:650 1.15rem/1.25 var(--display);margin:0 0 .15rem}}
.item a{{color:var(--ink);text-decoration-color:var(--edge);text-underline-offset:.18em}}
.item p{{margin:.35rem 0 0}}
.who{{color:var(--ink-soft);font-size:.92rem}}
.care{{background:var(--card-2);padding:.5rem .65rem;font-size:.95rem}}
.no{{border:2px solid var(--oxide);padding:.9rem 1rem;background:var(--card)}}
.no h2{{font:650 1.2rem/1.2 var(--display);margin:0 0 .3rem;color:var(--oxide)}}
.no p{{margin:0}}
footer{{font:.78rem/1.5 var(--mono);color:var(--ink-soft);border-top:1.5px solid var(--hair);padding-top:.8rem}}
@media (prefers-reduced-motion:no-preference){{.chip{{transition:background .15s,color .15s}}}}
</style>
<div class="wrap">
<header>
<p class="eyebrow">Room 63 · AP Research · Mr. Portela</p>
<h1>Research Library</h1>
<p class="lede">Every source and tool here was opened and checked. Each card says what it is for, whether you may cite it, and what to watch out for. To find sources on your own topic, use your Search Guide slip.</p>
</header>
<p class="rule">Nothing here writes or changes your research question.<span>Your question is the one in your log. These tools help you answer it.</span></p>
<nav class="chips" aria-label="Show one need">{chips}</nav>
{sections}
<section class="no"><h2>Do not use</h2><p><b>PapersOwl</b> and sites like it. Their advice pages sell papers written for you. College Board requires your paper to be your own work.</p></section>
<footer>{len(LIB)} entries · checked November 2026 · If a link breaks, tell Mr. Portela.</footer>
</div>
<script>
(function(){{
  var chips=[].slice.call(document.querySelectorAll('.chip')),secs=[].slice.call(document.querySelectorAll('.need'));
  function show(n){{
    chips.forEach(function(c){{c.setAttribute('aria-pressed',String(c.dataset.need===n));}});
    secs.forEach(function(s){{s.hidden=!(n==='all'||s.dataset.need===n);}});
    try{{localStorage.setItem('r63lib_need',n);}}catch(e){{}}
  }}
  chips.forEach(function(c){{c.addEventListener('click',function(){{show(c.dataset.need);}});}});
  var saved='all';try{{saved=localStorage.getItem('r63lib_need')||'all';}}catch(e){{}}
  if(!chips.some(function(c){{return c.dataset.need===saved;}}))saved='all';
  show(saved);
}})();
</script>
""", encoding="utf-8")
print("built", len(LIB), "library entries")
