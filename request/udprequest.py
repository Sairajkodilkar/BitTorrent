from packetization import *
import socket

import struct

class Action:
    CONNECT = 0
    ANNOUNCE = 1
    SCRAPE = 2
    ERROR = 3

class Event:
    NONE = 0
    COMPLETE = 1
    STARTED = 2
    STOPPED = 3
    

class TrackerTimeoutError(Exception):
    
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

class UDPRequest:

    def __init__(self, tracker_address):

        self.tracker_address = tracker_address

        self.torrent_client_socket = socket.socket(socket.AF_INET, 
                                                    socket.SOCK_DGRAM)
        self.torrent_client_socket.setsockopt(socket.SOL_SOCKET,
                                                socket.SO_REUSEADDR, 1)

    def connect(self, transaction_id):

        connection_req_packet = paketize_connection_req(transaction_id)
        #TODO: take care of return value
        self.make_request(connection_req_packet)

        #TODO: check action number 
        #TODO: check weather the packet is at least 16 bytes
        connection_res_packet, address = self.get_response()
        connection_res = unpaketize_response(connection_res_packet)
        return connection_res

    def announce(self, connection_id, transaction_id, info_hash,
                peer_id, downloaded, left,
                uploaded, port, key,
                event=0, ip_address=0, num_want=-1):

        announce_req_packet = packetize_announce_req(
                                connection_id, transaction_id, info_hash, 
                                peer_id, downloaded, left,
                                uploaded, port, key,
                                event, ip_address, num_want)

        #TODO: take care of return value
        self.make_request(announce_req_packet)
        #TODO: check action number
        #TODO: check weather the packet is at least 20 bytes
        announce_res_packet, address = self.get_response()
        announce_res = unpaketize_response(announce_res_packet)
        return announce_res, address

    def scrape(self, connection_id, transaction_id, info_hash):
        #TODO write scrape for multiple info_hash, possibly change
        #       pktformatting

        scrape_req_packet = packetize_scrap_req(connection_id, 
                                                transaction_id,
                                                info_hash)

        print("sending", self.tracker_address, scrape_req_packet, hex(connection_id))
        #TODO: take care of return value
        self.make_request(scrape_req_packet)
        print("unpacking", struct.unpack("!q", scrape_req_packet[0:8]))

        #TODO: check weather the packet is at least 8 byte
        scrape_res_packet, address = self.get_response()
        print("recvd", scrape_res_packet)
        #TODO: check action number
        scrape_res = unpaketize_response(scrape_res_packet)
        return scrape_res

    def make_request(self, req_packet):
        return self.torrent_client_socket.sendto(req_packet,
                                                self.tracker_address)
    
    def get_response(self):

        timeout = 15
        count = 0
        while(1):
            if(count > 8):
                raise 
            self.torrent_client_socket.settimeout(timeout)
            try:
                print("waiting for server to respond...")
                #FIXME 2048 might restrict the peer list so we have to recv
                #       full msg(find a good hack)
                res_packet, address = self.torrent_client_socket.recvfrom(2048)
            except socket.timeout:
                timeout *= 2
                count += 1
                continue
            break

        return res_packet, address

