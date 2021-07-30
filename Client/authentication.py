from encryption import write_key

USERNAME_LEN = 256


def authenticate_client(sock):
    name = ''
    is_valid_name = False

    while not is_valid_name:
        name = input('ENTER USERNAME: ')
        if 0 < len(name) <= USERNAME_LEN:
            is_valid_name = True
        else:
            print('Illegal name length.')

    sock.send(str.encode(name))
    password = input('ENTER PASSWORD: ')
    sock.send(str.encode(password))
    ''' Response : Status of Connection :
    	1 : Registeration successful 
    	2 : Connection Successful
    	3 : Login Failed
    '''
    # Receive response
    response = sock.recv(2048)
    response = response.decode()

    if response == 'Login Failed':
        pass
    if response == 'Registration Successful':
        write_key(name)
    return name, response
