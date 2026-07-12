from fastapi import FastAPI
from pydantic import BaseModel
from agent import run_agent
import uuid

app = FastAPI()

sessions: dict[str, list] = {}   # session_id → conversation history

class MessageRequest(BaseModel):
    session_id: str | None = None
    message: str

@app.post("/chat")
def chat(req: MessageRequest):
    session_id = req.session_id or str(uuid.uuid4())
    history    = sessions.get(session_id, [])

    reply, updated_history = run_agent(req.message, history)
    sessions[session_id]   = updated_history

    return {"session_id": session_id, "reply": reply}

@app.get("/")
def health():
    return {"status": "Retail Agent is running"}