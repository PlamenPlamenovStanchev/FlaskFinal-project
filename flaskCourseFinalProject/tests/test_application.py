from unittest.mock import patch

from flask_testing import TestCase

from Services.ses import SESService
from models import RoleType, UserModel
from tests.base import generate_token, APIBaseTestCase
from tests.factories import UserFactory


class TestApp(APIBaseTestCase):
    endpoints = (
        ("GET", "/complainers/complaints"),
        ("POST", "/complainers/complaints"),
        ("PUT", "/approver/complaints/1/approved"),
        ("PUT", "/approver/complaints/2/rejected"),
        ("POST", "/admins/users"),
        ("POST", "/users/change-password"),
        ("DELETE", "/admins/complaints/1"),
    )


    def make_request(self, method, endpoint, headers=None):
        if method == "GET":
            response = self.client.get(endpoint, headers=headers)

        elif method == "POST":
            response = self.client.get(endpoint, headers=headers)

        elif method == "PUT":
            response = self.client.put(endpoint, headers=headers)
        else:
            response = self.client.delete(endpoint, headers=headers)
        return response

    def test_login_required_endpoints(self):
        endpoints = (
            ("GET", "/complainers/complaints"),
            ("POST", "/complainers/complaints"),
            ("PUT", "/approver/complaints/1/approved"),
            ("PUT", "/approver/complaints/2/rejected"),
            ("POST", "/admins/users"),
            ("POST", "/users/change-password"),
            ("DELETE", "/admins/complaints/1"),
        )
        for method, endpoint in self.endpoints:
            response = self.make_request(method, endpoint)


            self.assertEqual(response.status_code, 401)
            expected_message = {"message": "Invalid or missing token"}
            self.assertEqual(response.json, expected_message)


    def test_login_required_endpoints_invalid_token(self):

        headers = {"Authorization": "Bearer invalid"}
        for method, endpoint in self.endpoints:
            response = self.make_request(method, endpoint, headers=headers)

            self.assertEqual(response.status_code, 401)
            expected_message = {"message": "Invalid or missing token"}
            self.assertEqual(response.json, expected_message)


    def test_permission_required_endpoints_approvers(self):
        endpoints = (
            ("PUT", "/approver/complaints/1/approved"),
            ("PUT", "/approver/complaints/2/rejected"),
        )
        headers = {"Authorization": "Bearer invalid"}
        user = UserFactory()
        user_token = generate_token(user)
        headers = {"Authorization": f"Bearer {user_token}"}
        for method, endpoint in endpoints:
            response = self.make_request(method, endpoint, headers=headers)

            self.assertEqual(response.status_code, 403)
            expected_message = {"message": "You do not have permissions to access this resource"}
            self.assertEqual(response.json, expected_message)

    def test_permission_required_endpoints_admins(self):
        endpoints = (
            ("POST", "/admins/users"),
            ("DELETE", "/admins/complaints/1"),
        )
        user = UserFactory()
        user_token = generate_token(user)
        headers = {"Authorization": f"Bearer {user_token}"}
        for method, endpoint in endpoints:
            response = self.make_request(method, endpoint, headers=headers)

            self.assertEqual(response.status_code, 403)
            expected_message = {"message": "You do not have permissions to access this resource"}
            self.assertEqual(response.json, expected_message)


    def test_permission_required_endpoints_complainers(self):
        endpoints = (
            ("POST", "/complainers/complaints"),
        )
        user = UserFactory(role=RoleType.admin)
        user_token = generate_token(user)
        headers = {"Authorization": f"Bearer {user_token}"}
        for method, endpoint in endpoints:
            response = self.make_request(method, endpoint, headers=headers)

            self.assertEqual(response.status_code, 403)
            expected_message = {"message": "You do not have permissions to access this resource"}
            self.assertEqual(response.json, expected_message)

