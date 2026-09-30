#!/usr/bin/env python3
"""Book S3, The End-of-Course Exam (key "ex"). Prints the spec for tools/build_book.py.

Every College Board fact comes from ex/facts.md (checked September 30, 2026).
Markup follows The Team Project (tp_faces.json). Page numbers are [[...]] tokens only.
"""
import json, math

HEAD = 'THE END-OF-COURSE EXAM'
CK = 'Checked September 30, 2026.'

# ---------------------------------------------------------------- text helpers
def tx(s):
    """Prose: straight apostrophes become &#39; (attributes in this spec use single quotes)."""
    return s.replace("'", '&#39;')

def page(body, folio=None, icon=None):
    top = "<div class='grainlayer grain'></div><div class='pg'><div class='head'><span>%s</span><span>{{SHORT}}{{PHEAD}}</span></div>" % HEAD
    if folio:
        top += "<p class='folio'><svg class='femb' aria-hidden='true'><use href='#%s'/></svg>FOLIO %d</p>" % (icon, folio)
    return top + body + "</div>[[num]]<div class='shade'></div>"

def h2(s): return '<h2>%s</h2>' % tx(s)
def h3(s): return '<h3>%s</h3>' % tx(s)
def p(s, fill=False): return "<p class='small%s'>%s</p>" % (' fill' if fill else '', tx(s))

def table(cls, head, rows, style=''):
    h = ''.join('<th>%s</th>' % tx(c) for c in head)
    b = ''
    for r in rows:
        b += '<tr><th>%s</th>%s</tr>' % (tx(r[0]), ''.join('<td>%s</td>' % tx(c) for c in r[1:]))
    st = " style='%s'" % style if style else ''
    return "<table class='stages %s'%s><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (cls, st, h, b)

def card(kind, label, text, mt='1.2cqw'):
    cls = ('card2 ' + kind) if kind else 'card2 '
    return "<div class='%s' style='margin-top:%s'><div class='k'>%s</div><p>%s</p></div>" % (cls, mt, tx(label), tx(text))

def wait(text):
    return card('wait', 'WAITING ON A ROOM 63 DECISION', text)

def tryit(level, q, a):
    return ("<div class='card2 try' style='margin-top:1.2cqw'><div class='k'>TRY IT &middot; %s</div><p>%s</p>"
            "<p class='small ans' role='button' tabindex='0' aria-label='Show the answer' aria-expanded='false' style='margin-top:.6cqw'>%s</p></div>") % (level, tx(q), tx(a))

def newword(en, es, line):
    return "<div class='card2 ' style='margin-top:1.2cqw'><div class='k'>NEW WORD &middot; %s</div><p><em lang='es' class='esw'>%s</em> &middot; %s</p></div>" % (en, es, tx(line))

def rowq(n, name, pts):
    return "<p class='rowq'><span class='rown'>ROW %d</span>&quot;%s&quot; &middot; %s</p>" % (n, name, pts)

def link(url, text):
    return "<a href='%s' target='_blank' rel='noopener'>%s</a>" % (url, tx(text))

STAMP = ("<svg class='passstamp' viewBox='0 0 150 50' aria-hidden='true'><rect x='3' y='3' width='144' height='44' rx='7' fill='none' stroke='#1f5c4a' stroke-width='3'/>"
         "<rect x='8' y='8' width='134' height='34' rx='4' fill='none' stroke='#1f5c4a' stroke-width='1.4'/><text x='75' y='33' text-anchor='middle' "
         "font-family='Space Mono,monospace' font-weight='700' font-size='21' letter-spacing='4' fill='#1f5c4a'>CHECKED</text></svg>")

def form(name, left, groups):
    h = "<div class='form' data-form='%s'><div class='fhead'><span>%s</span><span>TAP WHAT IS TRUE</span></div>" % (name, left)
    for lab, ticks in groups:
        h += "<p class='tierlab'>%s</p>" % lab
        for t in ticks:
            h += "<button type='button' class='tick' aria-pressed='false' aria-label='%s'><span class='bx' aria-hidden='true'></span>%s</button>" % (tx(t), tx(t))
    return h + STAMP + "<span class='live srt' aria-live='polite'></span></div>"

# ---------------------------------------------------------------- svg helpers
MONO = 'Space Mono,Courier New,monospace'
SERIF = 'Cormorant Garamond,Georgia,serif'
HAND = 'Patrick Hand,cursive'
NAVY, RED, PINE, BRASS, DEEP, GOLD, PAPER, CREAM, BROWN, INK = '#1f3a5a', '#9c3322', '#245e55', '#b8903f', '#16294a', '#e8c878', '#fbf6ea', '#f6edd6', '#4a3f31', '#1d1812'

def T(x, y, s, font=MONO, size=7, weight=700, fill=NAVY, anchor='start'):
    return "<text x='%s' y='%s' font-family='%s' font-size='%s' font-weight='%s' fill='%s' text-anchor='%s'>%s</text>" % (x, y, font, size, weight, fill, anchor, tx(s))

def R(x, y, w, h, fill=PAPER, stroke=NAVY, sw=1.2, rx=3, dash=None):
    d = " stroke-dasharray='%s'" % dash if dash else ''
    return "<rect x='%s' y='%s' width='%s' height='%s' rx='%s' fill='%s' stroke='%s' stroke-width='%s'%s/>" % (x, y, w, h, rx, fill, stroke, sw, d)

def L(x1, y1, x2, y2, stroke=NAVY, sw=1.2, dash=None):
    d = " stroke-dasharray='%s'" % dash if dash else ''
    return "<path d='M%s %s L%s %s' fill='none' stroke='%s' stroke-width='%s'%s/>" % (x1, y1, x2, y2, stroke, sw, d)

def A(x1, y1, x2, y2, stroke=RED, sw=1.3, both=False):
    def head(xa, ya, xb, yb):
        dx, dy = xb - xa, yb - ya; n = math.hypot(dx, dy); ux, uy = dx / n, dy / n
        bx, by = xb - 3.9 * ux, yb - 3.9 * uy; px, py = -uy * 1.7, ux * 1.7
        return "<path d='M%.1f %.1f L%.1f %.1f L%.1f %.1f' fill='none' stroke='%s' stroke-width='%s' stroke-linejoin='round'/>" % (bx + px, by + py, xb, yb, bx - px, by - py, stroke, sw)
    s = L(x1, y1, x2, y2, stroke, sw) + head(x1, y1, x2, y2)
    if both: s += head(x2, y2, x1, y1)
    return s

def plate(num, title, vb_h, aria, svg, cap_b, cap):
    return ("<figure class='plate'><div class='pl'><span>PLATE %s</span><span>%s</span></div>"
            "<svg class='fig' viewBox='0 0 320 %s' role='img' aria-label='%s'>%s</svg>"
            "<figcaption><b>%s</b>%s</figcaption></figure>") % (num, tx(title), vb_h, tx(aria), svg, tx(cap_b), tx(cap))

# ---------------------------------------------------------------- boards
def board(folio, title, icon, target, inside):
    lis = ''.join("<li><span class='it'>%s</span><span class='ld' aria-hidden='true'></span><span class='pn'>[[pno:%s]]</span></li>" % (tx(t), i) for t, i in inside)
    html = ("<div class='chap'>{{GOLD}}<div class='ch-in'><div class='ch-top'>FOLIO</div><div class='ch-num'>%d</div><div class='ch-title'>%s</div>"
            "<svg class='ch-rule' viewBox='0 0 120 12' aria-hidden='true'><line x1='4' y1='6' x2='48' y2='6'/><path d='M60 1 l5 5 -5 5 -5 -5z'/><line x1='72' y1='6' x2='116' y2='6'/></svg>"
            "<svg class='ch-icon' aria-hidden='true'><use href='#%s'/></svg><div class='ch-target'><div class='k'>BY THE END</div><p>%s</p></div>"
            "<div class='ch-inside'><div class='k'>INSIDE</div><ul>%s</ul></div></div></div><div class='num ch-pn'>&middot; x &middot;</div><div class='shade'></div>") % (folio, tx(title), icon, tx(target), lis)
    return {'cls': 'board chapter', 'html': html, 'label': 'Folio %d' % folio, 'id': 'b%d' % folio, 'folio': folio, 'title': title}

def paper(id_, label, html):
    return {'cls': 'paper', 'html': html, 'label': label, 'id': id_}

FACES = []
def add(f): FACES.append(f)

# ================================================================ FRONT
add({'cls': 'board lthr', 'label': 'Cover', 'html':
    '<svg class="A-art" viewBox="0 0 720 1000" preserveAspectRatio="none" aria-hidden="true" focusable="false"><g filter="url(#A-grain)"><rect class="A-leather" width="720" height="1000"/><g filter="url(#A-recess)"><path class="A-onlay" d="M474.27,348.02A120,120 0 0 1 474.27,587.98A116,116 0 0 1 245.73,587.98A120,120 0 0 1 245.73,348.02A116,116 0 0 1 474.27,348.02Z"/></g><g filter="url(#A-recess)"><path class="A-labelskin" d="M192,768H528A12,12 0 0 0 540,780V828A12,12 0 0 0 528,840H192A12,12 0 0 0 180,828V780A12,12 0 0 0 192,768Z"/></g></g><rect width="720" height="1000" fill="url(#A-vig)"/><rect width="720" height="1000" fill="url(#A-sheen)"/><rect width="22" height="1000" fill="url(#A-hinge)"/><g filter="url(#A-gilt)"><rect width="720" height="1000" fill="url(#A-goldg)" mask="url(#A-goldmask)"/></g><g class="A-titleart" filter="url(#A-titlef)" fill="url(#A-titleg)" text-anchor="middle">'
    '<text class="A-t-the" x="358.42" y="COVER_Y1" font-size="COVER_S1">The</text>'
    '<text class="A-t-big" x="359.26" y="COVER_Y2" font-size="COVER_S2">END-OF-COURSE</text>'
    '<text class="A-t-big" x="359.33" y="COVER_Y3" font-size="COVER_S3">EXAM</text>'
    "</g></svg><h1 class='A-sr'>The End-of-Course Exam</h1><label for='nameIn' class='A-sr'>Your name</label><input id='nameIn' class='A-name' type='text' maxlength='40' autocomplete='off' spellcheck='false' placeholder='Type your name' value='{{NAMEVAL}}'><div class='shade'></div>"})

