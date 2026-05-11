# mvhs-bellschedule-skill

A Claude skill that fetches and displays the live MVHS (Mountain View High School) bell schedule, with the current period highlighted and a progress indicator.

## Features

- Live data from MVHS Firebase Realtime DB (no auth required)
- Special day override detection (finals, advisory, testing days, breaks)
- Current period highlighted with `→` and `% complete`
- Natural language summary line
- Supports querying any specific date via `MMDDYYYY` arg

## Structure

```
mvhs-bell-schedule/
├── SKILL.md                    # Skill definition (triggers + usage)
└── scripts/
    └── bell_schedule.py        # All logic — fetch, resolve, render
```

## Installation

Install the `.skill` file from the [latest release](../../releases/latest) into your Claude skills directory.

## Usage

Claude triggers this skill automatically on phrases like:
- "what period is it right now?"
- "show me the MVHS bell schedule"
- "is there school today?"
- "what time is lunch?"

## License

Noncommercial use only. See [LICENSE](LICENSE) for details.
