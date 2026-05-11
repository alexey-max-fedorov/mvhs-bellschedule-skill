---
name: mvhs-bell-schedule
description: Fetch and display the live MVHS (Mountain View High School) bell schedule for today or any given date, with the current period highlighted and a progress indicator. Use this skill whenever the user asks about the MVHS bell schedule, what period it is right now, whether there's school today, or what time any period starts or ends at MVHS. Trigger on phrases like "bell schedule", "what period is it", "MVHS schedule", "is there school today", "what time is lunch/brunch/tutorial", or any reference to MVHS class periods.
---

# MVHS Bell Schedule

Fetches live schedule data from the MVHS Firebase Realtime DB (public, no auth required).

## Usage

**Today's schedule:**
```bash
python3 scripts/bell_schedule.py
```

**Specific date:**
```bash
python3 scripts/bell_schedule.py MMDDYYYY
```

The script handles everything: parallel Firebase fetches, special-day override detection, current period highlight with % progress, and a natural language summary line.

## Output Example

```
📅 Monday, May 11, 2026 — Schedule A

  Period    Time                 Status
  ────────  ───────────────────  ──────────────
  Period 1  8:30 AM – 9:20 AM    ✓ done
  Period 2  9:27 AM – 10:17 AM   ✓ done
  Brunch    10:17 AM – 10:25 AM  ✓ done
→ Period 4  11:29 AM – 12:19 PM  ◀ NOW (91%)
  Lunch     12:19 PM – 12:54 PM  upcoming
  ...

You're in Period 4 right now — 5 min left.
```

## Notes

- All times are America/Los_Angeles (PDT = UTC−7 Mar–Oct, PST = UTC−8 Nov–Feb)
- `"none"` schedule = no school today
- Special day keys in `/days.json` use format `MMDDYYYY-MMDDYYYY`
- Always fetches fresh — no caching
