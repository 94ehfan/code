from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Red Sox Ticket Draft"
    database_url: str = "postgresql://draft:draft@localhost:5432/ticketdraft"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # Anthropic
    anthropic_api_key: str = ""

    # App URL (for links in SMS)
    app_url: str = "http://localhost:5173"

    model_config = {"env_file": ".env"}


settings = Settings()
