import jwt
from os import path
from typing import Mapping, Any

# ES256 = ECDSA using P-256 curve and SHA-256 hash
# TODO: Put this somewhere else, config or env maybe.
ALGORITHM = "ES256"

# DEVELOPMENT mocking stuff
PRIVK_FILENAME = "id_ecc.priv"
PUBK_FILENAME = "id_ecc.pub"
KEYS_DIR = "keys"


# Without verification, needed to get the username
# so that we can know which key to verify with.
def get_unverified_payload(jwt_blob: str) -> Mapping[str, Any]:
    return jwt.decode(jwt_blob, options={"verify_signature": False})


# TODO: Add verify function that checks iat (timestamp) and possbily more.


def encode(json_obj: dict, private_key: bytes):
    return jwt.encode(json_obj, private_key, ALGORITHM)


# Throws jwt.exceptions.InvalidSignatureError upon failed
# verification due to false signature.
def decode(jwt_blob: str, public_key: bytes):
    return jwt.decode(
        jwt_blob,
        public_key,
        options={"verify_signature": True},
        algorithms=ALGORITHM,
    )


# DEVELOPMEMT
def _make_keyfile_path(key_filename: str) -> str:
    dir_of_this_file = path.dirname(__file__)
    return path.join(dir_of_this_file, KEYS_DIR, key_filename)


# DEVELOPMEMT
def _read_key(key_filename: str) -> bytes:
    key_path = _make_keyfile_path(key_filename)
    key_file = open(key_path, "rb")
    key = key_file.read()
    key_file.close()
    return key


# DEVELOPMENT
# private_key = _read_key(PRIVK_FILENAME)
# public_key = _read_key(PUBK_FILENAME)


# jwt encode only supports JSON objects!!!
# payload = {"a": "b"}
# e: bytes = jwt.encode(payload, private_key, ALGORITHM)
# d = jwt.decode(e, public_key)

# print(type(e))
