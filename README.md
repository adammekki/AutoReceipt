# AutoReceipt - AI-Powered Travel Expense Automation

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Poppler (required by pdf2image)
  - macOS: `brew install poppler`
  - Ubuntu: `apt-get install poppler-utils`
  - Windows: Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases)
- Google Gemini API Key

### Running the Project Locally

**1. Clone the repository and navigate to the project root:**

```bash
git clone https://github.com/adammekki/AutoReceipt.git
cd AutoReceipt
```

**2. Start the Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the backend directory:

```
GEMINI_API_KEY=your_api_key_here
```

Start the server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

**3. Start the Frontend (in a new terminal):**

```bash
cd frontend
npm install
```

Create a `.env.local` file in the frontend directory:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`.

---

## Overview

AutoReceipt automates the **expense reporting process** for academics (professors, researchers, etc.) who attend conferences or work trips.

Traditionally, users must manually fill out a university-provided PDF form by extracting data (date, amount, purpose, etc.) from multiple receipts — a tedious and error-prone task.

This app eliminates that manual work by using **AI (Google Gemini)** and **automated PDF form filling (fillpdf)**. Simply upload your receipts (PDFs or images), and the system:

1. Extracts all relevant information (amounts, dates, origins, destinations, transport type, etc.) using Gemini AI
2. Automatically fills out the university's **Reisekostenabrechnung** PDF form
3. Returns the completed, ready-to-submit PDF to the user

---

## Project Structure

This project is organized as a monorepo with separate backend and frontend applications:

```
AutoReceipt/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI entrypoint
│   │   ├── antrag.py        # Antrag processing logic
│   │   ├── hinreise.py      # Outbound journey processing
│   │   ├── ruckreise.py     # Return journey processing
│   │   ├── hotel.py         # Hotel/conference processing
│   │   └── templates/       # PDF templates
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   ├── profile/
│   │   └── screens/
│   │       ├── AntragUploadScreen.tsx
│   │       ├── CompletionScreen.tsx
│   │       ├── FlightUploadScreen.tsx
│   │       ├── HotelUploadScreen.tsx
│   │       ├── LandingScreen.tsx
│   │       ├── ProcessingScreen.tsx
│   │       └── VerificationScreen.tsx
│   ├── components/
│   │   ├── FileUpload.tsx
│   │   ├── Navigation.tsx
│   │   ├── ProcessingAnimation.tsx
│   │   ├── StepIndicator.tsx
│   │   ├── SuccessAnimation.tsx
│   │   └── SummaryCard.tsx
│   ├── context/
│   │   └── AppContext.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   ├── userProfile.ts
│   │   └── verification.ts
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
├── .gitignore
└── README.md
```

---

## How It Works

### 1. Input
The user provides one or multiple receipts — either as **images** (`.jpg`, `.png`, etc.) or **PDFs** — through the web interface or API.

### 2. Document Preparation
Each document is processed and converted (if necessary) into a format suitable for the **Gemini Vision API**:
- PDFs are converted to images using `pdf2image`
- Images are loaded and converted to byte arrays via `Pillow (PIL)`

### 3. Data Extraction (Gemini API)
A prompt is sent to **Google's Gemini 2.5 Flash model**, which analyzes the receipts and extracts structured travel expense information in **JSON format**.

### 4. PDF Form Filling
The extracted JSON is then passed into **fillpdf**, which automates the population of PDF form fields in the university's **Reisekostenabrechnung** form.

### 5. Output
The system generates a **filled PDF document** ready for submission.

---

## API Endpoints

### Health Check
```
GET /api/health
```

### Process Trip (Main Endpoint)
```
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
```

### Download Generated PDF
```
GET /api/download/Reisekostenabrechnung_ausgefuellt.pdf
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Frontend | Next.js (React/TypeScript) |
| AI Model | Google Gemini 2.5 Flash |
| PDF Processing | fillpdf, pdf2image, PyMuPDF |
| Image Processing | Pillow (PIL) |
| PDF Rendering | Poppler |

---

## Security and Privacy

- API keys are stored in environment variables (never committed)
- Uploaded files are processed in temporary directories
- No user data or receipts are stored permanently
- CORS is configured for local development only

---

## Development Notes

### Running the Full Pipeline

The processing pipeline runs in this order:
1. **Antrag** - Extracts applicant data from Dienstreiseantrag
2. **Hinreise** - Processes outbound journey receipts
3. **Ruckreise** - Processes return journey receipts
4. **Hotel** - Processes accommodation and conference receipts

### API Documentation

When the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Author

Project by: **Adam Mekki**

Goal: Automate and simplify academic travel reimbursement using AI and PDF automation.

---

## License

This project is part of a thesis and is intended for educational purposes.
