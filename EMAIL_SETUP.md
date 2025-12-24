# Email Configuration Guide

Email sending is **optional** but fully implemented. Here's how to enable it:

## ⚠️ Important Note
The email feature is **disabled by default** because Gmail credentials need to be configured first.

If you don't need email functionality, you can:
1. Simply skip this setup
2. Use all other features (registration, BMI calculation, PDF generation, dashboard)
3. Just don't click "Send Report via Email"

---

## 📧 How to Enable Email (Optional)

### Step 1: Enable 2-Factor Authentication on Gmail

1. Go to: https://myaccount.google.com/security
2. Look for "2-Step Verification"
3. Click "Enable" if not already enabled
4. Follow Gmail's instructions to set it up

### Step 2: Generate Gmail App Password

1. Go to: https://myaccount.google.com/apppasswords
   (You must have 2FA enabled first)
2. Select "Mail" from the "Select app" dropdown
3. Select "Windows Computer" (or your device type)
4. Click "Generate"
5. Gmail will show you a 16-character password
6. **Copy this password** (you'll need it next)

### Step 3: Update app.py with Your Credentials

1. Open `app.py` in a text editor
2. Find line 161: `sender_email = "your_email@gmail.com"`
   - Replace `your_email@gmail.com` with your actual Gmail address
   
3. Find line 162: `sender_password = "your_app_password"`
   - Replace `your_app_password` with the 16-character App Password from Step 2

**Example:**
```python
sender_email = "john.doe@gmail.com"
sender_password = "abcd efgh ijkl mnop"  # 16-character app password
```

### Step 4: Restart the Application

1. Stop the Flask server (Ctrl+C)
2. Run the app again: `python app.py`
3. The email functionality is now enabled!

---

## ✅ Test Email Feature

1. Register and login to your account
2. Calculate a BMI
3. Click "Send Report via Email"
4. Check your email inbox (may take 1-2 minutes)

---

## 🔒 Alternative: Use Environment Variables (Recommended for Production)

For better security, use environment variables instead of editing the code:

**Windows Command Prompt:**
```bash
set GMAIL_EMAIL=your_email@gmail.com
set GMAIL_APP_PASSWORD=your_16_char_password
python app.py
```

**Linux/Mac Terminal:**
```bash
export GMAIL_EMAIL=your_email@gmail.com
export GMAIL_APP_PASSWORD=your_16_char_password
python3 app.py
```

Then update app.py lines 161-162 to read from environment variables:
```python
sender_email = os.environ.get('GMAIL_EMAIL', "your_email@gmail.com")
sender_password = os.environ.get('GMAIL_APP_PASSWORD', "your_app_password")
```

---

## ⚠️ Troubleshooting Email Issues

### Email still not sending?

**Check these things:**

1. **2FA Not Enabled**
   - Gmail requires 2-Factor Authentication
   - Can't use App Passwords without it

2. **Wrong Credentials**
   - Verify email and app password are correct
   - Copy-paste to avoid typos

3. **Firewall/Network**
   - Port 465 (Gmail SMTP) must be accessible
   - Check if your network blocks SMTP

4. **App Password Format**
   - Should be 16 characters with spaces
   - Example: `abcd efgh ijkl mnop`

5. **Check Server Log**
   - Look at the terminal/console where Flask is running
   - Error messages are printed there

---

## 🔐 Security Best Practices

1. **Never share your App Password** - it's like a second password
2. **Use App Password, not your regular password** - Gmail will reject regular password
3. **For production**: Use environment variables, never hardcode in source code
4. **Revoke old App Passwords**: Go to account security and delete unused ones
5. **Enable Gmail alerts**: Be notified if someone else logs in

---

## ❌ Email Completely Optional

The entire BMI Health Tracker works without email:
- ✅ User registration
- ✅ Secure login
- ✅ BMI calculation
- ✅ PDF generation (saved locally)
- ✅ Dashboard with records
- ✅ Health advice

Only the email sending feature requires configuration.

---

## 📝 Quick Checklist

- [ ] Enabled 2FA on Gmail account
- [ ] Generated App Password from Gmail
- [ ] Copied App Password (16 characters with spaces)
- [ ] Updated app.py line 161 with Gmail email
- [ ] Updated app.py line 162 with App Password
- [ ] Restarted Flask application
- [ ] Tested by sending a report

---

**Questions?** Check RUN.md for more detailed setup instructions.
