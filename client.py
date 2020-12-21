import socket


from message import Message,MessageType,FORMAT
from server import Server,get_message_from_socket, DEFAULT_BUFFER_SIZE


class Client:   
    def __init__(self, ip_address, port, category=None,entity="Default"):
        self.ip_address = ip_address
        self.port = port
        self.category = category
        self.__entity = entity
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((self.ip_address,self.port))
    
    def __send(self, msg):
        mlength = Message(msg=msg.length,entity=self.__entity)
        self.__socket.send(mlength.encode(buffer_size=DEFAULT_BUFFER_SIZE))
        self.__socket.send(msg.encode())
        return get_message_from_socket(DEFAULT_BUFFER_SIZE,self.__socket)

    def send(self, msg):
        m2send = Message(msg=msg,entity=self.__entity)
        return self.__send(msg=m2send)
    
    def ask_if_message_available(self):
        m2send = Message.create_msg(message_type=MessageType.MESSAGE_4_CLIENT,entity=self.__entity)
        mes = self.__send(msg=m2send)
        if mes.is_message_ok():
            #nbr message
            mes = get_message_from_socket(DEFAULT_BUFFER_SIZE,self.__socket)
            nbr_message = int(mes.message)
            mess = []
            for i in range(nbr_message):
                mlenght = get_message_from_socket(DEFAULT_BUFFER_SIZE, self.__socket)
                mess.append( get_message_from_socket(int(mlenght.message), self.__socket))
            return mess
    
    def disconnect(self):
        return Message.create_msg(message_type=MessageType.DISCONNECT_MESSAGE,entity=self.__entity)
        

if __name__ == "__main__":
    client = Client("192.168.0.7", 5050,entity="Manu")
    mess = client.send("TOTOcoucou")
    print(mess.message)
    mess = client.send("coucou")
    print(mess.message)
    mess = client.ask_if_message_available()
    print(mess)
    mess = client.disconnect()
    print(mess.message)
