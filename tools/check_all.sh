#!/bin/sh
# Every check, in the order that matters. Run from the repository root:  sh tools/check_all.sh
# Privacy comes first: if the repository is public, stop and tell Mr. Portela before anything else.
# The build steps rewrite the handout PDFs and the consent forms, so expect those files to show as changed.
export NODE_PATH="$(npm root -g)"
fail=0
run() { name=$1; shift; printf '\n== %s\n' "$name"; "$@" || { fail=1; printf 'FAILED: %s\n' "$name"; }; }
run "privacy: the repository must be private"   python3 tools/check_privacy.py
run "data: roster, searches, databases"          python3 tools/check.py
run "build: handouts and Research Library"       python3 classroom/build.py
run "print: handout page counts and fonts"       node classroom/build-pdf.cjs
run "print: consent forms, one page each"        sh -c 'cd classroom && sh build-consent.sh'
run "links: every link in the log and handouts"  python3 tools/check_links.py
run "browser: all slips"                         node tools/smoke.cjs
run "browser: the question workbench"            node tools/workbench.cjs
run "design: the DESIGN.md floor"                node tools/design_check.cjs
printf '\n%s\n' "$([ $fail = 0 ] && echo 'ALL CHECKS PASS' || echo 'SOME CHECKS FAILED: see FAILED lines above')"
exit $fail
