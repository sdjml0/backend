import asyncio
import json
import logging
import socket
import smtplib
import urllib.request
import urllib.error
from typing import Optional
from uuid import UUID
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException, status

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
    def send_otp_email(recipient_email: str, otp_code: str, purpose: str = "signup") -> bool:
        import base64

        subject = f"Your Verification OTP Code: {otp_code}"
        purpose_label = "Email Verification (Sign Up)" if purpose == "signup" else "Password Reset Request"

        frontend_url = getattr(settings, "FRONTEND_URL", "https://frontend-ui-new-liart.vercel.app").rstrip("/")
        action_path = "forgot-password" if purpose == "password_reset" else "forgot-password"

        # Encode OTP into URL-safe Base64 token to hide raw numeric OTP in URL
        otp_token = base64.urlsafe_b64encode(otp_code.encode("utf-8")).decode("utf-8").rstrip("=")
        action_url = f"{frontend_url}/{action_path}?token={otp_token}"
        button_text = "Reset Password" if purpose == "password_reset" else "Verify OTP"

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
                                        <span style="color: #818CF8; font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;">Security Center</span>
                                    </div>
                                    <h1 style="color: #FFFFFF; font-size: 22px; font-weight: 700; margin: 0; letter-spacing: -0.5px;">E-Commerce Admin Portal</h1>
                                </td>
                            </tr>

                            <!-- Body Content -->
                            <tr>
                                <td style="padding: 40px; text-align: left;">
                                    <h2 style="font-size: 18px; font-weight: 600; color: #0F172A; margin-top: 0; margin-bottom: 8px;">Authentication Code</h2>
                                    <p style="font-size: 14px; color: #64748B; margin-top: 0; margin-bottom: 28px; line-height: 1.6;">
                                        You recently initiated an <strong>{purpose_label}</strong>. Use the verification code below or click the action button to complete the process.
                                    </p>

                                    <!-- OTP Code Box -->
                                    <div style="background-color: #F1F5F9; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; text-align: center; margin-bottom: 32px;">
                                        <div style="font-size: 11px; font-weight: 700; color: #64748B; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px;">One-Time Security Passcode</div>
                                        <span style="font-family: 'Courier New', Courier, monospace; font-size: 36px; font-weight: 800; letter-spacing: 10px; color: #4F46E5; display: inline-block; margin-left: 10px;">{otp_code}</span>
                                    </div>

                                    <!-- Primary CTA Button -->
                                    <div style="text-align: center; margin-bottom: 32px;">
                                        <a href="{action_url}" target="_blank" style="background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%); color: #FFFFFF; padding: 14px 36px; text-decoration: none; border-radius: 10px; font-weight: 600; font-size: 15px; display: inline-block; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);">
                                            {button_text}
                                        </a>
                                    </div>

                                    <!-- Link Fallback -->
                                    <div style="background-color: #F8FAFC; border-radius: 8px; padding: 16px; margin-bottom: 24px; border-left: 3px solid #4F46E5;">
                                        <p style="font-size: 12px; color: #64748B; margin: 0 0 6px 0;">Having trouble clicking the button? Copy and paste this URL into your browser:</p>
                                        <a href="{action_url}" style="font-size: 12px; color: #4F46E5; text-decoration: underline; word-break: break-all;">{action_url}</a>
                                    </div>

                                    <!-- Expiration & Security Info -->
                                    <p style="font-size: 13px; color: #94A3B8; margin: 0; line-height: 1.5; text-align: center;">
                                        ⏱️ This security code expires in <strong style="color: #64748B;">{settings.OTP_EXPIRE_MINUTES} minutes</strong>. If you did not request this email, no action is required.
                                    </p>
                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #F8FAFC; border-top: 1px solid #E2E8F0; padding: 24px 40px; text-align: center;">
                                    <p style="font-size: 12px; color: #94A3B8; margin: 0 0 4px 0;">© 2026 E-Commerce Platform. All rights reserved.</p>
                                    <p style="font-size: 11px; color: #CBD5E1; margin: 0;">Automated security notification • Please do not reply to this message</p>
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
                        logger.info(f"✅ OTP email delivered to {recipient_email} via Brevo API.")
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

                with SMTP_SSL_IPv4(smtp_host, smtp_port, timeout=12) as server:
                    server.login(settings.USERNAME_GMAIL_SMTP, settings.PASSWORD_GMAIL_SMTP)
                    server.sendmail(settings.USERNAME_GMAIL_SMTP, [recipient_email], msg.as_string())
                logger.info(f"✅ OTP email delivered to {recipient_email} via SSL SMTP.")
                return True
            except Exception as e:
                logger.error(f"❌ SMTP email dispatch failed ({e}).")

        logger.info(f"ℹ️ Dev/Mock Mode OTP for {recipient_email}: [{otp_code}]")
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
        from features.otp.service import OTPService

        otp_res = await OTPService.verify_otp(
            email=req.email,
            otp_code=req.otp,
            purpose="password_reset"
        )

        user = await UserRepository.get_user_by_email(req.email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        hashed_password = hash_password(req.new_password)
        await OTPRepository.update_user_password(req.email, hashed_password)

        if "otpid" in otp_res:
            await OTPRepository.delete_otp(otp_res["otpid"])

        return {
            "success": True,
            "message": "Password reset successfully. You can now login with your new password."
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
    async def update_profile(userid: UUID, user_data: UserUpdate) -> UserResponse:
        existing = await UserRepository.get_user_by_id(userid)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found."
            )

        updated = await UserRepository.update_user(userid, user_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile."
            )

        u = dict(updated)
        return UserResponse(
            userid=u["userid"],
            name=u["name"],
            email=u["email"],
            phone=u.get("phone"),
            address=u.get("address"),
            city=u.get("city"),
            postalcode=u.get("postalcode"),
            country=u.get("country"),
        )

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
