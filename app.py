from flask import Flask

app = Flask(__name__)


@app.route("/send/groups/<int:group_id>")
def send_group(group_id):
    """Send message to all students in one group"""
    return f'Group: {group_id}'


@app.route("/send/locations/<int:location_id>")
def send_location(location_id):
    """Send message to all students from all the groups of the location"""
    return f'Location: {location_id}'
