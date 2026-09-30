#!/usr/bin/env python3
"""Book S2, The Individual Project (key "ip"). Prints the build spec as JSON.

Every page reference and page number is a [[...]] token. College Board facts come
from build/ip/facts.md (tags in the comments). Visible text: no em dashes, no en
dashes, no semicolons, no contractions.
"""
import json, re

RUN = 'THE INDIVIDUAL PROJECT'
CHK = 'Checked September 30, 2026.'
HEAD = "<div class='head'><span>%s</span><span>{{SHORT}}{{PHEAD}}</span></div>" % RUN

MONO = "Space Mono,Courier New,monospace"
SERIF = "Cormorant Garamond,Georgia,serif"
HAND = "Patrick Hand,cursive"
NAVY, OX, PINE, GOLD, DK, LGOLD, PAPER, CREAM, SOFT, INK = (
    '#1f3a5a', '#9c3322', '#245e55', '#b8903f', '#16294a', '#e8c878', '#fbf6ea', '#f6edd6', '#4a3f31', '#1d1812')

FACES = []

def A(s):
    """escape for an attribute value in single quotes"""
    return s.replace('&', '&amp;').replace("'", '&#39;').replace('"', '&quot;')

def add(fid, cls, label, html, **kw):
    d = {'id': fid, 'cls': cls, 'label': label, 'html': html}
    d.update(kw)
    FACES.append(d)

def paper(fid, label, body):
    add(fid, 'paper', label, "<div class='grainlayer grain'></div><div class='pg'>" + HEAD + body + "</div>[[num]]<div class='shade'></div>")

def P(t, cls='small', style=None):
    st = " style='%s'" % style if style else ''
    return "<p class='%s'%s>%s</p>" % (cls, st, t)

def folio(icon, n):
    return "<p class='folio'><svg class='femb' aria-hidden='true'><use href='#%s'/></svg>FOLIO %d</p>" % (icon, n)

def table(cls, head, rows):
    h = ''.join('<th>%s</th>' % x for x in head)
    b = ''
    for r in rows:
        b += '<tr><th>%s</th>%s</tr>' % (r[0], ''.join('<td>%s</td>' % x for x in r[1:]))
    return "<table class='%s'><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (cls, h, b)

def card(kind, k, *ps, mt='1.2cqw'):
    body = ''.join('<p>%s</p>' % p for p in ps)
    return "<div class='card2 %s' style='margin-top:%s'><div class='k'>%s</div>%s</div>" % (kind, mt, k, body)

def notes(k, *ps, mt='1.2cqw'):
    body = ''.join("<p class='note2'>%s</p>" % p for p in ps)
    return "<div class='card2 ' style='margin-top:%s'><div class='k'>%s</div>%s</div>" % (mt, k, body)

def wait(t):
    return card('wait', 'WAITING ON A ROOM 63 DECISION', t)

def tryit(level, q, a):
    return ("<div class='card2 try' style='margin-top:1.2cqw'><div class='k'>TRY IT &middot; %s</div><p>%s</p>"
            "<p class='small ans' role='button' tabindex='0' aria-label='Show the answer' aria-expanded='false' style='margin-top:.6cqw'>%s</p></div>") % (level, q, a)

def rowq(n, name, pts):
    return "<p class='rowq'><span class='rown'>ROW %d</span>&quot;%s&quot; &middot; %s</p>" % (n, name, pts)

def newword(word, es, line):
    return "<div class='card2 ' style='margin-top:1.2cqw'><div class='k'>NEW WORD &middot; %s</div><p><em lang='es' class='esw'>%s</em> &middot; %s</p></div>" % (word, es, line)

def link(url, t):
    return "<a href='%s' target='_blank' rel='noopener'>%s</a>" % (url, t)

def pj(i):
    return '[[pj:%s]]' % i

def tick(t):
    return "<button type='button' class='tick' aria-pressed='false' aria-label='%s'><span class='bx' aria-hidden='true'></span>%s</button>" % (A(t), t)

STAMP = ("<svg class='passstamp' viewBox='0 0 150 50' aria-hidden='true'><rect x='3' y='3' width='144' height='44' rx='7' fill='none' stroke='#1f5c4a' stroke-width='3'/>"
         "<rect x='8' y='8' width='134' height='34' rx='4' fill='none' stroke='#1f5c4a' stroke-width='1.4'/><text x='75' y='33' text-anchor='middle' "
         "font-family='Space Mono,monospace' font-weight='700' font-size='21' letter-spacing='4' fill='#1f5c4a'>CHECKED</text></svg>")

def form(name, left, tiers):
    h = "<div class='form' data-form='%s'><div class='fhead'><span>%s</span><span>TAP WHAT IS TRUE</span></div>" % (name, left)
    for lab, ticks in tiers:
        h += "<p class='tierlab'>%s</p>" % lab + ''.join(tick(t) for t in ticks)
    return h + STAMP + "<span class='live srt' aria-live='polite'></span></div>"

def gorow(t, fid):
    return "<button type='button' class='gorow' data-jump='[[idx:%s]]'><span>%s</span><span class='gpn'>[[pno:%s]]</span></button>" % (fid, t, fid)

def tocrow(n, board, title, sub):
    return ("<li><button type='button' data-jump='[[idx:%s]]'><span class='rn'>%d</span><span class='tt'><span class='tl'>%s</span>"
            "<span class='ld' aria-hidden='true'></span><span class='pn'>[[pno:%s]]</span></span><span class='sb'>%s</span></button></li>") % (board, n, title, board, sub)

def board(fid, n, title, icon, byend, inside):
    lis = ''.join("<li><span class='it'>%s</span><span class='ld' aria-hidden='true'></span><span class='pn'>[[pno:%s]]</span></li>" % (t, i) for t, i in inside)
    html = ("<div class='chap'>{{GOLD}}<div class='ch-in'><div class='ch-top'>FOLIO</div><div class='ch-num'>%d</div><div class='ch-title'>%s</div>"
            "<svg class='ch-rule' viewBox='0 0 120 12' aria-hidden='true'><line x1='4' y1='6' x2='48' y2='6'/><path d='M60 1 l5 5 -5 5 -5 -5z'/><line x1='72' y1='6' x2='116' y2='6'/></svg>"
            "<svg class='ch-icon' aria-hidden='true'><use href='#%s'/></svg><div class='ch-target'><div class='k'>BY THE END</div><p>%s</p></div>"
            "<div class='ch-inside'><div class='k'>INSIDE</div><ul>%s</ul></div></div></div><div class='num ch-pn'>&middot; x &middot;</div><div class='shade'></div>") % (n, title, icon, byend, lis)
    add(fid, 'board chapter', 'Folio %d' % n, html, folio=n, title=title)

def wrow(icon, en, es, line, fid):
    return ("<div class='wrow'><div class='wt'><svg class='gi' aria-hidden='true'><use href='#%s'/></svg><strong>%s</strong><em lang='es'>%s</em></div>"
            "<p>%s</p>[[gtag:%s]]</div>") % (icon, en, es, line, fid)

# ---------- svg helpers for plates ----------
def T(x, y, s, font=MONO, size=7, weight=700, fill=NAVY, anchor='middle', extra=''):
    return "<text x='%s' y='%s' font-family='%s' font-size='%s' font-weight='%s' fill='%s' text-anchor='%s'%s>%s</text>" % (x, y, font, size, weight, fill, anchor, extra, s)

def R(x, y, w, h, fill=PAPER, stroke=NAVY, sw=1.2, rx=3, extra=''):
    return "<rect x='%s' y='%s' width='%s' height='%s' rx='%s' fill='%s' stroke='%s' stroke-width='%s'%s/>" % (x, y, w, h, rx, fill, stroke, sw, extra)

def L(d, stroke=OX, sw=1.4, extra=''):
    return "<path d='%s' fill='none' stroke='%s' stroke-width='%s'%s/>" % (d, stroke, sw, extra)

def arrowhead(x, y, direction, stroke=OX, sw=1.4):
    # small open chevron pointing in direction ('r','l','u','d')
    if direction == 'r': d = 'M%.1f %.1f L%.1f %.1f L%.1f %.1f' % (x - 4, y - 2.6, x, y, x - 4, y + 2.6)
    elif direction == 'l': d = 'M%.1f %.1f L%.1f %.1f L%.1f %.1f' % (x + 4, y - 2.6, x, y, x + 4, y + 2.6)
    elif direction == 'u': d = 'M%.1f %.1f L%.1f %.1f L%.1f %.1f' % (x - 2.6, y + 4, x, y, x + 2.6, y + 4)
    else: d = 'M%.1f %.1f L%.1f %.1f L%.1f %.1f' % (x - 2.6, y - 4, x, y, x + 2.6, y - 4)
    return "<path d='%s' fill='none' stroke='%s' stroke-width='%s' stroke-linejoin='round'/>" % (d, stroke, sw)

def plate(num, title, vbh, aria, inner, capk, cap):
    return ("<figure class='plate'><div class='pl'><span>PLATE %s</span><span>%s</span></div>"
            "<svg class='fig' viewBox='0 0 320 %s' role='img' aria-label='%s'>%s</svg>"
            "<figcaption><b>%s</b>%s</figcaption></figure>") % (num, title, vbh, A(aria), inner, capk, cap)

# =====================================================================
# FRONT MATTER
# =====================================================================

