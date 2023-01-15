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


class SMSMessage:
    def __init__(self, scheduled_at, message, from_number, to_number):
        self.scheduledAt = scheduled_at
        self.message = message,
        self.fromPhoneNumber = from_number
        self.toPhoneNumber = to_number

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


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