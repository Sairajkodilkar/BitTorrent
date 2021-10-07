from packet import make_pkt
from pkt_format import *

def paketize_connection_req:
    pass

def unpaketize_connection_res:
    pass

class packetize_announce_req:
    pass

class unpacketize_announce_res:
    pass

class packetize_scrap_req:
    pass

class unpacketize_announce_res:
    pass

class UDPRequest:

    def __init__(self, address):
        self.address = address

    def connect(self, transaction_id):
        return dictionary of transaction_id_by_server, connection_id

    def announce(self, connection_id, transaction_id, info_hash, peer_id,
            downloaded, left, uploaded, port, key, event=0, IP_address=0, num_want =
            -1):

        return dictionary of transaction_id, interval, leechers, seeders, IP_address, TCP_port

    def scrap(self, connection_id, transaction_id, info_hash):
        return list of dictionar of seeds, completed, leechers for each of the info_hash
