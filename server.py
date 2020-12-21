import socket
import threading

from message import Message,MessageType,FORMAT

DEFAULT_BUFFER_SIZE = 64

def get_message_from_socket(msg_length, conn):
    total_received = 0
    chunks = []
    while total_received < msg_length:
        chunk = conn.recv(msg_length-total_received).decode(FORMAT)
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        total_received = total_received + len(chunk)
    return Message.decode("".join(chunks))

class Server:   
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.__continue = True
        self.__MessageReceived_handler = None
        self.__MessageCheck_handler = None
        self.__MessageSendToClient_handler = None
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind((self.ip_address,self.port))
    
    @property
    def MessageReceived_handler(self):
        """Event handler used to send the message from the client.

        Returns:
            [function]: function should have 3 parameters : addr (tuple client IP and client port),  msg string message, list of message from client
        """
        return self.__MessageReceived_handler

    @property
    def MessageCheck_handler(self):
        return self.__MessageCheck_handler

    @property
    def MessageSendToClient_handler(self):
        return self.__MessageSendToClient_handler
    
    @MessageSendToClient_handler.setter
    def MessageSendToClient_handler(self, value):
        self.__MessageSendToClient_handler = value

    @MessageCheck_handler.setter
    def MessageCheck_handler(self, value):
        self.__MessageCheck_handler = value
    
    @MessageReceived_handler.setter
    def MessageReceived_handler(self, value):
        """Event handler used to send the message from the client.

        Args:
            value (function): function should have 3 parameters : addr (tuple client IP and client port),  msg string message, list of message from client
        """
        self.__MessageReceived_handler = value

    def __send_message_to_client(self,addr, conn, last_msg):
        messages = self.__MessageSendToClient_handler(addr, last_msg)
        if messages:
            conn.send(Message.create_msg(MessageType.MSG_OK).encode(buffer_size=DEFAULT_BUFFER_SIZE))
            conn.send(Message(len(messages)).encode(buffer_size=DEFAULT_BUFFER_SIZE))
            for m in messages:
                mlength = Message(m.length)
                conn.send(mlength.encode(buffer_size=DEFAULT_BUFFER_SIZE))
                conn.send(m.encode())
        else:
            conn.send(Message.create_msg(MessageType.NO_MESSAGE).encode(buffer_size=DEFAULT_BUFFER_SIZE))

    def __handle_connection(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected")
        connected = True
        while connected:
            msg = get_message_from_socket(DEFAULT_BUFFER_SIZE,conn)
            if msg:
                msg_length = int(msg.message)
                msg = get_message_from_socket(msg_length,conn)          
                if msg.is_disconnect_message():
                    connected = False
                    conn.send(Message.create_msg(MessageType.MSG_OK).encode(buffer_size=DEFAULT_BUFFER_SIZE))
                elif msg.is_message_available_on_server():
                    if self.__MessageSendToClient_handler:
                        self.__send_message_to_client(addr, conn, msg)
                    else:
                        conn.send(Message.create_msg(MessageType.NO_MESSAGE).encode(buffer_size=DEFAULT_BUFFER_SIZE))
                else:
                    message_validate = True
                    if self.__MessageCheck_handler:
                        message_validate = self.__MessageCheck_handler(addr, msg.message)
                    if message_validate:
                        #if someone get the handler we sent it into new thread
                        if self.MessageReceived_handler:
                            thread = threading.Thread(target=self.MessageReceived_handler, args=(addr, msg))
                            thread.start()
                        
                        conn.send(Message.create_msg(MessageType.MSG_OK).encode(buffer_size=DEFAULT_BUFFER_SIZE))
                    else:
                            conn.send(Message.create_msg(MessageType.MSG_NOK).encode(buffer_size=DEFAULT_BUFFER_SIZE))
        
        print(f"[CLOSE CONNECTION] {addr}")
        conn.close()

    def start(self):
        """[summary]
        Start the server into an loop
        """
        self.__socket.listen()
        print(f"[LISTENING] Server is listening on {self.ip_address}")
        while self.__continue:
            conn,addr = self.__socket.accept()
            thread = threading.Thread(target=self.__handle_connection, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() -1}")
        print(f"[STOP LISTENING]")
    



def manage_message(address, msg):
    print(f"New message to treat {address}, category:{msg.category} message:{msg.message}")

def check_message(address, msg):
    if msg.startswith("TOTO"):
        return True
    else:
        return False

def message_send_to_client(addr, last_msg):
    if last_msg and last_msg.entity() == "Manu":
        mess = []
        for i in range(5):
            mess.append( Message(f"{i} c'est bien !!!!"))
        return mess


if __name__ == "__main__":
    serveur = Server("192.168.0.7", 5050)
    serveur.MessageReceived_handler = manage_message
    serveur.MessageCheck_handler = check_message
    serveur.MessageSendToClient_handler = message_send_to_client
    serveur.start()