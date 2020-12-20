import socket

class Client:
    DEFAULT_BUFFER_SIZE = 64
    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = '!DISCONNECT' 
    
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((self.ip_address,self.port))
    
    def send(self, msg):
        message = msg.encode(Client.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(Client.FORMAT)
        send_length += b' '*(Client.DEFAULT_BUFFER_SIZE -  len(send_length))
        self.__socket.send(send_length)
        self.__socket.send(message)
        return self.__socket.recv(2048).decode(Client.FORMAT)
    
    def disconnect(self):
        return self.send(Client.DISCONNECT_MESSAGE)

if __name__ == "__main__":
    client = Client("192.168.0.7", 5050)
    print(client.send("coucou"))
    print(client.disconnect())