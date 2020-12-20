# Socket
Is a simple class to allow the management of sending message from a client to a server. 

Create an instance of Server with your IpAdresse and an available port
and wait a client connection 

## how does it works
When a client want to send a message to the server. The client class calculate the length of the message and send it to the server and directly send the message.
the message will be encoded in UTF-8. 

The server get the message length and read the socket to get all message. 
* if MessageCheck_handler is set into the server a validation occured. By default no check all message is validated 
* if MessageReceived_handler is set into the server an event into a thread is raised 