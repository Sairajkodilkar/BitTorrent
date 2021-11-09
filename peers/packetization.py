from bittorrent.packet.packet import (
    make_pkt,
    decode_pkt,
    PacketFormat
)

from bittorrent.peers.packetformat import *

LENGHT_LEN = PacketFormat.INTEGER_SIZE
HEADER_LEN = PacketFormat.BYTE_SIZE
CHOKE_LEN = HEADER_LEN
UNCHOKE_LEN = HEADER_LEN
INTERESTED_LEN = HEADER_LEN
NOTINTERESTED_LEN = HEADER_LEN
HAVE_LEN = HEADER_LEN + PacketFormat.INTEGER_SIZE
REQUEST_LEN = HEADER_LEN + 3 * PacketFormat.INTEGER_SIZE
PIECE_LEN = HEADER_LEN + 2 * PacketFormat.INTEGER_SIZE
CANCEL_LEN = HEADER_LEN + 3 * PacketFormat.INTEGER_SIZE
PORT_LEN = HEADER_LEN + PacketFormat.INTEGER_SIZE


class ID:
    CHOKE = 0
    UNCHOKE = 1
    INTERESTED = 2
    NOT_INTERESTED = 3
    HAVE = 4
    BIT_FIELD = 5
    REQUEST = 6
    PIECE = 7
    CANCEL = 8
    PORT = 9
    KEEP_ALIVE = 10
    EXTENDED = 20


class IndentityError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)


def packetize_handshake(pstrlen, pstr, reserved, info_hash, peer_id):

    packet_content = [pstrlen, pstr, reserved, info_hash, peer_id]
    packet_structure = tuple(zip(packet_content, HANDSHAKE_FORMAT))

    return make_pkt(packet_structure)


def packetize_keepalive():

    packet_content = [0]
    packet_structure = tuple(zip(packet_content, KEEP_ALIVE_FORMAT))

    return make_pkt(packet_structure)


def packetize_header(message_len, message_id):
    packet_lenght = [message_len]
    packet_structure = tuple(zip(packet_lenght, LENGTH_FORMAT))
    packet = make_pkt(packet_structure)

    packet_id = [message_id]
    packet_structure = tuple(zip(packet_id, HEADER_FORMAT))
    packet += make_pkt(packet_structure)

    return packet


def packetize_choke():

    return packetize_header(CHOKE_LEN, ID.CHOKE)


def packetize_unchoke():

    return packetize_header(UNCHOKE_LEN, ID.UNCHOKE)


def packetize_interested():

    return packetize_header(INTERESTED_LEN, ID.INTERESTED)


def packetize_notinterested():

    return packetize_header(NOTINTERESTED_LEN, ID.NOT_INTERESTED)


def packetize_have(piece_index: int):

    header = packetize_header(HAVE_LEN, ID.HAVE)
    packet_content = [piece_index]
    packet_structure = tuple(zip(packet_content, HAVE_FORMAT))

    return header + make_pkt(packet_structure)


def packetize_bitfield(bitfield: bytes):

    header = packetize_header(HEADER_LEN + len(bitfield), ID.BIT_FIELD)

    return header + bitfield


def packetize_request(index: int, begin: int, length: int):

    header = packetize_header(REQUEST_LEN, ID.REQUEST)
    packet_content = [index, begin, length]
    packet_structure = tuple(zip(packet_content, REQUEST_FORMAT))

    return header + make_pkt(packet_structure)


def packetize_piece(index: int, begin: int, block: bytes):

    header = packetize_header(PIECE_LEN + len(block), ID.PIECE)
    packet_content = [index, begin, block]
    packet_structure = tuple(zip(packet_content, PIECE_FORMAT))

    return header + make_pkt(packet_structure)


def packetize_cancel(index: int, begin: int, length: int):

    header = packetize_header(CANCEL_LEN, ID.CANCEL)
    packet_content = [index, begin, length]
    packet_structure = tuple(zip(packet_content, REQUEST_FORMAT))

    return header + make_pkt(packet_structure)


def packetize_port(listen_port: int):

    header = packetize_header(PORT_LEN, ID.PORT)
    packet_content = [listen_port]
    packet_structure = tuple(zip(packet_content,  PORT_FORMAT))

    return header + make_pkt(packet_structure)


def unpacketize_handshake_length(packet):

    length = decode_pkt(packet, HANDSHAKE_LEN_FORMAT)

    return length


def unpacketize_handshake(packet):

    handshake = decode_pkt(packet, HANDSHAKE_FORMAT)

    return handshake


def unpacketize_length(packet):

    response = decode_pkt(packet, LENGTH_FORMAT)

    return response


def unpacketize_response(packet):
    # user should always call unpacketize lenght to ensure that the packet is
    # recv completely before unpacking it
    # remove it from here and give it to control to user
    if(len(packet) == 0):
        return

    unpacktized = decode_pkt(packet, HEADER_FORMAT)

    identity = unpacktized[0]

    response = None
    if(identity == ID.CHOKE or identity == ID.UNCHOKE
            or identity == ID.INTERESTED or identity == ID.NOT_INTERESTED):
        return (identity,)

    if(len(unpacktized) != len(HEADER_FORMAT)):
        return (-1,)

    payload = unpacktized[1]

    if(identity == ID.HAVE):
        response = decode_pkt(payload, HAVE_FORMAT)

    elif(identity == ID.BIT_FIELD):
        response = decode_pkt(payload, BITFIELD_FORMAT)

    elif(identity == ID.REQUEST):
        response = decode_pkt(payload, REQUEST_FORMAT)

    elif(identity == ID.PIECE):
        response = decode_pkt(payload, PIECE_FORMAT)

    elif(identity == ID.CANCEL):
        response = decode_pkt(payload, CANCEL_FORMAT)

    elif(identity == ID.PORT):
        response = decode_pkt(payload, PORT_FORMAT)

    elif(identity == ID.EXTENDED):
        response = decode_pkt(payload, EXTENDED_FORMAT)

    else:
        IndentityError("Wrong ID field in response")

    return (identity, *response)