# Face 0, cover: tp face 0, only the three title lines and the h1 change.
COVER = ('<svg class="A-art" viewBox="0 0 720 1000" preserveAspectRatio="none" aria-hidden="true" focusable="false"><g filter="url(#A-grain)"><rect class="A-leather" width="720" height="1000"/>'
         '<g filter="url(#A-recess)"><path class="A-onlay" d="M474.27,348.02A120,120 0 0 1 474.27,587.98A116,116 0 0 1 245.73,587.98A120,120 0 0 1 245.73,348.02A116,116 0 0 1 474.27,348.02Z"/></g>'
         '<g filter="url(#A-recess)"><path class="A-labelskin" d="M192,768H528A12,12 0 0 0 540,780V828A12,12 0 0 0 528,840H192A12,12 0 0 0 180,828V780A12,12 0 0 0 192,768Z"/></g></g>'
         '<rect width="720" height="1000" fill="url(#A-vig)"/><rect width="720" height="1000" fill="url(#A-sheen)"/><rect width="22" height="1000" fill="url(#A-hinge)"/>'
         '<g filter="url(#A-gilt)"><rect width="720" height="1000" fill="url(#A-goldg)" mask="url(#A-goldmask)"/></g>'
         '<g class="A-titleart" filter="url(#A-titlef)" fill="url(#A-titleg)" text-anchor="middle">'
         '<text class="A-t-the" x="358.42" y="%(y1)s" font-size="%(s1)s">The</text>'
         '<text class="A-t-big" x="360" y="%(y2)s" font-size="%(s2)s">INDIVIDUAL</text>'
         '<text class="A-t-big" x="360" y="%(y3)s" font-size="%(s3)s">PROJECT</text></g></svg>'
         "<h1 class='A-sr'>The Individual Project</h1><label for='nameIn' class='A-sr'>Your name</label>"
         "<input id='nameIn' class='A-name' type='text' maxlength='40' autocomplete='off' spellcheck='false' placeholder='Type your name' value='{{NAMEVAL}}'><div class='shade'></div>")
COVER_SIZES = {'y1': '404.0', 's1': '50.0', 'y2': '478.0', 's2': '60.0', 'y3': '544.0', 's3': '60.0'}
add('cover', 'board lthr', 'Cover', COVER % COVER_SIZES)

# Face 1, Kept by
add('keptby', 'endpaper', 'Kept by',
    "<div class='panel'><svg viewBox='0 0 80 80' aria-hidden='true' style='width:10cqw;height:10cqw;margin:0 auto 1.2cqw;display:block'><circle class='draw' pathLength='1' cx='40' cy='40' r='34' fill='none' stroke='#9c3322' stroke-width='2.5'/><circle class='draw d2' pathLength='1' cx='40' cy='40' r='27' fill='none' stroke='#9c3322' stroke-width='1'/><text class='pop d3' x='40' y='48' text-anchor='middle' font-family='Fraunces,serif' font-weight='700' font-size='22' fill='#9c3322'>63</text></svg>"
    "<div class='kept'>THIS BOOK BELONGS TO</div><div class='who' style='--nl:{{NLEN}}'>{{NAME}}</div><div class='meta'>{{META}}</div><div class='pick'><div class='drawers' role='group' aria-label='Your period'>{{DRAWERS}}</div></div>"
    "<div class='box'>How one packet becomes your own question, one written argument, one talk, and two answers. Stuck? Folio 10.</div>"
    "<p class='small' style='margin:0 0 1.4cqw;font-weight:700'>One packet. Your question. Your argument. Your defense.</p>"
    "<p class='small' style='margin:0'>Turn the page with the arrows, a tap on the page edge, or a drag of the corner.</p>"
    "<p class='small' style='margin:1.4cqw 0 0'>Room 63 &middot; Mr. Portela &middot; AP Seminar &middot; 2026-27</p></div><div class='shade'></div>")

# Face 2, Contents
paper('contents', 'Contents',
    "<h2>Contents</h2>" + P("Tap a line to open that folio. New here? Start on page %s." % pj('start')) +
    "<div class='R'><div class='card2 weak' style='margin-top:1cqw'><div class='k'>AP RESEARCH?</div><p>This book is for AP Seminar. Your paper&#39;s book is Writing the Paper.</p></div></div>"
    "<div class='P'><p class='small'>This book is for AP Seminar, Periods 2, 5, 6, 7, and 8.</p></div>"
    "<div class='tochead'><span>FOLIO</span><span>PAGE</span></div><ul class='toc'>" +
    tocrow(1, 'f1', 'The task, two runs', 'the parts, practice or real, my role, the dates') +
    tocrow(2, 'f2', 'The packet', 'what it holds, when it comes, how to read it') +
    tocrow(3, 'f3', 'A theme, then a question', 'two texts, one link, your question') +
    tocrow(4, 'f4', 'Research and the first checkpoint', 'sources, the log, the talk') +
    tocrow(5, 'f5', 'The outline and the second checkpoint', 'argue, outline, explain it') + "</ul>")

# Face 3, Contents, continued
paper('contents2', 'Contents',
    "<h3>Contents, continued</h3><div class='tochead'><span>FOLIO</span><span>PAGE</span></div><ul class='toc'>" +
    tocrow(6, 'f6', 'The written argument, row by row', 'the rules, 48 points, Rows 1 to 4') +
    tocrow(7, 'f7', 'Finish and submit the argument', 'Rows 5 to 7, checks, final') +
    tocrow(8, 'f8', 'Honest work', 'credit, tools, what I sign') +
    tocrow(9, 'f9', 'Your talk and two questions', 'the rows, the defense, the day') +
    tocrow(10, 'f10', 'When you get stuck', 'the work, absences, your file') + "</ul>"
    "<div class='card2' style='margin-top:1.4cqw'><div class='k'>SIGNS IN THIS BOOK</div><div class='notes' style='margin-top:.6cqw'>"
    "<div><svg class='ic sm' aria-hidden='true'><use href='#i-check'/></svg><p>strong, or allowed</p></div>"
    "<div><svg class='ic sm' aria-hidden='true'><use href='#i-cross'/></svg><p>weak, or not allowed</p></div>"
    "<div><span class='marks'><i class='y'></i><i></i></span><p>a check passes, or does not</p></div></div></div>"
    "<p class='small' style='margin-top:1cqw'>A dashed box: WAITING ON A ROOM 63 DECISION.</p>")

# Face 4, Start here
paper('start', 'Start here',
    "<h2>Your project in eight steps</h2>" + P("Do the steps in order. Tap a step to open its page.") +
    "<div class='tochead'><span>STEP</span><span>PAGE</span></div>" +
    gorow('1 Know the task, the rules, and the dates.', 'f1-glance') +
    gorow('2 Get the packet. Read it three times.', 'f2-read') +
    gorow('3 Link two texts with one theme.', 'f3-theme') +
    gorow('4 Write one question of your own.', 'f3-question') +
    gorow('5 Research. Log every source. Pass checkpoint 1.', 'f4-beyond') +
    gorow('6 Outline your argument. Pass checkpoint 2.', 'f5-outline') +
    gorow('7 Write it row by row. Submit it as final.', 'f6-rules') +
    gorow('8 Present it. Answer two questions.', 'f9-talk') +
    P("The examples in this book are made up. You find your own theme, question, and sources."))

# Face 5, Find it fast
paper('find', 'Find it fast',
    "<h3>Find it fast</h3>" + P("Tap your problem. The page opens.") +
    "<div class='tochead'><span>I HAVE</span><span>PAGE</span></div>" +
    gorow('A packet I have not seen yet.', 'f2-when') +
    gorow('Seven texts and no idea where to start.', 'f2-read') +
    gorow('Two texts that seem to share nothing.', 'f3-links') +
    gorow('A question that is really two questions.', 'f3-question') +
    gorow('A checkpoint this week.', 'f4-cp1') +
    gorow('A draft that only summarizes.', 'f5-argue') +
    gorow('A packet text I mention only once.', 'f6-row1') +
    gorow('A paper ready to submit.', 'f7-before') +
    gorow('A tool I want to use.', 'f8-tools') +
    gorow('A talk coming up.', 'f9-talk') +
    gorow('Days of school I will miss.', 'f10-missed'))

# =====================================================================
# FOLIO 1, The task, two runs
# =====================================================================
board('f1', 1, 'The task, two runs', 'i-cal',
      'Say what the individual project asks, what is scored, when it is due, and what I can and cannot do.',
      [('The individual project at a glance', 'f1-glance'), ('What carries over from the team project', 'f1-repeat'),
       ('Practice run, real run', 'f1-runs'), ('What I can do, and what I cannot', 'f1-can'), ('The dates', 'f1-dates')])

# [D5, G2, O1] [D2, D3, K1, D7] [D1, D7] [A4]
paper('f1-glance', 'Folio 1',
    folio('i-cal', 1) + "<h2>The individual project at a glance</h2>" +
    P("This time you work alone. You find a theme that links two texts in a College Board packet, and ask your own question. Then you research, write, present, and defend.") +
    table('stages four tight', ['PART', 'LENGTH', 'WHO SCORES IT', 'SCORE'], [
        ['Individual Written Argument', '2,000 words or fewer', 'the College Board', '24.5 percent'],
        ['Individual Multimedia Presentation', '6 to 8 minutes', 'I do, for the College Board', '7 percent'],
        ['Oral Defense', 'two questions', 'I do, for the College Board', '3.5 percent']]) +
    P("The task is 35 percent of your AP score. College Board rubrics call the parts the Individual Written Argument (IWA), the Individual Multimedia Presentation (IMP), and the Oral Defense (OD). " + CHK))

