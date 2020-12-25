import socket

from easy_message import IntMessage, EasyMessage, ServerMessage, ServerMessageEnum
from easy_server import DEFAULT_BUFFER_SIZE, get_json_message_from_socket


class EasyClient:   
    def __init__(self, ip_address, port, entity="Default", category=None):
        self.ip_address = ip_address
        self.port = port
        self.__category = category
        self.__entity = entity
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((self.ip_address, self.port))

    def __read_message(self, length):
        return EasyMessage.decode(get_json_message_from_socket(msg_length=length, connection=self.__socket))

    def __read_int_message(self):
        return IntMessage.decode(get_json_message_from_socket(DEFAULT_BUFFER_SIZE, connection=self.__socket))

    def __read_server_message(self):
        return ServerMessage.decode(get_json_message_from_socket(DEFAULT_BUFFER_SIZE, connection=self.__socket))

    def __send(self, message):
        self.__socket.send(message.encode())

    def __send_message(self, message):
        int_msg = IntMessage(int_value=message.length, buffer_size=DEFAULT_BUFFER_SIZE, entity=message.entity)
        self.__send(int_msg)
        self.__send(message)
    
    def send(self, message):
        """
        Send a message to server protocol :
        Send ServerMessage with SEND_MESS
        Length of the message to send
        Send the message 
        receive MSG_OK or MSG_NOK

        Args:
            message (Message): Message to send at the server

        Returns:
            [ServerMessage]: server message describe if the server get or not the message
        """
        if isinstance(message, EasyMessage):
            self.__send(ServerMessage(ServerMessageEnum.SEND_MESS, buffer_size=DEFAULT_BUFFER_SIZE))
            self.__send_message(message)
            return self.__read_server_message()
        else:
            raise ValueError("The msg parameter should be an instance of Message")
    
    def get_messages(self):
        message = ServerMessage(server_message_enum=ServerMessageEnum.MESSAGE_4_CLIENT, buffer_size=DEFAULT_BUFFER_SIZE,
                                entity="Manu", category='Admin')
        self.__send(message)
        message = self.__read_server_message()
        if message.ServerMessageEnum == ServerMessageEnum.MSG_OK:
            int_msg = self.__read_int_message()
            lst_message = []
            for i in range(int_msg.int_value):
                length_msg = self.__read_int_message()
                lst_message.append(self.__read_message(length_msg.int_value))
            return lst_message

    def disconnect(self):
        self.__send(ServerMessage(server_message_enum=ServerMessageEnum.DISCONNECT_MESSAGE,
                                  buffer_size=DEFAULT_BUFFER_SIZE, entity=self.__entity, category=self.__category))
        return self.__read_server_message()


if __name__ == "__main__":
    client = EasyClient("localhost", 5050, entity="Manu")
    msg = client.send(EasyMessage(message="<ADD_PL>Bonjour serveur c'est Manu", entity="Manu", category="Admin"))
    print(msg.message)
    client.get_messages()
    msg = client.disconnect()
    print(msg.message)
