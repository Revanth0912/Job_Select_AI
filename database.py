import sqlite3

def create_database():
    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()
    
    # Candidates table with ON DELETE CASCADE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            skills TEXT,
            resume_path TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Job matches table with all required columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            job_title TEXT NOT NULL,
            base_score REAL NOT NULL,
            weighted_score REAL NOT NULL,
            matched_skills TEXT,
            missing_skills TEXT,
            status TEXT DEFAULT 'Pending',
            notes TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_matches_candidate ON job_matches(candidate_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_matches_status ON job_matches(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_matches_score ON job_matches(weighted_score DESC)')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()