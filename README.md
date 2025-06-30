# 🎓 CourseCrafter

**CourseCrafter** is an AI-powered personalized learning roadmap generator. Users can input a topic, duration, budget, and content preference, and receive a well-structured, resource-rich course plan tailored to their needs.

This project connects a Gradio UI with an AWS Lambda backend that queries a deployed LLM via Modal to generate learning plans.

---

## 🚀 Demo

🌐 Live UI: [https://hackathon-june-28.onrender.com](https://hackathon-june-28.onrender.com)  
🎥 Demo Video: [https://youtu.be/RnvDnqmwhNQ?feature=shared](https://youtu.be/RnvDnqmwhNQ?feature=shared)

---

## ✨ Features

- 🌐 **Gradio Frontend**: User-friendly form interface
- 🧠 **AI-Powered Backend**: LLM generates structured course plans
- ☁️ **Serverless Lambda API**: Scalable AWS Lambda function processes user input
- 📄 **TXT Download**: Users can save their learning roadmap instantly

---

## 🛠️ Stack Used

| Layer        | Technology                      |
|-------------|----------------------------------|
| UI          | Gradio (Python)                  |
| Backend     | AWS Lambda + API Gateway         |
| AI Engine   | Modal-hosted FastAPI LLM Server  |
| Dev Tools   | Gitpod, GitHub                   |

---

## 📂 Project Structure

```
├── gradio_ui.py              # Frontend Gradio interface
├── lambda_handler.py         # AWS Lambda backend function
├── server.py                 # Modal FastAPI LLM server (Mistral or LLaMA)
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 🧪 How to Test API (Console)

```bash
curl -X POST https://<your-api-id>.execute-api.<region>.amazonaws.com/default/CourseCrafter \
  -H "Content-Type: application/json" \
  -d '{
    "body": {
      "topic": "Machine Learning",
      "duration": "30 days",
      "budget": "0",
      "currency": "USD",
      "preferred_content_type": "video"
    }
  }'
```

---

## ✅ Setup Instructions

### 🖥️ Local UI (Gradio)

```bash
# Install dependencies
pip install -r requirements.txt

# Run Gradio app
python gradio_ui.py
```

### ☁️ Deploy Lambda (Python 3.12+)

1. Zip `lambda_handler.py` + dependencies (e.g., `requests`)
2. Upload to AWS Lambda
3. Create API Gateway with `/CourseCrafter` route (POST method)
4. Enable CORS: allow `*` origin, `Content-Type` header, and `POST` method
5. Deploy stage and copy the endpoint into `gradio_ui.py`

---

## 🧠 About the Project

### What Inspired Me

I often struggled to find personalized learning paths for specific topics. Most platforms are generic or behind paywalls. I wanted a tool to generate actionable roadmaps with real resources.

### What I Learned

- Creating serverless APIs with AWS Lambda + API Gateway  
- Hosting LLM endpoints with Modal + FastAPI  
- Building user-friendly interfaces using Gradio  

### Challenges I Faced

- Handling nested JSON payloads in Lambda  
- Fixing CORS issues with API Gateway  
- Debugging Lambda–Modal communication

---

## 📄 License

This project is open-source and available under the MIT License.