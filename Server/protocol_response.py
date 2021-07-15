""" Response """
import uuid
from enum import Enum


class ResponseCode(Enum):
    REGISTERED_SUCCESSFULLY = 1000
    CLIENTS_LIST = 1001
    PUBLIC_KEY = 1002
    PUSH_MESSAGE = 1003
    PULL_MESSAGES = 1004
    GENERAL_ERROR = 9000

    @classmethod
    def is_valid(cls, value):
        return value in cls._value2member_map_


class Response:
    def __init__(self, srv_version=None):
        self.header = ResponseHeader(srv_version)
        self.payload = None

    def set_general_error(self):
        self.header.code = ResponseCode.GENERAL_ERROR.value
        self.header.payload_size = 0
        self.payload = None

    def set_registered_successfully(self, uid):
        self.header.code = ResponseCode.REGISTERED_SUCCESSFULLY.value
        self.header.payload_size = 16
        self.payload = ResponsePayload(uid.bytes)

    def set_clients_list(self, clients_list):
        self.header.code = ResponseCode.CLIENTS_LIST.value
        self.header.payload_size = len(clients_list) * (16 + 255)
        self.payload = ClientsListPayload(clients_list)

    def set_public_key(self, pkey):
        self.header.code = ResponseCode.PUBLIC_KEY.value
        self.header.payload_size = 16 + 160
        uid = uuid.UUID(pkey[0].decode('utf-8'))
        public_key = pkey[1]
        self.payload = PublicKeyPayload(uid.bytes, public_key)

    def set_pull_messages(self, messages):
        self.header.code = ResponseCode.PULL_MESSAGES.value
        self.header.payload_size = len(messages) * (16 + 4 + 1 + 4)
        self.payload = PullMassagesPayload(self.header, messages)

    def set_push_message(self, uid, message_id):
        self.header.code = ResponseCode.PUSH_MESSAGE.value
        self.header.payload_size = 16 + 4
        self.payload = MessagePushPayload(uid, message_id)


class ResponseHeader:
    def __init__(self, srv_version=None):
        self.version = srv_version
        self.code = None
        self.payload_size = None

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

    @property
    def payload_size(self):
        return self._payload_size

    @payload_size.setter
    def payload_size(self, payload_size):
        self._payload_size = payload_size


class ResponsePayload:
    def __init__(self, client_id=None):
        self.client_id = client_id

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, uid):
        self._client_id = uid


class ClientsListPayload:
    def __init__(self, clients_list):
        self.clients_list = []
        for id, name in clients_list:
            uid = uuid.UUID(id.decode('utf-8'))
            self.clients_list.append(ClientPayloadPart(uid.bytes, name))

    @property
    def clients_list(self):
        return self._clients_list

    @clients_list.setter
    def clients_list(self, value):
        self._clients_list = value


# Part of ClientsListPayload
class ClientPayloadPart:
    def __init__(self, client_id, client_name):
        self.client_id = client_id
        self.client_name = client_name

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, id):
        self._client_id = id

    @property
    def client_name(self):
        return self._client_name

    @client_name.setter
    def client_name(self, name):
        self._client_name = name


class PublicKeyPayload(ResponsePayload):
    def __init__(self, client_id=None, key=None):
        super().__init__(client_id)
        self.public_key = key

    @property
    def public_key(self):
        return self._public_key

    @public_key.setter
    def public_key(self, key):
        self._public_key = key


class PullMassagesPayload:
    def __init__(self, header, messages):
        self.messages = []
        for client_id, message_id, message_type, message_content in messages:
            uid = uuid.UUID(client_id.decode('utf-8'))
            header.payload_size += len(message_content)
            self.messages.append(MessagePayloadPart(
                uid.bytes, message_id, message_type, message_content))

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, value):
        self._messages = value


class MessagePayloadPart:
    def __init__(self, client_id, message_id, message_type, message_content):
        self.client_id = client_id
        self.message_id = message_id
        self.message_type = message_type
        self.message_size = len(message_content)
        self.message_content = message_content

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, id):
        self._client_id = id

    @property
    def message_id(self):
        return self._message_id

    @message_id.setter
    def message_id(self, message_id):
        self._message_id = message_id

    @property
    def message_type(self):
        return self._message_type

    @message_type.setter
    def message_type(self, message_type):
        self._message_type = message_type

    @property
    def message_size(self):
        return self._message_size

    @message_size.setter
    def message_size(self, message_size):
        self._message_size = message_size

    @property
    def message_content(self):
        return self._message_content

    @message_content.setter
    def message_content(self, content):
        self._message_content = content


class MessagePushPayload(ResponsePayload):
    def __init__(self, client_id, message_id):
        super().__init__(client_id)
        self.message_id = message_id

    @property
    def message_id(self):
        return self._message_id

    @message_id.setter
    def message_id(self, message_id):
        self._message_id = message_id
