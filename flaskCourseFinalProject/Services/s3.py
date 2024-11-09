import boto3
from botocore.exceptions import ClientError
from decouple import config
from werkzeug.exceptions import InternalServerError


class S3Service:
    def __init__(self):
        self.aws_key = config("AWS_ACCESS_KEY")
        self.aws_secret = config("AWS_SECRET_KEY")
        self.bucket_name = config("AWS_BUCKET")
        self.region = config("AWS_REGION")
        self.s3 = boto3.client(
            "s3", aws_access_key_id=self.aws_key,
            aws_secret_access_key=self.aws_secret
        )

    def upload_photo(self, path, key, ext):
        try:
            # Removed the 'ACL' parameter to avoid the error
            self.s3.upload_file(
                path,
                self.bucket_name,
                key,
                ExtraArgs={'ContentType': f'image/{ext}'}
            )
            return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
        except ClientError as e:
            raise InternalServerError(f"S3 is not available at the moment: {str(e)}")

