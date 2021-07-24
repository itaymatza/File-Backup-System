""" Request """
from enum import Enum

GENERAL_ERROR = 9000


class RequestCode(Enum):
    BACKUP_REQUEST = 100
    RECOVER_REQUEST = 101
    DELETION_REQUEST = 102
    GETLIST_REQUEST = 103

    # check if given value code is part of the Enum
    @classmethod
    def is_valid(cls, value):
        return value in cls._value2member_map_


class Request:
    def __init__(self):
        self.header = RequestHeader()
        self.payload = None

    def set_payload(self):
        if self.header.code == RequestCode.BACKUP_REQUEST.value:
            self.payload = RequestPayload()


class RequestHeader:
    def __init__(self):
        self.version = None
        self.code = None
        self.filename_len = None
        self.filename = None

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        if version is None:
            self._code = None
        elif version in {1, 2}:
            self._version = version

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code):
        if code is None:
            self._code = None
        if RequestCode.is_valid(code):
            self._code = code
        else:
            self._code = GENERAL_ERROR

    @property
    def filename_len(self):
        return self._filename_len

    @filename_len.setter
    def filename_len(self, filename_len):
        self._filename_len = filename_len

    @property
    def filename(self):
        return self.filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename


class RequestPayload:
    def __init__(self):
        self.payload_size = None
        self.payload = None

    @property
    def payload_size(self):
        return self._payload_size

    @payload_size.setter
    def payload_size(self, payload_size):
        self._payload_size = payload_size

    @property
    def payload(self):
        return self.payload

    @payload.setter
    def payload(self, payload):
        self._payload = payload
