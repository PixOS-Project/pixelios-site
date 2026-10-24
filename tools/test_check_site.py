#!/usr/bin/env python3
"""Self-check for check-site.py: a clean tree passes, each rule fires on a bad one."""
import importlib.util, os, tempfile

spec = importlib.util.spec_from_file_location("cs", os.path.join(os.path.dirname(__file__), "check-site.py"))
cs = importlib.util.module_from_spec(spec); spec.loader.exec_module(cs)

GOOD = "Last update: 2026-10-24\n| Area | State | Evidence |\n|---|---|---|\n| a | works (2026-10-24) | `run1` |\n"
with tempfile.TemporaryDirectory() as t:
    os.makedirs(t + "/docs")
    def run(status, extra=""):
        open(t + "/docs/STATUS.md", "w").write(status)
        open(t + "/README.md", "w").write(extra)
        cs.SITE = t
        return cs.check({}, "origin/main", 7)
    assert run(GOOD) == []
    assert any("tag" in f for f in run(GOOD.replace("works (2026-10-24) | `run1`", "works | nothing")))
    assert any("stale" in f for f in run("no date here\n"))
    assert any("secret" in f for f in run(GOOD, "see /home/bob/key\n"))
    assert any("link" in f for f in run(GOOD, "github.com/PixOS-Project/pixelios-site/blob/main/nope.md\n"))
print("RESULT: PASS check-site self-test")
