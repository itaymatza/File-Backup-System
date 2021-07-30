import os
import pathlib
import shutil
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
          'BACKUP_SUCCESS': 202,
          'DELETE_SUCCESS': 203,
          'UNKNOWN_FILE_ERROR': 1000,
          'EMPTY_FILE_LIST_ERROR': 1001,
          'GENERAL_ERROR': 1002}


# Encode client request according to the protocol spec
def encode_request(version, op, filename=None, enc=None):
    request = encode_request_header(version, op, filename)
    if op == 'BACKUP_REQUEST':
        request += encode_request_payload(filename, enc)
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
            head, tail = os.path.split(filename)
            filename = tail
            filename_len = len(filename.encode('utf-8'))
            if filename_len <= 0 or USHORT_MAX < filename_len:
                raise Exception('Failed to create request header - Missing filename size')
        op_number = OP.get(op)
    else:
        raise Exception('Failed to create request header - Invalid op number')

    # encode the request header
    header = struct.pack(UCHAR, version)
    header += struct.pack(UCHAR, op_number)

    if op == 'GETLIST_REQUEST':
        header += struct.pack(USHORT, 0)
    else:  # other requests have filename filed
        filename_len = len(filename.encode('utf-8'))
        header += struct.pack(USHORT, filename_len)
        filename_len = '<' + str(filename_len) + 's'  # filename_len format for struct
        header += struct.pack(filename_len, filename.encode('utf-8'))
    return header


# Encode client request payload according to the protocol spec
# Request payload apply just for backup request
def encode_request_payload(filename, enc):
    if not os.path.exists(filename):
        raise Exception("The file in the path: " + filename + " not exist.")

    file_name_enc = enc.encrypt_file(filename)
    with open(file_name_enc, 'rb') as f:
        file = f.read()
        payload_size = len(file)
    os.remove(file_name_enc)

    if payload_size < 0 or ULONG_MAX < payload_size:
        raise Exception('Failed to create request header - Invalid payload size')
    payload = struct.pack(ULONG, payload_size)
    payload += file
    return payload


# Decode server response according to the protocol spec
# Returns tuple - (date,is_success_status)
def decode_server_response(sock, name, enc=None):
    # pars header - receive version and status bytes
    srv_version, request_status = struct.unpack('<BH', sock.recv(3))

    # error status
    if request_status in {STATUS.get('EMPTY_FILE_LIST_ERROR'), STATUS.get('GENERAL_ERROR')}:
        error_msg = "Unable to get file list from the server - \n"
        if request_status == STATUS.get('EMPTY_FILE_LIST_ERROR'):
            error_msg += "There are no files for user " + str(name) + "."
        else:
            error_msg += "General error - problem with the server."
        return error_msg, False

    # filename header decode
    filename_len = sock.recv(2)
    received_filename_len, = struct.unpack('<H', filename_len)
    filename = recv_all(sock, received_filename_len)
    received_filename_len = '<' + str(received_filename_len) + 's'  # received_filename_len format for struct
    received_filename, = struct.unpack(received_filename_len, filename)

    # file payload decode and decrypt, for recover request
    if request_status == STATUS.get('RECOVER_SUCCESS'):
        received_data = sock.recv(4)
        received_file_len, = struct.unpack(ULONG, received_data)
        # receive to client's directory
        path_file_dst = os.path.join(os.path.join(pathlib.Path().resolve(), name), received_filename.decode())
        recv_to_file(sock, received_file_len, path_file_dst)
        enc.decrypt_file(path_file_dst)

    if request_status == STATUS.get('UNKNOWN_FILE_ERROR'):
        return received_filename, False
    elif request_status in {STATUS.get('BACKUP_SUCCESS'),
                            STATUS.get('DELETE_SUCCESS'),
                            STATUS.get('RECOVER_SUCCESS'),
                            STATUS.get('SENT_LIST_SUCCESSFULLY')}:
        return received_filename, True


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
