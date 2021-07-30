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
from authentication import authenticate_client

SERVER_VERSION = 1
VERSION_LENGTH = 1


def requests_handler(conn, uid, lock, db):
    request = protocol.Request()
    response = protocol.Response(SERVER_VERSION)

    while True:
        try:
            version = conn.recv(VERSION_LENGTH)
            if not version:
                raise Exception('Connection closed by client.')
        except Exception as connection_exception:
            print('Socket connection closed: %s' % connection_exception)
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


def client_handler(conn, lock, db):
    authentications_attempted, number_of_attempts = 0, 3
    while authentications_attempted < number_of_attempts:
        authentications_attempted += 1
        is_client_authenticated, uid = authenticate_client(connection, DB, thread_lock)
        if is_client_authenticated:
            requests_handler(conn, uid, lock, db)
            break
        if authentications_attempted == number_of_attempts:
            print('Client failed to authenticate 3 times.')
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()


if __name__ == '__main__':
    TCP_IP = ''
    PORT_FILE = 'port.info'
    TCP_PORT = server_helper.get_tcp_port(PORT_FILE)
    SERVER_CERT = 'server.crt'
    SERVER_KEY = 'server.key'
    CLIENT_CERTS = 'client.crt'
    DB = database.DataBase()

    # Configuration for SSL
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)
    context.load_verify_locations(cafile=CLIENT_CERTS)

    try:
        # Socket connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((TCP_IP, TCP_PORT))
            sock.listen(100)
            thread_lock = threading.Lock()
            while True:
                sock_conn, address_and_port = sock.accept()
                print("Client connected: {}:{}".format(address_and_port[0], address_and_port[1]))
                connection = context.wrap_socket(sock_conn, server_side=True)
                print("SSL established. Peer: {}".format(connection.getpeercert()))

                client_thread = threading.Thread(target=client_handler, args=(connection, thread_lock, DB))
                client_thread.start()
    except Exception as error:
        print('Error: %s' % error)
