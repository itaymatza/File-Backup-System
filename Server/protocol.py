""" File Backup System - protocol.

Decode requests and encode responses by the protocol specification.
This is a stateless Protocol - no session information is retained by the
server. Relevant session data is sent to the server by the client in such a way
that every packet of information transferred can be understood in isolation,
without context information from previous packets in the session.

"""
import struct
from protocol_request import Request, RequestCode
from protocol_response import Response, ResponseCode

ULONG = '<L'  # unsigned 32-bit long
ULONG_MAX = (2 ** (8 * 4)) - 1
USHORT = '<H'  # unsigned 16-bit short
UCHAR = '<B'  # unsigned 8-bit char
UCHAR_MAX = (2 ** 8) - 1
UNAME_LENGTH = '<256s'
KEY_LENGTH = '<160s'


def recv_all(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def encode_server_response(response):
    encoded_response = struct.pack(UCHAR, response.header.version)
    encoded_response += struct.pack(USHORT, response.header.code)
    encoded_response += struct.pack(ULONG, response.header.filename_len)
    if response.header.code == ResponseCode.REGISTERED_SUCCESSFULLY.value:
        encoded_response += struct.pack(UNAME_LENGTH, response.payload.client_id)
    elif response.header.code == ResponseCode.CLIENTS_LIST.value:
        for client in response.payload.clients_list:
            encoded_response += struct.pack(UNAME_LENGTH, client.client_id)
            encoded_response += struct.pack(UNAME_LENGTH, client.client_name)
    elif response.header.code == ResponseCode.PUBLIC_KEY.value:
        encoded_response += struct.pack(UNAME_LENGTH, response.payload.client_id)
        encoded_response += struct.pack(KEY_LENGTH, response.payload.public_key)
    elif response.header.code == ResponseCode.PULL_MESSAGES.value:
        for message in response.payload.messages:
            encoded_response += struct.pack(UNAME_LENGTH, message.client_id)
            encoded_response += struct.pack(ULONG, message.message_id)
            encoded_response += struct.pack(UCHAR, message.message_type)
            encoded_response += struct.pack(ULONG, message.message_size)
            message_length = '<' + str(message.message_size) + 's'
            encoded_response += struct.pack(message_length, message.message_content)
    elif response.header.code == ResponseCode.PUSH_MESSAGE.value:
        encoded_response += struct.pack(UNAME_LENGTH, response.payload.client_id)
        encoded_response += struct.pack(ULONG, response.payload.message_id)
    return encoded_response


def recv_and_decode_client_request(conn, db, request, uid):
    # decode request header
    request.header.client_id, = struct.unpack(UNAME_LENGTH, uid)
    request.header.version, = struct.unpack(UCHAR, conn.recv(1))
    request.header.code, = struct.unpack(UCHAR, conn.recv(1))
    request.header.filename_len, = struct.unpack(ULONG, conn.recv(4))

    # validate request header
    if None in {request.header.client_id, request.header.version, request.header.code}:
        request.header.code = ResponseCode.GENERAL_ERROR.value

    # validate request payload
    request.set_payload()
    if request.header.code == RequestCode.REGISTER_REQUEST.value:
        request.payload.name, = struct.unpack(UNAME_LENGTH, conn.recv(255))
        request.payload.public_key, = struct.unpack(KEY_LENGTH, conn.recv(160))
        return request.header.code

    elif request.header.code == RequestCode.PUBLIC_KEY_REQUEST.value:
        request.payload.client_id, = struct.unpack(UNAME_LENGTH, conn.recv(16))
        if not db.is_id_exists(request.payload.client_id):
            request.header.code = ResponseCode.GENERAL_ERROR.value

    elif request.header.code == RequestCode.PUSH_MESSAGE_REQUEST.value:
        request.payload.client_id, = struct.unpack(UNAME_LENGTH, conn.recv(16))
        request.payload.message_type, = struct.unpack(UCHAR, conn.recv(1))
        request.payload.content_size, = struct.unpack(ULONG, conn.recv(4))
        received = recv_all(conn, request.payload.content_size)
        content_size = '<' + str(request.payload.content_size) + 's'
        request.payload.message_content, = struct.unpack(content_size, received)
        if not db.is_id_exists(request.payload.client_id):
            request.header.code = ResponseCode.GENERAL_ERROR.value

    # unknown request code
    else:
        if request.header.code not in {RequestCode.CLIENTS_LIST_REQUEST.value,
                                       RequestCode.PULL_MESSAGES_REQUEST.value}:
            request.header.code = ResponseCode.GENERAL_ERROR.value

    # validations
    if not db.is_id_exists(request.header.client_id):
        request.header.code = ResponseCode.GENERAL_ERROR.value

    return request.header.code
