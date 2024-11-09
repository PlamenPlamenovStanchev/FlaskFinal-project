from config import create_app
from managers.auth import AuthManager
from flask_testing import TestCase
from db import db
from models import UserModel


def mock_uuid():
    return "111111"


def generate_token(user):
    return AuthManager.encode_token(user)



class APIBaseTestCase(TestCase):
    def create_app(self):
        return create_app("config.TestingConfig")

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def register_user(self):
        example_register_user_data = {
            "email": "a@a.com",
            "password": "<asd",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "1234567890",
            "iban": "BG1234"
        }
        users = UserModel.query.all()
        self.assertEqual(len(users), 0)
        response = self.client.post("/register", json=example_register_user_data)
        self.assertEqual(response.status_code, 201)
        token = response.json["token"]
        self.assertIsNotNone(example_register_user_data)
        return (example_register_user_data['email'], example_register_user_data['password'])