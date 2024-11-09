from marshmallow import fields
from marshmallow_enum import EnumField

from models.enums import State
from schemas.base import BaseComplaintsSchema


class ComplaintResponseSchema(BaseComplaintsSchema):
    status = EnumField(State, by_value=True)
    complainer_id = fields.Integer(required=True)
    create_on = fields.DateTime(required=True)
    photo_url = fields.Str(required=True)