class TestRegisterSchema(APIBaseTestCase):


    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)

    def test_register_schema_missing_fields(self):
        # "email": "a@a.com",
        # "password": "<asd",
        # "first_name": "Test",
        # "last_name": "User",
        # "phone_number": "1234567890",
        # "iban": "BG1234"

        data = {}
        users = UserModel.query.all()
        self.assertEqual(len(users), 0)


        response = self.client.post("/register", json=data)
        self.assertEqual(response.status_code, 400)
        error_message = response.json["message"]
        for field in ("email", "password", "first_name", "last_name", "iban"):
            self.assertIn(field, error_message)

        users = UserModel.query.all()
        self.assertEqual(len(users), 0)



    def test_register_schema_invalid_email(self):
        data = {
            "email": "asd",
            "password": "<asd",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "1234567890",
            "iban": "BG1234"
        }
        response = self.client.post("/register", json=data)
        self.assertEqual(response.status_code, 400)
        error_message = response.json["message"]
        expected_message = "Invalid payload {'email' :['Not a valid email address']}"
        self.assertEqual(error_message, expected_message)

    def test_register_schema_invalid_password(self):
        data = {
            "email": "a@a.com",
            "password": "<asd",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "1234567890",
            "iban": "BG1234"
        }
        response = self.client.post("/register", json=data)
        self.assertEqual(response.status_code, 400)
        error_message = response.json["message"]
        expected_message = "Invalid payload {'password' :['Not a valid password']}"
        self.assertEqual(error_message, expected_message)

    @patch.object(SESService, "send_email")
    def test_register(self, mock_ses):
        self.register_user()
        users = UserModel.query.all()
        expected_called_args = {
            "recipient": self.example_register_user_data["email"],
            "subject": f"Welcome {self.example_register_data['first_name']} {self.example_register_user_data['last_name']}",
            "content": "Welcome to our complaint system. You can now login and submit complaints! ",

        }
        self.assertEqual(len(users), 1)
        mock_ses.assert_called_once_with(**expected_called_args)


class TestLoginSchema(APIBaseTestCase):
    def test_login_schema_missing_fields(self):
        # "email": "a@a.com",
        # "password": "<asd",

        data = {}

        users = UserModel.query.all()
        self.assertEqual(len(users), 0)
        response = self.client.post("/login", json=data)
        self.assertEqual(response.status_code, 400)
        error_message = response.json["message"]
        for field in ("email", "password"):
            self.assertIn(field, error_message)

        users = UserModel.query.all()
        self.assertEqual(len(users), 0)

    def test_login_schema_invalid_email(self):
        data = {
            "email": "asd",
            "password": "<asd",
        }
        response = self.client.post("/login", json=data)
        self.assertEqual(response.status_code, 400)
        error_message = response.json["message"]
        expected_message = "Invalid payload {'email' :['Not a valid email address']}"
        self.assertEqual(error_message, expected_message)

    def test_register_schema_invalid_password(self):

        email, password = self.register_user()

        data = {
            "email": "a@a.com",
            "password": "<asd",

        }
        self.assertEqual(email, data["email"])
        response = self.client.post("/login", json=data)
        self.assertEqual(response.status_code, 400)
        error_message = response.json["message"]
        expected_message = "Invalid payload {'password' :['Not a valid password']}"
        self.assertEqual(error_message, expected_message)

    def test_login(self):
        data = {
            "email": "a@a.com",
            "password": "asd",
        }
        # email, password = self.register_user()
        user = UserFactory(password=data["password"], email=data["email"])
        response = self.client.post("/login", json=data)
        self.assertEqual(response.status_code, 200)
        token = response.json["token"]
        self.assertIsNotNone(token)


    def test_login_invalid_email_raises(self):
        email, password = self.register_user()

        data = {
            "email": "b@a.com",
            "password": "asd",
        }
        self.assertNotEqual(email, data["email"])
        user = UserModel.query.filter_by(email="b@a.com").all()
        self.assertEqual(len(user), 0)
        response = self.client.post("/login", json=data)
        self.assertEqual(response.status_code, 401)
        message = response.json
        expected_message = {"message": "Wrong email or password"}
        self.assertEqual(message, expected_message)

    def test_login_invalid_password_raises(self):
        email, password = self.register_user()

        data = {
            "email": "a@a.com",
            "password": "invalid",
        }
        self.assertNotEqual(password, data["password"])
        user = UserModel.query.filter_by(password="invalid").all()
        self.assertEqual(len(user), 1)
        response = self.client.post("/login", json=data)
        self.assertEqual(response.status_code, 401)
        message = response.json
        expected_message = {"message": "Wrong email or password"}
        self.assertEqual(message, expected_message)