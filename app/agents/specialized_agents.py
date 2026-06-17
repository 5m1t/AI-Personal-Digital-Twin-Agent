from google.adk import Agent
from google.adk.tools import ToolContext
from .. import tools

# Unified tool to handle routing back to orchestrator in workflow graph
def finish_task_and_route_back(tool_context: ToolContext) -> str:
    """Finishes the specialized agent's current task and routes execution control back to the Executive Assistant orchestrator. 
    Call this when you have successfully addressed the user request.
    """
    tool_context.route = "orchestrator"
    return "Task complete. Routing back to Executive Assistant."

# Model definition (Gemini 2.5 Flash is selected)
MODEL_NAME = "gemini-2.5-flash"

memory_agent = Agent(
    name="MemoryAgent",
    model=MODEL_NAME,
    instruction=(
        "You are the Memory Agent of the user's Digital Twin system.\n"
        "Your role is to maintain the long-term user profile, interests, habits, goals context, "
        "and retrieve or summarize relevant memories. You have tools to write new facts "
        "into the memory bank and search existing ones. When you have finished writing or "
        "searching memories to answer the user's request, call `finish_task_and_route_back`."
    ),
    tools=[
        tools.search_memory_bank,
        tools.record_new_memory,
        finish_task_and_route_back
    ]
)

learning_coach_agent = Agent(
    name="LearningCoachAgent",
    model=MODEL_NAME,
    instruction=(
        "You are the Learning Coach Agent.\n"
        "You create personalized learning plans, monitor progress, recommend resources, and generate quizzes. "
        "Use your study plan and quiz tools to maintain study pathways. Once you have set up a plan, "
        "generated a quiz, or updated progress, call `finish_task_and_route_back`."
    ),
    tools=[
        tools.create_study_plan,
        tools.add_quiz_question,
        tools.get_study_plans_summary,
        tools.update_study_progress,
        finish_task_and_route_back
    ]
)

research_agent = Agent(
    name="ResearchAgent",
    model=MODEL_NAME,
    instruction=(
        "You are the Research Agent.\n"
        "Your job is to conduct web research, summarize information, compare alternatives, "
        "and compile structured reports. Use `perform_web_search` to find data and "
        "`compile_research_report` to save reports. Call `finish_task_and_route_back` when done."
    ),
    tools=[
        tools.perform_web_search,
        tools.compile_research_report,
        finish_task_and_route_back
    ]
)

productivity_agent = Agent(
    name="ProductivityAgent",
    model=MODEL_NAME,
    instruction=(
        "You are the Productivity Agent.\n"
        "You manage projects, break goals into milestones, generate action plans, monitor progress, "
        "and detect bottlenecks. Use goal and task management tools to keep the user's DB updated. "
        "Call `finish_task_and_route_back` once goals or tasks are reviewed/updated."
    ),
    tools=[
        tools.create_new_goal,
        tools.add_task_to_goal,
        tools.get_goals_and_tasks_summary,
        tools.update_task_state,
        tools.update_goal_state,
        tools.analyze_productivity_bottlenecks,
        finish_task_and_route_back
    ]
)

communication_agent = Agent(
    name="CommunicationAgent",
    model=MODEL_NAME,
    instruction=(
        "You are the Communication Agent.\n"
        "Your role is to draft emails, draft messages, summarize conversations, create meeting notes, "
        "and list follow-up actions. Use `draft_email_message`, `format_meeting_notes`, and "
        "`list_drafts_summary`. Call `finish_task_and_route_back` when your draft or summary is stored."
    ),
    tools=[
        tools.draft_email_message,
        tools.format_meeting_notes,
        tools.list_drafts_summary,
        finish_task_and_route_back
    ]
)

finance_agent = Agent(
    name="FinanceAgent",
    model=MODEL_NAME,
    instruction=(
        "You are the Finance Agent.\n"
        "You track expenses, analyze spending, suggest savings opportunities, and compile reports. "
        "Use transaction log tools to add items and get budgeting reports. Call `finish_task_and_route_back` when done."
    ),
    tools=[
        tools.log_transaction,
        tools.get_financial_report,
        finish_task_and_route_back
    ]
)

wellness_agent = Agent(
    name="WellnessAgent",
    model=MODEL_NAME,
    instruction=(
        "You are the Wellness Agent.\n"
        "You track sleep, exercise, routines, suggest healthy habits, and compile reports. "
        "Use `log_daily_wellness` and `get_wellness_report` to maintain wellness logs. "
        "Call `finish_task_and_route_back` when done."
    ),
    tools=[
        tools.log_daily_wellness,
        tools.get_wellness_report,
        finish_task_and_route_back
    ]
)

career_growth_agent = Agent(
    name="CareerGrowthAgent",
    model=MODEL_NAME,
    instruction=(
        "You are the Career Growth Agent.\n"
        "You track professional skills, certifications, suggest training, and build career roadmaps. "
        "Use `add_career_skill_entry` and `list_career_roadmap_summary` to update the profile. "
        "Call `finish_task_and_route_back` when portfolio roadmaps are complete."
    ),
    tools=[
        tools.add_career_skill_entry,
        tools.list_career_roadmap_summary,
        finish_task_and_route_back
    ]
)