add({'cls': 'endpaper', 'label': 'Kept by', 'html':
    "<div class='panel'><svg viewBox='0 0 80 80' aria-hidden='true' style='width:10cqw;height:10cqw;margin:0 auto 1.2cqw;display:block'><circle class='draw' pathLength='1' cx='40' cy='40' r='34' fill='none' stroke='#9c3322' stroke-width='2.5'/><circle class='draw d2' pathLength='1' cx='40' cy='40' r='27' fill='none' stroke='#9c3322' stroke-width='1'/><text class='pop d3' x='40' y='48' text-anchor='middle' font-family='Fraunces,serif' font-weight='700' font-size='22' fill='#9c3322'>63</text></svg><div class='kept'>THIS BOOK BELONGS TO</div><div class='who' style='--nl:{{NLEN}}'>{{NAME}}</div><div class='meta'>{{META}}</div><div class='pick'><div class='drawers' role='group' aria-label='Your period'>{{DRAWERS}}</div></div>"
    "<div class='box'>How to read one argument closely in Part A and build your own in Part B, in two hours on Monday, May 10, 2027. Worried about exam day? Folio 8.</div>"
    "<p class='small' style='margin:0 0 1.4cqw;font-weight:700'>Identify. Explain. Evaluate. Then argue your own.</p><p class='small' style='margin:0'>Turn the page with the arrows, a tap on the page edge, or a drag of the corner.</p><p class='small' style='margin:1.4cqw 0 0'>Room 63 &middot; Mr. Portela &middot; AP Seminar &middot; 2026-27</p></div><div class='shade'></div>"})

def tocrow(n, bid, title, sub):
    return ("<li><button type='button' [[jump:%s]]><span class='rn'>%d</span><span class='tt'><span class='tl'>%s</span><span class='ld' aria-hidden='true'></span>"
            "<span class='pn'>[[pno:%s]]</span></span><span class='sb'>%s</span></button></li>") % (bid, n, tx(title), bid, tx(sub))

add(paper('contents', 'Contents', page(
    h2('Contents') + "<p class='small'>Tap a line to open that folio. New here? Start on page [[pj:start]].</p>"
    "<div class='R'><div class='card2 weak' style='margin-top:1cqw'><div class='k'>AP RESEARCH?</div><p>This book is for AP Seminar. AP Research has no end-of-course exam.</p></div></div>"
    "<div class='P'><p class='small'>This book is for AP Seminar, Periods 2, 5, 6, 7, and 8.</p></div>"
    "<div class='tochead'><span>FOLIO</span><span>PAGE</span></div><ul class='toc'>"
    + tocrow(1, 'b1', 'The exam at a glance', 'when, how, what it counts, getting on the list')
    + tocrow(2, 'b2', 'How readers score', 'seven rows, best fit, what scores 0')
    + tocrow(3, 'b3', 'Part A, short answers', 'identify, explain, evaluate')
    + tocrow(4, 'b4', 'Part B, your argument', 'theme, perspective, a worked set')
    + tocrow(5, 'b5', 'Part B, row by row', 'reasoning, sources, credit')
    + '</ul>')))

add(paper('contents2', 'Contents', page(
    h3('Contents, continued') + "<div class='tochead'><span>FOLIO</span><span>PAGE</span></div><ul class='toc'>"
    + tocrow(6, 'b6', 'Skills on the exam', 'argument, lens, perspective')
    + tocrow(7, 'b7', 'A year of practice', 'the plan, released exams, scoring')
    + tocrow(8, 'b8', 'Exam day', 'bring, the room, the clock, the rules')
    + tocrow(9, 'b9', 'Late testing and accommodations', 'another date, another way')
    + tocrow(10, 'b10', 'Scores in July', 'readers, your score, deadlines')
    + "</ul><div class='card2' style='margin-top:1.4cqw'><div class='k'>SIGNS IN THIS BOOK</div><div class='notes' style='margin-top:.6cqw'><div><svg class='ic sm' aria-hidden='true'><use href='#i-check'/></svg><p>strong, or allowed</p></div><div><svg class='ic sm' aria-hidden='true'><use href='#i-cross'/></svg><p>weak, or not allowed</p></div><div><span class='marks'><i class='y'></i><i></i></span><p>a check passes, or does not</p></div></div></div>"
    "<p class='small' style='margin-top:1cqw'>A dashed box: WAITING ON A ROOM 63 DECISION.</p>")))

def gorow(target, text):
    return "<button type='button' class='gorow' [[jump:%s]]><span>%s</span><span class='gpn'>[[pno:%s]]</span></button>" % (target, tx(text), target)

add(paper('start', 'Start here', page(
    h2('The exam in eight steps') + p('Do the steps in order. Tap a step to open its page.')
    + "<div class='tochead'><span>STEP</span><span>PAGE</span></div>"
    + gorow('f1-register', '1 Get on the list for the exam.')
    + gorow('f2-rows', '2 Learn the seven rows readers use.')
    + gorow('f3-glance', '3 Practice Part A: identify, explain, evaluate.')
    + gorow('f4-glance', '4 Practice Part B: find a theme, argue your view.')
    + gorow('f7-selfscore', '5 Score your practice like a reader.')
    + gorow('f7-classroom', '6 Try the Bluebook test preview.')
    + gorow('f8-bring', '7 Pack for May 10.')
    + gorow('f10-june', '8 Find your score in July.')
    + p('The examples in this book are made up. The exam brings its own sources.'))))

add(paper('find', 'Find it fast', page(
    h3('Find it fast') + p('Tap your problem. The page opens.')
    + "<div class='tochead'><span>I HAVE</span><span>PAGE</span></div>"
    + gorow('f1-glance', 'A question about the date or the time.')
    + gorow('f1-score', 'No idea how much the exam counts.')
    + gorow('f1-register', 'No exam ordered for me yet.')
    + gorow('f3-a2', 'A Part A answer that only lists claims.')
    + gorow('f3-a3', 'Evidence I do not know how to judge.')
    + gorow('f4-theme', 'Four sources and no idea what links them.')
    + gorow('f5-row3', 'An essay full of "Source A says."')
    + gorow('f7-selfscore', 'A practice answer to score.')
    + gorow('f8-bring', 'A bag to pack for May 10.')
    + gorow('f9-late', 'Two exams at the same time.')
    + gorow('f9-accom', 'A need for extra time.')
    + gorow('f10-june', 'A score that did not come.'))))

# ================================================================ FOLIO 1
add(board(1, 'The exam at a glance', 'i-cal',
    'Say when and how you test, what the exam counts, and how to get on the list.',
    [('The exam at a glance', 'f1-glance'), ('The exam in your AP score', 'f1-score'), ('Typed, in Bluebook', 'f1-bluebook'),
     ('Get on the list', 'f1-register'), ("The exam's dates", 'f1-dates')]))

add(paper('f1-glance', 'Folio 1', page(
    h2('The exam at a glance')
    + p('Two hours. Two parts. Five sources you have not seen.')
    + table('four tight', ['WHAT', 'THE FACT'], [
        ['When', 'Monday, May 10, 2027, at noon, local time. The start can be up to 1 hour later.'],
        ['How', 'Typed in the Bluebook app. Fully digital.'],
        ['Length', '2 hours, with no scheduled break.'],
        ['Part A', 'One source, three short answers, about 30 minutes.'],
        ['Part B', 'Four sources, one essay, about 90 minutes.'],
        ['Counts', '45 percent of your AP Seminar score.']])
    + p('College Board calls this slot Session 2. The four prompts are the same every year. ' + CK)
    + wait('Your room and your arrival time on May 10: from the AP coordinator, on Google Classroom.'), 1, 'i-cal')))

add(paper('f1-score', 'Folio 1', page(
    h3('The exam in your AP score')
    + table('wide2 tight', ['PART', 'SHARE'], [
        ['Team project', '20 percent: your report and the team talk.'],
        ['Individual project', '35 percent: your written argument, your own talk, and its questions.'],
        ['The exam', '45 percent: Part A 13.5, Part B 31.5.']])
    + p('Part A is 30 percent of the exam. Part B is 70 percent. All three parts make one AP score, from 1 to 5.')
    + card('weak', 'NO EXAM, NO SCORE', 'Submit both tasks and skip the exam, and you get no AP Seminar score.')
    + card('good', 'A TASK NOT DONE?', 'You may still take the exam.')
    + p('The same shares, drawn: The Research Log, page 71. ' + CK))))

