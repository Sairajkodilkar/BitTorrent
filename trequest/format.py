from packet import PacketFormat, make_pkt
CONNECTION_REQUEST_FORMAT = {
        packetformat.long_long,     #protocol_id
        PacketFormat.INTEGER,       #action
        PacketFormat.INTEGER        #transaction_id
    }

CONNECTION_RESPONSE_FORMAT = {
        PacketFormat.INTEGER,       #action
        PacketFormat.INTEGER,       #transaction_id
        PacketFormat.LONG_LONG      #connection_id
    }
        
        
ANNOUNCE_REQUEST_FORMAT = {
        PacketFormat.LONG_LONG,     #connection_id
        PacketFormat.INTEGER,       #action
        PacketFormat.INTEGER,       #transaction_id
        20,                         #info_hash
        20,                         #peer_id
        PacketFormat.LONG_LONG,     #downloaded
        PacketFormat.LONG_LONG,     #left
        PacketFormat.LONG_LONG,     #uploaded
        PacketFormat.INTEGER,       #event
        PacketFormat.INTEGER,       #IP address, all 0 for IPv6
        PacketFormat.INTEGER,       #key
        PacketFormat.INTEGER,       #num_want
        PacketFormat.SHORT          #port
    }

ANNOUNCE_RESPONSE_FORMAT = {
        PacketFormat.INTEGER,       #action
        PacketFormat.INTEGER,       #transaction_id
        PacketFormat.INTEGER,       #interval
        PacketFormat.INTEGER,       #leechers
        PacketFormat.INTEGER,       #seeders
        -1                          #peer_list
    }


SCRAPE_REQEST_FORMAT = {
        PacketFormat.LONG_LONG,     #connection_id 
        PacketFormat.INTEGER,       #action
        PacketFormat.INTEGER,       #transaction_id
        20                          #info_hash
    }

SCRAPE_RESPONSE_FORMAT = {
        PacketFormat.INTEGER,       #action   
        PacketFormat.INTEGER,       #transacti
        PacketFormat.INTEGER,       #seeders
        PacketFormat.INTEGER,       #completed
        PacketFormat.INTEGER,       #leechers
    }

