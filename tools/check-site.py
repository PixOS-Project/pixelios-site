#!/usr/bin/env python3
"""Gate for the docs site (TP-019). Flags drift; it cannot prove a claim true.

Checks: (1) cross-repo GitHub links resolve, (2) STATUS.md "works" rows carry evidence,
(3) STATUS.md "Last update" is not more than --max-age-days behind data/progress.json (the export of the milestone numbers, T-69a2),
(4) the generated tables match that file, (5) no page still makes a claim the export contradicts, (6) no secrets,
(7) every page carries a "Last verified: YYYY-MM-DD" line no older than --page-age-days (default 14): a WARN line, a failure only with
--strict-age (the weekly run uses it, so a stale page opens an issue; a deploy is never blocked by age alone).
Run labels and commits cited by a page are checked against the private logs by the maintainers' export (tools/site-progress check).
Usage: tools/check-site.py [--kernel DIR] [--userland DIR] [--ref REF] [--max-age-days N] [--page-age-days N] [--strict-age] [--today YYYY-MM-DD]
Report: one `file:line rule message` per finding, last line `RESULT: PASS|FAIL|ERROR ...`; exit 0/1/2.
"""
import argparse, datetime, glob, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINK = re.compile(r"github\.com/PixOS-Project/(pixelios-[a-z]+)/(?:blob|tree)/main/([^)\s>#\"'`]+)")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
SECRETS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY"), "private key"),
    (re.compile(r"/home/[a-z][\w-]*/"), "local path"),
    (re.compile(r"(?<!\d)\d{15}(?!\d)"), "15-digit number (IMEI?)"),
    (re.compile(r"(?i)\bserial(?:no| number)?\s*[:=]\s*[A-Z0-9]{8,}\b"), "device serial"),
]


# claims that stop being true once the export records a rung as reached: (pattern, rung, states that contradict it)
DONE = ("done", "done-one-run", "met-one-run", "met-with-stopgap")
STALE_CLAIMS = [
    (re.compile(r"(?i)GPU is not used for drawing|no GPU[- ]rendered frame|no GPU rendering|no renderer yet|Software rendering only \(no GPU\)"), "G-F20", DONE),
    (re.compile(r"(?i)no driver and no firmware|no firmware or driver yet|Wi-Fi[^.|]{0,60}not working"), "W-SCAN", DONE),
    (re.compile(r"(?i)M13 Bluetooth \[open|Bluetooth[^.|]{0,40}no drivers yet"), "W-HCI", DONE),
]


def git(d, *a):
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True)


LAST_VERIFIED = re.compile(r"(?i)last verified:?\**\s*(\d{4}-\d{2}-\d{2})")


def age_findings(today, max_age):
    out = []
    for f in sorted(md_files() + [os.path.join(SITE, "CONTRIBUTING.md")]):
        if not os.path.isfile(f) or os.path.basename(f) in ("CODE_OF_CONDUCT.md", "SECURITY.md", "AGENTS.md", "LICENSE"):
            continue
        m = LAST_VERIFIED.search(open(f, encoding="utf-8").read())
        if not m:
            out.append("%s:1 age no 'Last verified: YYYY-MM-DD' line" % rel(f))
        elif (today - datetime.date.fromisoformat(m.group(1))).days > max_age:
            out.append("%s:1 age last verified %s, more than %d days ago: re-check the page against the logs" % (rel(f), m.group(1), max_age))
    return out


def md_files():
    fs = glob.glob(SITE + "/*.md") + glob.glob(SITE + "/docs/*.md")
    return fs


def rel(f):
    return os.path.relpath(f, SITE)


def check(repos, ref, max_age):
    out = []
    refs = {}
    for name, d in repos.items():
        if d and os.path.isdir(d):
            refs[name] = ref if git(d, "rev-parse", "--verify", "-q", ref).returncode == 0 else "HEAD"
    for f in md_files():
        for n, line in enumerate(open(f, encoding="utf-8"), 1):
            for repo, path in LINK.findall(line):
                if repo == "pixelios-site":
                    ok = os.path.exists(os.path.join(SITE, path))
                elif repo in refs:
                    ok = git(repos[repo], "cat-file", "-e", "%s:%s" % (refs[repo], path.rstrip("/"))).returncode == 0
                else:
                    continue  # repo not checked out: cannot judge
                if not ok:
                    out.append("%s:%d link %s/%s does not exist on %s" % (rel(f), n, repo, path, refs.get(repo, "main")))
            for rx, what in SECRETS:
                if rx.search(line):
                    out.append("%s:%d secret %s" % (rel(f), n, what))
    status = os.path.join(SITE, "docs/STATUS.md")
    lines = open(status, encoding="utf-8").read().splitlines()
    for n, line in enumerate(lines, 1):
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
        if len(cells) >= 3 and re.search(r"(?i)\bworks\b", cells[1]) and not (DATE.search(line) or "`" in cells[2]):
            out.append("%s:%d tag 'works' row has no date or evidence (rule 5): %s" % (rel(status), n, cells[0][:50]))
    m = re.search(r"Last update:\s*(\d{4}-\d{2}-\d{2})", "\n".join(lines))
    prog = os.path.join(SITE, "data", "progress.json")
    if not m:
        out.append("docs/STATUS.md:1 stale no 'Last update: YYYY-MM-DD' line")
    if not os.path.exists(prog):
        out.append("data/progress.json:1 stale no progress export (tools/site-progress build in the maintainers' repo writes it)")
    else:
        data = json.load(open(prog, encoding="utf-8"))
        if m and data.get("as_of"):
            age = (datetime.date.fromisoformat(data["as_of"]) - datetime.date.fromisoformat(m.group(1))).days
            if age > max_age:
                out.append("docs/STATUS.md:1 stale Last update %s is %d days behind the export (%s)" % (m.group(1), age, data["as_of"]))
        import render_progress
        for d in render_progress.run(SITE, check=True):
            out.append("docs/STATUS.md:1 drift %s: run python3 tools/render_progress.py" % d)
        states = {r["id"]: r["state"] for r in data["rows"]}
        for f in md_files():
            for n, line in enumerate(open(f, encoding="utf-8"), 1):
                for rx, rung, bad in STALE_CLAIMS:
                    if states.get(rung) in bad and rx.search(line):
                        out.append("%s:%d stale claim contradicts rung %s (%s): %s" % (rel(f), n, rung, states[rung], rx.search(line).group(0)))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--kernel", default=os.path.join(SITE, "..", "pixelios-kernel"))
    p.add_argument("--userland", default=os.path.join(SITE, "..", "pixelios-userland"))
    p.add_argument("--ref", default="origin/main")
    p.add_argument("--max-age-days", type=int, default=7)
    p.add_argument("--page-age-days", type=int, default=14)
    p.add_argument("--strict-age", action="store_true")
    p.add_argument("--today")
    a = p.parse_args()
    try:
        out = check({"pixelios-kernel": a.kernel, "pixelios-userland": a.userland}, a.ref, a.max_age_days)
        today = datetime.date.fromisoformat(a.today) if a.today else datetime.datetime.now(datetime.timezone.utc).date()
        ages = age_findings(today, a.page_age_days)
    except Exception as e:  # noqa
        print("RESULT: ERROR %s" % e)
        return 2
    if a.strict_age:
        out += ages
    else:
        for w in ages:
            print("WARN " + w)
    if out:
        print("\n".join(out))
    print("RESULT: %s %d findings" % ("FAIL" if out else "PASS", len(out)))
    return 1 if out else 0


if __name__ == "__main__":
    sys.exit(main())
