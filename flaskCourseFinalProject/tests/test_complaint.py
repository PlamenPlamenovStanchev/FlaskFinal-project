import json
import os

from requests import patch

from Services.s3 import S3Service
from constants import TEMP_FILE_FOLDER
from managers.complainer import ComplainerManager
from models import ComplaintModel
from tests.base import APIBaseTestCase, generate_token, mock_uuid
from tests.factories import UserFactory
from utils.helpers import encoded_file


class TestComplaint(APIBaseTestCase):
    url = "/complainers/complaints"

def test_complaint_missing_input_fields_raises(self):
    comp = UserFactory()
    token = generate_token(comp)

    complaints = ComplaintModel.query.all()
    self.assertEqual(len(complaints), 0)
    data = {
        "title": "Test",
        "description": "Test test",
        "photo": encoded_file,
        "photo_extension": "png",
        "amount": 10.00,
    }

    for key in data:
        current_data = data.copy()
        current_data.pop(key)
        resp = self.client.post(
            self.url,
            data=json.dumps(current_data),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

        message = resp.json["message"]
        expected_message = "Invalid payload {'" + key + "': ['Missing data for required field.']}"
        self.assert400(resp)
        self.assertEqual(message, expected_message)

    complaints = ComplaintModel.query.all()
    self.assertEqual(len(complaints), 0)


@patch("uuid.uuid4", mock_uuid)
@patch.object(ComplainerManager, "issue_transaction")
@patch.object(S3Service, "upload_photo", return_value="some.s3.url")
def test_create_complaint(self, mock_s3, mock_issue_transaction):
    user = UserFactory()
    token = generate_token(user)
    header = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Test",
        "description": "Test test",
        "amount": 20.00,
        "photo": encoded_file,
        "photo_extension": "png",
    }

    complaints = ComplaintModel.query.all()
    self.assertEqual(len(complaints), 0)
    resp = self.client.post(self.url, headers=header, json=data)

    complaints = ComplaintModel.query.all()
    self.assertEqual(len(complaints), 1)

    extension = data["photo_extension"]
    name = mock_uuid() + "." + extension
    path = os.path.join(TEMP_FILE_FOLDER, name)

    mock_s3.assert_called_once_with(path, name, extension)

    mock_issue_transaction.assert_called_once_with(data["amount"],
                                                   user.first_name,
                                                   user.last_name,
                                                   user.iban,
                                                   complaints[0].id)
