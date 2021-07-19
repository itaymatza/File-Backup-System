import struct

ULONG = '<L'  # unsigned 32-bit long
ULONG_MAX = (2 ** (8 * 4)) - 1
USHORT = '<H'  # unsigned 16-bit short
UCHAR = '<B'  # unsigned 8-bit char
UCHAR_MAX = (2 ** 8) - 1
OP = {'BACKUP_REQUEST': 100,
      'RECOVER_REQUEST': 101,
      'DELETION_REQUEST': 102,
      'GETLIST_REQUEST': 103}
STATUS = {'RECOVER_SUCCESS': 210,
          'SENT_LIST_SUCCESSFULLY': 211,
          'BACKUP_OR_DELETE_SUCCESS': 212,
          'UNKNOWN_FILE_ERROR': 1001,
          'EMPTY_FILE_LIST_ERROR': 1002,
          'GENERAL_ERROR': 1003}


def encode_request_header(uid, version, op, filename=None):
    # validate parameters
    if uid <= 0 or uid > ULONG_MAX:
        raise Exception(
            'Failed to create request header - Invalid user id')
    if version <= 0 or version > UCHAR_MAX:
        raise Exception(
            'Failed to create request header - Invalid version number')
    if op in OP:
        if op != 'GETLIST_REQUEST':
            if not filename:
                raise Exception(
                    'Failed to create request header - Missing filename')
        op_number = OP.get(op)
    else:
        raise Exception(
            'Failed to create request header - Invalid op number')

    # encode the request header
    header = struct.pack(ULONG, uid)
    header += struct.pack(UCHAR, version)
    header += struct.pack(UCHAR, op_number)
    if op != 'GETLIST_REQUEST':
        name_len = len(filename.encode('utf-8'))
        header += struct.pack(USHORT, name_len)
        header += struct.pack('<' + str(name_len) + 's',
                              filename.encode('utf-8'))
    return header


def encode_request_payload(filename):
    try:
        with open(filename, 'rb') as f:
            payload = f.read()
            payload_size = len(payload)
            if payload_size <= 0 or payload_size >= ULONG_MAX:
                raise Exception(
                    'Failed to create request header - Invalid payload size')
    except IOError:
        print("Error: " + filename + "file is not accessible.")
        exit(-1)

    header = struct.pack(ULONG, payload_size)
    header += payload
    return header


def encode_request(uid, version, op, filename=None):
    request = encode_request_header(uid, version, op, filename)
    if op == 'BACKUP_REQUEST':
        request += encode_request_payload(filename)
    return request


def recv_all(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def recv_to_file(sock, n, file):
    # Helper function to recv n bytes or return None if EOF is hit
    with open(file, 'wb') as f:
        while n != 0:
            packet = sock.recv(n)
            received_file = b""
            received_file += packet
            if not packet:
                return
            f.write(packet)
            n -= len(packet)


def decode_server_response(sock, uid):
    # pars header - receive version and status bytes
    received = sock.recv(3)
    srv_version, request_status = struct.unpack('<BH', received)

    # error status
    if request_status in {STATUS.get('EMPTY_FILE_LIST_ERROR'),
                          STATUS.get('GENERAL_ERROR')}:
        error_msg = "Unable to get file list from the server - \n"
        if request_status == STATUS.get('EMPTY_FILE_LIST_ERROR'):
            error_msg += "There are no files for user " + str(uid) + "."
        else:
            error_msg += "General error - problem with the server."
        return error_msg, False

    # filename header decode
    received = sock.recv(2)
    received_filename_len, = struct.unpack('<H', received)
    received = recv_all(sock, received_filename_len)
    received_filename, = struct.unpack('<' + str(received_filename_len) + 's',
                                       received)

    if request_status == STATUS.get('UNKNOWN_FILE_ERROR'):
        return received_filename, False
    elif request_status == STATUS.get('BACKUP_OR_DELETE_SUCCESS'):
        return received_filename, True
    elif request_status in {STATUS.get('RECOVER_SUCCESS'),
                            STATUS.get('SENT_LIST_SUCCESSFULLY')}:
        received = sock.recv(4)
        received_file_len, = struct.unpack('<L', received)
        if request_status == STATUS.get('RECOVER_SUCCESS'):
            recv_to_file(sock, received_file_len, 'tmp')
            return received_filename, True
        else:  # SENT_LIST_SUCCESSFULLY
            received = recv_all(sock, received_file_len)
            received_file = b""
            received_file += received
            return received_filename, received_file
