import os
import psycopg2
from psycopg2.extras import RealDictCursor
from sys import stdout
from typing import List
from datetime import datetime

# from mypy_extensions import TypedDict

#####################################################
#                    CONSTANTS                      #
#####################################################

# Database constants
####################
DATABASE_URL = os.environ["DATABASE_URL"]

USR_TABLE = '"user"'
USR_NAME = "name"
USR_ID = "id"
USR_PUBLIC_KEY = "public_key"
USR = {
    "TABLE": USR_TABLE,
    "NAME": USR_NAME,
    "ID": USR_ID,
    "PUBLIC_KEY": USR_PUBLIC_KEY,
}

MSG_TABLE = "message"
MSG_AUTHOR = "createdby"
MSG_AUTHOR_ID = "createdby"
MSG_TEXT = "text"
MSG_TIMESTAMP = "created"
MSG_UPDATED_TIMESTAMP = "updated"
MSG_ID = "id"
MSG = {
    "TABLE": MSG_TABLE,
    "AUTHOR": MSG_AUTHOR,
    "AUTHOR_ID": MSG_AUTHOR_ID,
    "TEXT": MSG_TEXT,
    "TIMESTAMP": MSG_TIMESTAMP,
    "UPDATED_TIMESTAMP": MSG_UPDATED_TIMESTAMP,
    "ID": MSG_ID,
}


# Types
####################


class Msg:
    def __init__(
        self, id: int, created: datetime, author: str, text: str, updated: datetime
    ):
        self.id = id
        self.created = created
        self.author = author
        self.text = text
        self.updated = updated


# Msg_row = TypedDict(
#     "Msg_row",
#     {
#         "id": int,
#         "created": datetime,
#         "createdby": str,
#         "text": str,
#         "updated": datetime,
#     },
# )

# typ_msg = dict
# typ_msgs = List[typ_msg]

# Using union because the bare class raises an error in
# mypy when referenced throush a variable. Probably a bug.
# typ_cursor = Union[psycopg2.extras.RealDictCursor]
# typ_cursor = typing.Union[psycopg2.extras.RealDictCursor,
#                           psycopg2.extensions.cursor]


#####################################################
#                       API                         #
#####################################################


def insert_message(username: str, text: str) -> Msg:
    """Create and insert a new message into the database.

    Returns:
        The newly created message, as a dict
    """
    # query = "INSERT INTO {} ({}, {}) VALUES (%s, %s) RETURNING *"
    # query = query.format(MSG_TABLE, MSG_AUTHOR, MSG_TEXT)
    query = "INSERT INTO {TABLE} ({AUTHOR_ID}, {TEXT}) (SELECT {{ID}}, %s FROM {{TABLE}} WHERE {{NAME}} = %s) RETURNING {ID}, {TIMESTAMP}, {TEXT}, {UPDATED_TIMESTAMP}, %s AS {{NAME}}"
    query = query.format(**MSG).format(**USR)
    created_msg = _oneoff_query(query, [text, username, username], True)[0]
    return _db_msg_row_to_msg(created_msg)


def edit_message(msg_id: int, new_text: str) -> Msg:
    """Edit an existing message in the database.

    Returns:
        The newly edited message, as a dict
    """
    query = "UPDATE {} SET {}=CURRENT_TIMESTAMP, {}=%s WHERE {}=%s RETURNING *"
    query = query.format(MSG_TABLE, MSG_UPDATED_TIMESTAMP, MSG_TEXT, MSG_ID)
    edited_msg = _oneoff_query(query, [new_text, msg_id], True)[0]
    return _db_msg_row_to_msg(edited_msg)


def retrieve_messages_by_user(usr_id: str, limit=100) -> List[Msg]:
    """Retrieve all messages by a given user in the database.

    Params:
        usr_id: ID of desired user
        limit: Max number of messages to retrieve. 0 means no limit.
    Returns:
        The newly edited message, as a dict
    """
    query = "SELECT * FROM {} WHERE {}=%s {}"
    query_lim = "" if limit == 0 else "LIMIT {}".format(limit)
    query = query.format(MSG_TABLE, MSG_AUTHOR, query_lim)
    msg_rows = _oneoff_query(query, [usr_id])
    return _db_msg_rows_to_msgs(msg_rows)


def delete_message(msg_id: int) -> Msg:
    """Deletes an existing message in the database.

    Returns:
        The deleted message, as a dict
    """
    query = "DELETE FROM {} WHERE {}=%s RETURNING *"
    query = query.format(MSG_TABLE, MSG_ID)
    msg_row = _oneoff_query(query, [msg_id], True)[0]
    return _db_msg_row_to_msg(msg_row)


def get_user_public_key(username: str) -> bytes:
    query = "SELECT {} FROM {} WHERE {}=%s"
    query = query.format(USR_PUBLIC_KEY, USR_TABLE, USR_NAME)
    public_key_row = _oneoff_query(query, [username])[0]
    public_key: bytes = public_key_row[USR_PUBLIC_KEY]
    return public_key


#####################################################
#                     Internals                     #
#####################################################


def _db_msg_row_to_msg(msg_row: dict) -> Msg:
    a = msg_row[MSG_ID]
    b = msg_row[MSG_TIMESTAMP]
    c = msg_row[USR_NAME]
    d = msg_row[MSG_TEXT]
    e = msg_row[MSG_UPDATED_TIMESTAMP]
    return Msg(a, b, c, d, e)


def _db_msg_rows_to_msgs(msg_rows: List[dict]) -> List[Msg]:
    return [_db_msg_row_to_msg(row) for row in msg_rows]


def _oneoff_query(query: str, params=None, commit=False) -> List[dict]:
    cur = _new_dict_cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    if commit:
        cur.connection.commit()
    cur.connection.close()
    return rows


def _new_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def _new_dict_cursor() -> RealDictCursor:
    db_connection = _new_db_connection()
    return db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


#######################################################
#  Mocking and Testing
#######################################################

_mock_name = "test_usr_3"


def _get_n_msgs(n: int) -> List[Msg]:
    query = "SELECT * FROM {} LIMIT {}"
    query = query.format(MSG_TABLE, n)
    msg_rows = _oneoff_query(query)
    return _db_msg_rows_to_msgs(msg_rows)


def clear_all_messages(username: str) -> None:
    query = "DELETE FROM {} WHERE {}=%s"
    query = query.format(MSG_TABLE, MSG_AUTHOR)
    cur = _new_dict_cursor()
    cur.execute(query, [username])
    cur.connection.commit()
    cur.connection.close()


def _debug(obj):
    print(obj)
    stdout.flush()
