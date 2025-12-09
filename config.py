import os
from dotenv import load_dotenv

# =================================================
# LOAD .env FIRST (FORCE OVERRIDE)
# =================================================
load_dotenv(override=True)

class Config:
    # =================================================
    # GENERAL
    # =================================================
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    # =================================================
    # DATABASE CONFIG
    # =================================================
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =================================================
    # EMAIL CONFIG (GMAIL)
    # =================================================
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() == "true"

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    # =================================================
    # OTP SETTINGS
    # =================================================
    OTP_ADMIN_EMAIL = os.getenv("OTP_ADMIN_EMAIL", MAIL_USERNAME)
    OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", 5))


# ========== DEBUG PRINTS ==========
print("========= CONFIG DEBUG =========")
print("DB_HOST =", Config.DB_HOST)
print("DB_PORT =", Config.DB_PORT)
print("DB_USER =", Config.DB_USER)
print("DB_NAME =", Config.DB_NAME)
print("FULL URI =", Config.SQLALCHEMY_DATABASE_URI)
print("MAIL_USERNAME =", Config.MAIL_USERNAME)
print("MAIL_PASSWORD =", Config.MAIL_PASSWORD)
print("================================")