add(paper('f1-bluebook', 'Folio 1', page(
    h3('Typed, in Bluebook')
    + p('The exam is fully digital, in the Bluebook app. When time ends, Bluebook submits your answers.')
    + p('You type every answer. Only typed answers earn points. Scratch paper is for notes and plans. Write complete sentences. An outline or a bulleted list is not accepted.')
    + p('AP Seminar is not a hybrid exam. You do not handwrite in a booklet. A paper version exists only when approved accommodations call for it (page [[pj:f9-accom]]).')
    + card('weak', 'NO CREDIT', 'Notes on scratch paper. Text typed as a Bluebook annotation.')
    + p('The 2025 and 2026 exams were typed in Bluebook. The 2024 Set 1 you can read was the paper version. On a tablet, an external keyboard is required (page [[pj:f8-before]]). ' + CK)
    + wait('The device you test on, a school device or your own: the AP coordinator decides.'))))

add(paper('f1-register', 'Folio 1', page(
    h3('Get on the list')
    + p('You get an AP Seminar score only if three things happen.')
    + table('narrow1 tight', ['STEP', 'WHAT'], [
        ['1', 'You are in an AP Seminar class section in My AP. You join it with my join code.'],
        ['2', 'An exam is ordered for you.'],
        ['3', 'You take the exam.']])
    + table('dates tight', ['WHEN', 'COLLEGE BOARD DEADLINE'], [
        ['October 2, 2026', 'Preferred deadline to order exams.'],
        ['November 13, 2026', 'Final deadline to order, 11:59 in the evening, Eastern Time.']], 'margin-top:1.4cqw')
    + p('The fee is $99. Ordered November 14 to March 12: $40 more. Dropped after November 13: $40. You pay through the school. ' + CK)
    + wait('The school&#39;s own sign-up and payment deadline, any fee above $99, and my join code: on Google Classroom.'.replace('&#39;', "'")))))

add(paper('f1-dates', 'Folio 1', page(
    h3("The exam's dates")
    + table('dates tight', ['WHEN', 'WHAT'], [
        ['November 13, 2026', 'Last day to order your exam.'],
        ['January 22, 2027', 'Last day for the SSD coordinator to ask for accommodations.'],
        ['April 30, 2027', 'Both tasks final, 11:59 in the evening, Eastern Time.'],
        ['May 10, 2027', 'The exam, at noon, local time.'],
        ['May 18, 2027', 'Late testing, 8 in the morning, local time.'],
        ['June 2027', 'Two score choices, June 15 and 20 (page [[pj:f10-choices]]).'],
        ['July 2027', 'Scores. No day is announced.']])
    + p('May 10 is also my deadline to enter presentation scores (The Team Project, page 8). Dates can move. The newest Google Classroom post wins. ' + CK)
    + wait('Practice exam dates: on Google Classroom.'))))

# ================================================================ FOLIO 2
add(board(2, 'How readers score', 'i-count',
    'Read the seven rows, and say how readers score and what scores 0.',
    [('Seven rows, 39 points', 'f2-rows'), ('How readers read', 'f2-read'), ('What scores 0', 'f2-zero')]))

def plate1():
    s = ''
    # left: Part A
    s += R(4, 4, 150, 18, DEEP, BRASS, 1.2) + T(79, 16.5, 'PART A · 15 POINTS', size=8, fill=GOLD, anchor='middle')
    rows_a = [('A1 · ROW 1', 'Understand and Analyze Argument', '0 TO 3'),
              ('A2 · ROW 2', 'Understand and Analyze Argument', '0, 2, 4, 6'),
              ('A3 · ROW 3', 'Evaluate Sources and Evidence', '0, 2, 4, 6')]
    for i, (a, b, c) in enumerate(rows_a):
        y = 27 + i * 40
        s += R(4, y, 150, 35, PAPER, NAVY, 1.1)
        s += T(9, y + 12.5, a, size=7.2) + T(149, y + 12.5, c, size=7.2, fill=RED, anchor='end')
        s += T(9, y + 27.5, b, font=SERIF, size=9, weight=600, fill=BROWN)
    # right: Part B
    s += R(166, 4, 150, 18, DEEP, BRASS, 1.2) + T(241, 16.5, 'PART B · 24 POINTS', size=8, fill=GOLD, anchor='middle')
    rows_b = [('ROW 1', 'Establish Argument'), ('ROW 2', 'Establish Argument'), ('ROW 3', 'Select and Use Evidence'), ('ROW 4', 'Apply Conventions')]
    for i, (a, b) in enumerate(rows_b):
        y = 27 + i * 30
        s += R(166, y, 150, 25.5, PAPER, NAVY, 1.1)
        s += T(171, y + 10, a, size=7.2) + T(311, y + 10, '0, 2, 4, 6', size=7.2, fill=RED, anchor='end')
        s += T(171, y + 21.5, b, font=SERIF, size=9.6, weight=600, fill=BROWN)
    # base band
    s += R(4, 150, 312, 22, CREAM, BRASS, 1.3)
    s += T(160, 165, '39 POINTS · PART A 30 PERCENT OF THE EXAM · PART B 70 PERCENT', size=7.1, fill=NAVY, anchor='middle')
    return s

add(paper('f2-rows', 'Folio 2', page(
    h2('Seven rows, 39 points')
    + p('College Board readers score the exam with seven rows. The rows were the same in 2024, 2025 and 2026.')
    + plate('I', 'The scoresheet', 176,
            'Two panels. Left, Part A, 15 points: A1 is Row 1, Understand and Analyze Argument, 0 to 3 points. A2 is Row 2, Understand and Analyze Argument, 0, 2, 4, or 6. A3 is Row 3, Evaluate Sources and Evidence, 0, 2, 4, or 6. Right, Part B, 24 points: Row 1 and Row 2, Establish Argument. Row 3, Select and Use Evidence. Row 4, Apply Conventions. Each 0, 2, 4, or 6. Below: 39 points. Part A is 30 percent of the exam, Part B 70 percent',
            plate1(), 'THE RULE', "Each Part B row is 6 of Part B's 24 points.")
    + p('College Board calls this the scoring guidelines. Read the ' + link('https://apcentral.collegeboard.org/media/pdf/ap26-sg-seminar-eoc.pdf', '2026 scoring guidelines') + ' on AP Central. ' + CK), 2, 'i-count')))

add(paper('f2-read', 'Folio 2', page(
    h3('How readers read')
    + p('Readers follow written rules. These are the ones that change how you write.')
    + table('rules tight', ['THE RULE', 'WHAT IT MEANS FOR YOU'], [
        ['Best fit', 'Readers pick the level your answer fits best. It is not a checklist.'],
        ['Each row alone', 'Every row is scored on its own.'],
        ['The whole essay', 'In Part B, readers read to the end before they score. An argument can emerge late. Still, start with your argument (page [[pj:f4-steps]]).'],
        ['Credit where it sits', 'In Part A, reasoning (A2) or evidence judged (A3) earns credit wherever you write it. This note is new in 2026. Keep your answers apart anyway: each prompt asks for something different.'],
        ['Who scores', 'College Board readers, not me.']])
    + p('College Board calls best fit the "preponderance of evidence." ' + CK))))

add(paper('f2-zero', 'Folio 2', page(
    h3('What scores 0')
    + card('weak', 'EVERY ROW 0, PART A AND PART B', 'An answer off the topic. A copy of the prompt. All of it crossed out. A drawing or other marks. An answer not in English.')
    + card('weak', 'ONE ROW 0, PART B', "A row scores 0 when the work is below that row's lowest level. One source, or none, scores 0 on Row 3.")
    + p('Learning English? The rows say it: "Grammar and syntax need not be perfect." Clear beats fancy.')
    + tryit('FIRST STEP', 'A practice essay uses only Source C. What does Row 3 score?', '0. Part B needs at least two of the sources.')
    + p(CK))))

# ================================================================ FOLIO 3
add(board(3, 'Part A, short answers', 'i-eye',
    'Identify an argument, explain its reasoning, and evaluate its evidence.',
    [('Part A at a glance', 'f3-glance'), ('A1: the argument', 'f3-a1'), ('A2: the line of reasoning', 'f3-a2'),
     ('A3: the evidence', 'f3-a3'), ('2025 samples, Part A', 'f3-samples')]))

add(paper('f3-glance', 'Folio 3', page(
    h2('Part A at a glance')
    + p('One source. Read it, then answer three prompts. The prompts never change.')
    + table('narrow1 tight', ['PROMPT', 'THE WORDS', 'POINTS'], [
        ['A1', '"Identify the author\'s argument, main idea, or thesis."', '3'],
        ['A2', '"Explain the author\'s line of reasoning by identifying the claims used to build the argument and the connections between them."', '6'],
        ['A3', '"Evaluate the effectiveness of the evidence the author uses to support the claims made in the argument."', '6']])
    + p('Watch the verbs: identify, explain, evaluate. Each asks for something different. About 30 minutes is the suggestion. Write complete sentences. ' + CK)
    + newword('LINE OF REASONING', 'l&iacute;nea de razonamiento', 'Claims and evidence in an order that leads to a conclusion.'), 3, 'i-eye')))

add(paper('f3-a1', 'Folio 3', page(
    h3('A1: the argument')
    + rowq(1, 'Understand and Analyze Argument', '0 to 3 points')
    + table('narrow1 tight', ['SCORE', 'LOOKS LIKE'], [
        ['1', 'Misstates it, names only the topic, or repeats the title.'],
        ['2', 'Names it in part, with some accuracy.'],
        ['3', 'Names all its main parts, and shows the argument as a whole.']])
    + p('Readers saw: part of the argument, a claim taken for the argument, or the title.')
    + card('weak', 'WEAK, A MADE-UP CASE', '"The author writes about school start times."', '.8cqw')
    + card('good', 'STRONG, A MADE-UP CASE', '"The author argues that later start times help teens sleep, that the gain is worth the bus costs, and that districts should act now."', '.8cqw')
    + p('A claim, not a topic: The Research Log, page 24. ' + CK))))

