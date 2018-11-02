# TEST VERSION USER INPUT NOT SANITIZED
# MOCKY MOCKIDY MOCK

import os
import sys
import psycopg2
import psycopg2.extras
from typing import List, Union
from datetime import datetime
from flask import Flask, jsonify, request

DATABASE_URL = os.environ['DATABASE_URL']
MSG_TABLE = 'message'
MSG_USERNAME = 'createdby'
MSG_TEXT_BODY = 'text'
MSG_TIMESTAMP = 'created'
MSG_UPDATED_TIMESTAMP = 'updated'
MSG_ID = 'id'


app = Flask(__name__)

cursor_types = Union[psycopg2.extras.RealDictCursor,
                     psycopg2.extensions.cursor]


##############################
# Simple testing API
##############################

# Simple test to see if we have contact
@app.route('/hello/')
def hello():
    return "hello"


# Test variable sending
@app.route('/hello/<x>')
def hello2(x):
    return "hello " + x


# Test databse connection
@app.route('/helloDB')
def hello_db():
    rows = _oneoff_query("SELECT * FROM message LIMIT 3")
    return _msg_rows_to_json(rows)


# Clear all messages belonging to _mock_user
@app.route('/clearMock')
def clear_mock():
    query = "DELETE FROM {} WHERE {}=%s"
    query = query.format(MSG_TABLE, MSG_USERNAME)
    cur = _new_dict_cursor()
    cur.execute(query, [_mock_name])
    cur.connection.commit()
    cur.connection.close()
    return "yes"


#######################################
#                 API                 #
#######################################

############################
# POST: Create new message
############################
# Requires form-data 'message'
# NOT SANITIZED
@app.route('/messages/', methods=['POST'])
def post_message():
    cur = _new_dict_cursor()
    msg_id = _insert_message(cur, _mock_name, request.form['text'])
    new_msg = _retrieve_message(cur, msg_id, datetime_to_string=True)
    cur.connection.commit()
    cur.connection.close()
    return jsonify(new_msg)


def _insert_message(cur: cursor_types, createdby: str, text: str) -> int:
    query = "INSERT INTO {} ({}, {}) VALUES (%s, %s) RETURNING id"
    query = query.format(MSG_TABLE, MSG_USERNAME, MSG_TEXT_BODY)
    return _query(cur, query, [createdby, text])[0]['id']


def _retrieve_message(cur: cursor_types,
                      msg_id: int,
                      datetime_to_string=False):
    query = "SELECT * FROM {} WHERE id=%s LIMIT 1"
    query = query.format(MSG_TABLE)
    msg_row = _query(cur, query, [msg_id])[0]
    if datetime_to_string:
        msg_row[MSG_TIMESTAMP] = _datetime_to_str(msg_row[MSG_TIMESTAMP])
    return msg_row


#####################
# PUT: Edit message
#####################
# Requires form-data 'newMessage'
# NOT SANITIZED
@app.route('/messages/<msg_id>', methods=['PUT'])
def replace_message(msg_id: int):
    new_text = request.form['newText']
    new_msg_row = _edit_message(msg_id, new_text, datetime_to_string=True)
    return jsonify(new_msg_row)


def _edit_message(msg_id: int, new_text: str, datetime_to_string=False):
    query = "UPDATE {} SET {}=CURRENT_TIMESTAMP, {}=%s WHERE {}=%s"
    query = query.format(MSG_TABLE,
                         MSG_UPDATED_TIMESTAMP, MSG_TEXT_BODY,
                         MSG_ID)
    cur = _new_dict_cursor()
    cur.execute(query, [new_text, msg_id])
    new_msg_row = _retrieve_message(cur, msg_id, datetime_to_string)
    cur.connection.commit()
    cur.connection.close()
    return new_msg_row


#################################
# GET: All messages by one user
#################################
# NOT SANITISED
@app.route('/users/<usr_id>/messages', methods=['GET'])
def get_messages(usr_id: str):
    return jsonify(_retrieve_messages_by_user(usr_id, datetime_to_string=True))


def _retrieve_messages_by_user(usr_id: str, datetime_to_string=False):
    query = "SELECT * FROM {} WHERE {}=%s LIMIT 100"
    query = query.format(MSG_TABLE, MSG_USERNAME)
    rows = _oneoff_query(query, [usr_id])
    if datetime_to_string:
        for row in rows:
            row[MSG_TIMESTAMP] = _datetime_to_str(row[MSG_TIMESTAMP])
    return rows


##########################
# DELETE: Delete message
##########################
# NOT SANITIZED
@app.route('/messages/<msg_id>', methods=['DELETE'])
def delete_messages(msg_id: int) -> str:
    id = int(msg_id)
    _delete_message(id)
    return jsonify(id=id)


def _delete_message(msg_id: int):
    query = "DELETE FROM {} WHERE {}=%s"
    query = query.format(MSG_TABLE, MSG_ID)
    cur = _new_dict_cursor()
    cur.execute(query, [msg_id])
    cur.commit()
    cur.close()

#########################
#       INTERNALS       #
#########################


def _debug(obj):
    print(obj)
    sys.stdout.flush()


def _new_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


def _new_dict_cursor():
    db_connection = _new_db_connection()
    return db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def _query(cur: cursor_types, query: str, params: List):
    cur.execute(query, params)
    return cur.fetchall()


def _oneoff_query(query: str, params=None):
    cur = _new_dict_cursor()
    rows = _query(cur, query, params)
    cur.connection.close()
    return rows


# 'statements' and 'listof_listof_params' better have the same lengths.
def _a_few_queries(queries: List[str], listlist_params: List[List]) -> List:
    zipped = zip(queries, listlist_params)
    cur = _new_dict_cursor()
    results = [_query(cur, pair[0], pair[1]) for pair in zipped]
    cur.connection.close()
    return results


# mock
_mock_name = "test_usr_3"
_mock_timestamp = datetime.utcnow().isoformat(timespec='seconds')


# Note returned timestamp format, iso 8601
def _datetime_to_str(dt: datetime) -> str:
    return dt.isoformat(timespec='seconds')
    # dt.strftime('%d/%m/%Y')


# Turns a datetime into a string, preserves everything else
def _maybe_datetime_to_str(maybe_dt):
    if type(maybe_dt) == datetime:
        return _datetime_to_str(maybe_dt)
    else:
        return maybe_dt


# Turns 'createdby'-datetimes into strings
# message row: {id: int, created: str, createdby: str, text: str}
def _msg_rows_to_json(rows):
    for row in rows:
        row[MSG_TIMESTAMP] = _datetime_to_str(row[MSG_TIMESTAMP])
    return jsonify(rows)

# db_conn = _new_db_connection()
# _db(str(type(db_conn.cursor())))
