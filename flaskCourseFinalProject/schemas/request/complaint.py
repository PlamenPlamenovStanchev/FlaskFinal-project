from marshmallow import fields

from schemas.base import BaseComplaintsSchema


class ComplaintRequestSchema(BaseComplaintsSchema):
    photo = fields.String(required=True)
    photo_extension = fields.String(required=True)