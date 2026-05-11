#!/usr/bin/env python3
"""
MVHS Bell Schedule fetcher.
Usage: python3 bell_schedule.py [MMDDYYYY]
  - No arg: today (America/Los_Angeles)
  - With date arg: show schedule for that date (no NOW highlight)
"""
import urllib.request, json, threading, sys
from datetime import datetime, timezone, timedelta

URLS = {
    "weekday_map": "https://mvhs-app-d04d2.firebaseio.com/weekday-map.json",
    "days":        "https://mvhs-app-d04d2.firebaseio.com/days.json",
    "schedules":   "https://mvhs-app-d04d2.firebaseio.com/schedules.json",
}

# ── Fetch all endpoints in parallel ───────────────────────────────────────
results, errors = {}, {}
def fetch(key, url):
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            results[key] = json.load(r)
    except Exception as e:
        errors[key] = str(e)

threads = [threading.Thread(target=fetch, args=(k, u)) for k, u in URLS.items()]
for t in threads: t.start()
for t in threads: t.join()

if errors:
    print("Fetch error:", errors, file=sys.stderr)
    sys.exit(1)

weekday_map = results["weekday_map"]
days        = results["days"]
schedules   = results["schedules"]

# ── Resolve target date ────────────────────────────────────────────────────
def la_offset():
    return -7 if 3 <= datetime.now(timezone.utc).month <= 10 else -8

offset = la_offset()
now_la = datetime.now(timezone(timedelta(hours=offset))).replace(tzinfo=None)

if len(sys.argv) > 1:
    target = datetime.strptime(sys.argv[1], "%m%d%Y").replace(
        hour=now_la.hour, minute=now_la.minute)
    is_today = False
else:
    target = now_la
    is_today = True

today_str = target.strftime("%m%d%Y")
js_day    = (target.weekday() + 1) % 7

# ── Resolve schedule name (special day override first) ─────────────────────
def to_yyyymmdd(s):  # s = MMDDYYYY
    return int(s[4:8] + s[0:2] + s[2:4])

target_int = to_yyyymmdd(today_str)
schedule_name, is_special = None, False

for range_key, sched in days.items():
    try:
        if to_yyyymmdd(range_key[:8]) <= target_int <= to_yyyymmdd(range_key[9:]):
            schedule_name = sched
            is_special = True
            break
    except:
        pass

if schedule_name is None:
    schedule_name = weekday_map[js_day]

# ── Render ─────────────────────────────────────────────────────────────────
date_label    = target.strftime("%A, %B %-d, %Y")
sched_display = schedule_name + ("*" if is_special else "")
print(f"\n📅 {date_label} — {sched_display}")
if is_special:
    print("   * Special schedule override")

if schedule_name == "none":
    print("   🚫 No school today.\n")
    sys.exit(0)

if schedule_name not in schedules:
    print(f"   ⚠️  Schedule '{schedule_name}' not found in database.\n")
    sys.exit(1)

def parse_hhmm(s, base):
    return base.replace(hour=int(s[:2]), minute=int(s[2:]), second=0, microsecond=0)

def fmt12(dt):
    h, m = dt.hour, dt.minute
    return f"{h%12 or 12}:{m:02d} {'AM' if h < 12 else 'PM'}"

rows, current_label = [], None
for time_key in sorted(schedules[schedule_name].keys()):
    label  = schedules[schedule_name][time_key]
    start  = parse_hhmm(time_key[:4], target)
    end    = parse_hhmm(time_key[5:], target)
    period = f"Period {label}" if isinstance(label, int) else str(label)
    trange = f"{fmt12(start)} – {fmt12(end)}"
    if not is_today or target < start:
        status = "upcoming"
    elif target >= end:
        status = "✓ done"
    else:
        pct    = int((target - start).total_seconds() / (end - start).total_seconds() * 100)
        status = f"◀ NOW ({pct}%)"
        current_label = period
    rows.append((period, trange, status))

c1 = max(len(r[0]) for r in rows)
c2 = max(len(r[1]) for r in rows)
print(f"\n  {'Period':<{c1}}  {'Time':<{c2}}  Status")
print(f"  {'─'*c1}  {'─'*c2}  {'─'*14}")
for p, t, s in rows:
    marker = "→ " if "NOW" in s else "  "
    print(f"{marker}{p:<{c1}}  {t:<{c2}}  {s}")

# ── Natural language summary ───────────────────────────────────────────────
print()
if not is_today:
    pass
elif current_label:
    for time_key in sorted(schedules[schedule_name].keys()):
        start = parse_hhmm(time_key[:4], target)
        end   = parse_hhmm(time_key[5:], target)
        if start <= target < end:
            mins_left = int((end - target).total_seconds() / 60)
            print(f"You're in {current_label} right now — {mins_left} min left.")
            break
elif all(s == "✓ done" for _, _, s in rows):
    print("School's done for the day.")
elif all(s == "upcoming" for _, _, s in rows):
    first_start = parse_hhmm(sorted(schedules[schedule_name].keys())[0][:4], target)
    mins_to = int((first_start - target).total_seconds() / 60)
    print(f"School hasn't started yet — {mins_to} min until Period 1.")
