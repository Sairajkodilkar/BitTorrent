from bittorrent.packet.packet import PacketFormat

HANDSHAKE_FORMAT = [
        PacketFormat.BYTE,          #protocol string length //"BitTorrent protocol"
        19,                         #protocol string 
                                    #   Note:   Protocol string can be changed
                                    #           by the user hence the protocol
                                    #           length must also be changed
        PacketFormat.LONG_LONG,     #reserved 8 bytes // 0
        20,                         #Info Hash
        20                          #peer ID
    ]

KEEP_ALIVE_FORMAT = [
        PacketFormat.INTEGER        #length //0
    ]

HEADER_FORMAT = [
        PacketFormat.INTEGER,       #length 
        PacketFormat.BYTE           #id     
    ]

HAVE_FORMAT =  [
        PacketFormat.INTEGER        #piece index
    ]

BITFIELD_FORMAT = [
        -1                          #bit field
    ]

REQUEST_FORMAT = [
        PacketFormat.INTEGER,       #index
        PacketFormat.INTEGER,       #begin
        PacketFormat.INTEGER        #length
    ]

PIECE_FORMAT = [
        PacketFormat.INTEGER,       #index
        PacketFormat.INTEGER,       #begin
        -1                          #block
    ]

CANCEL_FORMAT = [
        PacketFormat.INTEGER,       #index
        PacketFormat.INTEGER,       #begin
        PacketFormat.INTEGER        #length
    ]

PORT_FORMAT = [
        PacketFormat.SHORT          #listen port //DHT
    ]

