""" Server helper - functions related to server management"""


# Reads port number from ./port.info file.
def get_tcp_port(file):
    try:
        with open(file) as portfile:
            read_data = portfile.read().strip().split()
            if len(read_data) > 1:
                raise Exception('Error: port.info file should contain just port number.')
            port_info = int(read_data[0])
            if not 0 < port_info < 65536:
                raise ValueError
    except IOError:
        raise IOError("Error: server.info file is not accessible.")
    except ValueError:
        raise ValueError("Error: Invalid port number.") from None
    return port_info
