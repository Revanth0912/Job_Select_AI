import pdfplumber
import re
import os
import zipfile
import xml.etree.ElementTree as ET

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdfplumber"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {str(e)}")
        return ""

def extract_text_from_docx(docx_path):
    """Extract text from DOCX without python-docx"""
    try:
        # DOCX is a zip file containing XML
        with zipfile.ZipFile(docx_path) as z:
            # Get the main document XML
            with z.open('word/document.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                
                # Namespace for Word documents
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                
                # Extract text from paragraphs
                text_parts = []
                for paragraph in root.findall('.//w:p', ns):
                    for elem in paragraph.findall('.//w:t', ns):
                        if elem.text:
                            text_parts.append(elem.text)
                    text_parts.append('\n')
                
                return ''.join(text_parts)
    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {str(e)}")
        return ""

def extract_email(text):
    """Extract first email address from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "N/A"

def parse_resume(resume_path):
    """Parse resume file and return text and email"""
    try:
        if not os.path.exists(resume_path):
            print(f"File not found: {resume_path}")
            return None, "N/A"
        
        if resume_path.lower().endswith(".pdf"):
            text = extract_text_from_pdf(resume_path)
        elif resume_path.lower().endswith(".docx"):
            text = extract_text_from_docx(resume_path)
        else:
            # Try to read as plain text
            try:
                with open(resume_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except UnicodeDecodeError:
                with open(resume_path, 'r', encoding='latin-1') as f:
                    text = f.read()
        
        return text, extract_email(text)
    except Exception as e:
        print(f"Error parsing {resume_path}: {str(e)}")
        return None, "N/A"