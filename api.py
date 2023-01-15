import json
import uuid

from flask import Flask, jsonify, Blueprint
import pika
from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError

from data.db_models import SMSMessage, Location, Group, Student

app = Flask(__name__)
api_bp = Blueprint('api', __name__, url_prefix='/')


@app.route("/send/groups/<int:group_id>", methods=['POST'])
def send_group(group_id):
    """Send message to all students in one group"""
    get_group("")
    message = SMSMessage("Test", "message", "nr", "nr")
    send_message_to_queue(message)
    return f'SMS send to group: {group_id}'


@app.route("/send/locations/<int:location_id>", methods=['POST'])
def send_location(location_id):
    """Send message to all students from all the groups of the location"""
    return f'Location: {location_id}'


def send_message_to_queue(message: SMSMessage):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.basic_publish(exchange='',
                          routing_key='SMSQueue',
                          body=message.toJson())
    connection.close()


def get_group(group_id):
    """Returns a specific group"""
    try:
        specific_group = Group.query.get(group_id)

        if not specific_group:
            return f"A group with id \"{group_id}\" doesn't exist.", 404

        return jsonify(specific_group), 200

    except SQLAlchemyError:
        return "Group couldn't be retrieved", 400


def get_location(location_id):
    """Returns a specific location"""
    try:
        specific_location = Location.query.get(location_id)

        if not specific_location:
            return f"A location with id \"{location_id}\" doesn't exist.", 404

        return jsonify(specific_location), 200

    except SQLAlchemyError:
        return "Location couldn't be retrieved", 400


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

        return jsonify(students), 200

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

        return jsonify(groups), 200

    except SQLAlchemyError:
        return "Groups couldn't be retrieved", 400