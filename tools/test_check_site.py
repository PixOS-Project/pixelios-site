#!/usr/bin/env python3
"""Self-check for check-site.py: a clean tree passes, each rule fires on a bad one."""
import importlib.util, json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render_progress as rp

spec = importlib.util.spec_from_file_location("cs", os.path.join(HERE, "check-site.py"))
cs = importlib.util.module_from_spec(spec); spec.loader.exec_module(cs)

ROW = lambda i, state, head: {"id": i, "stream": "GPU", "rung": "r", "state": state, "headline": head, "date": "2026-11-07", "run": "run1", "tag": "observed on hardware", "note": ""}
DATA = {"as_of": "2026-11-07", "milestones_newest": "2026-11-07", "rows": [ROW("G-F20", "done", "38"), ROW("W-SCAN", "open", "none")]}
GOOD = "Last update: 2026-11-07\n| Area | State | Evidence |\n|---|---|---|\n| a | works (2026-11-07) | `run1` |\n"
BLOCKS = "<!-- progress:%s:begin -->\n<!-- progress:%s:end -->\n"

with tempfile.TemporaryDirectory() as t:
    os.makedirs(t + "/docs"); os.makedirs(t + "/data")

    def run(status=GOOD, extra="", data=DATA, render=True):
        json.dump(data, open(t + "/data/progress.json", "w"))
        open(t + "/docs/STATUS.md", "w").write(status + BLOCKS % ("features", "features") + BLOCKS % ("status", "status"))
        open(t + "/docs/MILESTONES.md", "w").write(BLOCKS % ("ladder", "ladder"))
        open(t + "/README.md", "w").write(extra)
        if render:
            rp.run(t)
        cs.SITE = t
        return cs.check({}, "origin/main", 7)

    assert run() == [], run()
    assert any("tag" in f for f in run(GOOD.replace("works (2026-11-07) | `run1`", "works | nothing")))
    assert any("stale" in f for f in run("no date here\n"))
    assert any("secret" in f for f in run(GOOD, "see /home/bob/key\n"))
    assert any("link" in f for f in run(GOOD, "github.com/PixOS-Project/pixelios-site/blob/main/nope.md\n"))
    # staleness: the page date is more than 7 days behind the export
    assert any("days behind the export" in f for f in run(GOOD.replace("2026-11-07\n", "2026-10-24\n", 1).replace("works (2026-11-07)", "works (2026-10-24)")))
    assert run(GOOD.replace("Last update: 2026-11-07", "Last update: 2026-11-01").replace("works (2026-11-07)", "works (2026-11-01)")) == []  # 6 days: inside the limit
    # drift: a hand edit inside the generated block
    run()
    s = open(t + "/docs/STATUS.md").read().replace("| 38 |", "| 99 |").replace("38", "99")
    open(t + "/docs/STATUS.md", "w").write(s)
    cs.SITE = t
    assert any("drift" in f for f in cs.check({}, "origin/main", 7)), "hand edit in a generated block not reported"
    # a stale claim the export contradicts (rung G-F20 is done)
    assert any("contradicts rung G-F20" in f for f in run(GOOD, "The GPU is not used for drawing yet.\n"))
    assert run(GOOD, "The GPU is not used for drawing yet.\n", data={**DATA, "rows": [ROW("G-F20", "open", "none")]}) == []
    # no export at all
    os.remove(t + "/data/progress.json")
    assert any("no progress export" in f for f in cs.check({}, "origin/main", 7))
    # page age: Last verified missing / older than the limit / fresh
    import datetime
    open(t + "/docs/A.md", "w").write("# A\nLast verified: 2026-11-01\n")
    open(t + "/docs/B.md", "w").write("# B\n")
    ages = cs.age_findings(datetime.date(2026, 11, 20), 14)
    assert any("docs/A.md:1 age last verified 2026-11-01" in f for f in ages) and any("docs/B.md:1 age no 'Last verified" in f for f in ages), ages
    assert not any("docs/A.md" in f for f in cs.age_findings(datetime.date(2026, 11, 10), 14))
print("RESULT: PASS check-site self-test")
