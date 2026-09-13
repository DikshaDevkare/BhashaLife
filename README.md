# 🛡️ BhashaLife AI

### Your Multilingual Life & Digital Safety Agent

> **Understand what matters. Know what to do next.**

BhashaLife AI is a **multilingual, multimodal AI-powered digital safety agent** designed to help users understand potentially risky messages, identify important information, assess digital safety risks, and receive clear, actionable next steps.

It supports **English, Hindi, Marathi, and Hinglish/Roman text**, making digital safety assistance more accessible to users with different language preferences.

---

## 🚨 Problem Statement

People receive messages every day from banks, colleges, government services, unknown contacts, and other sources. Some messages may contain scams, phishing attempts, financial threats, OTP requests, suspicious links, important notices, or threatening content.

Users often struggle to understand:

- Is this message important?
- Is this message risky?
- Why is it risky?
- What could happen?
- What should I do next?

Traditional solutions often focus only on classification, without providing understandable explanations and practical next steps.

---

## 💡 Our Solution

BhashaLife AI acts as an intelligent safety assistant that converts confusing or potentially risky information into **understandable, risk-aware, and actionable guidance**.

### Core Workflow

```text
UPLOAD
   ↓
UNDERSTAND
   ↓
HIGHLIGHT
   ↓
PLAN
   ↓
ACT
   ↓
VERIFY
   ↓
ADAPT

✨ Key Features
🌐 Multilingual Understanding

BhashaLife AI supports:

🇬🇧 English
🇮🇳 Hindi
🟠 Marathi
🔤 Hinglish / Roman text

The system identifies the language/script and provides understandable explanations.

🧠 AI-Powered Risk Assessment

Messages are evaluated using a risk-scoring system.

Risk Score	Risk Level
0–24	🟢 LOW
25–49	🟡 MODERATE
50–74	🟠 HIGH
75–100	🔴 CRITICAL

The analysis can consider factors such as:

OTP requests
Financial pressure
Urgency
Threatening language
Suspicious instructions
Potential consequences
🛡️ Life Shield

The Life Shield focuses on potential real-world consequences of risky digital interactions.

User receives suspicious message
            ↓
      Message Analysis
            ↓
       Risk Assessment
            ↓
         Life Shield
            ↓
     Consequence Analysis
            ↓
        Action Plan

Instead of simply saying:

"This message is risky."

BhashaLife explains:

"Why is it risky, what could happen, and what should I do next?"

🤖 Adaptive AI Agent

One of the core features of BhashaLife AI is its ability to reassess a situation when new information is provided.

Example

Initial message:

Your bank account will be blocked today.
Share the OTP immediately to verify your account.

The system identifies the message as highly risky.

Then the user provides additional context:

I already shared my OTP.

The system reassesses the situation and generates an updated action plan based on the new information.

Initial Information
        ↓
Risk Assessment
        ↓
Action Plan
        ↓
New User Information
        ↓
Reassessment
        ↓
Updated Consequences
        ↓
Updated Action Plan

This demonstrates the agent's ability to adapt its response based on changing context.

📄 Multimodal Input

BhashaLife AI can work with multiple types of information:

💬 Text messages
🖼️ Screenshots and images
📄 PDF documents
📝 TXT documents
📑 DOCX documents

For image-based inputs, OCR can extract text before analysis.

🔍 Important Only

Instead of overwhelming users with unnecessary information, BhashaLife focuses on what matters most.

The system highlights:

Important information
Risk indicators
Required actions
Potential consequences
Recommended next steps
🧩 Agent Architecture
                         USER
                          │
                          ▼
                MULTIMODAL INPUT
                          │
                          ▼
                   BHASHA SHIELD
                          │
                          ▼
                   ORCHESTRATOR
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
            OCR      DOCUMENT       URL
                    INTELLIGENCE    ANALYSIS
             │            │            │
             └────────────┼────────────┘
                          ▼
                   LLM REASONER
                          │
                          ▼
                    LIFE SHIELD
                          │
                          ▼
                CONSEQUENCE AGENT
                          │
                          ▼
                  ACTION PLANNER
                          │
                          ▼
                    EVALUATOR
                     /       \
                    ▼         ▼
                SUCCESS     REPLAN
🏗️ Technology Stack
Frontend
React
Vite
JavaScript / TypeScript
Responsive UI
Backend
Python
FastAPI
Pydantic
AI / Intelligence
LLM-based reasoning
OCR
Document parsing
Risk assessment
Retrieval-based knowledge support
Adaptive orchestration
Document Processing
PyPDF
PyMuPDF
python-docx
Pillow
Tesseract OCR
Deployment
GitHub
Vercel
📁 Project Structure
BhashaLife/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   └── orchestrator.py
│   │   │
│   │   ├── services/
│   │   │   ├── bhasha_shield.py
│   │   │   ├── rag.py
│   │   │   ├── life_shield.py
│   │   │   ├── action_planner.py
│   │   │   └── document_intelligence.py
│   │   │
│   │   ├── tools/
│   │   │   ├── ocr.py
│   │   │   ├── url_analyzer.py
│   │   │   └── document_parser.py
│   │   │
│   │   ├── models/
│   │   │   └── schemas.py
│   │   │
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── knowledge/
│
├── .gitignore
├── vercel.json
└── README.md

🎯 Why BhashaLife AI?

BhashaLife AI combines:

Multilingual Understanding
          +
Multimodal Input
          +
Risk Assessment
          +
Consequence Analysis
          +
Action Planning
          +
Adaptive Replanning
          ↓
     BhashaLife AI

The key innovation is moving beyond simple classification.

Instead of only saying:

❌ This message is risky.

BhashaLife aims to provide:

✅ Why it is risky
✅ What could happen
✅ What you should do next
✅ How the plan changes when new information arrives
🔐 Safety & Responsible AI

BhashaLife AI is designed as an AI-assisted digital safety and risk-triage system.

It does not claim to:

Guarantee that a message is a scam
Diagnose psychological conditions
Predict future violence
Replace professional, legal, financial, or emergency services

The system provides risk-aware explanations and actionable guidance to help users make safer and more informed decisions.

🚀 Future Scope

Future improvements may include:

🎙️ Voice-based interaction
🌐 Support for additional Indian languages
🔗 Real-time URL safety analysis
📷 Improved OCR for regional scripts
👤 Personalized safety workflows
🧠 More comprehensive knowledge retrieval
🆘 Integration with verified emergency/help resources
🔄 Continuous context-aware assistance
👥 Team
BhashaLife AI

Built with ❤️ for the hackathon to make digital safety assistance more understandable, multilingual, adaptive, and actionable.
