import struct

UCHAR = '<B'  # unsigned 8-bit char
UCHAR_MAX = (2 ** 8) - 1
USHORT = '<H'  # unsigned 16-bit short
USHORT_MAX = (2 ** (8 * 2))
ULONG = '<L'  # unsigned 32-bit long
ULONG_MAX = (2 ** (8 * 4))

OP = {'BACKUP_REQUEST': 100,
      'RECOVER_REQUEST': 101,
      'DELETION_REQUEST': 102,
      'GETLIST_REQUEST': 103}
STATUS = {'RECOVER_SUCCESS': 200,
          'SENT_LIST_SUCCESSFULLY': 201,
          'BACKUP_OR_DELETE_SUCCESS': 202,
          'UNKNOWN_FILE_ERROR': 1000,
          'EMPTY_FILE_LIST_ERROR': 1001,
          'GENERAL_ERROR': 1002}


# Encode client request according to the protocol spec
def encode_request(version, op, filename=None):
    request = encode_request_header(version, op, filename)
    if op == 'BACKUP_REQUEST':
        request += encode_request_payload(filename)
    return request


# Encode client request header according to the protocol spec
def encode_request_header(version, op, filename=None):
    # validate parameters
    if version <= 0 or UCHAR_MAX < version:
        raise Exception('Failed to create request header - Invalid version number')
    if op in OP:
        if op != 'GETLIST_REQUEST':
            if not filename:
                raise Exception('Failed to create request header - Missing filename')
            filename_len = len(filename.encode('utf-8'))
            if filename_len <= 0 or USHORT_MAX < filename_len:
                raise Exception('Failed to create request header - Missing filename size')
        op_number = OP.get(op)
    else:
        raise Exception('Failed to create request header - Invalid op number')

    # encode the request header
    header = struct.pack(UCHAR, version)
    header += struct.pack(UCHAR, op_number)

    if op != 'GETLIST_REQUEST':  # getlist request have no filename filed
        filename_len = len(filename.encode('utf-8'))
        header += struct.pack(USHORT, filename_len)
        filename_len = '<' + str(filename_len) + 's'  # filename_len format for struct
        header += struct.pack(filename_len, filename.encode('utf-8'))
    return header


# Encode client request payload according to the protocol spec
# Request payload apply just for backup request
def encode_request_payload(filename):
    try:
        with open(filename, 'rb') as f:
            file = f.read()
            payload_size = len(file)
            if payload_size <= 0 or ULONG_MAX < payload_size:
                raise Exception('Failed to create request header - Invalid payload size')
    except IOError:
        raise Exception('Error: ' + filename + 'file is not accessible.')

    payload = struct.pack(ULONG, payload_size)
    payload += payload
    return payload


# Decode server response according to the protocol spec
# Returns tuple - (date,is_success_status)
def decode_server_response(sock, uid):
    # pars header - receive version and status bytes
    srv_version = struct.unpack('<B', sock.recv(1))
    request_status = struct.unpack('<H', sock.recv(2))

    # error status
    if request_status in {STATUS.get('EMPTY_FILE_LIST_ERROR'), STATUS.get('GENERAL_ERROR')}:
        error_msg = "Unable to get file list from the server - \n"
        if request_status == STATUS.get('EMPTY_FILE_LIST_ERROR'):
            error_msg += "There are no files for user " + str(uid) + "."
        else:
            error_msg += "General error - problem with the server."
        return error_msg, False

    # filename header decode
    filename_len = sock.recv(2)
    received_filename_len, = struct.unpack('<H', filename_len)
    filename = recv_all(sock, received_filename_len)
    received_filename, = struct.unpack('<' + str(received_filename_len) + 's', filename)

    if request_status == STATUS.get('UNKNOWN_FILE_ERROR'):
        return received_filename, False
    elif request_status == STATUS.get('BACKUP_OR_DELETE_SUCCESS'):
        return received_filename, True

    # response with payload
    elif request_status in {STATUS.get('RECOVER_SUCCESS'), STATUS.get('SENT_LIST_SUCCESSFULLY')}:
        received_data = sock.recv(4)
        received_file_len, = struct.unpack('<L', received_data)
        if request_status == STATUS.get('RECOVER_SUCCESS'):
            recv_to_file(sock, received_file_len, 'tmp')
            return received_filename, True
        else:  # SENT_LIST_SUCCESSFULLY
            files_list = b"" + recv_all(sock, received_file_len)
            return files_list, True


def recv_all(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


# Receive n bytes or return None if EOF is hit
def recv_to_file(sock, n, file):
    with open(file, 'wb') as f:
        while n != 0:
            packet = sock.recv(n)
            received_file = b""
            received_file += packet
            if not packet:
                return
            f.write(packet)
            n -= len(packet)
