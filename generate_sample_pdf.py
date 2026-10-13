"""
generate_sample_pdf.py
-----------------------
Generates a valid, realistic standard PDF resume without requiring external
third-party PDF generation libraries. Compatible with pypdf and standard PDF viewers.
"""

import os

def create_sample_pdf_bytes() -> bytes:
    """
    Constructs a valid PDF 1.4 binary document containing a realistic sample resume.
    """
    lines = [
        "Alex Mercer",
        "alex.mercer@example.com | San Francisco, CA | github.com/alexmercer",
        "--------------------------------------------------------------------------------",
        "PROFESSIONAL SUMMARY",
        "Passionate Software Engineer with 3+ years of experience specializing in Python,",
        "Flask, and relational databases. Proven track record of designing REST APIs,",
        "developing microservices with Docker, and collaborating in fast-paced Agile",
        "environments. Strong problem solving and communication skills.",
        "",
        "TECHNICAL SKILLS",
        "* Programming Languages: Python, JavaScript, SQL, HTML, CSS",
        "* Web & Frameworks: Flask, Django, React, Bootstrap, REST API",
        "* Databases: PostgreSQL, SQLite, Redis",
        "* DevOps & Tools: Git, GitHub, Docker, Linux, CI/CD, Unit Testing, Pytest",
        "* Soft Skills: Problem Solving, Teamwork, Communication, Time Management",
        "",
        "PROFESSIONAL EXPERIENCE",
        "Software Engineer | CloudScale Technologies (2022 - Present)",
        "- Engineered high-throughput REST APIs using Python and Flask, reducing latency by 35%.",
        "- Implemented caching with Redis and optimized queries for PostgreSQL databases.",
        "- Containerized backend services with Docker and automated testing via Git and CI/CD.",
        "- Participated in Agile sprint planning, daily standups, and peer code reviews.",
        "",
        "Junior Developer | DataPulse Solutions (2020 - 2022)",
        "- Built interactive frontend features using JavaScript, React, and Bootstrap.",
        "- Wrote automated test suites using Pytest, improving code coverage to 88%.",
        "- Demonstrated consistent teamwork, communication, and adaptability.",
        "",
        "EDUCATION",
        "Bachelor of Science in Computer Science | State University (2016 - 2020)"
    ]

    # Convert text lines into PDF content stream commands
    # BT = Begin Text, ET = End Text, Tf = Font, Td = Move, Tj = Show Text
    # Starting coordinates: x=50, y=750, line-height=18
    stream_commands = ["BT", "/F1 10 Tf", "50 760 Td", "16 TL"]
    for idx, line in enumerate(lines):
        # Escape parenthesis and backslashes in PDF text strings
        escaped_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        if idx == 0:
            # Name in larger font (simulated by spacing/text)
            stream_commands.append(f"({escaped_line}) Tj")
        elif line.startswith("PROFESSIONAL") or line.startswith("TECHNICAL") or line.startswith("EDUCATION"):
            stream_commands.append("T*")
            stream_commands.append(f"({escaped_line}) Tj")
        else:
            stream_commands.append("T*")
            stream_commands.append(f"({escaped_line}) Tj")

    stream_commands.append("ET")
    content_stream = "\n".join(stream_commands).encode("latin-1")

    # Assemble PDF objects
    objects = []
    
    # Object 1: Catalog
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    
    # Object 2: Pages
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    
    # Object 3: Page
    objects.append(
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\n"
        b"endobj\n"
    )
    
    # Object 4: Font
    objects.append(
        b"4 0 obj\n"
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\n"
        b"endobj\n"
    )
    
    # Object 5: Content stream
    stream_length = len(content_stream)
    obj5_header = f"5 0 obj\n<< /Length {stream_length} >>\nstream\n".encode("latin-1")
    obj5_footer = b"\nendstream\nendobj\n"
    objects.append(obj5_header + content_stream + obj5_footer)

    # Build PDF with xref table
    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    pdf_bytes = bytearray(header)
    offsets = []

    for obj in objects:
        offsets.append(len(pdf_bytes))
        pdf_bytes.extend(obj)

    xref_offset = len(pdf_bytes)
    xref = [f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"]
    for offset in offsets:
        xref.append(f"{offset:010d} 00000 n \n")

    trailer = (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    )

    pdf_bytes.extend("".join(xref).encode("latin-1"))
    pdf_bytes.extend(trailer.encode("latin-1"))

    return bytes(pdf_bytes)

def write_sample_pdf(filepath: str = "samples/sample_resume.pdf") -> str:
    """Generate and write sample resume PDF to target path."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    pdf_data = create_sample_pdf_bytes()
    with open(filepath, "wb") as f:
        f.write(pdf_data)
    return filepath

if __name__ == "__main__":
    out_path = write_sample_pdf()
    print(f"Sample resume created successfully at: {out_path}")
