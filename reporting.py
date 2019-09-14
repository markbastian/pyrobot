import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# iMac
serversocket.bind(('192.168.0.9', 8089))
# bot
# serversocket.bind(('192.168.0.17', 8089))
# become a server socket, maximum 5 connections
serversocket.listen(5)

connection, address = serversocket.accept()

while True:
    buf = connection.recv(64)
    if len(buf) > 0:
        msg = buf.decode('UTF-8')
        if msg == 'EOF':
            break
        else:
            print(msg)


# Client - Add code to send state info to the server to be plotted.
def doclient():
    clientsocket = socket.socket()
    clientsocket.connect(('192.168.0.9', 8089))
    clientsocket.send('This is a test'.encode())
