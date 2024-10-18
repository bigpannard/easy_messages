from easy_client import EasyClient, EasyMessage

client = EasyClient("localhost", 5050, entity="Manu")
msg = client.send(EasyMessage(message="<ADD_PL>Bonjour serveur c'est Manu", entity="Manu", category="Admin"))
msg = client.send(EasyMessage(message="TOTO<ADD_PL>Bonjour serveur c'est Manu", entity="Manu", category="Admin"))
print(msg.message)
messages = client.get_messages()
if messages:
    for mess in messages:
        print(f"Message from serveur :{mess.message}")
msg = client.disconnect()
print(msg.message)