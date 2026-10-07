import json
import os
import socket
from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from pathlib import Path
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="K8s Beginners 02 Demo Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

POD_NAME = os.getenv("POD_NAME", socket.gethostname())
ENV_NAME = os.getenv("ENV_NAME", "LOCAL")
API_KEY = os.getenv("API_KEY", "local-demo-secret")
DATA_PATH = Path(os.getenv("DATA_PATH", "./data/message.json"))

class MessageRequest(BaseModel):
    message: str

def masked_secret(value: str) -> str:
    if not value:
        return "not set"
    return "*" * 8

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "pod": POD_NAME,
    }
@app.get("/api/info")
def info():
    return {
        "app": "backend",
        "pod": POD_NAME,
        "environment": ENV_NAME,
        "secret" : {
            "key": "API_KEY",
            "value": masked_secret(API_KEY),
        }
    }

@app.post("/api/data")
def write_data(request: MessageRequest):
    try:
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "message": request.message,
            "written_by": POD_NAME,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        DATA_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8")
        return {
            **data,
            "served_by": POD_NAME,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data")
def read_data():
    if not DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="no persistent data yet")
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        return {
            **data,
            "read_by": POD_NAME,
            "served_by": POD_NAME,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

