"""File Backup System - Client

The role of this module is to interface with the client -
Authenticate the client with the server,
gets command from the client and send request to the server,
receives response from the server and output status for the client.
"""
import socket
import ssl

from Client.authentication import authenticate_user
from Client.client_helper import MENU, get_server_ip_and_port, RequestMenu
from protocol import encode_request, decode_server_response

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
        uid = authenticate_user(sock)

        proceed_to_another_request = True
        while proceed_to_another_request:
            try:  # Gets input from user
                option = int(input(MENU))
            except Exception as exception:
                print(exception)
                continue

            # Backup file request
            if option == RequestMenu.BACKUP.value:
                file_to_backup = input("Please enter the path for the file to backup: ")
                try:
                    file_backup_request = encode_request(CLIENT_VERSION, 'BACKUP_REQUEST', file_to_backup)
                except IOError as exception:
                    print(exception)
                    continue
                sock.sendall(file_backup_request)
                file_name, is_succeeded_status = decode_server_response(sock, uid)
                if is_succeeded_status:
                    print("Successfully backup file " + file_name.decode("utf-8") + '.')
                else:
                    print("Unable to backup file - " + file_name.decode("utf-8") + '.')

            # Recover file request
            elif option == RequestMenu.RECOVER.value:
                file_to_recover = input("Please enter file name to recover: ")
                file_recover_request = encode_request(CLIENT_VERSION, 'RECOVER_REQUEST', file_to_recover)
                sock.sendall(file_recover_request)
                file_name, is_succeeded_status = decode_server_response(sock, uid)
                if is_succeeded_status:
                    print("Recovered file - " + file_name.decode("utf-8") + '.')
                else:
                    print("File " + file_name.decode("utf-8") + ' is not exists in the server.')

            # Get files list request
            elif option == RequestMenu.GETLIST.value:
                list_request = encode_request(CLIENT_VERSION, 'GETLIST_REQUEST')
                sock.sendall(list_request)
                files_list, is_succeeded_status = decode_server_response(sock, uid)
                if is_succeeded_status:
                    print("Received files list for " + uid + ':')
                    print(files_list.decode("utf-8"))
                else:
                    print("Error: Unable to get files list from server.")

            # Delete file from server request
            elif option == RequestMenu.DELETION.value:
                file_to_delete = input("Please enter file name to delete from the server: ")
                file_delete_request = encode_request(CLIENT_VERSION, 'DELETION_REQUEST', file_to_delete)
                sock.sendall(file_delete_request)
                file_name, is_succeeded_status = decode_server_response(sock, uid)
                if is_succeeded_status:
                    print("Deletion succeed of file " + file_name.decode("utf-8") + '.')
                else:
                    print("Unable to delete file - " + file_name.decode("utf-8") + '.')

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
