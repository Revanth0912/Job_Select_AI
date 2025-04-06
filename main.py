import os
import csv
import sqlite3
import configparser
from match_candidates import match_resume_to_jobs, extract_skills
from parse_resume import parse_resume

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

def load_job_titles(csv_path):
    """Load job titles from CSV"""
    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            return [row["Job Title"] for row in csv.DictReader(file)]
    except Exception as e:
        print(f"Error loading job titles: {str(e)}")
        return []

def process_resume(filepath):
    """Process a single resume file and store results in database"""
    try:
        # Parse resume
        resume_text, email = parse_resume(filepath)
        if not resume_text:
            print(f"Skipping unreadable file: {filepath}")
            return

        # Extract candidate name from filename
        candidate_name = os.path.splitext(os.path.basename(filepath))[0].replace('_', ' ').title()
        
        # Process the resume
        skills = extract_skills(resume_text)
        matches = match_resume_to_jobs(resume_text, min_score=int(config.get('SETTINGS', 'min_match_score', fallback=40)))
        
        print(f"\n{'='*50}")
        print(f"Analyzing: {candidate_name}")
        print(f"Email: {email}")
        print(f"Top Skills: {', '.join(skills)[:200]}...")

        # Connect to database
        conn = sqlite3.connect("candidates.db")
        cursor = conn.cursor()

        # Insert or update candidate
        cursor.execute('''
            INSERT OR REPLACE INTO candidates (name, email, resume_path, skills)
            VALUES (?, ?, ?, ?)
        ''', (candidate_name, email, filepath, ','.join(skills)))
        
        # Get candidate ID
        candidate_id = cursor.execute('SELECT id FROM candidates WHERE email = ?', (email,)).fetchone()[0]

        # Delete old matches for this candidate
        cursor.execute('DELETE FROM job_matches WHERE candidate_id = ?', (candidate_id,))
        
        # Insert new matches
        for match in matches:
            cursor.execute('''
                INSERT INTO job_matches (
                    candidate_id, job_title, base_score, 
                    weighted_score, matched_skills, missing_skills
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                candidate_id,
                match['job_title'],
                match['base_score'],
                match['weighted_score'],
                ','.join(match['matched_skills']),
                ','.join(match['missing_skills'])
            ))
        
        conn.commit()
        conn.close()

        # Print top matches
        for match in matches[:3]:
            print(f"\n→ Role: {match['job_title']}")
            print(f"  Score: {match['base_score']}% (Weighted: {match['weighted_score']})")
            print(f"  ✅ Matched: {', '.join(match['matched_skills'])}")
            missing = match['missing_skills'][:5]
            print(f"  ❌ Missing: {', '.join(missing) if missing else 'None'}")

    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")

def main():
    # Get paths from config
    resume_folder = config.get('PATHS', 'resume_folder')
    job_csv = config.get('PATHS', 'job_csv')

    # Validate paths
    if not os.path.exists(job_csv):
        print(f"Error: Job CSV not found at {job_csv}")
        return
    if not os.path.exists(resume_folder):
        print(f"Error: Resume folder not found at {resume_folder}")
        return

    # Process all resumes
    for filename in os.listdir(resume_folder):
        if filename.lower().endswith(('.txt', '.pdf', '.docx')):
            process_resume(os.path.join(resume_folder, filename))

if __name__ == "__main__":
    main()