# Pseudo Monitoring API

FastAPI prototype that exposes sample monitoring and agent endpoints. The current implementation includes log and system-metric routes, agent-chat routes, and Twilio message/call routes.

## Routes

- `GET /system/metrics` and `GET /logs`
- `POST /agent-chat` and `POST /graph-agent-chat`
- `POST /twilio/send-message` and `POST /twilio/make-call`

Install the Python packages imported by `main.py`, configure any provider credentials locally, then run `uvicorn main:app --reload`. Treat the endpoints as a prototype; verify integrations and configuration before exposing the service publicly. Never commit credentials.
