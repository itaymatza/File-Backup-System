"""Client-Server program which will facilitate a client to register itself to the server.
A server should keep a table of user-hash(password) entry for each user.

This program registers user with username, password and stores password hash in dictionary.
Also, when a user tries to login , password validation occurs.
"""

import uuid
import hashlib

USERNAME_LEN = 256
PASSWORD_LEN = 2048


def authenticate_client(connection, db, lock):
    is_client_authenticated = False
    uid = ''
    authentications_attempted = 0
    number_of_attempts = 3

    while authentications_attempted < number_of_attempts:
        authentications_attempted += 1
        is_client_authenticated, uid = _authenticate_client(connection, db, lock)
        if is_client_authenticated:
            break
        if authentications_attempted == number_of_attempts:
            print('Client failed to authenticate 3 times.')
    return is_client_authenticated, uid


# Returns false if connection denied and true otherwise.
def _authenticate_client(connection, db, lock):
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
