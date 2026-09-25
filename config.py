import os
import pymysql

def resolve_database_uri():
    """
    Hospital Management System (HMS) Database URI Resolver
    Default target: XAMPP / phpMyAdmin MySQL defaults:
      - Host: localhost (3306)
      - User: root
      - Password: "" (blank)
      - Database: hospital_db
    
    If MySQL is running and accessible with credentials, it connects via PyMySQL.
    If MySQL is not reachable or credentials mismatch, it automatically falls back
    to SQLite (hospital_dev.db) so development and local testing remain smooth and crash-free.
    """
    db_user = os.environ.get('DB_USER', 'root')
    db_password = os.environ.get('DB_PASSWORD', '')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = int(os.environ.get('DB_PORT', 3306))
    db_name = os.environ.get('DB_NAME', 'hospital_db')

    # Explicit override to use SQLite
    if os.environ.get('USE_SQLITE', '0') == '1':
        return 'sqlite:///hospital_dev.db'

    # Check MySQL reachability
    try:
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            port=db_port,
            connect_timeout=1
        )
        conn.close()
        # Connection succeeded! Use MySQL
        if db_password:
            return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
        else:
            return f"mysql+pymysql://{db_user}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    except Exception as e:
        print(f"[HMS Database Notice] MySQL at {db_host}:{db_port} not reachable with user '{db_user}' (Details: {e}).")
        print("[HMS Database Notice] Auto-activating local fallback: 'sqlite:///hospital_dev.db'")
        return 'sqlite:///hospital_dev.db'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'medicare-hms-super-secret-key-2026-xyz')

    # MySQL Parameters
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'hospital_db')

    # Active Database URI
    SQLALCHEMY_DATABASE_URI = resolve_database_uri()

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

    # Session settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
