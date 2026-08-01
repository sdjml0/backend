import json
import logging
import socket
import smtplib
import urllib.request
import urllib.error

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import settings

logger = logging.getLogger(__name__)


def _safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))


def _create_ipv4_socket(address, timeout=12, source_address=None):
    """
    Creates an IPv4-only socket connection.
    Prevents '[Errno 101] Network is unreachable' on cloud hosts like Render
    where IPv6 address resolution is attempted without IPv6 routing support.
    """
    host, port = address
    err = None
    for res in socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        sock = None
        try:
            sock = socket.socket(af, socktype, proto)
            if timeout is not None:
                sock.settimeout(timeout)
            if source_address:
                sock.bind(source_address)
            sock.connect(sa)
            return sock
        except Exception as e:
            err = e
            if sock is not None:
                sock.close()
    if err is not None:
        raise err
    raise socket.error("No IPv4 address found for SMTP host.")


class SMTP_IPv4(smtplib.SMTP):
    """SMTP client forced to use IPv4 sockets on cloud host containers."""
    def _get_socket(self, host, port, timeout):
        return _create_ipv4_socket((host, port), timeout, self.source_address)


class SMTP_SSL_IPv4(smtplib.SMTP_SSL):
    """SMTP_SSL client forced to use IPv4 sockets on cloud host containers."""
    def _get_socket(self, host, port, timeout):
        new_socket = _create_ipv4_socket((host, port), timeout, self.source_address)
        return self.context.wrap_socket(new_socket, server_hostname=self._host)


