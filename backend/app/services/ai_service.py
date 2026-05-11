import httpx
import os
import dotenv
from ollama import AsyncClient
from openrouter import OpenRouter

dotenv.load_dotenv(dotenv.find_dotenv(), override=True)

class AiService:
    def __init__(self):
        self.ollama_client = AsyncClient(
            host="https://ollama.com",
            headers={'Authorization': 'Bearer ' + str(os.getenv('OLLAMA_API_KEY'))}
        )
        self.local_ollama_client = AsyncClient(
            host="http://localhost:11434"
        )

    async def ask(self, text: str, model: str = None):
        is_testing = os.getenv("AI_TESTING", "false").lower() == "true"

        if is_testing:
            response = await self.ollama_client.chat(
                #diffrent model is used for testing
                model="gemma4:31b-cloud",
                messages=[
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            )
            return response["message"]["content"]
        else:
            # Note: OpenRouter class from 'openrouter' package might not be async-native.
            # If it blocks, we should use run_in_threadpool or a direct httpx async call.
            # Assuming OpenRouter is a wrapper around httpx, but let's check if there's an async way.
            # For now, if it's sync, we use run_in_threadpool to not block the loop.
            from fastapi.concurrency import run_in_threadpool
            
            def sync_ask():
                with OpenRouter(
                    api_key=os.getenv("OPENROUTER_API_KEY", ""),
                ) as client:
                    response = client.chat.send(
                        model=f"{"anthropic/claude-sonnet-4" if model == None else model}",
                        messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"{text}"
                                },
                            ]
                        }
                        ]
                    )
                    return response.choices[0].message.content
            
            return await run_in_threadpool(sync_ask)

    async def ask_local(self, text: str):
        response = await self.local_ollama_client.chat(
            model="gemma4:latest",
            messages=[
                {
                    "role": "user",
                    "content": text
                }
            ]
        )
        return response["message"]["content"]