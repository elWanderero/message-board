import os

# from sys import stdout
# from . import jwt_stuff
from . import db_stuff
from .db_stuff import Msg
from typing import List
from datetime import datetime
from flask.wrappers import Response
from flask import Flask, jsonify, request, escape


API_ID = "id"
API_TIMESTAMP = "created"
API_AUTHOR = "createdby"
API_TEXT = "text"
API_UPDATED_TIMESTAMP = "updated"


# mock
_mock_name = db_stuff._mock_name
# _mock_timestamp = datetime.utcnow().isoformat(timespec='seconds')


# TEMP SECURITY MEASURE! Put an URL_PREFIX in the environment
# to make stuff accesible only by putting '/URL_PREFIX' in front
# of all routes.
URL_PREFIX = os.getenv("URL_PREFIX")
if URL_PREFIX is None or URL_PREFIX == "":
    URL_PREFIX = ""
else:
    URL_PREFIX = "/" + URL_PREFIX

app = Flask(__name__)


##############################
# Simple testing API
##############################


# Simple test to see if we have contact
@app.route(URL_PREFIX + "/hello/")
def hello() -> str:
    return "hello"


# Test variable sending
@app.route(URL_PREFIX + "/hello/<x>")
def hello2(x) -> str:
    return "hello " + x


# Test databse connection
@app.route(URL_PREFIX + "/helloDB")
def hello_db() -> Response:
    msgs = db_stuff._get_n_msgs(3)
    return jsonify(_msgs_to_dicts(msgs, True, True))


# Clear all messages belonging to _mock_user
@app.route(URL_PREFIX + "/clearMock")
def clear_mock() -> str:
    db_stuff.clear_all_messages(_mock_name)
    return "yes"


@app.route(URL_PREFIX + "/test")
def test() -> str:
    return request.data


#######################################
#                 API                 #
#######################################

############################
# POST: Create new message
############################
# Requires form-data 'message'
@app.route(URL_PREFIX + "/messages/", methods=["POST"])
def post_message() -> Response:
    text = request.form["text"]
    new_msg = db_stuff.insert_message(_mock_name, text)
    return jsonify(_msg_to_dict(new_msg, True, True))


#####################
# PUT: Edit message
#####################
# Requires form-data 'newMessage'
@app.route(URL_PREFIX + "/messages/<msg_id>", methods=["PUT"])
def replace_message(msg_id: int) -> Response:
    new_text = request.form["newText"]
    new_msg = db_stuff.edit_message(msg_id, new_text)
    return jsonify(_msg_to_dict(new_msg, True, True))


#################################
# GET: All messages by one user
#################################
@app.route(URL_PREFIX + "/users/<usr_id>/messages", methods=["GET"])
def get_messages(usr_id: str) -> Response:
    msgs = db_stuff.retrieve_messages_by_user(usr_id, limit=100)
    return jsonify(_msgs_to_dicts(msgs, True, True))


##########################
# DELETE: Delete message
##########################
@app.route(URL_PREFIX + "/messages/<msg_id>", methods=["DELETE"])
def delete_messages(msg_id: int) -> Response:
    id = int(msg_id)
    deleted_id = db_stuff.delete_message(id).id
    return jsonify(id=deleted_id)


#########################
#       INTERNALS       #
#########################


def _msg_to_dict(msg: Msg, stringify: bool = False, clean: bool = False) -> dict:
    created = _dt_to_str(msg.created) if stringify else msg.created
    updated = _dt_to_str(msg.updated) if stringify else msg.updated
    text = escape(msg.text) if clean else msg.text
    author = escape(msg.author) if clean else msg.author
    return {
        API_ID: msg.id,
        API_TIMESTAMP: created,
        API_AUTHOR: author,
        API_TEXT: text,
        API_UPDATED_TIMESTAMP: updated,
    }


def _msgs_to_dicts(
    msgs: List[Msg], stringify: bool = False, clean: bool = False
) -> List[dict]:
    return [_msg_to_dict(msg, stringify, clean) for msg in msgs]


# Note returned timestamp format, iso 8601
def _dt_to_str(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")
    # dt.strftime('%d/%m/%Y')
