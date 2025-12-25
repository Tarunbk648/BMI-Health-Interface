# Password Reset with FormSubmit

Password reset emails use **FormSubmit.co** - a free service that requires zero configuration!

## ✅ NO SETUP REQUIRED!

The password reset feature is **ready to use immediately**. No credentials, no configuration needed!

## How FormSubmit Works

FormSubmit.co is a service that:
- ✅ Accepts form submissions via HTTP
- ✅ Automatically sends professional emails
- ✅ No authentication needed
- ✅ Completely free
- ✅ Works globally

## Testing Password Reset

1. **Login** to your BMI Health Tracker
2. **Click** "Forgot password?" on the login page
3. **Enter** your registered email address
4. **Check your inbox** for the reset link email
5. **Click** the reset link in the email
6. **Enter your new password** (minimum 6 characters)
7. **Confirm** password matches
8. **Done!** Password has been reset ✅

## Email Verification (First Time Only)

**When you use an email for the first time with FormSubmit:**

FormSubmit may send you a verification email first:
- Open your email
- Click the **verification link** from FormSubmit
- After that, password reset emails will work normally

This is a one-time step for security. After verification, all future emails will go through automatically.

## What You'll Receive

Users will receive an email with:
- ✅ Secure password reset link
- ✅ Their name in the greeting
- ✅ Link expires after 1 hour
- ✅ Security instructions
- ✅ One-time use (can't be reused)

## Features

✅ Secure token generation (32-character random tokens)
✅ Password reset links expire after 1 hour
✅ One-time use only (tokens can't be reused)
✅ Database tracking of all reset requests
✅ Professional email formatting
✅ No configuration needed
✅ Works globally
✅ Completely free

## Troubleshooting

### Email not received?

**Check these things:**

1. **Wait 1-2 minutes**
   - Emails can take a moment to arrive

2. **Check spam/junk folder**
   - Sometimes emails go to spam
   - Mark as "Not Spam" to prevent future emails going to spam

3. **Verify first-time verification (if applicable)**
   - If this is the first time using this email with FormSubmit
   - Check for a verification email from FormSubmit
   - Click the verification link first
   - Then request password reset again

4. **Try with a different email**
   - Use another registered email to test
   - This helps isolate if it's a specific email issue

5. **Check Flask console**
   - Look at terminal where Flask is running
   - Error messages are printed there

### Reset link says "Invalid or expired"?

- Links expire after 1 hour
- Request a new password reset if link expired
- Check the token in the URL is correct

### Still having issues?

- Email from FormSubmit@formsubmit.co (check for verification emails)
- Check spam/junk folder
- Try again after a few minutes
- Clear browser cache and cookies

## Routes Available

- `GET /forgot-password` - Forgot password page
- `POST /send-reset-email` - Send reset link via FormSubmit
- `GET /reset-password?token=...` - Reset password form
- `POST /reset-password-submit` - Process new password

## Database Schema

Password reset tokens are stored in `password_reset_tokens` table:
- `id` - Token ID
- `user_id` - User who requested reset
- `token` - Secure random token (32 characters)
- `created_at` - When token was created
- `expires_at` - When token expires (1 hour)
- `used` - Whether token has been used (0 or 1)

## Security

✅ Tokens are cryptographically secure (32 random characters)
✅ Links expire after 1 hour
✅ Tokens are one-time use only (marked as used after reset)
✅ All requests tracked in database
✅ HTTPS required by FormSubmit
✅ User data is protected

## Environment Variables

Not needed for FormSubmit! The `.env` file is optional and not required for password reset functionality.

If you had `.env` with Gmail credentials before, you can delete it or keep it for other features.

## Advantages of FormSubmit

| Feature | FormSubmit | Gmail SMTP |
|---------|-----------|-----------|
| Setup Time | 0 minutes | 20+ minutes |
| Configuration | None | 2FA + App Password |
| Email Verification | Per email (1st time) | Not needed |
| Speed | Instant | Usually instant |
| Cost | Free | Free |
| Support | Good | Good |
| Global Reliability | Excellent | Excellent |

## How to Customize

To send reset emails to a different email address (for testing):

Edit `app.py` line 709:
```python
formsubmit_url = 'https://formsubmit.co/ajax/' + email
```

Change `email` to your custom email (but keep the user's email in the form data).

## Limits

- ✅ No daily limits on FormSubmit free plan
- ✅ No credit card required
- ✅ Can handle unlimited submissions

## File Checklist

- [x] Password reset feature implemented
- [x] FormSubmit integration complete
- [x] No configuration needed
- [x] Ready to use immediately

---

**Password reset is ready to use! No setup needed!** 🚀

Just test it:
1. Forgot password page
2. Enter email
3. Check inbox for reset link
4. Done!
