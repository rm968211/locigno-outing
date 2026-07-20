#!/usr/bin/env python3
"""Regenerate index.html from the save data embedded in assets/locigno-outing.xlsx.

Every spreadsheet the Cross Creek Commissioners Toolkit saves carries its full
save JSON, deflate+base64 encoded ("CC1:...") in a hidden _meta sheet. This
script decodes it and fills tools/template.html — mirroring the Toolkit PDF's
layout: Roomies, Rankings, Pairings day by day with Tuesday and the total.

Run from anywhere: python3 tools/build.py  (stdlib only)
"""
import base64, html, json, os, re, sys, zipfile, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, "assets", "locigno-outing.xlsx")
TEMPLATE = os.path.join(ROOT, "tools", "template.html")
OUT = os.path.join(ROOT, "index.html")

# ---------- pull the save JSON out of the workbook ----------
def sheet_text(xml, shared):
    """Concatenated cell text of one worksheet — inline strings plus
    sharedStrings refs, so a copy re-saved by Excel still decodes."""
    out = []
    for c in re.findall(r"<c [^>]*>.*?</c>", xml, re.S):
        if 't="inlineStr"' in c:
            out += re.findall(r"<t[^>]*>([^<]*)</t>", c)
        elif 't="s"' in c and shared:
            m = re.search(r"<v>(\d+)</v>", c)
            if m and int(m.group(1)) < len(shared):
                out.append(shared[int(m.group(1))])
    return html.unescape("".join(out))

def load_save(path):
    z = zipfile.ZipFile(path)
    shared = None
    if "xl/sharedStrings.xml" in z.namelist():
        sst = z.read("xl/sharedStrings.xml").decode()
        shared = ["".join(re.findall(r"<t[^>]*>([^<]*)</t>", si))
                  for si in re.findall(r"<si[ >].*?</si>|<si/>", sst, re.S)]
    for name in sorted(z.namelist()):
        if not re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name):
            continue
        text = sheet_text(z.read(name).decode(), shared).strip()
        if text.startswith("CC1:"):
            return json.loads(zlib.decompress(base64.b64decode(text[4:]), -15))
        if text.startswith('{"type":"cross-creek-save"'):
            return json.loads(text)
    sys.exit("No Cross Creek save data found in " + path)

save = load_save(XLSX)

# ---------- generate the page ----------
COLS = [save["roster"][L].split("\n") for L in "ABCD"]
LETTERS = "ABCD"
SENIORS = set(save.get("seniors", []))
TEE = save["tee"]
GAM = save.get("gambling", {})
TWOMAN = save["twoMan"]
TUESDAY = save.get("tuesday", {"name": "Tuesday Round", "desc": "", "start": ""})
EVENTS = save["events"]
TEAMS = save["teams"]
DAYS = ["Sunday", "Monday"]

esc = lambda t: html.escape(str(t), quote=False)

def fmt_tee(t):
    if not t: return ""
    h, m = t.split(":")
    h = int(h)
    return f"{(h + 11) % 12 + 1}:{m} {'AM' if h < 12 else 'PM'}"

def find(nm):
    for c in range(4):
        if nm in COLS[c]: return c, COLS[c].index(nm)
    return None

def tag(nm):
    p = find(nm)
    out = esc(nm)
    if p: out += f' <span class="rk">{LETTERS[p[0]]}{p[1]+1}</span>'
    if nm in SENIORS: out += ' <span class="sr">SR</span>'
    return out

def gam_foot(key):
    g = GAM.get(key, {})
    amt, det = str(g.get("amt", "")).strip(), str(g.get("det", "")).strip()
    if not (amt or det): return ""
    buy = f'<span class="buyin">${int(amt) if amt.isdigit() else esc(amt)} buy-in</span>' if amt else ""
    dd = f'<div class="gamdet">{esc(det).replace(chr(10), "<br>")}</div>' if det else ""
    return f'    <div class="gam">{buy}{dd}</div>\n'

def card(name, holes, time, body, key, details=""):
    t = f'<span class="time">{time}</span>' if time else ""
    h = f'  <div class="event">\n    <div class="ehead"><span class="ename">{esc(name)} <span class="holes">({holes} holes)</span></span>{t}</div>\n'
    if details:
        h += f'    <div class="details">{esc(details).replace(chr(10), "<br>")}</div>\n'
    if body:
        h += f'    <div class="tscroll"><table>\n      <tbody>\n{body}\n      </tbody>\n    </table></div>\n'
    return h + gam_foot(key) + "  </div>\n"

def fourman_body(r):
    rows = []
    for k, gi in enumerate(TEE["perm"][f"e{r}"]):
        tds = "".join(f'<td>{tag(COLS[c][TEAMS[r][gi][c]])}</td>' for c in range(4))
        rows.append(f'      <tr><td class="num">{k+1}</td>{tds}</tr>')
    return "\n".join(rows)

def twoman_body():
    rows = []
    for k, gi in enumerate(TEE["perm"]["tm"]):
        grp = TWOMAN["groups"][gi]
        t1 = " &amp; ".join(tag(n) for n in grp[0] if n) or "&mdash;"
        t2 = " &amp; ".join(tag(n) for n in grp[1] if n) or "&mdash;"
        rows.append(f'      <tr><td class="num">{k+1}</td><td>{t1}</td><td>{t2}</td></tr>')
    return "\n".join(rows)

pair, last_day = "", None
key_html = '<span class="daykey"><span class="sr">SR</span> = plays the senior tees</span>' if SENIORS else ""
for key in TEE["seq"]:
    day = TEE["day"][key]
    first = DAYS[day] != last_day
    if first:
        pair += f'  <div class="day"><span>{DAYS[day]}</span>{key_html if last_day is None else ""}</div>\n'
        last_day = DAYS[day]
    time = fmt_tee(TEE.get("start", {}).get(str(day), "")) if first else ""
    if key == "tm":
        pair += card(TWOMAN["name"], 9, time, twoman_body(), "tm")
    else:
        r = int(key[1:])
        pair += card(EVENTS[r], 18, time, fourman_body(r), key)

pair += '  <div class="day"><span>Tuesday</span></div>\n'
pair += card(TUESDAY["name"], 18, fmt_tee(TUESDAY.get("start", "")), "", "tu", details=TUESDAY.get("desc", ""))

total = sum(int(a) for a in (str(GAM.get(g, {}).get("amt", "")).strip() for g in GAM) if a.isdigit())
if total:
    pair += f'  <div class="total">${total} total &mdash; all buy-ins, per player</div>\n'

rank_cols = "\n".join(
    f'      <div class="rankcol"><h4>{LETTERS[c]} Players</h4><ol>\n'
    + "\n".join(f'        <li>{esc(nm)}</li>' for nm in COLS[c])
    + '\n      </ol></div>'
    for c in range(4))

room_rows = "\n".join(
    f'      <tr><td class="num">{i+1}</td><td>{esc(rm[0] or "")}</td><td>{esc(rm[1] or "")}</td></tr>'
    for i, rm in enumerate(save.get("roomies", {}).get("rooms", [])))

out = open(TEMPLATE).read()
out = out.replace("@@PAIRINGS@@", pair.rstrip())
out = out.replace("@@RANK_COLS@@", rank_cols)
out = out.replace("@@ROOM_ROWS@@", room_rows)
assert "@@" not in out, "unfilled template token"
open(OUT, "w").write(out)
print("regenerated index.html from", os.path.basename(XLSX))