class EmailService:

    @staticmethod
    def send_otp_email(recipient_email: str, otp_code: str, purpose: str = "signup") -> bool:
        """
        Sends an email verification (OTP code or password reset link) via Brevo, Resend HTTPS API, or SMTP fallback.
        """
        is_password_reset = (
            "reset" in purpose.lower() or 
            purpose.lower().strip() in ["password_reset", "password reset request", "password reset", "password-reset"]
        )

        frontend_base = getattr(settings, "FRONTEND_URL", "https://frontend-ui-new-liart.vercel.app").rstrip("/")
        reset_link = f"{frontend_base}/forgot-password?token={otp_code}&resetotp={otp_code}"

        if is_password_reset:
            subject = "Password Reset Request - E-Commerce Security"
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset Request</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f6f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #333333; -webkit-font-smoothing: antialiased;">
    <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f4f6f9; padding: 40px 10px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 580px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 32px 40px; text-align: center;">
                            <h1 style="color: #ffffff; font-size: 22px; font-weight: 700; margin: 0; letter-spacing: 0.5px; text-transform: uppercase;">
                                E-Commerce Security
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 40px 32px 40px;">
                            <h2 style="color: #0f172a; font-size: 20px; font-weight: 600; margin: 0 0 16px 0;">
                                Password Reset Request
                            </h2>
                            <p style="font-size: 15px; line-height: 1.6; color: #475569; margin: 0 0 20px 0;">
                                Hello,
                            </p>
                            <p style="font-size: 15px; line-height: 1.6; color: #475569; margin: 0 0 28px 0;">
                                We received a request to reset the password for your account registered with <strong style="color: #0f172a;">{recipient_email}</strong>. Click the button below to set a new password:
                            </p>
                            
                            <!-- Action Button -->
                            <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 32px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{reset_link}" target="_blank" style="background-color: #2563eb; color: #ffffff; display: inline-block; padding: 14px 32px; font-size: 15px; font-weight: 600; text-decoration: none; border-radius: 8px; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);">
                                            Reset Password
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <!-- Fallback Link Box -->
                            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin: 28px 0 24px 0;">
                                <p style="margin: 0 0 6px 0; font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                    Button not working? Copy & paste this link into your browser:
                                </p>
                                <p style="margin: 0; font-size: 13px; word-break: break-all;">
                                    <a href="{reset_link}" style="color: #2563eb; text-decoration: underline;">{reset_link}</a>
                                </p>
                            </div>
                            
                            <!-- Security Alert Note -->
                            <div style="border-left: 4px solid #f59e0b; background-color: #fffbe6; padding: 14px 16px; border-radius: 0 6px 6px 0; margin-bottom: 24px;">
                                <p style="margin: 0; font-size: 13px; line-height: 1.5; color: #92400e;">
                                    🔒 This reset link is valid for <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>. If you did not request a password reset, you can safely ignore this email; your account remains secure.
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 24px 40px; border-top: 1px solid #e2e8f0; text-align: center;">
                            <p style="font-size: 12px; color: #94a3b8; margin: 0 0 8px 0;">
                                © E-Commerce Security Team • All rights reserved
                            </p>
                            <p style="font-size: 11px; color: #cbd5e1; margin: 0;">
                                This is an automated security transmission. Please do not reply to this message.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
        else:
            purpose_label = "Email Verification (Sign Up)" if purpose == "signup" else purpose.replace("_", " ").title()
            subject = f"Your Verification OTP Code: {otp_code}"
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verification Code</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f6f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #333333; -webkit-font-smoothing: antialiased;">
    <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f4f6f9; padding: 40px 10px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 580px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 32px 40px; text-align: center;">
                            <h1 style="color: #ffffff; font-size: 22px; font-weight: 700; margin: 0; letter-spacing: 0.5px; text-transform: uppercase;">
                                E-Commerce Security
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 40px 32px 40px;">
                            <h2 style="color: #0f172a; font-size: 20px; font-weight: 600; margin: 0 0 16px 0;">
                                Account Verification Code
                            </h2>
                            <p style="font-size: 15px; line-height: 1.6; color: #475569; margin: 0 0 20px 0;">
                                Hello,
                            </p>
                            <p style="font-size: 15px; line-height: 1.6; color: #475569; margin: 0 0 24px 0;">
                                You requested a 6-digit verification code for <strong>{purpose_label}</strong>. Please enter the code below:
                            </p>
                            
                            <!-- OTP Display Box -->
                            <div style="background-color: #f1f5f9; border: 1px dashed #cbd5e1; border-radius: 10px; padding: 20px; text-align: center; margin: 28px 0;">
                                <span style="font-family: 'Courier New', Courier, monospace; font-size: 36px; font-weight: 700; letter-spacing: 10px; color: #1e40af;">{otp_code}</span>
                            </div>

                            <!-- Security Alert Note -->
                            <div style="border-left: 4px solid #2563eb; background-color: #eff6ff; padding: 14px 16px; border-radius: 0 6px 6px 0; margin-bottom: 24px;">
                                <p style="margin: 0; font-size: 13px; line-height: 1.5; color: #1e40af;">
                                    🔒 This code is valid for <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>. Do not share this code with anyone. If you did not request this, please ignore this email.
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 24px 40px; border-top: 1px solid #e2e8f0; text-align: center;">
                            <p style="font-size: 12px; color: #94a3b8; margin: 0 0 8px 0;">
                                © E-Commerce Security Team • All rights reserved
                            </p>
                            <p style="font-size: 11px; color: #cbd5e1; margin: 0;">
                                This is an automated security transmission. Please do not reply to this message.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

        # Strategy 1: Primary Delivery via Brevo HTTPS REST API (Port 443 - No Custom Domain Required)
        if settings.BREVO_API_KEY:
            try:
                sender_email = settings.BREVO_SENDER_EMAIL or settings.USERNAME_GMAIL_SMTP or "noreply@ecommerce.com"
                payload = json.dumps({
                    "sender": {
                        "name": settings.EMAILS_FROM_NAME,
                        "email": sender_email
                    },
                    "to": [
                        {
                            "email": recipient_email
                        }
                    ],
                    "subject": subject,
                    "htmlContent": html_content
                }).encode("utf-8")

                brevo_key = settings.BREVO_API_KEY.strip().strip('"').strip("'")
                req = urllib.request.Request(
                    "https://api.brevo.com/v3/smtp/email",
                    data=payload,
                    headers={
                        "api-key": brevo_key,
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "User-Agent": "FastAPI-ECommerce/1.0"
                    },
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status in (200, 201, 202):
                        logger.info(f"📧 Email successfully dispatched to {recipient_email} via Brevo HTTPS API")
                        _safe_print(f"📧 Email successfully dispatched to {recipient_email} via Brevo HTTPS API")
                        return True
            except urllib.error.HTTPError as http_err:
                err_body = ""
                try:
                    err_body = http_err.read().decode("utf-8")
                except Exception:
                    err_body = str(http_err)
                logger.warning(f"⚠️ Brevo HTTP API dispatch failed (HTTP {http_err.code}): {err_body}")
                _safe_print(f"⚠️ Brevo HTTP API error ({http_err.code}): {err_body}")
            except Exception as brevo_err:
                logger.warning(f"⚠️ Brevo HTTP API dispatch failed ({brevo_err})")

        # Strategy 2: Resend HTTPS REST API (Port 443)
        if settings.RESEND_API_KEY:
            try:
                payload = json.dumps({
                    "from": f"{settings.EMAILS_FROM_NAME} <{settings.RESEND_FROM_EMAIL}>",
                    "to": [recipient_email],
                    "subject": subject,
                    "html": html_content
                }).encode("utf-8")

                req = urllib.request.Request(
                    "https://api.resend.com/emails",
                    data=payload,
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                        "User-Agent": "FastAPI-ECommerce/1.0"
                    },
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status in (200, 201):
                        logger.info(f"📧 Email successfully dispatched to {recipient_email} via Resend HTTPS API")
                        _safe_print(f"📧 Email successfully dispatched to {recipient_email} via Resend HTTPS API")
                        return True
            except urllib.error.HTTPError as http_err:
                err_body = ""
                try:
                    err_body = http_err.read().decode("utf-8")
                except Exception:
                    err_body = str(http_err)
                logger.warning(f"⚠️ Resend HTTP API dispatch failed (HTTP {http_err.code}): {err_body}. Attempting SMTP fallback...")
                _safe_print(f"⚠️ Resend HTTP API error ({http_err.code}): {err_body}")
            except Exception as resend_err:
                logger.warning(f"⚠️ Resend HTTP API dispatch failed ({resend_err}). Attempting SMTP fallback...")

        # Strategy 3: Determine SMTP configuration fallback
        smtp_user = settings.USERNAME_GMAIL_SMTP or settings.SMTP_USER or settings.EMAILS_FROM_EMAIL
        smtp_password = settings.PASSWORD_GMAIL_SMTP or settings.SMTP_PASSWORD

        if not smtp_user or smtp_user == "noreply@ecommerce.com" or not smtp_password:
            logger.warning(
                "⚠️ Resend API Key or SMTP Credentials missing on server! Please configure RESEND_API_KEY or SMTP credentials in Render Dashboard."
            )
            if is_password_reset:
                _safe_print(f"🔑 [DEV / FALLBACK LINK] Email: {recipient_email} | Purpose: {purpose} | Link: {reset_link}")
            else:
                _safe_print(f"🔑 [DEV / FALLBACK OTP] Email: {recipient_email} | Purpose: {purpose} | OTP: {otp_code}")
            return True

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{smtp_user}>"
        msg["To"] = recipient_email
        msg.attach(MIMEText(html_content, "html"))

        tls_error = "Not attempted"
        ssl_error = "Not attempted"

        # Try standard SMTP with STARTTLS over IPv4 (Port 587)
        try:
            with SMTP_IPv4(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, recipient_email, msg.as_string())

            logger.info(f"📧 Email successfully dispatched to {recipient_email} via TLS ({settings.SMTP_PORT})")
            _safe_print(f"📧 Email successfully dispatched to {recipient_email}")
            return True
        except Exception as e:
            tls_error = str(e)
            logger.warning(f"⚠️ SMTP TLS ({settings.SMTP_PORT}) failed on server: {tls_error}. Attempting SSL (Port 465) fallback...")

        # Fallback to SMTP_SSL over IPv4 (Port 465)
        try:
            with SMTP_SSL_IPv4(settings.SMTP_HOST, 465, timeout=10) as server:
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, recipient_email, msg.as_string())

            logger.info(f"📧 Email successfully dispatched to {recipient_email} via SSL (465)")
            _safe_print(f"📧 Email successfully dispatched to {recipient_email} via SSL fallback")
            return True
        except Exception as e:
            ssl_error = str(e)
            logger.error(f"❌ All SMTP dispatch attempts failed on server for {recipient_email}. TLS Error: {tls_error} | SSL Error: {ssl_error}")
            _safe_print(f"❌ SMTP failed for {recipient_email}. TLS: {tls_error} | SSL: {ssl_error}")

        # Safe fallback log output if email network services are unreachable
        if is_password_reset:
            logger.info(f"🔑 [FALLBACK LOG LINK] Email: {recipient_email} | Purpose: {purpose} | Link: {reset_link}")
            _safe_print(f"🔑 [FALLBACK LOG LINK] Email: {recipient_email} | Purpose: {purpose} | Link: {reset_link}")
        else:
            logger.info(f"🔑 [FALLBACK LOG OTP] Email: {recipient_email} | Purpose: {purpose} | OTP: {otp_code}")
            _safe_print(f"🔑 [FALLBACK LOG OTP] Email: {recipient_email} | Purpose: {purpose} | OTP: {otp_code}")
        return True


