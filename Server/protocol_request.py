""" Request """
from enum import Enum

GENERAL_ERROR = 9000


class RequestCode(Enum):
    BACKUP_REQUEST = 100
    RECOVER_REQUEST = 101
    DELETION_REQUEST = 102
    GETLIST_REQUEST = 103

    @classmethod
    def is_valid(cls, value):
        return value in cls._value2member_map_


class Request:
    def __init__(self):
        self.header = RequestHeader()
        self.payload = None

    def set_suitable_payload(self):
        if self.header.code is not None:
            if self.header.code == RequestCode.REGISTER_REQUEST.value:
                self.payload = RegisterRequestPayload()
            elif self.header.code == RequestCode.PUBLIC_KEY_REQUEST.value:
                self.payload = PublicKeyRequestPayload()
            elif self.header.code == RequestCode.PUSH_MESSAGE_REQUEST.value:
                self.payload = MessagePayload()


class RequestHeader:
    def __init__(self):
        self.version = None
        self.code = None
        self.payload_size = None
        self.client_id = None

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, cid):
        self._client_id = cid

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
    def payload_size(self):
        return self._payload_size

    @payload_size.setter
    def payload_size(self, payload_size):
        self._payload_size = payload_size


class RequestPayload:
    pass


class RegisterRequestPayload(RequestPayload):
    def __init__(self):
        self.name = None
        self.public_key = None

    @property
    def name(self):
        return self._name.split(b'\0', 1)[0].decode("utf-8")

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def public_key(self):
        return self._public_key

    @public_key.setter
    def public_key(self, key):
        self._public_key = key


class PublicKeyRequestPayload(RequestPayload):
    def __init__(self):
        self.client_id = None

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, client_id):
        self._client_id = client_id


class MessagePayload(RequestPayload):
    def __init__(self):
        self.client_id = None
        self.message_type = None
        self.content_size = None
        self.message_content = None

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, client_id):
        self._client_id = client_id

    @property
    def message_type(self):
        return self._message_type

    @message_type.setter
    def message_type(self, message_type):
        self._message_type = message_type

    @property
    def content_size(self):
        return self._content_size

    @content_size.setter
    def content_size(self, content_size):
        self._content_size = content_size

    @property
    def message_content(self):
        return self._message_content

    @message_content.setter
    def message_content(self, message_content):
        self._message_content = message_content
