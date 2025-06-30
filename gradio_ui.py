import gradio as gr
import os
import requests
import tempfile

# 👉 Replace with your deployed Lambda HTTP endpoint
LAMBDA_API_URL = "https://4dcejstet7r36b2fah2csdlb4y0ibswa.lambda-url.eu-north-1.on.aws/"

# Function to call AWS Lambda
def generate(topic, duration, budget, currency, preferred_type):
    context = {
        "topic": topic,
        "duration": duration,
        "budget": budget,
        "currency": currency,
        "preferred_content_type": preferred_type,
        "user_profile": {
            "learning_style": "visual",
            "time_per_day": "1 hour"
        }
    }

    try:
        # Send context directly as JSON (not nested in "body")
        response = requests.post(LAMBDA_API_URL, json=context)

        if response.status_code == 200:
            result = response.json().get("plan", response.text)
            print("📦 AI Response:\n", result)
            return result, None
        else:
            print("❌ Lambda error:", response.text)
            return f"⚠️ Lambda error: {response.text}", None

    except Exception as e:
        print("⚠️ Exception:", e)
        return f"⚠️ Error: {str(e)}", None

# Generate .txt file from course plan
def create_txt(course_text):
    if not course_text or course_text.startswith("⚠️ Error"):
        print("⚠️ No content to create TXT file.")
        return None

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
        tmp.write(course_text)
        print("✅ TXT file saved at:", tmp.name)
        return tmp.name

# Build the UI
with gr.Blocks(css=".gr-box { border-radius: 12px; padding: 16px; box-shadow: 0 0 10px #eee; }") as ui:
    gr.Markdown("""
    # 🎓 **CourseCrafter**
    _AI-powered personalized course generator_

    Enter your details and download your learning roadmap as a TXT file! ✨
    """)

    with gr.Row():
        with gr.Column(scale=1):
            topic = gr.Textbox(label="📘 Topic", placeholder="e.g. Python programming")
            duration = gr.Textbox(label="⏱️ Duration", placeholder="e.g. 4 weeks")

            with gr.Row():
                budget = gr.Textbox(label="💰 Budget", placeholder="e.g. 1000")
                currency = gr.Dropdown(
                    choices=["INR", "USD", "EUR", "GBP", "JPY"],
                    value="INR",
                    label="🌍 Currency"
                )

            preferred_type = gr.Dropdown(
                choices=["video", "text", "interactive", "any"],
                value="any",
                label="🎯 Preferred Content Type"
            )

            submit_btn = gr.Button("🚀 Generate Course Plan", variant="primary")

        with gr.Column(scale=1):
            output_box = gr.Textbox(
                label="📦 AI-Generated Course Plan",
                lines=18,
                interactive=False,
                show_copy_button=True
            )
            txt_file = gr.File(label="📄 TXT file", visible=True)

    submit_btn.click(
        fn=generate,
        inputs=[topic, duration, budget, currency, preferred_type],
        outputs=[output_box, txt_file]
    ).then(
        fn=create_txt,
        inputs=output_box,
        outputs=txt_file
    )

# Run app
if __name__ == "__main__":
    ui.launch(server_name="0.0.0.0", server_port=8080)