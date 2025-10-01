# Real-Time Personal Finance Coach & Fraud Alert System

This project is an MVP (Minimum Viable Product) of a **finance coach app**.  
It ingests transactions in real-time, categorizes spending, flags possible fraud, and gives budgeting insights.

---

## Features (MVP scope)

- **Backend (FastAPI)** → REST API + fraud detection logic.  
- **Frontend (React + TypeScript)** → Dashboard with charts and alerts.  
- **Streaming (AWS Kinesis)** → Real-time pipeline for transactions.  
- **Database (PostgreSQL + TimescaleDB)** → Stores processed transactions.  
- **Auth (Cognito)** → Secure login and tokens.  
- **Monitoring (CloudWatch)** → Logs + metrics.  
- **Fake transaction generator** → Simulates live bank data for testing.  

---

## 📂 Project Structure

/finance-coach
  /backend         # FastAPI backend
    /api
    /models
    /streaming     # transaction generator lives here
    /tests
  /frontend        # React + TypeScript frontend
  /infra           # Docker, Terraform configs
  /docs            # architecture, API spec, etc.



## Getting Started

# Prerequisites
Make sure you have these installed:
- Python 3.11+ → check with python3 --version
- Node.js 18+ → check with node -v
- Docker Desktop → check with docker --version
- Git → check with git --version

## Run the Backend (FastAPI)

# Build the backend Docker image
docker build -t finance-coach-backend:dev -f backend/Dockerfile backend

# Run the backend container
docker run --rm -p 8000:8000 finance-coach-backend:dev

**Test it:** 
curl http://localhost:8000/health

**You should see:**
{"status":"ok"}


## Run the Frontend (React + Vite)
cd frontend
npm install
npm run dev

Open your browser at the link printed (usually http://localhost:5173).


## Fake Transaction Generator

This is a simple Python script that pretends to be a bank.  
It creates a new random transaction every ~2 seconds and prints it as JSON.  
You can use it to test the system without connecting to a real bank API.

# How to run
```bash
python3 backend/streaming/generate_transactions.py

# ** Example output **
# {"id": "c5f0a6d6-12ab-4f91-93f4-8f98a7a1d2cd", "merchant": "Tesco", "category_hint": "groceries", "amount": 23.41, "currency": "GBP", "timestamp": "2025-09-30T18:15:22.123456+00:00", "location": {"country": "GB"}, "channel": "online", "card_last4": "4821"}
# {"id": "12f4e33e-cc0c-40b6-9939-8f2a765bcad1", "merchant": "Netflix", "category_hint": "entertainment", "amount": 9.99, "currency": "GBP", "timestamp": "2025-09-30T18:15:24.987654+00:00", "location": {"country": "GB"}, "channel": "card_present", "card_last4": "7723"}
