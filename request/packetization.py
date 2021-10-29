from bittorrent.packet.packet import make_pkt, decode_pkt
from bittorrent.request.packetformat import *

#TODO: Check the given argument is of expected bits

#magic constant
CONNECTION_PROTOCOL_ID = 0x41727101980

class UnpacketizationError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class PacketizationError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

def paketize_connection_req(transaction_id):

    pkt_content = [CONNECTION_PROTOCOL_ID, Action.CONNECT, transaction_id]
    packet_structure = tuple(zip(pkt_content, CONNECTION_REQUEST_FORMAT))

    return make_pkt(packet_structure)


def packetize_announce_req(connection_id, transaction_id, info_hash,
                            peer_id, downloaded, left,
                            uploaded, port, key,
                            event, ip_address, num_want):

    print(connection_id)
    pkt_content = [
                    connection_id, Action.ANNOUNCE, transaction_id,
                    info_hash, peer_id, downloaded, 
                    left, uploaded, event,
                    ip_address, key, num_want, port
                ]
    print(pkt_content)
    packet_structure = tuple(zip(pkt_content, ANNOUNCE_REQUEST_FORMAT))

    return make_pkt(packet_structure)

def packetize_scrap_req(connection_id, transaction_id, info_hash):

    pkt_content = [connection_id, Action.SCRAPE, transaction_id, info_hash]
    print(pkt_content[0])
    packet_structure = tuple(zip(pkt_content, SCRAPE_REQEST_FORMAT))


    return make_pkt(packet_structure)


def unpaketize_response(packet):
    
    action, transaction_id, payload = decode_pkt(packet, 
                                                RESPONSE_HEADER_FORMAT)
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

