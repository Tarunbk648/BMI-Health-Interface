# BMI Health Tracker - Full Stack Web Application

A complete, production-ready BMI (Body Mass Index) health tracking web application built with Flask, SQLite, and modern responsive design.

## 🌟 Features

### Core Functionality
- ✅ **User Authentication** - Secure registration and login with password hashing
- ✅ **BMI Calculator** - Automatic calculation with category classification
- ✅ **Health Dashboard** - View all BMI records with history
- ✅ **PDF Report Generation** - Auto-generated health reports with ReportLab
- ✅ **Email Integration** - Send reports via Gmail SMTP
- ✅ **Session Management** - Secure user sessions with login protection
- ✅ **Responsive Design** - Mobile-first, works on all devices

### BMI Categories
- **Underweight** (BMI < 18.5)
- **Normal** (BMI 18.5 - 24.9)
- **Overweight** (BMI 25 - 29.9)
- **Obese** (BMI ≥ 30)

## 📋 Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3.7+, Flask 2.3.3 |
| Database | SQLite3 |
| PDF Generation | ReportLab 4.0.4 |
| Security | Werkzeug (password hashing) |
| Email | Python SMTP (Gmail) |

## 📁 Project Structure

```
BMI Health Tracker/
├── app.py                 # Main Flask application (402 lines)
├── config.py              # Configuration and constants
├── requirements.txt       # Python dependencies
├── run.bat               # Windows startup script
├── run.sh                # Linux/Mac startup script
├── RUN.md                # Detailed setup instructions
├── README.md             # This file
├── database.db           # SQLite database (created on startup)
├── templates/            # HTML templates (6 files)
│   ├── base.html        # Base template with navigation
│   ├── register.html    # User registration page
│   ├── login.html       # User login page
│   ├── dashboard.html   # Main dashboard with records
│   ├── bmi.html         # BMI calculator form
│   └── result.html      # Result display page
├── static/
│   ├── css/
│   │   └── style.css    # Responsive CSS (700+ lines)
│   └── js/
│       └── main.js      # Frontend JavaScript
└── temp_pdfs/           # Temporary PDF storage (auto-created)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation

1. **Clone or extract the project**
```bash
cd "BMI indicator project"
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

**Or directly with Python:**
```bash
python app.py
```

4. **Access the application**
Open your browser and navigate to: `http://127.0.0.1:5000`

## 📖 Usage Guide

### Registration
1. Click "Register here" on the login page
2. Enter your full name, email, and password (min. 6 characters)
3. Confirm password and submit
4. You'll be redirected to login

### Login
1. Enter your registered email and password
2. Click "Login"
3. You'll be directed to your dashboard

### Calculate BMI
1. Click "Calculate BMI" from the dashboard
2. Enter your height in centimeters
3. Enter your weight in kilograms
4. Click "Calculate BMI"
5. View your results with health advice

### View Reports
1. From the result page, click "Send Report via Email" to email your PDF
2. On the dashboard, click "View" on any record to see details
3. Each report includes health advice based on your BMI category

### Download PDF
PDF reports are automatically generated and can be emailed to you

## 🔐 Security Features

- **Password Hashing**: Uses Werkzeug security for SHA256 + salt hashing
- **Session Management**: Secure Flask sessions with unique secret keys
- **Login Protection**: @login_required decorator on protected routes
- **CSRF Prevention**: Session-based security
- **Input Validation**: Client and server-side validation

## 📧 Email Configuration (Optional)

To enable email functionality:

1. **Enable 2-Factor Authentication on Gmail:**
   - Go to https://myaccount.google.com/
   - Click "Security" in the left menu
   - Enable 2-Factor Authentication

2. **Generate Gmail App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer" (or your device)
   - Generate password and copy it

3. **Update app.py:**
   ```python
   sender_email = "your_email@gmail.com"
   sender_password = "your_16_character_app_password"
   ```

4. **For production, use environment variables:**
   ```bash
   set GMAIL_EMAIL=your_email@gmail.com
   set GMAIL_APP_PASSWORD=your_app_password
   python app.py
   ```

## 🎨 Responsive Design

The application is fully responsive with breakpoints at:
- **Desktop**: > 768px (full navigation bar)
- **Tablet**: 481px - 768px (optimized layout)
- **Mobile**: < 480px (stacked layout)

