from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ollama import Client
import json
import re
import os

# ==========================
# Ollama Client
# ==========================

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

client = Client(host=OLLAMA_HOST)

# ==========================
# FastAPI App
# ==========================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# Request Model
# ==========================

class LogRequest(BaseModel):
    logs: str

# ==========================
# API Endpoint
# ==========================

@app.post("/analyze")
def analyze_logs(request: LogRequest):

    prompt = f"""
You are a Senior Kubernetes SRE.

Analyze the Kubernetes logs below.

Return ONLY valid JSON.

Format:

{{
  "root_cause": "string",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "evidence": [
    "string"
  ],
  "recommendations": [
    "string"
  ]
}}

Rules:
- root_cause must never be empty
- severity must be LOW, MEDIUM, HIGH, or CRITICAL
- evidence must contain important log lines
- recommendations must contain exactly 3 actionable recommendations
- return only JSON

Logs:

{request.logs}
"""

    try:

        response = client.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result = response["message"]["content"].strip()

        print("\n===== OLLAMA RESPONSE =====")
        print(result)
        print("==========================\n")

        json_match = re.search(
            r"\{.*\}",
            result,
            re.DOTALL
        )

        if not json_match:
            return {
                "error": "No valid JSON returned by model"
            }

        parsed_json = json.loads(
            json_match.group()
        )

        # ==========================
        # Fallbacks
        # ==========================

        if not parsed_json.get("root_cause"):
            parsed_json["root_cause"] = (
                "Unable to determine root cause"
            )

        if (
            not parsed_json.get("severity")
            or parsed_json["severity"]
            == "LOW|MEDIUM|HIGH|CRITICAL"
        ):
            parsed_json["severity"] = "HIGH"

        recommendations = parsed_json.get(
            "recommendations",
            []
        )

        if (
            not recommendations
            or all(
                str(r).strip() == ""
                for r in recommendations
            )
        ):
            parsed_json["recommendations"] = [
                "Review pod logs using kubectl logs",
                "Check Kubernetes events",
                "Verify application configuration"
            ]

        print("\n===== PARSED JSON =====")
        print(parsed_json)
        print("======================\n")

        return parsed_json

    except Exception as e:
        print("ERROR:", str(e))

        return {
            "error": str(e)
        }