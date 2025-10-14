# 🧾 AI-Powered Receipt-to-PDF Automation

## 📖 Overview

This project automates the **expense reporting process** for academics (professors, researchers, etc.) who attend conferences or work trips.  

Traditionally, they must manually fill out a university-provided PDF form by extracting data (date, amount, purpose, etc.) from multiple receipts — a tedious and error-prone task.  

This app eliminates that manual work by using **AI (Gemini)** and **automated PDF form filling (fillpdf)**. Simply upload your receipts (PDFs or images), and the system:
1. Extracts all relevant information (amounts, dates, origins, destinations, transport type, etc.) using Gemini.
2. Automatically fills out the university’s **Reisekostenabrechnung** PDF form.
3. Returns the completed, ready-to-submit PDF to the user.

---

## 🧠 How It Works

### 1. Input  
The user provides one or multiple receipts — either as **images** (`.jpg`, `.png`, etc.) or **PDFs**.

### 2. Document Preparation  
Each document is processed and converted (if necessary) into a format suitable for the **Gemini Vision API**:
- PDFs are converted to images using `pdf2image`.
- Images are loaded and converted to byte arrays via `Pillow (PIL)`.

### 3. Data Extraction (Gemini API)  
A prompt is sent to **Google’s Gemini 2.5 Flash model**, which analyzes the receipts and extracts structured travel expense information in **JSON format**, for example:
```json
{
  "Hinreise_von": "Frankfurt",
  "Hinreise_nach": "China",
  "Flugzeug_Hinreise": "1500€",
  "Hinreise_Beginn": "12.05.2026",
  "Hinreise_Uhrzeit": "17:00",
  "Verkehrsmittel Hinreise": "Flugzeug"
}
```

### 4. PDF Form Filling  
The extracted JSON is then passed into **fillpdf**, a Python library that automates the population of PDF form fields.  
Each key in the JSON corresponds to a specific field in the university’s **Reisekostenabrechnung** (travel expense form).  
`fillpdf` takes care of writing these values into a new, filled version of the form.

## 5. Output

After successful execution, the program generates a **filled PDF document** named `filled_form.pdf`.  
This file can be reviewed and directly submitted to the university’s finance department for reimbursement.

---

## 🧩 Tech Stack

| Component | Purpose |
|------------|----------|
| **Python 3.x** | Core programming language |
| **Google Gemini 2.5 Flash** | AI model for visual and textual data extraction |
| **fillpdf** | Library for automated PDF form filling |
| **pdf2image** | Converts PDFs to images for AI vision processing |
| **Pillow (PIL)** | Image handling and conversion |
| **dotenv** | Securely manages API keys and environment variables |
| **Poppler** | Required by `pdf2image` for rendering PDF pages |

---

## 🛠️ File Structure
```bash
├── hinreise.py                 # Main application script
├── .env                        # Environment variables (API key, Poppler path)
├── requirements.txt            # Python dependencies
├── Reisekostenabrechnung_*.pdf # University PDF form template
├── Receipt_*.pdf / .jpg        # Input receipt examples
└── filled_form.pdf             # Generated filled output
```

## 🔒 Security & Privacy
- No user data or receipts are uploaded or stored externally

## 🛠️ Current Work in Progress

The project is actively under development. Current focus areas include:

1. **Complete Information Extraction & PDF Filling**  
   - Extending the AI extraction to cover **all fields in the university’s Reisekostenabrechnung form**, including outbound and return trips, accommodations, and miscellaneous expenses.  
   - Ensuring **accurate mapping** from extracted JSON to all PDF fields for fully automated form completion.

2. **User Interface (UI) Development**  
   - Building a **user-friendly interface** that allows users to easily upload receipts (PDFs or images).  
   - Providing **real-time feedback** on extracted data and letting users review before generating the final PDF.  
   - Designing the UI to support both **desktop and web-based usage**, making the app accessible to a wide range of users.

These improvements aim to make the app a **complete end-to-end solution** for academic travel expense reporting, minimizing manual effort and errors.

## 👩‍💻 Author
Project by: [Adam Mekki]
Goal: Automate and simplify academic travel reimbursement using AI and PDF automation.
