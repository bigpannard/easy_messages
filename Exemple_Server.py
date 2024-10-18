from easy_server import EasyMessage,EasyServer

def manage_message(address, message):
    print(
        f"New message to treat from {address}\n\t entity:{message.entity}\n\t category:{message.category}"
        f"\n\t message:{message.message}")


def check_message(address, msg):
    return True


def message_send_to_client(address, entity, category):
    if entity == "Manu":
        mess = []
        for i in range(10):
            mess.append(EasyMessage(f"{i} c'est bien !!!!"))
        return mess


s = EasyServer("localhost", 5050)
s.message_received_handler = manage_message
"""s.message_check_handler = check_message"""
s.message_send_to_client_handler = message_send_to_client
s.start()