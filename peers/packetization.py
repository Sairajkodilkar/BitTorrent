from bittorrent.packet.packet import (
        make_pkt, 
        decode_pkt,
        PacketFormat
    )

from packetformat import *

HEADER_LEN        = PacketFormat.BYTE_SIZE
CHOCK_LEN         = HEADER_LEN
UNCHOCK_LEN       = HEADER_LEN
INTERESTED_LEN    = HEADER_LEN
NOTINTERESTED_LEN = HEADER_LEN
HAVE_LEN          = HEADER_LEN + PacketFormat.INTEGER_SIZE
REQUEST_LEN       = HEADER_LEN + 3 * PacketFormat.INTEGER_SIZE
PIECE_LEN         = HEADER_LEN + 2 * PacketFormat.INTEGER_SIZE
CANCEL_LEN        = HEADER_LEN + 3 * PacketFormat.INTEGER_SIZE
PORT_LEN          = HEADER_LEN + PacketFormat.INTEGER_SIZE

class ID:
    CHOCK           = 0
    UNCHOCK         = 1
    INTERESTED      = 2
    NOT_INTERESTED  = 3
    HAVE            = 4
    BIT_FIELD       = 5
    REQUEST         = 6
    PIECE           = 7
    CANCEL          = 8
    PORT            = 9

def packetize_handshake(pstrlen, pstr, reserved, info_hash, peer_id):

    packet_content = [pstrlen, pstr, reserved, info_hash, peer_id]
    packet_structure  = tuple(zip(packet_content, HANDSHAKE_FORMAT))

    return make_pkt(packet_structure)

def packetize_keepalive():

    packet_content = [0]
    packet_structure = tuple(zip(packet_content, KEEP_ALIVE_FORMAT))

    return make_pkt(packet_structure)

def packetize_header(message_len, message_id):
    packet_content = [message_len, message_id]
    packet_structure = tuple(zip(packet_content, HEADER_FORMAT))

    return make_pkt(packet_structure)

def packetize_chock():

    return packetize_header(CHOCK_LEN, ID.CHOCK)

def packetize_unchock():

    return packetize_header(UNCHOCK_LEN, ID.UNCHOCK)

def packetize_interested():

    return packetize_header(INTERESTED_LEN, ID.INTERESTED)

def packetize_notinterested():

    return packetize_header(NOTINTERESTED_LEN, ID.NOT_INTERESTED)

def packetize_have(piece_index:int):

    header = packetize_header(HAVE_LEN, ID.HAVE)
    packet_content = [piece_index]
    packet_structure = tuple(zip(packet_content, HAVE_FORMAT))

    return header + make_pkt(packet_structure)

def packetize_bitfield(bitfield:bytes):

    header = packetize_header(HEADER_LEN + len(bitfield), ID.BIT_FIELD)

    return header + bitfield

def packetize_request(index:int, begin:int, length:int):

    header = packetize_header(REQUEST_LEN, ID.REQUEST)
    packet_content = [index, begin, length]
    packet_structure = tuple(zip(packet_content, REQUEST_FORMAT))

    return header + make_pkt(packet_structure)

def packetize_piece(index:int, begin:int, block:bytes):

    header = packetize_header(PIECE_LEN + len(block), ID.PIECE)
    packet_content = [index, begin, block]
    packet_structure = tuple(zip(packet_content, PIECE_FORMAT))

    return header + make_pkt(packet_structure)

def packetize_cancel(index:int, begin:int, length:int):

    header = packetize_header(CANCEL_LEN, ID.CANCEL)
    packet_content = [index, begin, length]
    packet_structure = tuple(zip(packet_content, REQUEST_FORMAT))

    return header + make_pkt(packet_structure)

def packetize_port(listen_port:int):

    header = packetize_header(PORT_LEN, ID.PORT)
    packet_content = [listen_port]
    packet_structure = tuple(zip(packet_content,  PORT_FORMAT))

    return header + make_pkt(packet_structure)

def unpacketize_handshake(packet):

    handshake = decode_pkt(packet, HANDSHAKE_FORMAT)

    return handshake

def unpacketize_response(packet):

    if(len(packet) == PacketFormat.INTEGER_SIZE):
        return (0,)
    
    unpacktized = decode_pkt(packet, HEADER_FORMAT)

    length = unpacktized[0]
    identity =  unpacktized[1]

    response = None
    if(identity == ID.CHOCK or identity == ID.UNCHOCK 
            or identity == ID.INTERESTED or identity == ID.NOT_INTERESTED):
        return (identity,)

    if(len(unpacktized) != 3):
        return -1

    payload = unpacktized[2]

    if(identity == ID.HAVE):
        response = decode_pkt(payload, HAVE_FORMAT)

    elif(identity == ID.BIT_FIELD):
        response  = decode_pkt(payload, BITFIELD_FORMAT)

    elif(identity == ID.REQUEST):
        response = decode_pkt(payload, REQUEST_FORMAT)

    elif(identity == ID.PIECE):
        response = decode_pkt(payload, PIECE_FORMAT)

    elif(identity == ID.CANCEL):
        response = decode_pkt(payload, CANCEL_FORMAT)

    elif(identity == ID.PORT):
        response = decode_pkt(payload, PORT_FORMAT)

    return identity, *response
