import os
import binascii

# Generate a random 32-byte string
jwt_secret_key = binascii.hexlify(os.urandom(32)).decode()

print(jwt_secret_key)

