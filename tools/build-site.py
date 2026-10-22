#!/usr/bin/env python3
"""Assemble the documentation site (MkDocs) from docs/, soc/*/ and device/*/.

  python3 tools/build-site.py [OUTDIR]        default .site
  pip install mkdocs-material && mkdocs build -f .site/mkdocs.yml -d site

Device and SoC pages are generated from their json files, so adding a device tree adds its page.
Relative links are rewritten while copying: links between pages that end up in the site stay
relative, links to other repository files become GitHub links, so nothing breaks wherever a
document lives in the repository.
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, ".site"))
SRC = os.path.join(OUT, "src")
GH = "https://github.com/PixOS-Project/pixelios/blob/main/"
UPSTREAM = "https://github.com/dipa-studio/ios-sweet/blob/11da58bd050672960c0a83b5bef2176047eea479/"

pages = {}      # original repo path -> site path (under src/)
extra = {}      # site path -> generated text
copied = {}     # original repo path -> site path (non-markdown assets)


def rd(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def jload(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return json.load(f)


# ---- 1. decide what goes where
for f in sorted(os.listdir(os.path.join(ROOT, "docs"))):
    if f.endswith(".md"):
        pages["docs/" + f] = f
for sub in ("research", "reviews"):
    d = os.path.join(ROOT, "docs", sub)
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.endswith(".md"):
            pages["docs/%s/%s" % (sub, f)] = "%s/%s" % (sub, f)
pages["CONTRIBUTING.md"] = "CONTRIBUTING.md"

devices, socs = [], []
for vendor in sorted(os.listdir(os.path.join(ROOT, "device"))) if os.path.isdir(os.path.join(ROOT, "device")) else []:
    if not os.path.isdir(os.path.join(ROOT, "device", vendor)):
        continue    # e.g. device/AGENTS.md
    for code in sorted(os.listdir(os.path.join(ROOT, "device", vendor))):
        base = "device/%s/%s" % (vendor, code)
        if not os.path.isfile(os.path.join(ROOT, base, "board.json")):
            continue
        devices.append((vendor, code, base))
        site = "devices/%s/%s" % (vendor, code)
        for sub in ("docs",):
            d = os.path.join(ROOT, base, sub)
            for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
                if f.endswith(".md"):
                    pages["%s/%s/%s" % (base, sub, f)] = "%s/%s" % (site, f)
        if os.path.isfile(os.path.join(ROOT, base, "README.md")):
            pages[base + "/README.md"] = site + "/index.md"
        hw = os.path.join(ROOT, base, "hardware")
        for f in sorted(os.listdir(hw)) if os.path.isdir(hw) else []:
            copied["%s/hardware/%s" % (base, f)] = "%s/hardware/%s" % (site, f)
for vendor in sorted(os.listdir(os.path.join(ROOT, "soc"))) if os.path.isdir(os.path.join(ROOT, "soc")) else []:
    if not os.path.isdir(os.path.join(ROOT, "soc", vendor)):
        continue    # e.g. soc/AGENTS.md
    for name in sorted(os.listdir(os.path.join(ROOT, "soc", vendor))):
        base = "soc/%s/%s" % (vendor, name)
        if not os.path.isfile(os.path.join(ROOT, base, "soc.json")):
            continue
        socs.append((vendor, name, base))
        site = "socs/%s/%s" % (vendor, name)
        d = os.path.join(ROOT, base, "docs")
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if f.endswith(".md"):
                pages["%s/docs/%s" % (base, f)] = "%s/%s" % (site, f)

# ---- 2. link rewriting
LINK = re.compile(r"(\]\()([^)\s]+)(\))")


def rewrite(orig, text):
    here = os.path.dirname(orig)
    mine = os.path.dirname(pages[orig])

    def sub(m):
        tgt = m.group(2)
        if re.match(r"^(https?:|mailto:|#)", tgt):
            return m.group(0)
        path, _, frag = tgt.partition("#")
        full = os.path.normpath(os.path.join(here, path)) if path else orig
        dest = pages.get(full) or copied.get(full)
        if dest:
            rel = os.path.relpath(dest, mine or ".")
            return m.group(1) + rel + ("#" + frag if frag else "") + m.group(3)
        if full.startswith(".upstream/"):
            return m.group(1) + UPSTREAM + full[len(".upstream/"):] + m.group(3)
        if full.startswith("..") or full.startswith("/"):
            return m.group(0)
        if os.path.exists(os.path.join(ROOT, full)):
            kind = "tree" if os.path.isdir(os.path.join(ROOT, full)) else "blob"
            return m.group(1) + GH.replace("blob", kind) + full + m.group(3)
        return m.group(0)
    return LINK.sub(sub, text)


# ---- 3. generated pages
def md_table(rows, head):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def hexs(v):
    return v if isinstance(v, str) else str(v)


rows = []
for vendor, code, base in devices:
    d = jload(base + "/board.json")
    rows.append(["[%s](%s/%s/index.md)" % (d["codename"], vendor, code), d["name"], d["soc"], d.get("status", "")])
extra["devices/index.md"] = "# Devices\n\nOne tree per phone under `device/<vendor>/<codename>/`.\n\n" + \
    md_table(rows, ["Codename", "Name", "SoC", "Status"]) + \
    "\n\nAdd yours with `tools/pix new-device`; see [Adding a device](../PORTING.md).\n"

rows = []
for vendor, name, base in socs:
    s = jload(base + "/soc.json")
    users = [d["codename"] for _, _, b in devices for d in [jload(b + "/board.json")] if d["soc"] == "%s/%s" % (vendor, name)]
    rows.append(["[%s](%s/%s/index.md)" % (s["name"], vendor, name), s.get("marketing", ""), ", ".join(users)])
extra["socs/index.md"] = "# SoCs\n\nShared values and code per chip under `soc/<vendor>/<soc>/`.\n\n" + \
    md_table(rows, ["SoC", "Marketing name", "Devices"]) + "\n"

for vendor, code, base in devices:
    d = jload(base + "/board.json")
    site = "devices/%s/%s" % (vendor, code)
    notes = d.get("notes", {})
    body = "# %s (`%s`)\n\n- SoC: [%s](%s)\n- Status: %s\n- Tree: [`%s`](%s%s)\n\n" % (
        d["name"], d["codename"], d["soc"], os.path.relpath("socs/%s/index.md" % d["soc"], site),
        d.get("status", ""), base, GH.replace("blob", "tree"), base)
    keys = [k for k in d if k not in ("name", "codename", "soc", "status", "notes")]
    body += "## board.json\n\n" + md_table([[k, "`%s`" % json.dumps(d[k])] for k in keys], ["Key", "Value"]) + "\n"
    if notes:
        body += "\n## Notes\n\n" + "\n".join("- **%s**: %s" % (k, v) for k, v in notes.items()) + "\n"
    hw = [c for c in copied if c.startswith(base + "/hardware/")]
    if hw:
        body += "\n## Hardware captures\n\n" + "\n".join(
            "- [%s](hardware/%s) (%d KiB)" % (os.path.basename(c), os.path.basename(c),
                                             os.path.getsize(os.path.join(ROOT, c)) // 1024 + 1) for c in hw) + "\n"
    readme = base + "/README.md"
    if readme in pages:
        body += "\n---\n\n" + rd(readme)
        del pages[readme]
    extra[site + "/index.md"] = body

for vendor, name, base in socs:
    s = jload(base + "/soc.json")
    site = "socs/%s/%s" % (vendor, name)
    keys = [k for k in s if k not in ("name", "marketing", "notes")]
    body = "# %s (%s)\n\nTree: [`%s`](%s%s)\n\n## soc.json\n\n" % (
        s["name"], s.get("marketing", ""), base, GH.replace("blob", "tree"), base)
    body += md_table([[k, "`%s`" % json.dumps(s[k])] for k in keys], ["Key", "Value"]) + "\n"
    if s.get("notes"):
        body += "\n## Notes\n\n" + "\n".join("- **%s**: %s" % (k, v) for k, v in s["notes"].items()) + "\n"
    srcd = os.path.join(ROOT, base, "shim")
    if os.path.isdir(srcd):
        body += "\n## Shim sources\n\n" + "\n".join("- [`%s`](%s%s/shim/%s)" % (f, GH, base, f) for f in sorted(os.listdir(srcd))) + "\n"
    extra[site + "/index.md"] = body

# ---- 4. write the tree
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(SRC)
for orig, site in pages.items():
    dst = os.path.join(SRC, site)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(rewrite(orig, rd(orig)))
for site, text in extra.items():
    dst = os.path.join(SRC, site)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    # generated pages link only inside the site, plus GitHub URLs: no rewriting needed
    with open(dst, "w", encoding="utf-8") as f:
        f.write(text)
for orig, site in copied.items():
    dst = os.path.join(SRC, site)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(os.path.join(ROOT, orig), dst)


def title(site):
    p = os.path.join(SRC, site)
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.startswith("# "):
                return line[2:].strip().replace('"', "'")
    return os.path.basename(site)


def entry(site):
    return "      - \"%s\": %s" % (title(site), site)


nav = ["nav:", "  - Home: index.md", "  - Guide:"]
nav += [entry(p) for p in ("STATUS.md", "BUILD.md", "QR_LOG.md", "AUTOMATION.md", "ROOTLESS_BUILD.md", "PORTING.md", "MAP.md", "SAFETY.md", "AI_DEVELOPMENT.md", "CONTRIBUTING.md")
        if os.path.exists(os.path.join(SRC, p))]
nav += ["  - Design:"] + [entry(p) for p in ("PLAN.md", "CASE_STUDY.md") if os.path.exists(os.path.join(SRC, p))]
nav += ["  - Devices:", "      - Overview: devices/index.md"]
for vendor, code, base in devices:
    nav.append("      - \"%s\":" % jload(base + "/board.json")["name"])
    nav.append("          - Overview: devices/%s/%s/index.md" % (vendor, code))
    for p in sorted(x for x in pages.values() if x.startswith("devices/%s/%s/" % (vendor, code)) and not x.endswith("index.md")):
        nav.append("          - \"%s\": %s" % (title(p), p))
nav += ["  - SoCs:", "      - Overview: socs/index.md"]
for vendor, name, base in socs:
    nav.append("      - \"%s\":" % jload(base + "/soc.json")["name"])
    nav.append("          - Overview: socs/%s/%s/index.md" % (vendor, name))
    for p in sorted(x for x in pages.values() if x.startswith("socs/%s/%s/" % (vendor, name)) and not x.endswith("index.md")):
        nav.append("          - \"%s\": %s" % (title(p), p))
nav += ["  - Research:"] + [entry(p) for p in sorted(x for x in pages.values() if x.startswith("research/"))]
nav += ["  - Reviews:"] + [entry(p) for p in sorted(x for x in pages.values() if x.startswith("reviews/"))]
nav += ["  - Credits: CREDITS.md"]

cfg = """site_name: PixeliOS
site_description: Apple's XNU and iOS 16 on the Google Pixel 6a (Tensor G1), with device trees for other Pixels
site_url: https://pixos-project.github.io/pixelios/
repo_url: https://github.com/PixOS-Project/pixelios
repo_name: PixOS-Project/pixelios
docs_dir: src
theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle: {icon: material/brightness-7, name: Dark mode}
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle: {icon: material/brightness-4, name: Light mode}
  features: [navigation.sections, navigation.top, search.suggest, content.code.copy, toc.follow]
markdown_extensions:
  - admonition
  - tables
  - toc: {permalink: true}
  - pymdownx.highlight
  - pymdownx.superfences
validation:
  omitted_files: ignore
  unrecognized_links: warn
  anchors: ignore
""" + "\n".join(nav) + "\n"
with open(os.path.join(OUT, "mkdocs.yml"), "w") as f:
    f.write(cfg)
print("site tree: %d pages, %d generated, %d assets -> %s" % (len(pages), len(extra), len(copied), OUT))
