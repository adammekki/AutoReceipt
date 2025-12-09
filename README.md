# 🧾 AutoReceipt - AI-Powered Travel Expense Automation

## �� Overview

AutoReceipt automates the **expense reporting process** for academics (professors, researchers, etc.) who attend conferences or work trips.

Traditionally, users must manually fill out a university-provided PDF form by extracting data (date, amount, purpose, etc.) from multiple receipts — a tedious and error-prone task.

This app eliminates that manual work by using **AI (Google Gemini)** and **automated PDF form filling (fillpdf)**. Simply upload your receipts (PDFs or images), and the system:

1. Extracts all relevant information (amounts, dates, origins, destinations, transport type, etc.) using Gemini AI
2. Automatically fills out the university's **Reisekostenabrechnung** PDF form
3. Returns the completed, ready-to-submit PDF to the user

---

## 🏗️ Project Structure

This project is organized as a monorepo with separate backend and frontend applications:

\`\`\`
AutoReceipt/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI entrypoint
│   │   ├── antrag.py       # Antrag processing logic
│   │   ├── hinreise.py     # Outbound journey processing
│   │   ├── ruckreise.py    # Return journey processing
│   │   └── hotel.py        # Hotel/conference processing
│   ├── requirements.txt
│   └── .env.example
├── frontend/                # Next.js React frontend
│   └── README.md           # Frontend setup instructions
├── .gitignore
└── README.md
\`\`\`

---

## 🧠 How It Works

### 1. Input
The user provides one or multiple receipts — either as **images** (\`.jpg\`, \`.png\`, etc.) or **PDFs** — through the web interface or API.

### 2. Document Preparation
Each document is processed and converted (if necessary) into a format suitable for the **Gemini Vision API**:
- PDFs are converted to images using \`pdf2image\`
- Images are loaded and converted to byte arrays via \`Pillow (PIL)\`

### 3. Data Extraction (Gemini API)
A prompt is sent to **Google's Gemini 2.5 Flash model**, which analyzes the receipts and extracts structured travel expense information in **JSON format**.

### 4. PDF Form Filling
The extracted JSON is then passed into **fillpdf**, which automates the population of PDF form fields in the university's **Reisekostenabrechnung** form.

### 5. Output
The system generates a **filled PDF document** ready for submission.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for frontend)
- **Poppler** (required by pdf2image)
  - macOS: \`brew install poppler\`
  - Ubuntu: \`apt-get install poppler-utils\`
  - Windows: Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases)
- **Google Gemini API Key**

### Backend Setup

1. Navigate to the backend directory:
   \`\`\`bash
   cd backend
   \`\`\`

2. Create and activate a virtual environment:
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

3. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. Create environment file:
   \`\`\`bash
   cp .env.example .env
   \`\`\`

5. Edit \`.env\` and add your Gemini API key:
   \`\`\`
   GEMINI_API_KEY=your_api_key_here
   \`\`\`

6. Start the backend server:
   \`\`\`bash
   uvicorn app.main:app --reload
   \`\`\`

The API will be available at \`http://localhost:8000\`.

### Frontend Setup

1. Navigate to the frontend directory:
   \`\`\`bash
   cd frontend
   \`\`\`

2. Create the Next.js app (first time only):
   \`\`\`bash
   npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
   \`\`\`

3. Install dependencies:
   \`\`\`bash
   npm install
   \`\`\`

4. Create \`.env.local\`:
   \`\`\`
   NEXT_PUBLIC_API_URL=http://localhost:8000
   \`\`\`

5. Start the development server:
   \`\`\`bash
   npm run dev
   \`\`\`

The frontend will be available at \`http://localhost:3000\`.

---

## 🔌 API Endpoints

### Health Check
\`\`\`
GET /api/health
\`\`\`

### Process Trip (Main Endpoint)
\`\`\`
POST /api/process-trip
Content-Type: multipart/form-data

Required files:
- dienstreiseantrag: Dienstreiseantrag PDF form
- reisekostenabrechnung: Reisekostenabrechnung template

Optional files:
- receipt_flight1, receipt_flight2, receipt_flight3: Flight receipts
- receipt_parking: Parking receipt
- payment_conference, receipt_conference: Conference receipts
- payment_parking: Parking payment
- receipt_hotel: Hotel receipt

Optional parameters:
- supervisor_name: Override supervisor name
\`\`\`

### Download Generated PDF
\`\`\`
GET /api/download/{filename}
\`\`\`

---

## 🧩 Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI (Python) |
| **Frontend** | Next.js (React/TypeScript) |
| **AI Model** | Google Gemini 2.5 Flash |
| **PDF Processing** | fillpdf, pdf2image, PyMuPDF |
| **Image Processing** | Pillow (PIL) |
| **PDF Rendering** | Poppler |

---

## 🔒 Security & Privacy

- API keys are stored in environment variables (never committed)
- Uploaded files are processed in temporary directories
- No user data or receipts are stored permanently
- CORS is configured for local development only

---

## 📝 Development Notes

### Running the Full Pipeline

The processing pipeline runs in this order:
1. **Antrag** - Extracts applicant data from Dienstreiseantrag
2. **Hinreise** - Processes outbound journey receipts
3. **Ruckreise** - Processes return journey receipts
4. **Hotel** - Processes accommodation and conference receipts

### API Documentation

When the backend is running, visit:
- Swagger UI: \`http://localhost:8000/docs\`
- ReDoc: \`http://localhost:8000/redoc\`

---

## 👩‍💻 Author

- Project by: **Adam Mekki**
- Goal: Automate and simplify academic travel reimbursement using AI and PDF automation.

---

## 📄 License

This project is part of a thesis and is intended for educational purposes.
