from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from ollama import Client

from prometheus_client import (
    Counter,
    Histogram,
    generate_latest
)

import json
import re
import os
import time


# =====================================
# OLLAMA CONFIG
# =====================================

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

client = Client(host=OLLAMA_HOST)


# =====================================
# FASTAPI APP
# =====================================

app = FastAPI()

print("APP FILE LOADED - METRICS VERSION")

@app.on_event("startup")
async def show_routes():
    print("\n===== ROUTES =====")
    for route in app.routes:
        print(route.path)
    print("==================\n")

@app.get("/debug-routes")
def debug_routes():
    return [route.path for route in app.routes]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================
# PROMETHEUS METRICS
# =====================================

REQUEST_COUNT = Counter(
    "ai_requests_total",
    "Total AI requests"
)

REQUEST_LATENCY = Histogram(
    "ai_request_latency_seconds",
    "AI request latency"
)


# =====================================
# REQUEST MODEL
# =====================================

class LogRequest(BaseModel):
    logs: str


# =====================================
# METRICS ENDPOINT
# =====================================

@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type="text/plain"
    )


# =====================================
# ANALYZE ENDPOINT
# =====================================

@app.post("/analyze")
def analyze_logs(request: LogRequest):

    REQUEST_COUNT.inc()

    start_time = time.time()

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
- return ONLY JSON

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
        print("===========================\n")

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

        # =====================================
        # FALLBACKS
        # =====================================

        if not parsed_json.get("root_cause"):
            parsed_json["root_cause"] = (
                "Unable to determine root cause"
            )

        severity = parsed_json.get(
            "severity",
            ""
        )

        if severity not in [
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL"
        ]:
            parsed_json["severity"] = "HIGH"

        evidence = parsed_json.get(
            "evidence",
            []
        )

        if not evidence:
            parsed_json["evidence"] = [
                "No evidence extracted"
            ]

        recommendations = parsed_json.get(
            "recommendations",
            []
        )

        if (
            not recommendations
            or all(
                str(item).strip() == ""
                for item in recommendations
            )
        ):
            parsed_json["recommendations"] = [
                "Review pod logs using kubectl logs",
                "Check Kubernetes events using kubectl describe pod",
                "Verify application configuration and secrets"
            ]

        REQUEST_LATENCY.observe(
            time.time() - start_time
        )

        print("\n===== PARSED JSON =====")
        print(parsed_json)
        print("=======================\n")

        return parsed_json

    except Exception as e:

        print("\n===== ERROR =====")
        print(str(e))
        print("=================\n")

        return {
            "error": str(e)
        }