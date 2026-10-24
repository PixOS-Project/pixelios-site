#!/usr/bin/env python3
"""Gate for the docs site (TP-019). Flags drift; it cannot prove a claim true.

Checks: (1) cross-repo GitHub links resolve, (2) STATUS.md "works" rows carry evidence,
(3) STATUS.md "Last update" is not far behind the kernel Wi-Fi coverage file, (4) no secrets.
Usage: tools/check-site.py [--kernel DIR] [--userland DIR] [--ref REF] [--max-age-days N]
Report: one `file:line rule message` per finding, last line `RESULT: PASS|FAIL|ERROR ...`; exit 0/1/2.
"""
import argparse, datetime, glob, os, re, subprocess, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINK = re.compile(r"github\.com/PixOS-Project/(pixelios-[a-z]+)/(?:blob|tree)/main/([^)\s>#\"'`]+)")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
SECRETS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY"), "private key"),
    (re.compile(r"/home/[a-z][\w-]*/"), "local path"),
    (re.compile(r"(?<!\d)\d{15}(?!\d)"), "15-digit number (IMEI?)"),
    (re.compile(r"(?i)\bserial(?:no| number)?\s*[:=]\s*[A-Z0-9]{8,}\b"), "device serial"),
]


def git(d, *a):
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True)


def md_files():
    fs = glob.glob(SITE + "/*.md") + glob.glob(SITE + "/docs/*.md")
    return [f for f in fs if os.path.basename(f) not in ("COVERAGE.md",)]  # generated


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
    m = DATE.search(re.search(r"Last update:\s*([\d-]+)", "\n".join(lines)).group(1)) if re.search(r"Last update:\s*[\d-]+", "\n".join(lines)) else None
    if not m:
        out.append("docs/STATUS.md:1 stale no 'Last update: YYYY-MM-DD' line")
    elif "pixelios-kernel" in refs:
        r = git(repos["pixelios-kernel"], "log", "-1", "--format=%cs", refs["pixelios-kernel"], "--", "docs/WIFI-COVERAGE.md")
        if DATE.fullmatch(r.stdout.strip()):
            age = (datetime.date.fromisoformat(r.stdout.strip()) - datetime.date.fromisoformat(m.group(0))).days
            if age > max_age:
                out.append("docs/STATUS.md:1 stale Last update %s is %d days behind kernel WIFI-COVERAGE.md (%s)" % (m.group(0), age, r.stdout.strip()))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--kernel", default=os.path.join(SITE, "..", "pixelios-kernel"))
    p.add_argument("--userland", default=os.path.join(SITE, "..", "pixelios-userland"))
    p.add_argument("--ref", default="origin/main")
    p.add_argument("--max-age-days", type=int, default=7)
    a = p.parse_args()
    try:
        out = check({"pixelios-kernel": a.kernel, "pixelios-userland": a.userland}, a.ref, a.max_age_days)
    except Exception as e:  # noqa
        print("RESULT: ERROR %s" % e)
        return 2
    print("\n".join(out))
    print("RESULT: %s %d findings" % ("FAIL" if out else "PASS", len(out)))
    return 1 if out else 0


if __name__ == "__main__":
    sys.exit(main())
