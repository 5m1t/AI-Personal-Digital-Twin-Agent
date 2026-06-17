import os
import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

# Set up ADK Runner and Services
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.genai import types

from app.database import DatabaseRepository
from app.graphs.twin_workflow import twin_workflow

# Ensure database is initialized
db = DatabaseRepository()

# Instantiate Session & Memory Services
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

# Verify GEMINI_API_KEY is present
if not os.getenv("GEMINI_API_KEY"):
    print("WARNING: GEMINI_API_KEY environment variable is not set! LLM calls will fail.")

# Initialize ADK Runner
runner = Runner(
    app_name="DigitalTwinAI",
    agent=twin_workflow,
    session_service=session_service,
    memory_service=memory_service,
    auto_create_session=True
)

app = FastAPI(title="Digital Twin AI Operating System")

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Schemes
class ChatRequest(BaseModel):
    message: str
    session_id: str

class GoalCreate(BaseModel):
    title: str
    description: str = ""
    category: str = "personal"
    target_date: str = ""

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    goal_id: Optional[int] = None
    due_date: str = ""
    priority: str = "medium"

class WellnessLog(BaseModel):
    sleep_hours: float
    exercise_minutes: int
    calories_burned: int = 0
    mood: str = "good"
    habits: List[str] = []

class TransactionLog(BaseModel):
    amount: float
    type: str # 'expense' or 'income'
    category: str
    description: str = ""

