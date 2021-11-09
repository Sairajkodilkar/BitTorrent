import struct

NETWORK_ENDIANESS = "big"


class PacketFormat:

    BYTE = 'b'
    SHORT = 'h'
    INTEGER = 'i'
    LONG_LONG = 'q'
    STRING = 's'
    UBYTE = 'B'
    USHORT = 'H'
    UINTEGER = 'I'
    ULONG_LONG = 'Q'
    USTRING = 'S'
    TILL_END = -1
    BYTES_SIZE_TYPE = int

    BYTE_SIZE = 1
    SHORT_SIZE = 2
    INTEGER_SIZE = 4
    LONG_LONG_SIZE = 8

    def __contains__(self, format_specifier):
        return (format_specifier in (self.SHORT, self.INTEGER, self.LONG_LONG,
                                     self.BYTE, self.TILL_END, self.STRING, 
                                     self.USHORT, self.UINTEGER,
                                     self.ULONG_LONG, self.UBYTE, self.USTRING)
                or isinstance(format_specifier, int))


class PacketStructureError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def make_pkt(packet_structure):

    # TODO:handle tuple of tuple
    if(not isinstance(packet_structure, tuple)):
        raise PacketStructureError("Wrong Packet structure, expected tuple")

    packet = b''
    # TODO: change key, value names to the sensible names
    for key, value in packet_structure:
        if(value not in PacketFormat()):
            raise PacketStructureError(f"Invalid format specifier {value}")

        elif(isinstance(value, PacketFormat.BYTES_SIZE_TYPE)
                or value == PacketFormat.STRING):

            if(not isinstance(key, bytes)):
                raise PacketStructureError(
                    "Invalid key type, expected bytes object")
            packet += key

        else:
            if(not isinstance(key, int)):
                raise PacketStructureError(
                    f"{key}:{value}, Invalid value type")
            packet += struct.pack("!" + value, key)

    return packet


def decode_pkt(packet, packet_format):
    if(not isinstance(packet, bytes)):
        raise PacketStructureError("Wrong Packet structure, expected bytes")

    packet_values = list()
    offset = 0
    # TODO: change key, value names to the sensible names
    for value in packet_format:
        if(offset >= len(packet)):
            break

        elif(value not in PacketFormat()):
            raise PacketStructureError("Invalid format specifier")

        elif(isinstance(value, PacketFormat.BYTES_SIZE_TYPE)):
            if(value == PacketFormat.TILL_END):
                packet_values.append(packet[offset:])
                offset = len(packet)
            else:
                packet_values.append(packet[offset: offset + value])
                offset += value

        elif(value == PacketFormat.STRING):
            string_len = packet_values[-1]
            packet_values.append(packet[offset: offset + string_len])
            offset += string_len

        elif(value == PacketFormat.BYTE):
            decode_value = struct.unpack("!" + value,
                                         packet[
                                             offset:
                                             offset + PacketFormat.BYTE_SIZE
                                         ])
            packet_values.append(*decode_value)
            offset += PacketFormat.BYTE_SIZE

        elif(value == PacketFormat.SHORT or value == PacketFormat.USHORT):
            decoded_value = struct.unpack("!" + value,
                                          packet[
                                              offset:
                                              offset + PacketFormat.SHORT_SIZE
                                          ])
            packet_values.append(*decoded_value)
            offset += PacketFormat.SHORT_SIZE

        elif(value == PacketFormat.INTEGER or value == PacketFormat.UINTEGER):
            decoded_value = struct.unpack("!" + value,
                                          packet[
                                              offset:
                                              offset + PacketFormat.INTEGER_SIZE
                                          ])
            packet_values.append(*decoded_value)
            offset += PacketFormat.INTEGER_SIZE

        elif(value == PacketFormat.LONG_LONG
             or value == PacketFormat.ULONG_LONG):
            decoded_value = struct.unpack("!" + value,
                                          packet[
                                              offset:
                                              offset + PacketFormat.LONG_LONG_SIZE
                                          ])
            packet_values.append(*decoded_value)
            offset += PacketFormat.LONG_LONG_SIZE
        else:
            PacketStructureError("Invalid packet error")

    return tuple(packet_values)
