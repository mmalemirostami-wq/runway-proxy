from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

RUNWAY_API_KEY = os.environ.get("RUNWAY_API_KEY")

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/runway")
async def runway_proxy(req: Request):
    body = await req.json()

    response = requests.post(
        "https://api.runwayml.com/v1/generate",
        headers={
            "Authorization": f"Bearer {RUNWAY_API_KEY}",
            "Content-Type": "application/json"
        },
        json=body
    )

    return response.json()