# tp pages 16, 17 and 18, 24, 26, 28 checked in tp_text. [G11]
paper('f1-repeat', 'Folio 1',
    "<h3>What carries over from the team project</h3>" +
    P("The Team Project still teaches these skills. This book adds what is new.") +
    table('stages checks tight', ['SKILL', 'TEAM PROJECT', 'NEW IN THIS BOOK'], [
        ['Perspectives', 'page 16', 'objections and limits: page %s' % pj('f6-row3')],
        ['Checkpoint talk', 'pages 17 and 18', 'a second talk, on your outline: page %s' % pj('f5-cp2')],
        ['Citation', 'page 24', 'packet texts too: page %s' % pj('f6-rules')],
        ['Submit as final', 'page 28', 'the Individual Written Argument: page %s' % pj('f7-submit')]]) +
    card('good', 'THE BIG CHANGE', 'Your report explained what experts say. Your written argument takes a position and defends it.') +
    P(CHK, style='margin-top:1cqw'))

# [U3] [B, V1] [R] [D8] [IG p. 12] [F6, V2, P8] [V4, Y11]
paper('f1-runs', 'Folio 1',
    "<h3>Practice run, real run</h3>" +
    table('stages runs tight', ['', 'PRACTICE RUN', 'REAL RUN'], [
        ['The packet', 'A past packet from AP Central.', 'The 2027 packet.'],
        ['My help', 'See the dashed box.', 'Only what page %s allows.' % pj('f1-can')],
        ['Where it goes', 'Google Classroom', 'The AP Digital Portfolio, as final']]) +
    P("The real run cannot start before January, when the College Board publishes the packet. " + CHK) +
    card('weak', 'NO REUSE', 'No practice text goes into your real paper. It has my help in it. Start a new Google Doc.') +
    wait('Whether we do a practice run, with which past packet, when, and how much I help: on Google Classroom.'))

# [R, F8, O3] CED pp. 49 to 50
paper('f1-can', 'Folio 1',
    "<h3>What I can do, and what I cannot</h3>" +
    table('stages half tight', ['I CAN', 'I CANNOT'], [
        ['Tell you the dates and the rubrics.', 'Give you a question or sources.'],
        ['Discuss the packet with the class.', 'Hand it out with no discussion.'],
        ['Hold your checkpoints.', 'Tell you what to write or change.'],
        ['Point to a rubric row.', 'Edit or proofread your paper.'],
        ['Give you the defense questions list.', 'Tell you which two you will get.']]) +
    P("In the real run, the College Board sets these rules. This book is general help, not feedback on your work. " + CHK) +
    tryit('NEXT STEP', 'In the real run, you ask me: "Which two texts should I link?" What can I say?',
          'I can talk about the packet with the whole class. I cannot choose your texts for you.'))

# [B] January (no day), April 15 (CED p. 46, IG p. 12), April 30 and May 10 (EXAM, checked live September 30, 2026)
paper('f1-dates', 'Folio 1',
    "<h3>The dates</h3>" +
    table('stages dates tight', ['WHEN', 'WHAT'], [
        ['January 2027', 'The College Board releases the packet to teachers.'],
        ['April 15, 2027', 'The College Board&#39;s recommended finish.'],
        ['April 30, 2027', 'The last moment to submit your written argument as final: 11:59 in the evening, Eastern Time.'],
        ['May 10, 2027', 'The last moment for me to enter talk scores and sign that your work is yours. The exam is the same day.']]) +
    P("Dates can move. The newest Google Classroom post wins. " + CHK) +
    wait('The day you get the packet, your checkpoint dates, and my due date for your paper: on Google Classroom. Your own talk: March 17 to April 15, 2027.') +
    P("Team project dates: The Team Project, page 8. The exam: The End-of-Course Exam.", style='margin-top:1cqw'))

# =====================================================================
# FOLIO 2, The packet
# =====================================================================
board('f2', 2, 'The packet', 'i-book',
      'Say what the packet holds, when you get it, and how to read it for links.',
      [('What the packet is', 'f2-what'), ('When it comes, and how you get it', 'f2-when'),
       ('Read it three times', 'f2-read'), ('This year&#39;s packet only', 'f2-this')])

# [F1] [F2] [F3, Y2] [F4]
paper('f2-what', 'Folio 2',
    folio('i-book', 2) + "<h2>What the packet is</h2>" +
    P("Each year the College Board releases one set of texts on one theme, from many perspectives: the stimulus materials. In this book: the packet, and its stimulus texts.") +
    table('stages rules tight', ['KIND', 'FOR EXAMPLE'], [
        ['Many fields', 'science, social science, the arts, languages, history, literature'],
        ['Pictures and data', 'a photograph, artwork, video, or music, and numbers']]) +
    P("No rule fixes how many texts. The 2024, 2025, and 2026 packets each held seven. In 2026: a study of coffee shops in city life, a Surgeon General chapter on social connection, a magazine article on roads, an essay by Haruki Murakami, a news story on the Berlin Wall, a column about a ballpark, and a study of satellite internet.") +
    P("Chief Readers named the 2024 theme courage, and the 2025 theme memory and nostalgia. " + CHK))

# PLATE I [C1, N4] [B, F8] [C3] [F5]
PL1 = (T(31, 15, 'ROOM 63 PICKS', size=5.8, fill=OX) +
       R(4, 20, 54, 30, fill=PAPER, stroke=OX, sw=1.2, extra=" stroke-dasharray='3 2'") +
       T(31, 33, 'PACKET', size=6.8, fill=OX) + T(31, 43, 'DAY', size=6.8, fill=OX) +
       R(62, 20, 150, 30, fill=CREAM, stroke=NAVY, sw=1.2) +
       T(137, 32, 'AT LEAST 30 SCHOOL DAYS', size=6.8) +
       T(137, 44, 'research, write, build your talk', font=SERIF, size=9.5, weight=600, fill=SOFT) +
       R(216, 20, 46, 30, fill=PAPER, stroke=NAVY, sw=1.2) +
       T(239, 33, 'ALL WORK', size=6.2) + T(239, 43, 'COLLECTED', size=6.2) +
       R(266, 20, 50, 30, fill=DK, stroke=GOLD, sw=1.4) +
       T(291, 33, 'THE', size=6.8, fill=LGOLD) + T(291, 43, 'TALKS', size=6.8, fill=LGOLD) +
       L('M62 54 L62 58 L212 58 L212 54', stroke=OX, sw=1) +
       T(137, 68, 'no testing days, breaks, or holidays', font=HAND, size=10, weight=400, fill=OX))
paper('f2-when', 'Folio 2',
    "<h3>When it comes, and how you get it</h3>" +
    P("The College Board releases the packet to teachers in January. I choose the day you get it.") +
    plate('I', 'Thirty school days, then the talks', 72,
          'A bar read left to right. First, packet day, a dashed box: Room 63 picks it. Then at least 30 school days to research, write, and build your talk. Testing days, breaks, and holidays do not count. Then all work is collected. Then the talks.',
          PL1, 'COLLEGE BOARD RULES', 'At least 30 school days, then the talks.') +
    P("We meet every other school day, so 30 school days is about 15 of our classes.") +
    P("To get it: AP Digital Portfolio, Overview, under Individual Research-Based Essay and Presentation. Tap Download. " + CHK) +
    wait('The day you get the packet: on Google Classroom.'))

# [G1] Room 63 method [K4] [F8]
paper('f2-read', 'Folio 2',
    "<h3>Read it three times</h3>" +
    P("The College Board&#39;s first step: read the texts to find links between them, and questions worth asking. A Room 63 way to do it:") +
    table('stages narrow1 tight', ['READ', 'ASK'], [
        ['1', 'What does each text say? One line each, in your log.'],
        ['2', 'What does it argue, and from what view? A view with its reason.'],
        ['3', 'Which two texts talk to each other? About what?']]) +
    P("Log each text like any source (The Research Log, page 30). Cite each one like any other source (The Research Manual, page 67).") +
    P("We discuss the packet in class first. The College Board asks that of me. " + CHK) +
    tryit('FIRST STEP', 'One text is a photograph. Do you read it?',
          'Yes. Ask what it shows, who made it, and when. It is a text like the others.'))

# [F6] [F7, K8, Y4] [CRR25 p. 7] [U3, Z7] [G2]
paper('f2-this', 'Folio 2',
    "<h3>This year&#39;s packet only</h3>" +
    P("Your paper must use this year&#39;s packet.") +
    card('weak', 'OLD PACKET', 'The 2025 scoring guidelines told readers to treat a paper that cites only an earlier packet as off-topic. An off-topic paper earns 0 points.') +
    P("In 2025 the Chief Reader listed papers built on a previous year&#39;s packet as a weakness.", style='margin-top:1cqw') +
    P("Past packets are good practice. %s posts recent ones with their scoring guidelines." % link('https://apcentral.collegeboard.org/courses/ap-seminar/exam/past-exam-questions', 'AP Central')) +
    tryit('NEXT STEP', 'Your friend&#39;s 2026 paper linked two strong texts. Can you use the same link?',
          'No. Your theme must link two texts from the 2027 packet.') +
    P(CHK, style='margin-top:1cqw'))

# =====================================================================
# FOLIO 3, A theme, then a question
# =====================================================================
board('f3', 3, 'A theme, then a question', 'i-link',
      'Find a theme that links two stimulus texts, and turn it into one question of your own.',
      [('A theme, not a topic', 'f3-theme'), ('Find the links', 'f3-links'), ('Strong link, weak link', 'f3-strong'),
       ('Your question is yours', 'f3-yours'), ('From a theme to a question', 'f3-question')])

