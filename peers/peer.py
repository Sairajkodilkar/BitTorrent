'''
Keepalives are generally sent once every two minutes, but note that timeouts can be done much more quickly when data is expected.
Should I include timeout inside or outside
Problems:
    How to manage all the peers?
        there must be one listening thread
        Each peer must have its own thread?
            -But main thread must be able to manage all the thread
            -Main thread should be able to determine download rate and
            determine to chock
            -I might need to make subclass using the threading class and then
                invoke the peer functions on it

        On termination of peer connection the thread must also be closed
        -How to determine if the connections is closed by peer
        -Need to check the socket state every time.

        I should also maintain the states for all the peers:
            Is he chocking/unchocking me
            Is he interested/not interested in me
            Am I chocking/unchocking him
            Am I interested/not interested in him

    What exactly is the max block size?
        There is conflict on this topic

    How to manange all the pieces since they will come in block of small size?
        There must be lock on the piece
        If two client send same block then we must select which block write.
        There must be global piece state

    How to request blocks?
        Should I request all of them to all the peers or should I request
        different blocks to differnet peers

'''
class Peer:

    def __init__(self, address):
        self._peer_is_chock = 
        self._peer_is_interested = 
        self._chock =
        self._interested = 
        self.address = address
        pass

    def handshake(self, info_has, peer_id, pstr=b"BitTorrent Protocol"):
        pkt_content = packetize_hanshake(len(pstr), pstr, reserved, info_hash,
                peer_id)
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

    def close


