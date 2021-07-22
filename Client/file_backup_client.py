"""File Backup System - Client

The role of this module is to interface with the client -
Authenticate the client with the server,
gets command from the client and send request to the server,
receives response from the server and output status for the client.
"""
import socket
import ssl

from Client.authentication import authenticate
from Client.client_helper import MENU, get_server_ip_and_port, RequestMenu
from protocol import encode_request, decode_server_response, ULONG_MAX

CLIENT_VERSION = 1

if __name__ == '__main__':
    server_info_file = "server.info"
    server_ip, server_port = get_server_ip_and_port(server_info_file)
    server_sni_hostname = 'backupserver.com'
    server_cert = 'server.crt'
    client_cert = 'client.crt'
    client_key = 'client.key'

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
    context.load_cert_chain(certfile=client_cert, keyfile=client_key)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock = context.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)
        sock.connect((server_ip, server_port))  # connect to backupserver
        print("SSL established. Peer: {}".format(sock.getpeercert()))
        uid = authenticate(sock)

        proceed_to_another_request = True
        while proceed_to_another_request:
            option = int(input(MENU))

            if option == RequestMenu.BACKUP.value:
                pass

            elif option == RequestMenu.RECOVER.value:
                pass

            # Get files list request
            elif option == RequestMenu.GETLIST.value:
                list_request = encode_request(uid, CLIENT_VERSION, 'GETLIST_REQUEST')
                sock.sendall(list_request)
                files_list, success = decode_server_response(sock, uid)
                if success:
                    print("Received files list for" + uid + ':')
                    print(files_list)
                else:
                    print("Error: Unable to get files list from server.")

            elif option == RequestMenu.DELETION.value:
                pass

            elif option == RequestMenu.EXIT.value:
                print("Bye Bye.")
                proceed_to_another_request = False

            else:
                print("Illegal option, please try again.")

        print("Closing connection")
        sock.close()
    except OSError as exception:
        print("Error: Failed to connect to the server - %s." % exception)
        exit(-1)
    except Exception as exception:
        print("Error: %s." % exception)
        exit(-1)