# [G2] [G4] [G3]
paper('f3-theme', 'Folio 3',
    folio('i-link', 3) + "<h2>A theme, not a topic</h2>" +
    table('stages rules tight', ['', 'IT IS'], [
        ['Topic', 'What one text is about. Bus waits. A ballpark.'],
        ['Theme', 'An idea two or more texts share. Who a public place is for.']]) +
    P("The College Board rule: your question must relate to a theme that connects at least two of the stimulus texts.") +
    P("The packet has one big theme. You do not have to use it. In 2025, strong papers found themes rooted in two or more texts, even outside the packet&#39;s theme. Pick one you care about, rich enough for a real argument. " + CHK) +
    newword('THEME', 'tema en com&uacute;n', 'An idea that two or more texts share.'))

# PLATE II, a made-up packet [G5]
def pbox(x, y, head, l1, l2=None):
    s = R(x, y, 96, 36, fill=PAPER, stroke=NAVY, sw=1.2) + T(x + 6, y + 11, head, size=6.4, anchor='start')
    if l2:
        s += T(x + 6, y + 22, l1, font=SERIF, size=8.8, weight=600, fill=SOFT, anchor='start') + T(x + 6, y + 31, l2, font=SERIF, size=8.8, weight=600, fill=SOFT, anchor='start')
    else:
        s += T(x + 6, y + 26, l1, font=SERIF, size=8.8, weight=600, fill=SOFT, anchor='start')
    return s
def vlink(cx, l1, l2):
    return (L('M%d 46 L%d 62' % (cx, cx)) + L('M%d 96 L%d 112' % (cx, cx)) +
            "<circle cx='%d' cy='46' r='2.2' fill='%s'/><circle cx='%d' cy='112' r='2.2' fill='%s'/>" % (cx, OX, cx, OX) +
            T(cx, 76, l1, font=HAND, size=11, weight=400, fill=OX) + T(cx, 89, l2, font=HAND, size=11, weight=400, fill=OX))
PL2 = (pbox(8, 10, 'A &#183; ESSAY', 'Ortiz,', 'Who Is the Bench For?') +
       pbox(112, 10, 'B &#183; PHOTOGRAPH', 'a library with a', 'CLOSED sign') +
       pbox(216, 10, 'C &#183; CHART', 'park visits', 'by hour') +
       pbox(8, 112, 'E &#183; STUDY', 'how long', 'bus riders wait') +
       pbox(112, 112, 'D &#183; POEM', 'a grandmother&#39;s', 'kitchen') +
       pbox(216, 112, 'F &#183; SPEECH', 'a new', 'highway') +
       vlink(56, 'who public', 'space is for') + vlink(160, 'places that', 'hold memory') + vlink(264, 'who a city', 'is built for'))
paper('f3-links', 'Folio 3',
    "<h3>Find the links</h3>" +
    P("Draw a line between any two texts. Name what they share in four words or fewer.") +
    plate('II', 'One packet, many links', 152,
          'A made-up packet of six texts. A, an essay: Ortiz, Who Is the Bench For? B, a photograph of a library with a CLOSED sign. C, a chart of park visits by hour. D, a poem about a grandmother\'s kitchen. E, a study of how long bus riders wait. F, a speech about a new highway. Three links: A and E, who public space is for. B and D, places that hold memory. C and F, who a city is built for.',
          PL2, 'A MADE-UP PACKET', 'Six texts, three links. Each line names what two texts share.') +
    P("Start with the obvious link. Then look for one that is harder to see. A text can join more than one link. " + CHK) +
    P("This made-up packet is off limits for your paper."))

# [G4] [K9]
paper('f3-strong', 'Folio 3',
    "<h3>Strong link, weak link</h3>" +
    table('stages wide1 tight', ['WEAK IN 2025', 'WHAT GOES WRONG'], [
        ['A topic only one text covers', 'No theme connects two texts.'],
        ['A topic one text already argues', 'Your paper turns into a summary.']]) +
    card('weak', 'WEAK, A MADE-UP CASE', '&quot;Text E times bus waits. My question: how long do riders wait?&quot;', mt='.8cqw') +
    card('good', 'STRONG, A MADE-UP CASE', '&quot;Texts A and E both ask who a public space serves. My question asks it about one county&#39;s bus stops.&quot;', mt='.8cqw') +
    P("Readers lean toward scoring. If they can find any link to a theme from two texts, they score the paper. " + CHK, style='margin-top:1cqw'))

# [G6] [G7, quote keeps the qualifier] fg p. 4 [P8] [Y10]
paper('f3-yours', 'Folio 3',
    "<h3>Your question is yours</h3>" +
    table('stages rules tight', ['RULE', 'WHAT IT SAYS'], [
        ['College Board', '&quot;Compose a research question of your own.&quot; I may not assign, give, or write one for you.'],
        ['A tool that writes', 'Not acceptable: &quot;using AI to generate a research question,&quot; taken &quot;uncritically,&quot; &quot;without engaging with the actual research.&quot;'],
        ['Room 63', 'No tool writes, rewrites, or narrows your question (The Field Guide, page 4).']]) +
    P("Everyone reads the same packet. The question you ask of it is yours.") +
    P("The College Board bans reusing a paper, even one you wrote (page %s). %s" % (pj('f8-credit'), CHK)) +
    wait('Using your team project&#39;s issue, sources, or lens in this paper: my rule posts on Google Classroom.'))

# [G9] real 2025 Chief Reader example [G10]
paper('f3-question', 'Folio 3',
    "<h3>From a theme to a question</h3>" +
    P("Narrow the theme to one place and one time. A real example from the 2025 Chief Reader:") +
    card('weak', 'TOO BROAD', '&quot;Why are memories important?&quot;', mt='.8cqw') +
    card('good', 'FOCUSED', '&quot;How is nostalgia leveraged in the US to influence consumer behavior?&quot;', mt='.8cqw') +
    table('stages wide1 tight', ['BROKEN', 'THE REPAIR'], [
        ['Two questions in one', 'Keep one.'],
        ['No place or time', 'Add both.'],
        ['Closed: a yes, or a fact', 'Ask how, or to what extent.'],
        ['No one is affected', 'Say who is, and why now.']]).replace("<table class='stages wide1 tight'>", "<table class='stages wide1 tight' style='margin-top:1.2cqw'>") +
    P("A good question is open, relevant, debatable, and researchable. Test yours: The Field Guide, page 20. " + CHK))

# =====================================================================
# FOLIO 4, Research and the first checkpoint
# =====================================================================
board('f4', 4, 'Research and the first checkpoint', 'i-search',
      'Research beyond the packet, log every source, and pass the first checkpoint talk.',
      [('Research beyond the packet', 'f4-beyond'), ('Your log, and a question that changes', 'f4-log'),
       ('Three checkpoints', 'f4-cp1'), ('The first checkpoint talk', 'f4-talk1')])

# [H1] [H8] [H9]
paper('f4-beyond', 'Folio 4',
    folio('i-search', 4) + "<h2>Research beyond the packet</h2>" +
    P("Find more sources, from a range of perspectives. Include scholarly work. EBSCO and Turnitin come free through the AP Digital Portfolio.") +
    card('weak', 'WEAK IN 2025', 'Mostly news, blogs, or encyclopedias. One or two sources for a whole paper. Sources read only to the abstract.', mt='.8cqw') +
    table('stages wide1 tight', ['TO DO THIS', 'GO TO'], [
        ['Find the other views', 'The Research Manual, page 25'],
        ['Check a source', 'The Research Manual, page 44'],
        ['Scholarly or popular?', 'The Research Manual, page 46']]).replace("<table class='stages wide1 tight'>", "<table class='stages wide1 tight' style='margin-top:1.2cqw'>") +
    P("Same skill, first time: The Team Project, page 15. " + CHK))

# [H2] [G8] [H3] WAIT 5 as tp f22, log f7
paper('f4-log', 'Folio 4',
    "<h3>Your log, and a question that changes</h3>" +
    P("For checkpoint 1, the College Board asks for a log of the sources you found and read, with notes and links. Your log is your Research Log. Every source goes in, even the ones you drop (The Research Log, page 33).") +
    P("Your question will change. The College Board expects you to keep refining it. Each time, write a version line (The Research Log, page 46). " + CHK) +
    wait('Before the talk, photograph your log pages into the Google Classroom assignment. The notebook stays with you.') +
    tryit('FIRST STEP', 'Your question changed twice. What do you bring?',
          'The log, with both version lines. They show your thinking.'))

# PLATE III [J3, H2, I1, J1] [J5, J4] [H6]
def station(cx, n, t1, t2, when, what, miss, dark=False):
    fill, tc = (DK, LGOLD) if dark else (OX, '#fff8ea')
    return ("<circle cx='%d' cy='20' r='11' fill='%s' stroke='%s' stroke-width='1.4'/>" % (cx, fill, GOLD if dark else NAVY) +
            T(cx, 24, n, size=10.5, fill=tc) + T(cx, 46, t1, size=6.6) + T(cx, 55, t2, size=6.6) +
            T(cx, 69, when, font=SERIF, size=9.4, weight=600, fill=SOFT) + T(cx, 81, what, font=SERIF, size=9.4, weight=600, fill=SOFT) +
            T(cx, 97, miss, font=HAND, size=10.5, weight=400, fill=OX))
