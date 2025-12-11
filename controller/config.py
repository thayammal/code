class Config:
    SECRET_KEY = '#$uper$ecretKey123'  # Secret key for session management and security
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vpa.sqlite3'  # Database URI for SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking to save resources