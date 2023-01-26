from urllib import request
import pika
from flask import Flask, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from marshmallow import ValidationError

from data.db_models import SMSMessage, Location, Group, Student
from data.validation_schemes import MessageValidationSchema

app = Flask(__name__)
api_bp = Blueprint('api', __name__, url_prefix='/')

db = SQLAlchemy()


@api_bp.route("/send/groups/<int:group_id>", methods=['POST'])
def send_group(group_id):
    """Send message to all students in one group"""
    try:
        data = MessageValidationSchema().load(request.json)

        students = get_students_from_group("6a6a1630-e4e8-4163-9954-1977c8d87012")
        for student in students[0]:
            send_message_to_queue(SMSMessage("test", data["Message"], data["From_phone_number"], student.phone_number))

        return f'SMS send to group: '

    except ValidationError as err:
        return jsonify(err.messages), 400


@api_bp.route("/send/locations/<uuid:location_id>", methods=['POST'])
def send_location(location_id):
    """Send message to all students from all the groups of the location"""
    try:
        data = MessageValidationSchema().load(request.json)

        groups = get_groups_from_locations(location_id)
        for group in groups:
            students = get_students_from_group(group.id)
            for student in students:
                send_message_to_queue(SMSMessage("test", data["Message"], data["From_phone_number"], student.phone_number))

        return f'SMS send to groups: '

    except ValidationError as err:
        return jsonify(err.messages), 400


def send_message_to_queue(message: SMSMessage):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.basic_publish(exchange='',
                          routing_key='SMSQueue',
                          body=message.toJson())
    connection.close()


def get_students_from_group(group_id):
    """Get all students from a specific group"""
    try:
        students = Student.query \
            .join(Group, Student.group_id == group_id) \
            .filter(Student.group_id == group_id) \
            .order_by(asc(Student.name)) \
            .all()

        if len(students) == 0:
            return "No students could be found", 200

        return students

    except SQLAlchemyError:
        return "Students couldn't be retrieved", 400


def get_groups_from_locations(location_id):
    """Get all groups from a specific location"""
    try:
        specific_location = Location.query.get(location_id)

        if not specific_location:
            return f"A location with id \"{location_id}\" doesn't exist", 404

        groups = Group.query \
            .join(Location, Group.location_id == location_id) \
            .filter(Location.id == location_id) \
            .order_by(asc(Group.name)) \
            .all()

        return groups

    except SQLAlchemyError:
        return "Groups couldn't be retrieved", 400