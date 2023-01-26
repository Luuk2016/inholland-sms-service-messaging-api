from marshmallow import Schema, fields, validate


class MessageValidationSchema(Schema):
    """Used to validate the posted data when trying to send a new SMS"""
    # noinspection PyTypeChecker
    Scheduled_at = fields.DateTime(required=True)
    # noinspection PyTypeChecker
    Message = fields.Str(required=True, validate=validate.Length(min=2))
    # noinspection PyTypeChecker
    From_phone_number = fields.Str(required=True, validate=validate.Length(min=8))