def plate2():
    s = ''
    claims = ['Teen body clocks run late.', 'Early starts cut sleep.', 'Buses cost more to move.']
    seq = ['first', 'then', 'finally']
    # left panel: a list
    s += T(84, 11, 'A LIST', size=8.4, fill=RED, anchor='middle')
    for i, c in enumerate(claims):
        y = 20 + i * 34
        s += R(40, y, 112, 22, PAPER, RED, 1.2)
        s += T(96, y + 14.5, c, font=SERIF, size=9.6, weight=600, fill=INK, anchor='middle')
        s += T(35, y + 15, seq[i], font=HAND, size=11.5, weight=400, fill=RED, anchor='end')
    s += T(96, 148, 'no links: stops at 2', font=HAND, size=12, weight=400, fill=RED, anchor='middle')
    s += L(162, 4, 162, 152, '#b9ad94', 1)
    # right panel: a line
    s += T(226, 11, 'A LINE', size=8.4, fill=PINE, anchor='middle')
    for i, c in enumerate(claims):
        y = 20 + i * 34
        s += R(170, y, 112, 22, PAPER, PINE, 1.2)
        s += T(226, y + 14.5, c, font=SERIF, size=9.6, weight=600, fill=INK, anchor='middle')
    s += A(226, 42, 226, 53.5, PINE) + T(232, 51, 'so', font=HAND, size=12, weight=400, fill=PINE)
    s += A(226, 76, 226, 87.5, PINE) + T(232, 85, 'but', font=HAND, size=12, weight=400, fill=PINE)
    s += "<path d='M284 31 L298 31 L298 99 L284 99' fill='none' stroke='%s' stroke-width='1.3'/>" % PINE
    s += L(284, 65, 298, 65, PINE, 1.3)
    s += A(298, 99, 298, 113.5, PINE)
    s += R(186, 115, 128, 20, DEEP, BRASS, 1.4)
    s += T(250, 128.5, 'THE ARGUMENT', size=8, fill=GOLD, anchor='middle')
    s += T(250, 148, 'can reach 6', font=HAND, size=12, weight=400, fill=PINE, anchor='middle')
    return s

add(paper('f3-a2', 'Folio 3', page(
    h3('A2: the line of reasoning')
    + rowq(2, 'Understand and Analyze Argument', '0, 2, 4, or 6 points')
    + plate('II', 'A list, or a line', 154,
            'Left, a list: three made-up claims in boxes, marked first, then, finally, with no links. It stops at 2. Right, a line: the same three claims joined. Teen body clocks run late, so early starts cut sleep, but buses cost more to move. A bracket ties all three to the argument. It can reach 6',
            plate2(), 'A MADE-UP CASE', 'Readers saw "first, then, finally" in place of real links. Link words explain how the claims connect.')
    + p('2: names at least one claim. 4: some claims, and a link between them. 6: the relevant claims, with the links clearly explained.')
    + p("A source's reasoning: The Team Project, page 21. " + CK))))

add(paper('f3-a3', 'Folio 3', page(
    h3('A3: the evidence')
    + rowq(3, 'Evaluate Sources and Evidence', '0, 2, 4, or 6 points')
    + p("At the top, you judge how relevant and credible the evidence is, and how well it holds up the author's argument.")
    + p('Readers advise: judge at least two separate pieces of evidence. Talk about the source and the specific evidence.')
    + card('weak', 'ONLY THE SOURCES', 'Judge only where the evidence came from, never a specific piece, and Row 3 cannot reach 6.')
    + tryit('NEXT STEP', 'An answer says, "The author uses credible sources." Nothing more. What happens?',
            'It stays low. It names no evidence and explains nothing. A 2025 sample judged evidence without naming any, and scored 2 (page [[pj:f3-samples]]).')
    + p('One number, four questions: The Research Manual, page 42. ' + CK))))

add(paper('f3-samples', 'Folio 3', page(
    h3('2025 samples, Part A')
    + p('Three real answers from the 2025 exam, Set 1. The scores are for Rows 1, 2 and 3.')
    + table('rules tight', ['SAMPLE', 'WHY'], [
        ['A · 3, 6, 6', 'All three parts of the argument named. Top scores on Rows 2 and 3.'],
        ['B · 2, 4, 4', 'Two of three parts named. "The author\'s first claim" and "then goes on to talk about" showed a limited grasp of the reasoning. Evidence judged unevenly: "they are both from credible sources."'],
        ['C · 1, 2, 2', 'The title restated. A list of claims. Evidence judged, but none of it named.']])
    + p('The average that year: 10.19 of 15 points. Row 1 averaged 1.99 of 3.')
    + p('Read all three with the readers&#39; notes: '.replace('&#39;', "'") + link('https://apcentral.collegeboard.org/media/pdf/ap25-apc-seminar-eoc-a-set-1.pdf', '2025 Part A samples') + ', on AP Central. ' + CK))))

# ================================================================ FOLIO 4
add(board(4, 'Part B, your argument', 'i-compass',
    'Find the theme that links four sources, and argue a view of your own.',
    [('Part B at a glance', 'f4-glance'), ('Read, plan, then write', 'f4-steps'), ('From a theme to your perspective', 'f4-theme'),
     ('One made-up set, worked', 'f4-set')]))

add(paper('f4-glance', 'Folio 4', page(
    h2('Part B at a glance')
    + p('Four sources. No question to write. Find a theme or issue that links them, and argue your own view on it.')
    + table('rules tight', ['WHAT', 'THE FACT'], [
        ['Sources', 'Four, each a different perspective on one theme.'],
        ['You must use', 'At least two. You may use the others, or what you know.'],
        ['Time', 'About 90 minutes.'],
        ['Points', '24, in four rows.'],
        ['Share', '31.5 percent of your AP score.'],
        ['The prompt', 'The same every year.']])
    + card('', 'ON THE EXAM', 'Call a source Source A, or use its author&#39;s name (The Research Manual, page 67).'.replace('&#39;', "'"))
    + p(CK), 4, 'i-compass')))

add(paper('f4-steps', 'Folio 4', page(
    h3('Read, plan, then write')
    + p('Readers name three steps for Part B.')
    + table('narrow1 tight', ['STEP', 'DO THIS'], [
        ['1', 'Read and think. Mark up each source. Note its perspective: a view and its reason (The Research Log, page 36). Bluebook highlights and notes are not your answer.'],
        ['2', 'Plan and outline. On scratch paper: the theme, your view, two or three claims, and the sources for each.'],
        ['3', 'Write. Begin with your argument, not a long talk about the theme. Then proofread.']])
    + card('weak', 'DOES NOT SCORE WELL', 'A summary of two sources, then a line or two of your view at the end.')
    + tryit('NEXT STEP', 'Your first paragraph spends six sentences on what "power" means. What do readers advise?',
            'Start with your argument, not a long talk about the theme.')
    + p(CK))))

add(paper('f4-theme', 'Folio 4', page(
    h3('From a theme to your perspective')
    + rowq(1, 'Establish Argument', '0, 2, 4, or 6 points')
    + p('A perspective is "a point of view conveyed through an argument." A topic is what a source is about. A theme is an idea the sources share.')
    + table('narrow1 tight', ['SCORE', 'LOOKS LIKE'], [
        ['2', 'Misses the theme. Your view is unclear or unrelated, or the essay is mostly summary.'],
        ['4', 'Names a theme, but your view comes from only one source, or it is trite, obvious, or too general.'],
        ['6', 'A theme that links the sources, and a view no single source holds, a sharp take on one of their views, or a strong link among them.']])
    + p('Readers saw the best essays build "an argument that connected the sources but occurred in none of them." ' + CK))))

def plate3():
    s = ''
    s += "<ellipse cx='160' cy='56' rx='58' ry='21' fill='%s' stroke='%s' stroke-width='2'/>" % (DEEP, BRASS)
    s += T(160, 51, 'THEME', size=7.4, fill=GOLD, anchor='middle')
    s += T(160, 65, 'who a school day is for', font=SERIF, size=10, weight=600, fill='#f3e3bd', anchor='middle')
    cards = [(6, 4, 'A · A POEM', 'an alarm before dawn'), (210, 4, 'B · A STUDY', 'teen sleep diaries'),
             (6, 84, 'C · A REPORT', 'the cost of buses'), (210, 84, 'D · AN OP-ED', 'a coach on practice')]
    for x, y, a, b in cards:
        s += R(x, y, 104, 34, PAPER, NAVY, 1.4)
        s += T(x + 6, y + 12, a, size=6.8)
        s += T(x + 6, y + 27, b, font=SERIF, size=9, weight=600, fill=BROWN)
    s += A(110, 26, 117, 42) + A(210, 26, 203, 42) + A(110, 98, 116, 70) + A(210, 98, 204, 70)
    s += A(160, 78, 160, 91, PINE)
    s += R(122, 93, 76, 18, PAPER, PINE, 1.6)
    s += T(160, 105.5, 'YOUR VIEW', size=7.4, fill=PINE, anchor='middle')
    s += T(160, 125, 'in none of the four', font=HAND, size=11.5, weight=400, fill=PINE, anchor='middle')
    return s

