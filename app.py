import os
import sqlite3
import hashlib
import secrets
import traceback
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import io
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
# Using a fixed secret key for PythonAnywhere stability
app.secret_key = 'bmi-health-tracker-secret-key-123'

# Get the absolute path of the project directory
basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(basedir, 'database.db')
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_now():
    return datetime.now(IST)

def format_date_display(date_str):
    try:
        if isinstance(date_str, str):
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00')) if 'T' in date_str else datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            dt_ist = dt.astimezone(IST)
        else:
            dt_ist = date_str.astimezone(IST) if date_str.tzinfo else date_str.replace(tzinfo=timezone.utc).astimezone(IST)
        return dt_ist.strftime('%d-%m-%Y %H:%M:%S')
    except Exception as e:
        print(f"DEBUG: Date format error: {e}")
        return str(date_str)[:19]

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            age INTEGER,
            height REAL NOT NULL,
            weight REAL NOT NULL,
            bmi REAL NOT NULL,
            category TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id)
        )
    ''')
    
    try:
        cursor.execute("PRAGMA table_info(bmi_records)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'age' not in columns:
            print("DEBUG: Adding 'age' column to bmi_records table...")
            cursor.execute('ALTER TABLE bmi_records ADD COLUMN age INTEGER')
            db.commit()
            print("DEBUG: 'age' column added successfully")
        if 'gender' not in columns:
            print("DEBUG: Adding 'gender' column to bmi_records table...")
            cursor.execute('ALTER TABLE bmi_records ADD COLUMN gender TEXT')
            db.commit()
            print("DEBUG: 'gender' column added successfully")
    except Exception as e:
        print(f"DEBUG: Error checking/adding columns: {e}")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            patient_id INTEGER NOT NULL,
            record_id INTEGER NOT NULL,
            consultation_fee REAL DEFAULT 50.00,
            bmi_assessment_fee REAL DEFAULT 30.00,
            health_report_fee REAL DEFAULT 20.00,
            total_amount REAL NOT NULL,
            payment_status TEXT DEFAULT 'Pending',
            payment_terms TEXT DEFAULT 'Due within 30 days',
            invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id),
            FOREIGN KEY (record_id) REFERENCES bmi_records(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    db.commit()
    db.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_bmi_category(bmi):
    if bmi < 18.5:
        return 'Underweight'
    elif bmi < 25:
        return 'Normal'
    elif bmi < 30:
        return 'Overweight'
    else:
        return 'Obese'

def get_health_advice(category):
    advice = {
        'Underweight': 'Consider consulting a healthcare professional. A balanced diet with adequate calories and nutrients is important.',
        'Normal': 'Great! Maintain your healthy weight with regular exercise and a balanced diet.',
        'Overweight': 'Consider a healthier lifestyle with regular physical activity and a balanced diet. Consult a healthcare provider if needed.',
        'Obese': 'It is highly recommended to consult a healthcare professional for personalized advice on weight management.'
    }
    return advice.get(category, '')

def generate_pdf(patient_name, patient_id, height, weight, bmi, category, date_str, gender=None, age=None):
    pdf_filename = f"BMI_Report_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join('temp_pdfs', pdf_filename)
    
    if not os.path.exists('temp_pdfs'):
        os.makedirs('temp_pdfs')
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    story = []
    
    # LifeTrack Health Hub Palette
    hospital_blue = colors.HexColor('#0F4C81')
    text_dark = colors.HexColor('#1F2937')
    text_muted = colors.HexColor('#4B5563')
    border_gray = colors.HexColor('#E5E7EB')
    light_blue = colors.HexColor('#F0F7FF')
    
    # Styles
    header_style = ParagraphStyle('Header', fontSize=22, fontName='Helvetica-Bold', textColor=hospital_blue, leading=26)
    sub_header_style = ParagraphStyle('SubHeader', fontSize=10, fontName='Helvetica-Bold', textColor=text_muted, leading=14)
    contact_style = ParagraphStyle('Contact', fontSize=9, fontName='Helvetica', textColor=text_muted, alignment=TA_RIGHT, leading=12)
    section_title_style = ParagraphStyle('SecTitle', fontSize=10, fontName='Helvetica-Bold', textColor=colors.white, leftIndent=8)
    label_style = ParagraphStyle('Label', fontSize=9, fontName='Helvetica-Bold', textColor=text_dark)
    value_style = ParagraphStyle('Value', fontSize=9, fontName='Helvetica', textColor=text_dark)
    interpretation_style = ParagraphStyle('Interp', fontSize=10, fontName='Helvetica', textColor=text_dark, leading=14)
    sig_verify_style = ParagraphStyle('SigVerify', fontSize=8, fontName='Helvetica', alignment=TA_CENTER, textColor=text_muted)

    # 1. Header & Branding
    brand_content = [
        [
            [Paragraph("LifeTrack Health Hub", header_style), 
             Paragraph("PERSONAL HEALTH REPORT", sub_header_style)],
            Paragraph("support@lifetrack.com<br/>+91 98765 43210<br/>www.lifetrack.com", contact_style)
        ]
    ]
    brand_table = Table(brand_content, colWidths=[4.2*inch, 3.0*inch])
    brand_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('LINEBELOW', (0, 0), (-1, -1), 1, hospital_blue),
    ]))
    story.append(brand_table)
    story.append(Spacer(1, 0.2*inch))

    # 2. Patient Information Section
    story.append(Table([[Paragraph("PATIENT INFORMATION", section_title_style)]], 
                       colWidths=[7.2*inch], style=[('BACKGROUND', (0,0), (-1,-1), hospital_blue), ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    
    patient_data = [
        [Paragraph("Patient Name", label_style), Paragraph(f": {patient_name}", value_style), 
         Paragraph("Patient ID", label_style), Paragraph(f": PID-{patient_id}", value_style)],
        [Paragraph("Gender", label_style), Paragraph(f": {gender}" if gender and str(gender).strip() else ": Not Specified", value_style), 
         Paragraph("Report Date", label_style), Paragraph(f": {date_str}", value_style)]
    ]
    patient_table = Table(patient_data, colWidths=[1.2*inch, 2.4*inch, 1.2*inch, 2.4*inch])
    patient_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1, -2), 0.5, border_gray),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.25*inch))

    # 3. Anthropometric Measurements
    story.append(Table([[Paragraph("ANTHROPOMETRIC MEASUREMENTS", section_title_style)]], 
                       colWidths=[7.2*inch], style=[('BACKGROUND', (0,0), (-1,-1), hospital_blue), ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    
    meas_data = [
        [Paragraph("Height (cm)", label_style), Paragraph(f"{height} cm", value_style), 
         Paragraph("Weight (kg)", label_style), Paragraph(f"{weight} kg", value_style)],
        [Paragraph("BMI Value", label_style), Paragraph(f"{bmi:.2f}", value_style),
         Paragraph("Category", label_style), Paragraph(category, value_style)]
    ]
    meas_table = Table(meas_data, colWidths=[1.2*inch, 2.4*inch, 1.2*inch, 2.4*inch])
    meas_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, border_gray),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meas_table)
    story.append(Spacer(1, 0.3*inch))

    # 4. Highlighted BMI Card
    bmi_val_style = ParagraphStyle('BMIVal', fontSize=36, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=hospital_blue)
    bmi_cat_style = ParagraphStyle('BMICat', fontSize=14, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=hospital_blue)
    
    bmi_card_content = [
        [Paragraph(f"{bmi:.2f}", bmi_val_style)],
        [Paragraph(category.upper(), bmi_cat_style)]
    ]
    bmi_card = Table(bmi_card_content, colWidths=[2.5*inch])
    bmi_card.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, hospital_blue),
        ('BACKGROUND', (0,0), (-1,-1), light_blue),
        ('ROUNDEDCORNERS', [15, 15, 15, 15]),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    
    story.append(Table([[bmi_card]], colWidths=[7.2*inch], style=[('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(Spacer(1, 0.3*inch))

    # 5. Health Advice
    story.append(Table([[Paragraph("HEALTH ADVICE", section_title_style)]], 
                       colWidths=[7.2*inch], style=[('BACKGROUND', (0,0), (-1,-1), hospital_blue), ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    
    advice = get_health_advice(category)
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(advice, interpretation_style))
    
    story.append(Spacer(1, 1.0*inch))
    
    # Authorized Signature Section
    sig_content = [
        [Paragraph("Authorized Signature", ParagraphStyle('SigText', fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=text_dark))],
        [Paragraph("LifeTrack Health Hub", ParagraphStyle('SigSub', fontSize=9, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=text_dark))],
        [Paragraph("Digitally Verified Document", sig_verify_style)]
    ]
    
    sig_table = Table(sig_content, colWidths=[2.5*inch])
    sig_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 0.75, text_dark),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    
    container_table = Table([[sig_table]], colWidths=[7.2*inch])
    container_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
    ]))
    story.append(container_table)
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("This is a digitally generated report. For medical diagnosis, please consult a healthcare professional.", sig_verify_style))
    
    doc.build(story)
    return pdf_path

from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_invoice_pdf(patient_name, patient_id, invoice_number, height, weight, bmi, category, 
                         consultation_fee, bmi_assessment_fee, health_report_fee, 
                         total_amount, payment_terms, invoice_date_str, age=None, gender=None):
    pdf_filename = f"BMI_Report_{invoice_number}_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join('temp_pdfs', pdf_filename)
    
    if not os.path.exists('temp_pdfs'):
        os.makedirs('temp_pdfs')
    
    # Use A4 as requested
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=0.4*inch, bottomMargin=0.4*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # LifeTrack Health Hub Palette
    hospital_blue = colors.HexColor('#0F4C81')
    text_dark = colors.HexColor('#1F2937')
    text_muted = colors.HexColor('#4B5563')
    border_gray = colors.HexColor('#E5E7EB')
    light_blue = colors.HexColor('#F0F7FF')
    
    # Category Colors (Professional Hospital Standards)
    bmi_colors = {
        'Underweight': colors.HexColor('#2563EB'), # Blue
        'Normal': colors.HexColor('#059669'),      # Green
        'Overweight': colors.HexColor('#D97706'),  # Amber
        'Obese': colors.HexColor('#DC2626')        # Red
    }
    status_color = bmi_colors.get(category, hospital_blue)

    # Risk Level & Classification
    risk_data = {
        'Underweight': ('High Risk', 'Nutritional Deficit'),
        'Normal': ('Low Risk', 'Optimal Health Range'),
        'Overweight': ('Moderate Risk', 'Increased Health Risk'),
        'Obese': ('High Risk', 'Significant Health Risk')
    }
    risk_level, classification = risk_data.get(category, ('N/A', 'N/A'))

    # Styles
    header_style = ParagraphStyle('Header', fontSize=22, fontName='Helvetica-Bold', textColor=hospital_blue, leading=26)
    sub_header_style = ParagraphStyle('SubHeader', fontSize=10, fontName='Helvetica-Bold', textColor=text_muted, leading=14)
    contact_style = ParagraphStyle('Contact', fontSize=9, fontName='Helvetica', textColor=text_muted, alignment=TA_RIGHT, leading=12)
    
    section_title_style = ParagraphStyle('SecTitle', fontSize=10, fontName='Helvetica-Bold', textColor=colors.white, leftIndent=8)
    label_style = ParagraphStyle('Label', fontSize=9, fontName='Helvetica-Bold', textColor=text_dark)
    value_style = ParagraphStyle('Value', fontSize=9, fontName='Helvetica', textColor=text_dark)
    
    meta_style = ParagraphStyle('Meta', fontSize=9, fontName='Helvetica', textColor=text_dark, alignment=TA_RIGHT)

    interpretation_style = ParagraphStyle('Interp', fontSize=10, fontName='Helvetica', textColor=text_dark, leading=14)
    guidance_style = ParagraphStyle('Guidance', fontSize=9.5, fontName='Helvetica', textColor=text_dark, leading=14, leftIndent=0)
    
    footer_text_style = ParagraphStyle('FooterText', fontSize=8, fontName='Helvetica', textColor=text_muted)
    disclaimer_style = ParagraphStyle('Disclaimer', fontSize=7.5, fontName='Helvetica', textColor=text_muted, alignment=TA_CENTER, leading=10)

    # 1. Header & Branding
    brand_content = [
        [
            [Paragraph("LifeTrack Health Hub", header_style), 
             Paragraph("MEDICAL & WELLNESS REPORT", sub_header_style)],
            Paragraph("support@lifetrack.com<br/>+91 98765 43210<br/>www.lifetrack.com", contact_style)
        ]
    ]
    brand_table = Table(brand_content, colWidths=[4.2*inch, 3.0*inch])
    brand_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('LINEBELOW', (0, 0), (-1, -1), 1, hospital_blue),
    ]))
    story.append(brand_table)
    story.append(Spacer(1, 0.1*inch))

    # Report Metadata
    meta_data = [
        [Paragraph(f"<b>Report ID:</b> {invoice_number} | <b>Date:</b> {invoice_date_str}", meta_style)]
    ]
    meta_table = Table(meta_data, colWidths=[7.2*inch])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(meta_table)

    # 2. Patient Information Section
    story.append(Table([[Paragraph("PATIENT INFORMATION", section_title_style)]], 
                       colWidths=[7.2*inch], style=[('BACKGROUND', (0,0), (-1,-1), hospital_blue), ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    
    patient_data = [
        [Paragraph("Patient Name", label_style), Paragraph(f": {patient_name}", value_style), 
         Paragraph("Age", label_style), Paragraph(f": {age} yrs" if age else ": N/A", value_style)],
        [Paragraph("Gender", label_style), Paragraph(f": {gender}" if gender and str(gender).strip() else ": Not Specified", value_style), 
         Paragraph("Visit Type", label_style), Paragraph(": Wellness Assessment", value_style)]
    ]
    patient_table = Table(patient_data, colWidths=[1.2*inch, 2.4*inch, 1.2*inch, 2.4*inch])
    patient_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1, -2), 0.5, border_gray),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.2*inch))

    # 3. Anthropometric Measurements
    story.append(Table([[Paragraph("ANTHROPOMETRIC MEASUREMENTS", section_title_style)]], 
                       colWidths=[7.2*inch], style=[('BACKGROUND', (0,0), (-1,-1), hospital_blue), ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    
    meas_data = [
        [Paragraph("Height (cm)", label_style), Paragraph(f"{height} cm", value_style), 
         Paragraph("Weight (kg)", label_style), Paragraph(f"{weight} kg", value_style)],
        [Paragraph("BMI Reference", label_style), Paragraph("WHO Standards", value_style),
         Paragraph("WHO Category", label_style), Paragraph(classification, value_style)]
    ]
    meas_table = Table(meas_data, colWidths=[1.2*inch, 2.4*inch, 1.2*inch, 2.4*inch])
    meas_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, border_gray),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meas_table)
    story.append(Spacer(1, 0.25*inch))

    # 4. BMI Result Highlight
    bmi_val_style = ParagraphStyle('BMIVal', fontSize=36, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=hospital_blue)
    bmi_cat_style = ParagraphStyle('BMICat', fontSize=14, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=status_color)
    
    bmi_card_content = [
        [Paragraph(f"{bmi:.2f}", bmi_val_style)],
        [Paragraph(category.upper(), bmi_cat_style)]
    ]
    bmi_card = Table(bmi_card_content, colWidths=[2.5*inch])
    bmi_card.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, hospital_blue),
        ('BACKGROUND', (0,0), (-1,-1), light_blue),
        ('ROUNDEDCORNERS', [15, 15, 15, 15]),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    
    story.append(Table([[bmi_card]], colWidths=[7.2*inch], style=[('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(Spacer(1, 0.25*inch))

    # 5. Clinical Interpretation
    story.append(Table([[Paragraph("CLINICAL INTERPRETATION", section_title_style)]], 
                       colWidths=[7.2*inch], style=[('BACKGROUND', (0,0), (-1,-1), hospital_blue), ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    
    interp_text = f"""
    Based on the recorded Body Mass Index (BMI) of <b>{bmi:.2f}</b>, the patient is clinically classified as <b>{category}</b>. 
    This assessment indicates a <b>{risk_level}</b> risk level according to World Health Organization (WHO) protocols. 
    BMI is a specialized screening tool used by healthcare professionals to evaluate body composition and related health risks.
    """
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(interp_text, interpretation_style))
    story.append(Spacer(1, 0.2*inch))

    # 6. Doctor's Wellness Prescription
    story.append(Table([[Paragraph("<b style='font-size:12px;'>Rx</b> - DOCTOR'S WELLNESS PRESCRIPTION", section_title_style)]], 
                       colWidths=[7.2*inch], style=[('BACKGROUND', (0,0), (-1,-1), hospital_blue), ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    
    prescription_items = [
        "Maintain a balanced nutritional intake focusing on whole grains, lean proteins, and micronutrients.",
        "Ensure consistent physical activity (minimum 150 minutes of moderate aerobic exercise weekly).",
        "Monitor hydration levels (2.5 - 3.0 Liters daily) and maintain a consistent sleep-wake cycle.",
        "Limit intake of processed carbohydrates, saturated fats, and high-sodium dietary items.",
        "Schedule a follow-up consultation with a clinical specialist for personalized metabolic evaluation."
    ]
    
    for item in prescription_items:
        story.append(Spacer(1, 0.05*inch))
        story.append(Paragraph(f"&bull; {item}", guidance_style))
    
    story.append(Spacer(1, 0.4*inch))

    # 7. Doctor Details Section (Three-Column Layout)
    doc_label_style = ParagraphStyle('DocLabel', fontSize=9, fontName='Helvetica-Bold', textColor=text_dark)
    doc_sub_style = ParagraphStyle('DocSub', fontSize=8, fontName='Helvetica', textColor=text_muted)
    
    doctors_data = [
        [
            [Paragraph("Dr. Sarah Thompson (MD)", doc_label_style),
             Paragraph("Primary Consultant (Endocrinology)", doc_sub_style),
             Paragraph("Reg No: LT-DR-001", doc_sub_style)],
            [Paragraph("Dr. Rajesh Kumar (MS)", doc_label_style),
             Paragraph("Clinical Nutritionist", doc_sub_style),
             Paragraph("Reg No: LT-DR-002", doc_sub_style)],
            [Paragraph("Dr. Anita Desai (MD)", doc_label_style),
             Paragraph("General Medicine", doc_sub_style),
             Paragraph("Reg No: LT-DR-003", doc_sub_style)]
        ]
    ]
    
    # Define alignments for each column
    col_style1 = ParagraphStyle('Col1', parent=doc_label_style, alignment=TA_LEFT)
    col_sub1 = ParagraphStyle('Sub1', parent=doc_sub_style, alignment=TA_LEFT)
    
    col_style2 = ParagraphStyle('Col2', parent=doc_label_style, alignment=TA_CENTER)
    col_sub2 = ParagraphStyle('Sub2', parent=doc_sub_style, alignment=TA_CENTER)
    
    col_style3 = ParagraphStyle('Col3', parent=doc_label_style, alignment=TA_RIGHT)
    col_sub3 = ParagraphStyle('Sub3', parent=doc_sub_style, alignment=TA_RIGHT)

    doctors_content = [
        [
            [Paragraph("Dr. Sarah Thompson (MD)", col_style1),
             Paragraph("Primary Consultant (Endocrinology)", col_sub1),
             Paragraph("Reg No: LT-DR-001", col_sub1)],
            [Paragraph("Dr. Rajesh Kumar (MS)", col_style2),
             Paragraph("Clinical Nutritionist", col_sub2),
             Paragraph("Reg No: LT-DR-002", col_sub2)],
            [Paragraph("Dr. Anita Desai (MD)", col_style3),
             Paragraph("General Medicine", col_sub3),
             Paragraph("Reg No: LT-DR-003", col_sub3)]
        ]
    ]
    
    doctors_table = Table(doctors_content, colWidths=[2.3*inch, 2.6*inch, 2.3*inch])
    doctors_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (0,0), 15),  # Shifted slightly right from left margin
        ('RIGHTPADDING', (-1,0), (-1,0), 15), # Shifted slightly inward from right margin
    ]))
    story.append(doctors_table)
    story.append(Spacer(1, 0.8*inch))

    # 8. Authorized Signature Section (Right-Aligned Style)
    sig_text_style = ParagraphStyle('SigText', fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=text_dark)
    sig_sub_style = ParagraphStyle('SigSub', fontSize=9, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=text_dark)
    sig_verify_style = ParagraphStyle('SigVerify', fontSize=8, fontName='Helvetica', alignment=TA_CENTER, textColor=text_muted)
    
    sig_content = [
        [Paragraph("Authorized Signature", sig_text_style)],
        [Paragraph("LifeTrack Health Hub", sig_sub_style)],
        [Paragraph("Medical & Wellness Report", sig_verify_style)],
        [Paragraph("Digitally Verified Document", sig_verify_style)]
    ]
    
    # Create a narrower table for the signature and align it to the right
    sig_table = Table(sig_content, colWidths=[2.5*inch])
    sig_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 0.75, text_dark), # Short line ABOVE "Authorized Signature"
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    
    # Wrap in a container table to right-align the whole block
    container_table = Table([[sig_table]], colWidths=[7.2*inch])
    container_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
    ]))
    story.append(container_table)


    doc.build(story)
    return pdf_path

def send_email(recipient_email, patient_name, pdf_path):
    sender_email = os.getenv('GMAIL_EMAIL', "your_email@gmail.com")
    sender_password = os.getenv('GMAIL_PASSWORD', "your_app_password")
    
    if sender_email == "your_email@gmail.com" or sender_password == "your_app_password":
        print("❌ Email credentials not configured.")
        print("📧 To enable email, create a .env file with:")
        print("   GMAIL_EMAIL=your_gmail_address@gmail.com")
        print("   GMAIL_PASSWORD=your_16_character_app_password")
        return False
    
    try:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = "BMI Prescription Report - Your Assessment"
        
        body = f"""
Dear {patient_name},

Please find attached your BMI Prescription Report containing your complete health assessment.

Report includes:
• Patient details and measurements
• BMI value and health category
• Clinical recommendations
• Assessment charges and payment terms

This report has been generated based on your health measurements. We recommend reviewing it and consulting with a healthcare professional if you have any concerns.

Best regards,
LifeTrack Health Hub
BMI Health Tracker
        """
        
        message.attach(MIMEText(body, 'plain'))
        
        with open(pdf_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(pdf_path)}')
            message.attach(part)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        errors = []
        
        if not name:
            errors.append('Name is required')
        if not email:
            errors.append('Email is required')
        if not password:
            errors.append('Password is required')
        if password != confirm_password:
            errors.append('Passwords do not match')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters')
        
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        try:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                (name, email, hashed_password)
            )
            db.commit()
            return jsonify({'success': True, 'message': 'Registration successful. Please login.'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'errors': ['Email already registered']}), 400
        finally:
            db.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({'success': False, 'errors': ['Email and password required']}), 400
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        db.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        
        return jsonify({'success': False, 'errors': ['Invalid email or password']}), 401
    
    return render_template('login.html')



@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor()
    # Fetch records from the last 3 months
    cursor.execute(
        "SELECT * FROM bmi_records WHERE patient_id = ? AND date >= date('now', '-3 months') ORDER BY date DESC",
        (session['user_id'],)
    )
    records = cursor.fetchall()
    db.close()
    
    return render_template('dashboard.html', records=records)

@app.route('/bmi', methods=['GET', 'POST'])
@login_required
def bmi_calculator():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        try:
            print(f"DEBUG: Raw data received: {data}")
            height_cm = float(data.get('height', 0))
            weight_kg = float(data.get('weight', 0))
            age = data.get('age')
            gender = data.get('gender')
            print(f"DEBUG: height={height_cm}, weight={weight_kg}, age={age}, gender={gender}")
            
            if height_cm <= 0 or weight_kg <= 0:
                return jsonify({'success': False, 'errors': ['Height and weight must be positive values']}), 400
            
            age_int = None
            if age is not None and age != '' and age != 'null':
                try:
                    age_int = int(float(age)) if isinstance(age, str) else int(age)
                    print(f"DEBUG: age_int after conversion: {age_int}")
                    if age_int < 1 or age_int > 150:
                        return jsonify({'success': False, 'errors': ['Age must be between 1 and 150']}), 400
                except (ValueError, TypeError) as e:
                    print(f"DEBUG: Age conversion error: {e}")
                    return jsonify({'success': False, 'errors': ['Age must be a valid number']}), 400
            
            height_m = height_cm / 100
            bmi = round(weight_kg / (height_m * height_m), 2)
            category = get_bmi_category(bmi)
            
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO bmi_records (patient_id, age, gender, height, weight, bmi, category) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (session['user_id'], age_int, gender, height_cm, weight_kg, bmi, category)
            )
            db.commit()
            record_id = cursor.lastrowid
            db.close()
            
            date_str = get_ist_now().strftime('%Y-%m-%d %H:%M:%S')
            pdf_path = generate_pdf(
                session['user_name'],
                session['user_id'],
                height_cm,
                weight_kg,
                bmi,
                category,
                date_str,
                gender=gender
            )
            
            result_data = {
                'success': True,
                'bmi': bmi,
                'category': category,
                'height': height_cm,
                'weight': weight_kg,
                'date': date_str,
                'record_id': record_id,
                'pdf_path': pdf_path
            }
            
            return jsonify(result_data), 201
        
        except ValueError as e:
            print(f"DEBUG: ValueError in BMI Calculator: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'errors': ['Please enter valid numbers']}), 400
        except Exception as e:
            print(f"DEBUG: General Exception in BMI Calculator: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'errors': [f'Error: {str(e)}']}), 500
    
    return render_template('bmi.html')

@app.route('/result/<int:record_id>')
@login_required
def result(record_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT * FROM bmi_records WHERE id = ? AND patient_id = ?',
        (record_id, session['user_id'])
    )
    record = cursor.fetchone()
    db.close()
    
    if not record:
        return redirect(url_for('dashboard'))
    
    advice = get_health_advice(record['category'])
    formatted_date = format_date_display(record['date'])
    return render_template('result.html', record=record, advice=advice, formatted_date=formatted_date)

@app.route('/send-email/<int:record_id>')
@login_required
def send_email_route(record_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT * FROM bmi_records WHERE id = ? AND patient_id = ?',
        (record_id, session['user_id'])
    )
    record = cursor.fetchone()
    db.close()
    
    if not record:
        return jsonify({'success': False, 'error': 'Record not found'}), 404
    
    pdf_path = generate_pdf(
        session['user_name'],
        session['user_id'],
        record['height'],
        record['weight'],
        record['bmi'],
        record['category'],
        record['date'],
        gender=record['gender']
    )
    
    user_email = session.get('user_email')
    user_name = session.get('user_name')
    
    if not user_email or not user_name:
        return jsonify({'success': False, 'error': 'User information not found. Please log in again.'}), 401
    
    if send_email(user_email, user_name, pdf_path):
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        return jsonify({'success': True, 'message': 'Email sent successfully'}), 200
    else:
        return jsonify({'success': False, 'error': 'Failed to send email'}), 500

@app.route('/create-invoice/<int:record_id>', methods=['POST'])
@login_required
def create_invoice(record_id):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute(
        'SELECT * FROM bmi_records WHERE id = ? AND patient_id = ?',
        (record_id, session['user_id'])
    )
    record = cursor.fetchone()
    
    if not record:
        db.close()
        return jsonify({'success': False, 'error': 'Record not found'}), 404
    
    consultation_fee = 500.00
    bmi_assessment_fee = 300.00
    health_report_fee = 200.00
    total_amount = consultation_fee + bmi_assessment_fee + health_report_fee
    
    ist_now = get_ist_now()
    invoice_number = f"INV-{session['user_id']}-{record_id}-{ist_now.strftime('%Y%m%d%H%M%S')}"
    payment_terms = "Due within 30 days"
    invoice_date = ist_now.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        cursor.execute('''
            INSERT INTO invoices 
            (invoice_number, patient_id, record_id, consultation_fee, bmi_assessment_fee, 
             health_report_fee, total_amount, payment_terms, invoice_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (invoice_number, session['user_id'], record_id, consultation_fee, 
              bmi_assessment_fee, health_report_fee, total_amount, payment_terms, invoice_date))
        db.commit()
        invoice_id = cursor.lastrowid
        
        invoice_path = generate_invoice_pdf(
            session['user_name'],
            session['user_id'],
            invoice_number,
            record['height'],
            record['weight'],
            record['bmi'],
            record['category'],
            consultation_fee,
            bmi_assessment_fee,
            health_report_fee,
            total_amount,
            payment_terms,
            invoice_date,
            age=record['age'],
            gender=record['gender']
        )
        
        return jsonify({
            'success': True,
            'invoice_id': invoice_id,
            'invoice_number': invoice_number,
            'invoice_date': invoice_date,
            'patient_name': session['user_name'],
            'age': record['age'],
            'height': record['height'],
            'weight': record['weight'],
            'bmi': record['bmi'],
            'category': record['category'],
            'total_amount': total_amount,
            'invoice_path': invoice_path
        }), 201
    
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()

