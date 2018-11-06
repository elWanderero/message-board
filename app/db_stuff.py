import os
import typing
import psycopg2
import psycopg2.extras
from sys import stdout
# from datetime import datetime
# from mypy_extensions import TypedDict

#####################################################
#                    CONSTANTS                      #
#####################################################

# Database constants
####################
DATABASE_URL = os.environ['DATABASE_URL']
MSG_TABLE = 'message'
MSG_USERNAME = 'createdby'
MSG_TEXT_BODY = 'text'
MSG_TIMESTAMP = 'created'
MSG_UPDATED_TIMESTAMP = 'updated'
MSG_ID = 'id'


# Types
####################

# Currently (mypy 0.641) not working with variables instead of
# hardcoded field names, i.e. MSG_ID instead of 'id'. We do not
# want hard-coded field names all over, so we skip this solution
# until we can find a way to solve it.
# typ_msg_row = TypedDict('typ_msg_row', {
#     'id': int,
#     'created': datetime,
#     'createdby': str,
#     'text': str,
#     'updated': datetime
# })

typ_msg_row = dict
typ_msg_rows = typing.List[typ_msg_row]

# Using union because the bare class raises an error in
# mypy when referenced throush a variable. Probably a bug.
typ_cursor = typing.Union[psycopg2.extras.RealDictCursor]
# typ_cursor = typing.Union[psycopg2.extras.RealDictCursor,
#                           psycopg2.extensions.cursor]


#####################################################
#                       API                         #
#####################################################


def insert_message(username: str, text: str) -> typ_msg_row:
    """Create and insert a new message into the database.

    Returns:
        The newly created message, as a dict
    """
    query = "INSERT INTO {} ({}, {}) VALUES (%s, %s) RETURNING *"
    query = query.format(MSG_TABLE, MSG_USERNAME, MSG_TEXT_BODY)
    created_msg = _oneoff_query_and_commit(query, [username, text])[0]
    return created_msg


def edit_message(msg_id: int, new_text: str) -> typ_msg_row:
    """Edit an existing message in the database.

    Returns:
        The newly edited message, as a dict
    """
    query = "UPDATE {} SET {}=CURRENT_TIMESTAMP, {}=%s WHERE {}=%s RETURNING *"
    query = query.format(MSG_TABLE,
                         MSG_UPDATED_TIMESTAMP, MSG_TEXT_BODY,
                         MSG_ID)
    edited_msg = _oneoff_query_and_commit(query, [new_text, msg_id])[0]
    return edited_msg


def retrieve_messages_by_user(usr_id: str, limit=100) -> typ_msg_rows:
    """Retrieve all messages by a given user in the database.

    Params:
        usr_id: ID of desired user
        limit: Max number of messages to retrieve. 0 means no limit.
    Returns:
        The newly edited message, as a dict
    """
    query = "SELECT * FROM {} WHERE {}=%s {}"
    query_lim = "" if limit == 0 else "LIMIT {}".format(limit)
    query = query.format(MSG_TABLE, MSG_USERNAME, query_lim)
    msg_rows = _oneoff_query(query, [usr_id])
    return msg_rows


def delete_message(msg_id: int) -> typ_msg_row:
    """Deletes an existing message in the database.

    Returns:
        The deleted message, as a dict
    """
    query = "DELETE FROM {} WHERE {}=%s RETURNING *"
    query = query.format(MSG_TABLE, MSG_ID)
    msg_row = _oneoff_query_and_commit(query, [msg_id])[0]
    return msg_row


#####################################################
#                     Internals                     #
#####################################################

def _oneoff_query(query: str, params=None) -> typ_msg_rows:
    cur = _new_dict_cursor()
    rows = _query(cur, query, params)
    cur.connection.close()
    return rows


def _oneoff_query_and_commit(query: str, params=None) -> typ_msg_rows:
    cur = _new_dict_cursor()
    rows = _query(cur, query, params)
    _kill_and_commit_cursor(cur)
    return rows


def _new_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


def _new_dict_cursor() -> typ_cursor:
    db_connection = _new_db_connection()
    return db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def _kill_and_commit_cursor(cur: psycopg2.extras.RealDictCursor) -> None:
    cur.connection.commit()
    cur.connection.close()


def _query(cur: typ_cursor, query: str, params: list) -> typing.List[dict]:
    cur.execute(query, params)
    return cur.fetchall()


#######################################################
#  Mocking and Testing
#######################################################

_mock_name = "test_usr_3"


def clear_all_messages(username: str):
    query = "DELETE FROM {} WHERE {}=%s"
    query = query.format(MSG_TABLE, MSG_USERNAME)
    cur = _new_dict_cursor()
    cur.execute(query, [username])
    _kill_and_commit_cursor(cur)


def _debug(obj):
    print(obj)
    stdout.flush()
