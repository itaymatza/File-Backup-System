"""File Backup System - Server

The role of this module is to manage the list of users registered to
the service and allow them to backup and restore files.

"""
import socket
import ssl
import protocol
import threading
import database
import server_helper
from authentication import authenticate_user

SERVER_VERSION = 1
VERSION_LENGTH = 1


def request_handler(conn, uid, lock, db):
    request = protocol.Request()
    response = protocol.Response(SERVER_VERSION)

    while True:
        try:
            version = conn.recv(VERSION_LENGTH)
            if not version:
                print('Connection closed by client.')
                break
        except Exception as connection_exception:
            print('Connection closed by client: %s' % connection_exception)
            break

        code = protocol.recv_and_decode_client_request(conn, db, request, version)

        if code == protocol.ResponseCode.GENERAL_ERROR.value:
            response.set_general_error()

        # Backup file request
        elif code == protocol.RequestCode.BACKUP_REQUEST.value:
            lock.acquire()
            db.add_file(uid, request.header.filename, request.payload.payload)
            lock.release()
            response.set_backup(request.header.filename)

        # Recover file request
        elif code == protocol.RequestCode.RECOVER_REQUEST.value:
            if db.is_file_exists(uid, request.header.filename):
                file = db.pull_file(uid, request.header.filename)
                response.set_recover(request.header.filename, file)
            else:
                response.set_unknown_file_error(request.header.filename)

        # Get files list request
        elif code == protocol.RequestCode.GETLIST_REQUEST.value:
            files_list = db.get_files_list(uid)
            response.set_files_list(files_list)

        # Delete request
        elif code == protocol.RequestCode.DELETION_REQUEST.value:
            if db.is_file_exists(uid, request.header.filename):
                lock.acquire()
                db.delete_file(uid, request.header.filename)
                lock.release()
                response.set_as_delete(request.header.filename)
            else:
                response.set_unknown_file_error(request.header.filename)

        encoded_response = protocol.encode_server_response(response)
        conn.sendall(encoded_response)


if __name__ == '__main__':
    TCP_IP = ''
    PORT_FILE = 'port.info'
    TCP_PORT = server_helper.get_tcp_port(PORT_FILE)
    server_cert = 'server.crt'
    server_key = 'server.key'
    client_certs = 'client.crt'
    DB = database.DataBase()

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(certfile=server_cert, keyfile=server_key)
    context.load_verify_locations(cafile=client_certs)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((TCP_IP, TCP_PORT))
            sock.listen(100)
            thread_lock = threading.Lock()
            while True:
                sock_conn, address_and_port = sock.accept()
                print("Client connected: {}:{}".format(address_and_port[0], address_and_port[1]))
                connection = context.wrap_socket(sock_conn, server_side=True)
                print("SSL established. Peer: {}".format(connection.getpeercert()))
                is_authenticated, uid = authenticate_user(connection, DB, thread_lock)
                if is_authenticated:
                    # client_thread = threading.Thread(target=request_handler, args=(connection, uid, thread_lock, DB))
                    # client_thread.start()
                    request_handler(connection, uid, thread_lock, DB)
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
    except Exception as error:
        print('Error: %s' % error)
