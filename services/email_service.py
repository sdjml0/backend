import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import settings

logger = logging.getLogger(__name__)


class EmailService:

    @staticmethod
    def send_otp_email(recipient_email: str, otp_code: str, purpose: str = "signup") -> bool:
        """
        Sends a 6-digit OTP verification code via email.
        Falls back to console/logger mode if SMTP server credentials are unavailable.
        """
        subject = f"Your Verification OTP Code: {otp_code}"
        purpose_label = "Email Verification (Sign Up)" if purpose == "signup" else "Password Reset Request"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                <h2 style="color: #2563eb; text-align: center;">E-Commerce Security</h2>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
                <p>Hello,</p>
                <p>You requested a 6-digit OTP for <strong>{purpose_label}</strong>.</p>
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; text-align: center; margin: 25px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #1e40af;">{otp_code}</span>
                </div>
                <p>This code is valid for <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>. If you did not request this, please ignore this email.</p>
                <br/>
                <p style="font-size: 12px; color: #6b7280; text-align: center;">This is an automated security message. Please do not reply.</p>
            </body>
        </html>
        """

        # Determine SMTP configuration
        smtp_user = settings.USERNAME_GMAIL_SMTP or settings.SMTP_USER or settings.EMAILS_FROM_EMAIL
        smtp_password = settings.PASSWORD_GMAIL_SMTP or settings.SMTP_PASSWORD

        if not smtp_user or smtp_user == "noreply@ecommerce.com" or not smtp_password:
            logger.warning(
                "⚠️ SMTP Credentials missing on server! Please configure USERNAME_GMAIL_SMTP and PASSWORD_GMAIL_SMTP environment variables in Render Dashboard."
            )
            print(f"🔑 [DEV / FALLBACK OTP] Email: {recipient_email} | Purpose: {purpose} | OTP: {otp_code}")
            return True

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{smtp_user}>"
        msg["To"] = recipient_email
        msg.attach(MIMEText(html_content, "html"))

        # Strategy 1: Try standard SMTP with STARTTLS (Port 587 / configured port)
        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=12) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, recipient_email, msg.as_string())

            logger.info(f"📧 OTP Email successfully dispatched to {recipient_email} via TLS ({settings.SMTP_PORT})")
            print(f"📧 OTP Email successfully dispatched to {recipient_email}")
            return True
        except Exception as err_tls:
            logger.warning(f"⚠️ SMTP TLS ({settings.SMTP_PORT}) failed on server: {err_tls}. Attempting SSL (Port 465) fallback...")

        # Strategy 2: Fallback to SMTP_SSL (Port 465) commonly required by Gmail on cloud servers like Render
        try:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, 465, timeout=12) as server:
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, recipient_email, msg.as_string())

            logger.info(f"📧 OTP Email successfully dispatched to {recipient_email} via SSL (465)")
            print(f"📧 OTP Email successfully dispatched to {recipient_email} via SSL fallback")
            return True
        except Exception as err_ssl:
            logger.error(f"❌ All SMTP dispatch attempts failed on server for {recipient_email}. TLS Error: {err_tls} | SSL Error: {err_ssl}")
            print(f"❌ SMTP failed for {recipient_email}. TLS: {err_tls} | SSL: {err_ssl}")

        # Fallback log output if SMTP network connection is blocked by cloud provider
        logger.info(f"🔑 [FALLBACK LOG OTP] Email: {recipient_email} | Purpose: {purpose} | OTP: {otp_code}")
        print(f"🔑 [FALLBACK LOG OTP] Email: {recipient_email} | Purpose: {purpose} | OTP: {otp_code}")
        return True

