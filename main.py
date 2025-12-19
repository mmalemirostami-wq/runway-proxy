from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx
import asyncio
import json

app = FastAPI()

RUNWAY_API_KEY = "key_afd895a9f225ed0f0a685879829322a33d8bb6df2ed2c41816cd6a44803cae145015d70eed4c79f4d2b3cad8c35d6c216a54ce3fbacf0bec77c69a1401bd4679"
RUNWAY_TASK_URL = "https://api.runwayml.com/v1/text_to_video"  # Or whichever endpoint

async def stream_task(task_id: str):
    async with httpx.AsyncClient() as client:
        while True:
            # Poll Runway task status
            resp = await client.get(
                f"https://api.runwayml.com/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {RUNWAY_API_KEY}"}
            )
            data = resp.json()

            # Send the update as SSE
            yield f"data: {json.dumps(data)}\n\n"

            # Stop if task is complete
            if data.get("status") in ["succeeded", "failed"]:
                break

            await asyncio.sleep(2)  # Poll every 2 seconds

@app.post("/runway-to-chatgpt")
async def runway_to_chatgpt(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "Hello")

    async with httpx.AsyncClient() as client:
        # Start the Runway task
        response = await client.post(
            RUNWAY_TASK_URL,
            headers={"Authorization": f"Bearer {RUNWAY_API_KEY}"},
            json={"prompt": prompt}
        )
        task_id = response.json()["id"]

    # Return streaming response to ChatGPT
    return StreamingResponse(
        stream_task(task_id),
        media_type="text/event-stream"
    )

