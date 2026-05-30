from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def env_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_service_role_key: str
    secret_key: str
    signing_private_key_b64: str
    signing_key_id: str
    app_timezone: str = "Asia/Manila"
    session_hours: int = 8
    max_login_attempts: int = 5
    login_cooldown_seconds: int = 300
    secure_cookies: bool = True


def load_settings() -> Settings:
    return Settings(
        supabase_url=require_env("SUPABASE_URL"),
        supabase_service_role_key=require_env("SUPABASE_SERVICE_ROLE_KEY"),
        secret_key=require_env("SECRET_KEY"),
        signing_private_key_b64=require_env("CITLOG_SIGNING_PRIVATE_KEY_B64"),
        signing_key_id=os.getenv("CITLOG_SIGNING_KEY_ID", "citlog-ed25519-v1"),
        app_timezone=os.getenv("APP_TIMEZONE", "Asia/Manila"),
        session_hours=env_int("SESSION_HOURS", 8),
        max_login_attempts=env_int("MAX_LOGIN_ATTEMPTS", 5),
        login_cooldown_seconds=env_int("LOGIN_COOLDOWN_SECONDS", 300),
        secure_cookies=os.getenv("SESSION_COOKIE_SECURE", "true").strip().lower() != "false",
    )


settings = load_settings()
