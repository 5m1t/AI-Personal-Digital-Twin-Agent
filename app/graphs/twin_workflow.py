from google.adk import Workflow
from google.adk.workflow import START
from ..agents import (
    executive_assistant_agent,
    memory_agent,
    learning_coach_agent,
    research_agent,
    productivity_agent,
    communication_agent,
    finance_agent,
    wellness_agent,
    career_growth_agent,
)

twin_workflow = Workflow(
    name="DigitalTwinWorkflow",
    edges=[
        # Entry point to the Orchestrator
        (START, executive_assistant_agent),
        
        # Branching based on the route value returned by Orchestrator
        (executive_assistant_agent, {
            "memory": memory_agent,
            "learning": learning_coach_agent,
            "research": research_agent,
            "productivity": productivity_agent,
            "communication": communication_agent,
            "finance": finance_agent,
            "wellness": wellness_agent,
            "career": career_growth_agent,
        }),
        
        # Direct return paths from all specialized agents back to the Orchestrator
        (memory_agent, executive_assistant_agent),
        (learning_coach_agent, executive_assistant_agent),
        (research_agent, executive_assistant_agent),
        (productivity_agent, executive_assistant_agent),
        (communication_agent, executive_assistant_agent),
        (finance_agent, executive_assistant_agent),
        (wellness_agent, executive_assistant_agent),
        (career_growth_agent, executive_assistant_agent),
    ]
)
