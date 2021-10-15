import struct

NETWORK_ENDIANESS = "big"

class PacketFormat:
    SHORT = 'h'
    INTEGER = 'i'
    LONG_LONG = 'q'
    BYTES_SIZE_TYPE = int

    SHORT_SIZE = 2
    INTEGER_SIZE = 4
    LONG_LONG_SIZE = 8

    def __contains__(self, format_specifier):
        return (format_specifier in (self.SHORT, self.INTEGER, self.LONG_LONG) 
                or isinstance(format_specifier, int))


class PacketStructureError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

def make_pkt(packet_structure):

    #TODO:handle tuple of tuple
    if(not isinstance(packet_structure, tuple)):
        raise PacketStructureError("Wrong Packet structure, expected tuple")

    packet = b''
    #TODO: change key, value names to the sensible names
    for key, value in packet_structure:
        if(value not in PacketFormat()):
            raise PacketStructureError(f" Invalid format specifier")

        elif(isinstance(value, PacketFormat.BYTES_SIZE_TYPE)):
            if(not isinstance(key, bytes)):
                raise PacketStructureError("Invalid key type, expected bytes object")
            packet += key

        else:
            if(not isinstance(key, int)):
                raise PacketStructureError(f"{key}:{value}, Invalid value type")
            packet += struct.pack("!" + value, key)

    return packet


def decode_pkt(packet, packet_format):
    if(not isinstance(packet, bytes)):
        raise PacketStructureError("Wrong Packet structure, expected bytes")

    packet_values = list()
    offset = 0
    #TODO: change key, value names to the sensible names
    for value in packet_format:
        if(offset >= len(packet)):
            raise PacketStructureError("Too many field in packet format")

        elif(value not in PacketFormat()):
            raise PacketStructureError("Invalid format specifier")

        elif(isinstance(value, PacketFormat.BYTES_SIZE_TYPE)):
            if(value == -1):
                packet_values.append(packet[offset : ])
                offset += value
            else:
                packet_values.append(packet[offset : offset + value])
                offset += value

        elif(value == PacketFormat.SHORT):
            decoded_value = struct.unpack("!" + value, 
                                        packet[
                                            offset : 
                                            offset + PacketFormat.SHORT_SIZE
                                            ])
            packet_values.append(*decoded_value)
            offset += PacketFormat.SHORT_SIZE

        elif(value == PacketFormat.INTEGER):
            decoded_value = struct.unpack("!" + value, 
                                        packet[
                                            offset : 
                                            offset + PacketFormat.INTEGER_SIZE
                                            ])
            packet_values.append(*decoded_value)
            offset += PacketFormat.INTEGER_SIZE

        elif(value == PacketFormat.LONG_LONG):
            decoded_value = struct.unpack("!" + value, 
                                        packet[
                                            offset : 
                                            offset + PacketFormat.LONG_LONG_SIZE
                                            ])
            packet_values.append(*decoded_value)
            offset += PacketFormat.LONG_LONG_SIZE

    return tuple(packet_values)

