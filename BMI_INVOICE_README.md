# 🏥 Patient BMI Invoice Generator

A **standalone HTML/CSS/JavaScript web application** for calculating BMI and generating professional invoices. No backend, no database, no authentication required.

---

## 📋 Features

✅ **Patient Information Form**
- Patient name, age, gender
- Height (cm) and weight (kg)
- Email ID for invoice delivery

✅ **BMI Calculation**
- Automatic calculation: `BMI = weight / (height in meters)²`
- 2 decimal place rounding
- Real-time classification

✅ **BMI Categories**
- **Underweight**: BMI < 18.5
- **Normal**: BMI 18.5 – 24.9
- **Overweight**: BMI 25 – 29.9
- **Obese**: BMI ≥ 30

✅ **Professional Invoice**
- Unique invoice number (auto-generated)
- Clinic name and branding
- Complete patient details
- Height, weight, BMI value, category
- Health recommendations based on BMI
- Professional PDF-ready design

✅ **Email Integration**
- Uses **FormSubmit** (no backend needed)
- Zero configuration required
- Sends invoice details via email
- Custom email subject and template

✅ **User Experience**
- Form validation
- Error messages for invalid inputs
- Mobile responsive design
- Printable invoice layout
- Clean, professional UI

---

## 📁 Files

| File | Purpose |
|------|---------|
| `bmi_invoice.html` | Main BMI calculator and invoice generator |
| `thank-you.html` | Thank you page after form submission |
| `BMI_INVOICE_README.md` | This file - Documentation |

---

## 🚀 Quick Start

### Option 1: Open Locally
1. Download `bmi_invoice.html` to your computer
2. Double-click to open in your browser
3. Fill in the form and click "Generate Invoice"
4. Click "Send Invoice to Email" to email it

### Option 2: Use with Web Server
```bash
# If you have Python 3 installed
python -m http.server 8000

# If you have Node.js installed
npx http-server

# If you have PHP installed
php -S localhost:8000
```

Then visit: `http://localhost:8000/bmi_invoice.html`

### Option 3: Host Online
Upload `bmi_invoice.html` and `thank-you.html` to any web hosting service:
- GitHub Pages (free)
- Netlify (free)
- Vercel (free)
- Firebase Hosting (free tier)
- Any shared hosting provider

---

## 📝 How to Use

### Step 1: Enter Patient Information
```
Patient Name: John Doe
Age: 35
Gender: Male
Height (cm): 175
Weight (kg): 80
Email: john@example.com
```

### Step 2: Click "Generate Invoice"
- Form validation occurs automatically
- Invalid inputs show error messages
- Invoice displays on the right side

### Step 3: Review Invoice
- Check all patient details
- Verify BMI calculation
- Read health recommendations

### Step 4: Send Invoice via Email
- Click "Send Invoice to Email"
- Invoice is sent to the email provided
- User receives confirmation

---

## 🔧 Customization

### Change Clinic Name
Edit line in `bmi_invoice.html`:
```html
<div class="clinic-name">🏥 HealthCare Clinic</div>
```

Change to:
```html
<div class="clinic-name">🏥 Your Clinic Name</div>
```

### Modify Invoice Charges
Currently, no charges are displayed. To add charges, update the invoice display section.

### Change Email Recipient (if not using form input)
In the JavaScript section, find:
```javascript
form.action = `https://formsubmit.co/${email}`;
```

Replace `${email}` with a fixed email to always send to that address.

### Customize Health Remarks
Edit the `healthRemarks` object:
```javascript
const healthRemarks = {
    'Underweight': 'Your custom message here...',
    'Normal': 'Your custom message here...',
    'Overweight': 'Your custom message here...',
    'Obese': 'Your custom message here...'
};
```

### Change Color Scheme
Edit the CSS gradient colors:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

---

## 📧 Email Setup with FormSubmit

### What is FormSubmit?
FormSubmit is a **free service** that:
- Handles form submissions without backend code
- Sends emails automatically
- Requires NO configuration
- Works with any HTML form

### How It Works
1. User fills the form and clicks "Send Invoice"
2. Form data is sent to: `https://formsubmit.co/user_email@gmail.com`
3. FormSubmit processes the submission
4. Email is sent to the user
5. User redirected to thank-you page

### Current Implementation
The form uses FormSubmit automatically when user clicks "Send Invoice to Email":

```javascript
// Update FormSubmit action with user's email
const form = document.getElementById('formsubmitForm');
form.action = `https://formsubmit.co/${email}`;