add(paper('f4-set', 'Folio 4', page(
    h3('One made-up set, worked')
    + plate('III', 'Four sources, one view', 130,
            'A made-up set of four sources around one theme. A, a poem about an alarm before dawn. B, a study of teen sleep diaries. C, a report on the cost of buses. D, an op-ed by a coach on practice times. The theme in the center: who a school day is for. Below it, your view, found in none of the four',
            plate3(), 'A MADE-UP SET', 'Four views on one theme. Yours links them, and is none of them.')
    + card('good', 'STRONG, A MADE-UP CASE', '"A school schedule decides whose time counts. Students lose the most hours, so students should help set it."', '.8cqw')
    + p('Weak: "Sleep is important for teenagers." Trite and obvious. Source A is a poem: use it for its view, not as data. Past themes: power, work, home (page [[pj:f7-released]]). ' + CK))))

# ================================================================ FOLIO 5
add(board(5, 'Part B, row by row', 'i-pen',
    'Build your reasoning, put sources in conversation, and credit every idea.',
    [('Row 2: your reasoning', 'f5-row2'), ('Row 3: sources in conversation', 'f5-row3'),
     ('Row 4: clear writing and credit', 'f5-row4'), ('2025 samples, Part B', 'f5-samples')]))

add(paper('f5-row2', 'Folio 5', page(
    h2('Row 2: your reasoning')
    + rowq(2, 'Establish Argument', '0, 2, 4, or 6 points')
    + p('Commentary is "a discussion and analysis of evidence in relation to the claim." Interpret. Do not summarize.')
    + table('narrow1 tight', ['SCORE', 'LOOKS LIKE'], [
        ['2', 'Disorganized, or no commentary.'],
        ['4', 'Mostly clear, but the logic or the order slips.'],
        ['6', 'Points in an order you chose. Commentary ties evidence to claims convincingly.']])
    + tryit('FIRST STEP', 'Made-up. Which is commentary? A: "Source B says teens sleep seven hours. So sleep matters." B: "Source B shows bus riders lose the most sleep. So the schedule is not neutral."',
            'B. It interprets. A only repeats.')
    + p('Why evidence supports a claim: Writing the Paper, page 11. ' + CK), 5, 'i-pen')))

add(paper('f5-row3', 'Folio 5', page(
    h3('Row 3: sources in conversation')
    + rowq(3, 'Select and Use Evidence', '0, 2, 4, or 6 points')
    + table('narrow1 tight', ['SCORE', 'LOOKS LIKE'], [
        ['0', 'One source, or none.'],
        ['2', 'Repeats or misreads two sources, or the information does not fit.'],
        ['4', 'Relevant information from at least two sources, used accurately.'],
        ['6', 'Relevant information from at least two sources, synthesized into a compelling argument.']])
    + p('At the top, the sources talk to each other. "The evidence is not the argument itself." Signal words help: agrees, contradicts, qualifies, extends.')
    + card('weak', 'READERS SAW', 'All four sources forced in. Paragraphs that open "Source X says," then summarize. Quotes dropped in.')
    + p('In both 2025 sets, this row had the lowest Part B average. ' + CK))))

add(paper('f5-row4', 'Folio 5', page(
    h3('Row 4: clear writing and credit')
    + rowq(4, 'Apply Conventions', '0, 2, 4, or 6 points')
    + table('narrow1 tight', ['SCORE', 'LOOKS LIKE'], [
        ['2', "Many flaws in the reader's way, or wrong credit. A paraphrase with no credit, or no quotation marks, lands here."],
        ['4', 'Generally clear. Credit is accurate.'],
        ['6', 'Clear to the reader. Source material is introduced, worked in, and credited.']])
    + p('"Grammar and syntax need not be perfect." To credit, name Source A to D, or the author.')
    + card('weak', 'WEAK, A MADE-UP CASE', 'A dropped quote: "Teens need sleep." Schools should start later.', '.8cqw')
    + card('good', 'STRONG, A MADE-UP CASE', 'The sleep study (Source B) found that bus riders "lost the most sleep of any group."', '.8cqw')
    + p('Quote, paraphrase, or summary: The Research Manual, page 52. ' + CK))))

add(paper('f5-samples', 'Folio 5', page(
    h3('2025 samples, Part B')
    + p('Real essays, 2025 exam, Set 1. Scores for Rows 1 to 4.')
    + table('rules tight', ['SAMPLE', 'WHY'], [
        ['A · 6, 6, 6, 6', 'An original view built from Sources A and D. A counterargument. Sources worked in and credited.'],
        ['B · 4, 4, 4, 4', 'A view that was "overly general." Reasoning organized enough to follow. Sources used one at a time, never in conversation. Credit accurate, but the evidence had no context.'],
        ['C · 2, 2, 2, 2', 'Summary with no argument. Sources misread. Grammar in the way.']])
    + p('The average that year: 16.67 of 24 points.')
    + tryit('GOING FURTHER', 'Sample B used each source alone. What one move lifts Row 3?', 'Put two sources in one paragraph, and say how they agree or differ.')
    + p('Read all three with the readers&#39; notes: '.replace('&#39;', "'") + link('https://apcentral.collegeboard.org/media/pdf/ap25-apc-seminar-eoc-b-set-1.pdf', '2025 Part B samples') + ', on AP Central. ' + CK))))

# ================================================================ FOLIO 6
add(board(6, 'Skills on the exam', 'i-link',
    'Find where the skills of your year turn up on the exam.',
    [('Five skills, seven rows', 'f6-map'), ('The argument, read and built', 'f6-argument'),
     ('Lens and perspective on the exam', 'f6-lens'), ('Your tasks train the exam', 'f6-tasks')]))

add(paper('f6-map', 'Folio 6', page(
    h2('Five skills, seven rows')
    + p('Every exam row is named after a course skill. Five skills do all the scoring.')
    + table('wide1 tight', ['SKILL', 'ON THE EXAM'], [
        ['Understand and Analyze Argument', 'Part A, A1 and A2'],
        ['Evaluate Sources and Evidence', 'Part A, A3'],
        ['Establish Argument', 'Part B, Rows 1 and 2'],
        ['Select and Use Evidence', 'Part B, Row 3'],
        ['Apply Conventions', 'Part B, Row 4']])
    + p('Five course skills are not exam rows: context, perspective, engaging an audience, working in a team, and reflecting. The tasks score those.')
    + p('Perspective is not a row name. Part B still asks for yours (Row 1, page [[pj:f4-theme]]).')
    + p('Skill names: the course and exam description, page 9. ' + CK), 6, 'i-link')))

add(paper('f6-argument', 'Folio 6', page(
    h3('The argument, read and built')
    + p("Part A reads someone else's argument. Part B builds yours. The moves match.")
    + table('half tight', ['PART A: THEIR ARGUMENT', 'PART B: YOUR ARGUMENT'], [
        ['A1 Name it.', 'Row 1 Your perspective.'],
        ['A2 Explain its line of reasoning.', 'Row 2 Your line of reasoning.'],
        ['A3 Judge its evidence.', 'Row 3 Use your evidence well.']])
    + p('The course defines an argument as "A claim or thesis that conveys a perspective developed through a line of reasoning and supported by evidence." A claim is "A statement made about an issue that asserts a perspective."')
    + p('The course also says other sources should not stand in for your own thinking. Add to them. Do not only repeat them.')
    + p('A claim someone could dispute: Writing the Paper, page 10. ' + CK))))

add(paper('f6-lens', 'Folio 6', page(
    h3('Lens and perspective on the exam')
    + p('The exam never says lens. It asks for a theme or issue, and a perspective.')
    + p('Readers keep the two apart. A lens is "a filter through which a topic can be viewed." A perspective is "a point of view conveyed through a source\'s argument."')
    + table('half tight', ['LENS', 'PERSPECTIVE'], [
        ['A filter, like economic or ethical.', 'A view, with its reason.'],
        ['Not a side.', 'A side on the issue.']])
    + p('Each Part B source has its own perspective. Row 1 rewards yours.')
    + card('good', 'A ROOM 63 HABIT', 'Stuck on what links four sources? Try two lenses. Economic: who pays? Ethical: what is fair? The link is often there. This is my advice, not a College Board rule.')
    + p('The eight lenses: The Field Guide, page 12. ' + CK))))

add(paper('f6-tasks', 'Folio 6', page(
    h3('Your tasks train the exam')
    + table('wide2 tight', ['YOUR PAPER', 'ITS ROWS THAT MATCH THE EXAM'], [
        ['Your report', '"Understand and Analyze Argument" and "Evaluate Sources and Evidence": the Part A rows.'],
        ['Your written argument', '"Establish Argument," "Select and Use Evidence," and "Apply Conventions": the Part B rows.']])
    + p('Every source you explain for your report is Part A practice. Every paragraph of your written argument is Part B practice.')
    + card('weak', 'YOUR OWN AGENDA', 'Readers warn: do not bring your report or written argument topic into Part B and force the sources to fit. Argue from the four you are given.')
    + p("Your report's rows: The Team Project, Folio 5. Your written argument: The Individual Project, Folio 6. " + CK))))

# ================================================================ FOLIO 7
add(board(7, 'A year of practice', 'i-steps',
    'Plan practice that fits both tasks, with released exams and the real rows.',
    [('The year, drawn', 'f7-year'), ('Practice exam, real exam', 'f7-runs'), ('Released exams to practice with', 'f7-released'),
     ('AP Classroom and Bluebook', 'f7-classroom'), ('Score a practice answer', 'f7-selfscore')]))

