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
    except Exception as e:
        print(f"DEBUG: Error checking/adding age column: {e}")
    
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

def generate_pdf(patient_name, patient_id, height, weight, bmi, category, date_str):
    pdf_filename = f"BMI_Report_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join('temp_pdfs', pdf_filename)
    
    if not os.path.exists('temp_pdfs'):
        os.makedirs('temp_pdfs')
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=10
    )
    
    story.append(Paragraph("BMI Health Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    data = [
        ['Patient Name:', patient_name],
        ['Patient ID:', str(patient_id)],
        ['Height (cm):', str(height)],
        ['Weight (kg):', str(weight)],
        ['BMI Value:', f'{bmi:.2f}'],
        ['BMI Category:', category],
        ['Report Date:', date_str]
    ]
    
    table = Table(data, colWidths=[2*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.4*inch))
    
    story.append(Paragraph("Health Advice", heading_style))
    advice = get_health_advice(category)
    story.append(Paragraph(advice, normal_style))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Disclaimer: This report is for informational purposes only. Please consult a healthcare professional for personalized advice.", normal_style))
    
    doc.build(story)
    return pdf_path

def generate_invoice_pdf(patient_name, patient_id, invoice_number, height, weight, bmi, category, 
                         consultation_fee, bmi_assessment_fee, health_report_fee, 
                         total_amount, payment_terms, invoice_date_str):
    pdf_filename = f"BMI_Prescription_{invoice_number}_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join('temp_pdfs', pdf_filename)
    
    if not os.path.exists('temp_pdfs'):
        os.makedirs('temp_pdfs')
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.4*inch, bottomMargin=0.4*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Modern UI Colors from Dashboard
    dark_blue = colors.HexColor('#1a5490')
    section_bg = colors.HexColor('#4a8fc4')
    total_bg = colors.HexColor('#e3f2fd')
    total_red = colors.HexColor('#e74c3c')
    light_yellow_bg = colors.HexColor('#fef9e7')
    border_orange = colors.HexColor('#f39c12')
    
    # Category Colors
    bmi_colors = {
        'Underweight': colors.HexColor('#3498db'),
        'Normal': colors.HexColor('#2ecc71'),
        'Overweight': colors.HexColor('#d98d1a'),
        'Obese': colors.HexColor('#e74c3c')
    }
    bmi_color = bmi_colors.get(category, dark_blue)

    # Styles
    title_style = ParagraphStyle('TitleStyle', fontSize=18, textColor=dark_blue, fontName='Helvetica-Bold', leading=22)
    label_style = ParagraphStyle('LabelStyle', fontSize=10, textColor=dark_blue, fontName='Helvetica-Bold', leading=14)
    value_style = ParagraphStyle('ValueStyle', fontSize=10, textColor=colors.black, fontName='Helvetica', leading=14)
    section_title_style = ParagraphStyle('SectionTitle', fontSize=11, textColor=colors.white, fontName='Helvetica-Bold', leading=14)
    
    # 1. Header with Circular Logo and Title
    logo_circle = Table([[Paragraph("<b style='color:white;font-size:14px;'>TC</b>", ParagraphStyle('LogoText', alignment=1))]],
                         colWidths=[0.45*inch], rowHeights=[0.45*inch])
    logo_circle.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), dark_blue),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROUNDEDCORNERS', [15, 15, 15, 15]), 
    ]))

    header_data = [[logo_circle, Paragraph(f"<b>BMI PRESCRIPTION REPORT</b>", title_style)]]
    header_table = Table(header_data, colWidths=[0.6*inch, 6.9*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.15*inch))

    # 2. Prescription Info with underline
    info_data = [[
        Paragraph(f"<b>Prescription ID:</b> <font color='black'>{invoice_number}</font>", label_style),
        Paragraph(f"<b>Date:</b> <font color='black'>{invoice_date_str}</font>", label_style)
    ]]
    info_table = Table(info_data, colWidths=[4*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, dark_blue),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.2*inch))

    # 3. Patient Details
    story.append(Table([[Paragraph("PATIENT DETAILS", section_title_style)]], colWidths=[7.5*inch], 
                       style=[('BACKGROUND', (0,0), (-1,-1), section_bg), ('PADDING', (0,0), (-1,-1), 6)]))
    
    patient_data = [
        [Paragraph(f"<b>Name:</b> {patient_name}", label_style)],
        [Paragraph(f"<b>Age:</b> 46 yrs", label_style)]
    ]
    patient_table = Table(patient_data, colWidths=[7.5*inch])
    patient_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.2*inch))

    # 4. Measurements
    story.append(Table([[Paragraph("MEASUREMENTS", section_title_style)]], colWidths=[7.5*inch], 
                       style=[('BACKGROUND', (0,0), (-1,-1), section_bg), ('PADDING', (0,0), (-1,-1), 6)]))
    
    meas_data = [[
        Paragraph(f"<b>Height:</b> {height} cm", label_style),
        Paragraph(f"<b>Weight:</b> {weight} kg", label_style)
    ]]
    meas_table = Table(meas_data, colWidths=[1.8*inch, 5.7*inch])
    meas_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(meas_table)
    story.append(Spacer(1, 0.2*inch))

    # 5. Highlighted BMI Result Box
    badge_table = Table([[Paragraph(category.upper(), ParagraphStyle('Badge', alignment=1, textColor=bmi_color, fontSize=12, fontName='Helvetica-Bold'))]], 
                        colWidths=[1.8*inch], style=[
                            ('BACKGROUND', (0,0), (-1,-1), colors.white),
                            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('PADDING', (0,0), (-1,-1), 6)
                        ])

    bmi_box_data = [[Paragraph(f"<b style='color:white;font-size:32px;'>{bmi:.1f}</b>", ParagraphStyle('BMIVal', alignment=1))],
                    [Paragraph("<font color='white' size='11'>BMI Value</font>", ParagraphStyle('BMILabel', alignment=1))],
                    [Spacer(1, 0.15*inch)],
                    [badge_table]]
    bmi_box_table = Table(bmi_box_data, colWidths=[7.5*inch])
    bmi_box_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bmi_color),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    story.append(bmi_box_table)
    story.append(Spacer(1, 0.2*inch))

    # 6. Assessment Charges
    story.append(Table([[Paragraph("ASSESSMENT CHARGES", section_title_style)]], colWidths=[7.5*inch], 
                       style=[('BACKGROUND', (0,0), (-1,-1), section_bg), ('PADDING', (0,0), (-1,-1), 6)]))
    
    charges_data = [
        [Paragraph("Consultation & Evaluation", value_style), Paragraph("INR 500", ParagraphStyle('Right', alignment=2))],
        [Paragraph("BMI Assessment & Analysis", value_style), Paragraph("INR 300", ParagraphStyle('Right', alignment=2))],
        [Paragraph("Health Report", value_style), Paragraph("INR 200", ParagraphStyle('Right', alignment=2))],
        [Paragraph("<b>TOTAL</b>", label_style), Paragraph(f"<b style='color:#e74c3c;'>INR {total_amount}</b>", ParagraphStyle('Total', alignment=2))]
    ]
    charges_table = Table(charges_data, colWidths=[5.5*inch, 2*inch])
    charges_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -3), 0.5, colors.grey),
        ('BACKGROUND', (0, 3), (-1, 3), total_bg),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(charges_table)
    story.append(Spacer(1, 0.3*inch))

    # 7. Terms Box
    terms_content = [[
        Paragraph("<b>Terms:</b>", label_style),
        Paragraph("Due within 30 days from assessment date.", value_style)
    ]]
    terms_table = Table(terms_content, colWidths=[7.5*inch])
    terms_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_yellow_bg),
        ('LINEBEFORE', (0, 0), (0, -1), 4, border_orange),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(terms_table)

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
HealthCare Clinic & Wellness Center
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
    cursor.execute(
        'SELECT * FROM bmi_records WHERE patient_id = ? ORDER BY date DESC LIMIT 10',
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
            print(f"DEBUG: height={height_cm}, weight={weight_kg}, age={age}, age_type={type(age)}")
            
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
                'INSERT INTO bmi_records (patient_id, age, height, weight, bmi, category) VALUES (?, ?, ?, ?, ?, ?)',
                (session['user_id'], age_int, height_cm, weight_kg, bmi, category)
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
                date_str
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
        record['date']
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
            invoice_date
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
        'SELECT i.*, b.height, b.weight, b.bmi, b.category FROM invoices i '
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
        invoice['invoice_date']
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
        'SELECT i.*, b.height, b.weight, b.bmi, b.category FROM invoices i '
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
        invoice['invoice_date']
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
        'SELECT i.*, b.age, b.height, b.weight, b.bmi, b.category FROM invoices i '
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