// Submit the form
form.submit();
```

### FormSubmit Features Used
```html
<input type="hidden" name="_subject" value="Patient BMI Invoice">
<input type="hidden" name="_template" value="table">
<input type="hidden" name="_captcha" value="false">
<input type="hidden" name="_next" value="thank-you.html">
```

| Feature | Purpose |
|---------|---------|
| `_subject` | Email subject line |
| `_template` | Email formatting (table layout) |
| `_captcha` | Disable CAPTCHA for automated forms |
| `_next` | Redirect page after submission |

### For Production Use
1. Visit: https://formsubmit.co
2. Enter your email address
3. Submit the form once
4. Confirm your email in FormSubmit
5. All future submissions will be delivered

---

## ✅ Form Validation

All fields are validated before invoice generation:

| Field | Validation |
|-------|-----------|
| Patient Name | Required, min 3 characters |
| Age | Required, between 1-120 |
| Gender | Required, select from dropdown |
| Height (cm) | Required, between 50-300 |
| Weight (kg) | Required, between 20-500 |
| Email | Required, valid email format |

Error messages display inline if validation fails.

---

## 🖨️ Printing

### Print Invoice
1. Click "Generate Invoice"
2. Press `Ctrl+P` (or `Cmd+P` on Mac)
3. Choose printer
4. Print settings automatically hide the form

### Print Confirmation Page
- Click "Print Confirmation" on thank-you page
- Professional thank-you message

---

## 📱 Responsive Design

- **Desktop**: Full 2-column layout
- **Tablet**: Stacked layout, optimized for touch
- **Mobile**: Single column, large buttons, readable text

---

## 🎨 Invoice Design Features

- **Professional**: Corporate color scheme and typography
- **Printable**: High contrast, clear layout
- **Accessible**: WCAG compliant colors and fonts
- **Responsive**: Works on all screen sizes
- **Clean**: Minimal clutter, organized information

---

## 🔐 Security & Privacy

✅ **No Data Storage**
- Form data is NOT saved anywhere
- No database used
- No cookies set
- No tracking

✅ **Browser-Based Calculation**
- BMI calculated in your browser
- Data never leaves your computer (except email submission)

✅ **Email Security**
- Uses HTTPS for FormSubmit
- Email sent through secure SMTP
- No data logged by FormSubmit

---

## 📊 Invoice Components

### 1. Header
- Clinic name and logo
- Invoice title

### 2. Invoice Details
- Invoice number
- Invoice date
- Patient information (name, age, gender, email)

### 3. Health Measurements
- Height (cm)
- Weight (kg)

### 4. BMI Results
- BMI value (2 decimal places)
- BMI category (color-coded)

### 5. Health Recommendation
- Personalized advice based on BMI category
- Professional medical recommendation

### 6. Footer
- Disclaimer
- Generation timestamp

---

## 🐛 Troubleshooting

### Invoice Not Generating
**Problem**: "Generate Invoice" button doesn't work
**Solution**:
1. Check browser console for errors (F12)
2. Ensure all form fields are filled
3. Check error messages below each field

### Email Not Sending
**Problem**: Invoice doesn't arrive in email
**Solution**:
1. Check spam/junk folder
2. Verify email address is correct
3. Confirm you can receive emails
4. Wait 2-3 minutes (can be slow)

### FormSubmit Not Working
**Problem**: Getting FormSubmit confirmation page
**Solution**:
1. FormSubmit requires email confirmation first time
2. Visit https://formsubmit.co
3. Enter your email
4. Confirm in your email inbox
5. Then forms will work automatically

### Invoice Not Printing Correctly
**Problem**: Form visible when printing
**Solution**:
1. Use print preview (Ctrl+P)
2. Check "Background graphics" is enabled
3. Adjust margins if needed

---

## 🚀 Advanced Customization

### Add Custom Logo
Replace the emoji clinic name with an image:
```html
<img src="logo.png" alt="Clinic Logo" style="height: 50px;">
```

### Change Currency
In the invoice, add currency symbol:
```javascript
document.getElementById('costDisplay').textContent = '$' + amount;
```

### Add Multiple Patients
Create form that populates hidden patient list and generates batch invoices.

### Database Integration (Optional)
To add a backend:
1. Create a server (Node.js, Python, PHP)
2. Send form data via AJAX
3. Store in database
4. Generate PDF instead of HTML

---

## 📄 Sample Invoice Data

```
Invoice Number: INV-20231221-3847
Invoice Date: December 21, 2023

Patient: John Doe
Age: 35, Male
Email: john@example.com

Height: 175 cm
Weight: 80 kg
BMI: 26.12
Category: Overweight

Recommendation: Your BMI indicates you are overweight...
```

---

## 🎯 Use Cases

- **Clinics**: Quick BMI assessment invoices
- **Fitness Centers**: Member BMI tracking
- **Hospitals**: Patient wellness records
- **Nutritionists**: Client health documentation
- **Personal Training**: Progress tracking
- **Telehealth**: Remote patient assessment

---

## 📞 Support

For issues with:
- **FormSubmit**: Visit https://formsubmit.co/documentation
- **HTML/CSS**: Check browser developer tools (F12)
- **Customization**: Modify CSS or JavaScript directly

---

## 📜 License

Free to use and modify for personal and commercial purposes.

---

## 🔄 Version History

**v1.0** (2024)
- Initial release
- Complete form and validation
- Invoice generation
- FormSubmit integration
- Mobile responsive
- Thank you page

---

## ✨ Features You Can Add

- [ ] BMI chart/graph visualization
- [ ] Multiple invoice templates
- [ ] PDF download instead of email
- [ ] Invoice history (localStorage)
- [ ] Multiple languages
- [ ] Dark mode toggle
- [ ] Prescription/recommendations
- [ ] Medical test recommendations
- [ ] Admin dashboard (with backend)
- [ ] Payment integration

---

**Last Updated**: December 2024
**Status**: Production Ready ✅

Enjoy using the BMI Invoice Generator!