PL3 = (L('M14 20 L300 20', stroke=NAVY, sw=1.2) + arrowhead(306, 20, 'r', stroke=NAVY, sw=1.2) + L('M300 20 L306 20', stroke=NAVY, sw=1.2) +
       station(56, '1', 'SOURCES AND', 'PROCESS', 'while you research', 'your log, then a talk', 'missed: 0') +
       station(160, '2', 'ARGUMENT', 'OUTLINE', 'as you start writing', 'your outline, a talk', 'missed: 0') +
       station(264, '3', 'FINAL', 'PAPER', 'after you submit', 'I read it, then sign', 'no signature: 0', dark=True))
paper('f4-cp1', 'Folio 4',
    "<h3>Three checkpoints</h3>" +
    P("A checkpoint is a short talk with me that shows your thinking. The College Board requires them.") +
    plate('III', 'Three checkpoints, one paper', 102,
          'Three checkpoints on one line. 1, sources and process: while you research, your log, then a talk. Missed: 0. 2, argument outline: as you start writing, your outline, then a talk. Missed: 0. 3, final paper: after you submit, I read it, then sign. No signature: 0.',
          PL3, 'IN THE AP DIGITAL PORTFOLIO', 'Checkpoint 1, Sources and Process. Checkpoint 2, Argument Outline. Checkpoint 3, Final Review of Paper.') +
    card('weak', 'REQUIRED', 'Miss a checkpoint, and your written argument scores 0. I must sign for checkpoints 1 and 2, or it gets no score.', mt='.4cqw') +
    P("Checkpoint dates post on Google Classroom ahead of time. They do not move for an absence. " + CHK, style='margin-top:1cqw'))

# [H3, H4] [H5] tp p. 18, ai p. 25
paper('f4-talk1', 'Folio 4',
    "<h3>The first checkpoint talk</h3>" +
    P("A short talk with me, alone, while you research. You show your thinking and choices.") +
    table('stages wide2 tight', ['I ASK ABOUT', 'FOR EXAMPLE'], [
        ['Your process', 'How did you search?'],
        ['Your question', 'How has it changed?'],
        ['Your sources', 'Which helps most, and why?'],
        ['Their perspectives', 'What does this one argue?']]) +
    card('good', 'YOU PASS WHEN', 'You say more than the log says: a detail, a reason, a choice.') +
    P("Not yet? You redo it, with a new log and a new talk. If I think a tool did your reading, we talk about that first.", style='margin-top:1cqw') +
    P("The same talk as the team project: The Team Project, page 18. What it sounds like: The AI Manual, page 25. " + CHK))

# =====================================================================
# FOLIO 5, The outline and the second checkpoint
# =====================================================================
board('f5', 5, 'The outline and the second checkpoint', 'i-steps',
      'Turn your research into an argument, outline it, and explain your choices in a talk of about two minutes.',
      [('An argument, not a report', 'f5-argue'), ('Build the outline', 'f5-outline'),
       ('The outline talk', 'f5-cp2'), ('What the outline talk sounds like', 'f5-sounds')])

# [G11] [K2, K3, K4] paper pp. 10, 11
paper('f5-argue', 'Folio 5',
    folio('i-steps', 5) + "<h2>An argument, not a report</h2>" +
    P("Your report explained. Your written argument argues: it takes a position and defends it.") +
    table('stages narrow1 tight', ['ROW', 'THE PAPER MUST'], [
        ['1', 'Use at least one packet text inside the argument.'],
        ['2', 'Show why your question matters, in a larger context.'],
        ['3', 'Weigh other views: objections, limits, effects.'],
        ['4', 'Link claims and evidence to a clear conclusion.'],
        ['5', 'Use credible evidence, some of it scholarly.'],
        ['6', 'Cite every source, packet texts too.'],
        ['7', 'Write clearly, for an academic reader.']]) +
    P("A claim someone could dispute: Writing the Paper, page 10. The parts of an argument: Writing the Paper, page 11. " + CHK))

# [I1] [Q5 drafting row]
paper('f5-outline', 'Folio 5',
    "<h3>Build the outline</h3>" +
    P("I decide the outline&#39;s form: written, or drawn as a diagram. It shows how your ideas connect, why each section is there, and why you chose each piece of evidence and each view.") +
    table('stages narrow1 tight', ['', 'A MADE-UP OUTLINE'], [
        ['1', 'Why it matters: the question, its place and time.'],
        ['2', 'Claim A, its evidence, and a packet text.'],
        ['3', 'Claim B and its evidence.'],
        ['4', 'An objection, and your answer.'],
        ['5', 'Your conclusion or solution, and its limit.']]) +
    card('weak', 'NOT ALLOWED', 'A tool that writes your outline. A tool may give general tips on how essays are built.') +
    P(CHK, style='margin-top:1cqw') +
    wait('The outline&#39;s form in Room 63, and where it goes: on Google Classroom.'))

# PLATE IV [I1, I2] [J5]
def step(x, n, head, l1, l2, dark=False):
    fill, stroke, hc, lc = (DK, GOLD, LGOLD, '#f3e3bd') if dark else (PAPER, NAVY, NAVY, SOFT)
    return (R(x, 8, 70, 50, fill=fill, stroke=stroke, sw=1.3) +
            "<circle cx='%d' cy='20' r='6' fill='%s'/>" % (x + 11, OX) + T(x + 11, 23.3, n, size=8.5, fill='#fff8ea') +
            T(x + 20, 23, head, size=6.6, fill=hc, anchor='start') +
            T(x + 35, 39, l1, font=SERIF, size=9, weight=600, fill=lc) + T(x + 35, 50, l2, font=SERIF, size=9, weight=600, fill=lc))
PL4 = (step(2, '1', 'HAND IN', 'your outline,', 'on the day') +
       step(84, '2', 'EXPLAIN', 'about 2 minutes:', 'your choices') +
       step(166, '3', 'ANSWER', 'my follow-up', 'questions') +
       step(248, '4', 'PASS', 'you explain', 'some choices', dark=True) +
       L('M73 33 L82 33', stroke=OX) + arrowhead(83, 33, 'r') + L('M155 33 L164 33', stroke=OX) + arrowhead(165, 33, 'r') +
       L('M237 33 L246 33', stroke=OX) + arrowhead(247, 33, 'r') +
       L('M283 58 L283 70 L37 70 L37 61', stroke=OX, sw=1.3, extra=" stroke-dasharray='4 3'") + arrowhead(37, 59, 'u', sw=1.3) +
       T(160, 84, 'not yet? a new outline and a new talk', font=HAND, size=10.5, weight=400, fill=OX))
paper('f5-cp2', 'Folio 5',
    "<h3>The outline talk</h3>" +
    P("Checkpoint 2 is for the written argument only. You explain how your ideas connect, why these sections, and why this evidence.") +
    plate('IV', 'Two minutes on your outline', 90,
          'Four steps. 1, hand in your outline, on the day. 2, explain it, about 2 minutes, your choices. 3, answer my follow-up questions. 4, pass: you explain some choices. A dashed arrow loops from step 4 back to step 1: not yet? A new outline and a new talk.',
          PL4, 'REQUIRED', 'Miss it, and your written argument scores 0.') +
    P("You pass when you explain some of your choices about structure or content. If I think a tool made your outline, we talk about that before you redo it. " + CHK) +
    wait('Your outline talk date: on Google Classroom.'))

# [K3]
paper('f5-sounds', 'Folio 5',
    "<h3>What the outline talk sounds like</h3>" +
    P("Say why, not only what. Name a choice and its reason.") +
    card('weak', 'WEAK, A MADE-UP CASE', '&quot;First I talk about benches. Then I talk about buses. Then I conclude.&quot;', mt='.8cqw') +
    card('good', 'STRONG, A MADE-UP CASE', '&quot;I open with the wait-time study, because it shows who uses the stop. The objection comes after my strongest evidence, so I can answer it.&quot;', mt='.8cqw') +
    tryit('NEXT STEP', 'I ask: &quot;Why is this packet text in section 2?&quot; You say: &quot;We had to use one.&quot; Weak or strong?',
          'Weak. Say what it does: it gives context, or it is evidence for a claim.') +
    P(CHK, style='margin-top:1cqw'))

# =====================================================================
# FOLIO 6, The written argument, row by row
# =====================================================================
board('f6', 6, 'The written argument, row by row', 'i-pen',
      'Write an argument that follows the rules and earns the first four rows.',
      [('The rules and the shape', 'f6-rules'), ('Where the 48 points are', 'f6-points'), ('Row 1: a packet text, used', 'f6-row1'),
       ('Row 2: why your question matters', 'f6-row2'), ('Row 3: views in conversation', 'f6-row3'), ('Row 4: your argument', 'f6-row4')])

# [K1] [K7] [K4, K6] [K5] [K7, S7] [K8] Y5: no penalty stated, say only "stay within"
paper('f6-rules', 'Folio 6',
    folio('i-pen', 6) + "<h2>The rules and the shape</h2>" +
    table('stages rules tight', ['RULE', 'WHAT IT MEANS'], [
        ['2,000 words or fewer', 'Titles, sub-headings, and citations in your sentences count. Your list of sources, footnote citations, and words in figures or tables do not.'],
        ['No names', 'Take out your name, your school, and my name.'],
        ['Every source cited', 'Packet texts too, in your sentences and in a list at the end.'],
        ['One style', 'Any style, used the same way (The Research Manual, page 59).'],
        ['A PDF', 'Google Docs: File, then Download, then PDF Document.']]) +
    P("A paper with no link to a theme from two packet texts is off-topic. It earns 0 points. Your report&#39;s rules: The Team Project, page 19. " + CHK))

