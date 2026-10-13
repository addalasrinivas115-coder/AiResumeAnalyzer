# AI Resume & Skill Gap Analyzer

A beginner-friendly, privacy-first web application built with **Python**, **Flask**, and **Natural Language Processing (NLP)** that analyzes resumes against target job descriptions, identifies skill proficiencies and gaps, and computes an honest, transparent keyword match rate.

---

## 📌 Problem Statement

In today's competitive job market, candidates often submit resumes without knowing how well their skills align with the specific requirements of applicant tracking systems (ATS) or hiring managers. Existing commercial resume scanners often present critical issues:

1. **Opaque "Black-Box" Scoring**: Many tools present arbitrary scores or make deceptive claims about "guaranteed hiring probability" without showing candidates how the score was calculated.
2. **Data Privacy Risks**: Resumes contain sensitive personally identifiable information (PII). Many platforms permanently store, index, or monetize uploaded candidate data.
3. **Lack of Actionable Insights**: Candidates are frequently given low scores without clear, categorized breakdowns of what specific technical or soft skills are missing and how to bridge those gaps.
4. **False Matches on Technical Terms**: Basic keyword counters often fail on technical terminology, getting confused by punctuation in skills like `C++`, `C#`, `CI/CD`, and `REST API`, or confusing short acronyms with everyday English words.

**AI Resume & Skill Gap Analyzer** solves these problems by providing an open, transparent, in-memory, and boundary-aware skill analysis tool.

---

## 📖 Project Description

The **AI Resume & Skill Gap Analyzer** is a lightweight web application that allows users to upload a PDF resume and paste any target job description. The application parses the PDF in memory, extracts technical and soft skills using a boundary-aware NLP engine, and compares the candidate's skill set against the job posting.

It delivers an interactive dashboard featuring:
- An animated match gauge with a transparent mathematical formula.
- Color-coded badges for **matching skills**, **missing skills (skill gaps)**, and **additional candidate strengths**.
- Domain-by-domain categorization (Languages, Web, Databases, Cloud/DevOps, Data/AI, Tools, Soft Skills).
- Tailored, constructive recommendations for closing identified skill gaps.

---

## ✨ Features

