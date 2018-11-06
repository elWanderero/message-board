# TEST VERSION USER INPUT NOT SANITIZED
# MOCKY MOCKIDY MOCK

import os
from . import db_stuff
from .db_stuff import typ_msg_row, typ_msg_rows
import typing
from datetime import datetime
from flask import Flask, jsonify, request, wrappers, escape

# MSG_TABLE = 'message'
# MSG_USERNAME = 'createdby'
# MSG_TEXT_BODY = 'text'
# MSG_TIMESTAMP = 'created'
# MSG_UPDATED_TIMESTAMP = 'updated'
# MSG_ID = 'id'

typ_row_or_rows = typing.Union[typ_msg_row, typ_msg_rows]
# typ_fn_returns_msg_row = typing.Callable[..., typ_msg_row]
# typ_fn_returns_msg_rows = typing.Callable[..., typ_msg_rows]
# typ_msg_fn = typing.Union[typ_fn_returns_msg_row, typ_fn_returns_msg_rows]
typ_msg_fn = typing.Callable[..., typ_row_or_rows]
typ_Response = typing.Union[wrappers.Response]
typ_Response_fn = typing.Callable[..., wrappers.Response]

# mock
_mock_name = db_stuff._mock_name
# _mock_timestamp = datetime.utcnow().isoformat(timespec='seconds')


# TEMP SECURITY MEASURE! Put an URL_PREFIX in the environment
# to make stuff accesible only by putting '/URL_PREFIX' in front
# of all routes.
URL_PREFIX = os.getenv('URL_PREFIX')
if URL_PREFIX is None or URL_PREFIX == "":
    URL_PREFIX = ""
else:
    URL_PREFIX = "/" + URL_PREFIX

app = Flask(__name__)

##############################
# Simple testing API
##############################


# Simple test to see if we have contact
@app.route(URL_PREFIX+'/hello/')
def hello() -> str:
    return "hello"


# Test variable sending
@app.route(URL_PREFIX+'/hello/<x>')
def hello2(x) -> str:
    return "hello " + x


# Test databse connection
@app.route(URL_PREFIX+'/helloDB')
def hello_db() -> typ_Response:
    rows = db_stuff._oneoff_query("SELECT * FROM message LIMIT 3")
    return jsonify(_stringify_msgs(_sanitise_msgs(rows)))


# Clear all messages belonging to _mock_user
@app.route(URL_PREFIX+'/clearMock')
def clear_mock() -> str:
    db_stuff.clear_all_messages(_mock_name)
    return "yes"


#######################################
#                 API                 #
#######################################

############################
# POST: Create new message
############################
# Requires form-data 'message'
# NOT SANITIZED
@app.route(URL_PREFIX+'/messages/', methods=['POST'])
def post_message() -> typ_Response:
    text = request.form['text']
    new_msg_row = db_stuff.insert_message(_mock_name, text)
    return jsonify(_stringify_msg(_sanitise_msg(new_msg_row)))


#####################
# PUT: Edit message
#####################
# Requires form-data 'newMessage'
@app.route(URL_PREFIX+'/messages/<msg_id>', methods=['PUT'])
def replace_message(msg_id: int) -> typ_Response:
    new_text = request.form['newText']
    new_msg_row = db_stuff.edit_message(msg_id, new_text)
    return jsonify(_stringify_msg(_sanitise_msg(new_msg_row)))


#################################
# GET: All messages by one user
#################################
# NOT SANITISED
@app.route(URL_PREFIX+'/users/<usr_id>/messages', methods=['GET'])
def get_messages(usr_id: str) -> typ_Response:
    msg_rows = db_stuff.retrieve_messages_by_user(usr_id, limit=100)
    return jsonify(_stringify_msgs(_sanitise_msgs(msg_rows)))


##########################
# DELETE: Delete message
##########################
@app.route(URL_PREFIX+'/messages/<msg_id>', methods=['DELETE'])
def delete_messages(msg_id: int) -> typ_Response:
    id = int(msg_id)
    deleted_id = db_stuff.delete_message(id)[db_stuff.MSG_ID]
    return jsonify(id=deleted_id)

#########################
#       INTERNALS       #
#########################


# Note returned timestamp format, iso 8601
def _datetime_to_str(dt: datetime) -> str:
    return dt.isoformat(timespec='seconds')
    # dt.strftime('%d/%m/%Y')


# HTML-escape relevant strings
def _sanitise_msg(row: typ_msg_row) -> typ_msg_row:
    row[db_stuff.MSG_USERNAME] = \
        escape(row[db_stuff.MSG_USERNAME])
    row[db_stuff.MSG_TEXT_BODY] = \
        escape(row[db_stuff.MSG_TEXT_BODY])
    return row


def _sanitise_msgs(rows: typ_msg_rows) -> typ_msg_rows:
    return [_sanitise_msg(row) for row in rows]


# Turn datetimes into strings
def _stringify_msg(row: typ_msg_row) -> typ_msg_row:
    # Turn datetimes into str
    row[db_stuff.MSG_TIMESTAMP] = \
        _datetime_to_str(row[db_stuff.MSG_TIMESTAMP])
    row[db_stuff.MSG_UPDATED_TIMESTAMP] = \
        _datetime_to_str(row[db_stuff.MSG_UPDATED_TIMESTAMP])
    return row


def _stringify_msgs(rows: typ_msg_rows) -> typ_msg_rows:
    return [_stringify_msg(row) for row in rows]
