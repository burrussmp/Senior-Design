import socket
from ast import literal_eval as make_tuple

server_address = ('10.66.247.21',5001)

def communicateToServer(server_address,sock):
    message = "hi"
    message = message.encode()
    sock.sendall(message)
    data = sock.recv(32)
    print(data)
    data_decoded = data.decode()
    orientation = make_tuple(data_decoded) # (heading, roll, pitch) euler angles
    print(orientation)

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    terminateConnection = False
    while (not terminateConnection):
        try:
            communicateToServer(server_address,sock)
        except Exception as e:
            print(e)
            terminateConnection = True