- **Safe In-Memory File Handling**: Uploaded PDF resumes are processed entirely in RAM using Python's `io.BytesIO` and `pypdf`. Resumes are **never written to disk or permanently stored**.
- **Boundary-Aware NLP Skill Extraction**: Accurately recognizes over 300 technical and soft skills, properly handling multi-word technologies (*Machine Learning*, *REST API*, *Spring Boot*) and symbols (*C++*, *C#*, *CI/CD*).
- **Synonym & Alias Normalization**: Maps abbreviations and alternate terms to canonical skills (e.g., `js` $\rightarrow$ `javascript`, `postgres` $\rightarrow$ `postgresql`, `k8s` $\rightarrow$ `kubernetes`, `golang` $\rightarrow$ `go`).
- **Transparent Mathematical Match Rate**: Calculates score using an honest formula displayed directly on screen:
  $$\text{Match Percentage} = \left(\frac{\text{Number of Matched Skills}}{\text{Total Required Skills in Job Description}}\right) \times 100$$
- **Categorized Skill Breakdown**: Groups skills into 7 distinct domains with visual progress bars.
- **Actionable Gap Recommendations**: Provides tailored advice on what projects or proficiencies to highlight based on missing skills.
- **Pre-Built Sample Test Data**:
  - Sample resume (`samples/sample_resume.pdf`) available for download or immediate testing.
  - **Auto-fill Sample Job Description** button on the UI for quick 1-click testing.
- **Comprehensive Validation**: Validates file types (`.pdf`), empty files, oversized uploads (>5MB limit), empty job descriptions, and unreadable/scanned PDFs.
- **Clean, Modern Responsive UI**: Crafted with modern CSS (Flexbox/Grid, Inter font, pill badges, and print-to-PDF styles).
- **Ethical AI Disclaimer**: Prominently clarifies that keyword matching measures textual alignment only and is not a hiring guarantee or candidate competence assessment.

---

## 🛠️ Technologies Used

- **Backend**:
  - [Python 3.9+](https://www.python.org/)
  - [Flask 3.0+](https://palletsprojects.com/p/flask/) - Lightweight web framework and routing
  - [Werkzeug 3.0+](https://palletsprojects.com/p/werkzeug/) - WSGI utilities and file handling
- **PDF & Text Processing**:
  - [pypdf 4.0+](https://pypdf.readthedocs.io/) - Pure Python PDF text extraction
  - Python standard library: `io.BytesIO`, `re` (Regular Expressions), `typing`, `os`
- **Frontend**:
  - **HTML5** - Semantic layout and accessibility
  - **CSS3** - Custom responsive styling, CSS variables, glassmorphic cards, SVG progress ring
  - **JavaScript (ES6+)** - Drag-and-drop file upload, live character counting, Fetch API for sample loading
- **Testing**:
  - Python `unittest` module

---

## 📁 Project Structure

```
AiResumeAnalyzer/
│
├── app.py                         # Flask application, routing, and upload handling
├── skills_database.py             # Curated skill taxonomy, domains, and aliases
├── nlp_analyzer.py                # In-memory PDF text extraction & NLP matching logic
├── generate_sample_pdf.py         # Pure Python script to generate sample resume PDF
├── test_app.py                    # Automated test suite (unit and route tests)
├── requirements.txt               # Project Python dependencies
├── .gitignore                     # Git ignore rules for venv, cache, and temp files
├── README.md                      # Complete project documentation
│
├── samples/
│   ├── sample_resume.pdf          # Pre-built sample resume PDF for testing
│   └── sample_job_description.txt # Pre-built sample job description text
│
├── static/
│   ├── css/
│   │   └── style.css              # Custom responsive stylesheet
│   └── js/
│       └── main.js                # Frontend interactions, drag & drop, sample loader
│
└── templates/
    ├── base.html                  # Base layout with navbar, alerts, and disclaimer footer
    ├── index.html                 # Main dashboard with upload form and sample controls
    └── results.html               # Results report dashboard with gauge, tags, and advice
```

---

## ⚙️ Installation Steps

Follow these steps to set up the project on your machine (instructions shown for Windows):

### 1. Prerequisites
Ensure **Python 3.9 or higher** is installed:
```powershell
python --version
```

### 2. Navigate to the Project Directory
```powershell
cd c:\Users\Asrin\Downloads\AiResumeAnalyzer
```

### 3. Create a Virtual Environment
Create an isolated Python virtual environment named `venv`:
```powershell
python -m venv venv
```

### 4. Activate the Virtual Environment
- **In Windows PowerShell:**
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\venv\Scripts\Activate.ps1
  ```
- **In Windows Command Prompt (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```

*(Your terminal prompt will now show `(venv)` at the beginning).*

### 5. Install Dependencies
Install all required packages from `requirements.txt`:
```powershell
pip install -r requirements.txt
```

---

## 🚀 How to Run the Flask Application

### 1. Start the Server
Run the Flask application from your activated virtual environment:
```powershell
python app.py
```

You should see output similar to:
```text
============================================================
AI Resume & Skill Gap Analyzer is starting...
Local URL: http://127.0.0.1:5000
Safe in-memory PDF processing enabled (no files saved).
============================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### 2. Open in Your Browser
Navigate to:
```
http://127.0.0.1:5000
```

### 3. How to Test It
- **Quick 1-Click Test**:
  1. Click **"Download Sample Resume (.pdf)"** on the homepage and drop the file into the upload area.
  2. Click **"Auto-fill Sample Job Description"** to load the sample backend engineer requirements.
  3. Click **"Analyze Resume & Calculate Skill Gap"**.
- **Automated Tests**:
  To execute the unit and integration test suite:
  ```powershell
  python -m unittest test_app.py
  ```

---

## 🔮 Future Improvements

1. **Semantic Embeddings & Deep NLP**:
   - Integrate transformer embeddings (e.g., Sentence-Transformers / BERT) to detect semantic similarity beyond exact keywords (e.g., matching "Postgres" experience to "Relational Database Design" requirements).
2. **Optical Character Recognition (OCR)**:
   - Add OCR capability (e.g., via `pytesseract`) to extract text from scanned or graphic-heavy PDF resumes that lack selectable text.
3. **Multi-Format Resume Support**:
   - Add support for `.docx`, `.txt`, and Markdown resume uploads alongside PDF.
4. **Weighted Scoring & Seniority Detection**:
   - Allow job descriptions to distinguish "Must-Have" requirements from "Nice-to-Have" bonuses, calculating weighted match percentages.
5. **Resume Optimization Suggestions**:
   - Suggest action verbs, quantified achievement formulas (e.g., Google X-Y-Z formula: "Accomplished [X], as measured by [Y], by doing [Z]"), and structural improvements.
6. **Exportable PDF Analysis Reports**:
   - Enable single-click downloading of the complete skill gap analysis report as a formatted PDF.
