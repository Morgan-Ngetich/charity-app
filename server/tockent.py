# import os
# import binascii

# # Generate a random 32-byte string
# jwt_secret_key = binascii.hexlify(os.urandom(32)).decode()

# print(jwt_secret_key)

from sqlalchemy import text

# Assuming you have already imported and set up SQLAlchemy engine and session

# Execute the SQL command to remove the NOT NULL constraint from the "status" column
alter_query = text("ALTER TABLE charities ALTER COLUMN status DROP NOT NULL")
session.execute(alter_query)
session.commit()