# PLATE V [L, M1] [M3] [K10] [A5, Y3]
ROWS = [('1 PACKET TEXT', 5, 3.02), ('2 CONTEXT', 5, 3.27), ('3 PERSPECTIVE', 9, 5.22), ('4 ARGUMENT', 12, 7.09),
        ('5 EVIDENCE', 9, 5.52), ('6 CITATION', 5, 3.11), ('7 GRAMMAR, STYLE', 3, 2.11)]
def pl5():
    s, x0, k = '', 92, 13.0
    for i, (lab, mx, mean) in enumerate(ROWS):
        y = 4 + i * 18
        s += T(4, y + 9, lab, size=7, fill=NAVY, anchor='start')
        s += R(x0, y, mx * k, 12, fill=PAPER, stroke=NAVY, sw=1, rx=2)
        s += R(x0 + 1.2, y + 1.2, round(mean * k - 1.2, 1), 9.6, fill=NAVY, stroke='none', sw=0, rx=1.5)
        s += T(round(x0 + mx * k + 5, 1), y + 9, '%.2f of %d' % (mean, mx), size=7, fill=SOFT, anchor='start')
    # bracket and note on rows 3 and 4
    s += L('M290 42 C298 42 300 50 300 58 C300 66 298 74 290 74', stroke=OX, sw=1.2)
    s += T(316, 140, 'lowest for their size', font=HAND, size=11, weight=400, fill=OX, anchor='end')
    s += L('M300 60 L306 128', stroke=OX, sw=1, extra=" stroke-dasharray='2 2'")
    s += T(4, 140, 'OVERALL 29.35 OF 48', size=7, fill=OX, anchor='start')
    return s
paper('f6-points', 'Folio 6',
    "<h3>Where the 48 points are</h3>" +
    P("Readers score each row on its own. Rows 1 and 2 are all or nothing: 0 or 5.") +
    plate('V', 'Seven rows, 48 points', 146,
          'Seven bars, one per row. Each bar is as long as the row\'s top score. The dark part is the 2025 national average. Row 1, packet text: 3.02 of 5. Row 2, context: 3.27 of 5. Row 3, perspective: 5.22 of 9. Row 4, argument: 7.09 of 12. Row 5, evidence: 5.52 of 9. Row 6, citation: 3.11 of 5. Row 7, grammar and style: 2.11 of 3. Overall 29.35 of 48. Rows 3 and 4 are the lowest for their size.',
          pl5(), '2025 NATIONAL AVERAGE', 'The dark part of each bar. The whole bar is the top score.') +
    P("In 2025, Rows 3 and 4 had the lowest averages for their size.") +
    P("From the %s, the newest posted. The 2027 guidelines come out after the exam. %s" % (link('https://apcentral.collegeboard.org/media/pdf/ap26-sg-seminar-pt2.pdf', '2026 scoring guidelines'), CHK)))

# [L row 1] [M4]
paper('f6-row1', 'Folio 6',
    "<h3>Row 1: a packet text, used</h3>" + rowq(1, 'Understand and Analyze Context', '0 or 5 points') +
    P("Readers ask: does a packet text do work in your argument? One text, used well, is enough. It scores 0 if the text gets one sentence, or if you could delete it and lose nothing.") +
    card('weak', 'WEAK, A MADE-UP CASE', '&quot;As Ortiz once wrote, benches matter. Now, on to my topic.&quot;', mt='.8cqw') +
    card('good', 'STRONG, A MADE-UP CASE', '&quot;Ortiz argues that a bench serves riders first. The wait-time study tests her claim: most riders at these stops wait only minutes.&quot;', mt='.8cqw') +
    P("Weak in 2025: a packet text as a forced jumping-off point, a quote out of context, or a fact any source could give. " + CHK, style='margin-top:1cqw'))

# [L row 2] fg p. 22
paper('f6-row2', 'Folio 6',
    "<h3>Row 2: why your question matters</h3>" + rowq(2, 'Understand and Analyze Context', '0 or 5 points') +
    P("A 5 explains why your question matters by placing it in a larger context. It is narrow enough to show how complex the problem is. The College Board&#39;s example: water pollution in India. It makes a specific case for why the question is urgent.") +
    card('weak', 'WEAK, A MADE-UP CASE', '&quot;Public space is important to everyone.&quot;', mt='.8cqw') +
    card('good', 'STRONG, A MADE-UP CASE', '&quot;The county is choosing now which stops keep benches. Riders over 65 use those seats most. Who a stop serves is being decided this year.&quot;', mt='.8cqw') +
    P("Test it: finish &quot;so that readers understand ___&quot; (The Field Guide, page 22). " + CHK, style='margin-top:1cqw'))

# [L row 3 top and note] tp p. 23, log p. 36
paper('f6-row3', 'Folio 6',
    "<h3>Row 3: views in conversation</h3>" + rowq(3, 'Understand and Analyze Perspective', '0, 6, or 9 points') +
    P("A 9 weighs several views and joins them: links between them, objections, effects, and limits. Tie each view to its source, every time. Readers need clear attribution to score high.") +
    table('stages wide2 tight', ['CHECK', 'ASK'], [
        ['Objection', 'Who disagrees, and why?'],
        ['Limit', 'Where does this view stop being true?'],
        ['Effect', 'If it is right, what follows?']]) +
    P("Boxes or dialogue: The Team Project, page 23. " + CHK) +
    tryit('GOING FURTHER', 'Your paper gives a view and a source that disagrees. What is missing for a 9?',
          'Weigh them. Say where each is right, where it stops, and what follows.'))

# [L row 4 top and notes] paper pp. 11, 12
paper('f6-row4', 'Folio 6',
    "<h3>Row 4: your argument</h3>" + rowq(4, 'Establish Argument', '0, 8, or 12 points') +
    P("A 12 is a clear, convincing argument. It is logically organized, and it connects claims and evidence to a plausible conclusion that answers your question. It is driven by your own voice: your comments on the evidence. A paper that only summarizes earns 0.") +
    card('weak', 'WEAK, A MADE-UP CASE', '&quot;Ortiz says benches serve riders. The study says waits are short. The shelter group says people need rest.&quot;', mt='.8cqw') +
    card('good', 'STRONG, A MADE-UP CASE', '&quot;Short waits weaken Ortiz&#39;s claim. If riders sit for minutes, one bench can serve riders and people who need rest. The county should keep its benches open.&quot;', mt='.8cqw') +
    P("Claim, reason, evidence: Writing the Paper, pages 11 and 12. " + CHK, style='margin-top:1cqw'))

# =====================================================================
# FOLIO 7, Finish and submit the argument
# =====================================================================
board('f7', 7, 'Finish and submit the argument', 'i-check',
      'Earn Rows 5 to 7, check your draft, and submit your written argument as final.',
      [('Row 5: evidence you can trust', 'f7-row5'), ('Rows 6 and 7: credit and clear writing', 'f7-row67'),
       ('Score your own draft', 'f7-score'), ('Before you submit', 'f7-before'), ('Submit it as final', 'f7-submit')])

# [L row 5 top and note]
paper('f7-row5', 'Folio 7',
    folio('i-check', 7) + "<h2>Row 5: evidence you can trust</h2>" + rowq(5, 'Select and Use Evidence', '0, 6, or 9 points') +
    P("A 9 has relevant, credible, and enough evidence to support your argument. It scores 0 if no source beyond the packet is well vetted. Encyclopedias and dictionaries do not count.") +
    P("For each key source, say why it is credible and why it fits (The Team Project, page 22).") +
    table('stages wide1 tight', ['TO DO THIS', 'GO TO'], [
        ['One number, four questions', 'The Research Manual, page 42'],
        ['Scholarly or popular?', 'The Research Manual, page 46']]) +
    P(CHK))

# [L rows 6, 7] [Q5 citations row]
paper('f7-row67', 'Folio 7',
    "<h3>Rows 6 and 7: credit and clear writing</h3>" +
    notes('ROW 6 &middot; &quot;APPLY CONVENTIONS&quot;: CITATION &middot; 0, 3, OR 5',
          'A 5 credits every source accurately, in your sentences or in footnotes. Your list uses one style throughout.',
          'No list, or citations missing from most of your sentences: 0.',
          'A tool may draft your list from sources you read. Check every entry (The Research Manual, page 63). Never cite a source you did not read.') +
    notes('ROW 7 &middot; &quot;APPLY CONVENTIONS&quot;: GRAMMAR AND STYLE &middot; 0, 2, OR 3',
          'Readers score your sentences, not the ones you quote. A few errors are allowed. Clear beats fancy.',
          'Cut, then punctuate: Writing the Paper, page 20.') +
    P(CHK, style='margin-top:1cqw'))

# [R: peer review guidelines]
paper('f7-score', 'Folio 7',
    "<h3>Score your own draft</h3>" +
    P("Before peer review, find each row&#39;s move.") +
    form('ipdraft', 'MY DRAFT', [('ROWS 1 TO 7', [
        '1 A packet text works inside my argument.', '2 Why my question matters, and to whom.',
        '3 Views weighed, each tied to its source.', '4 My claims lead to my conclusion.',
        '5 Scholarly sources beyond the packet.', '6 Every citation is on my list.', '7 Every sentence clear.'])]) +
    P("Peer review: The Team Project, page 26. The words stay yours. " + CHK) +
    wait('Your peer readers: on Google Classroom.'))

