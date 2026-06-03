# Levina Language Model Backend

A Django REST API that powers an educational platform for Russian language learning. Teachers create and assign structured exercises (multiple-choice questions, free-response questions, and AI-driven dialogues) to students enrolled in courses. The system supports both asynchronous assignments and live classroom sessions hosted in real time.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Data Model](#data-model)
- [Authentication](#authentication)
- [API Reference](#api-reference)
- [Proof of Concepts](#proof-of-concepts)
- [Setup & Running Locally](#setup--running-locally)
- [CI/CD](#cicd)

---

## Architecture Overview

The backend is organized into four Django apps plus a shared utilities module:

```
mysite/
├── core/           # Django project settings, URL root, permission classes
├── users/          # Custom user model, JWT auth, password reset
├── courses/        # Course creation, enrollment, join-code management
├── assignments/    # Assignment templates, course assignments, student instances, live sessions
├── questions/      # Questions (MCQ/FRQ), dialogues, per-student response tracking
└── utils/          # Bulk-creation helpers shared across apps
```

**Request lifecycle:**
1. Client sends a JWT in the `Authorization: Bearer <token>` header.
2. DRF's `JWTAuthentication` validates the token and populates `request.user`.
3. A role-based permission class (`IsTeacher`, `IsStudent`, etc.) in `core/permissions.py` checks the user's `user_type` field.
4. The relevant `ViewSet` in the appropriate app handles the request.
5. Serializers validate and serialize data; bulk-creation helpers in `utils/create.py` handle cascading object creation.

---

## Data Model

### Users

| Field | Notes |
|---|---|
| `email` | Login identifier (no username) |
| `user_type` | `0` Student · `1` Teacher · `2` Admin · `3` Superuser |
| `PasswordResetCode` | 6-digit code, expires 10 minutes after creation |

### Courses

A `Course` links one or more teachers to many students. Students join via a randomly generated 6-character alphanumeric join code that can be refreshed at any time.

Class type choices: Freshman Russian, Sophomore Russian, Junior Russian, College Russian, Heritage (all levels), Business Russian.

### Assignment Hierarchy

```
AssignmentTemplate          ← reusable blueprint created by a teacher
    └── Assignment          ← template assigned to a specific course with a due date
            └── AssignmentInstance   ← one per enrolled student, tracks submission & time used
                    ├── QuestionInstance     ← student's answer to each question
                    └── DialogueInstance     ← student's back-and-forth dialogue thread
                            └── DialogueStatement (AI or STUDENT, audio file)
```

When `assign_assignment()` runs, it creates the full cascade in a single transaction using `bulk_create()` for efficiency — one `AssignmentInstance` per student, one `QuestionInstance` per (student × question), one `DialogueInstance` per (student × dialogue), plus an initial AI `DialogueStatement` seeded from the dialogue's `initial_statement` audio file.

### Sessions (Live Classroom)

```
Session                     ← teacher hosts, has a 6-character access code, can be ended
    └── SessionInstance     ← one per student who joins, holds a SHA-256 auth token
            ├── SessionQuestionInstance   ← student's answer during the live session
            └── SessionDialogueInstance  ← live dialogue thread (text-based, not audio)
                    └── SessionDialogueStatement (AI or STUDENT)
```

Sessions are anonymous by default — students join with just a display name, no account required.

### Questions

| Field | Notes |
|---|---|
| `question_type` | `MCQ` or `FRQ` |
| `question_content_type` | `TEXT` or `AUDIO` |
| `answer_content_type` | `TEXT` or `AUDIO` |
| `false_answers` | JSON array of wrong choices (MCQ only) |
| `text_answer` | Correct answer text |
| `audio_question` / `audio_answer` | File uploads stored under `media/audio/` |

Questions are many-to-many with both `AssignmentTemplate` and `Assignment`, so the same question bank can be reused across courses and semesters.

### Dialogues

A `Dialogue` defines a conversation framework: an `initial_statement` (audio file from the AI), a `description`, and a `max_statements` cap. Each student gets their own `DialogueInstance` which accumulates `DialogueStatement` records alternating between `STUDENT` and `AI` authors.

---

## Authentication

JWT tokens are issued by SimpleJWT.

```
POST /api/token/            body: { email, password }  → { access, refresh }
POST /api/token/refresh/    body: { refresh }           → { access }
```

Token lifetimes: access = 1 hour, refresh = 1 day.

**Password reset flow:**
1. `POST /password-reset/` with `{ email }` — sends a 6-digit code to the user's inbox.
2. `POST /password-reset/confirm/` with `{ email, code, new_password }` — validates the code (must be < 10 minutes old) and sets the new password.

**Role-based permissions** (`core/permissions.py`):

| Class | Who passes |
|---|---|
| `IsStudent` | `user_type >= 0` |
| `IsTeacher` | `user_type >= 1` |
| `IsAdmin` | `user_type >= 2` |
| `IsTeacherAndOwnsObject` | Teacher + created the object |
| `IsStudentAndOwnsObject` | Student + owns the instance |
| `IsStudentAndIsInCourse` | Student + enrolled in the relevant course |
| `IsStudentAndOwnsAssignmentInstance` | Student + owns that specific assignment instance |

---

## API Reference

Interactive docs are served at runtime:

- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

### Courses

| Method | Endpoint | Who | Description |
|---|---|---|---|
| GET/POST | `/courses/` | Teacher | List or create courses |
| GET/PATCH/DELETE | `/courses/{id}/` | Teacher | Retrieve, update, or delete a course |
| POST | `/courses/{id}/join/` | Student | Join using a join code |
| POST | `/courses/{id}/generate_join_code/` | Teacher | Issue a new join code |
| GET | `/courses/{id}/assignments/` | Teacher/Student | List assignments for a course |
| GET | `/courses/{id}/students/` | Teacher | List enrolled students |

### Assignment Templates

| Method | Endpoint | Who | Description |
|---|---|---|---|
| GET/POST | `/assignment-templates/` | Teacher | List or create templates |
| GET/PATCH/DELETE | `/assignment-templates/{id}/` | Teacher | Manage a template |
| POST | `/assignment-templates/{id}/assign/` | Teacher | Push template to a course as a live assignment |

### Assignments

| Method | Endpoint | Who | Description |
|---|---|---|---|
| GET/POST | `/assignments/` | Teacher | List or create assignments |
| GET/PATCH/DELETE | `/assignments/{id}/` | Teacher | Manage an assignment |

### Assignment Instances (student work)

| Method | Endpoint | Who | Description |
|---|---|---|---|
| GET | `/assignment-instances/` | Student | List own instances |
| GET | `/assignment-instances/{id}/` | Student | View instance detail |
| POST | `/assignment-instances/{id}/submit/` | Student | Mark as submitted |
| POST | `/assignment-instances/{id}/increment_time_used/` | Student | Record elapsed time |

### Questions

| Method | Endpoint | Who | Description |
|---|---|---|---|
| GET/POST | `/questions/` | Teacher | Create or list questions |
| GET/PATCH/DELETE | `/questions/{id}/` | Teacher | Manage a question |
| GET/PATCH | `/question-instances/{id}/` | Student | View or answer a question |

### Dialogues

| Method | Endpoint | Who | Description |
|---|---|---|---|
| GET/POST | `/dialogues/` | Teacher | Create or list dialogues |
| GET | `/dialogue-instances/{id}/` | Student | View dialogue + statement history |
| POST | `/dialogue-instances/{id}/add_statement/` | Student | Submit a student turn; triggers AI response |

### Sessions

| Method | Endpoint | Who | Description |
|---|---|---|---|
| POST | `/sessions/host_session/` | Teacher | Create and start a session |
| POST | `/sessions/join_session/` | Anyone | Join with access code + display name |
| POST | `/sessions/{id}/end_session/` | Teacher | Close the session |
| GET | `/session-instances/{id}/` | Student | View own session instance |
| PATCH | `/session-question-instances/{id}/` | Student | Update a live answer |
| POST | `/session-dialogue-instances/{id}/add_statement/` | Student | Add to a live dialogue |

---

## Proof of Concepts

### 1. AI Dialogue Response Generation

**Current state:** `add_statement()` in `questions/views.py` saves the student's turn but generates a placeholder AI response (`"AI response to: {user_text}"`). No real language model is called.

**What the wiring already provides:**
- A `Dialogue` has a `max_statements` cap — the turn-taking loop is already enforced.
- `DialogueStatement` records are ordered by `created_at`, so the full conversation history is easily retrieved in order.
- The assignment dialogue uses audio files; the session dialogue uses text — both paths exist.

**How to complete it:**

For **session dialogues** (text-based), the simplest integration is a synchronous call to the Claude API before saving the AI statement:

```python
import anthropic

client = anthropic.Anthropic()

def generate_ai_response(dialogue_description: str, history: list[dict], student_turn: str) -> str:
    system = (
        f"You are a Russian language tutor facilitating a conversation. "
        f"Context: {dialogue_description}. "
        "Respond naturally in Russian, then provide a brief English translation in parentheses. "
        "Keep responses concise and appropriate for the student's level."
    )
    messages = history + [{"role": "user", "content": student_turn}]
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=300,
        system=system,
        messages=messages,
    )
    return response.content[0].text
```

The `history` list is built by iterating the existing `SessionDialogueStatement` records:

```python
history = [
    {"role": "user" if s.author == "STUDENT" else "assistant", "content": s.text}
    for s in instance.statements.all()
]
```

For **assignment dialogues** (audio-based), the flow adds a TTS step after generating the text response. The resulting audio file is saved as the `DialogueStatement.audio` field. Anthropic currently does not offer TTS; this would require a separate service (e.g., ElevenLabs, Google TTS) converting the generated Russian text to an MP4/WAV file.

**Tradeoff:** Synchronous API calls block the request for ~1–3 seconds. If that's unacceptable, the AI call can be offloaded to a Celery task, with the client polling a `GET` endpoint for the AI statement instead of receiving it in the same response.

---

### 2. Answer Evaluation / Auto-Grading

**Current state:** Student answers are stored in `QuestionInstance.text_answer` / `audio_answer` and `QuestionInstance.submitted`, but nothing evaluates them.

**What needs to be added:**
- A `score` or `feedback` field on `QuestionInstance`.
- A grading endpoint or a post-submit signal.

**MCQ auto-grade** is trivial — compare `QuestionInstance.text_answer` to `Question.text_answer` (case-insensitive). This can run synchronously in the `submit` action.

**FRQ auto-grade** is where a language model adds value. After a student submits, send the question prompt, the correct answer, and the student's response to Claude and ask for a score (0–100) plus a correction note in Russian:

```python
def grade_frq(question: Question, student_answer: str) -> dict:
    prompt = (
        f"Russian language question: {question.text_question}\n"
        f"Model answer: {question.text_answer}\n"
        f"Student's answer: {student_answer}\n\n"
        "Score the student's answer from 0 to 100 based on accuracy, grammar, and vocabulary. "
        "Return JSON: {\"score\": <int>, \"feedback\": \"<feedback in Russian with English translation>\"}"
    )
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(response.content[0].text)
```

**Audio FRQ grading** requires a transcription step first (e.g., OpenAI Whisper or Google Speech-to-Text) before the text can be evaluated.

---

### 3. Token Security Hardening for Sessions

**Current state:** Session tokens are `SHA256("token_{session_instance.id}")` — deterministic and predictable given the instance ID.

**What to change:**

```python
import secrets

token = secrets.token_hex(32)  # 64-char cryptographically random hex string
session_instance.token = token
```

This is a one-line change in `utils/create.py:join_session()`. The token is returned once to the client on join and never re-derivable, making it suitable as a bearer credential for subsequent session requests.

---

### 4. Student Joins Course After Assignment Is Live

**Current state:** `join_course()` in `utils/create.py` correctly back-fills `AssignmentInstance` and `QuestionInstance` records for any assignments already active in the course when the student joins. However, it does not back-fill `DialogueInstance` or the seeded initial `DialogueStatement` for those assignments.

**What needs to be added in `join_course()`:**

```python
for assignment in course.assignments.all():
    assignment_instance = AssignmentInstance.objects.create(...)
    # existing question back-fill ...

    dialogue_instances = [
        DialogueInstance(assignment_instance=assignment_instance, dialogue=dialogue)
        for dialogue in assignment.dialogues.all()
    ]
    DialogueInstance.objects.bulk_create(dialogue_instances)
    initial_statements = [
        DialogueStatement(
            dialogue_instance=di,
            audio=di.dialogue.initial_statement,
            author="AI",
        )
        for di in dialogue_instances
    ]
    DialogueStatement.objects.bulk_create(initial_statements)
```

This mirrors the logic already in `assign_assignment()` and ensures late-joining students see the same starting state as everyone else.

---

## Setup & Running Locally

**Requirements:** Python 3.11+

```bash
cd mysite
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Create a .env file in the repo root with:
# GMAIL_APP_PASSWORD=<your gmail app password>
# FRONTEND_URL=http://localhost:3000

python manage.py migrate
python manage.py runserver
```

The API is available at `http://localhost:8000`.  
Swagger UI: `http://localhost:8000/api/docs/`

**Initialize test data:**

```bash
python manage.py runscript init_db
```

**Reset the database:**

```bash
python manage.py runscript reset_db
```

---

## CI/CD

Two GitHub Actions workflows run on every push and pull request:

| Workflow | What it does |
|---|---|
| `django-tests.yml` | Runs Ruff linter/formatter, then `python manage.py test` |
| `git-secrets.yml` | Scans for accidentally committed secrets |

Ruff is configured in `pyproject.toml` targeting Python 3.11 with a 120-character line limit.
