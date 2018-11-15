# A tiny tool to generate secp256r1 (NIST P-256) elliptic curve
# private/public key pairs. Keys are in PEM format (----BEGIN
# BLA BLA---- etc, key in ASCII base64 you've seen it before.)
#
# Will overwrite previous files with the given filenames.

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
)
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec  # Elliptic cryptography

#####################################
#              CONFIG               #
#####################################

PRIVATE_KEY_FILENAME = "id_ecc.priv"
PUBLIC_KEY_FILENAME = "id_ecc.pub"

# Could also use serialization.BestAvailableEncryption(psw_for_key)
# if we wanted to actually encrypt key. IF USED IN PRODUCTION PRIVATE
# KEY SHOULD BE STORED ENCRYPTED.
PRIVATE_KEY_ENCRYPTION_ALG = NoEncryption()

# PEM, in short, says that the key should be stored as
# ----BEGIN <stuff>----
# <more stuff>
# key in base64 ASCII
# -----END <stuff>----
# There is more detail to it, but that's the gist.
KEY_ENCODING = Encoding.PEM

# The formats decide what exactly goes in the <stuff> parts above.
# At least in this context, I'm pretty sure there is a LOT more
# detail to it. PKCS and PEM do not even seem to have a subset
# relation to each other in general. But sometimes they can be made
# compatible, and that is the case here.
#
# PKCS8 for private and SubjectPublicKeyInfo for public were
# recommended in the cryptography docs, so I just chose them.
PRIVATE_KEY_FORMAT = PrivateFormat.PKCS8
PUBLIC_KEY_FORMAT = PublicFormat.SubjectPublicKeyInfo

# Choose your elliptic curve! I'm not even gonna talk about this. If
# you know stuff and care, there is a list of available curves here:
# cryptography.io/en/latest/hazmat/primitives/asymmetric/ec/
# (2018-11-15)
CURVE = ec.SECP256K1

#####################################
#           KEY GENERATION          #
#####################################

priv_key_obj = ec.generate_private_key(ec.SECP256R1(), default_backend())
private_key: bytes = priv_key_obj.private_bytes(
    KEY_ENCODING, PRIVATE_KEY_FORMAT, PRIVATE_KEY_ENCRYPTION_ALG
)
public_key: bytes = priv_key_obj.public_key().public_bytes(
    KEY_ENCODING, PUBLIC_KEY_FORMAT
)

# print("Private key length: ", len(private_key))
# print(private_key)
print(private_key.decode("utf-8"))
# print("Public key length: ", len(public_key))
# print(public_key)
print(public_key.decode("utf-8"))

file_for_private_key = open(PRIVATE_KEY_FILENAME, "wb")
file_for_private_key.write(private_key)
file_for_private_key.close()

file_for_public_key = open(PUBLIC_KEY_FILENAME, "wb")
file_for_public_key.write(public_key)
file_for_public_key.close()
