from google.adk import Agent
from google.adk.tools import ToolContext

# Model definition (Gemini 2.5 Flash is selected)
MODEL_NAME = "gemini-2.5-flash"

def route_to_specialist(agent_name: str, tool_context: ToolContext) -> str:
    """Routes the user's request to the specialized agent best suited to handle it.
    
    Args:
        agent_name: The name of the agent to route to. Allowed values:
          - 'memory' (for long term profiles, preferences, recording memories)
          - 'learning' (for quizzes, learning plans, progress tracking)
          - 'research' (for web searches, report compilation, validations)
          - 'productivity' (for goals, milestones, tasks)
          - 'communication' (for email drafts, meeting notes summaries)
          - 'finance' (for expense logging, financial reports, budgeting)
          - 'wellness' (for sleep tracking, exercise logs, daily routines)
          - 'career' (for skills tracking, certifications, job portfolios)
    """
    tool_context.route = agent_name
    return f"Routing request to the {agent_name} agent."

executive_assistant_agent = Agent(
    name="ExecutiveAssistantAgent",
    model=MODEL_NAME,
    instruction=(
        "You are the Executive Assistant Agent, the central AI Chief of Staff and Orchestrator "
        "of the user's Digital Twin system.\n"
        "Your job is to understand the user request, determine if it requires specialized handling, "
        "and route it using the `route_to_specialist` tool. If the user request is a general greeting "
        "or doesn't require a specialist, respond directly to the user and do NOT call the tool.\n\n"
        "Available specialists:\n"
        "- 'memory': profile, habits, preferences, memories.\n"
        "- 'learning': learning plans, recommend resources, quizzes.\n"
        "- 'research': web research, reports, facts.\n"
        "- 'productivity': project management, goals, tasks, milestones.\n"
        "- 'communication': draft emails/messages, meeting summaries.\n"
        "- 'finance': expenses, budgets, savings.\n"
        "- 'wellness': sleep logs, exercise, routines.\n"
        "- 'career': professional skills, certifications, roadmaps."
    ),
    tools=[route_to_specialist]
)
