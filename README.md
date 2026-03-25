# AI Gateway — SISA Submissions Project

This project implements a production-ready AI Gateway answering **Topic 1**. It sits between clients and LLM providers, offering central control, cost management, and observability.

## Features Developed
- **Intelligent Routing**: Automatically routes tasks based on prompt analysis (code vs reasoning vs chat).
- **Cost-Aware Load Balancing**: Downgrades the model if the estimated prompt cost exceeds a threshold.
- **Resilience**: Fallback mechanisms when primary models fail.
- **Provider Adapters**: Real integration with Google Gemini, plus fallback stubs for Anthropic and OpenAI.
- **API Management**: Token-bucket rate limiting based on client API Key tiers (`free`, `pro`, `enterprise`).
- **Observability**: SQLite-backed audit trails and a real-time web dashboard.

## Setup & Running

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Ensure `.env` contains your `GEMINI_API_KEY`. (I have already configured it for you!)

3. **Start the Gateway**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

4. **View Dashboard**
   Navigate to [http://localhost:8000/dashboard](http://localhost:8000/dashboard) to see the admin UI.

## Testing the Gateway

You can simulate client requests using `demo.py`:
```bash
python demo.py
```

Or via cURL using different Gateway Keys (`gw-test-key-123`, `gw-pro-key-456`):
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer gw-pro-key-456" \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"def hello():"}]}'
```

## Running Unit Tests
```bash
python -m pytest tests/ -v
```
