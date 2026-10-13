"""
nlp_analyzer.py
---------------
Core NLP module for text extraction from PDF files, text cleaning,
boundary-aware skill extraction, and skill gap / match percentage analysis.
"""

import io
import re
from typing import Dict, List, Set, Tuple, Any
from pypdf import PdfReader
from skills_database import (
    SKILLS_TAXONOMY,
    SKILL_ALIASES,
    get_canonical_skill,
    get_skill_category,
    get_all_canonical_skills
)

def extract_text_from_pdf(pdf_file_stream: io.BytesIO) -> str:
    """
    Safely extract selectable text from an in-memory PDF stream.
    Does not save files to disk.

    Raises:
        ValueError: If PDF is encrypted, corrupted, or contains no selectable text.
    """
    try:
        reader = PdfReader(pdf_file_stream)
    except Exception as exc:
        raise ValueError(f"Could not read PDF file. It might be corrupted. Details: {str(exc)}")

    if reader.is_encrypted:
        try:
            # Attempt empty password decryption if applicable
            reader.decrypt("")
        except Exception:
            raise ValueError("The PDF file is password protected. Please upload an unlocked PDF.")

    extracted_pages = []
    for page_idx, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text() or ""
            if page_text.strip():
                extracted_pages.append(page_text)
        except Exception as page_exc:
            # Log/skip unreadable page and continue
            continue

    full_text = "\n".join(extracted_pages).strip()

    if not full_text:
        raise ValueError(
            "No readable text found in this PDF. The document may be an image-only scan "
            "or contains non-selectable graphics. Please upload a PDF with selectable text."
        )

    return full_text


def normalize_text_for_search(text: str) -> str:
    """
    Normalize text by lowering case, standardizing line breaks,
    and normalizing spaces while preserving special characters
    common in technology names (e.g., +, #, /, ., -).
    """
    # Replace non-breaking spaces and tabs with standard space
    text = re.sub(r'[\r\t\f\v]+', ' ', text)
    # Convert consecutive spaces to single space
    text = re.sub(r'[ ]+', ' ', text)
    return text.lower()


def _is_short_ambiguous_skill(skill: str) -> bool:
    """Identify short abbreviations that need strict context boundary checks."""
    return skill in {"c", "r", "go", "ai", "ml", "ci", "cd", "ts", "js", "sh"}


def _match_short_skill_strict(raw_text: str, skill: str) -> bool:
    """
    Perform strict context matching for single-letter or short skills
    to prevent false positives with everyday English words (e.g. 'go', 'are', 'c', 'ai').
    """
    if skill == "c":
        # Look for 'C programming', 'C language', 'C/C++', 'C,', 'C and Python'
        patterns = [
            r'\bC\s*(\+\+|#)',              # C++ or C# already handled, but keeps safety
            r'\bC\s+language\b',
            r'\bC\s+programming\b',
            r'\b[Cc]\s*,\s*(?:C\+\+|Python|Java|SQL)',
            r'\b(?:Python|Java|SQL|C\+\+)\s*,\s*[Cc]\b',
            r'\b[Cc]\s*/\s*C\+\+',
            r'\bknowledge of C\b'
        ]
        return any(re.search(p, raw_text) for p in patterns)

    elif skill == "r":
        # Look for 'R programming', 'R language', 'R package', 'Python/R', 'R, Python'
        patterns = [
            r'\bR\s+language\b',
            r'\bR\s+programming\b',
            r'\bR\s+package\b',
            r'\b[Rr]\s*,\s*(?:Python|SQL|Tableau|SPSS|MATLAB)',
            r'\b(?:Python|SQL|Tableau|SPSS|MATLAB)\s*,\s*[Rr]\b',
            r'\bPython\s*/\s*R\b'
        ]
        return any(re.search(p, raw_text) for p in patterns)

    elif skill == "go":
        # Look for 'Golang', 'Go language', 'Go developer', 'Go / Python'
        patterns = [
            r'\bgolang\b',
            r'\b[Gg]o\s+language\b',
            r'\b[Gg]o\s+developer\b',
            r'\b[Gg]o\s+backend\b',
            r'\b(?:Python|Rust|Java|C\+\+)\s*,\s*[Gg]o\b',
            r'\b[Gg]o\s*,\s*(?:Python|Rust|Java|C\+\+)\b'
        ]
        return any(re.search(p, raw_text, re.IGNORECASE) for p in patterns)

    elif skill in {"ai", "ml"}:
        # Look for isolated AI or ML in technical context or uppercase
        patterns = [
            rf'\b{skill.upper()}\b',
            rf'\b{skill.lower()}\s+engineer\b',
            rf'\b{skill.lower()}\s+model\b',
            rf'\b{skill.lower()}\s*/\s*ml\b' if skill == 'ai' else r'\bai\s*/\s*ml\b'
        ]
        return any(re.search(p, raw_text) for p in patterns)

    return False


