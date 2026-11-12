#!/usr/bin/env python3
"""Builds the printable handouts and the Research Library page in this folder.
Run: python3 classroom/build.py, then node classroom/build-pdf.cjs to print the PDFs and check their page counts."""
import pathlib
HERE = pathlib.Path(__file__).parent
CSS = """
/* Room 63 print register. Same ink, brass and pine, and the same three faces, as the Search Guide and the Research Library.
   Each .page is one letter sheet. On screen it shows as a sheet of paper; in print the sheet is the page.
   Every tinted block also carries a rule or border, so a printer with background graphics off loses nothing. */
@page{size:letter;margin:.5in .55in}
:root{--ink:#1d1812;--soft:#4a3f31;--hair:#c9b996;--brass:#6d4f14;--pine:#245e55;--oxide:#9c3322;--tint:#f3ead6;--tint-2:#fbf7ee;--ground:#ece4d2;
  --display:"Fraunces",Georgia,"Times New Roman",serif;--body:"Atkinson Hyperlegible",Verdana,system-ui,sans-serif;--mono:"Space Mono","Courier New",ui-monospace,monospace;color-scheme:light}
*{box-sizing:border-box}
html{font:10pt/1.4 var(--body);color:var(--ink);background:var(--ground);-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;padding:24px 16px 40px}
.page{position:relative;background:#fff;max-width:8.5in;margin:0 auto 24px;padding:.5in .55in;border:1px solid var(--hair);break-after:page}
.page:last-child{break-after:auto;margin-bottom:0}
.page::before{content:"63";position:absolute;top:.5in;right:.55in;width:2.9rem;height:2.9rem;border:.12rem solid var(--ink);border-radius:50%;outline:.06rem solid var(--ink);outline-offset:-.32rem;
  display:grid;place-items:center;font:900 1.15rem/1 var(--display);letter-spacing:-.02em}
.kicker{font:700 .74rem/1.3 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--brass);margin:0 3.6rem .35rem 0}
h1{font:900 2.5rem/1.02 var(--display);letter-spacing:-.015em;margin:0 0 .8rem;padding-right:3.6rem;text-wrap:balance}
h1::after{content:"";display:block;margin:.6rem -3.6rem 0 0;height:.34rem;border-top:.2rem solid var(--ink);border-bottom:.06rem solid var(--ink)}
h2{font:650 1.3rem/1.15 var(--display);margin:0 0 .4rem;text-wrap:balance}
h3{font:700 .74rem/1.3 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--soft);margin:.8rem 0 .3rem}
p{margin:0 0 .5rem} ul,ol{margin:0 0 .5rem;padding-left:1.5rem} li{margin-bottom:.2rem}
li::marker{font-weight:700;color:var(--brass)}
b{font-weight:700}
.lede{font-size:1.1rem;line-height:1.38;margin-bottom:.8rem;max-width:44rem}
.two{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
.card{border:.1rem solid var(--ink);padding:.85rem 1rem}
.card.a{border-top:.45rem solid var(--oxide)}.card.b{border-top:.45rem solid var(--pine)}
.band{background:var(--tint);border-left:.3rem solid var(--brass);padding:.6rem .9rem;margin:.8rem 0}
.rule{font:700 .95rem/1.35 var(--body);border:.12rem solid var(--ink);border-left-width:.55rem;padding:.6rem .9rem;margin:.8rem 0}
.foot{font:400 .68rem/1.3 var(--mono);letter-spacing:.02em;color:var(--soft);margin-top:1.3rem;border-top:.08rem solid var(--ink);padding-top:.4rem}
table{width:100%;border-collapse:collapse;margin:.6rem 0}
th,td{border:.08rem solid var(--ink);padding:.5rem .6rem;vertical-align:top;text-align:left}
th{font:700 .92rem/1.2 var(--body);background:var(--tint);border-bottom-width:.16rem}
td.q{font:700 .95rem/1.2 var(--body);width:1.15in;background:var(--tint-2)}
td.q small{display:block;font-weight:400;font-size:.85rem;line-height:1.25;color:var(--soft);margin-top:.2rem}
.blank td{height:.98in}.blank td.q{height:auto}
td.tick{width:.34in;text-align:center}
.box{display:inline-block;width:1.05rem;height:1.05rem;border:.12rem solid var(--ink);vertical-align:-.15rem}
.line{border-bottom:.08rem solid var(--ink);height:18pt;margin-bottom:2pt}
.name{display:flex;gap:1.4rem;font:700 .7rem/1.3 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--soft);margin:.4rem 0 .8rem}
.name span{flex:1;border-bottom:.08rem solid var(--ink);padding-bottom:1.3rem}
code{font:400 .88rem/1 var(--mono);background:var(--tint);padding:.05rem .3rem}
.ex{font-style:italic;color:var(--soft)}
@media print{html{background:#fff}body{padding:0}.page{border:0;margin:0;padding:0;max-width:none}.page::before{top:0;right:0}}
@media screen and (prefers-color-scheme:dark){html{background:#07201b}.page{border-color:#2f5a50}}
@media screen and (max-width:640px){html{font-size:15px}body{padding:0}h1{font-size:2rem}.two{grid-template-columns:1fr}
  .page{border:0;border-bottom:12px solid var(--ground);margin:0;padding:20px 16px 24px}.page::before{top:20px;right:16px}}
@media screen and (max-width:640px) and (prefers-color-scheme:dark){.page{border-bottom-color:#07201b}}
"""
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,650;9..144,900'
         '&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Space+Mono:wght@400;700&display=swap">')
