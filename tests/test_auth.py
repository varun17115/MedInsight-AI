import os
import unittest
import tempfile
from src.auth.validators import validate_email, validate_password
from src.auth.authenticator import Authenticator
from database.db_manager import DBManager

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_file = os.path.join(self.temp_dir.name, "test_auth.db")
        self.db = DBManager(db_path=self.db_file, schema_path="database/schema.sql")
        self.auth = Authenticator(self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_email_validation(self):
        self.assertTrue(validate_email("user@example.com"))
        self.assertTrue(validate_email("patient.smith+test@hospital.org"))
        self.assertFalse(validate_email("invalid-email"))
        self.assertFalse(validate_email("@domain.com"))

    def test_password_validation(self):
        is_valid, msg = validate_password("StrongPass1")
        self.assertTrue(is_valid)

        is_valid, msg = validate_password("short1A")
        self.assertFalse(is_valid)
        self.assertIn("8 characters", msg)

        is_valid, msg = validate_password("nouppercase1")
        self.assertFalse(is_valid)

        is_valid, msg = validate_password("NOLOWERCASE1")
        self.assertFalse(is_valid)

        is_valid, msg = validate_password("NoNumberHere")
        self.assertFalse(is_valid)

    def test_user_registration_and_login(self):
        # Register valid user
        success, msg = self.auth.register_user(
            username="dr_smith",
            email="smith@hospital.com",
            password="SecurePassword1",
            full_name="Dr. Smith",
            age=45,
            gender="Male"
        )
        self.assertTrue(success)

        # Duplicate username
        success_dup, msg_dup = self.auth.register_user(
            username="dr_smith",
            email="other@hospital.com",
            password="SecurePassword1",
            full_name="Dr. Smith Dup"
        )
        self.assertFalse(success_dup)
        self.assertIn("Username already exists", msg_dup)

        # Duplicate email
        success_dup_email, msg_dup_email = self.auth.register_user(
            username="dr_smith2",
            email="smith@hospital.com",
            password="SecurePassword1",
            full_name="Dr. Smith 2"
        )
        self.assertFalse(success_dup_email)
        self.assertIn("Email already registered", msg_dup_email)

        # Successful login with username
        success_login, msg_login, user = self.auth.login_user("dr_smith", "SecurePassword1")
        self.assertTrue(success_login)
        self.assertEqual(user['username'], "dr_smith")
        self.assertNotIn("password_hash", user)

        # Successful login with email
        success_login_email, _, user_email = self.auth.login_user("smith@hospital.com", "SecurePassword1")
        self.assertTrue(success_login_email)
        self.assertEqual(user_email['username'], "dr_smith")

        # Failed login invalid password
        success_fail, msg_fail, _ = self.auth.login_user("dr_smith", "WrongPassword1")
        self.assertFalse(success_fail)
        self.assertIn("Invalid password", msg_fail)

if __name__ == '__main__':
    unittest.main()
