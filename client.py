import socket

from message import IntMessage,Message,ServerMessage,ServerMessageEnum
from server import DEFAULT_BUFFER_SIZE, get_json_message_from_socket


class Client:   
    def __init__(self, ip_address, port, entity="Default", category=None):
        self.ip_address = ip_address
        self.port = port
        self.__category = category
        self.__entity = entity
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((self.ip_address,self.port))

    def __read_message(self, length):
        return Message.decode(get_json_message_from_socket(msg_length=length,socket=self.__socket))
    def __read_int_message(self):
        return IntMessage.decode(get_json_message_from_socket(DEFAULT_BUFFER_SIZE,socket=self.__socket))
    def __read_server_message(self):
        return ServerMessage.decode(get_json_message_from_socket(DEFAULT_BUFFER_SIZE,socket=self.__socket))
    def __send(self, message):
        self.__socket.send(message.encode())
    def __send_message(self, msg):
        imsg = IntMessage(int_value=msg.length,buffer_size=DEFAULT_BUFFER_SIZE,entity=msg.entity)
        self.__send(imsg)
        self.__send(msg)
    
    def send(self, msg):
        """
        Send a message to server protocol :
        Send ServerMessage with SEND_MESS
        Length of the message to send
        Send the message 
        receive MSG_OK or MSG_NOK

        Args:
            msg (Message): Message to send at the serveur 

        Returns:
            [ServerMessage]: server message describe if the server get or not the message
        """
        if isinstance(msg,Message):
            self.__send(ServerMessage(ServerMessageEnum.SEND_MESS,buffer_size=DEFAULT_BUFFER_SIZE))
            self.__send_message(msg)
            return self.__read_server_message()
        else:
            raise ValueError("The msg parameter should be an instancd of Message")
    
    def get_messsages(self):
        msg = ServerMessage(server_message_enum=ServerMessageEnum.MESSAGE_4_CLIENT,buffer_size=DEFAULT_BUFFER_SIZE,entity="Manu",category='Admin')
        self.__send(msg)
        msg = self.__read_server_message() 
        print(msg.ServerMessageEnum)
        print(ServerMessageEnum.MSG_NOK)
        if msg.ServerMessageEnum == ServerMessageEnum.MSG_OK:
            imsg = self.__read_int_message()
            for i in range(imsg.int_value):
                length_msg =self.__read_int_message()
                msg = self.__read_message(length_msg.int_value)

    def disconnect(self):
        self.__send(ServerMessage(server_message_enum=ServerMessageEnum.DISCONNECT_MESSAGE,buffer_size=DEFAULT_BUFFER_SIZE, entity=self.__entity, category=self.__category))
        return self.__read_server_message()

        

if __name__ == "__main__":
    client = Client("192.168.0.7", 5050,entity="Manu")
    msg = client.send(Message(message="TOTOBonjour serveur c'est Manu",entity="Manu",category="Admin"))
    print(msg.message)
    client.get_messsages()
    msg = client.disconnect()
    print(msg.message)
    input()