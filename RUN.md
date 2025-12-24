# BMI Health Tracker - Setup and Run Instructions

## Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

## Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Email (Optional)
To enable email functionality, edit `app.py` and update the email credentials in the `send_email()` function (around line 140):

```python
sender_email = "your_email@gmail.com"
sender_password = "your_app_password"  # Use Gmail App Password, not your regular password
```

**How to get Gmail App Password:**
1. Go to https://myaccount.google.com/
2. Click "Security" in the left menu
3. Enable 2-Factor Authentication if not already enabled
4. Search for "App passwords"
5. Create an app password for Mail
6. Use this password in the app.py file

### 3. Run the Application
```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

## Features

### Authentication
- **Register**: Create a new account with name, email, and password
- **Login**: Secure login with password hashing
- **Logout**: End your session securely
- **Session Management**: Automatic session handling with login-required protection

### BMI Calculator
- **Input**: Height (cm) and Weight (kg)
- **Calculation**: Automatic BMI calculation with 2 decimal places
- **Categories**:
  - Underweight: BMI < 18.5
  - Normal: BMI 18.5 - 24.9
  - Overweight: BMI 25 - 29.9
  - Obese: BMI ≥ 30

### Dashboard
- View all your BMI records
- Quick access to calculate new BMI
- View detailed reports for each calculation

### PDF Reports
- Auto-generated PDF after each BMI calculation
- Includes patient info, measurements, BMI, category, and health advice
- Downloadable from results page

### Email Integration
- Send PDF reports directly to your email
- Professional email format with attachment
- Works with Gmail SMTP

## Database
- SQLite database (database.db) is created automatically on first run
- Stores user information and BMI records
- No manual database setup required

## Project Structure
```
BMI indicator project/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── database.db           # SQLite database (created on first run)
├── templates/            # HTML templates
│   ├── base.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── bmi.html
│   └── result.html
├── static/
│   ├── css/
│   │   └── style.css     # Responsive styling
│   └── js/
│       └── main.js       # Frontend JavaScript
└── temp_pdfs/           # Temporary PDF storage (created on demand)
```

## Security Notes
- Passwords are hashed using Werkzeug security functions
- Session management with Flask sessions
- CSRF protection recommended for production
- Email credentials should not be hardcoded in production

## Mobile Responsive
- Fully responsive design for mobile, tablet, and desktop
- Mobile-first approach
- Optimized for all screen sizes

## Troubleshooting

### Port 5000 already in use
Change the port in the last line of app.py:
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # Use 5001 instead
```

### Email not sending
- Verify Gmail credentials in app.py
- Ensure Gmail App Password is used (not regular password)
- Check that 2FA is enabled on Gmail account
- Verify internet connection

### Database errors
- Delete `database.db` file and restart the app to recreate it
- Ensure the application has write permissions in the project directory

## Default Test Credentials
You can use the following to test the application:
- Name: Test User
- Email: test@example.com
- Password: password123

## Browser Compatibility
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Notes
- Uses SQLite for simple local storage
- For production, consider PostgreSQL or MySQL
- PDF generation may take a few seconds for first-time use

---

Enjoy tracking your health with BMI Health Tracker! 🏥