def plate4():
    x0, mw, ay = 10, 30, 72
    X = lambda m, d, days: x0 + mw * m + mw * d / days
    s = ''
    # College Board dates in three label rows, placed so no stem crosses a label
    top = [  # (x, row, anchor, label x, date, words)
        (X(2, 13, 30), 0, 'middle', None, 'NOV 13', 'last day to order'),
        (X(5, 28, 28), 0, 'middle', None, 'FEB 28', 'team project done'),
        (X(4, 22, 31), 1, 'middle', None, 'JAN 22', 'accommodations'),
        (X(7, 30, 30), 1, 'middle', None, 'APR 30', 'tasks final'),
        (X(4, 3, 31), 2, 'end', 138, 'JAN', 'the packet'),
        (X(8, 10, 31), 2, 'start', 255, 'MAY 10', 'the exam'),
    ]
    for x, row, anc, lx, d, w in top:
        y1 = 10 + row * 20
        lx = x if lx is None else lx
        col = RED if d == 'MAY 10' else NAVY
        s += T(round(lx, 1), y1, d, size=7.2, fill=col, anchor=anc)
        s += T(round(lx, 1), y1 + 9.5, w, font=HAND, size=10.5, weight=400, fill=BROWN if col == NAVY else RED, anchor=anc)
        s += L(round(x, 1), y1 + 12.5, round(x, 1), ay - 3, col, 0.9)
        s += "<circle cx='%.1f' cy='%s' r='2.8' fill='%s'/>" % (x, ay, col)
    s += L(x0, ay, x0 + mw * 9, ay, NAVY, 1.4)
    for i, m in enumerate(['SEP', 'OCT', 'NOV', 'DEC', 'JAN', 'FEB', 'MAR', 'APR', 'MAY']):
        s += L(x0 + mw * i, ay - 2.5, x0 + mw * i, ay + 2.5, NAVY, 1)
        s += T(x0 + mw * i + 15, ay + 11, m, size=6.8, weight=700, fill=NAVY, anchor='middle')
    s += L(x0 + mw * 9, ay - 2.5, x0 + mw * 9, ay + 2.5, NAVY, 1)
    bands = [(X(1, 18, 31), X(4, 29, 31), 'TEAM PROJECT', 'Part A skills'),
             (X(5, 1, 28), X(7, 15, 30), 'OWN PROJECT', 'Part B skills'),
             (X(7, 30, 30) + 3, 316, 'AFTER APR 30', 'timed practice')]
    for a, b, t1, t2 in bands:
        s += R(round(a, 1), 89, round(b - a, 1), 28, '#f0dfb4', '#8a6a2e', 1.1, rx=4)
        s += T(round((a + b) / 2, 1), 100, t1, size=7, fill='#6d4a14', anchor='middle')
        s += T(round((a + b) / 2, 1), 112.5, t2, font=HAND, size=10.5, weight=400, fill=RED, anchor='middle')
    s += T(4, 130, 'TOP: COLLEGE BOARD DATES', size=6.6, weight=700, fill=NAVY)
    s += T(316, 130, 'BOTTOM: A ROOM 63 PLAN', size=6.6, weight=700, fill='#6d4a14', anchor='end')
    return s

add(paper('f7-year', 'Folio 7', page(
    h2('The year, drawn')
    + plate('IV', 'Practice through the year', 134,
            'A timeline from September to May. Top, College Board dates: November 13, last day to order the exam. January, the packet goes to teachers. January 22, accommodations requests. February 28, the team project, suggested finish. April 30, both tasks final. May 10, the exam. Bottom, a Room 63 plan with no dates: during the team project, Part A skills. During your own project, Part B skills. After April 30, timed practice',
            plate4(), 'WHY THIS ORDER', 'Your report uses the Part A rows. Your written argument uses the Part B rows (page [[pj:f6-tasks]]). ' + CK)
    + wait('Team project dates: The Team Project, page 6. Own talk dates: Presenting and Defending, page 43. Practice exam dates, and which released sets we use: on Google Classroom.'), 7, 'i-steps')))

add(paper('f7-runs', 'Folio 7', page(
    h3('Practice exam, real exam')
    + table('runs tight', ['', 'PRACTICE', 'THE REAL EXAM'], [
        ['Who scores', 'I do, with the College Board rows.', 'College Board readers, not me.'],
        ['My help', 'I read your answers and show fixes.', 'None. The two hours are yours.'],
        ['Where', 'Room 63.', 'Bluebook, Monday, May 10, 2027.'],
        ['The clock', 'I time it: 30, 90, or 120 minutes.', '2 hours. Red when 5 minutes remain.']])
    + p('Released questions are public. Practice with them as often as you like. The real sources are new. The four prompts are not (page [[pj:f3-glance]]). ' + CK)
    + wait('Whether practice counts in our gradebook, and whether we practice on paper or on a device: on Google Classroom.'))))

add(paper('f7-released', 'Folio 7', page(
    h3('Released exams to practice with')
    + table('four tight', ['YEAR', 'PART A SOURCE', 'PART B'], [
        ['2026', 'A Nature editorial, "More-Powerful AI Is Coming"', 'Frost, Agarwal, the OECD, Barbara Bush'],
        ['2025, Set 1', 'Abrams, on paid parental leave', 'on power'],
        ['2025, Set 2', 'Milman, The Guardian', 'on work'],
        ['2024, Set 1', 'Malone, "Go Ahead, Laugh!"', 'King, a study of college goals, Clifford, Smil'],
        ['2024, Set 2', 'Tubb, Heritage Foundation', 'on home']])
    + p('2026 has the questions and scoring guidelines only. No samples yet. Some Part B sources are not online, so a set may give you three to read. The 2024 Set 1 you can read was the paper version.')
    + p('Every set: ' + link('https://apcentral.collegeboard.org/courses/ap-seminar/exam/past-exam-questions', 'past exam questions') + ', on AP Central. ' + CK))))

add(paper('f7-classroom', 'Folio 7', page(
    h3('AP Classroom and Bluebook')
    + table('rules tight', ['TOOL', 'WHAT IT GIVES'], [
        ['AP Classroom', 'The Question Bank, which I may assign, and AP Daily videos on course skills. Full practice is here, not in Bluebook.'],
        ['Test preview', 'In Bluebook: short and untimed, with no score. Try every tool. Try one this fall and again in April.'],
        ['AP Central', 'Real questions, scoring guidelines, and sample answers.'],
        ['A video', 'From College Board: <a href="https://apstudents.collegeboard.org/ap-exams-what-to-know/digital-testing-exam-modes" target="_blank" rel="noopener">2027 AP Exams: Introduction to Fully Digital AP Exam Testing</a>, 11 minutes.']])
    + p('The preview on a Room 63 iPad: not yet checked. ' + CK)
    + wait('Which AP Daily videos I assign, and when: on Google Classroom.'))))

add(paper('f7-selfscore', 'Folio 7', page(
    h3('Score a practice answer')
    + form('exscore', 'MY PRACTICE', [
        ('PART A', ['A1 names every main part, not the topic.', 'A2 links claims with because, so, or but.', 'A3 judges two pieces of evidence and their source.']),
        ('PART B', ['My view is in none of the sources.', 'Two sources talk in one paragraph.', 'Every quote names its source.']),
        ('GOING FURTHER', ["I marked each row's move in my answer."])])
    + p('Then compare a real sample (pages [[pj:f3-samples]] and [[pj:f5-samples]]). ' + CK))))

# ================================================================ FOLIO 8
add(board(8, 'Exam day', 'i-clock',
    'Arrive ready, bring only what is allowed, and use all two hours.',
    [('Before the day', 'f8-before'), ('Bring it, leave it', 'f8-bring'), ('In the room', 'f8-room'),
     ('The two hours', 'f8-clock'), ('Rules that cancel a score', 'f8-rules')]))

add(paper('f8-before', 'Folio 8', page(
    h2('Before the day')
    + form('exsetup', 'MY SETUP', [('READY', [
        'I know my College Board login by heart.',
        'I asked when Bluebook goes on my device.',
        'I found my exam under Your Tests.',
        'My device holds a 4-hour charge.',
        'On a tablet, I have an external keyboard.',
        'I tried a test preview.'])])
    + p('A saved password will not work. There may be no outlet. ' + CK)
    + wait('Your room, arrival time, seat, and device: from the AP coordinator, on Google Classroom.'), 8, 'i-clock')))

add(paper('f8-bring', 'Folio 8', page(
    h3('Bring it, leave it')
    + table('half tight', ['BRING', 'LEAVE AT HOME'], [
        ['A watch that is not a smartwatch.', 'Phones, smartwatches, anything you wear that connects.'],
        ['Pencils or pens, black or dark blue ink, for notes.', 'Timers, and watches that beep.'],
        ['A charged device and its cord, if the school does not give you one.', 'A stylus or Apple Pencil. Highlighters. Mechanical or colored pencils.'],
        ['A photo ID, only if you test away from your school.', 'Notes, books, dictionaries, your own scratch paper, food or drink.']])
    + p('On a laptop, no external keyboard. A mouse is fine. A power bank sits on your desk, never shared. Hats come off. A head covering for religious or medical reasons stays.')
    + card('weak', 'ONE BANNED ITEM', 'A banned item can end your exam and cancel your score.')
    + p(CK))))

add(paper('f8-room', 'Folio 8', page(
    h3('In the room')
    + table('narrow1 tight', ['STEP', 'WHAT HAPPENS'], [
        ['1', 'Connect to school Wi-Fi, sign in to Bluebook, and do a short check-in.'],
        ['2', 'The proctor reads instructions, collects banned items, and gives a start code. Enter it only when told.'],
        ['3', 'The school hands out scratch paper. It is collected at the end.'],
        ['4', 'Use the tools: highlights and notes, line reader, mark for review, question menu, zoom.'],
        ['5', 'At the end, Bluebook submits your answers. Keep your device open until the proctor dismisses you.']])
    + p('Submission failed? Follow the app, then raise your hand. Offline at the end? Reconnect and follow the app. A started exam is scored.')
    + p('Something wrong, like wrong directions? Tell the AP coordinator right away. From the 2026 rules. ' + CK))))

