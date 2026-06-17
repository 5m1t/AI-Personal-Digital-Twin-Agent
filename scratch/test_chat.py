import asyncio
import os
from dotenv import load_dotenv
from google.genai import types
from main import runner

load_dotenv()

async def test():
    print("API Key set:", bool(os.getenv("GEMINI_API_KEY")))
    user_message = types.Content(parts=[types.Part(text="Hello, who are you?")])
    try:
        async for event in runner._run_node_async(
            user_id="default_user",
            session_id="test_session_1",
            new_message=user_message
        ):
            print("Event author:", event.author)
            if event.content and event.content.parts:
                text = "".join([p.text for p in event.content.parts if p.text])
                print("Text content:", text)
    except Exception:
        import traceback
        traceback.print_exc()

asyncio.run(test())
