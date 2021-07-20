""" Client helper - functions related to client management"""


# Reads server's ip address and port number from file.
def get_server_ip_and_port(server_info_file):
    try:
        with open(server_info_file) as server:
            if len(server.readlines()) > 1:
                print('Error: ' + server_info_file + ' file should be in format "server:port".')
                exit(-1)
            server.seek(0)
            read_data = server.read()
            ip_info, port_info = read_data.strip().split(':')
            if len(port_info.split()) != 1 or not 0 < int(port_info) < 65536:
                print('Error: Invalid port number.')
    except IOError:
        print('Error: ' + server_info_file + ' file is not accessible.')
        exit(-1)
    return ip_info, int(port_info)
