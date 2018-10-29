# TEST VERSION USER INPUT NOT SANITIZED
# MOCKY MOCKIDY MOCK

import os
import sys
import json
import psycopg2
from datetime import datetime
#from urllib.parse import urlparse
from flask import Flask, jsonify, request

DATABASE_URL = os.environ['DATABASE_URL']


def db(str):
    print(str)
    sys.stdout.flush()


db_conn = psycopg2.connect(DATABASE_URL, sslmode='require')

app = Flask(__name__)


# mock
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


@app.route('/helloDB')
def helloDB():
    cur = db_conn.cursor()
    cur.execute("SELECT * FROM message LIMIT 3")
    rows = cur.fetchall()
    tmp1 = []
    for row in rows:
        tmp2 = []
        for col in row:
            if type(col) == datetime:
                tmp2.append(col.strftime('%d/%m/%Y'))
            else:
                tmp2.append(col)
        tmp1.append(tmp2)
    return json.dumps(tmp1)


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
