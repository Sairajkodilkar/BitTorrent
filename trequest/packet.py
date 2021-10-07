class PacketFormat:
    SHORT = 'h'
    INTEGER = 'i'
    LONG_LONG = 'q'
    BYTES_SIZE_TYPE = int

    SHORT_SIZE = 2
    INTEGER_SIZE = 4
    LONG_LONG_SIZE = 8

    def __contains__(self, format_specifier):
        return format_specifier in (self.SHORT, self.INTEGER, self.LONG_LONG)
                or isinstance(format_specifier, int)


class PacketStructureError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

def make_pkt(packet_structure):

    if(not isinstance(packet_structure, dict)):
        raise PacketStructureError("Wrong Packet structure, expected dict")

    packet = b''
    #TODO: change key, value names to the sensible names
    for key, value in packet_structure.items():
        if(value not in PacketFormat()):
            raise PacketStructureError("Invalid format specifier")

        elif(isinstance(value, PacketFormat.BYTES_SIZE_TYPE)):
            if(not isinstance(key, bytes)):
                raise PacketStructureError("Invalid key type, \
                                            expected bytes object")
            packet += key

        else:
            packet += struct.pack("!" + value, key)

    return packet


def decode_pkt(packet, packet_format):
    if(not isinstance(packet, bytes)):
        raise PacketStructureError("Wrong Packet structure, expected bytes")

    packet_values = list()
    offset = 0
    #TODO: change key, value names to the sensible names
    for value in packet_format:
        if(value not in PacketFormat()):
            raise PacketStructureError("Invalid format specifier")

        elif(isinstance(value, PacketFormat.BYTES_SIZE_TYPE)):
            packet_values.append(packet[offset : offset + value])
            offset += value

        elif(value == PacketFormat.SHORT):
            decoded_value = int.from_bytes(packet[
                                            offset : 
                                            offset + PacketFormat.SHORT_SIZE
                                            ])
            packet_values.append(decode_pkt)
            offset += PacketFormat.SHORT_SIZE

        elif(value == PacketFormat.INTEGER):
            decoded_value = int.from_bytes(packet[
                                            offset : 
                                            offset + PacketFormat.INTEGER_SIZE
                                            ])
            packet_values.append(decode_pkt)
            offset += PacketFormat.INTEGER_SIZE

        elif(value == PacketFormat.LONG_LONG):
            decoded_value = int.from_bytes(packet[
                                            offset : 
                                            offset + PacketFormat.LONG_LONG_SIZE
                                            ])
            packet_values.append(decode_pkt)
            offset += PacketFormat.LONG_LONG_SIZE

    return 