All features work seamlessly across device sizes.

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### BMI Records Table
```sql
CREATE TABLE bmi_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    height REAL NOT NULL,
    weight REAL NOT NULL,
    bmi REAL NOT NULL,
    category TEXT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id)
)
```

## 🔧 API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login user
- `GET /logout` - Logout user

### Main Features
- `GET /` - Redirect to dashboard if logged in
- `GET /dashboard` - View user dashboard (protected)
- `GET /bmi` - Show BMI calculator form (protected)
- `POST /bmi` - Calculate and store BMI (protected)
- `GET /result/<id>` - View specific result (protected)
- `GET /send-email/<id>` - Send report via email (protected)

## 📝 File Descriptions

### app.py (Main Application)
- Flask app initialization
- Database management functions
- Authentication routes (register, login, logout)
- BMI calculation and storage
- PDF generation with ReportLab
- Email integration with SMTP
- Session management

### style.css (Responsive Styling)
- Mobile-first responsive design
- CSS Grid and Flexbox layouts
- Color scheme with CSS variables
- Form styling
- Table styling
- Badge components
- Navigation bar
- Card layouts

### HTML Templates
- **base.html**: Navigation, footer, block extensions
- **register.html**: User registration form with validation
- **login.html**: User login form
- **dashboard.html**: BMI records table and quick start
- **bmi.html**: BMI calculator form with instructions
- **result.html**: Result display with health advice

## 🐛 Troubleshooting

### Port Already in Use
```python
# In app.py, change:
app.run(debug=True, host='127.0.0.1', port=5001)  # Use 5001 instead
```

### Database Errors
```bash
# Delete the database and restart (creates new one)
del database.db
python app.py
```

### Email Not Sending
- Verify Gmail credentials in app.py
- Use App Password, not regular Gmail password
- Ensure 2FA is enabled
- Check internet connection
- Verify sender email is correctly configured

### SMTP Connection Error
- Verify Gmail account allows less secure apps (if not using app password)
- Check firewall/network settings
- Verify port 465 is not blocked

## 📱 Browser Support

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile Safari (iOS 14+)
- ✅ Chrome Mobile

## 🔒 Production Deployment

For production deployment, consider:

1. **Security**
   - Change SECRET_KEY to a strong random value
   - Use environment variables for sensitive data
   - Set DEBUG=False
   - Use HTTPS

2. **Database**
   - Migrate to PostgreSQL or MySQL
   - Set up proper backups
   - Use connection pooling

3. **Email**
   - Use transactional email service (SendGrid, Mailgun)
   - Implement email verification
   - Set up proper email templates

4. **Server**
   - Use gunicorn or uWSGI as WSGI server
   - Set up Nginx as reverse proxy
   - Implement rate limiting
   - Use proper logging

5. **Hosting**
   - Deploy on Heroku, AWS, DigitalOcean, etc.
   - Set up CI/CD pipeline
   - Configure monitoring and alerts

## 📄 API Response Format

### Successful Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {}
}
```

### Error Response
```json
{
  "success": false,
  "errors": ["Error message 1", "Error message 2"]
}
```

## 🎓 Learning Resources

This project demonstrates:
- Flask web application development
- SQLite database design
- User authentication and sessions
- PDF generation
- Email integration
- Responsive web design
- Client-side form validation
- Server-side request validation
- RESTful API design patterns

## 📜 License

This project is provided as-is for educational and commercial use.

## 👨‍💻 Code Quality

- Clean, readable variable names
- Proper error handling
- Input validation on client and server
- Comments on important sections
- DRY (Don't Repeat Yourself) principles
- Separation of concerns
- Responsive design best practices

## 📞 Support

For issues or questions:
1. Check the RUN.md file for detailed setup instructions
2. Review troubleshooting section above
3. Ensure all dependencies are installed correctly
4. Check Python version compatibility

## 🎯 Future Enhancements

Possible improvements:
- User profile page
- BMI trend charts and graphs
- Goal setting and tracking
- Multi-language support
- Dark mode theme
- Export to CSV/Excel
- Mobile app version
- OAuth authentication
- Two-factor authentication
- User activity log

---

**Built with ❤️ for health tracking** 🏥

Version 1.0.0 - December 2024
