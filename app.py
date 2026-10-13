"""
app.py
------
AI Resume & Skill Gap Analyzer - Flask Web Application
Features:
- Safe, in-memory PDF extraction (no permanent storage of uploaded resumes).
- Transparent keyword match percentage calculation with ethical disclaimer.
- Skill extraction across technical and soft skills.
- Category breakdowns and actionable recommendations.
- Interactive dashboard with sample resume and job description loaders.
"""

import io
import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    jsonify
)
from werkzeug.exceptions import RequestEntityTooLarge

from nlp_analyzer import (
    extract_text_from_pdf,
    analyze_skill_gap,
    extract_skills_from_text
)
from generate_sample_pdf import write_sample_pdf

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "ai-resume-skill-analyzer-secret-2026")
# Limit upload size to 5 Megabytes
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf"}
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
SAMPLE_RESUME_PATH = os.path.join(SAMPLES_DIR, "sample_resume.pdf")
SAMPLE_JD_PATH = os.path.join(SAMPLES_DIR, "sample_job_description.txt")

# Ensure sample files exist on application startup
if not os.path.exists(SAMPLE_RESUME_PATH):
    try:
        write_sample_pdf(SAMPLE_RESUME_PATH)
    except Exception as e:
        app.logger.warning("Could not auto-generate sample resume: %s", e)


def allowed_file(filename: str) -> bool:
    """Check whether uploaded file has a valid .pdf extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    """Render the main input dashboard."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Handle resume upload and job description submission.
    Performs safe in-memory processing with comprehensive validation.
    """
    # 1. Validate resume upload
    if "resume" not in request.files:
        flash("Please select a resume file to upload.", "danger")
        return redirect(url_for("index"))

    resume_file = request.files["resume"]
    if resume_file.filename == "":
        flash("No file was selected. Please choose a PDF resume.", "danger")
        return redirect(url_for("index"))

    if not allowed_file(resume_file.filename):
        flash("Invalid file format. Only PDF files (.pdf) are supported.", "danger")
        return redirect(url_for("index"))

    # Read file content safely in-memory
    file_bytes = resume_file.read()

    # Check for empty file
    if len(file_bytes) == 0:
        flash("The uploaded PDF file is empty (0 bytes). Please upload a valid resume.", "danger")
        return redirect(url_for("index"))

    # Magic byte validation for PDF (%PDF-)
    if not file_bytes.startswith(b"%PDF"):
        flash("The file does not appear to be a valid PDF document.", "danger")
        return redirect(url_for("index"))

    # 2. Validate job description input
    job_description = request.form.get("job_description", "").strip()
    if not job_description:
        flash("Please enter or paste a job description to compare against.", "danger")
        return redirect(url_for("index"))

    if len(job_description) < 30:
        flash("The job description is too short. Please provide a more detailed job posting (at least 30 characters).", "warning")
        return redirect(url_for("index"))

    # 3. Extract text from PDF in memory (no disk write)
    try:
        resume_stream = io.BytesIO(file_bytes)
        resume_text = extract_text_from_pdf(resume_stream)
    except ValueError as ve:
        flash(str(ve), "danger")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"An unexpected error occurred while reading the PDF: {str(e)}", "danger")
        return redirect(url_for("index"))

    # 4. Perform NLP Skill Gap Analysis
    analysis_results = analyze_skill_gap(resume_text, job_description)

    # 5. Render results dashboard
    return render_template(
        "results.html",
        results=analysis_results,
        filename=resume_file.filename,
        resume_char_count=len(resume_text),
        jd_char_count=len(job_description),
        resume_preview=resume_text[:400] + ("..." if len(resume_text) > 400 else ""),
        jd_preview=job_description[:400] + ("..." if len(job_description) > 400 else "")
    )


@app.route("/sample-resume", methods=["GET"])
def download_sample_resume():
    """Download the included sample resume PDF."""
    if not os.path.exists(SAMPLE_RESUME_PATH):
        write_sample_pdf(SAMPLE_RESUME_PATH)

    return send_file(
        SAMPLE_RESUME_PATH,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="sample_resume.pdf"
    )


@app.route("/api/sample-job-description", methods=["GET"])
def get_sample_job_description():
    """API endpoint providing sample job description text for quick 1-click loading."""
    try:
        if os.path.exists(SAMPLE_JD_PATH):
            with open(SAMPLE_JD_PATH, "r", encoding="utf-8") as f:
                content = f.read()
            return jsonify({"status": "success", "content": content})
        else:
            return jsonify({"status": "error", "message": "Sample job description file not found."}), 404
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle uploads exceeding maximum allowed size."""
    flash("The uploaded file exceeds the 5MB size limit. Please upload a smaller PDF.", "danger")
    return redirect(url_for("index"))


@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 routes."""
    return render_template("index.html"), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 60)
    print("AI Resume & Skill Gap Analyzer is starting...")
    print(f"Local URL: http://127.0.0.1:{port}")
    print("Safe in-memory PDF processing enabled (no files saved).")
    print("=" * 60)
    app.run(host="127.0.0.1", port=port, debug=True)
