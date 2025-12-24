# Invoice Setup Guide

The invoice feature is **fully implemented and ready to use**. You can create and send invoices in two ways:

---

## 📄 Invoice Features

### What's Included in Each Invoice
- **Invoice Number**: Unique identifier (INV-PatientID-RecordID-Timestamp)
- **Patient Information**: Name and ID
- **BMI Assessment Details**: Height, Weight, BMI Value, BMI Category
- **Charges Breakdown**:
  - Consultation Fee: $50.00
  - BMI Assessment Fee: $30.00
  - Health Report Fee: $20.00
  - **Total Amount: $100.00**
- **Payment Terms**: Due within 30 days
- **Invoice Date**: Automatically set to current date

---

## 🚀 How to Use Invoice Feature

### Step 1: Calculate BMI
1. Login to your account
2. Go to "BMI Calculator"
3. Enter your height and weight
4. Submit the form

### Step 2: Create Invoice
1. On the result page, click **"🧾 Create Invoice"**
2. The system will generate an invoice with all your details
3. You'll see the invoice number and total amount displayed

### Step 3: Send Invoice via Email

**Option A: Gmail (if configured)**
1. Click **"📧 Send Invoice via Email"**
2. The invoice PDF will be sent to your registered email
3. (Requires Gmail credentials - see EMAIL_SETUP.md)

**Option B: FormSubmit (No Configuration Needed)**
1. Click **"✉️ Send via FormSubmit"**
2. The system prepares the invoice for FormSubmit
3. FormSubmit is a free service that doesn't require any setup

---

## 📧 Send Invoice via Email (Gmail)

### Prerequisites
- Gmail account
- 2-Factor Authentication enabled on Gmail
- App Password generated

### Setup Steps
1. Follow the instructions in **EMAIL_SETUP.md**
2. Configure `sender_email` and `sender_password` in `app.py` or use environment variables
3. Restart the application
4. Invoices will be sent with PDF attachment

---

## ✉️ Send Invoice via FormSubmit (No Setup Required)

### What is FormSubmit?
FormSubmit is a **free service** that allows you to send emails without any configuration.

### How It Works
1. Click **"✉️ Send via FormSubmit"** button
2. Your invoice data is prepared and ready
3. You can integrate it with your email backend

### FormSubmit API Usage
If you want to create a custom integration, here's how:

```html
<form action="https://formsubmit.co/YOUR_EMAIL" method="POST">
    <input type="hidden" name="invoice_number" value="INV-123-456">
    <input type="hidden" name="recipient_email" value="user@example.com">
    <input type="hidden" name="patient_name" value="John Doe">
    <input type="hidden" name="total_amount" value="100.00">
    <input type="hidden" name="payment_terms" value="Due within 30 days">
    <input type="hidden" name="_captcha" value="false">
    <button type="submit">Send Invoice</button>
</form>
```

---

## 💾 Invoice Data Stored in Database

All invoices are stored in the `invoices` table with:
- `invoice_number`: Unique identifier
- `patient_id`: User ID
- `record_id`: Associated BMI record
- `consultation_fee`, `bmi_assessment_fee`, `health_report_fee`: Individual charges
- `total_amount`: Sum of all charges ($100.00)
- `payment_status`: Current status (Pending/Paid)
- `payment_terms`: Payment deadline
- `invoice_date`: When invoice was created
- `due_date`: When payment is due

---

## 📋 Features Included

✅ **Automatic Invoice Generation**
- Invoices created automatically on demand
- Unique invoice numbers for tracking
- Professional PDF format

✅ **Multiple Payment Options**
- Invoice includes payment terms
- Support for future payment status tracking
- Clear breakdown of charges

✅ **Flexible Delivery Methods**
- Email via Gmail (if configured)
- FormSubmit integration
- Database storage for record keeping

✅ **Patient Details**
- Name and ID
- Health assessment information
- Invoice date and due date

---

## 🔧 Customizing Invoice Amounts

To change the invoice fees, edit `app.py` in the `create_invoice` function:

```python
consultation_fee = 50.00          # Change this
bmi_assessment_fee = 30.00        # Change this
health_report_fee = 20.00         # Change this
```

---

## ❓ Troubleshooting

### Invoice Not Creating
1. Make sure you're logged in
2. Make sure the BMI record exists
3. Check the server logs for errors

### Email Not Sending
1. Check if Gmail is configured (see EMAIL_SETUP.md)
2. Verify sender email and app password
3. Check internet connection

### FormSubmit Issues
1. Check that invoice data was prepared correctly
2. Verify recipient email is correct
3. Check server logs for submission errors

---

## 📝 Quick Checklist

- [ ] Calculated a BMI
- [ ] Created an invoice
- [ ] Viewed invoice details
- [ ] Sent invoice via email (if configured)
- [ ] Tested FormSubmit integration
- [ ] Checked invoice in database

---

**Questions?** Check the main README.md for more information.
