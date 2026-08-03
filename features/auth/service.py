import asyncio
import json
import logging
import socket
import smtplib
import urllib.request
import urllib.parse
import urllib.error
import secrets
from typing import Optional
from uuid import UUID
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse

from core.config import settings
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from features.auth.repository import UserRepository
from features.auth.schema import (
    UserLogin,
    UserResponse,
    UserSignup,
    UserUpdate,
    LoginResponse
)
from features.otp.repository import OTPRepository
from features.otp.schema import ResetPasswordRequest

logger = logging.getLogger(__name__)


def _create_ipv4_socket(address, timeout=12, source_address=None):
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
    def _get_socket(self, host, port, timeout):
        return _create_ipv4_socket((host, port), timeout, self.source_address)


class SMTP_SSL_IPv4(smtplib.SMTP_SSL):
    def _get_socket(self, host, port, timeout):
        new_socket = _create_ipv4_socket((host, port), timeout, self.source_address)
        return self.context.wrap_socket(new_socket, server_hostname=self._host)


class EmailService:

    @staticmethod
    def send_magic_link_email(recipient_email: str, token_code: str = None, purpose: str = "signup", otp_code: str = None) -> bool:
        active_code = token_code or otp_code or ""
        purpose_label = "Email Verification (Sign Up)" if purpose == "signup" else "Password Reset Request"
        subject = f"Verification Request for {purpose_label}"

        frontend_url = getattr(settings, "FRONTEND_URL", "https://frontend-ui-new-liart.vercel.app").rstrip("/")
        action_path = "verify-email" if purpose == "signup" else "forgot-password"
        encoded_email = urllib.parse.quote(recipient_email)
        action_url = f"{frontend_url}/{action_path}?token={active_code}&resetotp={active_code}&email={encoded_email}"
        button_text = "Verify Email & Log In" if purpose == "signup" else "Reset Password"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
        </head>
        <body style="margin: 0; padding: 0; background-color: #F8FAFC; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1E293B; -webkit-font-smoothing: antialiased;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #F8FAFC; padding: 40px 15px;">
                <tr>
                    <td align="center">
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 540px; background-color: #FFFFFF; border-radius: 16px; overflow: hidden; border: 1px solid #E2E8F0; box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.05);">
                            
                            <!-- Header Banner -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 32px 40px; text-align: center;">
                                    <div style="display: inline-block; background: rgba(79, 70, 229, 0.2); padding: 8px 16px; border-radius: 20px; margin-bottom: 12px; border: 1px solid rgba(129, 140, 248, 0.3);">
                                        <span style="color: #818CF8; font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;">Magic Link Authentication</span>
                                    </div>
                                    <h1 style="color: #FFFFFF; font-size: 22px; font-weight: 700; margin: 0; letter-spacing: -0.5px;">E-Commerce Admin Portal</h1>
                                </td>
                            </tr>

                            <!-- Body Content -->
                            <tr>
                                <td style="padding: 40px; text-align: left;">
                                    <h2 style="font-size: 18px; font-weight: 600; color: #0F172A; margin-top: 0; margin-bottom: 8px;">Action Required</h2>
                                    <p style="font-size: 14px; color: #64748B; margin-top: 0; margin-bottom: 32px; line-height: 1.6;">
                                        Click the secure button below to proceed with your <strong>{purpose_label}</strong>.
                                    </p>

                                    <!-- Primary CTA Button -->
                                    <div style="text-align: center; margin-bottom: 36px;">
                                        <a href="{action_url}" target="_blank" style="background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%); color: #FFFFFF; padding: 16px 40px; text-decoration: none; border-radius: 10px; font-weight: 600; font-size: 16px; display: inline-block; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3);">
                                            {button_text}
                                        </a>
                                    </div>

                                    <!-- Link Fallback -->
                                    <div style="background-color: #F8FAFC; border-radius: 8px; padding: 16px; margin-bottom: 24px; border-left: 3px solid #4F46E5;">
                                        <p style="font-size: 12px; color: #64748B; margin: 0 0 6px 0;">Or copy and paste this link into your browser:</p>
                                        <a href="{action_url}" style="font-size: 12px; color: #4F46E5; text-decoration: underline; word-break: break-all;">{action_url}</a>
                                    </div>

                                    <!-- Expiration & Security Info -->
                                    <p style="font-size: 13px; color: #94A3B8; margin: 0; line-height: 1.5; text-align: center;">
                                        ⏱️ This link is valid for <strong style="color: #64748B;">{settings.OTP_EXPIRE_MINUTES} minutes</strong>. If you did not request this email, please ignore it.
                                    </p>
                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #F8FAFC; border-top: 1px solid #E2E8F0; padding: 24px 40px; text-align: center;">
                                    <p style="font-size: 12px; color: #94A3B8; margin: 0 0 4px 0;">© 2026 E-Commerce Platform. All rights reserved.</p>
                                    <p style="font-size: 11px; color: #CBD5E1; margin: 0;">Automated security notification • Please do not reply</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        if settings.BREVO_API_KEY:
            try:
                sender_email = settings.BREVO_SENDER_EMAIL or settings.USERNAME_GMAIL_SMTP or "noreply@ecommerce.com"
                payload = json.dumps({
                    "sender": {
                        "name": settings.EMAILS_FROM_NAME,
                        "email": sender_email
                    },
                    "to": [{"email": recipient_email}],
                    "replyTo": {
                        "email": sender_email,
                        "name": settings.EMAILS_FROM_NAME
                    },
                    "headers": {
                        "Auto-Submitted": "auto-generated",
                        "X-Auto-Response-Suppress": "All"
                    },
                    "subject": subject,
                    "htmlContent": html_content
                }).encode("utf-8")

                req = urllib.request.Request(
                    "https://api.brevo.com/v3/smtp/email",
                    data=payload,
                    headers={
                        "api-key": settings.BREVO_API_KEY,
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=12) as response:
                    if response.status in (200, 201, 202):
                        logger.info(f"✅ Magic link email delivered to {recipient_email} via Brevo API.")
                        return True
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8") if e.fp else ""
                logger.warning(f"⚠️ Brevo API delivery failed HTTP {e.code}: {err_body}. Falling back to SMTP.")
            except Exception as e:
                logger.warning(f"⚠️ Brevo API delivery failed ({e}). Falling back to SMTP.")

        text_content = f"Hello,\n\nYou requested a {purpose_label}. Please click or copy and paste the link below into your browser to proceed:\n\n{action_url}\n\nThis link is valid for {settings.OTP_EXPIRE_MINUTES} minutes.\n\nThank you,\nE-Commerce Team"

        smtp_host = getattr(settings, "SERVER_GMAIL_SMTP", settings.SMTP_HOST)
        smtp_port = getattr(settings, "PORT_GMAIL_SMTP", settings.SMTP_PORT)
        if settings.PASSWORD_GMAIL_SMTP and settings.USERNAME_GMAIL_SMTP:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.USERNAME_GMAIL_SMTP}>"
                msg["To"] = recipient_email
                msg["Reply-To"] = settings.USERNAME_GMAIL_SMTP
                msg["Auto-Submitted"] = "auto-generated"
                msg["X-Auto-Response-Suppress"] = "All"
                msg["Message-ID"] = make_msgid()
                msg.attach(MIMEText(text_content, "plain"))
                msg.attach(MIMEText(html_content, "html"))

                if int(smtp_port) == 465:
                    with SMTP_SSL_IPv4(smtp_host, int(smtp_port), timeout=12) as server:
                        server.login(settings.USERNAME_GMAIL_SMTP, settings.PASSWORD_GMAIL_SMTP)
                        server.sendmail(settings.USERNAME_GMAIL_SMTP, [recipient_email], msg.as_string())
                else:
                    with SMTP_IPv4(smtp_host, int(smtp_port), timeout=12) as server:
                        server.ehlo()
                        server.starttls()
                        server.ehlo()
                        server.login(settings.USERNAME_GMAIL_SMTP, settings.PASSWORD_GMAIL_SMTP)
                        server.sendmail(settings.USERNAME_GMAIL_SMTP, [recipient_email], msg.as_string())

                logger.info(f"✅ Magic link email delivered to {recipient_email} via SMTP.")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to send magic link email to {recipient_email} via SMTP: {e}")
        return False

    send_otp_email = send_magic_link_email

    @staticmethod
    def send_profile_update_approval_email(recipient_email: str, token_code: str, pending_changes: dict) -> bool:
        subject = "Approve Requested Profile Changes"
        backend_url = (getattr(settings, "BACKEND_URL", None) or getattr(settings, "API_BASE_URL", "http://localhost:8000")).rstrip("/")
        encoded_email = urllib.parse.quote(recipient_email)
        action_url = f"{backend_url}/auth/approve-profile-update?approve_profile_token={token_code}&email={encoded_email}"

        changes_list = ""
        field_labels = {
            "name": "Full Name",
            "phone": "Phone Number",
            "address": "Street Address",
            "city": "City",
            "postalcode": "Postal Code",
            "country": "Country"
        }
        for k, label in field_labels.items():
            if k in pending_changes and pending_changes[k] is not None:
                changes_list += f"<li><strong>{label}:</strong> {pending_changes[k]}</li>"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
        </head>
        <body style="margin: 0; padding: 0; background-color: #F8FAFC; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1E293B; -webkit-font-smoothing: antialiased;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #F8FAFC; padding: 40px 15px;">
                <tr>
                    <td align="center">
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 540px; background-color: #FFFFFF; border-radius: 16px; overflow: hidden; border: 1px solid #E2E8F0; box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.05);">
                            <tr>
                                <td style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 32px 40px; text-align: center;">
                                    <div style="display: inline-block; background: rgba(16, 185, 129, 0.2); padding: 8px 16px; border-radius: 20px; margin-bottom: 12px; border: 1px solid rgba(52, 211, 153, 0.3);">
                                        <span style="color: #34D399; font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;">Profile Security Approval</span>
                                    </div>
                                    <h1 style="color: #FFFFFF; font-size: 22px; font-weight: 700; margin: 0; letter-spacing: -0.5px;">Approve Profile Changes</h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 40px; text-align: left;">
                                    <h2 style="font-size: 18px; font-weight: 600; color: #0F172A; margin-top: 0; margin-bottom: 8px;">Action Required: Verify Profile Update</h2>
                                    <p style="font-size: 14px; color: #64748B; margin-top: 0; margin-bottom: 20px; line-height: 1.6;">
                                        A request was received to update your profile details with the following values:
                                    </p>

                                    <div style="background-color: #F8FAFC; border-radius: 8px; padding: 16px 20px; margin-bottom: 28px; border: 1px solid #E2E8F0;">
                                        <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #334155; line-height: 1.8;">
                                            {changes_list}
                                        </ul>
                                    </div>

                                    <div style="text-align: center; margin-bottom: 36px;">
                                        <a href="{action_url}" target="_blank" style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: #FFFFFF; padding: 16px 40px; text-decoration: none; border-radius: 10px; font-weight: 600; font-size: 16px; display: inline-block; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);">
                                            Approve Changes
                                        </a>
                                    </div>

                                    <div style="background-color: #F8FAFC; border-radius: 8px; padding: 16px; margin-bottom: 24px; border-left: 3px solid #10B981;">
                                        <p style="font-size: 12px; color: #64748B; margin: 0 0 6px 0;">Or copy and paste this link into your browser:</p>
                                        <a href="{action_url}" style="font-size: 12px; color: #059669; text-decoration: underline; word-break: break-all;">{action_url}</a>
                                    </div>

                                    <p style="font-size: 13px; color: #94A3B8; margin: 0; line-height: 1.5; text-align: center;">
                                        ⏱️ This link is valid for <strong style="color: #64748B;">{settings.OTP_EXPIRE_MINUTES} minutes</strong>. If you did not initiate this change, please ignore this email.
                                    </p>
                                </td>
                            </tr>
                            <tr>
                                <td style="background-color: #F8FAFC; border-top: 1px solid #E2E8F0; padding: 24px 40px; text-align: center;">
                                    <p style="font-size: 12px; color: #94A3B8; margin: 0 0 4px 0;">© 2026 E-Commerce Platform. All rights reserved.</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        if settings.BREVO_API_KEY:
            try:
                sender_email = settings.BREVO_SENDER_EMAIL or settings.USERNAME_GMAIL_SMTP or "noreply@ecommerce.com"
                payload = json.dumps({
                    "sender": {"name": settings.EMAILS_FROM_NAME, "email": sender_email},
                    "to": [{"email": recipient_email}],
                    "replyTo": {"email": sender_email, "name": settings.EMAILS_FROM_NAME},
                    "subject": subject,
                    "htmlContent": html_content
                }).encode("utf-8")

                req = urllib.request.Request(
                    "https://api.brevo.com/v3/smtp/email",
                    data=payload,
                    headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=12) as response:
                    if response.status in (200, 201, 202):
                        logger.info(f"✅ Profile approval email sent to {recipient_email} via Brevo.")
                        return True
            except Exception as e:
                logger.warning(f"⚠️ Brevo API delivery failed ({e}). Falling back to SMTP.")

        smtp_host = getattr(settings, "SERVER_GMAIL_SMTP", settings.SMTP_HOST)
        smtp_port = getattr(settings, "PORT_GMAIL_SMTP", settings.SMTP_PORT)
        if settings.PASSWORD_GMAIL_SMTP and settings.USERNAME_GMAIL_SMTP:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.USERNAME_GMAIL_SMTP}>"
                msg["To"] = recipient_email
                msg.attach(MIMEText(html_content, "html"))

                if int(smtp_port) == 465:
                    server = SMTP_SSL_IPv4(smtp_host, int(smtp_port), timeout=12)
                else:
                    server = SMTP_IPv4(smtp_host, int(smtp_port), timeout=12)
                    server.starttls()

                server.login(settings.USERNAME_GMAIL_SMTP, settings.PASSWORD_GMAIL_SMTP)
                server.sendmail(settings.USERNAME_GMAIL_SMTP, recipient_email, msg.as_string())
                server.quit()
                logger.info(f"✅ Profile approval email sent to {recipient_email} via SMTP.")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to send profile approval email to {recipient_email} via SMTP: {e}")

        # Fallback log output for dev testing if email credentials are not configured or failed
        logger.info(f"🔑 [DEV / FALLBACK LINK] Email: {recipient_email} | Purpose: profile_update | Link: {action_url}")
        print(f"🔑 [DEV / FALLBACK LINK] Email: {recipient_email} | Purpose: profile_update | Link: {action_url}")
        return False


