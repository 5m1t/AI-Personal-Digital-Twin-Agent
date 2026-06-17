from google.adk.tools import ToolContext
from google.genai import types

async def search_memory_bank(query: str, tool_context: ToolContext) -> str:
    """Searches the digital twin's long-term memory bank for relevant context about the user's habits, history, preferences, and goals.
    
    Args:
        query: The search term or question about the user (e.g. 'what are my coding preferences?', 'where did I study?').
    """
    try:
        results = await tool_context.search_memory(query)
        if not results.memories:
            return "No matching memories found in the long-term bank."
        
        formatted = []
        for idx, m in enumerate(results.memories):
            text = " ".join([part.text for part in m.content.parts if part.text])
            timestamp = m.timestamp or "Unknown time"
            author = m.author or "system"
            formatted.append(f"[{idx+1}] ({timestamp}) {author}: {text}")
            
        return "\n".join(formatted)
    except Exception as e:
        return f"Error searching memory: {str(e)}"

async def record_new_memory(memory_text: str, tool_context: ToolContext) -> str:
    """Saves a new fact, preference, goal, or episodic event permanently in the user's digital twin memory bank.
    
    Args:
        memory_text: The statement or detail to remember (e.g. 'User prefers meetings after 10 AM', 'User finished their certification in AWS Cloud Practitioner').
    """
    try:
        content = types.Content(
            parts=[types.Part(text=memory_text)]
        )
        from google.adk.events.event import Event
        event = Event(
            invocation_id="inv_mem",
            author="Digital Twin Agent",
            content=content
        )
        await tool_context.add_events_to_memory(events=[event])
        return f"Successfully saved to long-term memory: '{memory_text}'"
    except Exception as e:
        return f"Error writing to memory: {str(e)}"
