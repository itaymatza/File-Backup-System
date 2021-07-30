"""Client-Server program which will facilitate a client to register itself to the server.
A server should keep a table of user-hash(password) entry for each user.

This program registers user with username, password and stores password hash in dictionary.
Also, when a user tries to login , password validation occurs.
"""

import uuid
import hashlib

USERNAME_LEN = 256
PASSWORD_LEN = 2048


# Returns false if connection denied and true otherwise.
def authenticate_client(connection, db, lock):
    name = connection.recv(USERNAME_LEN)
    name = name.decode()
    password = connection.recv(PASSWORD_LEN)
    password = password.decode()
    password = hashlib.sha256(str.encode(password)).hexdigest()  # Password hash using SHA256

    # REGISTRATION PHASE
    # If new user,  register in database
    if not db.is_client_name_exists(name):
        uid = uuid.uuid4()
        lock.acquire()
        db.insert_new_client_to_the_table(uid, name, password)
        lock.release()
        connection.send(str.encode('Registration Successful'))
        print('Registered : ', name)

    # If user already existing user, check if the entered password is correct
    else:
        uid = db.get_client_uid(name)
        if db.pull_password(uid) == password:
            connection.send(str.encode('Connection Successful'))  # Response Code for Connected Client
            print('Connected: ', name)
        else:
            connection.send(str.encode('Login Failed'))  # Response code for login failed
            print('Connection denied: ', name)
            return False, None
    return True, uid
