import socket
import threading
import time

class Server:
    DEFAULT_BUFFER_SIZE = 64
    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = '!DISCONNECT' 
    
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.MessageReceived_handler = None
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind((self.ip_address,self.port))
        #dictionnary to know who (ipaddress) what message is sent [ipaddresse]:[message]
        self.__dict_data = {}
    
    def __get_message(self, msg_length, conn):
        total_received = 0
        chunks = []
        while total_received < msg_length:
            chunk = conn.recv(msg_length-total_received).decode(Server.FORMAT)
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            total_received = total_received + len(chunk)
        return "".join(chunks)

    def __handle_connection(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected")

        connected = True
        while connected:
            msg_length = conn.recv(Server.DEFAULT_BUFFER_SIZE).decode(Server.FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = self.__get_message(msg_length,conn)
                               
                if msg == Server.DISCONNECT_MESSAGE:
                    connected = False
                else:
                    if addr[0] not in self.__dict_data:
                        self.__dict_data[addr[0]] = list()
                    self.__dict_data[addr[0]].append(msg)

                    #if someone get the handler we sent it into new thread
                    if self.MessageReceived_handler:
                        thread = threading.Thread(target=self.MessageReceived_handler, args=(addr, msg,self.__dict_data[addr[0]]))
                        thread.start()
                
                #check the message to return msg OK or NOT or else
                conn.send("Msg OK".encode(Server.FORMAT))
        
        print(f"[CLOSE CONNECTION] {addr}")
        conn.close()

    def start(self):
        self.__socket.listen()
        print(f"[LISTENING] Server is listening on {self.ip_address}")
        while True:
            conn,addr = self.__socket.accept()
            thread = threading.Thread(target=self.__handle_connection, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() -1}")
    
        
    
def manage_message(addresse, message, historique_Message):
    print(f"New message to treat {addresse}, {message} {historique_Message}")


if __name__ == "__main__":
    serveur = Server("192.168.0.7", 5050)
    serveur.MessageReceived_handler = manage_message
    serveur.start()