def authenticate(sock):
    name = input('ENTER USERNAME : ')
    sock.send(str.encode(name))
    password = input('ENTER PASSWORD : ')
    sock.send(str.encode(password))
    ''' Response : Status of Connection :
    	1 : Registeration successful 
    	2 : Connection Successful
    	3 : Login Failed
    '''
    # Receive response
    response = sock.recv(2048)
    response = response.decode()

    print(response)
    if response == 'Login Failed':
        raise Exception(response)
    return name
