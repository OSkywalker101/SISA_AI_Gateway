import asyncio
import httpx
import time

GATEWAY_URL = "http://localhost:8000/v1/chat/completions"

# Keys matching the config
KEYS = {
    "free": "gw-test-key-123",
    "pro": "gw-pro-key-456",
    "enterprise": "gw-enterprise-key-789"
}

scenarios = [
    {
        "name": "1. Simple Chat (Should route to gemini-1.5-flash)",
        "key": KEYS["free"],
        "payload": {
            "model": "auto",
            "messages": [{"role": "user", "content": "What is the capital of France?"}]
        }
    },
    {
        "name": "2. Coding Task (Should route to gemini-1.5-pro)",
        "key": KEYS["pro"],
        "payload": {
            "model": "auto",
            "messages": [{"role": "user", "content": "Write a python function to compute fibonacci"}]
        }
    },
    {
        "name": "3. Explicit Model Request (Should route to anthropic stub)",
        "key": KEYS["enterprise"],
        "payload": {
            "model": "anthropic-claude-stub",
            "messages": [{"role": "user", "content": "Analyze this dataset."}]
        }
    },
    {
        "name": "4. Exceed Cost Threshold (Should downgrade to flash)",
        "key": KEYS["pro"],
        "payload": {
            "model": "auto",
            "messages": [{"role": "user", "content": "summarize this text: " + ("word " * 10000)}]
        }
    }
]

async def run_scenario(client, scenario):
    print(f"\n--- Running: {scenario['name']} ---")
    headers = {
        "Authorization": f"Bearer {scenario['key']}",
        "Content-Type": "application/json"
    }
    
    start = time.time()
    try:
        response = await client.post(GATEWAY_URL, json=scenario["payload"], headers=headers, timeout=30.0)
        latency = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success ({latency:.0f}ms)")
            print(f"   Model Used : {data['model']}")
            print(f"   Provider   : {data['provider']}")
            print(f"   Tokens     : {data['total_tokens']}")
            print(f"   Response   : {data['content'][:60]}...")
        elif response.status_code == 429:
            print(f"⚠️ Rate Limited (429): {response.json()['detail']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: Gateway might not be running. {e}")

async def test_rate_limiting(client):
    print("\n--- Running Rate Limit Test (Free Tier > 5 req/min) ---")
    headers = {"Authorization": f"Bearer {KEYS['free']}"}
    payload = {"model": "auto", "messages": [{"role": "user", "content": "Hi"}]}
    
    for i in range(7):
        resp = await client.post(GATEWAY_URL, json=payload, headers=headers)
        if resp.status_code == 200:
            print(f"Req {i+1}: ✅ 200 OK")
        elif resp.status_code == 429:
            print(f"Req {i+1}: 🛑 429 TOO MANY REQUESTS")
        else:
            print(f"Req {i+1}: ❌ {resp.status_code}")

async def main():
    print("AI Gateway - Integration Demo")
    print("=============================")
    print("Make sure the gateway is running in another terminal:")
    print("uvicorn main:app --port 8000\n")
    
    async with httpx.AsyncClient() as client:
        # Check health
        try:
            health = await client.get("http://localhost:8000/health")
            if health.status_code == 200:
                print("🟢 Gateway is ONLINE\n")
            else:
                print("🔴 Gateway returned non-200. Proceeding anyway...\n")
        except:
            print("🔴 Gateway is OFFLINE. Start it first before running this demo.\n")
            return

        for scenario in scenarios:
            await run_scenario(client, scenario)
            await asyncio.sleep(1) # Be nice
            
        await test_rate_limiting(client)
        
    print("\nDone! Check the dashboard at http://localhost:8000/dashboard")

if __name__ == "__main__":
    asyncio.run(main())
