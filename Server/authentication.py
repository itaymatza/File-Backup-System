"""Client-Server program which will facilitate a client to register itself to the server.
A server should keep a table of user-hash(password) entry for each user.

This program registers user with username, password and stores password hash in dictionary.
Also, when a user tries to login , password validation occurs.
"""


import hashlib

USERNAME_LEN = 256
PASSWORD_LEN = 2048


# Returns false if connection denied and true otherwise.
def authenticate_user(connection, db):
    hashtable = {}

    name = connection.recv(USERNAME_LEN)
    name = name.decode()
    password = connection.recv(PASSWORD_LEN)
    password = password.decode()
    password = hashlib.sha256(str.encode(password)).hexdigest()  # Password hash using SHA256

    # REGISTRATION PHASE
    # If new user,  register in Hashtable Dictionary
    if name not in hashtable:
        hashtable[name] = password
        connection.send(str.encode('Registration Successful'))
        print('Registered : ', name)
        print("{:<8} {:<20}".format('USER', 'PASSWORD'))
        for k, v in hashtable.items():
            label, num = k, v
            print("{:<8} {:<20}".format(label, num))
        print("-------------------------------------------")

    # If user already existing user, check if the entered password is correct
    else:
        if hashtable[name] == password:
            connection.send(str.encode('Connection Successful'))  # Response Code for Connected Client
            print('Connected : ', name)
        else:
            connection.send(str.encode('Login Failed'))  # Response code for login failed
            print('Connection denied: ', name)
            return False
    return True