class UserService:

    @staticmethod
    async def signup(user: UserSignup):
        from features.otp.service import OTPService

        exists = await UserRepository.user_exists(user.email)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists."
            )

        hashed_password = hash_password(user.password)

        otp_code = OTPService._generate_6_digit_otp()
        payload = {
            "name": user.name,
            "email": user.email,
            "password": hashed_password,
            "phone": user.phone,
            "address": user.address,
            "city": user.city,
            "postalcode": user.postalcode,
            "country": user.country,
        }

        await OTPRepository.save_otp(
            email=user.email,
            otp_code=otp_code,
            purpose="signup",
            expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
            payload=payload
        )

        await asyncio.to_thread(
            EmailService.send_otp_email,
            recipient_email=user.email,
            otp_code=otp_code,
            purpose="signup"
        )

        return {
            "success": True,
            "message": f"Registration details received. 6-digit OTP code sent to {user.email}. Please verify OTP to complete account creation.",
            "email": user.email,
            "expires_in_minutes": settings.OTP_EXPIRE_MINUTES
        }

    @staticmethod
    async def reset_password(req: ResetPasswordRequest):
        from features.otp.service import MagicLinkService

        token = req.get_token()
        new_pwd = req.get_password()

        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Magic link token parameter ('token' or 'resetotp') is required for password reset."
            )

        if not new_pwd:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password parameter ('new_password' or 'password') is required."
            )

        otp_row = await OTPRepository.get_valid_otp_by_token(token)
        if not otp_row and req.email:
            otp_row = await OTPRepository.get_valid_otp(req.email, token, purpose="password_reset")

        if not otp_row or otp_row.get("purpose") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired magic link token. Please request a new password reset link."
            )

        target_email = req.email or otp_row["email"]
        otpid = otp_row["otpid"]

        user = await UserRepository.get_user_by_email(target_email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        hashed_password = hash_password(new_pwd)
        await OTPRepository.update_user_password(target_email, hashed_password)

        await OTPRepository.delete_otp(otpid)

        user_dict = dict(user)
        access_token = create_access_token(
            {
                "sub": str(user["userid"]),
                "name": user["name"],
                "email": user["email"],
                "phone": user_dict.get("phone"),
                "role": user_dict.get("role", "Owner")
            }
        )

        return {
            "success": True,
            "message": "Password updated successfully. You are now logged in.",
            "accessToken": access_token,
            "expiresIn": 3600,
            "user": {
                "id": str(user["userid"]),
                "name": user["name"],
                "email": user["email"],
                "role": user_dict.get("role", "Owner")
            }
        }

    @staticmethod
    async def login(login: UserLogin) -> LoginResponse:
        user = await UserRepository.get_user_by_email(login.email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        if not verify_password(login.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password."
            )

        user_dict = dict(user)

        access_token = create_access_token(
            {
                "sub": str(user["userid"]),
                "name": user["name"],
                "email": user["email"],
                "phone": user_dict.get("phone"),
                "role": user_dict.get("role", "Owner")
            }
        )

        return LoginResponse(
            success=True,
            accessToken=access_token,
            expiresIn=3600,
            user={
                "id": user["userid"],
                "name": user["name"],
                "email": user["email"],
                "role": user_dict.get("role", "Owner")
            }
        )

    @staticmethod
    async def get_profile(userid: UUID):
        user = await UserRepository.get_user_by_id(userid)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        user_dict = dict(user)

        return UserResponse(
            userid=user["userid"],
            name=user["name"],
            email=user["email"],
            phone=user_dict.get("phone"),
            address=user_dict.get("address"),
            city=user_dict.get("city"),
            postalcode=user_dict.get("postalcode"),
            country=user_dict.get("country"),
        )

    @staticmethod
    async def update_profile(userid: UUID, user_data: UserUpdate):
        existing = await UserRepository.get_user_by_id(userid)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found."
            )

        u_dict = dict(existing)
        recipient_email = u_dict.get("email")
        if not recipient_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email address is missing."
            )

        pending_changes = user_data.model_dump(exclude_unset=True)
        if not pending_changes:
            return UserResponse(
                userid=u_dict["userid"],
                name=u_dict["name"],
                email=u_dict["email"],
                phone=u_dict.get("phone"),
                address=u_dict.get("address"),
                city=u_dict.get("city"),
                postalcode=u_dict.get("postalcode"),
                country=u_dict.get("country"),
            )

        approval_token = secrets.token_urlsafe(32)
        payload = {
            "userid": str(userid),
            **pending_changes
        }

        # Stage profile changes in OTP repository with strict 10-minute expiration
        await OTPRepository.save_otp(
            email=recipient_email,
            otp_code=approval_token,
            purpose="profile_update",
            expires_in_minutes=10,
            payload=payload
        )

        # Dispatch verification email with direct backend approval URL
        UserService.send_profile_update_approval_email(
            recipient_email=recipient_email,
            token_code=approval_token,
            pending_changes=pending_changes
        )

        return {
            "requires_verification": True,
            "approval_token": approval_token,
            "message": "Verification email sent. Please click the approval button in your email within 10 minutes to confirm your profile changes.",
            "user": {
                "userid": str(u_dict["userid"]),
                "name": u_dict["name"],
                "email": u_dict["email"],
                "phone": u_dict.get("phone"),
                "address": u_dict.get("address"),
                "city": u_dict.get("city"),
                "postalcode": u_dict.get("postalcode"),
                "country": u_dict.get("country"),
            }
        }

    @staticmethod
    async def approve_profile_update(token: str, email: Optional[str] = None):
        frontend_url = getattr(settings, "FRONTEND_URL", "https://frontend-ui-new-liart.vercel.app").rstrip("/")
        otp_row = await OTPRepository.get_valid_otp_by_token(token)

        if not otp_row or otp_row.get("purpose") != "profile_update":
            redirect_url = f"{frontend_url}/settings?status=error&message=" + urllib.parse.quote("Invalid or expired profile update approval link. Changes were discarded.")
            return RedirectResponse(url=redirect_url, status_code=302)

        if email and otp_row.get("email"):
            if otp_row["email"].lower() != email.strip().lower():
                redirect_url = f"{frontend_url}/settings?status=error&message=" + urllib.parse.quote("Approval token email mismatch. Changes were discarded.")
                return RedirectResponse(url=redirect_url, status_code=302)

        otpid = otp_row["otpid"]
        payload_data = otp_row["payload"]

        if isinstance(payload_data, str):
            try:
                payload_data = json.loads(payload_data)
            except Exception:
                pass

        if not payload_data or not isinstance(payload_data, dict):
            await OTPRepository.delete_otp(otpid)
            redirect_url = f"{frontend_url}/settings?status=error&message=" + urllib.parse.quote("Malformed profile update payload. Changes were discarded.")
            return RedirectResponse(url=redirect_url, status_code=302)

        userid_str = payload_data.get("userid")
        if not userid_str:
            await OTPRepository.delete_otp(otpid)
            redirect_url = f"{frontend_url}/settings?status=error&message=" + urllib.parse.quote("User ID missing from profile update payload. Changes were discarded.")
            return RedirectResponse(url=redirect_url, status_code=302)

        target_userid = UUID(userid_str) if isinstance(userid_str, str) else userid_str

        update_data = UserUpdate(
            name=payload_data.get("name"),
            phone=payload_data.get("phone"),
            address=payload_data.get("address"),
            city=payload_data.get("city"),
            postalcode=payload_data.get("postalcode"),
            country=payload_data.get("country"),
        )

        updated = await UserRepository.update_user(target_userid, update_data)
        if not updated:
            redirect_url = f"{frontend_url}/settings?status=error&message=" + urllib.parse.quote("Failed to update profile changes in database.")
            return RedirectResponse(url=redirect_url, status_code=302)

        await OTPRepository.mark_verified(otpid)

        redirect_url = f"{frontend_url}/settings?status=approved&message=" + urllib.parse.quote("Changes made have been saved successfully!")
        return RedirectResponse(url=redirect_url, status_code=302)

    @staticmethod
    async def check_profile_approval_status(token: str):
        otp_row = await OTPRepository.get_valid_otp_by_token(token)
        if not otp_row or otp_row.get("purpose") != "profile_update":
            return {
                "approved": False,
                "status": "expired_or_not_found",
                "message": "Approval token expired or not found."
            }

        if otp_row.get("is_verified"):
            otpid = otp_row["otpid"]
            payload_data = otp_row["payload"]
            if isinstance(payload_data, str):
                try:
                    payload_data = json.loads(payload_data)
                except Exception:
                    pass

            userid_str = payload_data.get("userid") if isinstance(payload_data, dict) else None
            user_data = None
            if userid_str:
                u = await UserRepository.get_user_by_id(UUID(userid_str) if isinstance(userid_str, str) else userid_str)
                if u:
                    u_dict = dict(u)
                    user_data = {
                        "userid": str(u_dict["userid"]),
                        "name": u_dict["name"],
                        "email": u_dict["email"],
                        "phone": u_dict.get("phone"),
                        "address": u_dict.get("address"),
                        "city": u_dict.get("city"),
                        "postalcode": u_dict.get("postalcode"),
                        "country": u_dict.get("country"),
                    }

            await OTPRepository.delete_otp(otpid)
            return {
                "approved": True,
                "status": "completed",
                "message": "Profile changes approved and updated successfully!",
                "user": user_data
            }

        return {
            "approved": False,
            "status": "pending",
            "message": "Waiting for user to click email approval link."
        }

    @staticmethod
    async def delete_account(userid: UUID) -> dict:
        existing = await UserRepository.get_user_by_id(userid)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found."
            )

        await UserRepository.delete_user(userid)
        return {"success": True, "message": "User account successfully deleted."}