@app.route('/send-invoice/<int:invoice_id>', methods=['POST'])
@login_required
def send_invoice(invoice_id):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute(
        'SELECT i.*, b.age, b.gender, b.height, b.weight, b.bmi, b.category FROM invoices i '
        'JOIN bmi_records b ON i.record_id = b.id '
        'WHERE i.id = ? AND i.patient_id = ?',
        (invoice_id, session['user_id'])
    )
    invoice = cursor.fetchone()
    db.close()
    
    if not invoice:
        return jsonify({'success': False, 'error': 'Invoice not found'}), 404
    
    invoice_path = generate_invoice_pdf(
        session['user_name'],
        session['user_id'],
        invoice['invoice_number'],
        invoice['height'],
        invoice['weight'],
        invoice['bmi'],
        invoice['category'],
        invoice['consultation_fee'],
        invoice['bmi_assessment_fee'],
        invoice['health_report_fee'],
        invoice['total_amount'],
        invoice['payment_terms'],
        invoice['invoice_date'],
        age=invoice['age'],
        gender=invoice['gender']
    )
    
    user_email = session.get('user_email')
    user_name = session.get('user_name')
    
    if not user_email or not user_name:
        return jsonify({'success': False, 'error': 'User information not found. Please log in again.'}), 401
    
    if send_email(user_email, user_name, invoice_path):
        if os.path.exists(invoice_path):
            os.remove(invoice_path)
        return jsonify({'success': True, 'message': 'Invoice sent successfully'}), 200
    else:
        return jsonify({'success': False, 'error': 'Failed to send invoice'}), 500

