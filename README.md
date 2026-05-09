# Multi-Agent Customer Support Pipeline

> An AI-powered customer support system that classifies tickets, auto-generates responses for simple queries, and escalates complex/sensitive issues to Google Sheets — powered by a local LLM (Ollama) or OpenAI.

---

## Architecture Diagram

```
+---------------------+
|   data/tickets.json |  <-- Input: 10 support tickets (6 simple + 4 complex)
+---------------------+
          |
          v
+--------------------+
|     main.py        |  <-- Pipeline Orchestrator
| (run_pipeline())   |
+--------------------+
          |
          v
+-----------------------------+
|  Agent 1: ClassifierAgent   |  agents/classifier_agent.py
|  - Reads ticket             |
|  - Calls LLM with prompt    |
|  - Returns JSON:            |
|    { category,              |
|      priority,              |
|      escalate: true/false } |
+-----------------------------+
          |
     +----|----+
     |         |
     | escalate=False       escalate=True
     v                           v
+-------------------+    +----------------------+
| Agent 2:          |    | Agent 3:             |
| ResponseAgent     |    | EscalationAgent      |
| - Generates       |    | - Generates summary  |
|   empathetic      |    | - Sends row to       |
|   reply for       |    |   Google Sheets via  |
|   customer        |    |   GoogleSheetsHandler|
+-------------------+    +----------------------+
          |                         |
          v                         v
+-------------------+    +----------------------+
| data/responses    |    | Google Sheet:        |
|    .json          |    | CustomerSupport      |
| (all results      |    | Escalations          |
|  saved here)      |    | (live spreadsheet)   |
+-------------------+    +----------------------+
```

---

## Project Structure

```
p3/
|
|-- main.py                      # Pipeline orchestrator
|-- requirements.txt             # Python dependencies
|-- .env                         # Environment variables (not committed)
|-- .env.example                 # Template for .env
|-- credentials.json             # Google Service Account key (not committed)
|-- credentials.json.example     # Template showing required fields
|-- test_sheets.py               # Google Sheets connection test script
|-- support_pipeline.log         # Auto-generated log file
|
|-- agents/
|   |-- classifier_agent.py      # Agent 1: Classifies tickets via LLM
|   |-- response_agent.py        # Agent 2: Generates customer replies
|   |-- escalation_agent.py      # Agent 3: Summarizes & escalates to Sheets
|
|-- utils/
|   |-- google_sheets.py         # Google Sheets authentication & write handler
|   |-- prompts.py               # All LLM prompts (classifier, response, summary)
|
|-- data/
    |-- tickets.json             # Input: 10 test tickets (6 simple + 4 complex)
    |-- responses.json           # Output: Auto-generated after pipeline runs
```

---

## Agent Roles

| Agent | File | Role |
|---|---|---|
| **ClassifierAgent** | `agents/classifier_agent.py` | Reads each ticket and uses the LLM to assign a `category`, `priority` (P1/P2/P3), and `escalate` flag |
| **ResponseAgent** | `agents/response_agent.py` | For non-escalated tickets: generates a warm, professional reply |
| **EscalationAgent** | `agents/escalation_agent.py` | For escalated tickets: generates a 15-word summary and writes a row to Google Sheets |

### Classification Logic

| Category | Priority | Escalated? |
|---|---|---|
| `sensitive_complaint` | P1 | Yes |
| `refund` | P2 | No |
| `technical_bug` | P2 | No |
| `simple_question` | P3 | No |

> Tickets with P1 priority or `sensitive_complaint` category are automatically escalated.

---

## Setup Instructions

### 1. Clone & Install Dependencies

```bash
# Install all required packages
py -m pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
copy .env.example .env
```


### 3. Set Up Google Sheets Integration

#### Step 1 — Create a Google Cloud Project
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g., `customer-support`)

#### Step 2 — Enable APIs
Go to **APIs & Services > Library** and enable:
- **Google Sheets API**
- **Google Drive API**

#### Step 3 — Create a Service Account
1. Go to **APIs & Services > Credentials**
2. Click **+ Create Credentials > Service Account**
3. Name it (e.g., `sheets-bot`) and click **Done**

#### Step 4 — Download JSON Key
1. Click your service account > **Keys** tab
2. **Add Key > Create New Key > JSON**
3. Rename the downloaded file to `credentials.json`
4. Place it in the project root: `p3/credentials.json`

