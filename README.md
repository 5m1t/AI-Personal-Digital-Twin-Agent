# Digital Twin AI - Personal OS Dashboard

Digital Twin AI is a production-grade, multi-agent AI personal operating system built using **Google ADK 2.0**. It acts as an autonomous digital representation of a user, tracking their goals, habits, work style, wellness, finances, schedule, and career skills.

## Architectural Overview

The system uses a graph-based multi-agent architecture where the user interacts with a single orchestrator (`ExecutiveAssistantAgent`) which routes tasks to 8 specialized sub-agents:

```
                  [ START ]
                      │
           [ ExecutiveAssistantAgent ] ─── (directly handles basic queries)
                      │
      ┌───────────────┼───────────────┬───────────────┐
  (wellness)      (finance)     (learning)       (career) ... etc (conditional)
      │               │               │               │
  [Wellness]      [Finance]      [Learning]       [Career]
      │               │               │               │
      └───────────────┴───────────────┴───────────────┘
                      │
           (route back unconditionally)
                      │
           [ ExecutiveAssistantAgent ] ─── (replies to user)
```

### Specialized Agents
1.  **Executive Assistant Agent**: Understands user requests, prioritizes tasks, manages schedules, coordinates specialized agents, and generates daily briefings.
2.  **Memory Agent**: Maintains long-term user profile, stores preferences, habits, goals context, and recalls memories.
3.  **Learning Coach Agent**: Creates study tracks, logs progress, recommends resources, and generates quizzes.
4.  **Research Agent**: Conducts web research, summarizes documents, and compiles markdown reports.
5.  **Productivity Agent**: Manages goals, breaks them into milestones/tasks, and detects project bottlenecks.
6.  **Communication Agent**: Drafts emails/messages, structures meeting notes, and extracts action items.
7.  **Finance Agent**: Tracks expenses, analyzes budgets, and outputs monthly reports.
8.  **Wellness Agent**: Logs daily sleep hours, exercise, calories burned, mood, and checked habits.
9.  **Career Growth Agent**: Maps technical skills, certificates, and builds career roadmaps.

---

## Technical Stack & Configuration

*   **Core**: Python, google-adk 2.2.0, FastAPI, Uvicorn, SQLite3.
*   **Frontend**: HTML5, Vanilla JavaScript, Vanilla CSS (harmonious dark glassmorphism design with radial gradients, Outfit typography, HSL variables, and smooth animations).

---

## Database Schemas

The application persists user state to a local SQLite database (`digital_twin.db`). It contains the following tables:
*   `user_profile`: Key-value storage for work style, preferences, and long-term goals.
*   `goals`: Long-term targets showing categories, completion dates, and overall progress.
*   `tasks`: Detailed checklists with priority tags and goal associations.
*   `calendar_events`: Planned schedule timelines.
*   `learning_plans`: Study curricula with topics and active links.
*   `quizzes`: Multiple-choice questions for knowledge verification.
*   `wellness_logs`: Sleep, exercise, active calories, and habits logged per date.
*   `finance_logs`: Budget records (income/expenses) categorized.
*   `career_skills`: Skills, proficiencies, and targeted certifications.

---

## Installation & Setup

1.  **Clone the project** and open a terminal in the folder.
2.  **Create a virtual environment** (already created in the workspace):
    ```bash
    uv venv
    .venv\Scripts\activate
    ```
3.  **Install dependencies**:
    ```bash
    uv pip install -e .
    ```
4.  **Configure Environment**:
    Rename `.env.template` to `.env` and fill in your Gemini API key:
    ```env
    GEMINI_API_KEY=AIzaSy...
    ```

---

## Running the Web Application

To launch the web dashboard:
```bash
.venv\Scripts\python main.py
```
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

### Dashboard Features
*   **AI Chat**: Real-time dialogue with the Twin Orchestrator. Specialized tasks (e.g. logging wellness, adding goals, or drafting emails) are routed automatically to sub-agents.
*   **Briefing Block**: Click "Get Daily Briefing" to compile a breakdown of today's events, priorities, and health tips.
*   **Goals & Tasks Tab**: Interactive tasks list. Clicking checkmarks updates their status directly in the database.
*   **Wellness & Finance Tab**: Logging modal forms automatically updates the visual dials, metrics cards, and transaction history.
*   **Weekly Reflection**: Click the "Trigger Weekly Reflection" button to compile a reflection report identifying study/sleep inefficiencies and generating an optimization plan.

---

## Running the Evaluation Matrix

An automated test suite computes scores for semantic memory accuracy, orchestrator routing precision, and goal decomposition metrics:
```bash
# In powershell (sets python path and utf-8 encoding for unicode emoji prints)
$env:PYTHONIOENCODING="utf-8"; $env:PYTHONPATH="."; .venv\Scripts\python app/evaluation/eval_framework.py
```
**Expected Scores**:
*   Memory Accuracy Rate: 100.0%
*   Orchestrator Routing Accuracy: 100.0%
*   Planning Effectiveness: 100.0%
