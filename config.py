import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE = os.environ.get('DATABASE_URL') or 'database.db'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    DEBUG = os.environ.get('DEBUG') or True

class EmailConfig:
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    SENDER_EMAIL = os.environ.get('GMAIL_EMAIL') or "your_email@gmail.com"
    SENDER_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD') or "your_app_password"

ENABLE_EMAIL = False

MAX_CONTENT_LENGTH = 16 * 1024 * 1024

BMI_CATEGORIES = {
    'Underweight': (0, 18.5),
    'Normal': (18.5, 25),
    'Overweight': (25, 30),
    'Obese': (30, float('inf'))
}

HEALTH_ADVICE = {
    'Underweight': 'Consider consulting a healthcare professional. A balanced diet with adequate calories and nutrients is important.',
    'Normal': 'Great! Maintain your healthy weight with regular exercise and a balanced diet.',
    'Overweight': 'Consider a healthier lifestyle with regular physical activity and a balanced diet. Consult a healthcare provider if needed.',
    'Obese': 'It is highly recommended to consult a healthcare professional for personalized advice on weight management.'
}
