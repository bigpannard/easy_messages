import socket
import threading

from easy_message import EasyMessage, ServerMessage, IntMessage, ServerMessageEnum, FORMAT
from tools import set_log, Logging_level

DEFAULT_BUFFER_SIZE = 128


def get_json_message_from_socket(msg_length, connection: socket):
    set_log(f"get_json_message_from_socket INIT msg_length {msg_length} - socket {connection}",
            level=Logging_level.debug)
    total_received = 0
    chunks = []
    while total_received < msg_length:
        chunk = connection.recv(msg_length - total_received).decode(FORMAT)
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        total_received = total_received + len(chunk)
    msg = "".join(chunks)
    set_log(f"get_json_message_from_socket RETURN [{msg}] - socket {connection}", level=Logging_level.debug)
    return msg


class EasyServer:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.__continue = True
        self.__MessageReceived_handler = None
        self.__MessageCheck_handler = None
        self.__MessageSendToClient_handler = None
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind((self.ip_address, self.port))

    @property
    def message_received_handler(self):
        """Event handler used to send the message from the client.

        Returns:
            [function]: function should have 3 parameters : address (tuple client IP and client port),
            msg string message, list of message from client
        """
        return self.__MessageReceived_handler

    @property
    def message_check_handler(self):
        return self.__MessageCheck_handler

    @property
    def message_send_to_client_handler(self):
        return self.__MessageSendToClient_handler

    @message_send_to_client_handler.setter
    def message_send_to_client_handler(self, value):
        self.__MessageSendToClient_handler = value

    @message_check_handler.setter
    def message_check_handler(self, value):
        self.__MessageCheck_handler = value

    @message_received_handler.setter
    def message_received_handler(self, value):
        """Event handler used to send the message from the client.

        Args:
            value (function): function should have 3 parameters : address (tuple client IP and client port),
            msg string message, list of message from client
        """
        self.__MessageReceived_handler = value

    def __server_message_switcher(self, connection: socket, address, message_server_enum, msg):
        switcher = {
            ServerMessageEnum.SEND_MESS: self.__server_message_treat_send_mess,
            ServerMessageEnum.MSG_OK: self.__server_message_treat_msg_ok,
            ServerMessageEnum.MSG_NOK: self.__server_message_treat_msg_nok,
            ServerMessageEnum.DISCONNECT_MESSAGE: self.__server_message_treat_disconnect_message,
            ServerMessageEnum.MESSAGE_4_CLIENT: self.__server_message_message_4_client
        }
        func = switcher.get(message_server_enum, self.__server_message_treat_default)
        return func(connection, address, msg)

    def __server_message_message_4_client(self, connection, address, msg):
        set_log(f"__server_message_message_4_client {address}", level=Logging_level.info)
        if self.__MessageSendToClient_handler:
            messages = self.__MessageSendToClient_handler(address, msg.entity, msg.category)
            if messages:
                """
                    If message to sent at the client protocol is follow:
                    -> Response MSG OK
                    -> Nbr of message available on the server for the client
                    -> foreach message
                        -> Send the length of the message
                        -> Send the message itself
                """
                connection.send(ServerMessage(server_message_enum=ServerMessageEnum.MSG_OK,
                                              buffer_size=DEFAULT_BUFFER_SIZE).encode())
                connection.send(IntMessage(len(messages), DEFAULT_BUFFER_SIZE).encode())
                for m in messages:
                    connection.send(IntMessage(m.length, DEFAULT_BUFFER_SIZE).encode())
                    connection.send(m.encode())
            else:
                connection.send(ServerMessage(server_message_enum=ServerMessageEnum.NO_MESSAGE,
                                              buffer_size=DEFAULT_BUFFER_SIZE).encode())
        else:
            connection.send(ServerMessage(server_message_enum=ServerMessageEnum.NO_MESSAGE,
                                          buffer_size=DEFAULT_BUFFER_SIZE).encode())
        return True

    def __server_message_treat_send_mess(self, connection: socket.socket, address, message):
        """Private method to manage message from client. The protocol :
        SEND_MESS is done
        LENGTH of the message
        MESSAGE 

        if MessageCheck_handler is linked the server wait the validation to respond to the client with MSG_OK or MSG_NOK
        if MessageReceived_handler is linked, the server start a new threat to manage the message 

        Args:
            connection (socket): socket used to read and send data
            address (IP,PORT): address used to respond
            message (Message): last message
        """
        set_log(f"__server_message_treat_send_mess {address}", level=Logging_level.info)
        msg = get_json_message_from_socket(msg_length=DEFAULT_BUFFER_SIZE, connection=connection)
        if msg:
            msg = IntMessage.decode(msg)
            msg = EasyMessage.decode(get_json_message_from_socket(msg_length=msg.int_value, connection=connection))
            msg_check = True
            if self.__MessageCheck_handler:
                msg_check = self.__MessageCheck_handler(address, msg)
                if msg_check:
                    connection.send(ServerMessage(server_message_enum=ServerMessageEnum.MSG_OK,
                                                  buffer_size=DEFAULT_BUFFER_SIZE).encode())
                else:
                    connection.send(ServerMessage(server_message_enum=ServerMessageEnum.MSG_NOK,
                                                  buffer_size=DEFAULT_BUFFER_SIZE).encode())

            # TODO check if we need to create thread we don't need to stop the communication with the client
            if self.__MessageReceived_handler and msg_check:
                self.__MessageReceived_handler(address, msg)
        return True

    def __server_message_treat_msg_ok(self, connection, address, message):
        set_log(f"__server_message_treat_msg_ok {address}", level=Logging_level.info)
        return True

    def __server_message_treat_msg_nok(self, connection, address, message):
        set_log(f"__server_message_treat_msg_nok {address}", level=Logging_level.info)
        return True

    def __server_message_treat_disconnect_message(self, connection, address, message):
        set_log(f"__server_message_treat_disconnect_message {address}", level=Logging_level.info)
        connection.send(
            ServerMessage(server_message_enum=ServerMessageEnum.MSG_OK, buffer_size=DEFAULT_BUFFER_SIZE).encode())
        return False

    def __server_message_treat_default(self, connection, address, message):
        set_log(f"__server_message_treat_default {address}", level=Logging_level.info)
        return True

    def __handle_connection(self, connection, address):
        set_log(f"[NEW CONNECTION] {address} connected", level=Logging_level.info)
        connected = True
        while connected:
            '''
                A new client is connected we need to receive a server message
            '''
            msg = get_json_message_from_socket(DEFAULT_BUFFER_SIZE, connection)
            msg = ServerMessage.decode(msg)
            if msg:
                connected = self.__server_message_switcher(connection=connection, address=address,
                                                           message_server_enum=msg.server_message_enum, msg=msg)

        set_log(f"[CLOSE CONNECTION] {address}", level=Logging_level.info)
        connection.close()

    def start(self):
        """[summary]
        Start the server into a loop
        """
        self.__socket.listen()
        set_log(f"[LISTENING] Server is listening on {self.ip_address}:{self.port}", level=Logging_level.info)
        while self.__continue:
            (connection, address) = self.__socket.accept()
            thread = threading.Thread(target=self.__handle_connection, args=(connection, address))
            thread.start()
            set_log(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}", level=Logging_level.info)
        set_log(f"[STOP] Server is stopped", level=Logging_level.info)


def manage_message(address, message):
    print(
        f"New message to treat from {address}\n\t entity:{message.entity}\n\t category:{message.category}"
        f"\n\t message:{message.message}")


def check_message(address, msg):
    if msg.message.startswith("TOTO"):
        return True
    else:
        return False


def message_send_to_client(address, entity, category):
    if entity == "Manu":
        mess = []
        for i in range(10):
            mess.append(EasyMessage(f"{i} c'est bien !!!!"))
        return mess


if __name__ == "__main__":
    s = EasyServer("localhost", 5050)
    s.message_received_handler = manage_message
    s.message_check_handler = check_message
    s.message_send_to_client_handler = message_send_to_client
    s.start()