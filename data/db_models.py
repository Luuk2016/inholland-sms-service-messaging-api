import json
import os
import uuid
from dataclasses import dataclass
import datetime

import jwt
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class SMSMessage:  # pylint: disable=too-few-public-methods
    """The message that is put in the queue"""

    def __init__(self, ScheduledAt, Message, FromPhoneNumber, ToPhoneNumber):  # pylint: disable=C0103
        self.ScheduledAt = ScheduledAt  # pylint: disable=C0103
        self.Message = Message  # pylint: disable=C0103
        self.FromPhoneNumber = FromPhoneNumber  # pylint: disable=C0103
        self.ToPhoneNumber = ToPhoneNumber  # pylint: disable=C0103

    def to_json(self):
        """Message to Json"""
        return json.dumps(self, default=json_default)


def json_default(value):
    """Json default"""
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    return value.__dict__


@dataclass
class Location(db.Model):
    """The location class is used to store the various locations"""
    id: UUID(as_uuid=True)  # pylint: disable=c0103
    name: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, unique=True, nullable=False)

    def __init__(self, name):
        self.name = name


@dataclass
class Group(db.Model):
    """The group class is used to store the various groups"""
    id: UUID(as_uuid=True)  # pylint: disable=c0103
    location_id: UUID(as_uuid=True)
    name: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = db.Column(UUID(as_uuid=True), db.ForeignKey("location.id"), nullable=False)
    location = db.relationship("Location", backref="group", uselist=False)
    name = db.Column(db.String, unique=True, nullable=False)

    def __init__(self, location_id, name):
        self.location_id = location_id
        self.name = name


@dataclass
class Student(db.Model):
    """The student class is used to store the various students"""
    id: UUID(as_uuid=True)  # pylint: disable=c0103
    group_id: UUID(as_uuid=True)
    name: str
    phone_number: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey("group.id"), nullable=False)
    group = db.relationship("Group", backref="student", uselist=False)
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, unique=True, nullable=False)

    def __init__(self, group_id, name, phone_number):
        self.group_id = group_id
        self.name = name
        self.phone_number = phone_number


@dataclass
class Lecturer(db.Model):
    """The lecturer class is used to store the various lecturers"""
    id: UUID(as_uuid=True)  # pylint: disable=c0103
    email: str
    password: str

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password
        ).decode()

    @staticmethod
    def decode_token(token):
        """Decode JWT token payload"""
        try:
            payload = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=['HS256'])

            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again'