def page(fn, title, body):
    # One-sheet handouts are written without a wrapper; give them the same sheet as the two-page ones.
    if '<section class="page">' not in body:
        body = '<section class="page">' + body.strip() + '</section>'
    (HERE/fn).write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>{FONTS}<style>{CSS}</style></head><body>
{body}
</body></html>
""", encoding="utf-8")

FOOT = '<div class="foot">Room 63 · AP Research · Mater Academy · Mr. Portela · {x}</div>'

# ---------- 1. Own data or public data? ----------
page("own-data-or-public-data.html", "Own data or public data?", f"""
<style>/* This sheet carries the most text. Print it a step smaller so it stays on one page; build-pdf.cjs checks the count. */
@media print{{html{{font-size:9.4pt}}.card{{padding:.7rem .9rem}}.band,.rule{{margin:.6rem 0}}h3{{margin-top:.6rem}}}}</style>
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
<h3>My decision today (it can change)</h3><div class="line"></div><div class="line"></div>
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
<table><tr><th style="width:.9in">Minutes</th><th>What happens</th></tr>
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
    return "<table>"+"".join(f'<tr><td class="tick"><span class="box"></span></td><td><b>{a}</b> {b}</td></tr>' for a,b in items)+"</table>"
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
NEEDS = [("start","A","Start","Start here"),("data","B","Find data","Find data that already exists"),("method","C","Method","Choose and justify a method"),
         ("people","D","People","Study people safely"),("analyze","E","Analyze","Analyze what you collected"),("cite","F","Cite","Build your reference list")]
STAMPS = {"cite":("Cite it","s-pine","You may cite this in your paper."),"nocite":("Don't cite","s-oxide","Read it to learn. Cite something stronger."),"ask":("Ask first","s-plum","See Mr. Portela before you use it."),"tool":("Tool","s-brass","It does a job. You do the thinking.")}
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
def card(need,letter,n,tag,title,who,url,what,care):
    label,cls,_ = STAMPS[tag]
    host = url.split('/')[2].replace('www.','') if url else ''
    go = (f'<a class="open" href="{url}" target="_blank" rel="noopener" aria-label="Open {title}">Open {host} <span aria-hidden="true">&#8599;</span></a>'
          if url else '<span class="open none">Ask in Room 63</span>')
    return (f'<li class="card"><div class="card-top"><span class="callno">R63.{letter}.{n:02d}</span>'
            f'<span class="stamp {cls}">{label}</span></div><h3>{title}</h3><p class="who">{who}</p>'
            f'<p class="what">{what}</p><p class="care"><span class="care-l">Mind this</span>{care}</p>{go}</li>')
