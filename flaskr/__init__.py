# TEST VERSION USER INPUT NOT SANITIZED
# MOCKY MOCKIDY MOCK

from flask import Flask, jsonify, request
from datetime import datetime
app = Flask(__name__)

_mock_timestamp = datetime.utcnow().isoformat(timespec='seconds')
_current_id = 0


# Definitely TEMP
def _get_new_msg_id() -> int:
    global _current_id
    _current_id += 1
    return _current_id


# Simple test to see if we have contact
@app.route('/hello/')
def hello():
    return "hello"


@app.route('/hello/<x>')
def hello2(x):
    return "hello " + x


# Create new message
# Requires form-data 'message'
# Note returned timestamp format, iso 8601
# NOT SANITIZED
@app.route('/messages/', methods=['POST'])
def post_message() -> str:
    txt = request.form['text']
    return jsonify(id=_get_new_msg_id(),
                   created=_mock_timestamp,
                   createdBy="John Doe",
                   text=txt)


# Edit message
# Requires form-data 'newMessage'
# NOT SANITIZED
@app.route('/messages/<msg_id>', methods=['PUT'])
def replace_message(msg_id: int) -> str:
    new_text = request.form['newText']
    return jsonify(id=1,
                   created=_mock_timestamp,
                   createdBy="John Doe",
                   text=new_text)


# Get all messages by one user
# NOT SANITIZED
@app.route('/users/<usr_id>/messages', methods=['GET'])
def get_messages(usr_id: int) -> str:
    _mock_usr_name = "John Doe"
    msg1 = {'id': 1,
            'created': _mock_timestamp,
            'createdBy': _mock_usr_name,
            'text': "Hello world!"}
    msg2 = {'id': 2,
            'created': _mock_timestamp,
            'createdBy': _mock_usr_name,
            'text': "Hello world again!"}
    return jsonify([msg1, msg2])


# Delete message
# NOT SANITIZED
@app.route('/messages/<msg_id>', methods=['DELETE'])
def delete_messages(msg_id: int) -> str:
    id = int(msg_id)
    return jsonify(id=id)
