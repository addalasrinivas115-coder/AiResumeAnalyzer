"""
skills_database.py
------------------
A curated, categorized taxonomy of technical and soft skills, complete with
synonyms, aliases, and canonical naming for accurate extraction and gap analysis.
"""

# Categorized Skill Taxonomy
# Format: Category Name -> List of canonical skill names
SKILLS_TAXONOMY = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "c",
        "go", "rust", "php", "ruby", "swift", "kotlin", "r", "matlab",
        "scala", "dart", "perl", "bash", "shell", "powershell", "sql",
        "html", "css", "sass", "solidity"
    ],
    "Web & Frameworks": [
        "react", "angular", "vue.js", "next.js", "nuxt.js", "svelte",
        "flask", "django", "fastapi", "node.js", "express.js", "spring boot",
        "asp.net", "ruby on rails", "laravel", "tailwind css", "bootstrap",
        "jquery", "graphql", "rest api", "soap", "redux", "websockets",
        "microservices"
    ],
    "Databases & Storage": [
        "postgresql", "mysql", "sqlite", "mongodb", "redis", "cassandra",
        "oracle", "microsoft sql server", "dynamodb", "elasticsearch",
        "mariadb", "firebase", "supabase", "neo4j", "snowflake", "bigquery"
    ],
    "Cloud & DevOps": [
        "aws", "microsoft azure", "google cloud", "docker", "kubernetes",
        "terraform", "ansible", "jenkins", "github actions", "gitlab ci",
        "ci/cd", "linux", "nginx", "apache", "serverless", "helm",
        "prometheus", "grafana", "circleci", "vagrant"
    ],
    "Data Science & AI / ML": [
        "machine learning", "deep learning", "artificial intelligence",
        "natural language processing", "computer vision", "tensorflow",
        "pytorch", "scikit-learn", "keras", "pandas", "numpy", "scipy",
        "matplotlib", "seaborn", "hugging face", "llms", "generative ai",
        "langchain", "data analysis", "data visualization", "tableau",
        "power bi", "feature engineering", "predictive modeling"
    ],
    "Tools, Testing & Architecture": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "agile", "scrum", "kanban", "unit testing", "pytest", "jest",
        "junit", "selenium", "cypress", "postman", "swagger", "figma",
        "test driven development", "object oriented programming",
        "system design", "data structures", "algorithms"
    ],
    "Soft Skills & Collaboration": [
        "communication", "teamwork", "leadership", "problem solving",
        "critical thinking", "time management", "adaptability",
        "collaboration", "project management", "mentoring",
        "conflict resolution", "creativity", "attention to detail",
        "presentation skills", "stakeholder management", "work ethic"
    ]
}

# Synonyms and alias normalization mapping
# Map variation/slang/abbreviation -> canonical skill name
SKILL_ALIASES = {
    # Programming Languages
    "py": "python",
    "python3": "python",
    "js": "javascript",
    "ts": "typescript",
    "golang": "go",
    "cpp": "c++",
    "csharp": "c#",
    "c sharp": "c#",
    "sh": "shell",
    "html5": "html",
    "css3": "css",

    # Web & Frameworks
    "reactjs": "react",
    "react.js": "react",
    "vue": "vue.js",
    "vuejs": "vue.js",
    "next": "next.js",
    "nextjs": "next.js",
    "nodejs": "node.js",
    "express": "express.js",
    "expressjs": "express.js",
    "spring": "spring boot",
    "springboot": "spring boot",
    "restful api": "rest api",
    "rest apis": "rest api",
    "restful": "rest api",
    "rest": "rest api",
    "tailwind": "tailwind css",
    "tailwindcss": "tailwind css",
    "micro-services": "microservices",
    "micro service": "microservices",

    # Databases
    "postgres": "postgresql",
    "pg": "postgresql",
    "mongo": "mongodb",
    "ms sql": "microsoft sql server",
    "mssql": "microsoft sql server",
    "sql server": "microsoft sql server",
    "elastic search": "elasticsearch",

    # Cloud & DevOps
    "amazon web services": "aws",
    "azure": "microsoft azure",
    "gcp": "google cloud",
    "google cloud platform": "google cloud",
    "k8s": "kubernetes",
    "ci cd": "ci/cd",
    "cicd": "ci/cd",
    "continuous integration": "ci/cd",
    "gh actions": "github actions",
    "git hub": "github",
    "git lab": "gitlab",

    # AI & Data
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "deeplearning": "deep learning",
    "cv": "computer vision",
    "torch": "pytorch",
    "tf": "tensorflow",
    "sklearn": "scikit-learn",
    "genai": "generative ai",
    "gen ai": "generative ai",
    "large language models": "llms",
    "llm": "llms",
    "bi": "power bi",
    "powerbi": "power bi",

    # Tools & Testing
    "tdd": "test driven development",
    "oop": "object oriented programming",
    "oop concepts": "object oriented programming",
    "unit tests": "unit testing",
    "dsa": "data structures",
    "sys design": "system design",

    # Soft skills
    "interpersonal skills": "communication",
    "verbal communication": "communication",
    "written communication": "communication",
    "team player": "teamwork",
    "collaborative": "collaboration",
    "troubleshooting": "problem solving",
    "analytical thinking": "critical thinking",
    "time-management": "time management"
}

def get_canonical_skill(skill_str: str) -> str:
    """Normalize a skill string to its canonical database name."""
    cleaned = skill_str.strip().lower()
    return SKILL_ALIASES.get(cleaned, cleaned)

def get_skill_category(canonical_skill: str) -> str:
    """Find the category for a given canonical skill."""
    for category, skills in SKILLS_TAXONOMY.items():
        if canonical_skill in skills:
            return category
    return "Other Technical / Professional Skills"

def get_all_canonical_skills() -> set:
    """Return all canonical skills across all categories."""
    all_skills = set()
    for skills in SKILLS_TAXONOMY.values():
        all_skills.update(skills)
    return all_skills
