import os

from twilio.rest import Client
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List
import boto3
import uuid

import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import random

app = FastAPI(title="Pseudo Monitoring APIs")

# -----------------------------
# CORS CONFIG (IMPORTANT)
# -----------------------------

origins = [
    "http://localhost:3000",   # React default
    "http://localhost:5173",   # Vite default
    "http://127.0.0.1:3000",
    "*"  # Allow all (for development only)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)


# -----------------------------
# Request Models
# -----------------------------

class StringRequest(BaseModel):
    input_string: str

class TwilioMessageRequest(BaseModel):
    
    message: str

class TwilioCallRequest(BaseModel):
    
    message: str

# -----------------------------
# 1️⃣ Atharv's Service
# -----------------------------
def ask_graph_agent(prompt, session_id):
    client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
    
    AGENT_ID = '7Y7AY7L03L' 
    AGENT_ALIAS_ID = 'TSTALIASID' 

    response = client.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=session_id,
        inputText=prompt,
        enableTrace=True # <--- Turn this on to see why it's blank
    )

    answer = ""
    for event in response.get("completion"):
        # 1. Look for the actual answer
        if "chunk" in event:
            data = event["chunk"]["bytes"].decode("utf-8")
            answer += data
        
        # 2. Look for errors in the trace
        if "trace" in event:
            # This prints the 'Thinking' process so you can see where it fails
            trace = event["trace"]["trace"]
            if "orchestrationTrace" in trace:
                print("--- AI is thinking... ---")
    
    return answer

@app.post("/agent-chat")
def ask_log_agent(request: StringRequest):
    # 1. Connect to the Bedrock Agent Runtime
    client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

    # 2. These are the IDs from your AWS Console
    # Find these on the "Agent details" page
    AGENT_ID = 'GLZOPT9W37' 
    AGENT_ALIAS_ID = 'TSTALIASID' # Or your specific Alias ID

    # 3. Call the Agent
    response = client.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=str(uuid.uuid4()),
        inputText=request.input_string
    )

    # 4. The Agent sends back a "stream" of data. We need to collect it.
    answer = ""
    for event in response.get("completion"):
        if "chunk" in event:
            data = event["chunk"]["bytes"].decode("utf-8")
            answer += data
    print("Agent Response:", answer)
    return {
        
        "output": answer
    }
    

@app.post("/twilio/send-message")
def send_twilio_message(request: TwilioMessageRequest):

    # Use environment variables for sensitive credentials
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_whatsapp = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

    if not account_sid or not auth_token:
        raise RuntimeError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in the environment")

    print("FROM NUMBER:", from_whatsapp)
    print("ACCOUNT SID:", account_sid)
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=request.message,
        from_=from_whatsapp,
        to="whatsapp:+918329059925"
    )

    return {
        "status": "Message Sent",
        "sid": message.sid
    }

@app.post("/twilio/make-call")
def make_twilio_call(request: TwilioCallRequest):
    
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_CALL_FROM", "+18593282622")

    if not account_sid or not auth_token:
        raise RuntimeError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in the environment")

    client = Client(account_sid, auth_token)

    call = client.calls.create(
        twiml=f'<Response><Say>{request.message}</Say></Response>',
        to="+918329059925",
        from_=from_number  # Your Twilio purchased phone number
    )

    return {
        "status": "Call Initiated",
        "call_sid": call.sid
    }

# -----------------------------
# 4️⃣ System Metrics API
# -----------------------------

cpu_base = 65.0
memory_base = 70.0
disk_base = 55.0
connections_base = 10

@app.get("/system/metrics")
def get_system_metrics():
    """
    Hardcoded system metrics but dynamically changing
    """

    cpu = round(cpu_base + random.uniform(-5.3, 5.2), 2)
    memory = round(memory_base + random.uniform(-4.5, 4.5), 2)
    disk = round(disk_base + random.uniform(-3, 3), 2)
    connections = connections_base + random.randint(0, 10)

    return {
        "cpu_usage_percent": cpu,
        "memory_usage_percent": memory,
        "disk_usage_percent": disk,
        "active_db_connections": connections,
        "service_status": "Healthy",
        "timestamp": datetime.utcnow()
    }
# -----------------------------
# 5️⃣ Logs API
# -----------------------------