#### Step 5 — Share the Google Sheet
1. Create a Google Sheet named **`CustomerSupportEscalations`**
2. Add these headers in Row 1:

| Ticket ID | Subject | Summary | Priority | Category |
|---|---|---|---|---|

3. Click **Share** and paste your service account email:
   ```
   your-service-account@your-project-id.iam.gserviceaccount.com
   ```
4. Give **Editor** access and click **Send**

#### Step 6 — Test the Connection
```bash
py test_sheets.py
```

Expected output:
```
[OK] Credentials file found: credentials.json
[OK] Authentication successful!
[OK] Opened sheet: 'CustomerSupportEscalations'
[OK] Test row written successfully!
SUCCESS: Google Sheets integration is working!
```

---

## Running the Pipeline

### Prerequisites
- [Ollama](https://ollama.com) installed and running locally
- Your chosen model pulled (e.g., `ollama pull llama3.2`)
- Google Sheets configured as above

### Start Ollama
```bash
ollama serve
```

### Run the Pipeline
```bash
py main.py
```

### Expected Output
```
==================================================
STARTING CUSTOMER SUPPORT AGENT PIPELINE
==================================================

Processing Ticket #1 - Refund Request - Wrong Size...
  >> Generating response...
  Response: Thank you for reaching out about your order...

Processing Ticket #4 - SENSITIVE - FRAUD ALREADY REPORTED...
  >> Escalating ticket...

...

==================================================
PIPELINE COMPLETED SUCCESSFULLY
==================================================
```

---

## Input & Output Files

### Input — `data/tickets.json`
Contains 10 test tickets:
- **6 Simple tickets**: refund requests, technical bugs, simple questions
- **4 Complex tickets**: fraud reports, legal threats, multi-product issues, sensitive complaints

### Output — `data/responses.json`
Auto-generated after running the pipeline. Contains results for all tickets:

```json
[
  {
    "ticket_id": 1,
    "subject": "Refund Request - Wrong Size",
    "classification": { "category": "refund", "priority": "P2", "escalate": false },
    "status": "Responded",
    "response": "Thank you for reaching out...",
    "timestamp": "2026-05-08 20:00:00"
  },
  {
    "ticket_id": 4,
    "subject": "SENSITIVE - FRAUD ALREADY REPORTED",
    "classification": { "category": "sensitive_complaint", "priority": "P1", "escalate": true },
    "status": "Escalated",
    "escalation_summary": "Unauthorized $500 charge reported; customer already contacted bank.",
    "timestamp": "2026-05-08 20:00:05"
  }
]
```

### Google Sheet — `CustomerSupportEscalations`
Escalated tickets are written live to the shared Google Sheet with columns:

| Ticket ID | Subject | Summary | Priority | Category |
|---|---|---|---|---|
| 4 | SENSITIVE - FRAUD ALREADY REPORTED | Unauthorized charge; customer contacted bank. | P1 | sensitive_complaint |
| 8 | SENSITIVE - Legal Action Mentioned | Missing package; customer threatens legal action. | P1 | sensitive_complaint |

---

## Logs

All pipeline activity is recorded in `support_pipeline.log`:

```
2026-05-08 20:00:01 - ClassifierAgent - INFO - Classifying ticket #1...
2026-05-08 20:00:02 - ResponseAgent - INFO - Generating response for ticket #1...
2026-05-08 20:00:05 - EscalationAgent - INFO - Escalating ticket #4...
2026-05-08 20:00:05 - GoogleSheetsHandler - INFO - Successfully escalated ticket #4 to Google Sheets.
```

---

## Deliverables Checklist

| # | Deliverable | Status |
|---|---|---|
| 1 | Python script with 3 chained agents | `main.py` + `agents/` |
| 2 | JSON test file (min 10 tickets: 6 simple + 4 complex) | `data/tickets.json` |
| 3 | Shared Google Sheet with priority escalations | `CustomerSupportEscalations` (live) |
| 4 | JSON file of auto-generated responses | `data/responses.json` |
| 5 | README with architecture diagram and instructions | This file |

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.9+ | Core language |
| Ollama (llama3.2) | Local LLM inference (no API cost) |
| OpenAI SDK | API client (compatible with Ollama) |
| gspread | Google Sheets API client |
| oauth2client | Google Service Account authentication |
| python-dotenv | Environment variable management |
| colorama | Colored terminal output |
| logging | Structured pipeline logging |
