from flask import Flask, render_template, request, redirect, flash, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'

def get_db_connection():
    conn = sqlite3.connect("candidates.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def dashboard():
    conn = get_db_connection()
    
    # Get available job titles
    job_titles = [row[0] for row in conn.execute("SELECT DISTINCT job_title FROM job_matches").fetchall()]
    
    selected_job = request.args.get('job_title', 'all')
    status_filter = request.args.get('status', 'all')
    min_score = request.args.get('min_score', 0, type=float)
    
    # Base query
    if selected_job == 'all':
        query = '''
            SELECT c.id as candidate_id, c.name, c.email, 
                   m.job_title, m.base_score, m.weighted_score,
                   m.matched_skills, m.missing_skills, m.status, m.id as match_id
            FROM candidates c
            JOIN (
                SELECT candidate_id, MAX(weighted_score) as max_score
                FROM job_matches
                GROUP BY candidate_id
            ) best ON c.id = best.candidate_id
            JOIN job_matches m ON m.candidate_id = best.candidate_id AND m.weighted_score = best.max_score
            WHERE m.weighted_score >= ?
        '''
        params = [min_score]
    else:
        query = '''
            SELECT c.id as candidate_id, c.name, c.email,
                   m.job_title, m.base_score, m.weighted_score,
                   m.matched_skills, m.missing_skills, m.status, m.id as match_id
            FROM job_matches m
            JOIN candidates c ON m.candidate_id = c.id
            WHERE m.job_title = ? AND m.weighted_score >= ?
        '''
        params = [selected_job, min_score]
    
    if status_filter != 'all':
        query += ' AND m.status = ?'
        params.append(status_filter)
    
    query += ' ORDER BY m.weighted_score DESC'
    
    matches = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template("dashboard.html", 
                         matches=matches,
                         job_titles=job_titles,
                         selected_job=selected_job,
                         status_filter=status_filter,
                         min_score=min_score)

@app.route("/get_scores/<int:candidate_id>/<job_title>")
def get_scores(candidate_id, job_title):
    conn = get_db_connection()
    match = conn.execute('''
        SELECT base_score, weighted_score, matched_skills, missing_skills
        FROM job_matches
        WHERE candidate_id = ? AND job_title = ?
    ''', (candidate_id, job_title)).fetchone()
    conn.close()
    
    if match:
        return jsonify({
            "base_score": match["base_score"],
            "weighted_score": match["weighted_score"],
            "matched_skills": match["matched_skills"].split(','),
            "missing_skills": match["missing_skills"].split(',')
        })
    return jsonify({"error": "Match not found"}), 404

@app.route("/update_status", methods=["POST"])
def update_status():
    match_id = request.form.get("match_id")
    new_status = request.form.get("status")
    
    try:
        conn = get_db_connection()
        conn.execute('''
            UPDATE job_matches 
            SET status=?, last_updated=CURRENT_TIMESTAMP 
            WHERE id=?
        ''', (new_status, match_id))
        conn.commit()
        conn.close()
        flash("Status updated successfully", "success")
    except Exception as e:
        flash(f"Failed to update status: {str(e)}", "error")
    
    return redirect(request.referrer)

@app.route("/send_email", methods=["POST"])
def send_email():
    from email_sender import send_interview_email
    try:
        candidate_email = request.form.get("candidate_email")
        candidate_name = request.form.get("candidate_name")
        job_title = request.form.get("job_title")
        interview_date = request.form.get("interview_date")
        interview_time = request.form.get("interview_time")
        
        if send_interview_email(candidate_email, candidate_name, job_title, f"{interview_date} {interview_time}"):
            flash("Email sent successfully", "success")
        else:
            flash("Failed to send email", "error")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    
    return redirect(request.referrer)

if __name__ == "__main__":
    app.run(debug=True)