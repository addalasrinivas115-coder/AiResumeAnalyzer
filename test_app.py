"""
test_app.py
-----------
Comprehensive unit and integration test suite for the AI Resume & Skill Gap Analyzer.
Tests:
- Skills database taxonomy and alias normalization
- NLP boundary-aware extraction (single-word, multi-word, special characters)
- Skill gap analysis, formula transparency, and recommendations
- In-memory PDF text extraction
- Flask routes, file validation, and error handling
"""

import io
import unittest
from skills_database import (
    get_canonical_skill,
    get_skill_category,
    get_all_canonical_skills,
    SKILLS_TAXONOMY
)
from nlp_analyzer import (
    extract_skills_from_text,
    analyze_skill_gap,
    extract_text_from_pdf,
    normalize_text_for_search
)
from generate_sample_pdf import create_sample_pdf_bytes
from app import app


class TestSkillsDatabase(unittest.TestCase):
    """Test skill database dictionaries and normalization routines."""

    def test_alias_normalization(self):
        self.assertEqual(get_canonical_skill("js"), "javascript")
        self.assertEqual(get_canonical_skill("py"), "python")
        self.assertEqual(get_canonical_skill("postgres"), "postgresql")
        self.assertEqual(get_canonical_skill("k8s"), "kubernetes")
        self.assertEqual(get_canonical_skill("cpp"), "c++")
        self.assertEqual(get_canonical_skill("csharp"), "c#")
        self.assertEqual(get_canonical_skill("reactjs"), "react")
        self.assertEqual(get_canonical_skill("ci cd"), "ci/cd")

    def test_skill_categories(self):
        self.assertEqual(get_skill_category("python"), "Programming Languages")
        self.assertEqual(get_skill_category("flask"), "Web & Frameworks")
        self.assertEqual(get_skill_category("postgresql"), "Databases & Storage")
        self.assertEqual(get_skill_category("docker"), "Cloud & DevOps")
        self.assertEqual(get_skill_category("machine learning"), "Data Science & AI / ML")
        self.assertEqual(get_skill_category("communication"), "Soft Skills & Collaboration")

    def test_taxonomy_populated(self):
        canonical_set = get_all_canonical_skills()
        self.assertGreater(len(canonical_set), 80)
        self.assertIn("python", canonical_set)
        self.assertIn("docker", canonical_set)


class TestNLPAnalyzer(unittest.TestCase):
    """Test text processing, boundary checking, and skill extraction."""

    def test_normalize_text(self):
        sample = "Python\t\tDeveloper\r\nwith  C++  and   Docker"
        norm = normalize_text_for_search(sample)
        self.assertIn("c++", norm)
        self.assertIn("python developer", norm)

    def test_multi_word_skill_extraction(self):
        text = "Experienced in Machine Learning, REST API development, and CI/CD pipelines."
        skills = extract_skills_from_text(text)
        self.assertIn("machine learning", skills)
        self.assertIn("rest api", skills)
        self.assertIn("ci/cd", skills)

    def test_single_word_boundary_matching(self):
        # 'cat', 'city', 'format' should not trigger 'c'
        text_without_c = "The cat went to the city in the morning."
        skills = extract_skills_from_text(text_without_c)
        self.assertNotIn("c", skills)

        # Technical context for C
        text_with_c = "Proficient in C, C++, and Python."
        skills_c = extract_skills_from_text(text_with_c)
        self.assertIn("c", skills_c)
        self.assertIn("c++", skills_c)
        self.assertIn("python", skills_c)

    def test_alias_extraction(self):
        text = "Built web apps using ReactJS, NodeJS, and Postgres with Docker."
        skills = extract_skills_from_text(text)
        self.assertIn("react", skills)
        self.assertIn("node.js", skills)
        self.assertIn("postgresql", skills)
        self.assertIn("docker", skills)

    def test_skill_gap_analysis_math(self):
        resume = "Experienced in Python, Flask, Docker, and Git."
        jd = "Looking for an engineer skilled in Python, Flask, Docker, Kubernetes, and AWS."

        analysis = analyze_skill_gap(resume, jd)

        # Job skills: python, flask, docker, kubernetes, aws (5 skills)
        # Resume skills: python, flask, docker, git (4 skills)
        # Matched: python, flask, docker (3 skills)
        # Missing: kubernetes, aws (2 skills)
        # Additional: git (1 skill)
        self.assertIn("python", analysis["matching_skills"])
        self.assertIn("flask", analysis["matching_skills"])
        self.assertIn("docker", analysis["matching_skills"])

        self.assertIn("kubernetes", analysis["missing_skills"])
        self.assertIn("aws", analysis["missing_skills"])

        self.assertIn("git", analysis["additional_skills"])

        # Match % = 3 / 5 * 100 = 60.0%
        self.assertEqual(analysis["match_percentage"], 60.0)
        self.assertIn("3 Matched Skills ÷ 5 Required Skills", analysis["formula_explanation"])
        self.assertIn("disclaimer", analysis)
        self.assertGreater(len(analysis["recommendations"]), 0)

    def test_empty_jd_edge_case(self):
        resume = "Python, Flask"
        jd = "A role without recognized technical terms."
        analysis = analyze_skill_gap(resume, jd)
        self.assertEqual(analysis["match_percentage"], 0.0)
        self.assertEqual(analysis["total_job_skills_count"], 0)


