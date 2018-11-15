# Just prints a UTF-8 file to stdout, really.
# Usage: python print_key.py <filename>

import sys

filename = sys.argv[1]
key_file = open(filename, "rb")
file_content: bytes = key_file.read()
print(file_content.decode("UTF-8"))
