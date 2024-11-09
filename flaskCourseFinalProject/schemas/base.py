from marshmallow import Schema, fields


class BaseComplaintsSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    amount = fields.Int(required=True)