# [K1] [K7] [K4] rlog p. 60 [P5] [K7] [J1, P6] [Y16]
paper('f7-before', 'Folio 7',
    "<h3>Before you submit</h3>" +
    form('ipsubmit', 'MY PAPER', [('SIX CHECKS', [
        '2,000 words or fewer, the list not counted.', 'No name, school, or teacher, even in the header.',
        'Every source is on my list, packet texts too.', 'Closed-tools test: yes (The Research Log, page 60).',
        'Run Originality, View Originality, wording fixed.', 'Saved as a PDF file.'])]) +
    P("I read your final paper next to your checkpoints and your usual writing. Turnitin gives me a tool-writing report you do not see.") +
    P("Button names: College Board student guide, Summer 2026, not yet checked on a Room 63 iPad. " + CHK))

# [S2] [S5, S6] [S5, R TUG] [B] STUTL [N4] [P7]
paper('f7-submit', 'Folio 7',
    "<h3>Submit it as final</h3>" +
    table('stages narrow1 tight', ['STEP', 'DO THIS'], [
        ['1', 'Follow your report&#39;s steps: The Team Project, page 28. Choose Individual Written Argument.'],
        ['2', 'Only your latest upload is sent. A draft is never scored.'],
        ['3', 'Check that the status says Submitted.']]) +
    P("After final, it cannot change. Only I can send it back, and only for a wrong, broken, or unreadable file, never for quality. Then you submit it as final again.") +
    P("Last moment: April 30, 2027, 11:59 in the evening, Eastern Time. Upload early. The last night is slow. Every paper and slide deck is collected before anyone presents. Never post your paper online. " + CHK) +
    wait('My due date for your paper: on Google Classroom. It comes before the first talk.'))

# =====================================================================
# FOLIO 8, Honest work
# =====================================================================
board('f8', 8, 'Honest work', 'i-sign',
      'Credit every source, invent nothing, use tools only where the College Board allows, and know what I sign.',
      [('Credit every source, invent nothing', 'f8-credit'), ('Tools that write, stage by stage', 'f8-tools'),
       ('Turnitin, and what I sign', 'f8-sign')])

# [P1] [P2] [P8] [P3] [P7] [V2] [Z10]
paper('f8-credit', 'Folio 8',
    folio('i-sign', 8) + "<h2>Credit every source, invent nothing</h2>" +
    table('stages wide1 tight', ['BROKEN RULE', 'WHAT IT COSTS'], [
        ['A source with no credit', '0 on that part of the task'],
        ['Made-up evidence, data, sources, or authors', '0 on that part of the task'],
        ['A paper used again, even your own', 'Not allowed']]) +
    P("Your own voice should be clear. Other people&#39;s ideas are credited. Practice papers get uploaded by mistake: open your file before you submit.") +
    card('weak', 'NEVER POST IT', 'Work posted online can be copied. If it is, both students are flagged for plagiarism.', mt='.8cqw') +
    P("The rules: %s. What a zero costs: The AI Manual, page 24. %s" % (link('https://apcentral.collegeboard.org/courses/resources/ap-capstone-policies', 'AP Capstone policies'), CHK), style='margin-top:1cqw'))

# [Q1, Q3, Q4] [Q5] [Q2, Y12, Y13] fg p. 4, ai p. 6
paper('f8-tools', 'Folio 8',
    "<h3>Tools that write, stage by stage</h3>" +
    P("Tools are optional. Your paper must be your own work. Tools that write include chatbots and many writing helpers.") +
    table('stages checks tight', ['STAGE', 'ALLOWED', 'NOT ALLOWED'], [
        ['Explore', 'What people debate', 'Its question or thesis, used uncritically'],
        ['Find sources', 'Names to find and read', 'Its list, unread'],
        ['Read', 'Help with a hard passage', 'Its summary instead'],
        ['Join sources', 'Nothing', 'Any comparing'],
        ['Outline, draft', 'General tips on structure', 'Any outline or text'],
        ['Revise', 'Grammar and tone tips', 'Its new sentences']]) +
    P("The policy names four uses (The AI Manual, page 6). Its stage table allows a little more. Room 63 adds: no tool writes, rewrites, or narrows your question (The Field Guide, page 4). Citations: page %s. %s" % (pj('f7-row67'), CHK)))

# [P4] [P5, P6, Y14] [J1] [J2] [J6, B] [J7, J8, Y8]
paper('f8-sign', 'Folio 8',
    "<h3>Turnitin, and what I sign</h3>" +
    P("The College Board runs every final paper through Turnitin, for copying and for text a tool wrote. You may run Originality yourself first. You see the originality report. Only I see the tool-writing report.") +
    P("Checkpoint 3: after you submit, I read your paper. Is it like your usual writing? Like what I saw at your checkpoints? Is its tool-writing score low? The College Board warns that this score may not be accurate, and should never be the only reason.") +
    P("Then I sign that it is yours, by May 10, 2027. No signature: your written argument scores 0. " + CHK) +
    card('weak', 'IF I CANNOT SIGN', 'I file a report. The College Board may ask for your drafts and notes. Keep your log, your outline, and your Google Doc&#39;s version history.'))

# =====================================================================
# FOLIO 9, Your talk and two questions
# =====================================================================
board('f9', 9, 'Your talk and two questions', 'i-podium',
      'Turn your written argument into a 6 to 8 minute talk, and answer two questions with specific evidence.',
      [('Your talk at a glance', 'f9-talk'), ('What earns points in the talk', 'f9-rows'),
       ('The defense: two questions', 'f9-defense'), ('The day', 'f9-day')])

# [N1] [N3] [N5, N6] [N7] [N2] Y6: no penalty for a short talk
paper('f9-talk', 'Folio 9',
    folio('i-podium', 9) + "<h2>Your talk at a glance</h2>" +
    P("Your talk presents the argument and conclusions of your written argument, in 6 to 8 minutes, for educated people who are not experts.") +
    P("Only the first 8 minutes are scored. The questions come after and do not count toward the 8. It is live, never recorded ahead. Nothing is uploaded for it.") +
    card('weak', 'NO PAPER, NO SCORE', 'No written argument, no score for your talk or its questions.', mt='.8cqw') +
    P("The talk shows why your question matters, links your research to the packet, credits your evidence out loud or on a slide, and offers a conclusion or solution with its effects.", style='margin-top:1cqw') +
    P("Build it: Presenting and Defending, Folios 2 to 6. Your own talk: six cards, about 7 minutes (Presenting and Defending, page 14). " + CHK))

# [N8] [Q5 presentations row] pd p. 9
paper('f9-rows', 'Folio 9',
    "<h3>What earns points in the talk</h3>" +
    table('stages wide2 tight', ['ROW', 'WHAT EARNS POINTS'], [
        ['1 Context', 'Why your question matters, and its link to the packet.'],
        ['2 Argument', 'An argument. A summary earns 2.'],
        ['3 Evidence', 'Evidence from several perspectives, joined together.'],
        ['4 Conclusion', 'A detailed, realistic conclusion or solution, with its limits and effects.'],
        ['5 Design', 'Slides for the audience, not your essay pasted in.'],
        ['6 Delivery', 'Eyes, voice, movement, and energy that carry the argument.']]) +
    P("36 points, each row 0, 2, 4, or 6. Above 2 on Row 1 needs a link to the packet. One conclusion or solution is enough.") +
    P("Tools may give tips and first ideas. They may not make your key points, visuals, or order, or write a script. In plain words: Presenting and Defending, page 9. " + CHK))

# [O1] [O2] [O3] [O4, O5] [Q5 oral defense row] pd pp. 35, 36
paper('f9-defense', 'Folio 9',
    "<h3>The defense: two questions</h3>" +
    P("Right after your talk, I ask two questions, one from each list. I may add a follow-up so you can explain more.") +
    table('stages wide2 tight', ['LIST', 'FOR EXAMPLE'], [
        ['1 Your process', 'How did your question change?'],
        ['2 Your argument', 'What do your findings mean for your community?']]) +
    P("I can give you the whole list. I cannot tell you your two. Be ready for every one.") +
    P("12 points: two rows, each 0, 2, 4, or 6. The top is a detailed answer with specific evidence. Only repeating your talk, or missing the question, is a 2. The defense does not change your talk score.") +
    card('weak', 'NO TOOL', 'No tool may write answers for you to practice or memorize.', mt='.8cqw') +
    P("Every question: Presenting and Defending, page 35. A strong answer: Presenting and Defending, page 36. " + CHK, style='margin-top:1cqw'))

# [N4] [R] WAIT 10 as pd f53, f54, f56
paper('f9-day', 'Folio 9',
    "<h3>The day</h3>" +
    P("Every paper and slide deck is collected before anyone presents. You present that version.") +
    P("I video record every talk and defense, and keep the video at least one school year.") +
    P("I score your talk and your defense. I cannot tell you your scores. The College Board does not allow it. " + CHK) +
    wait('Your own talk: March 17 to April 15, 2027. Your day and time: on Google Classroom. Audience: your class, in Room 63. Absent on your day? The next open slot in the same week.') +
    P("The day before: Presenting and Defending, page 43.", style='margin-top:1cqw') +
    newword('ORAL DEFENSE', 'defensa oral', 'The two questions after your talk.'))

# =====================================================================
# FOLIO 10, When you get stuck
# =====================================================================
board('f10', 10, 'When you get stuck', 'i-tool',
      'Get unstuck on the work, keep going through an absence, and fix a problem with your file or your score.',
      [('Stuck on the work', 'f10-stuck'), ('Absent, sick, or behind', 'f10-missed'), ('Your file and your score', 'f10-score')])