def extract_skills_from_text(raw_text: str) -> List[str]:
    """
    Extract technical and soft skills from freeform text using
    exact boundary-aware matching, alias normalization, and phrase prioritization.
    """
    if not raw_text or not raw_text.strip():
        return []

    norm_text = normalize_text_for_search(raw_text)
    detected_canonical_skills: Set[str] = set()

    # 1. Compile search terms (canonical skills + alias keys)
    canonical_skills = get_all_canonical_skills()
    alias_dict = SKILL_ALIASES

    # Combine all searchable phrases and sort by length descending
    # (so longer phrases like "machine learning" take precedence over "learning")
    search_phrases = set(canonical_skills) | set(alias_dict.keys())
    sorted_phrases = sorted(search_phrases, key=lambda s: len(s), reverse=True)

    for phrase in sorted_phrases:
        canonical = get_canonical_skill(phrase)
        if canonical in detected_canonical_skills:
            continue

        if _is_short_ambiguous_skill(phrase):
            if _match_short_skill_strict(raw_text, phrase):
                detected_canonical_skills.add(canonical)
            continue

        # Handle phrases with special regex characters (+, #, ., /, -)
        escaped_phrase = re.escape(phrase)

        # Word boundary handling:
        # Standard \b works for alphanumeric. For symbols like ++, #, or ., customize boundary
        start_bound = r'(?:^|[\s,;:\(\)\[\]\{\}\<\>\"\'`\/\\\|])'
        end_bound = r'(?:$|[\s,;:\(\)\[\]\{\}\<\>\"\'`\/\\\|\.\?])'

        pattern = rf'{start_bound}{escaped_phrase}{end_bound}'

        if re.search(pattern, norm_text):
            detected_canonical_skills.add(canonical)

    return sorted(list(detected_canonical_skills))


def analyze_skill_gap(resume_text: str, job_description_text: str) -> Dict[str, Any]:
    """
    Perform complete skill gap analysis between resume and job description.

    Returns:
        dict containing:
            - resume_skills: List of detected resume skills
            - job_skills: List of detected job description skills
            - matching_skills: Intersection
            - missing_skills: In job description but absent from resume
            - additional_skills: In resume but not specifically asked in JD
            - match_percentage: Transparent keyword match rate (float)
            - formula_explanation: Transparent mathematical string
            - category_breakdown: Breakdown by skill domains
            - actionable_recommendations: Suggestions to close gaps
    """
    resume_skills = extract_skills_from_text(resume_text)
    job_skills = extract_skills_from_text(job_description_text)

    set_resume = set(resume_skills)
    set_job = set(job_skills)

    matching_skills = sorted(list(set_resume & set_job))
    missing_skills = sorted(list(set_job - set_resume))
    additional_skills = sorted(list(set_resume - set_job))

    total_job_skills = len(set_job)
    matched_count = len(matching_skills)

    if total_job_skills > 0:
        match_percentage = round((matched_count / total_job_skills) * 100.0, 1)
        formula_explanation = f"({matched_count} Matched Skills ÷ {total_job_skills} Required Skills) × 100 = {match_percentage}%"
    else:
        match_percentage = 0.0
        formula_explanation = "0 required skills identified in job description."

    # Categorized breakdown
    category_breakdown = {}
    for category, category_skills in SKILLS_TAXONOMY.items():
        matched_in_cat = [s for s in matching_skills if s in category_skills]
        missing_in_cat = [s for s in missing_skills if s in category_skills]
        additional_in_cat = [s for s in additional_skills if s in category_skills]
        total_in_cat = len(matched_in_cat) + len(missing_in_cat)

        if total_in_cat > 0 or len(additional_in_cat) > 0:
            cat_pct = round((len(matched_in_cat) / total_in_cat * 100.0), 1) if total_in_cat > 0 else 0.0
            category_breakdown[category] = {
                "matched": matched_in_cat,
                "missing": missing_in_cat,
                "additional": additional_in_cat,
                "match_percentage": cat_pct,
                "total_required": total_in_cat
            }

    # Generate personalized recommendations based on gaps
    recommendations = _generate_recommendations(missing_skills, match_percentage, total_job_skills)

    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "additional_skills": additional_skills,
        "matched_count": matched_count,
        "missing_count": len(missing_skills),
        "additional_count": len(additional_skills),
        "total_job_skills_count": total_job_skills,
        "total_resume_skills_count": len(resume_skills),
        "match_percentage": match_percentage,
        "formula_explanation": formula_explanation,
        "category_breakdown": category_breakdown,
        "recommendations": recommendations,
        "disclaimer": (
            "This keyword match percentage represents strict textual alignment between extracted "
            "keywords in your resume and the provided job description. It does NOT evaluate contextual "
            "experience depth, project impact, or guarantee an interview or hiring outcome."
        )
    }