@app.route('/download-invoice/<int:invoice_id>')
@login_required
def download_invoice(invoice_id):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute(
        'SELECT i.*, b.age, b.gender, b.height, b.weight, b.bmi, b.category FROM invoices i '
        'JOIN bmi_records b ON i.record_id = b.id '
        'WHERE i.id = ? AND i.patient_id = ?',
        (invoice_id, session['user_id'])
    )
    invoice = cursor.fetchone()
    db.close()
    
    if not invoice:
        return "Invoice not found", 404
    
    invoice_path = generate_invoice_pdf(
        session['user_name'],
        session['user_id'],
        invoice['invoice_number'],
        invoice['height'],
        invoice['weight'],
        invoice['bmi'],
        invoice['category'],
        invoice['consultation_fee'],
        invoice['bmi_assessment_fee'],
        invoice['health_report_fee'],
        invoice['total_amount'],
        invoice['payment_terms'],
        invoice['invoice_date'],
        age=invoice['age'],
        gender=invoice['gender']
    )
    
    return send_file(invoice_path, as_attachment=True, download_name=f"Invoice_{invoice['invoice_number']}.pdf")

@app.route('/send-invoice-formsubmit', methods=['POST'])
@login_required
def send_invoice_formsubmit():
    data = request.get_json()
    invoice_id = data.get('invoice_id')
    recipient_email = data.get('email') or session.get('user_email')
    
    if not recipient_email:
        return jsonify({'success': False, 'error': 'Email address not found. Please log in again.'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute(
        'SELECT i.*, b.age, b.gender, b.height, b.weight, b.bmi, b.category FROM invoices i '
        'JOIN bmi_records b ON i.record_id = b.id '
        'WHERE i.id = ? AND i.patient_id = ?',
        (invoice_id, session['user_id'])
    )
    invoice = cursor.fetchone()
    db.close()
    
    if not invoice:
        return jsonify({'success': False, 'error': 'Invoice not found'}), 404
    
    try:
        return jsonify({
            'success': True,
            'message': 'Prescription ready to be sent via FormSubmit',
            'formsubmit_data': {
                '_subject': 'BMI Prescription Report',
                '_template': 'table',
                '_captcha': 'false',
                '1_BMI_Prescription_Report_Header': 'BMI PRESCRIPTION REPORT',
                '2_Prescription_ID': invoice['invoice_number'],
                '3_Date_and_Time': invoice['invoice_date'],
                '4_Patient_Details_Name': session['user_name'],
                '5_Patient_Age': f"{invoice['age']} years" if invoice['age'] else 'Not provided',
                '5a_Patient_Gender': invoice['gender'] if invoice['gender'] else 'Not specified',
                '6_Height_cm': str(invoice['height']),
                '7_Weight_kg': str(invoice['weight']),
                '8_BMI_Value': f"{invoice['bmi']:.2f}",
                '9_BMI_Category': invoice['category'],
                '10_Consultation_Evaluation': '₹500.00',
                '11_BMI_Assessment_Analysis': '₹300.00',
                '12_Health_Report': '₹200.00',
                '13_Total_Amount': '₹1000.00',
                '14_Payment_Terms': 'Due within 30 days from assessment date',
                '_next': '/thank-you',
                'Email': recipient_email
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