# [R]
paper('f10-stuck', 'Folio 10',
    folio('i-tool', 10) + "<h2>Stuck on the work</h2>" +
    table('stages wide2 tight', ['I AM STUCK ON', 'TRY THIS'], [
        ['No theme yet', 'Read the packet again. Draw lines between texts (page %s).' % pj('f3-links')],
        ['A question too big', 'Add one place, one time, one group (page %s).' % pj('f3-question')],
        ['Too few scholarly sources', 'Search EBSCO through the AP Digital Portfolio (page %s).' % pj('f4-beyond')],
        ['A paper that only summarizes', 'Name your claim. Say what each source does for it (page %s).' % pj('f5-argue')],
        ['A tool I am not sure about', 'Ask me before, not after (page %s).' % pj('f8-tools')]]) +
    P("Still stuck? See me next class. I can ask questions and suggest places to look. I cannot give you a question, sources, or sentences. " + CHK))

# [J5] [U5] [U6, B] [U4, B]
paper('f10-missed', 'Folio 10',
    "<h3>Absent, sick, or behind</h3>" +
    P("We meet every other school day. One missed class is a long gap. Read Google Classroom the same day.") +
    P("Missing a checkpoint? See me next class. The checkpoint must happen, or your paper scores 0.") +
    notes('COLLEGE BOARD RULES',
          'A long absence: the school and I try to keep you in the task, with technology or other ways.',
          'School days lost to closures: the school can ask the College Board for more time, before March 12, 2027.',
          'A documented disability: accommodations are possible. The school&#39;s deadline to request them is January 22, 2027. See your school&#39;s accommodations coordinator well before.') +
    P("Absent on your talk day: page %s. %s" % (pj('f9-day'), CHK), style='margin-top:1cqw'))

# [T1, T2] [T3] [R TUG, B] [T4] [T5]
paper('f10-score', 'Folio 10',
    "<h3>Your file and your score</h3>" +
    table('stages wide1 tight', ['IF', 'THEN'], [
        ['My table does not say Registered for exam', 'Your work is not sent for scoring. Tell me or the AP coordinator now.'],
        ['I submit my paper but miss the May exam', 'No AP Seminar score. The exam: The End-of-Course Exam.'],
        ['I submitted the wrong file as final', 'See me the same day. I can return it. You submit it as final again by April 30.'],
        ['I want to cancel one part', 'Canceling removes the whole AP Seminar score.'],
        ['I hope for a rescore', 'Performance tasks are never rescored.']]) +
    P("Submitting anything as final means you get a score, unless you cancel it. " + CHK))

# =====================================================================
# BACK MATTER
# =====================================================================
paper('selfcheck', 'Self-check',
    "<h3>The individual project, ready</h3>" +
    form('ipready', 'MY PROJECT', [
        ('FIRST STEP &middot; MY QUESTION', ['My theme links two texts I can name.', 'My question is one question, with a place and a time.', 'Every source I read is in my log.']),
        ('NEXT STEP &middot; MY PAPER', ['2,000 words or fewer, no names.', 'A packet text works inside my argument.', 'Status says Submitted.']),
        ('GOING FURTHER &middot; MY TALK', ['My talk runs 6 to 8 minutes, timed twice.', 'I answered every question on the list once.', 'I can name one objection, and my answer.'])]) +
    P("A box you cannot tap is your next step: page %s." % pj('start'), cls='small fill'))

paper('fool', 'Words that fool you',
    "<h3>Words that fool you</h3>" + P("Some English words look like Spanish words but mean something else.") +
    "<table class='stages'><thead><tr><th>ENGLISH</th><th>IN SPANISH</th><th>NOT</th></tr></thead><tbody>"
    "<tr><th>large</th><td><span lang='es'>grande, amplio</span></td><td><span lang='es'>largo</span>, long</td></tr>"
    "<tr><th>to resume</th><td><span lang='es'>retomar, continuar</span></td><td><span lang='es'>resumir</span>, to summarize</td></tr>"
    "<tr><th>eventually</th><td><span lang='es'>con el tiempo, al final</span></td><td><span lang='es'>eventualmente</span>, which usually means possibly</td></tr>"
    "<tr><th>compromise</th><td><span lang='es'>acuerdo, t&eacute;rmino medio</span></td><td><span lang='es'>compromiso</span>, a promise or a duty</td></tr>"
    "<tr><th>assignment</th><td><span lang='es'>tarea, trabajo</span></td><td><span lang='es'>asignatura</span>, a school subject</td></tr>"
    "</tbody></table>" +
    P("Most task words match: <span lang='es'>tema, objeci&oacute;n, contexto, s&iacute;ntesis</span>."))

paper('words1', 'Words in this book',
    "<h2>Words in this book</h2>" + P("Tap a page to go there.") +
    wrow('i-pen', 'Argument', 'argumento', 'A position you defend with reasons and evidence.', 'f6-row4') +
    wrow('i-sign', 'Authentic', 'aut&eacute;ntico', 'Your own work. I sign that it is.', 'f8-sign') +
    wrow('i-check', 'Checkpoint', 'punto de control', 'A required talk with me. Missing one scores your paper 0.', 'f4-cp1') +
    wrow('i-compass', 'Context', 'contexto', 'Why your question matters, and the bigger picture it fits.', 'f6-row2') +
    wrow('i-steps', 'Implication', 'implicaci&oacute;n', 'A possible future effect.', 'f9-rows'))
paper('words2', 'Words in this book',
    "<h3>Words in this book, continued</h3>" +
    wrow('i-link', 'Integrate', 'integrar', 'To use a source inside your argument, not only mention it.', 'f6-row1') +
    wrow('i-cross', 'Limitation', 'limitaci&oacute;n', 'The point where an argument stops being true.', 'f6-row3') +
    wrow('i-bubble', 'Objection', 'objeci&oacute;n', 'A reason someone gives against a view.', 'f6-row3') +
    wrow('i-podium', 'Oral defense', 'defensa oral', 'The two questions after your talk.', 'f9-defense') +
    wrow('i-steps', 'Outline', 'esquema', 'The plan of your argument, section by section.', 'f5-outline'))
paper('words3', 'Words in this book',
    "<h3>Words in this book, continued</h3>" +
    wrow('i-eye', 'Perspective', 'perspectiva', 'A point of view with its reason.', 'f2-read') +
    wrow('i-zero', 'Plagiarism', 'plagio', 'Words or ideas used with no credit.', 'f8-credit') +
    wrow('i-compass', 'Research question', 'pregunta de investigaci&oacute;n', 'The one question your task answers. It is yours.', 'f3-yours') +
    wrow('i-book', 'Scholarly', 'acad&eacute;mico', 'Written by experts, often checked by other experts, like a journal article.', 'f4-beyond'))
paper('words4', 'Words in this book',
    "<h3>Words in this book, continued</h3>" +
    wrow('i-book', 'Stimulus text', 'texto de est&iacute;mulo', 'A source the College Board gives you for a task or the exam.', 'f2-what') +
    wrow('i-box', 'Submit as final', 'entregar como final', 'Send your paper to the College Board. After this it cannot change.', 'f7-submit') +
    wrow('i-history', 'Synthesis', 's&iacute;ntesis', 'Joining ideas from many sources into one new understanding.', 'f6-row3') +
    wrow('i-link', 'Theme', 'tema en com&uacute;n', 'An idea that two or more texts share.', 'f3-theme') +
    P("A heritage-language dictionary is welcome for any other word.", cls='small fill'))

add('last', 'endpaper', 'The last page',
    "<div class='panel'><div class='kept'>THE LAST PAGE</div><div class='who' style='font-size:7cqw'>Everyone reads the same packet. Only you can ask your question.</div>"
    "<div class='meta' style='margin-top:3cqw'>Kept in Room 63<br>AP Capstone, Mater Academy<br>2026-27</div>{{TILDE}}<button type='button' class='loopbtn' data-jump='2'>Back to the contents</button></div><div class='shade'></div>")
add('endpaper', 'endpaper marbled', 'Endpaper', "<div class='shade'></div>")
add('back', 'board lthr', 'Back cover',
    '<svg class="A-art" viewBox="0 0 720 1000" preserveAspectRatio="none" aria-hidden="true" focusable="false"><g filter="url(#A-grain)"><rect class="A-leather" width="720" height="1000"/><g filter="url(#A-recess)"><ellipse class="A-onlay" cx="360" cy="500" rx="150" ry="112"/></g></g><rect width="720" height="1000" fill="url(#A-vig)"/><rect width="720" height="1000" fill="url(#A-sheen)"/><rect width="22" height="1000" fill="url(#A-hinge)" transform="translate(720 0) scale(-1 1)"/><g filter="url(#A-gilt)"><rect width="720" height="1000" fill="url(#A-goldg)" mask="url(#A-backmask)"/></g><g class="A-titleart" filter="url(#A-titlef)" fill="url(#A-titleg)" text-anchor="middle"><text class="A-t-big" x="360" y="494" font-size="50">ROOM 63</text><text class="A-t-big" x="360" y="550" font-size="17" letter-spacing="3">AP CAPSTONE &#183; 2026-27</text></g></svg><div class=\'shade\'></div>')

# ---------- text-node escaping: apostrophes and quotes in visible text ----------
def esc_text(h):
    return re.sub(r'>([^<]+)<', lambda m: '>' + m.group(1).replace("'", '&#39;').replace('"', '&quot;') + '<', h)

for f in FACES:
    if f['cls'] not in ('board lthr',):
        f['html'] = esc_text(f['html'])

spec = {'key': 'ip', 'title': 'The Individual Project', 'theme': '#1f3a2c',
        'colors': {'leather': '#1f3a2c', 'onlay': '#0b120e', 'labelskin': '#6d1f1b'},
        'faces': FACES}
print(json.dumps(spec, ensure_ascii=False, indent=1))
