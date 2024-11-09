from marshmallow import Schema, fields, validate, ValidationError, validates_schema

from utils.decorators import validate_schema
from utils.usablefunctions import validate_password_strength


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.And(
        validate.Length(min=6, max=20),
    validate_password_strength))


class UserRegisterSchema(UserLoginSchema):
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    phone = fields.String(required=True)
    iban = fields.String(required=True)


class UserCreateRequestSchema(UserRegisterSchema):
    role = fields.String(required=True, validate=validate.OneOf(["admin", "approver"]))
    certificate = fields.URL()

    @validate_schema
    def validate_certificate(self, data, **kwargs):
        if data["role"] == "approver" and "certificate" not in data:
            raise ValidationError(
                "You must append certificate for approver user",
                field_names=["certificate"],
            )
        if data["role"] == "admin" and "certificate" in data:
            del data["certificate"]

class PasswordChangeSchema(Schema):
    old_password = fields.String(required=True)
    new_password = fields.String(required=True)

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        # Ensure that the old password is not the same as the new password
        if data["old_password"] == data["new_password"]:
            raise ValidationError(
            "New password cannot be the same as the old password.",
                    field_names=["new_password"],
                )
