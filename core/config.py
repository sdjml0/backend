from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://neondb_owner:npg_4mcHlQBOdYf6@ep-muddy-leaf-axcqb6r2.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"
    SECRET_KEY: str = "ThisIsMySecretKeyChangeInProduction"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # OTP Configuration
    OTP_EXPIRE_MINUTES: int = 10

    # SMTP / Email Configuration
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "onboarding@resend.dev"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    USERNAME_GMAIL_SMTP: str = ""
    PASSWORD_GMAIL_SMTP: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@ecommerce.com"
    EMAILS_FROM_NAME: str = "E-Commerce Verification"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()