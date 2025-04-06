import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from configparser import ConfigParser
from datetime import datetime

config = ConfigParser()
config.read('config.ini')

SENDER_EMAIL = config.get('EMAIL', 'sender_email')
SENDER_PASSWORD = config.get('EMAIL', 'sender_password')
COMPANY_NAME = config.get('COMPANY', 'name', fallback='Our Company')

def send_email(recipient, subject, body):
    msg = MIMEMultipart()
    msg['From'] = f"{COMPANY_NAME} <{SENDER_EMAIL}>"
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"{datetime.now()}: Email sent to {recipient}")
        return True
    except Exception as e:
        print(f"{datetime.now()}: Email failed to {recipient}: {str(e)}")
        return False

def send_interview_email(candidate_email, candidate_name, job_title, interview_datetime):
    subject = f"{COMPANY_NAME} Interview Invitation for {job_title}"
    body = f"""Dear {candidate_name},

We're pleased to invite you for an interview regarding your application for {job_title}.

📅 Interview Date: {interview_datetime}

Location: Virtual (Zoom)
Meeting Link: https://zoom.us/j/1234567890

Please prepare:
- Your professional background
- Any questions about the role

Best regards,
{COMPANY_NAME} HR Team"""
    
    return send_email(candidate_email, subject, body)