sections = ""
for k,letter,short,label in NEEDS:
    rows = [r for r in LIB if r[0]==k]
    sections += (f'<section class="drawer" id="{k}" data-need="{k}"><div class="plate"><span class="letter" aria-hidden="true">{letter}</span>'
                 f'<div><h2>{label}</h2><p class="count">Drawer {letter} · {len(rows)} {"card" if len(rows)==1 else "cards"}</p></div></div><ul class="cards">'
                 + "".join(card(k,letter,n,*r[1:]) for n,r in enumerate(rows,1)) + '</ul></section>')
chips = '<button type="button" class="chip" id="chip-all" data-need="all" aria-pressed="true">All</button>' + "".join(
    f'<button type="button" class="chip" id="chip-{k}" data-need="{k}" aria-pressed="false"><span class="chip-l" aria-hidden="true">{letter}</span>{short}</button>' for k,letter,short,label in NEEDS)
legend = "".join(f'<li><span class="stamp {cls}">{label}</span><span>{mean}</span></li>' for label,cls,mean in STAMPS.values())
(HERE/"research-library.html").write_text(f"""<title>Room 63 Research Library</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,650;9..144,900&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Space+Mono:wght@400;700&display=swap">
<style>
/* Layout: a card catalog. A loud masthead, then six lettered drawers; each resource is a paper catalog card with a call number and an inked stamp. The cards stay paper in both themes, as the Search Guide's own cards do. */
:root{{--ground:#ece4d2;--ink:#1d1812;--ink-soft:#4a3f31;--hair:#c9b996;--edge:#7d6a45;--brass-text:#6d4f14;--brass-fill:#d6ad55;--on-brass:#1d1812;--pine:#245e55;--on-pine:#fbf7ee;--focus:#245e55;--drop:#1d1812;
--paper:#fbf7ee;--paper-2:#f3ead6;--paper-ink:#1d1812;--paper-soft:#4a3f31;--paper-edge:#1d1812;--margin-red:#cf5b4c;--st-pine:#245e55;--st-oxide:#9c3322;--st-plum:#6d3a73;--st-brass:#6d4f14;
--display:"Fraunces",Georgia,"Times New Roman",serif;--body:"Atkinson Hyperlegible",Verdana,system-ui,sans-serif;--mono:"Space Mono","Courier New",ui-monospace,monospace}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--ground:#07201b;--ink:#f3ead6;--ink-soft:#c9bb9c;--hair:#2f5a50;--edge:#b8995a;--brass-text:#e2b964;--pine:#7fd1c0;--on-pine:#07201b;--focus:#f0c56a;--drop:#8f7336;color-scheme:dark}}}}
:root[data-theme="dark"]{{--ground:#07201b;--ink:#f3ead6;--ink-soft:#c9bb9c;--hair:#2f5a50;--edge:#b8995a;--brass-text:#e2b964;--pine:#7fd1c0;--on-pine:#07201b;--focus:#f0c56a;--drop:#8f7336;color-scheme:dark}}
*{{box-sizing:border-box}}
html{{scroll-padding-top:calc(76px + env(safe-area-inset-top,0px))}}
body{{background:var(--ground);color:var(--ink);font:400 1.0625rem/1.53 var(--body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:1.25rem 4rem}}
body::before{{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--ground)}}
.wrap{{max-width:62rem;margin:0 auto;display:flex;flex-direction:column;gap:2rem}}
a:focus-visible,button:focus-visible{{outline:3px solid var(--focus);outline-offset:3px}}

.mast{{display:flex;flex-direction:column;gap:1rem;border-bottom:3px solid var(--ink);padding-bottom:1.25rem}}
.eyebrow{{font:700 .8125rem/1.4 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--brass-text);margin:0}}
h1{{font:900 clamp(2.9rem,15.4vw,9rem)/.84 var(--display);text-transform:uppercase;letter-spacing:-.025em;margin:0;max-width:100%}}
h1 span{{display:block}}
h1 .l2{{color:var(--pine)}}
.strip{{display:flex;flex-wrap:wrap;gap:.25rem 1.25rem;font:700 .8125rem/1.5 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-soft);margin:0;padding:0;list-style:none}}
.lede{{margin:0;max-width:40rem;font-size:1.125rem;color:var(--ink)}}

.pledge{{background:var(--pine);color:var(--on-pine);padding:1.1rem 1.25rem;border-radius:6px;box-shadow:6px 6px 0 var(--drop);margin:0}}
.pledge b{{display:block;font:650 clamp(1.3rem,4.6vw,1.9rem)/1.12 var(--display);text-wrap:balance}}
.pledge span{{display:block;margin-top:.4rem}}

.legend{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem}}
.legend li{{display:flex;flex-direction:column;gap:.6rem;align-items:flex-start;min-width:0;background:var(--paper);color:var(--paper-ink);border:1.5px solid var(--paper-edge);border-radius:6px;padding:.8rem .8rem .7rem;font-size:.95rem;line-height:1.4}}
.legend .stamp{{flex:none}}

.tabs{{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--ground);margin-inline:-4px;padding:.6rem 4px .75rem;border-bottom:1.5px solid var(--hair)}}
.chips{{display:flex;gap:.6rem;overflow-x:auto;padding:2px 6px 6px 2px;scrollbar-width:thin}}
.chip{{flex:none;display:inline-flex;align-items:center;gap:.45rem;min-height:46px;padding:.5rem .9rem;background:var(--paper);color:var(--paper-ink);border:1.5px solid var(--paper-edge);border-radius:6px;box-shadow:4px 4px 0 var(--drop);font:700 1rem/1.2 var(--body);cursor:pointer}}
.chip-l{{font:700 .75rem/1 var(--mono);border:1.5px solid currentColor;border-radius:4px;padding:.2rem .32rem}}
.chip[aria-pressed="true"]{{background:var(--brass-fill);color:var(--on-brass);box-shadow:1px 1px 0 var(--drop);transform:translate(3px,3px)}}

.drawer{{display:grid;gap:1rem;min-width:0}}
.plate{{display:flex;gap:.9rem;align-items:center;min-width:0}}
.letter{{flex:none;display:grid;place-items:center;width:3.4rem;height:3.4rem;font:900 2.1rem/1 var(--display);color:var(--on-brass);background:var(--brass-fill);border:1.5px solid var(--paper-edge);border-radius:6px;box-shadow:4px 4px 0 var(--drop)}}
.plate h2{{font:900 clamp(1.45rem,5vw,2rem)/1.05 var(--display);text-transform:uppercase;letter-spacing:.01em;margin:0;text-wrap:balance}}
.count{{font:700 .8125rem/1.4 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-soft);margin:.25rem 0 0}}
.cards{{list-style:none;margin:0;padding:0;display:grid;gap:1.1rem;min-width:0}}

.card{{position:relative;background:var(--paper);color:var(--paper-ink);border:1.5px solid var(--paper-edge);border-radius:6px;box-shadow:6px 6px 0 var(--drop);padding:0 1.1rem 2.6rem;display:flex;flex-direction:column;gap:.5rem;min-width:0}}
.card::after{{content:"";position:absolute;left:50%;bottom:.75rem;width:.95rem;height:.95rem;margin-left:-.475rem;border-radius:50%;background:var(--ground);border:1.5px solid var(--paper-edge)}}
.card-top{{display:flex;flex-wrap:wrap;gap:.5rem 1rem;justify-content:space-between;align-items:center;margin-inline:-1.1rem;padding:.7rem 1.1rem .65rem;border-bottom:2px solid var(--margin-red)}}
.callno{{font:700 .8125rem/1 var(--mono);letter-spacing:.08em;color:var(--paper-soft)}}
.stamp{{display:inline-block;font:700 .78rem/1 var(--mono);letter-spacing:.13em;text-transform:uppercase;padding:.34rem .5rem .3rem;border:2px solid currentColor;border-radius:3px;outline:1px solid currentColor;outline-offset:2px;transform:rotate(-2.5deg);white-space:nowrap}}
.card:nth-child(even) .stamp{{transform:rotate(1.8deg)}}
.s-pine{{color:var(--st-pine)}}.s-oxide{{color:var(--st-oxide)}}.s-plum{{color:var(--st-plum)}}.s-brass{{color:var(--st-brass)}}
.card h3{{font:650 clamp(1.3rem,4.4vw,1.6rem)/1.15 var(--display);margin:.35rem 0 0;text-wrap:balance}}
.who{{font:400 .8125rem/1.45 var(--mono);letter-spacing:.03em;color:var(--paper-soft);margin:0}}
.what{{margin:.15rem 0 0;max-width:42rem}}
.care{{margin:.15rem 0 0;background:var(--paper-2);border-left:4px solid var(--paper-edge);padding:.55rem .75rem;max-width:42rem}}
.care-l{{display:block;font:700 .75rem/1.5 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--st-oxide)}}
.open{{align-self:flex-start;margin-top:.4rem;display:inline-flex;align-items:center;gap:.5rem;min-height:46px;padding:.55rem .95rem;font:700 1rem/1.2 var(--body);color:var(--paper-ink);background:transparent;border:1.5px solid var(--paper-edge);border-radius:6px;text-decoration:none;overflow-wrap:anywhere}}
a.open:hover{{background:var(--brass-fill);color:var(--on-brass)}}
.open.none{{border-style:dashed;color:var(--paper-soft)}}

.withdrawn{{background:var(--paper);color:var(--paper-ink);border:2px solid var(--st-oxide);border-radius:6px;padding:1rem 1.1rem;display:flex;flex-wrap:wrap;gap:.75rem 1.25rem;align-items:center}}
.withdrawn .stamp{{font-size:1rem;flex:none}}
.withdrawn p{{margin:0;flex:1 1 18rem;min-width:0}}
footer{{font:700 .8125rem/1.6 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-soft);border-top:3px solid var(--ink);padding-top:.9rem}}

@media (min-width:54rem){{
  .drawer{{grid-template-columns:15rem minmax(0,1fr);gap:2rem;align-items:start}}
  .plate{{position:sticky;top:calc(84px + env(safe-area-inset-top,0px));flex-direction:column;align-items:flex-start}}
  .mast{{display:grid;grid-template-columns:minmax(0,1fr) 20rem;align-items:end;column-gap:2rem}}
  .mast .eyebrow,.mast h1{{grid-column:1/-1}}
  .legend{{grid-template-columns:repeat(4,minmax(0,1fr))}}
}}
@media (prefers-reduced-motion:no-preference){{.chip{{transition:transform .08s,box-shadow .08s,background .12s}}}}
</style>
<div class="wrap">
<header class="mast">
<p class="eyebrow">Room 63 · AP Research · Mr. Portela</p>
<h1><span>Research</span><span class="l2">Library</span></h1>
<p class="lede">Every card here was opened and checked. Each one says what it is for, whether you may cite it, and what to watch out for.</p>
<ul class="strip"><li>{len(LIB)} cards</li><li>{len(NEEDS)} drawers</li><li>Checked Nov 2026</li></ul>
</header>
<p class="pledge"><b>Nothing here writes or changes your research question.</b><span>Your question is the one in your log. To find sources on your own topic, use your Search Guide slip.</span></p>
<ul class="legend" aria-label="What the stamps mean">{legend}</ul>
<nav class="tabs" aria-label="Open one drawer"><div class="chips">{chips}</div></nav>
{sections}
<section class="withdrawn" aria-label="Do not use"><span class="stamp s-oxide">Withdrawn</span><p><b>PapersOwl</b> and sites like it. Their advice pages sell papers written for you. College Board requires your paper to be your own work.</p></section>
<footer>Room 63 Research Library · If a link breaks, tell Mr. Portela</footer>
</div>
<script>
(function(){{
  var chips=[].slice.call(document.querySelectorAll('.chip')),secs=[].slice.call(document.querySelectorAll('.drawer'));
  function show(n){{
    chips.forEach(function(c){{c.setAttribute('aria-pressed',String(c.dataset.need===n));}});
    secs.forEach(function(s){{s.hidden=!(n==='all'||s.dataset.need===n);}});
    try{{localStorage.setItem('r63lib_need',n);}}catch(e){{}}
  }}
  chips.forEach(function(c){{c.addEventListener('click',function(){{show(c.dataset.need);c.scrollIntoView({{block:'nearest',inline:'center'}});}});}});
  var saved='all';try{{saved=localStorage.getItem('r63lib_need')||'all';}}catch(e){{}}
  if(!chips.some(function(c){{return c.dataset.need===saved;}}))saved='all';
  show(saved);
}})();
</script>
""", encoding="utf-8")
print("built", len(LIB), "library entries")
