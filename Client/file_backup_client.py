"""File Backup System - Client

The role of this module is to interface with the client -
Authenticate the client with the server,
gets command from the client and send request to the server,
receives response from the server and output status for the client.
"""
import os
import socket
import ssl

from authentication import authenticate_client
from client_helper import MENU, get_server_ip_and_port, RequestMenu
from encryption import load_key, AESenc
from protocol import encode_request, decode_server_response

CLIENT_VERSION = 1

if __name__ == '__main__':
    SERVER_INFO_FILE = "server.info"
    SERVER_IP, SERVER_PORT = get_server_ip_and_port(SERVER_INFO_FILE)
    CLIENT_KEY_SNI_HOSTNAME = 'backupserver.com'
    SERVER_CERT = 'server.crt'
    CLIENT_CERT = 'client.crt'
    CLIENT_KEY = 'client.key'

    # Configuration for SSL
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=SERVER_CERT)
    context.load_cert_chain(certfile=CLIENT_CERT, keyfile=CLIENT_KEY)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock = context.wrap_socket(s, server_side=False, server_hostname=CLIENT_KEY_SNI_HOSTNAME)
        sock.connect((SERVER_IP, SERVER_PORT))  # connect to backup server
        uname = authenticate_client(sock)
        key = load_key(uname)
        enc = AESenc(key)

        proceed_to_another_request = True
        while proceed_to_another_request:
            try:
                # Gets input from user
                option = int(input(MENU))
            except Exception as exception:
                print(exception)
                continue

            # Backup file request
            if option == RequestMenu.BACKUP.value:
                file_to_backup = input("Please enter the path for the file to backup: ")
                try:
                    file_backup_request = encode_request(CLIENT_VERSION, 'BACKUP_REQUEST', file_to_backup, enc)
                except Exception as exception:
                    print(exception)
                    continue
                sock.sendall(file_backup_request)
                file_name, is_succeeded_status = decode_server_response(sock, uname)
                if is_succeeded_status:
                    print("Successfully backup file " + file_name.decode("utf-8") + '.')
                else:
                    print("Unable to backup file - " + file_name.decode("utf-8") + '.')

            # Recover file request
            elif option == RequestMenu.RECOVER.value:
                file_to_recover = input("Please enter file name to recover: ")
                file_recover_request = encode_request(CLIENT_VERSION, 'RECOVER_REQUEST', file_to_recover)
                sock.sendall(file_recover_request)
                file_name, is_succeeded_status = decode_server_response(sock, uname, enc)
                if is_succeeded_status:
                    print("Recovered file - " + file_name.decode("utf-8") + '.')
                else:
                    print("Unable to get file '" + file_name.decode("utf-8") + "' from the server.")

            # Get files list request
            elif option == RequestMenu.GETLIST.value:
                list_request = encode_request(CLIENT_VERSION, 'GETLIST_REQUEST')
                sock.sendall(list_request)
                files_list, is_succeeded_status = decode_server_response(sock, uname)
                if is_succeeded_status:
                    print("Received files list for " + uname + ':')
                    print(files_list.decode("utf-8"))
                else:
                    print("Unable to get files list from the server.")

            # Delete file from server request
            elif option == RequestMenu.DELETION.value:
                file_to_delete = input("Please enter file name to delete from the server: ")
                file_delete_request = encode_request(CLIENT_VERSION, 'DELETION_REQUEST', file_to_delete)
                sock.sendall(file_delete_request)
                file_name, is_succeeded_status = decode_server_response(sock, uname)
                if is_succeeded_status:
                    print("Deletion succeed of file '" + file_name.decode("utf-8") + "'.")
                else:
                    print("Unable to delete file '" + file_name.decode("utf-8") + "'.")

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
