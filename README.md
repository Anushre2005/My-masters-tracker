# Masters Tracker

A personal Windows desktop app for planning a Master's application (2029 intake) and preparing for the GRE.
Everything runs locally: a Flask server on `http://127.0.0.1:8765` shown in its own window (pywebview), SQLite for data,
Windows notifications for reminders, and a local [Ollama](https://ollama.com) model for the AI features. No cloud account is needed.

## Features

### Application planning
| Screen | What it does |
|---|---|
| Today | Day schedule (routine blocks, habits, reminders), tasks to work on, what is coming up, today's GRE class |
| Upcoming | Key dates, programme deadlines, planned submits and task due dates by month |
| Tasks | Common and per-programme tasks: status, notes, due dates, your own tasks |
| Programmes | Planned submit dates, status, requirements (GRE/GMAT, English, fees, living costs) |
| Habits & schedule | Weekly tick grid; edit habit days/times; routine blocks |
| Reminders | One-off or repeating pop-ups |
| Assistant | Chat with the local Ollama model, using your tracker as context |
| Settings | Reminder times, Ollama model, Excel sync |

### GRE Prep (100-day plan)
- **Daily class, run like tuition:** a guided "Today's session" (warm-up → study notes → tutor → solve sums → vocab → quiz → end-of-day review), with time left and a *Done – next step* button on every step.
- **Study notes:** 56 original topic notes (quant, verbal, writing, strategy) with rule boxes, step-by-step worked examples, traps and self-checks; revision sheets on review days; printable / save-as-PDF pages.
- **Quant and Verbal courses:** lessons (concept → worked example → your turn), chapter and unit tests, GRE-timed section simulations with section-adaptive difficulty, weak-spot drills. Quant questions are generated with fresh numbers every time; verbal uses a bank of original questions (text completion, sentence equivalence, reading, critical reasoning).
- **Daily quiz in GRE format:** timed Quant and Verbal sections on the day's topics and vocabulary, Mark & Review, review screen, on-screen GRE calculator.
- **Full practice test in the app:** Issue essay + four sections with real timing and adaptive second sections; estimated scores.
- **Vocabulary:** 37 GregMat groups with spaced repetition (Leitner boxes), pronunciation, AI-written GRE-style sentence questions, a **missed-words queue** (morning warm-up; 5 correct answers clear a word), an **end-of-day review** of the day's misses, and a daily new-word budget that shrinks when the queue grows.
- **Formula & rule cards:** every rule box in the notes as a spaced-repetition card.
- **Progress:** score predictor (Rasch-style ability estimate), pacing by chapter, weekly report (and a Sunday notification), smart revision built from your own mistakes.
- **Error log:** mistakes from tests, quizzes and practice (✗ on any Magoosh question) with categories and a 7-day redo schedule.
- **Test results from screenshots:** Windows' built-in OCR + the local model read a score report; results feed the predictor, weak topics and Error log.
- **Essays:** 30-minute timer and AI feedback against the ETS Issue rubric.
- **Phone over Wi-Fi (opt-in):** flashcards, warm-up and end-of-day review on your phone via a token-protected link and QR code.
- **"Report a problem"** on any question hides it from future tests.
- **Backups:** daily SQLite backups (14 kept), optionally copied to OneDrive.

## Run from source
Requirements: Windows 10/11, Python 3.11, optionally Ollama with `llama3.1:8b` for the AI features.

```bat
python -m venv .venv
.venv\Scripts\pip install flask pywebview pystray pillow winotify openpyxl segno pyinstaller
.venv\Scripts\python main.py
```

Build and install the desktop app (Start Menu + Desktop shortcut): run `build_and_install.bat`.
Your data lives in `%LOCALAPPDATA%\MastersTracker\data` and is kept when you reinstall.

### Your GRE Drive folder (optional)
`tracker/gre_resources.py` is an index of a private Google Drive folder (Magoosh videos and practice questions, books)
and is **not** in this repository. Without it everything works except those Drive links. To add your own folder, create
`tracker/gre_resources.py` following `tracker/gre_resources_example.py`.

## Code map
| Path | What |
|---|---|
| `main.py` | Window, tray icon, startup backup, background loop |
| `tracker/server.py` | Flask API and static UI |
| `tracker/db.py`, `engine.py`, `notify.py` | SQLite storage + backups, schedules and reminders, Windows toasts |
| `tracker/gre.py` | GRE logic: schedule, quizzes, vocab queue, error log, courses, predictor, reports, mock tests |
| `tracker/gre_plan.py` | The 100-day plan (each day's notes, videos, practice, quizzes, course items) |
| `tracker/gre_course.py`, `gre_verbal.py` | Quant generators + lessons, verbal question bank + lessons |
| `tracker/gre_notes*.py` | Study notes and revision sheets |
| `tracker/gre_vocab.py`, `vocab_ctx.py` | GregMat word list; AI-written vocabulary sentences |
| `tracker/results.py`, `ocr.ps1` | Test results from screenshots (Windows OCR) |
| `tracker/mobile.py` | Opt-in phone page over Wi-Fi |
| `tracker/static/` | Front end (vanilla JS + CSS) |