# --- API Endpoints ---

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """Feeds the user's message to the ADK Agent Workflow and returns the twin's text response."""
    user_message = types.Content(
        parts=[types.Part(text=req.message)]
    )
    
    try:
        reply = ""
        # Execute the multi-agent workflow graph asynchronously
        async for event in runner._run_node_async(
            user_id="default_user",
            session_id=req.session_id,
            new_message=user_message
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        reply += part.text
                        
        if not reply:
            reply = "Workflow completed, but no direct text reply was emitted."
            
        return {"response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent workflow error: {str(e)}")

@app.get("/api/dashboard")
def get_dashboard_data():
    """Aggregates and returns all digital twin metrics for the dashboard view."""
    return {
        "profile": db.get_profile(),
        "goals": db.list_goals(),
        "tasks": db.list_tasks(),
        "calendar": db.list_calendar_events(),
        "learning": db.list_learning_plans(),
        "wellness": db.list_wellness_logs(limit=7),
        "finances": db.list_finance_logs()[:10], # Top 10 transactions
        "skills": db.list_career_skills()
    }

@app.get("/api/briefing")
async def get_daily_briefing():
    """Triggers the Executive Assistant agent to compile a comprehensive Daily Briefing."""
    today = datetime.date.today().isoformat()
    
    # 1. Fetch context data from database
    goals = db.list_goals()
    tasks = db.list_tasks()
    calendar = db.list_calendar_events()
    wellness = db.list_wellness_logs(limit=3)
    
    # Filter today's items
    todays_tasks = [t for t in tasks if t['status'] != 'done' and t['due_date'] == today]
    todays_events = [e for e in calendar if e['start_time'].startswith(today)]
    
    # 2. Build the context prompt
    context_prompt = (
        f"Generate my Daily Briefing for today ({today}).\n"
        f"Here is the context of my current metrics:\n"
        f"- Today's Calendar Events: {todays_events}\n"
        f"- Today's Priorities / Deadlines: {[t['title'] for t in todays_tasks]}\n"
        f"- Goal status summary: {[{g['title']: f'{g['progress']}% progress'} for g in goals]}\n"
        f"- Recent Wellness metrics: {wellness}\n\n"
        "Draft a structured executive briefing detailing priorities, schedules, learning summaries, wellness insights, and suggested actions. Be encouraging and highly structured."
    )
    
    user_message = types.Content(
        parts=[types.Part(text=context_prompt)]
    )
    
    try:
        briefing = ""
        # Run orchestrator directly to compile briefing
        async for event in runner._run_node_async(
            user_id="default_user",
            session_id=f"briefing_{today}",
            new_message=user_message
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        briefing += part.text
        return {"briefing": briefing}
    except Exception as e:
        return {"briefing": f"Could not generate briefing due to model error: {str(e)}. Please set your GEMINI_API_KEY."}

@app.post("/api/reflect")
async def trigger_weekly_reflection():
    """Weekly Reflection Engine: Analyzes productivity, learning, and wellness, and flags inefficiencies."""
    today = datetime.date.today()
    last_week = (today - datetime.timedelta(days=7)).isoformat()
    
    # Fetch logs
    tasks = db.list_tasks()
    wellness = db.list_wellness_logs(limit=7)
    finances = db.list_finance_logs()
    
    completed_tasks = [t for t in tasks if t['status'] == 'done']
    pending_tasks = [t for t in tasks if t['status'] != 'done']
    
    context_prompt = (
        "Run the Weekly Reflection analysis.\n"
        f"- Tasks Completed in last 7 days: {len(completed_tasks)}\n"
        f"- Pending / Overdue Tasks: {[t['title'] for t in pending_tasks]}\n"
        f"- Wellness sleep & exercise log: {[{w['date']: f'{w['sleep_hours']}h sleep, {w['exercise_minutes']}m exercise'} for w in wellness]}\n"
        "- Inefficiencies to analyze: Check sleep schedules and completed vs planned milestones.\n\n"
        "Generate a structured Weekly Reflection Report outlining productivity analysis, wellness patterns, inefficiencies detected, and an actionable optimization plan."
    )
    
    user_message = types.Content(
        parts=[types.Part(text=context_prompt)]
    )
    
    try:
        report = ""
        async for event in runner._run_node_async(
            user_id="default_user",
            session_id=f"reflection_{today.isoformat()}",
            new_message=user_message
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        report += part.text
                        
        # Save report as a custom artifact/record
        from app.tools.research_tools import compile_research_report
        compile_research_report(f"Weekly_Reflection_{today.isoformat()}", report)
        
        return {"reflection": report}
    except Exception as e:
        return {"reflection": f"Could not generate reflection due to error: {str(e)}"}

# --- Form Inputs ---

@app.post("/api/goals")
def create_goal_endpoint(g: GoalCreate):
    goal_id = db.add_goal(g.title, g.description, g.category, g.target_date)
    return {"status": "success", "goal_id": goal_id}

@app.post("/api/tasks")
def create_task_endpoint(t: TaskCreate):
    task_id = db.add_task(t.title, t.description, t.goal_id, t.due_date, t.priority)
    return {"status": "success", "task_id": task_id}

@app.post("/api/wellness")
def log_wellness_endpoint(w: WellnessLog):
    today = datetime.date.today().isoformat()
    db.log_wellness(today, w.sleep_hours, w.exercise_minutes, w.calories_burned, w.mood, w.habits)
    return {"status": "success"}

@app.post("/api/finances")
def log_finance_endpoint(f: TransactionLog):
    today = datetime.date.today().isoformat()
    log_id = db.add_finance_log(today, f.category, f.amount, f.type, f.description)
    return {"status": "success", "log_id": log_id}

# --- Serve Static UI ---

@app.get("/", response_class=HTMLResponse)
def serve_index():
    with open(os.path.join("app", "ui", "templates", "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# Mount static assets directory
app.mount("/static", StaticFiles(directory=os.path.join("app", "ui", "static")), name="static")

if __name__ == "__main__":
    import uvicorn
    # Pre-populate sample values if empty
    goals = db.list_goals()
    if not goals:
        g1 = db.add_goal("Certify in AWS Certified Developer", "Prepare and pass the DVA-C02 certification exam", "career", "2026-08-15")
        db.add_task("Read AWS DVA Chapter 1 & 2", "Core compute and networking", g1, "2026-06-20", "high")
        db.add_task("Build Serverless API prototype", "Use Lambda, API Gateway, DynamoDB", g1, "2026-06-25", "medium")
        
        g2 = db.add_goal("Establish Healthy Sleep Habits", "Achieve 8 hours of sleep consistently and wake up refreshed", "wellness", "2026-07-31")
        db.add_task("No screens after 10 PM", "Turn off phone and laptop, read paper book", g2, "2026-06-18", "high")
        db.add_task("Morning stretching routine", "5 minutes of yoga stretching right after waking up", g2, "2026-06-19", "low")

        db.add_calendar_event("Sprint Planning Review", "Review digital twin goals and task boards", "2026-06-18T10:00:00", "2026-06-18T11:00:00")
        db.add_calendar_event("AI Architecture Align", "Deep dive into ADK multi-agent structures", "2026-06-19T14:30:00", "2026-06-19T16:00:00")
        
        db.add_learning_plan("Rust Ecosystem", "Rust programming language and async towers", "active", 15, "https://doc.rust-lang.org/book/")
        db.add_career_skill("Rust", "beginner", "Rust Foundation Associate", ["Read Rust Book", "Build CLI Tool", "Build Async Web App"])
        
        db.log_wellness("2026-06-16", 7.2, 25, 180, "rested", ["Drink 3L Water"])
        db.log_wellness("2026-06-15", 6.5, 45, 300, "energetic", ["Drink 3L Water", "Exercise 30m"])
        
        db.add_finance_log("2026-06-16", "food", 25.40, "expense", "Lunch at Cafe")
        db.add_finance_log("2026-06-15", "subscriptions", 15.00, "expense", "Digital Twin AI hosting")
        db.add_finance_log("2026-06-14", "salary", 2500.00, "income", "Monthly paycheck")
        
    uvicorn.run(app, host="127.0.0.1", port=8000)
