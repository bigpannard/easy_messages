import json

FORMAT = 'utf-8'

class MessageType:
    MSG_OK = "Msg OK"
    MSG_NOK = "Msg NOK"
    DISCONNECT_MESSAGE = "!!DISCONNECT!!"
    MESSAGE_4_CLIENT = "!!MESS4U!!"
    NO_MESSAGE ="!!NOMESS!!"

class Message:
    def __init__(self, msg, entity="default", category="#D#"):
        self.__dict={}
        self.__dict[category]={}
        self.__dict[category][entity] = msg
        self.__category = category
        self.__msg = msg
        self.__entity = entity
        self.__encode = None

        self.__is_disconnect_msg = self.__msg == str(MessageType.DISCONNECT_MESSAGE)
        self.__is_message_available_on_server = self.__msg == str(MessageType.MESSAGE_4_CLIENT)
        self.__is_message_ok = self.__msg == str(MessageType.MSG_OK)
        
    @property
    def message(self):
        return self.__msg
    @property
    def category(self):
        return self.__category
    @property
    def length(self):
        if not self.__encode:
            self.encode()
        return len(self.__encode)
    def entity(self):
        return self.__entity

    def encode(self, buffer_size=None):
        self.__encode = json.dumps(self.__dict,indent=3).encode(FORMAT)
        if buffer_size:
            if buffer_size > len(self.__encode):
                self.__encode += b' ' * (buffer_size -  len(self.__encode))
            else:
                raise ValueError(f"Buffer_Size is lower than data to send")
        return self.__encode
    
    def is_disconnect_message(self):
        return self.__is_disconnect_msg
    
    def is_message_available_on_server(self):
        return self.__is_message_available_on_server
    
    def is_message_ok(self):
        return self.__is_message_ok
    
    @classmethod
    def decode(cls, json_data):
        dic = json.loads(json_data)
        for key,value in dic.items():
            for x,y in value.items():
                return cls(msg=y,category=key,entity=x)
    @classmethod
    def create_msg(cls, message_type,entity="default"):
        return cls(msg=message_type,entity=entity)