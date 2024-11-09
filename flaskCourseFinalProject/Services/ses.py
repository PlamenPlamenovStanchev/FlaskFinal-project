import boto3
from botocore.exceptions import ClientError
from decouple import config
from werkzeug.exceptions import InternalServerError


class SESService:
    def __init__(self):
        self.aws_key = config("AWS_ACCESS_KEY")
        self.aws_secret = config("AWS_SECRET_KEY")
        self.region = config("AWS_REGION")
        self.s3 = boto3.client(
            "ses", aws_access_key_id=self.aws_key,
            aws_secret_access_key=self.aws_secret,
            region_name=self.region
        )

    def send_email(self, recipient, subject, content):
        """
        Sends an email using AWS SES.

        :param recipient: Recipient email address (must be verified if SES is in sandbox mode).
        :param subject: Subject of the email.
        :param content: Content (body) of the email.
        :return: SES Message ID or raises an error if the email fails.
        """
        sender = config("EMAIL_SENDER")
        try:
            self.ses.send_email(
                Source=sender,
                Destination={
                    'ToAddresses': [recipient]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': content,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
        except ClientError as e:
            raise InternalServerError(f"Failed to send email: {str(e)}")


