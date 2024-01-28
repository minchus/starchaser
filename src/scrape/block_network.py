import socket


class BlockNetwork(socket.socket):
    def __init__(self, *args, **kwargs):
        super().__init__()
        raise Exception('Network call blocked')


# Test if cache is being used by blocking network
socket.socket = BlockNetwork
