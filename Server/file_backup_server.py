"""File Backup System - Server

The role of this module is to manage the list of users registered to
the service and allow them to backup and restore files.

"""
import socket
import protocol
import threading
import database
import server_helper

SERVER_VERSION = 1
UID_LEN = 16


def request_handler(conn, lock):
    db = database.DataBase()
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

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((TCP_IP, TCP_PORT))
            thread_lock = threading.Lock()
            while True:
                sock.listen(100)
                sock_conn, address_and_port = sock.accept()
                # TO DO - Add SSL
                # TO DO - Add user authentication check
                client_thread = threading.Thread(target=request_handler,
                                                 args=(sock_conn, thread_lock))
                client_thread.start()
    except Exception as error:
        print('Error: %s' % error)
