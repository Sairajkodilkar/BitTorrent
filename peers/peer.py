class Peer:

    def __init__(self, address):
        #create socket with peer
        pass

    def handshake(self, address):
        pass

    def chock(self, status):
        pass

    def interested(self, status):
        pass

    def have(self, piece_index):
        pass

    def send_bitfield(self, bitfield):
        pass

    def request(self, index, begin, length):
        pass

    def send_piece(self, index, begin, block):
        pass

    def cancel(self, index, begin, length):
        pass

    def send_port(self, listen_port):
        pass