def _generate_recommendations(missing_skills: List[str], match_percentage: float, total_job_skills: int) -> List[Dict[str, str]]:
    """Generate constructive, beginner-friendly advice to help bridge detected skill gaps."""
    recs = []

    if total_job_skills == 0:
        recs.append({
            "title": "Clarify Job Requirements",
            "body": "The job description did not contain recognized standard skill keywords. Try pasting a more detailed job posting containing specific technical requirements.",
            "type": "info"
        })
        return recs

    if not missing_skills:
        recs.append({
            "title": "Outstanding Keyword Coverage",
            "body": "Your resume covers 100% of the recognized skills requested in this job description! Focus now on highlighting quantified metrics, measurable impact, and real-world project results.",
            "type": "success"
        })
        return recs

    # Group missing skills by category to provide structured advice
    grouped_missing: Dict[str, List[str]] = {}
    for skill in missing_skills:
        cat = get_skill_category(skill)
        grouped_missing.setdefault(cat, []).append(skill)

    for cat, skills in grouped_missing.items():
        skills_formatted = ", ".join(s.title() for s in skills[:5])
        if len(skills) > 5:
            skills_formatted += f" (+{len(skills) - 5} more)"

        if cat == "Cloud & DevOps":
            recs.append({
                "title": f"Highlight Infrastructure & Cloud ({skills_formatted})",
                "body": f"The employer specifically seeks {skills_formatted}. If you have hands-on experience, containerized applications, or deployed projects using these, explicitly mention them in your project or experience bullets.",
                "type": "warning"
            })
        elif cat == "Databases & Storage":
            recs.append({
                "title": f"Showcase Database Proficiencies ({skills_formatted})",
                "body": f"The position lists {skills_formatted}. Highlight your schema design, query optimization, or ORM experience alongside your primary backend stack.",
                "type": "warning"
            })
        elif cat == "Programming Languages" or cat == "Web & Frameworks":
            recs.append({
                "title": f"Core Technical Gaps ({skills_formatted})",
                "body": f"These are foundational technologies for the role: {skills_formatted}. If you know them, ensure they are listed in your Skills section. If learning them, consider building a small portfolio project to demonstrate practical competence.",
                "type": "danger"
            })
        elif cat == "Soft Skills & Collaboration":
            recs.append({
                "title": f"Integrate Soft Skills with Impact ({skills_formatted})",
                "body": f"The role values {skills_formatted}. Rather than listing them as isolated buzzwords, integrate them into your bullet points (e.g. 'Collaborated across cross-functional teams to deliver...').",
                "type": "info"
            })
        else:
            recs.append({
                "title": f"Targeted Skill Addition: {cat}",
                "body": f"Consider detailing your familiarity with {skills_formatted} where applicable in your projects or coursework.",
                "type": "info"
            })

    # Overall match score advice
    if match_percentage < 40.0:
        recs.insert(0, {
            "title": "Low Alignment Detected",
            "body": f"Your resume matches {match_percentage}% of the job's stated skills. Review if this role aligns with your target trajectory or tailor your resume specifically for this domain.",
            "type": "danger"
        })
    elif match_percentage < 70.0:
        recs.insert(0, {
            "title": "Moderate Alignment — Good Potential",
            "body": f"You match {match_percentage}% of the required skills. Addressing 2 to 3 key missing keywords that you have experience with can significantly boost your textual alignment.",
            "type": "warning"
        })
    else:
        recs.insert(0, {
            "title": "Strong Alignment",
            "body": f"Great alignment ({match_percentage}% match)! Double-check that your most relevant accomplishments match the primary job responsibilities.",
            "type": "success"
        })

    return recs
