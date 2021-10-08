from packet import make_pkt, decode_pkt
from pkt_format import *
import sys

#TODO: Check the given argument is of expected bits

#magic constant
CONNECTION_PROTOCOL_ID = 0x41727101980

class Action:
    CONNECT = 0
    ANNOUNCE = 1
    SCRAPE = 2
    ERROR = 3

class Events:
    NONE = 0
    COMPLETE = 1
    STARTED = 2
    STOPPED = 3
    
class UnpacketizationError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class PacketizationError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

def paketize_connection_req(transaction_id):
    pkt_content = [CONNECTION_PROTOCOL_ID, Action.CONNECT, transaction_id]
    packet_structure = tuple(zip(pkt_content, CONNECTION_REQUEST_FORMAT))

    print(make_pkt(packet_structure))
    return make_pkt(packet_structure)


def packetize_announce_req(connection_id, transaction_id, info_hash,
                            peer_id, downloaded, left,
                            uploaded, port, key,
                            event=0, ip_address=0, num_want=-1):
    pkt_content = [
                    connection_id, Action.ANNOUNCE, transaction_id,
                    info_hash, peer_id, downloaded, 
                    left, uploaded, event,
                    ip_address, key, num_want, port
                ]
    packet_structure = zip(pkt_content, ANNOUNCE_REQUEST_FORMAT)

    return make_pkt(packet_structure)

def packetize_scrap_req(connection_id, transaction_id, info_hash):
    pkt_content = [connection_id, Action.SCRAPE, transaction_id, info_hash]
    packet_structure = zip(pkt_content, SCRAPE_REQEST_FORMAT)

    return make_pkt(packet_structure)


def unpaketize_request(packet):
    action, transaction_id, payload = decode_pkt(
                                                packet, 
                                                RESPONSE_HEADER_FORMAT)
    print(action, transaction_id, payload, Action.CONNECT)
    response = None
    if(action == Action.CONNECT):
        response = decode_pkt(payload, CONNECTION_RESPONSE_FORMAT)
    elif(action == Action.ANNOUNCE):
        response = decode_pkt(payload, ANNOUNCE_RESPONSE_FORMAT)
    elif(action == Action.SCRAPE):
        response = decode_pkt(payload, SCRAPE_RESPONSE_FORMAT)
    elif(action == Action.ERROR):
        response = decode_pkt(packet, ERROR_RESPONSE_FORMAT)
    else:
        raise UnpacketizationError("Invalid response type")

    return action, transaction_id, *response