@app.get("/logs")
def get_logs():
    """
    Returns mock logs
    """

    mock_logs = [
        {"timestamp":"2026-03-03T09:10:00Z","level":"INFO","service":"auth-service","message":"User login successful"},
        {"timestamp":"2026-03-03T09:10:22Z","level":"INFO","service":"auth-service","message":"Token generated for user"},
        {"timestamp":"2026-03-03T09:11:05Z","level":"WARNING","service":"db-service","message":"Slow query detected"},
        {"timestamp":"2026-03-03T09:11:33Z","level":"INFO","service":"notification-service","message":"Email notification queued"},
        {"timestamp":"2026-03-03T09:12:02Z","level":"INFO","service":"api-gateway","message":"Incoming API request processed"},
        {"timestamp":"2026-03-03T09:12:21Z","level":"WARNING","service":"db-service","message":"High query latency detected"},
        {"timestamp":"2026-03-03T09:12:55Z","level":"INFO","service":"auth-service","message":"Session validated"},
        {"timestamp":"2026-03-03T09:13:11Z","level":"INFO","service":"payment-service","message":"Payment request received"},
        {"timestamp":"2026-03-03T09:13:29Z","level":"ERROR","service":"payment-service","message":"Payment gateway timeout"},
        {"timestamp":"2026-03-03T09:13:58Z","level":"INFO","service":"notification-service","message":"Retrying failed email"},
        {"timestamp":"2026-03-03T09:14:12Z","level":"INFO","service":"api-gateway","message":"Route matched successfully"},
        {"timestamp":"2026-03-03T09:14:45Z","level":"ERROR","service":"api-gateway","message":"502 Bad Gateway"},
        {"timestamp":"2026-03-03T09:15:03Z","level":"INFO","service":"db-service","message":"Connection pool refreshed"},
        {"timestamp":"2026-03-03T09:15:21Z","level":"INFO","service":"auth-service","message":"Password verification completed"},
        {"timestamp":"2026-03-03T09:15:44Z","level":"WARNING","service":"api-gateway","message":"High request rate detected"},
        {"timestamp":"2026-03-03T09:16:10Z","level":"INFO","service":"notification-service","message":"Email sent successfully"},
        {"timestamp":"2026-03-03T09:16:31Z","level":"INFO","service":"auth-service","message":"New user session created"},
        {"timestamp":"2026-03-03T09:16:55Z","level":"INFO","service":"db-service","message":"Database replication healthy"},
        {"timestamp":"2026-03-03T09:17:19Z","level":"WARNING","service":"db-service","message":"Memory usage high on DB node"},
        {"timestamp":"2026-03-03T09:17:44Z","level":"INFO","service":"payment-service","message":"Payment authorized"},
        {"timestamp":"2026-03-03T09:18:02Z","level":"INFO","service":"api-gateway","message":"API response delivered"},
        {"timestamp":"2026-03-03T09:18:21Z","level":"INFO","service":"auth-service","message":"User logout successful"},
        {"timestamp":"2026-03-03T09:18:39Z","level":"ERROR","service":"payment-service","message":"Transaction declined"},
        {"timestamp":"2026-03-03T09:18:58Z","level":"INFO","service":"notification-service","message":"SMS notification queued"},
        {"timestamp":"2026-03-03T09:19:12Z","level":"INFO","service":"api-gateway","message":"Health check endpoint accessed"},
        {"timestamp":"2026-03-03T09:19:34Z","level":"WARNING","service":"api-gateway","message":"Unusual traffic spike"},
        {"timestamp":"2026-03-03T09:19:59Z","level":"INFO","service":"auth-service","message":"OAuth token validated"},
        {"timestamp":"2026-03-03T09:20:14Z","level":"INFO","service":"db-service","message":"Index optimization completed"},
        {"timestamp":"2026-03-03T09:20:37Z","level":"ERROR","service":"db-service","message":"Database connection dropped"},
        {"timestamp":"2026-03-03T09:20:59Z","level":"INFO","service":"db-service","message":"Reconnecting to database"},
        {"timestamp":"2026-03-03T09:21:18Z","level":"INFO","service":"notification-service","message":"Push notification sent"},
        {"timestamp":"2026-03-03T09:21:33Z","level":"INFO","service":"payment-service","message":"Refund initiated"},
        {"timestamp":"2026-03-03T09:21:55Z","level":"WARNING","service":"payment-service","message":"Slow external payment API"},
        {"timestamp":"2026-03-03T09:22:11Z","level":"INFO","service":"auth-service","message":"Two-factor authentication triggered"},
        {"timestamp":"2026-03-03T09:22:39Z","level":"INFO","service":"notification-service","message":"Webhook event processed"},
        {"timestamp":"2026-03-03T09:22:59Z","level":"INFO","service":"api-gateway","message":"Request validated"},
        {"timestamp":"2026-03-03T09:23:17Z","level":"WARNING","service":"db-service","message":"Disk I/O latency high"},
        {"timestamp":"2026-03-03T09:23:36Z","level":"INFO","service":"db-service","message":"Background cleanup executed"},
        {"timestamp":"2026-03-03T09:23:59Z","level":"ERROR","service":"api-gateway","message":"Service timeout detected"},
        {"timestamp":"2026-03-03T09:24:22Z","level":"INFO","service":"notification-service","message":"Email retry succeeded"},
        {"timestamp":"2026-03-03T09:24:44Z","level":"INFO","service":"auth-service","message":"JWT token refreshed"},
        {"timestamp":"2026-03-03T09:25:05Z","level":"INFO","service":"payment-service","message":"Payment status updated"},
        {"timestamp":"2026-03-03T09:25:29Z","level":"WARNING","service":"payment-service","message":"Currency conversion delay"},
        {"timestamp":"2026-03-03T09:25:48Z","level":"INFO","service":"db-service","message":"Backup job started"},
        {"timestamp":"2026-03-03T09:26:10Z","level":"INFO","service":"db-service","message":"Backup completed"},
        {"timestamp":"2026-03-03T09:26:29Z","level":"INFO","service":"api-gateway","message":"Cache refreshed"},
        {"timestamp":"2026-03-03T09:26:51Z","level":"ERROR","service":"notification-service","message":"Email service unavailable"},
        {"timestamp":"2026-03-03T09:27:15Z","level":"INFO","service":"notification-service","message":"Fallback SMTP activated"},
        {"timestamp":"2026-03-03T09:27:33Z","level":"INFO","service":"auth-service","message":"Permission check successful"},
        {"timestamp":"2026-03-03T09:27:58Z","level":"INFO","service":"api-gateway","message":"API response cached"}
    ]

    return {
        "total_logs": len(mock_logs),
        "logs": mock_logs
    }


@app.post("/graph-agent-chat")
def graph_agent(request: StringRequest):
    return {
        "output": ask_graph_agent(request.input_string , str(uuid.uuid4()))
    }