import socket
from random import randrange
from protocol import encode_request, decode_server_response, ULONG_MAX

CLIENT_VERSION = 1


def pars_info_files():
    try:
        with open('server.info') as server:
            if len(server.readlines()) > 1:
                print('Error: server.info file should be in format '
                      '"server:port".')
                exit(-1)
            server.seek(0)
            read_data = server.read()
            ip_info, port_info = read_data.strip().split(':')
            if len(port_info.split()) != 1 or not 0 < int(port_info) < 65536:
                print('Error: Invalid port number.')
    except IOError:
        print("Error: server.info file is not accessible.")
        exit(-1)

    try:
        with open('backup.info') as backup:
            backup_files_info = backup.read().splitlines()
            if len(backup_files_info) < 1:
                raise Exception("Error: Cannot send file the the server - "
                                "the file backup.info is empty.")
            if len(backup_files_info) < 2:
                raise Exception("Error: Cannot send file the the server - "
                                "the file backup.info have just one file.")
    except IOError:
        print("Error: backup.info file is not accessible.")
        exit(-1)
    except Exception as e:
        print("Error: %s." % e)
        exit(-1)
    return ip_info, int(port_info), backup_files_info


if __name__ == '__main__':
    uid = randrange(1, ULONG_MAX)
    server_ip, server_port, backup_files_list = pars_info_files()

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
