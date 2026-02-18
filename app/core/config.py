from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # =========================
    # DATABASE
    # =========================
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int

    # =========================
    # SECURITY
    # =========================
    SECRET_KEY: str
    ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # =========================
    # APP
    # =========================
    APP_NAME: str 
    DEBUG: bool 
    VERSION: str

    # =========================
    # BACKBLAZE B2
    # =========================
    B2_KEYID: str
    B2_KEYNAME: str
    B2_APPLICATIONKEY: str
    B2_ENDPOINT_URL: str


    class Config:
        env_file = ".env"


settings = Settings()
