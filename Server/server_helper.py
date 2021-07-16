""" Server helper - functions related to server management"""


# Reads port number from ./port.info file.
def get_tcp_port(file):
    try:
        with open(file) as port_file:
            data = port_file.read().strip().split()
            if len(data) > 1:
                raise Exception('Error: port.info file should contain just port number.')
            port_info = int(data[0])
            if not 0 < port_info < 65536:
                raise ValueError
    except IOError:
        raise IOError("Error: port.info file is not accessible.")
    except ValueError:
        raise ValueError("Error: Invalid port number.") from None
    return port_info
