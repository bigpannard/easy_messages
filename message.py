import json
from enum import Enum

FORMAT = 'utf-8'


class ServerMessageEnum(Enum):
    MSG_OK = "Msg OK"
    MSG_NOK = "Msg NOK"
    SEND_MESS = "!!SENDMESS!!"
    DISCONNECT_MESSAGE = "!!DISCONNECT!!"
    MESSAGE_4_CLIENT = "!!MESS4U!!"
    NO_MESSAGE = "!!NOMESS!!"


def encode(dictionary: dict, buffer_size: int):
    enc_value = json.dumps(dictionary, indent=3).encode(FORMAT)
    if buffer_size:
        if buffer_size > len(enc_value):
            enc_value += b' ' * (buffer_size - len(enc_value))
        else:
            raise ValueError(f"Buffer_Size is lower than data to send")
    return enc_value


class BaseMessage:
    def __init__(self, message: str, entity=None, category=None, buffer_size=None):
        self.__message = message
        self.__entity = entity
        self.__category = category
        self.__buffer_size = buffer_size
        self.__length = None
        
    @property
    def message(self):
        return self.__message

    @property
    def entity(self):
        return self.__entity

    @property
    def category(self):
        return self.__category

    @property
    def buffer_size(self):
        return self.__buffer_size

    @classmethod
    def decode(cls, json_data: bytes):
        dic = json.loads(json_data)
        message = dic.get("msg")
        ent = dic.get("ent")
        cat = dic.get("cat")
        buf = dic.get("buf")
        return cls(message=message, entity=ent, category=cat, buffer_size=buf)

    def create_dictionary(self):
        dic = {}
        if self.__message:
            dic["msg"] = self.__message
        if self.__entity:
            dic["ent"] = self.__entity
        if self.__category:
            dic["cat"] = self.__category
        if self.__buffer_size:
            dic["buf"] = self.__buffer_size
        return dic


class Message(BaseMessage):
    def __init__(self, message, entity=None, category=None):
        super().__init__(message=message, entity=entity, category=category)
        self.__length = None
    
    @property
    def length(self):
        if not self.__length:
            self.__length = len(self.encode())
        return self.__length

    @classmethod
    def decode(cls, json_data: bytes):
        return cls.create_from_base_message(BaseMessage.decode(json_data)) 
    
    @classmethod
    def create_from_base_message(cls, base_message):
        return cls(message=base_message.message, entity=base_message.entity, category=base_message.category)

    def create_dictionary(self):
        return super().create_dictionary()
    
    def encode(self):
        dic = self.create_dictionary()
        enc_value = encode(dictionary=dic, buffer_size=self.buffer_size)
        self.__length = len(enc_value)
        return enc_value


class ServerMessage(BaseMessage):
    def __init__(self, server_message_enum, buffer_size, entity=None, category=None):
        super().__init__(message=server_message_enum.value, entity=entity, category=category, buffer_size=buffer_size)
        self.__server_message_enum = server_message_enum        
        self.__length = None
    
    @property
    def length(self):
        if not self.__length:
            self.__length = len(self.encode())
        return self.__length

    @property
    def server_message_enum(self):
        return self.__server_message_enum
    
    @classmethod
    def decode(cls, json_data: bytes):
        return cls.create_from_base_message(BaseMessage.decode(json_data)) 
    
    @classmethod
    def create_from_base_message(cls, base_message):
        return cls(server_message_enum=ServerMessageEnum(base_message.message), buffer_size=base_message.buffer_size,
                   entity=base_message.entity, category=base_message.category)

    def create_dictionary(self):
        dic = super().create_dictionary()
        if self.__server_message_enum:
            dic["enum"] = self.__server_message_enum.value
        return dic
    
    def encode(self):
        dic = self.create_dictionary()
        enc_value = encode(dictionary=dic, buffer_size=self.buffer_size)
        self.__length = len(enc_value)
        return enc_value


class IntMessage(BaseMessage):
    def __init__(self, int_value, buffer_size, entity=None, category=None):
        super().__init__(message=str(int_value), buffer_size=buffer_size, entity=entity, category=category)
        self.__int = int_value        
        self.__length = None
    
    @property
    def length(self):
        if not self.__length:
            self.__length = len(self.encode())
        return self.__length

    @property
    def int_value(self):
        return self.__int
    
    @classmethod
    def decode(cls, json_data):
        return cls.create_from_base_message(BaseMessage.decode(json_data)) 
    
    @classmethod
    def create_from_base_message(cls, base_message):
        return cls(int_value=int(base_message.message), buffer_size=base_message.buffer_size,
                   entity=base_message.entity, category=base_message.category)

    def create_dictionary(self):
        dic = super().create_dictionary()
        if self.__int:
            dic["int"] = self.__int
        return dic
    
    def encode(self):
        dic = self.create_dictionary()
        enc_value = encode(dictionary=dic, buffer_size=self.buffer_size)
        self.__length = len(enc_value)
        return enc_value


if __name__ == "__main__":
    msg = ServerMessage(ServerMessageEnum.MESSAGE_4_CLIENT, 128, "Manu", "Admin")
    enc = msg.encode()
    print(enc)
    msg2 = ServerMessage.decode(enc)
    print(msg2.message)

    msg = IntMessage(127, 128, "Manu", "Admin")
    enc = msg.encode()
    print(enc)
    msg2 = IntMessage.decode(enc)
    print(msg2.message)

    msg = Message(message="fdsklfmjqsdfklqdmsjfqsdklfmqsdjfkqlsdmfjqsklmqsdjfqsdlmfdsklfmjqsdfklqdmsjfqsdklfmq"
                          "sdjfkqlsdmfjqsklmqsdjfqsdlmfdsklfmjqsdfklqdmsjfqsdklfmqsdjfkqlsdmfjqsklmqsdjfqsdlmfdsklfmjqs"
                          "dfklqdmsjfqsdklfmqsdjfkqlsdmfjqsklmqsdjfqsdlm")
    print(msg.length)
    enc = msg.encode()
    print(enc)
    msg2 = Message.decode(enc)
    print(msg2.message)
