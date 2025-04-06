import spacy
from collections import defaultdict

nlp = spacy.load("en_core_web_sm")

JOB_SKILLS = {
    "Software Engineer": ["python", "java", "c++", "sql", "git", "algorithms", "docker", "linux", "debugging", "oop"],
    "Data Scientist": ["python", "r", "sql", "pandas", "tensorflow", "statistics", "numpy", "matplotlib", "machine learning", "data visualization"],
    "Frontend Developer": ["javascript", "html", "css", "react", "angular", "typescript", "responsive design", "ui/ux", "webpack", "redux"],
    "Backend Developer": ["python", "java", "node.js", "django", "spring", "rest api", "microservices", "database design", "aws", "docker"],
    "DevOps Engineer": ["aws", "docker", "kubernetes", "ci/cd", "terraform", "ansible", "linux", "bash scripting", "monitoring", "cloud computing"],
    "Data Engineer": ["python", "sql", "etl", "hadoop", "spark", "airflow", "data warehousing", "nosql", "aws", "big data"],
    "Machine Learning Engineer": ["python", "tensorflow", "pytorch", "machine learning", "deep learning", "nlp", "computer vision", "scikit-learn", "data pipelines", "model deployment"],
    "Product Manager": ["product strategy", "market research", "agile", "scrum", "user stories", "roadmapping", "stakeholder management", "metrics analysis", "prototyping", "customer development"],
    "UX Designer": ["user research", "wireframing", "prototyping", "figma", "sketch", "usability testing", "interaction design", "information architecture", "ui design", "user personas"],
    "Cybersecurity Analyst": ["network security", "vulnerability assessment", "siem", "firewalls", "incident response", "penetration testing", "security compliance", "threat intelligence", "encryption", "risk assessment"],
    "Cloud Architect": ["aws", "azure", "google cloud", "cloud migration", "infrastructure as code", "serverless", "security architecture", "scalability", "cost optimization", "devops"],
    "Full Stack Developer": ["javascript", "python", "react", "node.js", "express", "mongodb", "rest api", "html/css", "git", "aws"],
    "QA Engineer": ["test automation", "selenium", "junit", "testng", "manual testing", "qa methodologies", "bug tracking", "performance testing", "security testing", "continuous integration"],
    "Business Analyst": ["requirements gathering", "process modeling", "data analysis", "sql", "power bi", "stakeholder management", "use cases", "user stories", "gap analysis", "uml"],
    "Technical Writer": ["documentation", "technical communication", "markdown", "git", "api documentation", "user manuals", "content strategy", "information architecture", "editing", "tools documentation"],
    "Systems Administrator": ["linux", "windows server", "networking", "active directory", "virtualization", "backup solutions", "monitoring", "scripting", "it security", "troubleshooting"],
    "Mobile Developer": ["swift", "kotlin", "react native", "flutter", "mobile ui", "rest api", "firebase", "performance optimization", "app store", "ci/cd"],
    "Database Administrator": ["sql", "database design", "performance tuning", "backup/recovery", "nosql", "data modeling", "etl", "security", "cloud databases", "replication"],
    "Network Engineer": ["cisco", "routing", "switching", "vpn", "wan", "lan", "network security", "tcp/ip", "firewalls", "sdn"],
    "AI Research Scientist": ["python", "machine learning", "deep learning", "research", "pytorch", "tensorflow", "mathematics", "publications", "nlp", "reinforcement learning"]
}

SKILL_WEIGHTS = {
    "python": 1.5, "tensorflow": 2.0, "aws": 1.8, "docker": 1.7, 
    "kubernetes": 2.2, "sql": 1.3, "machine learning": 2.1, "react": 1.6,
    "javascript": 1.4, "pytorch": 2.0, "ci/cd": 1.7, "terraform": 1.9,
    "data pipelines": 1.8, "security": 1.9, "cloud computing": 1.8,
    "deep learning": 2.2, "nlp": 2.1, "spark": 1.9, "airflow": 1.8
}

def extract_skills(text):
    """Extract skills using NLP and keyword matching"""
    text = text.lower()
    skills = set()
    
    # Method 1: Direct keyword matching
    for skill in set().union(*JOB_SKILLS.values()):
        if skill in text:
            skills.add(skill)
    
    # Method 2: NLP processing
    doc = nlp(text)
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN") and len(token.text) > 3:
            skills.add(token.text)
    
    return list(skills)

def match_resume_to_jobs(resume_text):
    """Calculate matches for ALL job roles"""
    resume_skills = extract_skills(resume_text)
    results = []
    
    for job_title, required_skills in JOB_SKILLS.items():
        matched = [s for s in required_skills if s in resume_skills]
        base_score = (len(matched) / len(required_skills)) * 100
        weighted_score = sum(SKILL_WEIGHTS.get(s, 1.0) for s in matched)
        
        results.append({
            "job_title": job_title,
            "base_score": round(base_score, 1),
            "weighted_score": round(weighted_score, 1),
            "matched_skills": matched,
            "missing_skills": list(set(required_skills) - set(matched))
        })
    
    return sorted(results, key=lambda x: x["weighted_score"], reverse=True)