def plate5():
    x0, x1, y, h = 20, 300, 44, 26
    k = (x1 - x0) / 120.0
    s = ''
    s += A(90, 16, 230, 16, NAVY, 1.2, both=True)
    s += T(160, 11, 'move between parts any time', font=HAND, size=11, weight=400, fill=NAVY, anchor='middle')
    s += R(x0, y, 30 * k, h, '#e6ecf2', NAVY, 1.2, rx=0)
    s += R(x0 + 30 * k, y, 85 * k, h, PAPER, NAVY, 1.2, rx=0)
    s += R(round(x0 + 115 * k, 1), y, round(5 * k, 1), h, RED, NAVY, 1.2, rx=0)
    s += T(round(x0 + 15 * k, 1), y + 11, 'PART A', size=7.8, anchor='middle') + T(round(x0 + 15 * k, 1), y + 22, 'about 30', font=HAND, size=11, weight=400, fill=RED, anchor='middle')
    s += T(round(x0 + 72 * k, 1), y + 11, 'PART B', size=7.8, anchor='middle') + T(round(x0 + 72 * k, 1), y + 22, 'about 90', font=HAND, size=11, weight=400, fill=RED, anchor='middle')
    s += L(round(x0 + 30 * k, 1), y - 8, round(x0 + 30 * k, 1), y + h + 4, RED, 1.2, '3 2')
    s += T(round(x0 + 30 * k + 3, 1), y - 3, 'suggested', font=HAND, size=10, weight=400, fill=RED)
    for m in (0, 30, 60, 90, 120):
        xx = round(x0 + m * k, 1)
        s += L(xx, y + h, xx, y + h + 5, NAVY, 1)
        s += T(xx, y + h + 14, ('%d MIN' % m) if m == 120 else str(m), size=7.4, anchor='end' if m == 120 else 'middle')
    s += A(262, 100, round(x0 + 117.5 * k, 1), y + h + 16, RED, 1.2)
    s += T(258, 104, 'red at 5 minutes left', font=HAND, size=11, weight=400, fill=RED, anchor='end')
    s += T(x0, 104, 'NO SCHEDULED BREAK', size=7.4, fill=NAVY)
    return s

add(paper('f8-clock', 'Folio 8', page(
    h3('The two hours')
    + plate('V', 'Two parts, 120 minutes', 110,
            'One bar from 0 to 120 minutes. Part A on the left, about 30 minutes, then a dashed line marked suggested. Part B, about 90 minutes. The last 5 minutes are red. A two-way arrow above: move between parts any time. Below: no scheduled break',
            plate5(), 'A PLAN', 'A plan for your minutes, not a picture of the Bluebook screen.')
    + p('You have 2 hours. About 30 minutes for Part A and 90 for Part B is the suggestion. You can move between them.')
    + p('The clock turns red when 5 minutes remain. The proctor gives no warnings. You may hide the timer until then. When time runs out, you cannot keep working.')
    + p('Released papers print "30 minutes" over Part A. The directions call it approximate. From the 2026 directions. ' + CK))))

add(paper('f8-rules', 'Folio 8', page(
    h3('Rules that cancel a score')
    + table('rules tight', ['WHAT', 'THE RULE'], [
        ['Other apps', 'None. No pasting from another program.'],
        ['Tools that write', 'None, and no websites. Every word is yours. College Board checks for tool writing and copying.'],
        ['Quotes', 'Type the words, in quotation marks.'],
        ['Breaks', 'No phone or notes in any break. Do not leave the building.'],
        ['Social media', 'A post during the exam cancels the score. A ban from AP, SAT and CLEP testing is possible.'],
        ['Afterward', 'Share no question until College Board posts it. Late-testing questions, never.']])
    + p('Tools on the tasks: The AI Manual, Folio 2. On the exam: none.')
    + p('These are the 2026 rules. College Board posts the 2027 rules in spring and emails you. ' + CK))))

# ================================================================ FOLIO 9
add(board(9, 'Late testing and accommodations', 'i-history',
    'Know what to do if you cannot test on May 10, or need to test another way.',
    [('Late testing', 'f9-late'), ('Accommodations', 'f9-accom'), ('Sick, stuck, or missing a piece', 'f9-stuck')]))

add(paper('f9-late', 'Folio 9', page(
    h2('Late testing')
    + table('rules tight', ['WHAT', 'THE FACT'], [
        ['When', 'Tuesday, May 18, 2027, 8 in the morning, local time. Late testing runs May 17 to 21.'],
        ['Why', 'Something unexpected on exam day, or two exams at the same time.'],
        ['Same slot', 'Music Theory. You may still sign up for both.'],
        ['How', 'A different version of the exam, arranged by the AP coordinator.'],
        ['Cost', 'Most reasons, nothing extra. Some cost $40. Scores may come later.']])
    + p('Extended time, and two exams on May 10, like Calculus and Seminar? Plan to take one late. No early testing. No other times. ' + CK)
    + wait('Who tests late, and by when you must tell us: the AP coordinator decides. Tell me as soon as you know.'), 9, 'i-history')))

add(paper('f9-accom', 'Folio 9', page(
    h3('Accommodations')
    + p('A student with a documented disability may get accommodations on the tasks and the exam, like extended time or a reader.')
    + table('rules tight', ['THE RULE', 'WHAT IT MEANS'], [
        ['Ahead of time', "College Board approves first. You or the school's SSD coordinator asks."],
        ['The deadline', 'January 22, 2027, for the SSD coordinator.'],
        ['Breaks', 'Extended time brings no extra breaks. Ask for breaks on their own.'],
        ['On the day', 'Bring your SSD Decision Letter. Help not approved cancels the score.'],
        ['Paper', 'Only if your approved accommodations call for it.']])
    + p(link('https://apstudents.collegeboard.org/request-exam-accommodations', 'How to ask') + ', College Board. ' + CK)
    + wait("Who the school's SSD coordinator is, and the school's own date to ask: on Google Classroom."))))

add(paper('f9-stuck', 'Folio 9', page(
    h3('Sick, stuck, or missing a piece')
    + table('rules tight', ['IF', 'THEN'], [
        ['Sick on May 10', 'Tell the AP coordinator. Late testing is for the unexpected.'],
        ['A task not finished', 'You may still take the exam.'],
        ['No exam at all', 'No AP Seminar score.'],
        ['A problem during the exam', 'Tell the AP coordinator right away. AP Services: 866-630-9305.'],
        ['A forgotten login', 'Learn it before May. A saved password will not work.']])
    + tryit('NEXT STEP', 'A trip is planned for May 10. Can you take the exam on May 7?',
            'No. Early testing is never allowed. Talk to the AP coordinator. Late testing is for the unexpected, or two exams at once.')
    + p('Tell me too. See me next class. ' + CK))))

# ================================================================ FOLIO 10
add(board(10, 'Scores in July', 'i-check',
    'Say who scores the exam, when scores come, and which choices have deadlines.',
    [('From June to July', 'f10-june'), ('Your score, 1 to 5', 'f10-score'), ('Choices with deadlines', 'f10-choices')]))

add(paper('f10-june', 'Folio 10', page(
    h2('From June to July')
    + table('dates tight', ['WHEN', 'WHAT'], [
        ['First two weeks of June', 'The AP Reading. College professors and experienced AP teachers score the exam.'],
        ['Before July', 'Sign in once, so you know your login works. Do not make a second account.'],
        ['July 2027', 'Your score, in your College Board account. No day is announced.'],
        ['August 15', 'No score yet? Call AP Services for Students, 866-630-9305.']])
    + p('College Board readers score it, not me. The exam is not rescored.')
    + p('Your score goes to you, to your free-send college, and to educators at your school, me included. Parents see it only if you share your login. ' + CK), 10, 'i-check')))

def plate6():
    rows = [(5, 'Extremely well qualified', 10), (4, 'Very well qualified', 21), (3, 'Qualified', 57), (2, 'Possibly qualified', 10), (1, 'No recommendation', 2)]
    s, bx, kx = '', 152, 2.6
    for i, (sc, words, pct) in enumerate(rows):
        y = 6 + i * 25
        top = sc >= 3
        s += "<circle cx='14' cy='%s' r='9' fill='%s' stroke='%s' stroke-width='1.3'/>" % (y + 9, PINE if top else PAPER, NAVY)
        s += T(14, y + 12.6, str(sc), size=10, fill=PAPER if top else NAVY, anchor='middle')
        s += T(29, y + 13, words, font=SERIF, size=11, weight=600, fill=BROWN)
        w = pct * kx
        s += R(bx, y + 1, round(w, 1), 17, PINE if top else '#b9ad94', NAVY, 1, rx=1)
        lab = '%d percent' % pct
        if w > 70:
            s += T(round(bx + w - 5, 1), y + 13, lab, size=7.8, fill=PAPER, anchor='end')
        else:
            s += T(round(bx + w + 5, 1), y + 13, lab, size=7.8, fill=NAVY)
    s += R(4, 132, 312, 20, CREAM, BRASS, 1.3)
    s += T(160, 145.5, '88 PERCENT SCORED 3 OR HIGHER', size=8.4, fill=PINE, anchor='middle')
    return s