class TestPDFExtraction(unittest.TestCase):
    """Test in-memory PDF parsing and safety checks."""

    def test_sample_pdf_text_extraction(self):
        pdf_bytes = create_sample_pdf_bytes()
        stream = io.BytesIO(pdf_bytes)
        text = extract_text_from_pdf(stream)
        self.assertIn("Alex Mercer", text)
        self.assertIn("Python", text)
        self.assertIn("Flask", text)
        self.assertIn("Docker", text)

    def test_corrupted_pdf_error(self):
        corrupted_stream = io.BytesIO(b"Not a valid PDF file stream")
        with self.assertRaises(ValueError):
            extract_text_from_pdf(corrupted_stream)


class TestFlaskRoutes(unittest.TestCase):
    """Test Flask web application routes and validations."""

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            b"AI Resume &amp; Skill Gap Analyzer" in response.data or
            b"AI Resume & Skill Gap Analyzer" in response.data
        )
        self.assertIn(b"Upload Resume", response.data)

    def test_sample_resume_download(self):
        response = self.client.get("/sample-resume")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/pdf")
        self.assertTrue(response.data.startswith(b"%PDF"))

    def test_sample_job_description_api(self):
        response = self.client.get("/api/sample-job-description")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "success")
        self.assertIn("Python", json_data["content"])

    def test_analyze_no_file_validation(self):
        response = self.client.post("/analyze", data={
            "job_description": "We need a Python developer."
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please select a resume file", response.data)

    def test_analyze_non_pdf_file_validation(self):
        data = {
            "resume": (io.BytesIO(b"Hello world text"), "resume.txt"),
            "job_description": "We need a Python developer with Flask experience."
        }
        response = self.client.post("/analyze", data=data, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid file format", response.data)

    def test_analyze_empty_job_description(self):
        pdf_bytes = create_sample_pdf_bytes()
        data = {
            "resume": (io.BytesIO(pdf_bytes), "sample.pdf"),
            "job_description": ""
        }
        response = self.client.post("/analyze", data=data, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please enter or paste a job description", response.data)

    def test_successful_analysis(self):
        pdf_bytes = create_sample_pdf_bytes()
        jd_text = (
            "We are seeking a Software Engineer skilled in Python, Flask, "
            "React, Docker, PostgreSQL, and Kubernetes. Excellent communication "
            "and problem solving skills required."
        )
        data = {
            "resume": (io.BytesIO(pdf_bytes), "sample_resume.pdf"),
            "job_description": jd_text
        }
        response = self.client.post("/analyze", data=data, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Skill Gap Analysis Report", response.data)
        self.assertIn(b"Matching Skills", response.data)
        self.assertIn(b"Missing Skills", response.data)
        self.assertIn(b"Transparent Formula", response.data)
        self.assertTrue(
            b"Ethical AI &amp; Privacy Notice" in response.data or
            b"Ethical AI & Privacy Notice" in response.data
        )


if __name__ == "__main__":
    unittest.main()
