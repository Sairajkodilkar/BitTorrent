from bittorrent.bdencoder import bdencoder
import socket

IP_ADDR_SIZE = 4
PORT_NUM_SIZE = 2
PEER_ADDRESS_SIZE = IP_ADDR_SIZE + PORT_NUM_SIZE

def parse_compact_peers(peers):
    peers_list = []
    if(len(peers) % 6):
        #TODO raise error here
        pass
    i = 0
    while(i < len(peers)):
        peer_ip = socket.inet_ntoa(peers[i:i + IP_ADDR_SIZE])
        peer_port = int.from_bytes(peers[i + IP_ADDR_SIZE : 
                                            i + PEER_ADDRESS_SIZE], "big")
        peers_list.append((peer_ip, peer_port))
        i += PEER_ADDRESS_SIZE

    return peers_list

def parse_scrape_res(scrape_res):

    i = 0
    scrape_list = []
    while(i < len(scrape_res)):
        status = struct.unpack(
                "!3" + PacketFormat.INTEGER, 
                scrape_res[i : i + (3 * PacketFormat.INTEGER_SIZE)])

        scrape_list.append(status)
        i += 3 * PacketFormat.INTEGER_SIZE

    return scrape_list

