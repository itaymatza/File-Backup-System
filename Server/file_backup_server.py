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
from Server.authentication import authenticate_user

SERVER_VERSION = 1
UID_LEN = 16


def request_handler(conn, lock, db):
    request = protocol.Request()
    response = protocol.Response(SERVER_VERSION)

    while True:
        try:
            uid = conn.recv(UID_LEN)
            if not uid:
                print('Connection closed by client.')
                break
        except Exception as connection_exception:
            print('Connection closed by client: %s' % connection_exception)
            break

        code = protocol.recv_and_decode_client_request(conn, db, request, uid)

        if code == protocol.ResponseCode.GENERAL_ERROR.value:
            response.set_general_error()

        elif code == protocol.RequestCode.BACKUP_REQUEST.value:
            pass

        elif code == protocol.RequestCode.RECOVER_REQUEST.value:
            file = db.pull_file(request.header.client_id, request.payload.message_content)
            response.set_pull_messages(file)

        elif code == protocol.RequestCode.GETLIST_REQUEST.value:
            clients_list = db.get_files_list(request.header.client_id)
            response.set_clients_list(clients_list)

        elif code == protocol.RequestCode.DELETION_REQUEST.value:
            lock.acquire()
            db.delete_file(request.header.client_id, request.payload.message_content)
            lock.release()

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
                is_authenticated = authenticate_user(connection, DB)
                if is_authenticated:
                    # client_thread = threading.Thread(target=request_handler, args=(connection, thread_lock, DB))
                    # client_thread.start()
                    request_handler(connection, thread_lock, DB)
                else:
                    # TODO: Return error status.
                    pass
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
    except Exception as error:
        print('Error: %s' % error)
