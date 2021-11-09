from bittorrent.packet.packet import PacketFormat

HANDSHAKE_LEN_FORMAT = [
    PacketFormat.BYTE, # protocol string length //"BitTorrent protocol"
    -1
]

HANDSHAKE_FORMAT = [
    PacketFormat.BYTE,      # protocol string length //"BitTorrent protocol"
    PacketFormat.STRING,    # protocol string
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