add(paper('f10-score', 'Folio 10', page(
    h3('Your score, 1 to 5')
    + p('Each score has a meaning in College Board words. The bars show how AP Seminar students scored in 2026.')
    + plate('VI', 'How 2026 went', 156,
            'Five bars for 2026 AP Seminar scores. 5, extremely well qualified: 10 percent. 4, very well qualified: 21 percent. 3, qualified: 57 percent. 2, possibly qualified: 10 percent. 1, no recommendation: 2 percent. 88 percent scored 3 or higher',
            plate6(), 'ALL AP SEMINAR STUDENTS', 'College Board score distributions, 2026.')
    + p('One score covers both tasks and the exam. College Board does not publish how points become a 1 to 5. ' + CK))))

add(paper('f10-choices', 'Folio 10', page(
    h3('Choices with deadlines')
    + table('dates tight', ['WHEN', 'CHOICE'], [
        ['June 15, 2027', 'Last moment to cancel a score, 11:59 in the evening, Eastern Time.'],
        ['June 20, 2027', 'Last moment to pick your one free score send, 11:59 in the evening, Eastern Time.'],
        ['September 15, 2027', 'Form due for a printed copy of your typed answers, $10. No scores, no comments. None for late-testing exams.']])
    + card('weak', 'ALL OR NOTHING', 'Cancel your AP Seminar score, and all of it goes, both tasks too.')
    + p('3 or higher in AP Seminar and AP Research earns the AP Seminar and Research Certificate. Add 3 or higher on 4 other AP Exams, and you earn the AP Capstone Diploma. Both show in your July score report. ' + CK))))

# ================================================================ BACK
add(paper('self', 'Self-check', page(
    h3('The exam, ready')
    + form('exready', 'MY EXAM', [
        ('FIRST STEP &middot; THE FACTS', ['I can say the date, the start, and the length.', 'I can say the three Part A prompts.', 'An exam is ordered for me.']),
        ('NEXT STEP &middot; PRACTICE', ['I scored a practice Part A with the rows.', 'I found a theme, not a topic.', 'Two sources talk in one of my paragraphs.']),
        ('GOING FURTHER &middot; READY', ['I wrote a timed Part B in 90 minutes.', 'I know my login and what to leave home.', 'I know when scores come.'])])
    + p('A box you cannot tap is your next step: page [[pj:start]].', fill=True))))

add(paper('fool', 'Words that fool you', page(
    h3('Words that fool you')
    + p('Some English words look like Spanish words but mean something else.')
    + "<table class='stages'><thead><tr><th>ENGLISH</th><th>IN SPANISH</th><th>NOT</th></tr></thead><tbody>"
    "<tr><th>college</th><td><span lang='es'>universidad</span></td><td><span lang='es'>colegio</span>, a school for children and teens</td></tr>"
    "<tr><th>parents</th><td><span lang='es'>padres</span></td><td><span lang='es'>parientes</span>, relatives</td></tr>"
    "<tr><th>to introduce</th><td><span lang='es'>presentar</span></td><td><span lang='es'>introducir</span>, to put something in</td></tr>"
    "<tr><th>large</th><td><span lang='es'>grande</span></td><td><span lang='es'>largo</span>, long</td></tr>"
    "<tr><th>eventually</th><td><span lang='es'>con el tiempo, al final</span></td><td><span lang='es'>eventualmente</span>, which usually means possibly</td></tr>"
    "</tbody></table>"
    + "<p class='small'>Most exam words match: <span lang='es'>identificar, explicar, evaluar, evidencia</span>.</p>")))

def wrow(icon, en, es, line, target):
    return ("<div class='wrow'><div class='wt'><svg class='gi' aria-hidden='true'><use href='#%s'/></svg><strong>%s</strong><em lang='es'>%s</em></div>"
            "<p>%s</p>[[gtag:%s]]</div>") % (icon, tx(en), es, tx(line), target)

WORDS = [
    ('i-check', 'Accommodation', 'adaptaci&oacute;n', 'A change in how you test, approved ahead by the College Board.', 'f9-accom'),
    ('i-quote', 'Attribution', 'atribuci&oacute;n', 'Naming the source of an idea in your sentence.', 'f5-row4'),
    ('i-pen', 'Claim', 'afirmaci&oacute;n', 'A statement about an issue that puts forward a view.', 'f3-a2'),
    ('i-chat', 'Commentary', 'comentario', 'Your explanation of how evidence supports a claim.', 'f5-row2'),
    ('i-cross', 'Counterargument', 'contraargumento', 'A view against yours that your essay answers.', 'f5-samples'),
    ('i-eye', 'Credibility', 'credibilidad', 'How far a source can be believed and trusted.', 'f3-a3'),
    ('i-search', 'Evidence', 'evidencia', 'Information used as proof for a claim.', 'f3-a3'),
    ('i-history', 'Late testing', 'examen en fecha posterior', 'A different version of the exam, on a later set date.', 'f9-late'),
    ('i-steps', 'Line of reasoning', 'l&iacute;nea de razonamiento', 'Claims and evidence in an order that leads to a conclusion.', 'f3-a2'),
    ('i-compass', 'Perspective', 'perspectiva', 'A point of view with its reason, from an argument.', 'f4-theme'),
    ('i-sign', 'Proctor', 'supervisor del examen', 'The adult who runs the exam room and gives the start code.', 'f8-room'),
    ('i-book', 'Reader', 'evaluador', 'A professor or AP teacher trained to score the exam.', 'f10-june'),
    ('i-link', 'Relevance', 'pertinencia', 'How well evidence fits the claim it supports.', 'f3-a3'),
    ('i-count', 'Scoring guidelines', 'pautas de calificaci&oacute;n', 'The rows and points readers use to score.', 'f2-rows'),
    ('i-box', 'Scratch paper', 'papel borrador', 'Paper for notes and plans. It earns no points.', 'f1-bluebook'),
    ('i-link', 'Synthesis', 's&iacute;ntesis', 'Joining ideas from sources into your own argument.', 'f5-row3'),
    ('i-compass', 'Theme', 'tema', 'An idea or issue that links the sources.', 'f4-theme'),
    ('i-pen', 'Thesis', 'tesis', 'The main claim an author argues.', 'f3-a1'),
]
chunks = [WORDS[0:5], WORDS[5:10], WORDS[10:14], WORDS[14:18]]
for n, ch in enumerate(chunks):
    body = (h2('Words in this book') + p('Tap a page to go there.')) if n == 0 else h3('Words in this book, continued')
    body += ''.join(wrow(*w) for w in ch)
    if n == 3:
        body += p('A heritage-language dictionary is welcome for any other word.', fill=True)
    add(paper('words%d' % (n + 1), 'Words in this book', page(body)))

add({'cls': 'endpaper', 'label': 'The last page', 'html':
     "<div class='panel'><div class='kept'>THE LAST PAGE</div><div class='who' style='font-size:7cqw'>Read their argument. Then build your own.</div><div class='meta' style='margin-top:3cqw'>Kept in Room 63<br>AP Capstone, Mater Academy<br>2026-27</div>{{TILDE}}<button type='button' class='loopbtn' data-jump='2'>Back to the contents</button></div><div class='shade'></div>"})
add({'cls': 'endpaper marbled', 'label': 'Endpaper', 'html': "<div class='shade'></div>"})
add({'cls': 'board lthr', 'label': 'Back cover', 'html':
     '<svg class="A-art" viewBox="0 0 720 1000" preserveAspectRatio="none" aria-hidden="true" focusable="false"><g filter="url(#A-grain)"><rect class="A-leather" width="720" height="1000"/><g filter="url(#A-recess)"><ellipse class="A-onlay" cx="360" cy="500" rx="150" ry="112"/></g></g><rect width="720" height="1000" fill="url(#A-vig)"/><rect width="720" height="1000" fill="url(#A-sheen)"/><rect width="22" height="1000" fill="url(#A-hinge)" transform="translate(720 0) scale(-1 1)"/><g filter="url(#A-gilt)"><rect width="720" height="1000" fill="url(#A-goldg)" mask="url(#A-backmask)"/></g><g class="A-titleart" filter="url(#A-titlef)" fill="url(#A-titleg)" text-anchor="middle"><text class="A-t-big" x="360" y="494" font-size="50">ROOM 63</text><text class="A-t-big" x="360" y="550" font-size="17" letter-spacing="3">AP CAPSTONE &#183; 2026-27</text></g></svg><div class=\'shade\'></div>'})

# ---------------------------------------------------------------- cover sizes (tuned by measuring the rendered cover)
COVER = {'COVER_Y1': '376.0', 'COVER_S1': '50.0', 'COVER_Y2': '449.0', 'COVER_S2': '50.0', 'COVER_Y3': '553.0', 'COVER_S3': '110.0'}
for k, v in COVER.items():
    FACES[0]['html'] = FACES[0]['html'].replace(k, v)

# ---------------------------------------------------------------- guards
import re
BAD = ['—', '–', ';', '’', '“', '”']
for i, f in enumerate(FACES):
    vis = re.sub(r'<[^>]+>', ' ', f['html'])
    vis = re.sub(r'&[#\w]+;', 'x', vis)
    for b in BAD:
        if b in vis:
            raise SystemExit('face %d (%s): banned mark %r in visible text' % (i, f.get('label'), b))
assert len(FACES) % 2 == 0, len(FACES)

print(json.dumps({'key': 'ex', 'title': 'The End-of-Course Exam', 'theme': '#1b2440',
                  'colors': {'leather': '#1b2440', 'onlay': '#0a0d17', 'labelskin': '#6d4a14'},
                  'faces': FACES}, ensure_ascii=False, indent=0))
