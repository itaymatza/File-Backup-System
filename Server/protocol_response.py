""" Response """
import uuid
from enum import Enum


class ResponseCode(Enum):
    RECOVER_SUCCESS = 200
    SENT_LIST_SUCCESSFULLY = 201
    BACKUP_SUCCESS = 202
    DELETE_SUCCESS = 203
    UNKNOWN_FILE_ERROR = 1000
    EMPTY_FILE_LIST_ERROR = 1001
    GENERAL_ERROR = 1002

    # check if given value code is part of the Enum
    @classmethod
    def is_valid(cls, value):
        return value in cls._value2member_map_


# TODO handle error messages
class Response:
    def __init__(self, srv_version=None):
        self.header = ResponseHeader(srv_version)
        self.payload = None

    def set_general_error(self):
        self.header.code = ResponseCode.GENERAL_ERROR.value

    def set_unknown_file_error(self, filename):
        self.header.code = ResponseCode.UNKNOWN_FILE_ERROR.value
        self.payload = ResponsePayload(len(filename), filename)

    def set_backup(self, filename):
        self.header.code = ResponseCode.BACKUP_SUCCESS.value
        self.payload = ResponsePayload(len(filename), filename)

    def set_files_list(self, files_list):
        if 0 < len(files_list):
            self.header.code = ResponseCode.SENT_LIST_SUCCESSFULLY.value
            self.payload = ResponsePayload(0, files_list)
            for file in files_list:
                self.payload.payload_size += len(file[0]) + 1
        else:
            self.header.code = ResponseCode.EMPTY_FILE_LIST_ERROR.value

    def set_as_delete(self, filename):
        self.header.code = ResponseCode.DELETE_SUCCESS.value
        self.payload = ResponsePayload(len(filename), filename)


class ResponseHeader:
    def __init__(self, srv_version=None):
        self.version = srv_version
        self.code = None

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code):
        if code is None:
            self._code = None
        elif ResponseCode.is_valid(code):
            self._code = code


class ResponsePayload:
    def __init__(self, payload_size=None, payload=None):
        self.payload_size = payload_size
        self.payload = payload

    @property
    def payload_size(self):
        return self._payload_size

    @payload_size.setter
    def payload_size(self, payload_size):
        self._payload_size = payload_size

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, payload):
        self._payload = payload


class RecoverPayload(ResponsePayload):
    def __init__(self, payload_size=None, payload=None, file_size=None, file=None):
        super().__init__(payload_size, payload)
        self.file_size = file_size
        self.file = file

    @property
    def file_size(self):
        return self._file_size

    @file_size.setter
    def file_size(self, file_size):
        self._file_size = file_size

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, file):
        self._file = file
