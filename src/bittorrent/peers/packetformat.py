from bittorrent.packet.packet import PacketFormat

HANDSHAKE_LEN_FORMAT = [
    PacketFormat.BYTE, # protocol string length 
    -1
]

HANDSHAKE_FORMAT = [
    PacketFormat.BYTE,      # protocol string length 
    PacketFormat.STRING,    # protocol string   //"BitTorrent protocol"
    PacketFormat.LONG_LONG, # reserved
    20,                     # Info Hash
    20                      # peer ID
]

KEEP_ALIVE_FORMAT = [
    PacketFormat.INTEGER  # length //0
]

LENGTH_FORMAT = [
    PacketFormat.UINTEGER,  # length
    PacketFormat.TILL_END
]

HEADER_FORMAT = [
    PacketFormat.BYTE,  # id
    PacketFormat.TILL_END
]

HAVE_FORMAT = [
    PacketFormat.INTEGER  # piece index
]

HAVE_ALL_FORMAT = [
    PacketFormat.TILL_END 
]

HAVE_NONE_FORMAT = [
    PacketFormat.TILL_END
]

SUGGEST_PIECE_FORMAT = [
    PacketFormat.INTEGER  # piece index
]

BITFIELD_FORMAT = [
    PacketFormat.TILL_END  # bit field
]

REQUEST_FORMAT = [
    PacketFormat.INTEGER, # index
    PacketFormat.INTEGER, # begin
    PacketFormat.INTEGER  # length
]

PIECE_FORMAT = [
    PacketFormat.INTEGER,  # index
    PacketFormat.INTEGER,  # begin
    PacketFormat.TILL_END  # block
]

CANCEL_FORMAT = [
    PacketFormat.INTEGER, # index
    PacketFormat.INTEGER, # begin
    PacketFormat.INTEGER  # length
]

PORT_FORMAT = [
    PacketFormat.SHORT # listen port //used in DHT
]

EXTENDED_FORMAT = [
        PacketFormat.UBYTE,
        PacketFormat.TILL_END
    ]
