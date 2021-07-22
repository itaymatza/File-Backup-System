"""File Backup System - Client

The role of this module is to interface with the client -
Authenticate the client with the server,
gets command from the client and send request to the server,
receives response from the server and output status for the client.
"""
import socket
from Client.client_helper import MENU, get_server_ip_and_port, RequestMenu
from protocol import encode_request, decode_server_response, ULONG_MAX

CLIENT_VERSION = 1


if __name__ == '__main__':
    server_info_file = "server.info"
    server_ip, server_port = get_server_ip_and_port(server_info_file)
    proceed_to_another_request = True
    while proceed_to_another_request:
        option = int(input(MENU))

        if option == RequestMenu.BACKUP.value:
            pass
        elif option == RequestMenu.RECOVER.value:
            pass
        elif option == RequestMenu.GETLIST.value:
            pass
        elif option == RequestMenu.DELETION.value:
            pass
        elif option == RequestMenu.EXIT.value:
            print("Bye Bye.")
            proceed_to_another_request = False
        else:
            print("Illegal option, please try again.")




    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((server_ip, server_port))  # connect to given server

            # request backed up files list from server
            list_request = encode_request(uid, CLIENT_VERSION,
                                          'GETLIST_REQUEST')
            sock.sendall(list_request)
            file_name, file = decode_server_response(sock, uid)
            if file:
                print("Received file list - " + file_name.decode(
                    "utf-8") + '.')
                print(file)
            else:
                print("Error: Unable to get files list from server.")

            # request server to backup the 1st file
            file_backup_request = encode_request(uid, CLIENT_VERSION,
                                                 'BACKUP_REQUEST',
                                                 backup_files_list[0])
            sock.sendall(file_backup_request)
            file_name, succeeded = decode_server_response(sock, uid)
            if succeeded:
                print("Successfully backup file " + file_name.decode(
                    "utf-8") + '.')
            else:
                print("Unable to backup file - " + file_name.decode(
                    "utf-8") + '.')

            # request server to backup the 2nd file
            file_backup_request = encode_request(uid, CLIENT_VERSION,
                                                 'BACKUP_REQUEST',
                                                 backup_files_list[1])
            sock.sendall(file_backup_request)
            file_name, succeeded = decode_server_response(sock, uid)
            if succeeded:
                print("Successfully backup file " + file_name.decode(
                    "utf-8") + '.')
            else:
                print("Unable to backup file - " + file_name.decode(
                    "utf-8") + '.')

            # request backed up files list from server
            list_request = encode_request(uid, CLIENT_VERSION,
                                          'GETLIST_REQUEST')
            sock.sendall(list_request)
            file_name, file = decode_server_response(sock, uid)
            if file:
                print("Received files list - " + file_name.decode(
                    "utf-8") + '.')
                print(file)
            else:
                print("Error: Unable go get files list from server.")

            # request server to recover the 1st file
            file_recover_request = encode_request(uid, CLIENT_VERSION,
                                                  'RECOVER_REQUEST',
                                                  backup_files_list[0])
            sock.sendall(file_recover_request)
            file_name, file = decode_server_response(sock, uid)
            if file:
                print("Recovered file - " + file_name.decode(
                    "utf-8") + '.')
            else:
                print("File " + file_name.decode("utf-8") +
                      ' is not exists in the server.')

            # request server delete the 1st file
            file_delete_request = encode_request(uid, CLIENT_VERSION,
                                                 'DELETION_REQUEST',
                                                 backup_files_list[0])
            sock.sendall(file_delete_request)
            file_name, succeeded = decode_server_response(sock, uid)
            if succeeded:
                print("Deletion succeed of file " + file_name.decode(
                    "utf-8") + '.')
            else:
                print("Unable to delete file - " + file_name.decode(
                    "utf-8") + '.')

            # request server to recover the 1st file
            file_recover_request = encode_request(uid, CLIENT_VERSION,
                                                  'RECOVER_REQUEST',
                                                  backup_files_list[0])
            sock.sendall(file_recover_request)
            file_name, file = decode_server_response(sock, uid)
            if file:
                print("Recovered file - " + file_name.decode(
                    "utf-8") + '.')
            else:
                print("File " + file_name.decode("utf-8") +
                      ' is not exists in the server.')

    except OSError as exception:
        print("Error: Failed to connect to the server - %s." % exception)
        exit(-1)
    except Exception as exception:
        print("Error: %s." % exception)
        exit(-1)
