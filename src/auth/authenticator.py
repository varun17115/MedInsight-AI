import bcrypt
from database.db_manager import DBManager, DatabaseManager
from src.auth.validators import validate_email, validate_password

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

class Authenticator:
    def __init__(self, db=None):
        self.db = db or DBManager()

    def hash_password(self, password: str) -> str:
        return hash_password(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return verify_password(password, hashed_password)

    def register(self, username, email, password, full_name, age=None, gender=None):
        success, _ = self.register_user(username, email, password, full_name, age, gender)
        return success

    def register_user(self, username, email, password, full_name, age=None, gender=None):
        if not username or len(username.strip()) < 3:
            return False, "Username must be at least 3 characters long."

        if not validate_email(email):
            return False, "Invalid email address format."

        is_valid_pwd, pwd_msg = validate_password(password)
        if not is_valid_pwd:
            return False, pwd_msg

        if self.db.get_user_by_username(username):
            return False, "Username already exists."

        if self.db.get_user_by_email(email):
            return False, "Email already registered."

        hashed = self.hash_password(password)
        user_id = self.db.create_user(
            username=username.strip(),
            email=email.strip().lower(),
            password_hash=hashed,
            full_name=full_name.strip(),
            age=age,
            gender=gender
        )

        if user_id:
            return True, "Registration successful!"
        return False, "Failed to create user account."

    def login(self, username, password):
        success, _, user = self.login_user(username, password)
        return user if success else None

    def login_user(self, credential, password):
        if not credential or not password:
            return False, "Username/Email and Password are required.", None

        user = self.db.get_user_by_credential(credential.strip())
        if not user:
            return False, "User not found.", None

        if self.verify_password(password, user['password_hash']):
            user_data = dict(user)
            user_data.pop('password_hash', None)
            return True, "Login successful!", user_data

        return False, "Invalid password.", None
