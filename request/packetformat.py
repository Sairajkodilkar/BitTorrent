from bittorrent.packet.packet import PacketFormat 

RESPONSE_HEADER_FORMAT = [
        PacketFormat.INTEGER,       #action         
        PacketFormat.INTEGER,       #transaction_id
        PacketFormat.TILL_END
    ]

CONNECTION_REQUEST_FORMAT = [
        PacketFormat.LONG_LONG,     #protocol_id    0x41727101980
        PacketFormat.INTEGER,       #action         0
        PacketFormat.INTEGER        #transaction_id
    ]

CONNECTION_RESPONSE_FORMAT = [
        PacketFormat.LONG_LONG      #connection_id
    ]
        
ANNOUNCE_REQUEST_FORMAT = [
        PacketFormat.LONG_LONG,     #connection_id
        PacketFormat.INTEGER,       #action         1
        PacketFormat.INTEGER,       #transaction_id
        20,                         #info_hash
        20,                         #peer_id
        PacketFormat.LONG_LONG,     #downloaded
        PacketFormat.LONG_LONG,     #left
        PacketFormat.LONG_LONG,     #uploaded
        PacketFormat.INTEGER,       #event          0
        PacketFormat.INTEGER,       #IP address     0 default/IPv6
        PacketFormat.INTEGER,       #key            
        PacketFormat.INTEGER,       #num_want       PacketFormat.TILL_END 
        PacketFormat.SHORT          #port           //What is use ofthis?typically 6881-6889 
    ]

ANNOUNCE_RESPONSE_FORMAT = [
        PacketFormat.INTEGER,       #interval
        PacketFormat.INTEGER,       #leechers
        PacketFormat.INTEGER,       #seeders
        PacketFormat.TILL_END                          #peer_list
    ]


SCRAPE_REQEST_FORMAT = [
        PacketFormat.LONG_LONG,     #connection_id 
        PacketFormat.INTEGER,       #action         2
        PacketFormat.INTEGER,       #transaction_id
        20                          #info_hash
    ]

SCRAPE_RESPONSE_FORMAT = [
        PacketFormat.INTEGER,       #seeders
        PacketFormat.INTEGER,       #completed
        PacketFormat.INTEGER,       #leechers
    ]

ERROR_RESPONSE_FORMAT = [
        PacketFormat.TILL_END
    ]

