import json
import requests

# Your deployed LLM server endpoint
LLM_API_URL = "https://namany7927--course-crafter-mistral-server-fastapi-app.modal.run/v19/chat/completions"

# Helper to send prompt to your LLM API
def query_llm(messages):
    payload = { "messages": messages }
    headers = { "Content-Type": "application/json" }

    response = requests.post(LLM_API_URL, json=payload, headers=headers)
    print("📨 Sent to LLM:", payload)
    print("📥 Received:", response.text)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"LLM request failed: {response.status_code} — {response.text}")

# AWS Lambda entry point
def generate_course_plan(event, context):
    try:
        # ✅ Log the raw incoming event
        print("📥 Raw event:", json.dumps(event))

        body = event.get("body")

        # ✅ If body is a JSON string, parse it
        if isinstance(body, str):
            body = json.loads(body)

        # ✅ Handle nested {"body": {...}} structure (common mistake)
        if isinstance(body, dict) and "body" in body and isinstance(body["body"], dict):
            body = body["body"]

        # ✅ Extract fields safely
        topic = body.get("topic")
        duration = body.get("duration", "")
        budget = body.get("budget", "")
        currency = body.get("currency", "")
        preferred_content_type = body.get("preferred_content_type", "")

        if not topic:
            raise Exception("Missing required field: 'topic'")

        # 🧠 Prompt generation
        prompt = f"""
        I want to learn {topic} but am unable to find the perfect plan and resources.
        I only have {duration}, and my budget is {budget} {currency}.
        I prefer content type to be {preferred_content_type}.
        Can you help me craft a course with perfect resources, a well-planned timetable, and mandatory links?
        """

        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates learning roadmaps."},
            {"role": "user", "content": prompt.strip()}
        ]

        result = query_llm(messages)

        return {
            "statusCode": 200,
            "headers": { "Content-Type": "application/json" },
            "body": json.dumps({ "plan": result })
        }

    except Exception as e:
        print("❌ Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({ "error": str(e) })
        }